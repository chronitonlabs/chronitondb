---
title: Commit log disk check
description: The startup check that warns when the commit log directory is on the same file system as a data directory, its switch, its warnings and its counters.
---
<!--
Copyright 2026 AxonOps Limited

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

SPDX-License-Identifier: Apache-2.0
-->

# Commit log disk check

Skeleton of the reference page `docs/reference/commitlog-disk-check.md`. The developer fills each placeholder in angle brackets and moves the file to that path in the code pull request. The page is a reference page: facts only, no steps, no background.

A ChronitonDB™ node can warn at startup when its commit log directory is on the same file system as one of its data directories. The check is off by default. Apache Cassandra® has no such check.

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in BCP 14 [RFC 2119] [RFC 8174] when, and only when, they appear in all capitals, as shown here.

## Setting

| Entry under `startup_checks` | Key | Type | Default | Change at runtime |
|---|---|---|---|---|
| `check_commitlog_shared_disk` | `enabled` | boolean | `false` | none, the value is read at start only |

```
startup_checks:
  check_commitlog_shared_disk:
    enabled: true
```

Any value but `true` leaves the check off. Other keys in the entry are not read.

## What the check compares

With the check on, the node compares, once at each start and after its other startup checks, the file system of `commitlog_directory` with the file system of each entry of `data_file_directories` and of `local_system_data_file_directory` when it is set. Symbolic links are followed. The check tells a file system by the device id the operating system reports for it, so one file system mounted at two places, as two bind mounts or two container volumes of one host file system are, is found. The node starts whatever the check finds.

## Warnings

When one or more data directories are on the commit log directory's file system, the node logs one line at WARN:

```
The commit log directory <commit log directory> is on the same file system as the data directories [<data directory>, <data directory>]. One failure of that file system loses the commit log and the data together, and on spinning disks commit log writes compete with reads, flushes and compaction. Put commitlog_directory on a file system of its own. This warning comes from the startup check check_commitlog_shared_disk.
```

When the file system of a directory cannot be read, the node logs one line at WARN for that directory, with the cause, leaves it out and compares the others:

```
The startup check check_commitlog_shared_disk could not read the file system of <directory> and left that directory out.
```

A start that finds nothing logs nothing.

## Metrics

Both counters exist only on a node that ran the check. A node with the check off has neither.

| Metric | Kind | What it counts |
|---|---|---|
| `org.chronitondb.metrics:type=CommitLogDiskCheck,name=SharedDataDirectories` | counter | the data directories found on the commit log directory's file system at this start |
| `org.chronitondb.metrics:type=CommitLogDiskCheck,name=UnreadableDirectories` | counter | the directories whose file system could not be read at this start |

<An alert on `SharedDataDirectories` above 0 finds a node that logged the warning.>

## Failure behaviour

| Case | What happens |
|---|---|
| the check is off | nothing is compared, logged or counted |
| the file system of the commit log directory cannot be read | one WARN line for it, nothing is compared, the node starts |
| the file system of a data directory cannot be read | one WARN line for it, the other data directories are compared, the node starts |

Timeouts, coordinator failure, missing replicas, limits and indexes that are not built do not apply: no request reaches the check.

## Known limitations

Two file systems on one physical device get no warning, for example two partitions of one disk or two logical volumes of one volume group. The check compares file systems, not devices.

The hints, saved caches and CDC directories are not compared.

The value is read at start only. A change needs a restart of the node.

## Rollback to Apache Cassandra

Before a node runs an Apache Cassandra binary, or a ChronitonDB build older than this feature, remove `check_commitlog_shared_disk` from its `cassandra.yaml`. <One sentence on what such a binary does with the entry, once section 15 item 7 of the design record is settled.>
