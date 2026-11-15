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

import com.codahale.metrics.Counter;
import com.google.common.annotations.VisibleForTesting;
import java.io.IOException;
import java.nio.file.Files;
import java.util.ArrayList;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Set;
import java.util.function.Function;
import java.util.function.LongConsumer;
import java.util.function.Supplier;
import org.apache.cassandra.config.DatabaseDescriptor;
import org.apache.cassandra.config.StartupChecksOptions;
import org.apache.cassandra.io.util.File;
import org.apache.cassandra.metrics.CassandraMetricsRegistry;
import org.apache.cassandra.service.StartupCheck;
import org.apache.cassandra.service.StartupChecks.StartupCheckType;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * A startup check that warns when the commit log directory is on the same file system as one or
 * more data directories. It is off by default and never stops the node: every failure inside a run
 * ends in a warning and a count.
 */
public final class CommitLogDiskCheck implements StartupCheck {
  static final String SHARED_WARNING =
      "The commit log directory {} is on the same file system as the data directories {}. One"
          + " failure of that file system loses the commit log and the data together, and on"
          + " spinning disks commit log writes compete with reads, flushes and compaction. Put"
          + " commitlog_directory on a file system of its own. This warning comes from the startup"
          + " check check_commitlog_shared_disk.";
  static final String UNREADABLE_WARNING =
      "The startup check check_commitlog_shared_disk could not read the file system of {} and did"
          + " not compare that directory.";
  static final String FAILED_WARNING =
      "The startup check check_commitlog_shared_disk failed and compared nothing more.";

  private static final Logger logger = LoggerFactory.getLogger(CommitLogDiskCheck.class);
  private static final String METRIC_GROUP = "org.chronitondb.metrics";
  private static final String METRIC_TYPE = "CommitLogDiskCheck";
  private static final String FAILED_RUNS = "FailedRuns";
  private static final String SHARED_DATA_DIRECTORIES = "SharedDataDirectories";
  private static final String UNREADABLE_DIRECTORIES = "UnreadableDirectories";

  private final Supplier<String> commitLogDirectory;
  private final Supplier<String[]> dataDirectories;
  private final FileSystemLookup lookup;
  private final Function<String, LongConsumer> counters;
  private final WarningLog warnings;

  /** The check the daemon registers. It reads nothing until it runs. */
  public CommitLogDiskCheck() {
    this(
        DatabaseDescriptor::getCommitLogLocation,
        DatabaseDescriptor::getAllDataFileLocations,
        CommitLogDiskCheck::deviceId);
  }

  @VisibleForTesting
  CommitLogDiskCheck(
      Supplier<String> commitLogDirectory,
      Supplier<String[]> dataDirectories,
      FileSystemLookup lookup) {
    this(
        commitLogDirectory,
        dataDirectories,
        lookup,
        CommitLogDiskCheck::registerCounter,
        logger::warn);
  }

  @VisibleForTesting
  CommitLogDiskCheck(
      Supplier<String> commitLogDirectory,
      Supplier<String[]> dataDirectories,
      FileSystemLookup lookup,
      Function<String, LongConsumer> counters,
      WarningLog warnings) {
    this.commitLogDirectory = commitLogDirectory;
    this.dataDirectories = dataDirectories;
    this.lookup = lookup;
    this.counters = counters;
    this.warnings = warnings;
  }

  @Override
  public StartupCheckType getStartupCheckType() {
    return check_commitlog_shared_disk;
  }

  @Override
  public void execute(StartupChecksOptions options) {
    if (options.isDisabled(getStartupCheckType())) {
      return;
    }
    LongConsumer failedRuns = null;
    try {
      failedRuns = counters.apply(FAILED_RUNS);
      LongConsumer shared = counters.apply(SHARED_DATA_DIRECTORIES);
      LongConsumer unreadable = counters.apply(UNREADABLE_DIRECTORIES);
      compare(shared, unreadable);
    } catch (Exception failure) {
      endFailedRun(failedRuns, failure);
    }
  }

  private void compare(LongConsumer shared, LongConsumer unreadable) {
    String commitLog = commitLogDirectory.get();
    Set<String> data = new LinkedHashSet<>(List.of(dataDirectories.get()));
    long commitLogDevice;
    try {
      commitLogDevice = lookup.deviceId(commitLog);
    } catch (Exception failure) {
      unreadable(unreadable, commitLog, failure);
      return;
    }
    List<String> sharing = new ArrayList<>();
    for (String directory : data) {
      try {
        if (lookup.deviceId(directory) == commitLogDevice) {
          sharing.add(directory);
        }
      } catch (Exception failure) {
        unreadable(unreadable, directory, failure);
      }
    }
    if (!sharing.isEmpty()) {
      shared.accept(sharing.size());
      warnings.warn(SHARED_WARNING, commitLog, sharing);
    }
  }

  /**
   * Counts and logs a directory whose lookup threw. A failure of the count or of the log is no
   * lookup failure, so it leaves this method and ends the run.
   */
  private void unreadable(LongConsumer unreadable, String directory, Exception cause) {
    unreadable.accept(1);
    warnings.warn(UNREADABLE_WARNING, directory, cause);
  }

  /**
   * Ends a failed run with its count and its warning. Each has a guard of its own, so neither stops
   * the other and nothing leaves the check.
   */
  private void endFailedRun(LongConsumer failedRuns, Exception cause) {
    if (failedRuns != null) {
      try {
        failedRuns.accept(1);
      } catch (Exception failure) {
        cause.addSuppressed(failure);
      }
    }
    try {
      warnings.warn(FAILED_WARNING, cause);
    } catch (Exception ignored) {
      // The log refused the warning, so nothing is left that could report this run.
    }
  }

  @VisibleForTesting
  static CassandraMetricsRegistry.MetricName metricName(String name) {
    return new CassandraMetricsRegistry.MetricName(
        METRIC_GROUP,
        METRIC_TYPE,
        name,
        null,
        METRIC_GROUP + ":type=" + METRIC_TYPE + ",name=" + name);
  }

  @VisibleForTesting
  static LongConsumer registerCounter(String name) {
    Counter counter = CassandraMetricsRegistry.Metrics.counter(metricName(name));
    return counter::inc;
  }

  private static long deviceId(String directory) throws IOException {
    return (Long) Files.getAttribute(new File(directory).toPath(), "unix:dev");
  }

  /** Looks up the device id of the file system that holds a directory. */
  @FunctionalInterface
  interface FileSystemLookup {
    long deviceId(String directory) throws IOException;
  }

  /** Logs one warning, with SLF4J placeholders and an optional exception as the last argument. */
  @FunctionalInterface
  interface WarningLog {
    void warn(String format, Object... arguments);
  }
}
