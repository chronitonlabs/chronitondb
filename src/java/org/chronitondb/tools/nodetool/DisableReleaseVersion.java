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

import io.airlift.airline.Command;
import org.apache.cassandra.tools.NodeProbe;
import org.apache.cassandra.tools.NodeTool.NodeToolCmd;

/** Turns nodetool_release_version_enabled off, in memory. */
@Command(
    name = "disablereleaseversion",
    description = "Show the Apache Cassandra version in nodetool version, until restart")
public class DisableReleaseVersion extends NodeToolCmd {
  @Override
  public void execute(NodeProbe probe) {
    ReleaseVersionProbe.setEnabled(probe, "disablereleaseversion", false);
  }
}
