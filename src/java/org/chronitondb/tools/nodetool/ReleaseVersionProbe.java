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

import java.io.IOException;
import javax.management.JMX;
import javax.management.MBeanServerConnection;
import javax.management.MalformedObjectNameException;
import javax.management.ObjectName;
import org.apache.cassandra.tools.NodeProbe;
import org.chronitondb.version.ReleaseVersionReporterMBean;

/** Finds the node's release version reporter over the JMX connection of a nodetool probe. */
final class ReleaseVersionProbe {
  private static final ObjectName NAME = objectName();

  private ReleaseVersionProbe() {}

  /**
   * The reporter of the node, or null when the node has none. A SecurityException from the
   * connection reaches the caller as it is. Any other failure is wrapped, with its cause.
   */
  static ReleaseVersionReporterMBean find(MBeanServerConnection connection) {
    try {
      if (!connection.isRegistered(NAME)) {
        return null;
      }
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
    return JMX.newMBeanProxy(connection, NAME, ReleaseVersionReporterMBean.class);
  }

  /** Sets the switch on the node, for the enable and disable commands. */
  static void setEnabled(NodeProbe probe, String command, boolean enabled) {
    MBeanServerConnection connection = probe.getMbeanServerConn();
    if (connection == null) {
      throw new IllegalStateException(command + " needs a JMX connection");
    }
    ReleaseVersionReporterMBean reporter = find(connection);
    if (reporter == null) {
      throw new IllegalStateException(
          command
              + ": the node has no ChronitonDB release version reporter. It runs Apache Cassandra"
              + " or an older ChronitonDB build, or the reporter failed to register at start.");
    }
    reporter.setEnabled(enabled);
  }

  private static ObjectName objectName() {
    try {
      return new ObjectName(ReleaseVersionReporterMBean.NAME);
    } catch (MalformedObjectNameException e) {
      throw new IllegalStateException(e);
    }
  }
}
