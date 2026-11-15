<!--
Copyright 2026 AxonOps Limited
SPDX-License-Identifier: Apache-2.0

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
-->

# Acceptance coverage for #112

Location: next to its design record, in `docs/design/CLD-commitlog-disk-check/`, the directory of the fork feature with the key `CLD`. Process: [testing.md](../../process/testing.md).

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in BCP 14 (RFC 2119, RFC 8174) when, and only when, they appear in all capitals, as shown here.

## Contents

- [Coverage](#coverage)

## Coverage

This item is a fork feature that fits one item, with the key `CLD`. It adds no scenario, under waiver 2 of the design record's Waivers, so every requirement has one row naming its JUnit test. "Problem n" is item n of the record's Where problems could occur. REQ-CLD-012 names a stock test that runs unchanged, with the gate's check that no pre-existing test changed as the other half of its proof. REQ-CLD-013 to REQ-CLD-015 name a documentation test that reads the two files. The acceptance criteria of the issue are covered end to end by `org.chronitondb.startup.CommitLogDiskCheckStartTest.enabledNodeWarnsAndStarts`, the row of REQ-CLD-011: a node with the check on logs the warning and starts.

| Id | Source | Requirement | Covering scenario | Test | Status |
|---|---|---|---|---|---|
| REQ-CLD-001 | acceptance criterion 1 | When the startup checks run with the switch on and the commit log directory shares a file system with one or more data directories, the check MUST log exactly one line at WARN with the text of the shared warning. | none | `org.chronitondb.startup.CommitLogDiskCheckTest.sharedFileSystemWarnsOnce` | Covered |
| REQ-CLD-002 | acceptance criterion 1 and decision record 0006 | The shared warning MUST list every data directory that shares a file system with the commit log directory and no other directory. | none | `org.chronitondb.startup.CommitLogDiskCheckTest.sharedFileSystemWarnsOnce` | Covered |
| REQ-CLD-003 | acceptance criterion 1 and decision record 0006 | When the startup checks run with the switch on and no data directory shares a file system with the commit log directory, the check MUST NOT log the shared warning. | none | `org.chronitondb.startup.CommitLogDiskCheckTest.separateFileSystemsLogNothing` | Covered |
| REQ-CLD-004 | decision record 0004 and branching-and-review.md item 7 | While the switch is off, the check MUST return without a file store lookup, a log line or a metric. | none | `org.chronitondb.startup.CommitLogDiskCheckTest.offDoesNothing` | Covered |
| REQ-CLD-005 | decision records 0004 and 0005 | The switch MUST be off on a node whose `cassandra.yaml` does not set `enabled` to `true` in the entry `check_commitlog_shared_disk` under `startup_checks`. | none | `org.chronitondb.startup.CommitLogDiskCheckTest.switchIsOffByDefault` | Covered |
| REQ-CLD-006 | acceptance criterion 2 and problem 1 | The check MUST return normally from every run, whatever a file store lookup returns or throws. | none | `org.chronitondb.startup.CommitLogDiskCheckTest.neverThrows` | Covered |
| REQ-CLD-007 | problem 6 | If the file store lookup of the commit log directory or of a data directory throws, then the check MUST log one line at WARN with the text of the unreadable warning for that directory. | none | `org.chronitondb.startup.CommitLogDiskCheckTest.unreadableDirectoryWarns` | Covered |
| REQ-CLD-008 | problem 6 | If the file store lookup of a data directory throws, then the check MUST still compare every other data directory with the commit log directory. | none | `org.chronitondb.startup.CommitLogDiskCheckTest.unreadableDirectoryDoesNotHideOthers` | Covered |
| REQ-CLD-009 | problem 7 and quality-requirements.md | When the startup checks run with the switch on, the check MUST raise the counter `org.chronitondb.metrics:type=CommitLogDiskCheck,name=SharedDataDirectories` by the number of data directories that share a file system with the commit log directory. | none | `org.chronitondb.startup.CommitLogDiskCheckTest.countsSharedDirectories` | Covered |
| REQ-CLD-010 | problem 6 and quality-requirements.md | When the startup checks run with the switch on, the check MUST raise the counter `org.chronitondb.metrics:type=CommitLogDiskCheck,name=UnreadableDirectories` by the number of directories whose file store lookup threw. | none | `org.chronitondb.startup.CommitLogDiskCheckTest.countsUnreadableDirectories` | Covered |
| REQ-CLD-011 | acceptance criterion 1 and problem 5 | A node that starts through `CassandraDaemon` MUST run the check as one of its startup checks. | none | `org.chronitondb.startup.CommitLogDiskCheckStartTest.enabledNodeWarnsAndStarts` | Covered |
| REQ-CLD-012 | problem 3 and conventions.md, Code layout item 5 | The change MUST NOT modify a test that exists on the line. | none | `org.apache.cassandra.config.StartupCheckOptionsTest.testStartupOptionsConfigApplication` | Covered |
| REQ-CLD-013 | problem 2 | The reference page `docs/reference/commitlog-disk-check.md` MUST hold one line that names `check_commitlog_shared_disk`, `cassandra.yaml`, `Apache Cassandra` and `older`, the rollback line. | none | `org.chronitondb.startup.CommitLogDiskCheckDocsTest.rollbackLineOnReferencePage` | Covered |
| REQ-CLD-014 | problem 2 | `NEWS-chronitondb.txt` MUST hold one line that names `check_commitlog_shared_disk`, `cassandra.yaml`, `Apache Cassandra` and `older`, the rollback line. | none | `org.chronitondb.startup.CommitLogDiskCheckDocsTest.rollbackLineInNews` | Covered |
| REQ-CLD-015 | problem 7 | The reference page MUST contain each of these exact texts: `check_commitlog_shared_disk`, `org.chronitondb.metrics:type=CommitLogDiskCheck,name=SharedDataDirectories`, `org.chronitondb.metrics:type=CommitLogDiskCheck,name=UnreadableDirectories`, the fixed text of the shared warning and the fixed text of the unreadable warning. | none | `org.chronitondb.startup.CommitLogDiskCheckDocsTest.exactNamesAreDocumented` | Covered |
