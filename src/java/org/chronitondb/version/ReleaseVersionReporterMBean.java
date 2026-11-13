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

/** Reports the node's ChronitonDB release version over JMX and holds the switch nodetool reads. */
public interface ReleaseVersionReporterMBean {
  /** The JMX name of the reporter, read by the node and by nodetool. */
  String NAME = "org.chronitondb:type=ReleaseVersion";

  /** The release version of the build, whatever the switch says. */
  String getReleaseVersion();

  /** Whether nodetool version prints the release version: nodetool_release_version_enabled. */
  boolean isEnabled();

  /** Sets nodetool_release_version_enabled in memory, until the next restart. */
  void setEnabled(boolean enabled);
}
