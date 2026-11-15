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

# Design: #112 Warn at startup when the commit log shares a disk with the data directories

| Field | Value |
|---|---|
| Title | Warn at startup when the commit log shares a disk with the data directories |
| Document type | Specification and description at item level (ISO/IEC/IEEE 15289) |
| Status | Draft |
| Version | 1 |
| Author | Designer: chronitondb-agent |
| Approver | The maintainer who merges the pull request |
| References | Issue #112. Line `chronitondb-sandbox`, read at commit `8d744bb0ac`. Apache base commit `76550e931481e965ae3283d8cf4a59c320d74c55` (Apache `cassandra-5.0`). No feature spec and no plan: the one-item path. Process pages [branching-and-review.md](../../process/branching-and-review.md#feature-switches-and-defaults) and [quality-requirements.md](../../process/quality-requirements.md). Decision records 0001, 0004, 0005 and 0006. |
| Risk | Normal: the issue's label `risk:normal`, which this record and the work on it follow. The label meets the floor, which applies because the change touches configuration and stock behaviour. For the maintainers, who confirm the class when they merge this record: if the check or its hook threw at startup the node would not start, an Availability fault that [classification.md](../../process/classification.md#risk) rates Critical. REQ-CLD-006 and REQ-CLD-013 are written to exclude it. Only a maintainer changes the label. |
| Size | Low Hanging Fruit: one fork class for the check, two small edits to stock files, no dependency on other work. |
| Reach | One area: the startup checks of one node, in `org.apache.cassandra.service` and the new package `org.chronitondb.startup`. |
| Touches | public interface (configuration), public interface (jmx mbeans, including metrics), stock behaviour (the start log of a node whose operator switched the check on), new feature or switch |

Change history: the git history of this file.

