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

import javax.management.MBeanServerConnection;
import org.apache.cassandra.tools.NodeProbe;
import org.chronitondb.version.ReleaseVersionReporterMBean;

/** What nodetool version prints on a node that reports its ChronitonDB release version. */
public final class VersionOutput {
  private VersionOutput() {}

  /**
   * Prints the node's release version, and with verbose the git SHA, then returns true. Returns
   * false and prints nothing when the probe has no connection, the node has no reporter, its
   * switch is off, or the role may not read the reporter: the caller then prints its own lines.
   */
  public static boolean print(NodeProbe probe, boolean verbose) {
    MBeanServerConnection connection = probe.getMbeanServerConn();
    if (connection == null) {
      return false;
    }
    String releaseVersion;
    try {
      ReleaseVersionReporterMBean reporter = ReleaseVersionProbe.find(connection);
      if (reporter == null || !reporter.isEnabled()) {
        return false;
      }
      releaseVersion = reporter.getReleaseVersion();
    } catch (SecurityException e) {
      return false;
    }
    probe.output().out.println("ReleaseVersion: " + releaseVersion);
    if (verbose) {
      probe.output().out.println("GitSHA: " + probe.getGitSHA());
    }
    return true;
  }
}
