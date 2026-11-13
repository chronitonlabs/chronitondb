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

import com.google.common.base.Supplier;
import com.google.common.base.Suppliers;
import java.io.InputStream;
import java.util.Properties;
import org.apache.cassandra.utils.FBUtilities;
import org.apache.cassandra.utils.JVMStabilityInspector;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * The ChronitonDB release version of this build, read from the properties file the build writes.
 * The value is {@code Unknown} when the file, the key or a value that is not blank is missing.
 */
public final class ReleaseVersion {
  /** The classpath resource the build writes, shared with the Apache Cassandra version. */
  static final String RESOURCE = "org/apache/cassandra/config/version.properties";

  /** The key the build writes the release version under. */
  static final String KEY = "ReleaseVersion";

  private static final Logger logger = LoggerFactory.getLogger(ReleaseVersion.class);
  private static final Supplier<ReleaseVersion> fromClasspath =
      Suppliers.memoize(() -> fromResource(RESOURCE));

  private final String value;

  private ReleaseVersion(String value) {
    this.value = value;
  }

  /** The release version of the running build, read once. */
  public static ReleaseVersion fromClasspath() {
    return fromClasspath.get();
  }

  static ReleaseVersion fromResource(String resource) {
    InputStream in = ReleaseVersion.class.getClassLoader().getResourceAsStream(resource);
    if (in == null) {
      return new ReleaseVersion(FBUtilities.UNKNOWN_RELEASE_VERSION);
    }
    return fromStream(in);
  }

  static ReleaseVersion fromStream(InputStream input) {
    try (InputStream in = input) {
      Properties props = new Properties();
      props.load(in);
      return fromProperties(props);
    } catch (Exception e) {
      JVMStabilityInspector.inspectThrowable(e);
      logger.warn("Unable to load the release version from {}", RESOURCE, e);
      return new ReleaseVersion(FBUtilities.UNKNOWN_RELEASE_VERSION);
    }
  }

  static ReleaseVersion fromProperties(Properties props) {
    String raw = props.getProperty(KEY);
    if (raw == null || raw.trim().isEmpty()) {
      return new ReleaseVersion(FBUtilities.UNKNOWN_RELEASE_VERSION);
    }
    return new ReleaseVersion(raw.trim());
  }

  /** The release version, for example {@code 5.0-chronitondb3}, or {@code Unknown}. */
  public String value() {
    return value;
  }
}
