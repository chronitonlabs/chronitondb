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

package org.chronitondb.version;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;

import ch.qos.logback.classic.Level;
import ch.qos.logback.classic.Logger;
import ch.qos.logback.classic.spi.ILoggingEvent;
import ch.qos.logback.core.read.ListAppender;
import java.io.IOException;
import java.io.InputStream;
import java.lang.management.ManagementFactory;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Properties;
import javax.management.MBeanAttributeInfo;
import javax.management.MBeanInfo;
import javax.management.MBeanServer;
import javax.management.ObjectName;
import org.apache.cassandra.config.Config;
import org.apache.cassandra.config.DatabaseDescriptor;
import org.apache.cassandra.utils.MBeanWrapper;
import org.junit.After;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import org.slf4j.LoggerFactory;

/** The node side of the release version: the MBean, its switch, its counter and its log lines. */
public class ReleaseVersionReporterTest {
  private static final ObjectName NAME = name(ReleaseVersionReporterMBean.NAME);
  private static final ObjectName REPORTED =
      name("org.chronitondb.metrics:type=ReleaseVersion,name=Reported");
  private static final MBeanServer SERVER = ManagementFactory.getPlatformMBeanServer();
  private static final String MISSING = "org/chronitondb/version/no-such.properties";

  private final ListAppender<ILoggingEvent> appender = new ListAppender<>();
  private final Logger[] loggers = {
    (Logger) LoggerFactory.getLogger(ReleaseVersionReporter.class),
    (Logger) LoggerFactory.getLogger(ReleaseVersion.class),
    (Logger) LoggerFactory.getLogger(MBeanWrapper.class)
  };

  @BeforeClass
  public static void setUpClass() {
    DatabaseDescriptor.daemonInitialization();
  }

  @Before
  public void attachAppender() {
    appender.start();
    for (Logger logger : loggers) {
      logger.addAppender(appender);
    }
  }

  @After
  public void cleanUp() {
    for (Logger logger : loggers) {
      logger.detachAppender(appender);
    }
    appender.stop();
    if (MBeanWrapper.instance.isRegistered(NAME)) {
      MBeanWrapper.instance.unregisterMBean(NAME);
    }
    DatabaseDescriptor.getRawConfig().nodetool_release_version_enabled = true;
  }

  @Test
  public void registerCreatesTheMBean() throws Exception {
    reporter("5.0-chronitondb7").register();
    assertTrue(MBeanWrapper.instance.isRegistered(NAME));

    MBeanInfo info = SERVER.getMBeanInfo(NAME);
    Map<String, MBeanAttributeInfo> attributes = new HashMap<>();
    for (MBeanAttributeInfo attribute : info.getAttributes()) {
      attributes.put(attribute.getName(), attribute);
    }
    assertEquals("java.lang.String", attributes.get("ReleaseVersion").getType());
    assertFalse(attributes.get("ReleaseVersion").isWritable());
    assertEquals("boolean", attributes.get("Enabled").getType());
    assertTrue(attributes.get("Enabled").isWritable());
  }

  @Test
  public void registerLogsReleaseVersion() {
    reporter("5.0-chronitondb7").register();
    assertEquals(1, count(Level.INFO, "ChronitonDB release version: 5.0-chronitondb7"));
  }

  @Test
  public void registerFailureIsLogged() {
    reporter("5.0-chronitondb7").register();
    reporter("5.0-chronitondb8").register();
    assertTrue(MBeanWrapper.instance.isRegistered(NAME));
    assertEquals(1, count(Level.ERROR, "Error in MBean wrapper: "));
    assertEquals(1, count(Level.INFO, "ChronitonDB release version: 5.0-chronitondb8"));
  }

  @Test
  public void attributeIsUnknownWithoutValue() {
    Properties blank = new Properties();
    blank.setProperty(ReleaseVersion.KEY, "   ");
    InputStream broken =
        new InputStream() {
          @Override
          public int read() throws IOException {
            throw new IOException("stub read failure");
          }
        };

    assertEquals("Unknown", answer(ReleaseVersion.fromProperties(new Properties())));
    assertEquals("Unknown", answer(ReleaseVersion.fromProperties(blank)));
    assertEquals("Unknown", answer(ReleaseVersion.fromResource(MISSING)));
    assertEquals(0, warnings());
    assertEquals("Unknown", answer(ReleaseVersion.fromStream(broken)));
    assertEquals(1, warnings());
  }

  @Test
  public void enabledReadsTheSwitch() {
    ReleaseVersionReporter reporter = reporter("5.0-chronitondb7");
    DatabaseDescriptor.getRawConfig().nodetool_release_version_enabled = false;
    assertFalse(reporter.isEnabled());
    DatabaseDescriptor.getRawConfig().nodetool_release_version_enabled = true;
    assertTrue(reporter.isEnabled());
  }

  @Test
  public void switchDefaultsToOn() {
    assertTrue(new Config().nodetool_release_version_enabled);
  }

  @Test
  public void writeLogsOldAndNewValue() {
    ReleaseVersionReporter reporter = reporter("5.0-chronitondb7");
    DatabaseDescriptor.getRawConfig().nodetool_release_version_enabled = true;

    reporter.setEnabled(false);
    assertFalse(reporter.isEnabled());
    assertFalse(DatabaseDescriptor.getRawConfig().nodetool_release_version_enabled);
    assertEquals(
        1, count(Level.INFO, "Changed nodetool_release_version_enabled from true to false"));

    reporter.setEnabled(false);
    assertEquals(
        1, count(Level.INFO, "Changed nodetool_release_version_enabled from false to false"));
  }

  @Test
  public void readCountsReported() throws Exception {
    ReleaseVersionReporter reporter = reporter("5.0-chronitondb7");
    reporter.register();

    long before = reported();
    reporter.getReleaseVersion();
    assertEquals(before + 1, reported());

    reporter.setEnabled(false);
    reporter.getReleaseVersion();
    assertEquals(before + 2, reported());
  }

  @Test
  public void reporterStaysRegisteredWhenOff() {
    ReleaseVersionReporter reporter = reporter("5.0-chronitondb7");
    reporter.register();
    reporter.setEnabled(false);
    assertTrue(MBeanWrapper.instance.isRegistered(NAME));
  }

  private static ReleaseVersionReporter reporter(String value) {
    Properties props = new Properties();
    props.setProperty(ReleaseVersion.KEY, value);
    return new ReleaseVersionReporter(ReleaseVersion.fromProperties(props));
  }

  private static String answer(ReleaseVersion releaseVersion) {
    return new ReleaseVersionReporter(releaseVersion).getReleaseVersion();
  }

  private long warnings() {
    return appender.list.stream().filter(e -> e.getLevel() == Level.WARN).count();
  }

  private long count(Level level, String message) {
    List<ILoggingEvent> events = appender.list;
    return events.stream()
        .filter(e -> e.getLevel() == level && e.getFormattedMessage().equals(message))
        .count();
  }

  private static long reported() throws Exception {
    return (Long) SERVER.getAttribute(REPORTED, "Count");
  }

  private static ObjectName name(String name) {
    try {
      return new ObjectName(name);
    } catch (Exception e) {
      throw new IllegalArgumentException(name, e);
    }
  }
}
