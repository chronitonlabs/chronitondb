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
import static org.junit.Assert.assertNotNull;
import static org.junit.Assert.assertTrue;

import java.io.IOException;
import java.io.InputStream;
import java.util.Properties;
import java.util.regex.Pattern;
import org.junit.Test;

/** The release version the build writes and the node reads. */
public class ReleaseVersionTest {
  private static final String RESOURCE = "org/apache/cassandra/config/version.properties";
  private static final Pattern RELEASE_FORM =
      Pattern.compile("5\\.0-chronitondb([1-9][0-9]*|-SNAPSHOT)");

  @Test
  public void readsTheKeyFromTheResource() throws IOException {
    String built = builtValue();
    assertNotNull("the build wrote no ReleaseVersion key", built);
    assertEquals(built.trim(), ReleaseVersion.fromClasspath().value());
  }

  @Test
  public void buildWritesTheKey() throws IOException {
    String built = builtValue();
    assertNotNull("the build wrote no ReleaseVersion key", built);
    assertFalse("the build wrote a blank ReleaseVersion", built.trim().isEmpty());
  }

  @Test
  public void valueHasTheReleaseForm() throws IOException {
    String built = builtValue();
    assertNotNull("the build wrote no ReleaseVersion key", built);
    assertTrue(
        "ReleaseVersion " + built + " does not have the release version form",
        RELEASE_FORM.matcher(built.trim()).matches());
  }

  private static String builtValue() throws IOException {
    try (InputStream in = ReleaseVersionTest.class.getClassLoader().getResourceAsStream(RESOURCE)) {
      assertNotNull("the build wrote no " + RESOURCE, in);
      Properties props = new Properties();
      props.load(in);
      return props.getProperty("ReleaseVersion");
    }
  }
}
