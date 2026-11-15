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

This item is a fork feature that fits one item, with the key `CLD`. It adds no scenario, under waiver 2 of the design record's Waivers, so every requirement has one row naming its JUnit test. "Problem n" is item n of the record's Where problems could occur. REQ-CLD-014 to REQ-CLD-016 name a documentation test that reads the two files.

The acceptance criteria of the issue. Criterion 1, the warning, is covered on a node whose operator switched the check on, by REQ-CLD-001 to REQ-CLD-003 and REQ-CLD-012. On a node with the check off, the default, criterion 1 is excluded by decision record 0004, the maintainers' decision of 2026-11-15 that the check is off by default (`docs/decisions/0004-commit-log-disk-check-off-by-default.md`). Criterion 2, the node still starts, is covered by REQ-CLD-006, REQ-CLD-012 and REQ-CLD-013. Both are proven end to end by `org.chronitondb.startup.test.CommitLogDiskCheckStartTest.enabledNodeWarnsAndStarts`, the row of REQ-CLD-012: a node with the check on logs the warning and starts.

| Id | Source | Requirement | Covering scenario | Test | Status |
|---|---|---|---|---|---|
| REQ-CLD-001 | acceptance criterion 1 | When the startup checks run with the switch on and the commit log directory shares a file system with one or more data directories, the check MUST log the shared warning exactly once. | none | `org.chronitondb.startup.CommitLogDiskCheckTest.sharedFileSystemWarnsOnce` | Covered |
| REQ-CLD-002 | acceptance criterion 1 and decision record 0006 | The shared warning MUST list every data directory that shares a file system with the commit log directory and no other data directory. | none | `org.chronitondb.startup.CommitLogDiskCheckTest.sharedFileSystemWarnsOnce` | Covered |
| REQ-CLD-003 | acceptance criterion 1 and decision record 0006 | When the startup checks run with the switch on and no data directory shares a file system with the commit log directory, the check MUST NOT log the shared warning. | none | `org.chronitondb.startup.CommitLogDiskCheckTest.separateFileSystemsLogNothing` | Covered |
| REQ-CLD-004 | decision record 0004 and branching-and-review.md item 7 | While the switch is off, the check MUST return without reading the directories, without a file system lookup, without a log line and without a metric. | none | `org.chronitondb.startup.CommitLogDiskCheckTest.offDoesNothing` | Covered |
| REQ-CLD-005 | decision records 0004 and 0005 | The switch MUST be off on a node whose `cassandra.yaml` holds no key `enabled` in an entry `check_commitlog_shared_disk` under `startup_checks`. | none | `org.chronitondb.startup.CommitLogDiskCheckTest.switchIsOffByDefault` | Covered |
| REQ-CLD-006 | acceptance criterion 2 and problem 1 | If an `Exception` is thrown anywhere in a run of the check with the switch on, in the read of the directories, in a file system lookup, in a counter or in a log call, then the check MUST still return normally. | none | `org.chronitondb.startup.CommitLogDiskCheckTest.neverThrows` | Covered |
| REQ-CLD-007 | problem 6 | If the file system lookup of the commit log directory or of a data directory throws an `Exception`, then the check MUST log the unreadable warning for that directory exactly once. | none | `org.chronitondb.startup.CommitLogDiskCheckTest.unreadableDirectoryWarns` | Covered |
| REQ-CLD-008 | problem 6 | If the file system lookup of a data directory throws an `Exception`, then the check MUST still compare every other data directory with the commit log directory. | none | `org.chronitondb.startup.CommitLogDiskCheckTest.unreadableDirectoryDoesNotHideOthers` | Covered |
| REQ-CLD-009 | problem 6 | If the file system lookup of the commit log directory throws an `Exception`, then the check MUST NOT look up the file system of any data directory. | none | `org.chronitondb.startup.CommitLogDiskCheckTest.unreadableCommitLogEndsTheComparison` | Covered |
| REQ-CLD-010 | problem 7 and quality-requirements.md | When the startup checks run with the switch on, the check MUST raise the counter `org.chronitondb.metrics:type=CommitLogDiskCheck,name=SharedDataDirectories` by the number of data directories it found sharing a file system with the commit log directory. | none | `org.chronitondb.startup.CommitLogDiskCheckTest.countsSharedDirectories` | Covered |
| REQ-CLD-011 | problem 6 and quality-requirements.md | When the startup checks run with the switch on, the check MUST raise the counter `org.chronitondb.metrics:type=CommitLogDiskCheck,name=UnreadableDirectories` by the number of directories whose file system lookup threw an `Exception`. | none | `org.chronitondb.startup.CommitLogDiskCheckTest.countsUnreadableDirectories` | Covered |
| REQ-CLD-012 | acceptance criterion 1 and problem 5 | A node that starts through `CassandraDaemon` MUST run the check as one of its startup checks. | none | `org.chronitondb.startup.test.CommitLogDiskCheckStartTest.enabledNodeWarnsAndStarts` | Covered |
| REQ-CLD-013 | problem 1 | The constructor of `CommitLogDiskCheck` that the daemon calls MUST NOT call a method of `DatabaseDescriptor`. | none | `org.chronitondb.startup.CommitLogDiskCheckConstructionTest.constructorReadsNoConfig` | Covered |
| REQ-CLD-014 | problem 2 | The reference page `docs/reference/commitlog-disk-check.md` MUST contain the rollback sentence. | none | `org.chronitondb.startup.CommitLogDiskCheckDocsTest.rollbackLineOnReferencePage` | Covered |
| REQ-CLD-015 | problem 2 | `NEWS-chronitondb.txt` MUST contain the rollback sentence. | none | `org.chronitondb.startup.CommitLogDiskCheckDocsTest.rollbackLineInNews` | Covered |
| REQ-CLD-016 | problem 7 | The reference page MUST contain each of these exact texts: `check_commitlog_shared_disk`, `org.chronitondb.metrics:type=CommitLogDiskCheck,name=SharedDataDirectories`, `org.chronitondb.metrics:type=CommitLogDiskCheck,name=UnreadableDirectories`, the fixed text of the shared warning and the fixed text of the unreadable warning. | none | `org.chronitondb.startup.CommitLogDiskCheckDocsTest.exactNamesAreDocumented` | Covered |
| REQ-CLD-017 | problem 1 | If an `Exception` is thrown in a run of the check with the switch on, outside a file system lookup, then the check MUST log the failed warning exactly once. | none | `org.chronitondb.startup.CommitLogDiskCheckTest.failureOutsideALookupWarns` | Covered |
| REQ-CLD-018 | problem 7 | When the startup checks run with the switch on, the check MUST register both counters before it reads the directories. | none | `org.chronitondb.startup.CommitLogDiskCheckTest.registersBothCounters` | Covered |
