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

import com.codahale.metrics.Counter;
import org.apache.cassandra.config.Config;
import org.apache.cassandra.config.DatabaseDescriptor;
import org.apache.cassandra.metrics.CassandraMetricsRegistry;
import org.apache.cassandra.utils.MBeanWrapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * The node side of the release version. It answers the release version over JMX, holds the
 * switch nodetool reads, and counts each read of the release version.
 */
public final class ReleaseVersionReporter implements ReleaseVersionReporterMBean {
  private static final Logger logger = LoggerFactory.getLogger(ReleaseVersionReporter.class);
  private static final CassandraMetricsRegistry.MetricName REPORTED =
      new CassandraMetricsRegistry.MetricName(
          "org.chronitondb.metrics",
          "ReleaseVersion",
          "Reported",
          null,
          "org.chronitondb.metrics:type=ReleaseVersion,name=Reported");

  /** The reporter of this node, registered by StorageService at start. */
  public static final ReleaseVersionReporter instance =
      new ReleaseVersionReporter(ReleaseVersion.fromClasspath());

  private final ReleaseVersion releaseVersion;
  private final Counter reported;

  ReleaseVersionReporter(ReleaseVersion releaseVersion) {
    this.releaseVersion = releaseVersion;
    this.reported = CassandraMetricsRegistry.Metrics.counter(REPORTED);
  }

  /**
   * Registers the MBean and logs the release version. A failed registration is logged by the
   * wrapper and never stops the node.
   */
  public void register() {
    MBeanWrapper.instance.registerMBean(this, NAME, MBeanWrapper.OnException.LOG);
    logger.info("ChronitonDB release version: {}", releaseVersion.value());
  }

  @Override
  public String getReleaseVersion() {
    reported.inc();
    return releaseVersion.value();
  }

  @Override
  public boolean isEnabled() {
    return DatabaseDescriptor.getRawConfig().nodetool_release_version_enabled;
  }

  @Override
  public void setEnabled(boolean enabled) {
    Config config = DatabaseDescriptor.getRawConfig();
    boolean old = config.nodetool_release_version_enabled;
    config.nodetool_release_version_enabled = enabled;
    logger.info("Changed nodetool_release_version_enabled from {} to {}", old, enabled);
  }
}