Location: `docs/design/CLD-commitlog-disk-check/`, the directory of the fork feature with the key `CLD`, which this record proposes and the merge of its pull request reserves ([additive.md, Feature keys and requirement ids](../../process/additive.md#feature-keys-and-requirement-ids), item 2), with the coverage file `ac-coverage.md` next to it. Every section is filled, or carries a waiver with its reason.

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in BCP 14 (RFC 2119, RFC 8174) when, and only when, they appear in all capitals, as shown here.

The Risk, Size and Reach rows are the item's class, as [classification.md](../../process/classification.md) defines it, and match the issue's `risk:normal`, `size:low-hanging-fruit` and `reach:one-area` labels. The issue also carries `kind:additive`, so the item is a fork feature small enough for one item and takes the one-item path of [maintenance.md](../../process/maintenance.md#the-one-item-path) with a feature key: this directory, the ids `REQ-CLD-nnn`, and the feature class stated in [section 3](#3-stock-behaviour-preservation).

## Contents

- [1. Problem, acceptance criteria and requirements](#1-problem-acceptance-criteria-and-requirements)
  - [Requirements](#requirements)
- [2. Decisions implemented](#2-decisions-implemented)
- [3. Stock behaviour preservation](#3-stock-behaviour-preservation)
  - [Stock hook points](#stock-hook-points)
- [4. Prior art reviewed](#4-prior-art-reviewed)
- [5. Idiom and consistency](#5-idiom-and-consistency)
- [6. Quality requirements](#6-quality-requirements)
- [7. Performance](#7-performance)
  - [Hot path statement](#hot-path-statement)
  - [Expected cost](#expected-cost)
  - [Isolation levers](#isolation-levers)
  - [Benchmarks that prove it](#benchmarks-that-prove-it)
  - [Regression threshold and gate](#regression-threshold-and-gate)
  - [Stock guard](#stock-guard)
  - [What was not measured](#what-was-not-measured)
- [8. Observability](#8-observability)
- [9. Compatibility](#9-compatibility)
- [10. Threat model and security](#10-threat-model-and-security)
- [11. Dependencies](#11-dependencies)
- [12. Compliance impact](#12-compliance-impact)
- [13. Documentation](#13-documentation)
- [14. Testing](#14-testing)
  - [Tests for this change](#tests-for-this-change)
  - [Existing suites at risk](#existing-suites-at-risk)
  - [Stock suites run unchanged](#stock-suites-run-unchanged)
  - [Tracing test](#tracing-test)
  - [Formats and configurations](#formats-and-configurations)
- [15. Not covered and follow-ups](#15-not-covered-and-follow-ups)
- [New terms](#new-terms)
- [Where problems could occur](#where-problems-could-occur)
  - [Test plan](#test-plan)
- [Planned file list](#planned-file-list)
  - [Shared with open items](#shared-with-open-items)
  - [Waivers](#waivers)
- [Requirement quality checklist (ISO/IEC/IEEE 29148)](#requirement-quality-checklist-isoiecieee-29148)

## 1. Problem, acceptance criteria and requirements

An operator can put the commit log on the same disk as the data files by mistake, and nothing tells them. On spinning disks the commit log's sequential writes then compete with reads, flushes and compaction, and write latency suffers. On any disk, one failure takes out the commit log and the data together.

Stock Apache Cassandra advises against it only in the comment above the key `commitlog_directory` in `conf/cassandra.yaml`: "when running on magnetic HDD, this should be a separate spindle than the data directories" (`conf/cassandra.yaml:405` to `406` at `8d744bb0ac`). The node itself checks one thing: `DatabaseDescriptor.applySimpleConfig` refuses to start when `commitlog_directory` is the same path as a data directory, with `commitlog_directory must not be the same as any data_file_directories` (`DatabaseDescriptor.java:706` to `707` at `8d744bb0ac`). Two different paths on one file system pass without a word.

That is also the layout of every node that sets neither directory. `DatabaseDescriptor.applySimpleConfig` puts the commit log in `<storagedir>/commitlog` (`DatabaseDescriptor.java:624` to `627` at `8d744bb0ac`) and the data in `<storagedir>/data` (`DatabaseDescriptor.java:693` to `696` at `8d744bb0ac`), and the variable `cassandra_storagedir` of `bin/cassandra.in.sh` sets the storage directory to `$CASSANDRA_HOME/data` (`bin/cassandra.in.sh:48` at `8d744bb0ac`). So a check that is on by default would warn on every node that runs the default layout, which includes every development install and every test node. Decision record 0004 keeps the check off by default for that reason.

Acceptance criteria, from the issue:

1. The node logs a clear warning at startup when the commit log directory is on the same file system as any data directory.
2. The node still starts as it does today.

Decision record 0004 limits criterion 1 to a node whose operator switched the check on: the maintainers decided that the check is off by default. So this record covers criterion 1 with the switch on. With the switch off the node logs no warning, by that decision.

What this record builds, in short. One new startup check, `org.chronitondb.startup.CommitLogDiskCheck`, which an operator switches on in `cassandra.yaml`:

```
startup_checks:
  check_commitlog_shared_disk:
    enabled: true
```

With the switch on, the check runs once at each start, after the stock checks. It compares the file system of the commit log directory with the file system of each data directory, by the device id the operating system reports for each. When one or more data directories are on the commit log's file system it logs one WARN line that names them. It never stops the node. With the switch off, which is the default, the check returns at once and the node logs and holds what a stock node does, except for one enum constant, one options map and one registered check, which row 3 of the departures table in section 3 lists.

A run of the check, step by step. Every section and every requirement below means this order.

1. The check reads the switch with `StartupChecksOptions.isDisabled`. Off: it returns. This call is outside the guard of step 2, as it is in every stock check.
2. Everything from here on runs inside one guard. An `Exception` that leaves a later step, other than a lookup failure that steps 5 and 6 handle themselves, ends the run: the check does no further step, logs the failed warning once, raises the counter `FailedRuns` by one if step 3 registered it, and returns. Counts made before that stay. If that last raise throws too, the check catches it and returns.
3. The check registers the three counters.
4. It reads the commit log directory and the data directories, and drops a data directory it has already seen.
5. It looks up the file system of the commit log directory. If that lookup throws an `Exception`, it logs the unreadable warning for the directory, raises `UnreadableDirectories` by one and returns.
6. For each data directory, in order, it looks up the file system. If that lookup throws an `Exception`, it logs the unreadable warning for the directory, raises `UnreadableDirectories` by one and goes on to the next directory. Otherwise it notes the directory when its device id equals the commit log directory's.
7. If it noted one or more directories, it raises `SharedDataDirectories` by their number and then logs the shared warning.

The words this record uses with one fixed meaning are in [New terms](#new-terms): the switch, the data directories, the file system lookup, shares a file system, the shared warning, the unreadable warning, the failed warning and the rollback sentence.

### Requirements

In the sources below, "problem n" is item n of [Where problems could occur](#where-problems-could-occur).

REQ-CLD-001 (event driven): When the startup checks run with the switch on and the commit log directory shares a file system with one or more data directories, the check MUST log the shared warning exactly once. Source: acceptance criterion 1.

REQ-CLD-002 (ubiquitous): The shared warning MUST list every data directory that shares a file system with the commit log directory and no other data directory. Source: acceptance criterion 1 and decision record 0006.

REQ-CLD-003 (event driven): When the startup checks run with the switch on and no data directory shares a file system with the commit log directory, the check MUST NOT log the shared warning. Source: acceptance criterion 1 and decision record 0006.

REQ-CLD-004 (state driven): While the switch is off, the check MUST return without reading the directories, without a file system lookup, without a log line and without a metric. Source: decision record 0004 and [branching-and-review.md](../../process/branching-and-review.md#feature-switches-and-defaults) item 7.

REQ-CLD-005 (ubiquitous): The switch MUST be off on a node whose `cassandra.yaml` has no entry `check_commitlog_shared_disk` under `startup_checks`. Source: decision records 0004 and 0005.

REQ-CLD-006 (unwanted behaviour): If the registration of a counter, the read of the directories or a file system lookup throws an `Exception` in a run of the check with the switch on, then the check MUST still return normally. Source: acceptance criterion 2 and problem 1.

REQ-CLD-007 (unwanted behaviour): If the file system lookup of the commit log directory or of a data directory throws an `Exception`, then the check MUST log the unreadable warning for that directory exactly once. Source: problem 6.

REQ-CLD-008 (unwanted behaviour): If the file system lookup of a data directory throws an `Exception`, then the check MUST still compare every other data directory with the commit log directory. Source: problem 6.

REQ-CLD-009 (unwanted behaviour): If the file system lookup of the commit log directory throws an `Exception`, then the check MUST NOT look up the file system of any data directory. Source: problem 6.

REQ-CLD-010 (event driven): When the startup checks run with the switch on, the check MUST raise the counter `org.chronitondb.metrics:type=CommitLogDiskCheck,name=SharedDataDirectories` by the number of data directories it found sharing a file system with the commit log directory. Source: problem 7 and [quality-requirements.md](../../process/quality-requirements.md#observability).

REQ-CLD-011 (event driven): When the startup checks run with the switch on, the check MUST raise the counter `org.chronitondb.metrics:type=CommitLogDiskCheck,name=UnreadableDirectories` by the number of directories whose file system lookup threw an `Exception`. Source: problem 6 and [quality-requirements.md](../../process/quality-requirements.md#observability).

REQ-CLD-012 (ubiquitous): A node that starts through `CassandraDaemon` MUST run the check as one of its startup checks. Source: acceptance criterion 1 and problem 5.

REQ-CLD-013 (state driven): While no configuration is loaded, the constructor of `CommitLogDiskCheck` that the daemon calls MUST return normally without loading one. Source: problem 1.

REQ-CLD-014 (ubiquitous): The reference page `docs/reference/commitlog-disk-check.md` MUST contain the rollback sentence. Source: problem 2.

REQ-CLD-015 (ubiquitous): `NEWS-chronitondb.txt` MUST contain the rollback sentence. Source: problem 2.

REQ-CLD-016 (ubiquitous): The reference page MUST contain each of these exact texts: `check_commitlog_shared_disk`, `org.chronitondb.metrics:type=CommitLogDiskCheck,name=SharedDataDirectories`, `org.chronitondb.metrics:type=CommitLogDiskCheck,name=UnreadableDirectories`, `org.chronitondb.metrics:type=CommitLogDiskCheck,name=FailedRuns`, the fixed text of the shared warning, the fixed text of the unreadable warning and the text of the failed warning. Source: problem 7.

REQ-CLD-017 (unwanted behaviour): If an `Exception` leaves a step of a run of the check with the switch on, other than a lookup failure that steps 5 and 6 of the run handle, then the check MUST log the failed warning exactly once. Source: problem 1.

REQ-CLD-018 (event driven): When a run of the check with the switch on ends, the three counters MUST be registered, unless their registration threw an `Exception`. Source: problem 7.

REQ-CLD-019 (unwanted behaviour): If an `Exception` leaves a step of a run of the check with the switch on, other than a lookup failure that steps 5 and 6 of the run handle, then the check MUST do no further file system lookup in that run. Source: problem 1.

REQ-CLD-020 (unwanted behaviour): If a run of the check ends with the failed warning after the counters were registered, then the check MUST raise the counter `org.chronitondb.metrics:type=CommitLogDiskCheck,name=FailedRuns` by one. Source: problem 7 and [quality-requirements.md](../../process/quality-requirements.md#observability).

## 2. Decisions implemented

1. Decision record 0001, The first maintainers, 2026-11-01: the maintainers who approve this record. Nothing in it binds the design.
2. Decision record 0004, The commit log disk check is off by default, 2026-11-15, added in this pull request with the status Accepted, which the maintainer's merge of this pull request makes true. The check runs only on a node whose operator switched it on. REQ-CLD-004 and REQ-CLD-005 implement it.
3. Decision record 0005, The commit log disk check is switched under `startup_checks`, 2026-11-15, added in this pull request the same way. The switch is the entry `check_commitlog_shared_disk` with the key `enabled` under the stock `startup_checks` block. The feature has no top level yaml key and no nodetool command. REQ-CLD-005, section 3 and waiver 3 implement it.
4. Decision record 0006, The commit log disk check compares file systems, 2026-11-15, added in this pull request the same way. Two directories share a disk, for this check, when they are on the same file system, as the operating system reports it. Two file systems on one physical device get no warning. REQ-CLD-001 to REQ-CLD-003, the term shares a file system in New terms and the known limitation in section 13 implement it.
5. The process pages, read on the line at commit `8d744bb0ac`: [branching-and-review.md, Feature switches and defaults](../../process/branching-and-review.md#feature-switches-and-defaults) item 4 (a behaviour-changing feature is off by default) and item 7 (stock behaviour with the feature off), [quality-requirements.md](../../process/quality-requirements.md) (the checklist in section 6), [maintenance.md, The one-item path](../../process/maintenance.md#the-one-item-path), [conventions.md, Names](../../process/conventions.md#names) (no `cassandra` or `axon` in a new name, fork metrics under their own types), [conventions.md, Code layout](../../process/conventions.md#code-layout) (fork code under `org.chronitondb`, a stock edit is the hook only) and [conventions.md, Change logs and release notes](../../process/conventions.md#change-logs-and-release-notes) item 2 (`NEWS-chronitondb.txt` is written in the pull request that makes the change).

As of 2026-11-15 the register on the line holds records 0001 to 0003. Records 0002 and 0003 are about `nodetool version` and its tests. Records 0004 to 0006 are added by this pull request. No newer record exists on startup checks, configuration or the commit log.

## 3. Stock behaviour preservation

This statement and the switch table below it follow the form of [section 2.8 of the feature spec template](../../process/templates/feature-spec.md#28-feature-class-and-switches), because a fork feature that fits one item has no feature spec.

Feature class: behaviour-changing, because with its switch on it adds a WARN line to the start log of a node, and a warning is something stock Apache Cassandra already does (branching-and-review.md, Feature switches and defaults, item 4).

| Switch | Class | Reason | Default per line | Stock operations it changes |
|---|---|---|---|---|
| `enabled` in the entry `check_commitlog_shared_disk` under `startup_checks` in `cassandra.yaml`, read at start only, with no nodetool toggle (decision record 0005) | behaviour-changing | with the switch on, a node may log one or more WARN lines at start that a stock node does not log, and holds three more counters | `chronitondb-sandbox`: off (decision record 0004) | node start: the start log and the list of metrics |

Rows 1 and 2 of the table below apply only with the switch on. Row 3 is a presence on every node, switch on or off: a departure from [branching-and-review.md](../../process/branching-and-review.md#feature-switches-and-defaults) item 7, which says that with a feature off no new memory is used. The maintainers approve it by merging this record.

| Stock behaviour today (file and line) | This change | Switch that controls it | Error text naming the switch |
|---|---|---|---|
| The startup checks say nothing about where the commit log is. `StartupChecks.checkDataDirs` checks that each directory exists and is writable and does not compare them (`src/java/org/apache/cassandra/service/StartupChecks.java:561` to `594` at `8d744bb0ac`) | with the switch on, the start log holds the shared warning when a data directory shares a file system with the commit log directory, and one unreadable warning for each directory whose file system lookup threw, and the failed warning when a run fails | `check_commitlog_shared_disk`, key `enabled` | none: the switch refuses nothing. The shared warning, the unreadable warning and the failed warning all name `check_commitlog_shared_disk` |
| The metrics registry holds Apache's metrics only. `CassandraMetricsRegistry.counter` registers a counter and its MBean (`src/java/org/apache/cassandra/metrics/CassandraMetricsRegistry.java:55` to `61` at `8d744bb0ac`) | with the switch on, the registry holds three more counters, `SharedDataDirectories`, `UnreadableDirectories` and `FailedRuns`, of the fork's own type `CommitLogDiskCheck` in the group `org.chronitondb.metrics`, from the first run of the check. No stock metric changes | `check_commitlog_shared_disk`, key `enabled` | none |
| `StartupChecks.StartupCheckType` has five constants (`StartupChecks.java:106` to `125` at `8d744bb0ac`), `StartupChecksOptions.apply` keeps one options map for each constant (`src/java/org/apache/cassandra/config/StartupChecksOptions.java:81` to `96` at `8d744bb0ac`), and the `CassandraDaemon` constructor registers the default checks and `FileSystemOwnershipCheck` (`src/java/org/apache/cassandra/service/CassandraDaemon.java:220` at `8d744bb0ac`) | one more constant, `check_commitlog_shared_disk`, declared disabled by default, so one more options map that holds `enabled` as `false`, and one more registered check, whose `execute` returns at its first statement while the switch is off. Together a few hundred bytes, allocated once at start. No log line, no file, no thread and no metric | none: the name must be a constant of the enum for a `cassandra.yaml` that names it to load, and the check must be registered to read the switch | none |

Everything else stays stock. No existing constant of `StartupChecks.StartupCheckType` changes its name, its place or its default: the new constant is the last one. No stock check changes what it does or when it runs: the new check is added after `FileSystemOwnershipCheck`, the last one the daemon registers today. No code default in a stock class changes. `Config.startup_checks` keeps its type and its default, an empty map (`Config.startup_checks`, `src/java/org/apache/cassandra/config/Config.java:960` at `8d744bb0ac`), so the row `startup_checks` of `system_views.settings` and the start log line `Node configuration:` show what they show today on a node that does not name the entry. No stock file under `conf/` changes. No test that exists on the line changes: the Planned file list names no existing test, and the commit checks refuse a modified pre-existing test ([conventions.md, Code layout](../../process/conventions.md#code-layout) item 5).

While the switch is off the check logs nothing. This differs on purpose from the stock `FileSystemOwnershipCheck`, which logs `Filesystem ownership check is not enabled.` at INFO when it is off (`FileSystemOwnershipCheck.execute`, `src/java/org/apache/cassandra/service/FileSystemOwnershipCheck.java:125` at `8d744bb0ac`): a line of that kind would change the start log of every node.

### Stock hook points

There is no feature spec for a one-item change, so the hook points are listed here with their delta entry, `docs/delta/commit-log-disk-check.md`. The entry records the two stock edits of this list and the stock behaviour changes of the departures table above.

1. `src/java/org/apache/cassandra/service/StartupChecks.java`: one constant in the enum `StartupChecks.StartupCheckType`, `check_commitlog_shared_disk(true)`, after `check_data_resurrection(true)` at line 113. It is a constant, not a hook that imports fork code, but it is a stock edit and so it is listed.
2. `src/java/org/apache/cassandra/service/CassandraDaemon.java`: one import and one call on line 220 in the constructor `CassandraDaemon(boolean)`, `.withTest(new CommitLogDiskCheck())` after `.withTest(new FileSystemOwnershipCheck())`. The constructor it calls takes no argument and reads nothing (REQ-CLD-013). `CassandraDaemon.instance` is built in a static initialiser (`CassandraDaemon.java:203` at `8d744bb0ac`), before the configuration is loaded, and `CassandraDaemon.activate` carries the comment that no reference to `DatabaseDescriptor` may come before the configuration is applied (`CassandraDaemon.java:720` at `8d744bb0ac`). The check reads the directories in `execute`, after the switch test, through suppliers, as `FileSystemOwnershipCheck` does (`FileSystemOwnershipCheck.FileSystemOwnershipCheck`, `FileSystemOwnershipCheck.java:100` to `112` at `8d744bb0ac`).

The new package `org.chronitondb.startup` imports from `org.apache.cassandra.config`, `org.apache.cassandra.service`, `org.apache.cassandra.io.util`, `org.apache.cassandra.metrics` and `org.apache.cassandra.exceptions`, all through public members. It needs no package private access to a stock package.

## 4. Prior art reviewed

Stock Apache Cassandra, read on this line at commit `8d744bb0ac`:

1. `StartupChecks.verify` runs every registered `StartupCheck` once, before the node changes any local state (`StartupChecks.java:176` to `192` at `8d744bb0ac`). `CassandraDaemon.setup` calls it through `CassandraDaemon.runStartupChecks` (`CassandraDaemon.java:258` and `457` to `466` at `8d744bb0ac`). `runStartupChecks` catches `StartupException` only, so a check that throws that exception stops the node with its message, any other exception leaves `setup` as it is thrown, and a check that only logs lets the node start.
2. Stock checks that only warn exist already. `StartupChecks.checkReadAheadKbSetting` finds the file store of each data directory with `Files.getFileStore`, logs a WARN and goes on when that lookup throws `IOException`, and logs a WARN when the device's read ahead is high (`StartupChecks.java:433` to `511` at `8d744bb0ac`). `StartupChecks.checkMaxMapCount` logs a WARN for a low `vm.max_map_count` (`StartupChecks.java:513` to `559` at `8d744bb0ac`). Neither stops the node. The new check has the same shape.
3. `StartupChecks.checkDataDirs` reads the data directories from `DatabaseDescriptor.getAllDataFileLocations`, the commit log directory, the saved caches directory and the hints directory, creates each one that is missing, and stops the node when one cannot be created or is not writable (`StartupChecks.java:561` to `594` at `8d744bb0ac`). It does not compare them. `DatabaseDescriptor.getAllDataFileLocations` returns every entry of `data_file_directories`, with `local_system_data_file_directory` in front when it is set (`DatabaseDescriptor.java:2791` to `2797` at `8d744bb0ac`).
4. A check is added to the daemon with `StartupChecks.withTest`, which appends it after the checks already registered (`StartupChecks.java:164` to `168` at `8d744bb0ac`). The `CassandraDaemon` constructor adds `FileSystemOwnershipCheck` that way, after the default checks (`CassandraDaemon.java:220` at `8d744bb0ac`). One more `withTest` call on that line is the hook a fork check needs, and it places the check after `checkDataDirs`, so every directory exists when the check runs.
5. A stock check that an operator can configure has a constant in the enum `StartupChecks.StartupCheckType` (`StartupChecks.java:106` to `125` at `8d744bb0ac`) and is set under `startup_checks` in `cassandra.yaml`, by that constant's name, with the key `enabled` (the commented block `startup_checks`, `conf/cassandra.yaml:2283` to `2303` at `8d744bb0ac`). `Config.startup_checks` is a map keyed by that enum (`Config.java:960` at `8d744bb0ac`). `StartupChecksOptions.apply` gives every constant an `enabled` value: `false` for a constant declared disabled by default, as `check_filesystem_ownership` and `check_data_resurrection` are, and `true` for the others (`StartupChecksOptions.java:81` to `96` at `8d744bb0ac`). `StartupChecksOptions.isDisabled` reads it (`StartupChecksOptions.java:71` to `74` at `8d744bb0ac`). No stock startup check has a nodetool command.
6. Stock code treats two paths as being on the same file system when their `FileStore` objects are equal by `equals`: `Directories.getWriteableLocationToLoadFile` (`src/java/org/apache/cassandra/db/Directories.java:377` to `391` at `8d744bb0ac`). The new check does not use that comparison, for the reason item 9 gives.
7. The in-JVM distributed test framework runs the startup checks of every instance, through `CassandraDaemon.getInstanceForTesting().runStartupChecks()` in `Instance.startup` (`test/distributed/org/apache/cassandra/distributed/impl/Instance.java:628` at `8d744bb0ac`). A test sets `startup_checks` for an instance as a map keyed by the enum: `DataResurrectionCheckTest.testDataResurrectionCheck` (`test/distributed/org/apache/cassandra/distributed/test/DataResurrectionCheckTest.java:71` to `72` at `8d744bb0ac`).
8. Apache's yaml loader refuses a top level key it does not know: `YamlConfigurationLoader.PropertiesChecker.check` throws `Invalid yaml. Please remove properties ... from your cassandra.yaml` (`src/java/org/apache/cassandra/config/YamlConfigurationLoader.java:417` to `424` at `8d744bb0ac`). A name under `startup_checks` is a key of a map typed by the enum, and `YamlConfigurationLoader.loadConfig` turns any failure to build the `Config` into `Invalid yaml` (`YamlConfigurationLoader.java:148` at `8d744bb0ac`). What a binary whose enum lacks the name does with a `cassandra.yaml` that names it was not run: this workspace holds no build and no Apache binary. This record therefore assumes the worse case, that such a node does not start, in problem 2 and in the rollback sentence of REQ-CLD-014 and REQ-CLD-015, which is right in either case.
9. The JDK, read and run on OpenJDK 17.0.21, the JDK of the machine this record was written on. `sun.nio.fs.UnixFileStore.equals` compares three things: the device id, the mount directory and the mount name. That is read from the class with `javap -c`, because that JDK ships no source. So two `FileStore` objects are equal only for paths under the same mount. One file system mounted at two places, as two bind mounts or two container volumes of one host file system are, gives two stores that are not equal, and a check built on that comparison would miss a layout the issue's criterion covers. `Files.getAttribute(path, "unix:dev")` returns the device id alone, as a `Long`. A run of it on that machine printed `35` for `/tmp`, a `tmpfs`, and `2049` for `/var/tmp`, on `/dev/sda1`, and threw `NoSuchFileException` for a path that does not exist. No stock code on the line reads a `unix:` attribute.

Apache `cassandra-6.0` and trunk, read from `apache/cassandra` at commit `2249e37b51` (trunk) and `84bca651ef` (`cassandra-6.0`):

1. Commit `585f89bb42`, "Support custom StartupCheck implementations via SPI", for CASSANDRA-21093, replaced the enum with a name. `StartupCheck.name` returns the name a check has under `startup_checks` in `cassandra.yaml`, `StartupCheck.isConfigurable` and `StartupCheck.isDisabledByDefault` say whether an operator can set it and whether it runs when the yaml does not name it (`StartupCheck.java:44`, `63` and `76` at `2249e37b51`). `StartupChecks.withServiceLoaderTests` loads every `StartupCheck` a jar on the classpath declares through `java.util.ServiceLoader` (`StartupChecks.java:164` to `207` at `2249e37b51`). Both branches carry it.
2. So on a 6.0 line a check of our own needs no edit to a stock file: it is a class under `org.chronitondb` with a service entry, named and switched under `startup_checks`. A check that is configured under `startup_checks` on this line ports to 6.0 with the same yaml.
3. Neither branch has a check that compares the commit log's file system with the data directories'. The default checks on trunk are the list `StartupChecks.DEFAULT_TESTS` (`StartupChecks.java:123` to `141` at `2249e37b51`).

Apache JIRA and the dev list were not read for this record. The one JIRA search this record's author tried was refused by the maintainers' automation on the worker, so no ticket about a warning for a shared commit log disk is cited or ruled out here. The git history of the line names none: no commit subject under `src/java` mentions a shared disk, volume, device or file system. Section 15 item 6 keeps the search as a follow-up for the maintainers.

Other systems, by behaviour: OpenSearch runs a fixed list of bootstrap checks at node start, `BootstrapChecks.checks` (`server/src/main/java/org/opensearch/bootstrap/BootstrapChecks.java:213` to `243` at `83addf7027`, in `opensearch-project/OpenSearch`, Apache License 2.0). None of them compares the storage paths of a node, so OpenSearch has no equivalent of this check and no default to compare with.

No patents were searched or read.

These rules apply to every source:

1. Describe and cite behaviour, published designs, papers, public documentation and code under licences compatible with the Apache License 2.0.
2. Code or text under an incompatible licence, for example the Elastic License, SSPL, BUSL or a proprietary licence, MUST NOT be copied. The behaviour of such a system is taken only from its public documentation. Code under a compatible licence MAY be used only with credit. See [conventions.md](../../process/conventions.md#code-from-elsewhere).
3. Contributors working on the project's behalf MUST NOT search for or read patents for design work. Any patent concern goes to the maintainers.

## 5. Idiom and consistency

OpenSearch has no equivalent of any choice below, as section 4 says, so each item names stock, the earlier decisions and the idiom only.

1. **Off by default.** Stock match: the two stock checks that are declared disabled by default, `check_filesystem_ownership` and `check_data_resurrection`. Earlier decision match: decision record 0004, and branching-and-review.md item 4. Idiom: a behaviour-changing feature is opt in.
2. **The switch under `startup_checks`, with no nodetool command.** Stock match: every configurable stock startup check is switched there and none has a nodetool command. Earlier decision match: decision record 0005, which sets aside the nodetool toggle of branching-and-review.md item 1 for this feature, because a startup check has run before nodetool can reach the node. Idiom: stock `startup_checks`, which Apache 6.0 extends to custom checks by name.
3. **The entry name `check_commitlog_shared_disk`.** Stock match: the stock names are `check_` and what is checked, in lower case, the words joined by `_`. Earlier decision match: decision record 0005 names it, and conventions.md, Names, item 1 is met. Idiom: stock.
4. **Same file system, not same physical device, told by the device id.** Stock match: differs on purpose. Stock compares `FileStore` objects in `Directories.getWriteableLocationToLoadFile`, and that comparison also needs the same mount (section 4, item 9 of the first list). It would give no warning for one file system mounted at two places, which the issue's criterion covers. The check compares the device id of the file system instead. Earlier decision match: decision record 0006. Idiom: the sentence of the issue. A deliberate limit: two file systems on one physical device get no warning, and the reference page says so.
5. **Which directories are data directories.** Every directory `DatabaseDescriptor.getAllDataFileLocations` returns: each entry of `data_file_directories`, and `local_system_data_file_directory` when it is set. Stock match: the set `StartupChecks.checkDataDirs` and `FileSystemOwnershipCheck` treat as the data directories. Earlier decision match: none on this point. Idiom: stock. The hints, saved caches and CDC directories are not compared, because the issue names the data directories only.
6. **One WARN line per start, naming every sharing directory.** Stock match: `StartupChecks.checkReadAheadKbSetting` and `StartupChecks.checkMaxMapCount` warn at WARN and let the node start. Earlier decision match: none. Idiom: stock.
7. **Nothing logged on a clean pass, and nothing while off.** Stock match: the stock warning checks log nothing when they find nothing. The stock ownership check logs an INFO line when it is off, and this check does not, for the reason section 3 gives. Earlier decision match: branching-and-review.md item 7. Idiom: stock. An operator tells a clean pass from a check that did not run by the three counters, which exist only after a run.
8. **An unreadable file system warns and the check goes on.** Stock match: `StartupChecks.checkReadAheadKbSetting` logs a WARN with the exception and goes on when `Files.getFileStore` throws. Earlier decision match: none. Idiom: stock.
9. **The counters `SharedDataDirectories`, `UnreadableDirectories` and `FailedRuns` of the type `CommitLogDiskCheck`.** Stock match: Dropwizard counters through `CassandraMetricsRegistry.counter` (`CassandraMetricsRegistry.java:55` at `8d744bb0ac`), named by a `CassandraMetricsRegistry.MetricName` from its five argument constructor (`CassandraMetricsRegistry.java:818` at `8d744bb0ac`), so each MBean name is exactly the one REQ-CLD-010, REQ-CLD-011 and REQ-CLD-020 give. Earlier decision match: conventions.md, Names, items 3 and 4, fork metrics use their own type and the `org.chronitondb` domain, and quality-requirements.md, every outcome has a counter. Idiom: a counter named for what it counts.

## 6. Quality requirements

| ISO/IEC 25010 characteristic | Line | Requirements, or the reason it does not apply |
|---|---|---|
| Performance efficiency | Fastest correct design, with benchmarks in the design and in the gates | Does not apply, because no request path runs the code: the check runs once at node start. Section 7. |
| Performance efficiency | Memory budgets on coordinator and replica | Does not apply, because the only memory is one check object and one options map on every node, and three counters with the switch on, a few hundred bytes together, allocated once. |
| Reliability | Isolation levers on coordinator and replica: thread pools, limits, load shedding, timeouts, kill switch | REQ-CLD-004 and REQ-CLD-005: the kill switch is the yaml entry, off by default. No thread, pool, limit or timeout exists, because the check does its work once, on the thread that runs the stock startup checks. |
| Reliability | Automatic fallbacks opt-in, with yaml setting, nodetool toggle, metric and rate-limited log line | Does not apply, because there is no fallback to a costlier path. A lookup that throws is left out, logged by REQ-CLD-007 and counted by REQ-CLD-011. |
| Reliability | Coordination between nodes model checked, when the design changes it | Does not apply, because each node checks its own directories and nothing crosses the network. |
| Compatibility | Stock Apache Cassandra behaviour unchanged | REQ-CLD-004, REQ-CLD-005. Section 3: the two changes behind the switch and the one presence, with its reason. |
| Compatibility | Stock behaviour unchanged with the feature off | REQ-CLD-004. `CommitLogDiskCheckTest.offDoesNothing` and `CommitLogDiskCheckStartTest.defaultNodeLogsNothingNew` prove it, and the stock suites of section 14 run unchanged with the switch at its default, off. While off the node holds the constant, the options map and the registered check of row 3 of the departures table in section 3, a departure from branching-and-review.md item 7 for the maintainers to approve. |
| Compatibility | Mixed-version cluster, upgrade and rollback (see the Compatibility section) | REQ-CLD-014, REQ-CLD-015 and section 9. |
| Functional suitability | CQL validity and results independent of replication factor, data centres and replica count | Does not apply, because the change has no CQL and reads no data. |
| Flexibility | Settings per index or per table over global ones, with global, include and exclude modes | Does not apply, because the setting is a property of the node, not of data. |
| Interaction capability | nodetool toggles change the in-memory value only, yaml holds the startup value | Does not apply, because the feature has no nodetool toggle (decision record 0005, waiver 3). The yaml holds the only value. |
| Interaction capability | Error messages name the setting or toggle that controls the behaviour | REQ-CLD-001, REQ-CLD-007 and REQ-CLD-017: the three warnings name `check_commitlog_shared_disk`. The switch refuses nothing, so there is no error. |
| Maintainability | Observability: metrics, traces and diagnostics as a gate item | REQ-CLD-001, REQ-CLD-007, REQ-CLD-010, REQ-CLD-011, REQ-CLD-017, REQ-CLD-018, REQ-CLD-020. Section 8. |
| Security | Threat model answered (see the Threat model section) | Section 10: no new entry point. |
| Safety | Any risk of data loss or corruption named, with its mitigation | None from the code: the check reads two settings and the device id of each directory, and writes nothing to disk, to the commit log or to any table. A missed warning leaves the operator's layout as it was, see problem 5. |

The design changes no coordination between nodes, so it carries no model.

## 7. Performance

### Hot path statement

No request type touches the new code. Coordinator reads and writes, replica reads, memtable writes, flush, compaction, streaming and repair never call it. The code runs once at node start, on the thread that runs the stock startup checks.

### Expected cost

| Path | Metric | Stock today | Expected with the change | Why (mechanism) |
|---|---|---|---|---|
| Node start, switch off | work | the stock checks | one more call of `StartupChecksOptions.isDisabled` | one lookup in an `EnumMap` and one `Boolean.parseBoolean` |
| Node start, switch on | file system lookups | one `Files.getFileStore` for each data directory, in `StartupChecks.checkReadAheadKbSetting` | one device id read for the commit log directory and one for each data directory | `Files.getAttribute` with `unix:dev` once for each directory, then one comparison of two numbers for each data directory |
| Node start | heap | the stock checks and their options | one more check object and options map, and with the switch on three counters | a few hundred bytes, allocated once |

### Isolation levers

The yaml entry `check_commitlog_shared_disk` with the key `enabled`. Off, the default: the check returns at its first statement. No thread pool, no memory limit and no timeout exist, since the check runs once, at start.

### Benchmarks that prove it

| Claim | Benchmark | Command | Pairs | Threshold |
|---|---|---|---|---|
| none | none, there is no request path to measure | none | none | none |

### Regression threshold and gate

No benchmark gates this pull request. The gate runs the tests of section 14.

### Stock guard

The stock suites of section 14 run unchanged. They run with the switch at its default, off, which is the state in which the node must match stock, so one run is the guard. `CommitLogDiskCheckTest.offDoesNothing` and `CommitLogDiskCheckStartTest.defaultNodeLogsNothingNew` prove the off state itself.

### What was not measured

Nothing was measured, because the change is off every request path. No follow-up issue is needed.

## 8. Observability

1. **Counted.** Three counters of the type `CommitLogDiskCheck`, registered at the start of every run with the switch on, step 3 of the run, and never while the switch is off (REQ-CLD-018). `org.chronitondb.metrics:type=CommitLogDiskCheck,name=SharedDataDirectories` rises by the number of data directories found on the commit log directory's file system (REQ-CLD-010). `org.chronitondb.metrics:type=CommitLogDiskCheck,name=UnreadableDirectories` rises by the number of directories whose file system lookup threw (REQ-CLD-011). `org.chronitondb.metrics:type=CommitLogDiskCheck,name=FailedRuns` rises by one when the run ends with the failed warning (REQ-CLD-020). The check runs once in the life of a node process, so the counters hold the result of that run: all three at 0 after a clean pass, the first above 0 after a shared warning, the second above 0 after an unreadable warning, the third at 1 after a failed run. A node without the counters did not run the check, or their registration threw, which the failed warning in its log shows.
2. **Timed.** Nothing: no duration to measure.
3. **Logged.** The shared warning, once for each start, at WARN (REQ-CLD-001). Its text, with the two SLF4J placeholders: `The commit log directory {} is on the same file system as the data directories {}. One failure of that file system loses the commit log and the data together, and on spinning disks commit log writes compete with reads, flushes and compaction. Put commitlog_directory on a file system of its own. This warning comes from the startup check check_commitlog_shared_disk.` The first placeholder is the commit log directory as `DatabaseDescriptor.getCommitLogLocation` returns it. The second is the sharing data directories, in the order `DatabaseDescriptor.getAllDataFileLocations` returns them, in square brackets and separated by a comma and a space, as a Java `List` prints. The unreadable warning, once for each directory whose lookup threw, at WARN, with the exception as the last logging argument (REQ-CLD-007). Its text: `The startup check check_commitlog_shared_disk could not read the file system of {} and left that directory out.` The placeholder is the directory as `DatabaseDescriptor.getCommitLogLocation` or `DatabaseDescriptor.getAllDataFileLocations` returns it, the same string the shared warning prints for it. The failed warning, once, at WARN, with the exception as the last logging argument, when an `Exception` ends the run in step 2 (REQ-CLD-017). Its text: `The startup check check_commitlog_shared_disk failed and compared nothing more.` After it the check does no further lookup (REQ-CLD-019). It can follow an unreadable warning of the same run. Nothing is logged on a clean pass or while the switch is off. Nothing is rate limited, since the check runs once.
4. **Traced.** Does not apply: no query runs, so there is no trace session to write to.
5. **Client visible.** Nothing: no client request reaches the check.
6. **Exposed.** The three counters over JMX and through any configured metrics reporter. The switch shows in the row `startup_checks` of `system_views.settings` and in the start log line `Node configuration:`, which `Config.log` writes for every field (`Config.java:1347` to `1376` at `8d744bb0ac`), on a node whose yaml names the entry.
7. **Toggled.** In `cassandra.yaml` only, read at start. No nodetool toggle (decision record 0005).
8. **Audited.** Nothing: the check changes no data and no access.
9. **Released on drop.** The counters live as long as the node. Nothing drops them.
10. **Documented.** The reference page of section 13 lists the entry, the three warnings and the three counters by exact name (REQ-CLD-016).
11. **Tested.** `CommitLogDiskCheckTest` asserts the log lines and the counters, and `CommitLogDiskCheckStartTest` asserts the shared warning in the log of a started node. No tracing test, see section 14.

No line above TRACE carries a key, a term, a literal or a secret: the lines carry directory paths, which the stock start log line `Node configuration:` already prints.

## 9. Compatibility

1. **On-disk format changes.** None. The check writes no file.
2. **Mixed-version cluster.** Does not apply to behaviour between nodes: each node checks its own directories at its own start, and nothing crosses the network.
3. **Upgrade path and prerequisites.** None. A `cassandra.yaml` that does not name the entry loads on Apache Cassandra, on an older ChronitonDB build and on a build with this change, and behaves the same on all three.
4. **Rollback path.** An operator who wrote the entry into `cassandra.yaml` MUST remove it before starting an Apache Cassandra binary or a ChronitonDB build older than this change on that node. Such a binary does not know the name, and this record assumes it does not start (section 4, stock item 8). When the entry was the only one under `startup_checks`, the operator removes that key as well: a key left with no value loads as null, and the stock loader refuses null for a setting that is not null by default (`YamlConfigurationLoader.PropertiesChecker`, `YamlConfigurationLoader.java:316` to `317`, `370` to `374` and `417` to `420` at `8d744bb0ac`, read and not run). REQ-CLD-014 and REQ-CLD-015 put that line on the reference page and in `NEWS-chronitondb.txt`.
5. **Runbook entries.** No runbook exists on this line. The rollback sentence lives on the reference page and in `NEWS-chronitondb.txt` until a runbook item creates one.
6. **Surfaces touched.** Configuration: one new name under `startup_checks`, which no existing yaml uses. JMX and metrics: two new counters under a fork type, with the switch on only. The start log: one or more new WARN lines, with the switch on only. No version of any surface is bumped, and the stock tests `StartupCheckOptionsTest`, `StartupChecksTest`, `YamlConfigurationLoaderTest` and `SettingsTableTest` pass unchanged.
7. **Shared state.** The switch writes nothing to shared state, off or on. The check reads `cassandra.yaml` through the stock options and the local file systems.
8. **The other line.** The item carries one line label, `chronitondb-sandbox`. On a 6.0 line the check is a service entry and needs no stock edit, with the same yaml (section 4). That port is section 15 item 2.

## 10. Threat model and security

No new entry point. The only input is `cassandra.yaml`, which the operator who runs the node writes, and which the stock loader parses. The check reads one value of it, `enabled`, through `StartupChecksOptions.isDisabled`, which parses it with `Boolean.parseBoolean` (`StartupChecksOptions.isEnabled`, `StartupChecksOptions.java:66` to `69` at `8d744bb0ac`), so the check is on exactly when the same value would switch a stock startup check on, and `enabled: true` does. The check adds no parsing of its own. Other keys under the entry are not read. The check opens no port, adds no CQL, no MBean operation and no permission, and needs none.

By STRIDE, for the code that runs with the switch on. Spoofing, tampering, repudiation and elevation of privilege do not apply: the check authenticates nobody, writes nothing and grants nothing. Information disclosure: the two warnings carry directory paths and, for the unreadable warning, the exception of the lookup. The stock start log already carries the same paths in its `Node configuration:` line, and the counters carry two numbers. Denial of service: a check that threw would stop the node, which REQ-CLD-006 and REQ-CLD-013 exclude. The number of lookups is bounded by the number of configured data directories plus one.

No audit entry, no limit with warn and fail thresholds and no client error exists, because no client request reaches the code.

## 11. Dependencies

No new dependency.

## 12. Compliance impact

The check copies no user data, so nothing needs erasure, masking, retention or a residency rule, and backups and snapshots hold nothing new. It logs directory paths and counts directories, never row data, keys or credentials. It uses no cryptography and adds no library, so the supply chain is unchanged. The default is the safe one: off. The isolation lever is the switch.

For operators: the check is switched with `enabled` in the entry `check_commitlog_shared_disk` under `startup_checks` in `cassandra.yaml`. It is off on a node whose yaml does not name the entry, and it reads `enabled` as the stock startup checks do. It reads the settings `commitlog_directory`, `data_file_directories` and `local_system_data_file_directory`, and writes nothing.

## 13. Documentation

This item adds one reference page, `docs/reference/commitlog-disk-check.md`, written by the developer from the skeleton `page-commitlog-disk-check.md` next to this record, because documentation ships in the same pull request as the code (conventions.md, Where things live, item 5). The path follows the reference page the design record of the release version feature proposes, `docs/reference/release-version.md`. The maintainers approve the path with this record, and a later item moves the page when a layout is decided. The page is a reference page in the Diátaxis sense and carries:

1. The entry `check_commitlog_shared_disk` under `startup_checks`, its key `enabled`, type boolean, default `false`, read at start only, with the yaml example of section 1.
2. What the check compares: the file system of `commitlog_directory` with the file system of each entry of `data_file_directories` and of `local_system_data_file_directory` when it is set. It tells a file system by the device id the operating system reports, so one file system mounted at two places is found.
3. The shared warning, the unreadable warning and the failed warning, each with its fixed text.
4. The three counters by their full names, what each counts, and that they exist only on a node that ran the check.
5. Failure behaviour: the node starts in every case. A directory whose file system cannot be read is left out, with the unreadable warning. On a platform without the `unix` attribute view that is the commit log directory, at every start with the check on. Any other error in the check gives the failed warning. Timeouts, coordinator failure, a missing replica, a limit and an index that is not built do not apply, because no request reaches the check.
6. Known limitations. Two file systems on one physical device, such as two partitions of one disk or two logical volumes of one volume group, get no warning (decision record 0006). The same holds for two subvolumes of one file system where the file system reports a device id of its own for each subvolume. btrfs is said to do so, which this record did not verify. The hints, saved caches and CDC directories are not compared. The value is read at start only, so a change needs a restart.
7. The rollback sentence (REQ-CLD-014).

`NEWS-chronitondb.txt` gains an entry for the new check and the rollback sentence (REQ-CLD-015). The delta entry `docs/delta/commit-log-disk-check.md` with its row in `docs/delta/README.md` records the stock edits and the stock behaviour changes of section 3. `CommitLogDiskCheckDocsTest` of section 14 reads the reference page and the news file for the lines REQ-CLD-014 and REQ-CLD-015 require and the exact texts REQ-CLD-016 requires.

Apache's `conf/cassandra.yaml` stays untouched, so the commented `startup_checks` block there does not list the new entry. `conf/cassandra_chronitondb.yaml` does not exist on this line, see section 15 item 3.

## 14. Testing

Three unit test classes under `test/unit/org/chronitondb/startup/` and one in-JVM distributed test class under `test/distributed/org/chronitondb/startup/test/`. [conventions.md, Where things live](../../process/conventions.md#where-things-live) gives both roots. The last directory of the distributed test is named `test` because the stock target that runs the whole in-JVM suite takes only classes in a directory of that name (the target `test-jvm-dtest`, `build.xml:1762` to `1763` at `8d744bb0ac`). A class one level up would run when named alone and never with the suite. The distributed test starts one node. Nothing is multi node in behaviour, each node checks itself, so replication factor does not apply. No sstable format or compaction is touched. The parity suite does not exist on this line yet, see waiver 1. This item adds no scenario, under waiver 2, so the template's `Scenario runner` and `Scenario tags` lines are left out. Existing suites at risk names the stock suites whose files or behaviour this change touches, and Stock suites run unchanged is the wider set that proves stock behaviour and includes the first. Every test sets its own starting state, so none depends on the order JUnit runs them in.

The test seam. `CommitLogDiskCheck` has two constructors. The one without arguments, which the daemon calls, reads nothing (REQ-CLD-013): it hands on two lambdas, in the form of the stock constructor `FileSystemOwnershipCheck.FileSystemOwnershipCheck` (`FileSystemOwnershipCheck.java:100` to `106` at `8d744bb0ac`), which the daemon runs at the same point today. The lambdas call `DatabaseDescriptor.getCommitLogLocation` and `DatabaseDescriptor.getAllDataFileLocations` only when `execute` calls them. It also hands on the file system lookup that reads `unix:dev`. The second constructor, for tests, takes the two suppliers, the lookup and the function that registers a counter, by default `CassandraMetricsRegistry.counter`, as `FileSystemOwnershipCheck` takes its directories through a supplier for its tests (`FileSystemOwnershipCheck.FileSystemOwnershipCheck`, `FileSystemOwnershipCheck.java:108` to `112` at `8d744bb0ac`). The lookup takes a directory as the string its getter returned and returns the device id as a `long`, or throws, so it has no empty answer. The unit tests give the check directory names and a lookup that answers a fixed number for each name, or throws. The log lines are asserted through the logback appender the stock tests use. The counters live in the registry of the JVM. A test reads a counter from the registry's map of counters, the Dropwizard `MetricRegistry.getCounters` that `CassandraMetricsRegistry` inherits, never through `CassandraMetricsRegistry.counter`, which would create it. It takes a counter that is not in the map as 0 and asserts the difference from the value it read before the run.

What each test of the list under Tests for this change proves:

1. `CommitLogDiskCheckTest.sharedFileSystemWarnsOnce`: with the switch on, a commit log directory on device 1 and four data directories on devices 1, 2, 1 and 1, the fourth the same string as the first, the check logs exactly one WARN line. That line equals the shared warning with the commit log directory and the first and third data directory, in that order, the repeated one listed once (REQ-CLD-001, REQ-CLD-002).
2. `CommitLogDiskCheckTest.separateFileSystemsLogNothing`: with the switch on and every data directory on a device other than the commit log's, the check logs no line at WARN or above (REQ-CLD-003).
3. `CommitLogDiskCheckTest.offDoesNothing`: the test first removes the three counters from the registry with `CassandraMetricsRegistry.remove` (`CassandraMetricsRegistry.java:208` at `8d744bb0ac`). Then, with the options of `new StartupChecksOptions()` and with suppliers and a lookup that fail the test when called, `execute` returns, none of them was called, the check's logger wrote no line, and the map of counters holds none of the three counters (REQ-CLD-004).
4. `CommitLogDiskCheckTest.switchIsOffByDefault`: `new StartupChecksOptions().isDisabled(check_commitlog_shared_disk)` is `true` (REQ-CLD-005).
5. `CommitLogDiskCheckTest.neverThrows`: with the switch on, `execute` returns normally in each of four cases: the lookup throws `IOException` for the commit log directory, the lookup throws `UnsupportedOperationException`, an unchecked exception, for a data directory only, the supplier of the data directories throws `IllegalStateException`, and the function that registers a counter throws `IllegalStateException` (REQ-CLD-006).
6. `CommitLogDiskCheckTest.unreadableDirectoryWarns`: with the switch on, three data directories on devices other than the commit log's, and a lookup that throws `IOException` for the second of them, the check logs exactly one WARN line, the unreadable warning with that directory. With a lookup that throws for the commit log directory, it logs exactly one WARN line, the unreadable warning with the commit log directory (REQ-CLD-007).
7. `CommitLogDiskCheckTest.unreadableDirectoryDoesNotHideOthers`: with the switch on, the commit log directory and the first and third data directories on device 1, and a lookup that throws for the second, the check logs two WARN lines: the unreadable warning with the second data directory and the shared warning with the first and third (REQ-CLD-008).
8. `CommitLogDiskCheckTest.unreadableCommitLogEndsTheComparison`: with the switch on, three data directories and a lookup that throws for the commit log directory and records its calls, the lookup was called once, for the commit log directory, and the check logged no shared warning (REQ-CLD-009).
9. `CommitLogDiskCheckTest.countsSharedDirectories`: the counter `SharedDataDirectories` is in the map of counters after each of these runs. It rose by 2 in the case of test 1, by 0 in the case of test 2 and by 0 in the case of test 8 (REQ-CLD-010).
10. `CommitLogDiskCheckTest.countsUnreadableDirectories`: the counter `UnreadableDirectories` is in the map of counters after each of these runs. It rose by 1 in the case of test 7, by 1 in the case of test 8 and by 0 in the case of test 1 (REQ-CLD-011).
11. `CommitLogDiskCheckConstructionTest.constructorReadsNoConfig`: a class of its own that holds this one test and loads no configuration. It asserts that `DatabaseDescriptor.getRawConfig()` is `null` (`DatabaseDescriptor.getRawConfig`, `DatabaseDescriptor.java:385` at `8d744bb0ac`), builds `new CommitLogDiskCheck()` without an exception, and asserts `null` again. A constructor that read a directory setting would throw `NullPointerException` here, as it would in the static initialiser of `CassandraDaemon` (REQ-CLD-013).
12. `CommitLogDiskCheckStartTest.enabledNodeWarnsAndStarts`: an in-JVM cluster of one node, configured with `startup_checks` holding the entry with `enabled` set to `true`, starts and answers `SELECT * FROM system.local`. Its log holds exactly one WARN line that contains `check_commitlog_shared_disk`, and that line is the shared warning with the instance's commit log directory and each of its data directories. The framework keeps all directories of an instance under one root. The test first asserts, with `Files.getAttribute` and `unix:dev`, that they are on one file system, so a test host that splits them fails with that message and not with a missing warning (REQ-CLD-012, and acceptance criteria 1 and 2 end to end).
13. `CommitLogDiskCheckStartTest.defaultNodeLogsNothingNew`: an in-JVM cluster of one node with the default configuration starts, and its log holds no line that contains `check_commitlog_shared_disk` (REQ-CLD-004 end to end, and the proof that the hook is silent while off).
14. `CommitLogDiskCheckDocsTest`, reading each file from the project root the tests run in. `rollbackLineOnReferencePage`: `docs/reference/commitlog-disk-check.md` has a line that holds the rollback sentence whole, letter for letter (REQ-CLD-014). `rollbackLineInNews`: the same for `NEWS-chronitondb.txt` (REQ-CLD-015). `exactNamesAreDocumented`: the text of the reference page, read as one string, contains each of the seven texts of REQ-CLD-016, with one assertion for each text that names the text that is missing. For a warning, the texts looked for are its fixed parts: the text before its first placeholder, the text between two placeholders and the text after the last. The page keeps each warning on one line, as the skeleton does, so each fixed part is found whole (REQ-CLD-016).
15. `CommitLogDiskCheckTest.failureOutsideALookupWarns`: with the switch on and a supplier of the commit log directory that throws `IllegalStateException`, `execute` returns and the check logs exactly one WARN line, the failed warning (REQ-CLD-017).
16. `CommitLogDiskCheckTest.registersTheCounters`: the test removes the three counters from the registry, runs the check with the switch on and a supplier of the commit log directory that throws, and finds the three counters in the map of counters (REQ-CLD-018).
17. `CommitLogDiskCheckTest.failureEndsTheRun`: with the switch on, three data directories, a lookup that throws for the first of them and records its calls, and a counter function that hands back, for `UnreadableDirectories`, a counter whose raise throws, the check logs two WARN lines, the unreadable warning for that directory and then the failed warning. The lookup was called twice, for the commit log directory and for the first data directory (REQ-CLD-019).
18. `CommitLogDiskCheckTest.countsFailedRuns`: the counter `FailedRuns` rose by 1 in the case of test 15 and by 0 in the case of test 1 (REQ-CLD-020).

The stock suites below run unchanged, `StartupCheckOptionsTest` first among them. Four stock test classes build a `CassandraDaemon` of their own and so run the hook line: `DefaultFSErrorHandlerTest`, `DiskFailurePolicyTest`, `JVMStabilityInspectorTest` and `CommitLogFailurePolicyTest`. They are in both lists.

Class loading in the in-JVM framework. Tests 12 and 13 need the framework to load `org.chronitondb.startup.CommitLogDiskCheck` in each instance's class loader, beside the instance's own `StartupCheck`. `AbstractCluster.getSharedClassPredicate` shares a class between instances when it is marked as shared or when `InstanceClassLoader.getDefaultLoadSharedFilter` names it (`test/distributed/org/apache/cassandra/distributed/impl/AbstractCluster.java:1186` to `1197` at `8d744bb0ac`). That filter lives in the dtest-api library, whose jar is not in the workspace this record was written in, so it was not read. If it shared the fork class, every in-JVM instance would fail in `StartupChecks.verify` with a `ClassCastException`, with the switch off too. So the developer runs `DataResurrectionCheckTest` and test 13 first, right after the two hook edits. If they fail that way the work stops: the fix would edit a stock test file outside the Planned file list, which needs change control. This is problem 8.

### Tests for this change

org.chronitondb.startup.CommitLogDiskCheckTest
org.chronitondb.startup.CommitLogDiskCheckConstructionTest
org.chronitondb.startup.test.CommitLogDiskCheckStartTest
org.chronitondb.startup.CommitLogDiskCheckDocsTest

### Existing suites at risk

org.apache.cassandra.config.StartupCheckOptionsTest
org.apache.cassandra.service.StartupChecksTest
org.apache.cassandra.service.YamlBasedFileSystemOwnershipCheckTest
org.apache.cassandra.service.SystemPropertiesBasedFileSystemOwnershipCheckTest
org.apache.cassandra.distributed.test.DataResurrectionCheckTest
org.apache.cassandra.service.DefaultFSErrorHandlerTest
org.apache.cassandra.service.DiskFailurePolicyTest
org.apache.cassandra.utils.JVMStabilityInspectorTest
org.apache.cassandra.db.commitlog.CommitLogFailurePolicyTest

### Stock suites run unchanged

org.apache.cassandra.config.StartupCheckOptionsTest
org.apache.cassandra.service.StartupChecksTest
org.apache.cassandra.service.YamlBasedFileSystemOwnershipCheckTest
org.apache.cassandra.service.SystemPropertiesBasedFileSystemOwnershipCheckTest
org.apache.cassandra.distributed.test.DataResurrectionCheckTest
org.apache.cassandra.service.DefaultFSErrorHandlerTest
org.apache.cassandra.service.DiskFailurePolicyTest
org.apache.cassandra.utils.JVMStabilityInspectorTest
org.apache.cassandra.db.commitlog.CommitLogFailurePolicyTest
org.apache.cassandra.config.YamlConfigurationLoaderTest
org.apache.cassandra.config.DatabaseDescriptorTest
org.apache.cassandra.config.ConfigCompatibilityTest
org.apache.cassandra.db.virtual.SettingsTableTest
org.apache.cassandra.metrics.CassandraMetricsRegistryTest

### Tracing test

does not apply, because no query runs through the change, so there is no trace session to show it in

### Formats and configurations

no

## 15. Not covered and follow-ups

1. The physical device under two file systems is not compared, by decision record 0006. The reference page lists the limitation.
2. The port to a 6.0 line, where the check is a class with a `java.util.ServiceLoader` entry and no stock file is edited (section 4). This item carries one line label. Candidate issue, for a maintainer to open when a 6.0 line takes the feature.
3. `conf/cassandra_chronitondb.yaml` does not exist on this line. When the item that creates it lands, the entry goes into it, commented out with its default. Candidate issue, for a maintainer to open. The code merge does not depend on it.
4. A nodetool command or a JMX operation that runs the check on a live node is out, by decision record 0005.
5. The hints, saved caches and CDC directories are not compared with the data directories or with each other. The issue names the commit log and the data directories only.
6. Apache JIRA and the dev list were not searched for earlier discussion of such a warning, see section 4. Candidate task for a maintainer: the search `project = CASSANDRA AND text ~ "commitlog data directory same disk"`. Nothing in this record depends on its result, since no Apache branch read here has the check.
7. What an Apache Cassandra binary does with a `cassandra.yaml` that names the entry was not run, see section 4, stock item 8. The rollback sentence is written for the worse case. A maintainer with an Apache 5.0 binary can settle it with one start.
8. [branching-and-review.md](../../process/branching-and-review.md#feature-switches-and-defaults) item 1 says every fork feature has a nodetool toggle. Decision record 0005 sets it aside for this feature. Whether the page should name startup checks as a standing exception is a documentation only change for the maintainers to decide. Candidate issue.
9. The scenarios of the feature `CLD`, once the scenario module `test/bdd/`, its runner and the shared step library exist on the line. Candidate issue, for a maintainer to open when the module lands. The code merge does not depend on it, see waiver 2.
10. `NEWS-chronitondb.txt` and `docs/reference/` do not exist on the line today, and the design record of the release version feature plans to create both. The Planned file list names `NEWS-chronitondb.txt` as `new`. If that feature's code merges first, the word becomes `edit`, through change control.

## New terms

1. **The switch**: the answer of `StartupChecksOptions.isDisabled` for the entry `check_commitlog_shared_disk` under `startup_checks` in `cassandra.yaml`, the opposite of `StartupChecksOptions.isEnabled` (`StartupChecksOptions.java:66` to `74` at `8d744bb0ac`). The check reads the switch in no other way, so a value of the key `enabled` switches it on exactly when the same value would switch a stock startup check on. `enabled: true` does. A missing entry and an entry without the key leave it off. Which other spellings the yaml loader reads as true was not read for this record, because the source of the yaml library is not in the workspace it was written in. In code the enum constant `StartupChecks.StartupCheckType.check_commitlog_shared_disk`, in docs "the check's `enabled` key".
2. **The data directories**: the directories `DatabaseDescriptor.getAllDataFileLocations` returns, every entry of `data_file_directories` and `local_system_data_file_directory` when it is set, in the order of the array. A directory the array holds more than once, as the same string, counts once, at its first place: the check looks it up once, lists it once and counts it once.
3. **The file system lookup**: the read of the device id of the file system that holds a directory, `Files.getAttribute(path, "unix:dev")`, which returns a `Long` that the lookup hands on as a `long`. The read follows symbolic links, so it answers for the place the files are in. The `unix` attribute view exists on Linux and macOS. The line does not run on Windows (the section Windows Support Removed, `NEWS.txt:903` to `906` at `8d744bb0ac`). On a platform without the view the lookup throws, which REQ-CLD-007 covers.
4. **Shares a file system**: two directories share a file system when their file system lookups return the same device id. One file system mounted at two places counts as shared. Two file systems on one physical device do not.
5. **The shared warning**: the WARN line of section 8, item 3, with its fixed text and its two placeholders.
6. **The unreadable warning**: the WARN line of section 8, item 3, for one directory whose file system lookup threw.
7. **The failed warning**: the WARN line of section 8, item 3, for an `Exception` that ends a run in step 2 of the run.
8. **The rollback sentence**: this exact text, on one line: `Before a node runs an Apache Cassandra binary, or a ChronitonDB build older than this feature, remove check_commitlog_shared_disk from its cassandra.yaml, and remove startup_checks as well when it then holds no other entry.`
9. **Commit log disk check**: the feature, key `CLD`. In code `org.chronitondb.startup.CommitLogDiskCheck`, in yaml `check_commitlog_shared_disk`, in docs "commit log disk check".

## Where problems could occur

1. **A node does not start.** Seen by an operator as a node that exits during startup, on every node if the hook in the `CassandraDaemon` constructor or the constructor of the check throws, or on nodes with the switch on if `execute` lets an exception out, since `CassandraDaemon.runStartupChecks` catches `StartupException` only. From the hook line and from `CommitLogDiskCheck.execute`. REQ-CLD-006 makes `execute` return normally whatever `Exception` is thrown in it, and REQ-CLD-017 logs one that no lookup threw. REQ-CLD-013 keeps the constructor from reading a configuration that is not loaded yet, which would stop every node, switch on or off.
2. **A node rolled back to an Apache Cassandra binary, or to an older ChronitonDB build, does not start.** Seen as an `Invalid yaml` error at start, on a node whose operator wrote the entry into the yaml. From the new name under `startup_checks`. Not from the default: a yaml that never names the entry loads on every binary.
3. **A node that does not use the feature logs, counts or holds something a stock node does not.** Seen as a new line in the start log of every node, a new metric on every dashboard, or a stock startup check that behaves differently because the enum grew. From the hook, from the new constant, or from a check that works before it reads the switch. REQ-CLD-004 excludes the first two, the stock suites of section 14 run unchanged against the third, and row 3 of the departures table names what is held.
4. **The warning is wrong.** Seen by an operator as a shared warning that names a directory on another file system, or that misses one that shares, so that the operator moves a directory for nothing or trusts a wrong list. From the comparison in `CommitLogDiskCheck`. REQ-CLD-002 and REQ-CLD-003.
5. **The warning is missing.** Seen as a silent start log on a node whose commit log and data share a file system, with the switch on, so that the operator believes the layout is sound. From a hook that does not register the check, from a comparison that never matches, or from the limit of decision record 0006: two file systems on one physical device. REQ-CLD-001 and REQ-CLD-012 cover the first two. The third is by decision, and the reference page says it.
6. **The file system of a directory cannot be read.** Seen as no warning and no hint why, on a file system or under a security policy where the device id cannot be read. From the file system lookup. REQ-CLD-007 to REQ-CLD-009 and REQ-CLD-011 make it one WARN line for that directory, a count, and a full comparison of the rest when the directory is a data directory.
7. **An operator cannot tell whether the check ran, or finds the page naming the entry, a counter or a warning wrongly.** Seen as a clean start log that could mean a clean layout or a check that never ran, or as a documented name the node does not know. From the silence on a clean pass and from a page written by hand. REQ-CLD-010, REQ-CLD-011, REQ-CLD-018 and REQ-CLD-020 give the three counters, which exist only after a run, and REQ-CLD-016 pins the exact names on the page.
8. **Every in-JVM distributed test fails to start its instances.** Seen by a developer as a `ClassCastException` at instance start in every in-JVM test, with the switch off too. From the hook line, if the in-JVM test framework loads the fork class once for all instances and not in each instance's class loader. Not seen on a real node, which has one class loader. Section 14 says what was not read and what the developer runs first.

### Test plan

1. Problem 1: `CommitLogDiskCheckTest.neverThrows` makes a lookup throw a checked exception, a lookup throw an unchecked one and a supplier throw, and asserts each time that `execute` returns. `failureOutsideALookupWarns` asserts the failed warning. `CommitLogDiskCheckConstructionTest.constructorReadsNoConfig` builds the check with no configuration loaded. `CommitLogDiskCheckStartTest.enabledNodeWarnsAndStarts` and `defaultNodeLogsNothingNew` start a real node through the hook, switch on and off, and the stock tests that build a `CassandraDaemon` run unchanged.
2. Problem 2: no test on this line can start an Apache binary. `CommitLogDiskCheckDocsTest.rollbackLineOnReferencePage` and `rollbackLineInNews` prove the rollback sentence is in both files, letter for letter. Watched through the reference page and the `NEWS-chronitondb.txt` entry, and settled by the one start of section 15 item 7.
3. Problem 3: `CommitLogDiskCheckTest.offDoesNothing` asserts no read, no lookup, no log line and no counter with the switch off, `CommitLogDiskCheckStartTest.defaultNodeLogsNothingNew` asserts a start log without the entry's name on a real node, and the stock suites of section 14 run unchanged, `StartupCheckOptionsTest` and `SettingsTableTest` among them.
4. Problem 4: `CommitLogDiskCheckTest.sharedFileSystemWarnsOnce` compares the whole line, so a directory too many or too few fails, and `separateFileSystemsLogNothing` asserts silence when nothing shares.
5. Problem 5: `CommitLogDiskCheckStartTest.enabledNodeWarnsAndStarts` fails when the hook is missing or the comparison never matches on real directories. No test on one host can mount one file system twice or see the physical device under two file systems. The first rests on the device id, which the operating system reports the same for every mount of a file system. The second is the limit of decision record 0006 and is watched through the known limitation on the reference page.
6. Problem 6: `CommitLogDiskCheckTest.unreadableDirectoryWarns`, `unreadableDirectoryDoesNotHideOthers`, `unreadableCommitLogEndsTheComparison` and `countsUnreadableDirectories`.
7. Problem 7: `CommitLogDiskCheckTest.countsSharedDirectories` and `countsUnreadableDirectories` assert that the three counters exist after a run, at a rise of 0 when nothing was found, `registersTheCounters` that they exist after a run that failed early, and `offDoesNothing` that they do not exist without a run. `CommitLogDiskCheckDocsTest.exactNamesAreDocumented` checks each exact name on the page.
8. Problem 8: `DataResurrectionCheckTest`, unchanged, and `CommitLogDiskCheckStartTest.defaultNodeLogsNothingNew` start instances through the hook line and fail at instance start if the fork class is shared between instances.

## Planned file list

```
src/java/org/apache/cassandra/service/StartupChecks.java stock
src/java/org/apache/cassandra/service/CassandraDaemon.java stock
src/java/org/chronitondb/startup/CommitLogDiskCheck.java new
test/unit/org/chronitondb/startup/CommitLogDiskCheckTest.java test
test/unit/org/chronitondb/startup/CommitLogDiskCheckConstructionTest.java test
test/unit/org/chronitondb/startup/CommitLogDiskCheckDocsTest.java test
test/distributed/org/chronitondb/startup/test/CommitLogDiskCheckStartTest.java test
docs/reference/commitlog-disk-check.md new
docs/delta/commit-log-disk-check.md new
docs/delta/README.md edit
NEWS-chronitondb.txt new
```

The two stock files carry the hook points of section 3 and nothing else. `CommitLogDiskCheck` holds the whole feature: the switch test, the lookups, the comparison, the three warnings and the three counters. The coverage file next to this record is not in the list: it changes only with this record, through change control. No protected path and no library file is in the list.

The open pull requests were listed on 2026-11-15: the repository had none, so no open item shares a planned file. The merged design record of the release version feature plans `NEWS-chronitondb.txt` as a new file too, and edits `docs/delta/README.md`, which exists on the line. Its code pull request is not open yet. Section 15 item 10 says what changes if it merges first.

### Shared with open items

None.

### Waivers

1. Exit criterion 4 of [testing.md](../../process/testing.md#exit-criteria), the parity suite passes with every fork feature off. The parity suite does not exist on this line. In its place the stock suites of section 14 run unchanged with the switch at its default, off, and `CommitLogDiskCheckTest.offDoesNothing` and `CommitLogDiskCheckStartTest.defaultNodeLogsNothingNew` prove the off state. Waived because there is no parity suite to run. The maintainers approve the waiver with this record.
2. [testing.md, Scenarios](../../process/testing.md#scenarios) item 6: the designer writes the scenarios of a feature item in this pull request, tagged `@wip`. Waived because nothing that runs a scenario exists on this line: no `test/bdd/` module, no shared step library and no Cucumber runner, whose library is a new dependency that only its own update item adds. A scenario written now could not fail before the code and pass after it, and the gate could not run it. Every requirement is proven instead by a JUnit test named in `ac-coverage.md`, which exit criterion 1 accepts. The scenarios of this feature are section 15 item 9. The maintainers approve the waiver with this record.
3. [branching-and-review.md, Feature switches and defaults](../../process/branching-and-review.md#feature-switches-and-defaults) item 1: every fork feature has a yaml setting and a nodetool toggle. The feature has the yaml setting and no nodetool toggle, by decision record 0005: the check has run before nodetool can reach the node, so a toggle could change nothing.

## Requirement quality checklist (ISO/IEC/IEEE 29148)

Each of REQ-CLD-001 to REQ-CLD-020 was checked against the seven qualities before this record went to review:

1. **Necessary:** each traces to an acceptance criterion of the issue, a problem named in Where problems could occur, or a decision record. REQ-CLD-010 and REQ-CLD-011 also answer the observability line of quality-requirements.md.
2. **Unambiguous:** each names an exact text, an exact entry, an exact counter or an exact count, and the fixed terms are defined in New terms. No "fast" or "large" appears.
3. **Singular:** one key word and one EARS shape each. The three counters have their own ids, REQ-CLD-010 and REQ-CLD-011, the unreadable case is REQ-CLD-007 for the line, REQ-CLD-008 for the rest of the comparison and REQ-CLD-009 for the commit log directory, and the two files of the rollback sentence are REQ-CLD-014 and REQ-CLD-015.
4. **Verifiable:** each has one row in `ac-coverage.md` naming its test.
5. **Feasible:** each mechanism is cited by symbol, file and line in sections 3 and 4, or is the new code of the Planned file list.
6. **Consistent:** REQ-CLD-001 and REQ-CLD-003 split the cases with the switch on, REQ-CLD-004 covers the switch off, REQ-CLD-006 to REQ-CLD-009, REQ-CLD-017 and REQ-CLD-019 cover an `Exception` in a run, and none contradicts a decision record or a stock behaviour rule.
7. **Traceable:** each has an id, a source and exactly one coverage row.
