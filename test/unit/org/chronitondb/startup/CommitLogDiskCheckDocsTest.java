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

package org.chronitondb.startup;

import static org.junit.Assert.assertTrue;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import org.junit.Test;

/** The reference page and the news file carry the names and the lines operators rely on. */
public class CommitLogDiskCheckDocsTest {
  private static final String PAGE = "docs/reference/commitlog-disk-check.md";
  private static final String NEWS = "NEWS-chronitondb.txt";
  private static final String ROLLBACK =
      "Before a node runs an Apache Cassandra binary, or a ChronitonDB build older than this"
          + " feature, remove check_commitlog_shared_disk from its cassandra.yaml, and remove"
          + " startup_checks as well when it then holds no other entry.";

  @Test
  public void rollbackLineOnReferencePage() throws IOException {
    assertLine(PAGE, ROLLBACK);
  }

  @Test
  public void rollbackLineInNews() throws IOException {
    assertLine(NEWS, ROLLBACK);
  }

  @Test
  public void exactNamesAreDocumented() throws IOException {
    String content = String.join("\n", lines(PAGE));
    List<String> texts = new ArrayList<>();
    texts.add("check_commitlog_shared_disk");
    texts.add("org.chronitondb.metrics:type=CommitLogDiskCheck,name=SharedDataDirectories");
    texts.add("org.chronitondb.metrics:type=CommitLogDiskCheck,name=UnreadableDirectories");
    texts.add("org.chronitondb.metrics:type=CommitLogDiskCheck,name=FailedRuns");
    texts.addAll(fixedParts(CommitLogDiskCheck.SHARED_WARNING));
    texts.addAll(fixedParts(CommitLogDiskCheck.UNREADABLE_WARNING));
    texts.addAll(fixedParts(CommitLogDiskCheck.FAILED_WARNING));
    for (String text : texts) {
      assertTrue(PAGE + " does not contain: " + text, content.contains(text));
    }
  }

  private static List<String> fixedParts(String warning) {
    List<String> parts = new ArrayList<>();
    for (String part : warning.split("\\{\\}", -1)) {
      if (!part.isEmpty()) {
        parts.add(part);
      }
    }
    return parts;
  }

  private static void assertLine(String file, String text) throws IOException {
    for (String line : lines(file)) {
      if (line.contains(text)) {
        return;
      }
    }
    throw new AssertionError(file + " has no line that holds the rollback sentence: " + text);
  }

  private static List<String> lines(String file) throws IOException {
    return Files.readAllLines(Path.of(file), StandardCharsets.UTF_8);
  }
}
