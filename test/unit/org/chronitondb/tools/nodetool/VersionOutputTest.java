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
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;

import java.io.IOException;
import java.io.InputStream;
import java.util.Properties;
import javax.management.ObjectName;
import org.apache.cassandra.config.DatabaseDescriptor;
import org.apache.cassandra.cql3.CQLTester;
import org.apache.cassandra.tools.NodeProbe;
import org.apache.cassandra.tools.ToolRunner;
import org.apache.cassandra.utils.FBUtilities;
import org.apache.cassandra.utils.MBeanWrapper;
import org.chronitondb.version.ReleaseVersion;
import org.chronitondb.version.ReleaseVersionReporter;
import org.chronitondb.version.ReleaseVersionReporterMBean;
import org.junit.After;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;

/** nodetool, run as its own process, against a node started in this JVM over real JMX. */
public class VersionOutputTest extends CQLTester {
  private static final String NL = System.lineSeparator();
  private static final String HELP_LINE = "See 'nodetool help' or 'nodetool help <command>'.";
  private static final String NO_REPORTER =
      ": the node has no ChronitonDB release version reporter. It runs Apache Cassandra or an"
          + " older ChronitonDB build, or the reporter failed to register at start.";

  private static ObjectName name;
  private static boolean registeredAtStart;

  @BeforeClass
  public static void setUpNode() throws Exception {
    requireNetwork();
    name = new ObjectName(ReleaseVersionReporterMBean.NAME);
    registeredAtStart = MBeanWrapper.instance.isRegistered(name);
    startJMXServer();
  }

  @Before
  public void switchOn() {
    ReleaseVersionReporter.instance.setEnabled(true);
  }

  @After
  public void restoreReporter() {
    if (!MBeanWrapper.instance.isRegistered(name)) {
      ReleaseVersionReporter.instance.register();
    }
    ReleaseVersionReporter.instance.setEnabled(true);
  }

  @Test
  public void initServerRegistersTheMBean() {
    assertTrue("initServer did not register " + name, registeredAtStart);
  }

  @Test
  public void versionPrintsReleaseVersion() {
    ToolRunner.ToolResult result = ToolRunner.invokeNodetool("version");
    result.assertOnCleanExit();
    assertEquals(releaseLine(), result.getStdout());
  }

  @Test
  public void verbosePrintsGitSha() {
    ToolRunner.ToolResult result = ToolRunner.invokeNodetool("version", "--verbose");
    result.assertOnCleanExit();
    assertEquals(releaseLine() + shaLine(), result.getStdout());
  }

  @Test
  public void disableSetsSwitchOff() {
    ToolRunner.ToolResult result = ToolRunner.invokeNodetool("disablereleaseversion");
    result.assertOnCleanExit();
    assertEquals("", result.getStdout());
    assertFalse(DatabaseDescriptor.getRawConfig().nodetool_release_version_enabled);
  }

  @Test
  public void switchOffPrintsStockOutput() {
    ReleaseVersionReporter.instance.setEnabled(false);
    assertStockOutput();
  }

  @Test
  public void enableSetsSwitchOn() {
    ReleaseVersionReporter.instance.setEnabled(false);
    ToolRunner.ToolResult result = ToolRunner.invokeNodetool("enablereleaseversion");
    result.assertOnCleanExit();
    assertEquals("", result.getStdout());
    assertTrue(DatabaseDescriptor.getRawConfig().nodetool_release_version_enabled);
  }

  @Test
  public void apacheVersionStringUnchanged() throws IOException {
    String built = builtCassandraVersion();
    try (NodeProbe probe = new NodeProbe(jmxHost, jmxPort)) {
      assertEquals(built, probe.getReleaseVersion());
      ReleaseVersionReporter.instance.setEnabled(false);
      assertEquals(built, probe.getReleaseVersion());
    }
  }

  @Test
  public void nodeWithoutReporterPrintsStockOutput() {
    MBeanWrapper.instance.unregisterMBean(name);
    assertStockOutput();
  }

  @Test
  public void enableAgainstNodeWithoutReporterFails() {
    MBeanWrapper.instance.unregisterMBean(name);
    assertUsageError("enablereleaseversion");
  }

  @Test
  public void disableAgainstNodeWithoutReporterFails() {
    MBeanWrapper.instance.unregisterMBean(name);
    assertUsageError("disablereleaseversion");
  }

  private static void assertStockOutput() {
    String stockLine = "ReleaseVersion: " + FBUtilities.getReleaseVersionString() + NL;

    ToolRunner.ToolResult plain = ToolRunner.invokeNodetool("version");
    plain.assertOnCleanExit();
    assertEquals(stockLine, plain.getStdout());

    ToolRunner.ToolResult verbose = ToolRunner.invokeNodetool("version", "--verbose");
    verbose.assertOnCleanExit();
    assertEquals(stockLine + shaLine(), verbose.getStdout());
  }

  private static void assertUsageError(String command) {
    ToolRunner.ToolResult result = ToolRunner.invokeNodetool(command);
    assertEquals(1, result.getExitCode());
    assertEquals("nodetool: " + command + NO_REPORTER + NL + HELP_LINE + NL, result.getStdout());
  }

  private static String releaseLine() {
    return "ReleaseVersion: " + ReleaseVersion.fromClasspath().value() + NL;
  }

  private static String shaLine() {
    return "GitSHA: " + FBUtilities.getGitSHA() + NL;
  }

  private static String builtCassandraVersion() throws IOException {
    String resource = "org/apache/cassandra/config/version.properties";
    try (InputStream in = VersionOutputTest.class.getClassLoader().getResourceAsStream(resource)) {
      Properties props = new Properties();
      props.load(in);
      return props.getProperty("CassandraVersion");
    }
  }
}
