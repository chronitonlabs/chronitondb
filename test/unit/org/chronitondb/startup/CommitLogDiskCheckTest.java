/*
 * Copyright 2026 AxonOps Limited
 * SPDX-License-Identifier: Apache-2.0
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package org.chronitondb.startup;

import static org.apache.cassandra.service.StartupChecks.StartupCheckType.check_commitlog_shared_disk;
import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;

import ch.qos.logback.classic.Level;
import ch.qos.logback.classic.Logger;
import ch.qos.logback.classic.spi.ILoggingEvent;
import ch.qos.logback.core.read.ListAppender;
import com.codahale.metrics.Counter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.function.Function;
import java.util.function.LongConsumer;
import java.util.function.Supplier;
import java.util.stream.Collectors;
import org.apache.cassandra.config.StartupChecksOptions;
import org.apache.cassandra.metrics.CassandraMetricsRegistry;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.slf4j.LoggerFactory;

/** The commit log disk check run against fixed directories and device ids. */
public class CommitLogDiskCheckTest {
  private static final String COMMIT_LOG = "/cl";
  private static final String SHARED = "SharedDataDirectories";
  private static final String UNREADABLE = "UnreadableDirectories";
  private static final String FAILED = "FailedRuns";
  private static final String SHARED_TAIL =
      ". One failure of that file system loses the commit log and the data together, and on"
          + " spinning disks commit log writes compete with reads, flushes and compaction. Put"
          + " commitlog_directory on a file system of its own. This warning comes from the startup"
          + " check check_commitlog_shared_disk.";
  private static final String FAILED_TEXT =
      "The startup check check_commitlog_shared_disk failed and compared nothing more.";

  private Logger logger;
  private ListAppender<ILoggingEvent> appender;

  @Before
  public void attachAppender() {
    logger = (Logger) LoggerFactory.getLogger(CommitLogDiskCheck.class);
    appender = new ListAppender<>();
    appender.start();
    logger.addAppender(appender);
  }

  @After
  public void detachAppender() {
    logger.detachAppender(appender);
  }

  @Test
  public void sharedFileSystemWarnsOnce() {
    Devices devices = new Devices().on(COMMIT_LOG, 1).on("/d1", 1).on("/d2", 2).on("/d3", 1);

    check(dirs("/d1", "/d2", "/d3", "/d1"), devices).execute(on());

    assertEquals(List.of(shared("[/d1, /d3]")), warnings());
  }

  @Test
  public void separateFileSystemsLogNothing() {
    Devices devices = new Devices().on(COMMIT_LOG, 1).on("/d1", 2).on("/d2", 3);

    check(dirs("/d1", "/d2"), devices).execute(on());

    assertEquals(List.of(), warnings());
  }

  @Test
  public void offDoesNothing() {
    removeCounters();
    AtomicBoolean called = new AtomicBoolean();
    Supplier<String> commitLog =
        () -> {
          called.set(true);
          throw new AssertionError("the commit log directory was read with the check off");
        };
    Supplier<String[]> data =
        () -> {
          called.set(true);
          throw new AssertionError("the data directories were read with the check off");
        };
    CommitLogDiskCheck.FileSystemLookup lookup =
        directory -> {
          called.set(true);
          throw new AssertionError("a file system was looked up with the check off");
        };

    new CommitLogDiskCheck(commitLog, data, lookup).execute(new StartupChecksOptions());

    assertFalse("a supplier or the lookup was called with the check off", called.get());
    assertEquals("the check logged with the check off", List.of(), appender.list);
    for (String name : List.of(SHARED, UNREADABLE, FAILED)) {
      assertFalse(name + " exists with the check off", registered(name));
    }
  }

  @Test
  public void switchIsOffByDefault() {
    assertTrue(new StartupChecksOptions().isDisabled(check_commitlog_shared_disk));
  }

  @Test
  public void neverThrows() {
    Devices sharing = new Devices().on(COMMIT_LOG, 1).on("/d1", 1);
    check(dirs("/d1"), new Devices().on("/d1", 1).failing(COMMIT_LOG, new IOException("one")))
        .execute(on());
    check(
            dirs("/d1", "/d2"),
            new Devices()
                .on(COMMIT_LOG, 1)
                .on("/d2", 1)
                .failing("/d1", new UnsupportedOperationException("two")))
        .execute(on());
    check(
            () -> COMMIT_LOG,
            () -> {
              throw new IllegalStateException("three");
            },
            sharing)
        .execute(on());
    caseFour().execute(on());
    caseFive().execute(on());
    caseSix().execute(on());
  }

  @Test
  public void unreadableDirectoryWarns() {
    Devices devices =
        new Devices()
            .on(COMMIT_LOG, 1)
            .on("/d1", 2)
            .on("/d3", 3)
            .failing("/d2", new IOException("unreadable"));
    check(dirs("/d1", "/d2", "/d3"), devices).execute(on());
    assertEquals(List.of(unreadable("/d2")), warnings());

    appender.list.clear();
    Devices commitLogFails =
        new Devices().on("/d1", 2).on("/d2", 3).failing(COMMIT_LOG, new IOException("unreadable"));
    check(dirs("/d1", "/d2"), commitLogFails).execute(on());
    assertEquals(List.of(unreadable(COMMIT_LOG)), warnings());
  }

