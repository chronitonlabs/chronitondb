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

import static org.junit.Assert.assertTrue;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import org.junit.Test;

/** The reference page and the news file carry the lines operators rely on. */
public class ReleaseVersionDocsTest {
  private static final String PAGE = "docs/reference/release-version.md";
  private static final String NEWS = "NEWS-chronitondb.txt";
  private static final String MBEAN = "org.chronitondb:type=ReleaseVersion";
  private static final String[] ROLLBACK = {
    "nodetool_release_version_enabled", "cassandra.yaml", "Apache Cassandra", "older"
  };

  @Test
  public void rollbackLineOnReferencePage() throws IOException {
    assertLine(PAGE, ROLLBACK);
  }

  @Test
  public void rollbackLineInNews() throws IOException {
    assertLine(NEWS, ROLLBACK);
  }

  @Test
  public void permissionsAreDocumented() throws IOException {
    assertLine(PAGE, MBEAN, "DESCRIBE", "SELECT");
    assertLine(PAGE, MBEAN, "DESCRIBE", "MODIFY");
    assertLine(PAGE, "superuser", "JMX root", "no authorization");
  }

  @Test
  public void knownLimitationsAreDocumented() throws IOException {
    assertContains(
        PAGE,
        "cassandra -v",
        "Cassandra version:",
        "cqlsh",
        "describecluster",
        "gossipinfo",
        "Apache Cassandra nodetool",
        "ChronitonDB nodetool older than this feature");
  }

  @Test
  public void exactNamesAreDocumented() throws IOException {
    assertContains(
        PAGE,
        "nodetool_release_version_enabled",
        "enablereleaseversion",
        "disablereleaseversion",
        MBEAN,
        "org.chronitondb.metrics:type=ReleaseVersion,name=Reported",
        "Unknown",
        "5.0-chronitondb-SNAPSHOT",
        "the node has no ChronitonDB release version reporter");
  }

  private static void assertLine(String file, String... words) throws IOException {
    for (String line : lines(file)) {
      if (containsAll(line, words)) {
        return;
      }
    }
    throw new AssertionError(file + " has no line that names all of " + String.join(", ", words));
  }

  private static void assertContains(String file, String... texts) throws IOException {
    String content = String.join("\n", lines(file));
    for (String text : texts) {
      assertTrue(file + " does not contain " + text, content.contains(text));
    }
  }

  private static boolean containsAll(String line, String... words) {
    for (String word : words) {
      if (!line.contains(word)) {
        return false;
      }
    }
    return true;
  }

  private static List<String> lines(String file) throws IOException {
    return Files.readAllLines(Path.of(file), StandardCharsets.UTF_8);
  }
}
