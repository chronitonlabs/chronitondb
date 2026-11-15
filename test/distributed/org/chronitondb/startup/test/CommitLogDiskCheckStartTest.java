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

package org.chronitondb.startup.test;

import static org.apache.cassandra.service.StartupChecks.StartupCheckType.check_commitlog_shared_disk;
import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Arrays;
import java.util.EnumMap;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import org.apache.cassandra.config.DatabaseDescriptor;
import org.apache.cassandra.config.StartupChecksOptions;
import org.apache.cassandra.distributed.Cluster;
import org.apache.cassandra.distributed.api.ConsistencyLevel;
import org.apache.cassandra.distributed.api.IInvokableInstance;
import org.apache.cassandra.distributed.test.TestBaseImpl;
import org.apache.cassandra.service.StartupChecks.StartupCheckType;
import org.junit.Test;

/** A node started through the daemon runs the commit log disk check, on and off. */
public class CommitLogDiskCheckStartTest extends TestBaseImpl {
  private static final String NAME = "check_commitlog_shared_disk";

  @Test
  public void enabledNodeWarnsAndStarts() throws IOException {
    try (Cluster cluster =
        Cluster.build(1).withConfig(config -> config.set("startup_checks", switchOn())).start()) {
      IInvokableInstance node = cluster.get(1);
      String commitLog = node.callOnInstance(DatabaseDescriptor::getCommitLogLocation);
      String[] data = node.callOnInstance(DatabaseDescriptor::getAllDataFileLocations);
      Object device = deviceId(commitLog);
      for (String directory : data) {
        assertEquals(
            "the test host put the directories of one instance on more than one file system: "
                + commitLog
                + " and "
                + directory,
            device,
            deviceId(directory));
      }

      cluster.coordinator(1).execute("SELECT * FROM system.local", ConsistencyLevel.ONE);

      List<String> warnings = node.logs().grep("^WARN .*" + NAME).getResult();
      assertEquals("WARN lines naming " + NAME + ": " + warnings, 1, warnings.size());
      String expected =
          "The commit log directory "
              + commitLog
              + " is on the same file system as the data directories "
              + Arrays.asList(data)
              + ". One failure of that file system loses the commit log and the data together,"
              + " and on spinning disks commit log writes compete with reads, flushes and"
              + " compaction. Put commitlog_directory on a file system of its own. This warning"
              + " comes from the startup check check_commitlog_shared_disk.";
      assertTrue(
          warnings.get(0) + " is not the shared warning", warnings.get(0).endsWith(expected));
    }
  }

  @Test
  public void defaultNodeLogsNothingNew() throws IOException {
    try (Cluster cluster = Cluster.build(1).start()) {
      IInvokableInstance node = cluster.get(1);

      cluster.coordinator(1).execute("SELECT * FROM system.local", ConsistencyLevel.ONE);

      List<String> lines = node.logs().grep(NAME).getResult();
      assertEquals("log lines naming " + NAME + ": " + lines, List.of(), lines);
    }
  }

  private static Object deviceId(String directory) throws IOException {
    return Files.getAttribute(Path.of(directory), "unix:dev");
  }

  private static Map<StartupCheckType, Map<String, Object>> switchOn() {
    Map<String, Object> entry = new HashMap<>();
    entry.put(StartupChecksOptions.ENABLED_PROPERTY, "true");
    Map<StartupCheckType, Map<String, Object>> checks = new EnumMap<>(StartupCheckType.class);
    checks.put(check_commitlog_shared_disk, entry);
    return checks;
  }
}