  @Test
  public void unreadableDirectoryDoesNotHideOthers() {
    check(dirs("/d1", "/d2", "/d3"), caseOfTestSeven()).execute(on());

    assertEquals(List.of(unreadable("/d2"), shared("[/d1, /d3]")), warnings());
  }

  @Test
  public void unreadableCommitLogEndsTheComparison() {
    Devices devices = caseOfTestEight();

    check(dirs("/d1", "/d2", "/d3"), devices).execute(on());

    assertEquals(List.of(COMMIT_LOG), devices.calls);
    assertTrue(warnings().stream().noneMatch(line -> line.endsWith(SHARED_TAIL)));
  }

  @Test
  public void countsSharedDirectories() {
    long before = count(SHARED);
    check(dirs("/d1", "/d2", "/d3", "/d1"), caseOfTestOne()).execute(on());
    assertTrue(registered(SHARED));
    assertEquals(2, count(SHARED) - before);

    before = count(SHARED);
    check(dirs("/d1", "/d2"), new Devices().on(COMMIT_LOG, 1).on("/d1", 2).on("/d2", 3))
        .execute(on());
    assertTrue(registered(SHARED));
    assertEquals(0, count(SHARED) - before);

    before = count(SHARED);
    check(dirs("/d1", "/d2", "/d3"), caseOfTestEight()).execute(on());
    assertTrue(registered(SHARED));
    assertEquals(0, count(SHARED) - before);
  }

  @Test
  public void countsUnreadableDirectories() {
    long before = count(UNREADABLE);
    check(dirs("/d1", "/d2", "/d3"), caseOfTestSeven()).execute(on());
    assertTrue(registered(UNREADABLE));
    assertEquals(1, count(UNREADABLE) - before);

    before = count(UNREADABLE);
    check(dirs("/d1", "/d2", "/d3"), caseOfTestEight()).execute(on());
    assertTrue(registered(UNREADABLE));
    assertEquals(1, count(UNREADABLE) - before);

    before = count(UNREADABLE);
    check(dirs("/d1", "/d2", "/d3", "/d1"), caseOfTestOne()).execute(on());
    assertTrue(registered(UNREADABLE));
    assertEquals(0, count(UNREADABLE) - before);
  }

  @Test
  public void failureOutsideALookupWarns() {
    commitLogSupplierFails().execute(on());
    assertEquals(List.of(FAILED_TEXT), warnings());

    appender.list.clear();
    caseSix().execute(on());
    assertEquals(List.of(FAILED_TEXT), warnings());
  }

  @Test
  public void registersTheCounters() {
    removeCounters();

    commitLogSupplierFails().execute(on());

    for (String name : List.of(SHARED, UNREADABLE, FAILED)) {
      assertTrue(name + " is not registered after a run", registered(name));
    }
  }

  @Test
  public void failureEndsTheRun() {
    Devices devices =
        new Devices()
            .on(COMMIT_LOG, 1)
            .on("/d1", 1)
            .on("/d3", 1)
            .failing("/d2", new IOException("unreadable"));
    org.slf4j.Logger real = LoggerFactory.getLogger(CommitLogDiskCheck.class);
    CommitLogDiskCheck.WarningLog log =
        (format, arguments) -> {
          if (format.equals(CommitLogDiskCheck.UNREADABLE_WARNING)) {
            throw new IllegalStateException("the log refused the unreadable warning");
          }
          real.warn(format, arguments);
        };
    long sharedBefore = count(SHARED);
    long failedBefore = count(FAILED);

    new CommitLogDiskCheck(
            () -> COMMIT_LOG,
            dirs("/d1", "/d2", "/d3"),
            devices,
            CommitLogDiskCheck::registerCounter,
            log)
        .execute(on());

    assertEquals(List.of(COMMIT_LOG, "/d1", "/d2"), devices.calls);
    assertEquals(List.of(FAILED_TEXT), warnings());
    assertEquals(0, count(SHARED) - sharedBefore);
    assertEquals(1, count(FAILED) - failedBefore);
  }

  @Test
  public void countsFailedRuns() {
    long before = count(FAILED);
    commitLogSupplierFails().execute(on());
    assertEquals(1, count(FAILED) - before);

    before = count(FAILED);
    caseFive().execute(on());
    assertEquals(1, count(FAILED) - before);
  }

  @Test
  public void registersFailedRunsFirst() {
    removeCounters();
    caseFour().execute(on());
    assertTrue(registered(FAILED));
    assertEquals(1, count(FAILED));
    assertFalse(registered(SHARED));

    removeCounters();
    registrarFailingFor(UNREADABLE).execute(on());
    assertTrue(registered(FAILED));
    assertEquals(1, count(FAILED));
    assertFalse(registered(UNREADABLE));
  }

