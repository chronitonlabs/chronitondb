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

import static org.apache.cassandra.service.StartupChecks.StartupCheckType.check_commitlog_shared_disk;
import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNull;

import org.apache.cassandra.config.DatabaseDescriptor;
import org.junit.Test;

/**
 * The daemon builds the check before its configuration is loaded, so the constructor must read
 * nothing. This class loads no configuration, so it holds this one test only.
 */
public class CommitLogDiskCheckConstructionTest {
  @Test
  public void constructorReadsNoConfig() {
    assertNull("a configuration is loaded before the test", DatabaseDescriptor.getRawConfig());

    CommitLogDiskCheck check = new CommitLogDiskCheck();

    assertEquals(check_commitlog_shared_disk, check.getStartupCheckType());
    assertNull("the constructor loaded a configuration", DatabaseDescriptor.getRawConfig());
  }
}
