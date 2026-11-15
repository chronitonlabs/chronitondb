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

# 0006. The commit log disk check compares file systems

| Field | Value |
|---|---|
| Document type | Record (ISO/IEC/IEEE 15289), MADR |
| Status | Accepted |
| Date | 2026-11-15 |
| Deciders | The maintainers |
| References | Issue #112, the design record in `docs/design/CLD-commitlog-disk-check/`, [branching-and-review.md, Feature switches and defaults](../process/branching-and-review.md#feature-switches-and-defaults) |

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in BCP 14 (RFC 2119, RFC 8174) when, and only when, they appear in all capitals, as shown here.

## Contents

- [Context and problem statement](#context-and-problem-statement)
- [Considered options](#considered-options)
- [Decision outcome](#decision-outcome)
  - [Consequences](#consequences)
- [More information](#more-information)

## Context and problem statement

The issue asks for a warning when the commit log shares a disk with the data directories, and its text names the test: the commit log directory is on the same file system as any data directory. The design had to know how the check tells that two directories are on the same file system, and how far it looks. Three layouts decide it. Two file systems can sit on one physical device, as two partitions of one disk do. One file system can be mounted at two places, as two container volumes of one host file system are. And a file system can report a device id of its own for each of its subvolumes. In this record a physical device is the whole disk, or the set of disks, under a partition or a volume.

## Considered options

1. The same device id. The check warns when the operating system reports the same device id for the commit log directory and for a data directory. One file system mounted at two places is found. The check needs no knowledge of volume managers or RAID. Two file systems on one physical device get no warning, and nor do two subvolumes of one file system that report a device id each.
2. Equal file stores, as stock code compares them in `Directories.getWriteableLocationToLoadFile` (`src/java/org/apache/cassandra/db/Directories.java:377` to `391` at `8d744bb0ac`). On the JDK read for the design record two file stores are equal only for paths under the same mount, so one file system mounted at two places gets no warning.
3. Option 1, and also the same physical device, read from `/sys` on Linux. It catches two partitions of one disk. It is best effort: volume managers, RAID and cloud volumes can hide a shared device or show a false one, and other platforms behave as option 1.
4. Option 1, and also the same source device of two mounts, on Linux. It catches subvolumes that report a device id each. It is best effort, its false warnings and misses are not known, and other platforms behave as option 1.

## Decision outcome

Chosen option: "The same device id", because the comparison is never a guess, and because it finds one file system mounted at two places, which the sentence of the issue covers.

The commit log disk check MUST treat two directories as sharing a disk when, and only when, the operating system reports the same device id for both. The check MUST NOT read the physical device under a file system. The check MUST NOT read the source device of a mount. The reference page MUST state that two file systems on one physical device get no warning. The reference page MUST state that two subvolumes of one file system get no warning when the file system reports a device id of its own for each subvolume.

### Consequences

- Good: the warning is never a guess.
- Good: a commit log and data on two mounts of one file system get the warning.
- Bad: a commit log on its own partition or volume of the same physical disk as the data gets no warning.
- Bad: a commit log and data on two subvolumes that report a device id each get no warning.

## More information

The design record in `docs/design/CLD-commitlog-disk-check/` applies this decision in REQ-CLD-001 to REQ-CLD-003, in its New terms, and in the known limitations of section 13. That the operating system reports one device id for two mounts of one file system was not run for the design record, which says so in its section 15 item 11.
