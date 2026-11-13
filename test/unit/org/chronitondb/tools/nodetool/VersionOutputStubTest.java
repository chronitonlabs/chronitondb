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

package org.chronitondb.tools.nodetool;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.PrintStream;
import java.lang.reflect.Proxy;
import java.nio.charset.StandardCharsets;
import javax.management.MBeanServerConnection;
import org.apache.cassandra.service.StorageServiceMBean;
import org.apache.cassandra.tools.INodeProbeFactory;
import org.apache.cassandra.tools.NodeProbe;
import org.apache.cassandra.tools.NodeTool;
import org.apache.cassandra.tools.Output;
import org.junit.Test;

/**
 * nodetool against a stub JMX connection, through the real entry point, so that each failure of
 * the connection can be made on purpose.
 */
public class VersionOutputStubTest {
  private static final String NL = System.lineSeparator();
  private static final String STOCK_VERSION = "5.0.10-stub";
  private static final String STOCK_SHA = "stub-sha";
  private static final String NO_REPORTER =
      ": the node has no ChronitonDB release version reporter. It runs Apache Cassandra or an"
          + " older ChronitonDB build, or the reporter failed to register at start.";
  private static final String HELP_LINE = "See 'nodetool help' or 'nodetool help <command>'.";

  @Test
  public void printsTheNodesOwnValue() {
    StubConnection conn = new StubConnection();
    conn.release = "stub-release";

    Result plain = run(conn, "version");
    assertEquals(0, plain.status);
    assertEquals("ReleaseVersion: stub-release" + NL, plain.out);
    assertEquals("", plain.err);

    Result verbose = run(conn, "version", "--verbose");
    assertEquals(0, verbose.status);
    assertEquals("ReleaseVersion: stub-release" + NL + "GitSHA: " + STOCK_SHA + NL, verbose.out);
    assertEquals("", verbose.err);
  }

  @Test
  public void accessDeniedPrintsStockOutput() {
    StubConnection onLookup = new StubConnection();
    onLookup.onIsRegistered = new SecurityException("Access Denied");
    StubConnection onEnabled = new StubConnection();
    onEnabled.onEnabled = new SecurityException("Access Denied");
    StubConnection onRelease = new StubConnection();
    onRelease.onRelease = new SecurityException("Access Denied");

    assertStockOutput(onLookup);
    assertStockOutput(onEnabled);
    assertStockOutput(onRelease);
  }

  @Test
  public void noConnectionPrintsStockOutput() {
    assertStockOutput(null);
  }

  @Test
  public void otherFailureReportsAsStock() {
    StubConnection onLookup = new StubConnection();
    onLookup.onIsRegistered = new IOException("stub io failure");
    StubConnection onEnabled = new StubConnection();
    onEnabled.onEnabled = new IOException("stub io failure");
    StubConnection onRelease = new StubConnection();
    onRelease.onRelease = new IOException("stub io failure");

    for (StubConnection conn : new StubConnection[] {onLookup, onEnabled, onRelease}) {
      assertStockError(run(conn, "version"), "stub io failure");
      assertStockError(run(conn, "version", "--verbose"), "stub io failure");
    }
  }

  @Test
  public void enableAgainstStubWithoutReporterFails() {
    assertWithoutReporter("enablereleaseversion");
  }

  @Test
  public void disableAgainstStubWithoutReporterFails() {
    assertWithoutReporter("disablereleaseversion");
  }

  @Test
  public void enableWithoutConnectionFails() {
    assertUsageError(
        run(null, "enablereleaseversion"), "enablereleaseversion needs a JMX connection");
  }

  @Test
  public void disableWithoutConnectionFails() {
    assertUsageError(
        run(null, "disablereleaseversion"), "disablereleaseversion needs a JMX connection");
  }

  @Test
  public void enableFailureReportsAsStock() {
    assertToggleFailures("enablereleaseversion");
  }

  @Test
  public void disableFailureReportsAsStock() {
    assertToggleFailures("disablereleaseversion");
  }

  private static void assertWithoutReporter(String command) {
    StubConnection conn = new StubConnection();
    conn.registered = false;
    assertUsageError(run(conn, command), command + NO_REPORTER);
  }

  private static void assertToggleFailures(String command) {
    StubConnection onLookup = new StubConnection();
    onLookup.onIsRegistered = new SecurityException("Access Denied");
    StubConnection onWrite = new StubConnection();
    onWrite.onSet = new SecurityException("Access Denied");
    StubConnection onWriteIo = new StubConnection();
    onWriteIo.onSet = new IOException("stub io failure");

    assertStockError(run(onLookup, command), "Access Denied");
    assertStockError(run(onWrite, command), "Access Denied");
    assertStockError(run(onWriteIo, command), "stub io failure");
  }

