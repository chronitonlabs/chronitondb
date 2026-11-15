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
| References | Issue #112. Line `chronitondb-sandbox`, read at commit `8d744bb0ac`. Apache base commit `76550e931481e965ae3283d8cf4a59c320d74c55` (Apache `cassandra-5.0`). No feature spec and no plan: the one-item path. Process pages [branching-and-review.md](../../process/branching-and-review.md#feature-switches-and-defaults) and [quality-requirements.md](../../process/quality-requirements.md). Decision record 0001. |
| Risk | Normal: the issue's label. Open: the worst Bug Category is named when the maintainers have answered the three open points below. |
| Size | Low Hanging Fruit: one fork class for the check, one or two small edits to stock files, no dependency on other work. |
| Reach | One area: the startup checks of one node, in `org.apache.cassandra.service` and one new package under `org.chronitondb`. |
| Touches | public interface (configuration), stock behaviour (the start log of a node), new feature or switch. Open: the list is final when the maintainers have answered the three open points below. |

Change history: the git history of this file.

Location: `docs/design/CLD-commitlog-disk-check/`, the directory of the fork feature with the key `CLD`, which this record proposes and the merge of its pull request reserves ([additive.md, Feature keys and requirement ids](../../process/additive.md#feature-keys-and-requirement-ids), item 2). Every section is filled, or carries a waiver with its reason.

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in BCP 14 (RFC 2119, RFC 8174) when, and only when, they appear in all capitals, as shown here.

The Risk, Size and Reach rows are the item's class, as [classification.md](../../process/classification.md) defines it, and match the issue's `risk:normal`, `size:low-hanging-fruit` and `reach:one-area` labels. The issue also carries `kind:additive`, so the item is a fork feature small enough for one item and takes the one-item path of [maintenance.md](../../process/maintenance.md#the-one-item-path) with a feature key: this directory, the ids `REQ-CLD-nnn`, and the feature class stated in [section 3](#3-stock-behaviour-preservation).

**This record is not finished.** Three points wait for the maintainers' answer, and each changes what is built. Sections 1 and 4 are written. Every other section says `Open` until the answers are in.

1. **The default.** A new warning in the start log changes what a stock node logs, so the switch rules make the feature off by default. Whether it stays off by default, or becomes a second exception that is on by default.
2. **The switch.** Whether the check is switched on under the stock `startup_checks` block of `cassandra.yaml`, with no nodetool command, as every stock startup check is, or with a yaml key of its own and a pair of nodetool commands.
3. **What "shares a disk" means.** Whether the check compares file systems only, as the issue's text says, or also the physical device under two file systems.

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

Stock Apache Cassandra advises against it only in a comment of `conf/cassandra.yaml`: "when running on magnetic HDD, this should be a separate spindle than the data directories" (`conf/cassandra.yaml:405` to `406` at `8d744bb0ac`). The node itself checks one thing: `DatabaseDescriptor.applySimpleConfig` refuses to start when `commitlog_directory` is the same path as a data directory, with `commitlog_directory must not be the same as any data_file_directories` (`DatabaseDescriptor.java:706` to `707` at `8d744bb0ac`). Two different paths on one file system pass without a word.

That is also the layout of every node that sets neither directory. `DatabaseDescriptor.applySimpleConfig` puts the commit log in `<storagedir>/commitlog` (`DatabaseDescriptor.java:624` to `627` at `8d744bb0ac`) and the data in `<storagedir>/data` (`DatabaseDescriptor.java:693` to `696` at `8d744bb0ac`), and `bin/cassandra.in.sh` sets the storage directory to `$CASSANDRA_HOME/data` (`bin/cassandra.in.sh:48` at `8d744bb0ac`). So a check that is on by default would warn on every node that runs the default layout, which includes every development install and every test node.

Acceptance criteria, from the issue:

1. The node logs a clear warning at startup when the commit log directory is on the same file system as any data directory.
2. The node still starts as it does today.

### Requirements

Open: the requirements are written when the maintainers have answered the three open points above, because each answer changes them.

## 2. Decisions implemented

Open: written when the maintainers have answered the three open points at the top of this record.

## 3. Stock behaviour preservation

Open: written when the maintainers have answered the three open points at the top of this record.

### Stock hook points

Open: written when the maintainers have answered the three open points at the top of this record.

## 4. Prior art reviewed

Stock Apache Cassandra, read on this line at commit `8d744bb0ac`:

1. `StartupChecks.verify` runs every registered `StartupCheck` once, before the node changes any local state (`StartupChecks.java:176` to `192` at `8d744bb0ac`). `CassandraDaemon.setup` calls it through `CassandraDaemon.runStartupChecks` (`CassandraDaemon.java:258` and `457` to `466` at `8d744bb0ac`). A check that throws `StartupException` stops the node. A check that only logs lets it start.
2. Stock checks that only warn exist already. `StartupChecks.checkReadAheadKbSetting` finds the file store of each data directory with `Files.getFileStore` and logs a WARN when the device's read ahead is high (`StartupChecks.java:433` to `511` at `8d744bb0ac`). `StartupChecks.checkMaxMapCount` logs a WARN for a low `vm.max_map_count` (`StartupChecks.java:513` to `559` at `8d744bb0ac`). Neither stops the node. The new check has the same shape.
3. `StartupChecks.checkDataDirs` already reads the data directories, the commit log directory, the saved caches directory and the hints directory, and checks that each exists and is writable (`StartupChecks.java:561` to `594` at `8d744bb0ac`). It does not compare them.
4. A check is added to the daemon with `StartupChecks.withTest` (`StartupChecks.java:164` to `168` at `8d744bb0ac`). The `CassandraDaemon` constructor adds `FileSystemOwnershipCheck` that way (`CassandraDaemon.java:220` at `8d744bb0ac`). One more `withTest` call on that line is the hook a fork check needs.
5. A stock check that an operator can configure has a constant in the enum `StartupChecks.StartupCheckType` (`StartupChecks.java:106` to `125` at `8d744bb0ac`) and is set under `startup_checks` in `cassandra.yaml`, by that constant's name, with the key `enabled` (`conf/cassandra.yaml:2283` to `2303` at `8d744bb0ac`). `Config.startup_checks` is a map keyed by that enum (`Config.java:960` at `8d744bb0ac`). `StartupChecksOptions.apply` gives every constant an `enabled` value: `false` for a constant declared disabled by default, as `check_filesystem_ownership` and `check_data_resurrection` are, and `true` for the others (`StartupChecksOptions.java:81` to `96` at `8d744bb0ac`). No stock startup check has a nodetool command.
6. Stock code decides that two paths are on the same file system by comparing their `FileStore` objects with `equals`: `Directories.getWriteableLocationToLoadFile` (`Directories.java:377` to `391` at `8d744bb0ac`). The new check can use the same comparison.
7. The in-JVM distributed test framework runs the startup checks of every instance, through `CassandraDaemon.getInstanceForTesting().runStartupChecks()` (`test/distributed/org/apache/cassandra/distributed/impl/Instance.java:628` at `8d744bb0ac`). Every instance of such a test keeps its commit log and its data on one file system.
8. Apache's yaml loader refuses a key it does not know: `YamlConfigurationLoader` throws `Invalid yaml. Please remove properties ... from your cassandra.yaml` (`YamlConfigurationLoader.java:423` at `8d744bb0ac`). So a `cassandra.yaml` that names a new key, at the top level or under `startup_checks`, does not load on an Apache Cassandra binary.

Apache `cassandra-6.0` and trunk, read from `apache/cassandra` at commit `2249e37b51` (trunk) and `84bca651ef` (`cassandra-6.0`):

1. Commit `585f89bb42`, "Support custom StartupCheck implementations via SPI", for CASSANDRA-21093, replaced the enum with a name. `StartupCheck.name` returns the name a check has under `startup_checks` in `cassandra.yaml`, `StartupCheck.isConfigurable` and `StartupCheck.isDisabledByDefault` say whether an operator can set it and whether it runs when the yaml does not name it (`StartupCheck.java:44`, `63` and `76` at `2249e37b51`). `StartupChecks.withServiceLoaderTests` loads every `StartupCheck` a jar on the classpath declares through `java.util.ServiceLoader` (`StartupChecks.java:164` to `207` at `2249e37b51`). Both branches carry it.
2. So on the 6.0 line a check of our own needs no edit to a stock file: it is a class under `org.chronitondb` with a service entry, named and switched under `startup_checks`. A check that is configured under `startup_checks` on this line ports to 6.0 with the same yaml.
3. Neither branch has a check that compares the commit log's file system with the data directories'. The default checks on trunk are listed at `StartupChecks.java:123` to `141` at `2249e37b51`.

Apache JIRA and the dev list were not read for this record. The JIRA search this run tried was refused by the maintainers' automation on the worker, twice, so no ticket about a warning for a shared commit log disk is cited or ruled out here. The git history of the line names none: no commit subject under `src/java` mentions a shared disk, volume, device or file system. The next run of this record reads JIRA before the record goes to review.

Other systems, by behaviour: Open, with the answers.

No patents were searched or read.

These rules apply to every source:

1. Describe and cite behaviour, published designs, papers, public documentation and code under licences compatible with the Apache License 2.0.
2. Code or text under an incompatible licence, for example the Elastic License, SSPL, BUSL or a proprietary licence, MUST NOT be copied. The behaviour of such a system is taken only from its public documentation. Code under a compatible licence MAY be used only with credit. See [conventions.md](../../process/conventions.md#code-from-elsewhere).
3. Contributors working on the project's behalf MUST NOT search for or read patents for design work. Any patent concern goes to the maintainers.

## 5. Idiom and consistency

Open: written when the maintainers have answered the three open points at the top of this record.

## 6. Quality requirements

Open: written when the maintainers have answered the three open points at the top of this record.

## 7. Performance

Open: written when the maintainers have answered the three open points at the top of this record.

### Hot path statement

Open: written when the maintainers have answered the three open points at the top of this record.

### Expected cost

Open: written when the maintainers have answered the three open points at the top of this record.

### Isolation levers

Open: written when the maintainers have answered the three open points at the top of this record.

### Benchmarks that prove it

Open: written when the maintainers have answered the three open points at the top of this record.

### Regression threshold and gate

Open: written when the maintainers have answered the three open points at the top of this record.

### Stock guard

Open: written when the maintainers have answered the three open points at the top of this record.

### What was not measured

Open: written when the maintainers have answered the three open points at the top of this record.

## 8. Observability

Open: written when the maintainers have answered the three open points at the top of this record.

## 9. Compatibility

Open: written when the maintainers have answered the three open points at the top of this record.

## 10. Threat model and security

Open: written when the maintainers have answered the three open points at the top of this record.

## 11. Dependencies

Open: written when the maintainers have answered the three open points at the top of this record.

## 12. Compliance impact

Open: written when the maintainers have answered the three open points at the top of this record.

## 13. Documentation

Open: written when the maintainers have answered the three open points at the top of this record.

## 14. Testing

Open: written when the maintainers have answered the three open points at the top of this record.

### Tests for this change

Open: written when the maintainers have answered the three open points at the top of this record.

### Existing suites at risk

Open: written when the maintainers have answered the three open points at the top of this record.

### Stock suites run unchanged

Open: written when the maintainers have answered the three open points at the top of this record.

### Tracing test

Open: written when the maintainers have answered the three open points at the top of this record.

### Formats and configurations

Open: written when the maintainers have answered the three open points at the top of this record.

## 15. Not covered and follow-ups

Open: written when the maintainers have answered the three open points at the top of this record.

## New terms

Open: written when the maintainers have answered the three open points at the top of this record.

## Where problems could occur

Open: written when the maintainers have answered the three open points at the top of this record.

### Test plan

Open: written when the maintainers have answered the three open points at the top of this record.

## Planned file list

Open: written when the maintainers have answered the three open points at the top of this record.

### Shared with open items

Open: written when the maintainers have answered the three open points at the top of this record.

### Waivers

Open: written when the maintainers have answered the three open points at the top of this record.

## Requirement quality checklist (ISO/IEC/IEEE 29148)

Open: written when the maintainers have answered the three open points at the top of this record.
