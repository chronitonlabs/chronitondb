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

# Delta: Commit log disk check

| Field | Value |
|---|---|
| Title | Commit log disk check |
| Document type | Record (ISO/IEC/IEEE 15289) |
| Status | Current |
| Version | 1 |
| Author | The maintainers |
| Approver | The maintainer who merges the pull request |
| References | The Origin, Bug, Bug-ChronitonDB and Pull requests fields below. |

Change history: the git history of this file.

## Contents

- [Header](#header)
- [What](#what)
- [Why](#why)
- [Area](#area)
- [Lines](#lines)

## Header

The fields follow Debian's [DEP-3 patch header convention](https://dep-team.pages.debian.net/deps/dep3/). See [the delta register](README.md#fields).

| Field | Value |
|---|---|
| Description | A startup check, off by default, warns when the commit log directory is on the same file system as a data directory. |
| Origin | ChronitonDB. |
| Bug | none |
| Bug-ChronitonDB | [#112](https://github.com/chronitonlabs/chronitondb/issues/112) |
| Forwarded | Not needed. It is a ChronitonDB feature, and features go to Apache Cassandra only when the maintainers decide. |
| Added | 2026-11-15 |
| Last-Update | 2026-11-15 |
| Pull requests | `chronitondb-sandbox`: the pull request for #112, not merged yet. |

## What

Two stock files change. `StartupChecks.StartupCheckType` gains one constant, `check_commitlog_shared_disk`, declared disabled by default, as the last constant of the enum. The `CassandraDaemon` constructor registers one more startup check, `org.chronitondb.startup.CommitLogDiskCheck`, after `FileSystemOwnershipCheck`, with one import for it.

With the entry `check_commitlog_shared_disk` set to `enabled: true` under `startup_checks` in `cassandra.yaml`, the start log can hold up to three new WARN lines, and the metrics registry holds three counters of the type `CommitLogDiskCheck` in the group `org.chronitondb.metrics`. With the entry absent, the default, the check returns at its first statement: it logs nothing, counts nothing and reads no directory. Every node still holds the new constant, its options map and the registered check.

## Why

A commit log on the same file system as the data loses both in one failure, and on spinning disks its writes compete with reads, flushes and compaction. Stock Apache Cassandra refuses only the case where the two paths are equal. A name under `startup_checks` must be a constant of the enum for a `cassandra.yaml` that names it to load, and a check must be registered with the daemon to run, so the feature needs both stock edits.

## Area

Startup checks: `src/java/org/apache/cassandra/service/StartupChecks.java` and `src/java/org/apache/cassandra/service/CassandraDaemon.java`, with the check in `src/java/org/chronitondb/startup/`. The page is [docs/reference/commitlog-disk-check.md](../reference/commitlog-disk-check.md).

## Lines

`chronitondb-sandbox`.