  private static CommitLogDiskCheck caseFour() {
    return registrarFailingFor(SHARED);
  }

  private static CommitLogDiskCheck registrarFailingFor(String refused) {
    Function<String, LongConsumer> counters =
        name -> {
          if (name.equals(refused)) {
            throw new IllegalStateException("the registry refused " + name);
          }
          return CommitLogDiskCheck.registerCounter(name);
        };
    return new CommitLogDiskCheck(
        () -> COMMIT_LOG,
        dirs("/d1"),
        new Devices().on(COMMIT_LOG, 1).on("/d1", 1),
        counters,
        LoggerFactory.getLogger(CommitLogDiskCheck.class)::warn);
  }

  private static CommitLogDiskCheck caseFive() {
    return new CommitLogDiskCheck(
        () -> COMMIT_LOG,
        dirs("/d1"),
        new Devices().on(COMMIT_LOG, 1).on("/d1", 1),
        CommitLogDiskCheck::registerCounter,
        (format, arguments) -> {
          throw new IllegalStateException("the log refused a warning");
        });
  }

  private static CommitLogDiskCheck caseSix() {
    return new CommitLogDiskCheck(
        () -> COMMIT_LOG,
        dirs("/d1"),
        new Devices().on(COMMIT_LOG, 1).on("/d1", 1),
        name ->
            amount -> {
              throw new IllegalStateException("the counter refused a raise");
            },
        LoggerFactory.getLogger(CommitLogDiskCheck.class)::warn);
  }

  private static CommitLogDiskCheck commitLogSupplierFails() {
    return check(
        () -> {
          throw new IllegalStateException("no commit log directory");
        },
        dirs("/d1"),
        new Devices().on(COMMIT_LOG, 1).on("/d1", 1));
  }

  private static Devices caseOfTestOne() {
    return new Devices().on(COMMIT_LOG, 1).on("/d1", 1).on("/d2", 2).on("/d3", 1);
  }

  private static Devices caseOfTestSeven() {
    return new Devices()
        .on(COMMIT_LOG, 1)
        .on("/d1", 1)
        .on("/d3", 1)
        .failing("/d2", new IOException("unreadable"));
  }

  private static Devices caseOfTestEight() {
    return new Devices()
        .on("/d1", 1)
        .on("/d2", 1)
        .on("/d3", 1)
        .failing(COMMIT_LOG, new IOException("unreadable"));
  }

  private static CommitLogDiskCheck check(Supplier<String[]> data, Devices devices) {
    return check(() -> COMMIT_LOG, data, devices);
  }

  private static CommitLogDiskCheck check(
      Supplier<String> commitLog, Supplier<String[]> data, Devices devices) {
    return new CommitLogDiskCheck(commitLog, data, devices);
  }

  private static Supplier<String[]> dirs(String... directories) {
    return () -> directories.clone();
  }

  private static StartupChecksOptions on() {
    StartupChecksOptions options = new StartupChecksOptions();
    options.enable(check_commitlog_shared_disk);
    return options;
  }

  private static String shared(String dataDirectories) {
    return "The commit log directory "
        + COMMIT_LOG
        + " is on the same file system as the data directories "
        + dataDirectories
        + SHARED_TAIL;
  }

  private static String unreadable(String directory) {
    return "The startup check check_commitlog_shared_disk could not read the file system of "
        + directory
        + " and did not compare that directory.";
  }

  private List<String> warnings() {
    return appender.list.stream()
        .filter(event -> event.getLevel().isGreaterOrEqual(Level.WARN))
        .map(ILoggingEvent::getFormattedMessage)
        .collect(Collectors.toList());
  }

  private static void removeCounters() {
    for (String name : List.of(SHARED, UNREADABLE, FAILED)) {
      CassandraMetricsRegistry.Metrics.remove(CommitLogDiskCheck.metricName(name));
    }
  }

  private static boolean registered(String name) {
    return CassandraMetricsRegistry.Metrics.getCounters()
        .containsKey(CommitLogDiskCheck.metricName(name).getMetricName());
  }

  private static long count(String name) {
    Counter counter =
        CassandraMetricsRegistry.Metrics.getCounters()
            .get(CommitLogDiskCheck.metricName(name).getMetricName());
    return counter == null ? 0 : counter.getCount();
  }

  /** A file system lookup that answers a fixed device id for each directory, or throws. */
  private static final class Devices implements CommitLogDiskCheck.FileSystemLookup {
    private final Map<String, Long> ids = new HashMap<>();
    private final Map<String, Exception> failures = new HashMap<>();
    private final List<String> calls = new ArrayList<>();

    Devices on(String directory, long id) {
      ids.put(directory, id);
      return this;
    }

    Devices failing(String directory, Exception failure) {
      failures.put(directory, failure);
      return this;
    }

    @Override
    public long deviceId(String directory) throws IOException {
      calls.add(directory);
      Exception failure = failures.get(directory);
      if (failure instanceof IOException) {
        throw (IOException) failure;
      }
      if (failure != null) {
        throw (RuntimeException) failure;
      }
      return ids.get(directory);
    }
  }
}