  private static void assertStockOutput(StubConnection conn) {
    Result plain = run(conn, "version");
    assertEquals(0, plain.status);
    assertEquals("ReleaseVersion: " + STOCK_VERSION + NL, plain.out);
    assertEquals("", plain.err);

    Result verbose = run(conn, "version", "--verbose");
    assertEquals(0, verbose.status);
    assertEquals(
        "ReleaseVersion: " + STOCK_VERSION + NL + "GitSHA: " + STOCK_SHA + NL, verbose.out);
    assertEquals("", verbose.err);
  }

  private static void assertStockError(Result result, String message) {
    assertEquals(2, result.status);
    assertEquals("", result.out);
    assertTrue(result.err, result.err.startsWith("error: " + message + NL + "-- StackTrace --"));
  }

  private static void assertUsageError(Result result, String message) {
    assertEquals(1, result.status);
    assertEquals("nodetool: " + message + NL + HELP_LINE + NL, result.out);
    assertEquals("", result.err);
  }

  private static Result run(StubConnection conn, String... args) {
    ByteArrayOutputStream out = new ByteArrayOutputStream();
    ByteArrayOutputStream err = new ByteArrayOutputStream();
    Output output =
        new Output(
            new PrintStream(out, true, StandardCharsets.UTF_8),
            new PrintStream(err, true, StandardCharsets.UTF_8));
    MBeanServerConnection connection = conn == null ? null : conn.proxy();
    int status = new NodeTool(new StubFactory(connection), output).execute(args);
    return new Result(
        status, out.toString(StandardCharsets.UTF_8), err.toString(StandardCharsets.UTF_8));
  }

  private static final class Result {
    final int status;
    final String out;
    final String err;

    Result(int status, String out, String err) {
      this.status = status;
      this.out = out;
      this.err = err;
    }
  }

  /** A JMX connection that answers the release version calls, or throws what a test sets. */
  private static final class StubConnection {
    boolean registered = true;
    boolean enabled = true;
    String release = "stub-release";
    Exception onIsRegistered;
    Exception onEnabled;
    Exception onRelease;
    Exception onSet;

    MBeanServerConnection proxy() {
      return (MBeanServerConnection)
          Proxy.newProxyInstance(
              getClass().getClassLoader(),
              new Class<?>[] {MBeanServerConnection.class},
              (target, method, args) -> answer(method.getName(), args));
    }

    private Object answer(String method, Object[] args) throws Exception {
      switch (method) {
        case "isRegistered":
          throwIfSet(onIsRegistered);
          return registered;
        case "getAttribute":
          if ("Enabled".equals(args[1])) {
            throwIfSet(onEnabled);
            return enabled;
          }
          throwIfSet(onRelease);
          return release;
        case "setAttribute":
          throwIfSet(onSet);
          return null;
        default:
          throw new UnsupportedOperationException(method);
      }
    }

    private static void throwIfSet(Exception e) throws Exception {
      if (e != null) {
        throw e;
      }
    }
  }

  /** Hands nodetool a probe on the stub connection, as the in-JVM test framework does. */
  private static final class StubFactory implements INodeProbeFactory {
    private final MBeanServerConnection connection;

    StubFactory(MBeanServerConnection connection) {
      this.connection = connection;
    }

    @Override
    public NodeProbe create(String host, int port) {
      return new StubProbe(connection);
    }

    @Override
    public NodeProbe create(String host, int port, String username, String password) {
      return new StubProbe(connection);
    }
  }

  private static final class StubProbe extends NodeProbe {
    private final MBeanServerConnection connection;

    StubProbe(MBeanServerConnection connection) {
      this.connection = connection;
      connect();
    }

    @Override
    protected void connect() {
      mbeanServerConn = connection;
      ssProxy =
          (StorageServiceMBean)
              Proxy.newProxyInstance(
                  getClass().getClassLoader(),
                  new Class<?>[] {StorageServiceMBean.class},
                  (target, method, args) -> storageService(method.getName()));
    }

    @Override
    public void close() {}

    private static Object storageService(String method) {
      switch (method) {
        case "getReleaseVersion":
          return STOCK_VERSION;
        case "getGitSHA":
          return STOCK_SHA;
        default:
          throw new UnsupportedOperationException(method);
      }
    }
  }
}
