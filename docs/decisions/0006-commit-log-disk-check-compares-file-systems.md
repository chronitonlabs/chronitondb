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

The issue asks for a warning when the commit log shares a disk with the data directories, and its text names the test: the commit log directory is on the same file system as any data directory. Two file systems can sit on one physical device, as two partitions of one disk do. The design had to know whether the check compares file systems only, or also the device under them.

## Considered options

1. Same file system only. The check warns when the commit log directory and a data directory are on one file system, as the operating system reports it. It needs no knowledge of volume managers or RAID. Two file systems on one physical device get no warning.
2. Also the same physical device, read from `/sys` on Linux. It catches two partitions of one disk. It is best effort: volume managers, RAID and cloud volumes can hide a shared device or show a false one, and other platforms behave as option 1.

## Decision outcome

Chosen option: "Same file system only", because the comparison is never a guess and it is what the issue asks for.

The commit log disk check MUST treat two directories as sharing a disk when, and only when, they are on the same file system. The check MUST NOT read the physical device under a file system. The device id the operating system reports for a file system names that file system, not the physical device under it, and the check MAY read it. The reference page MUST state that two file systems on one physical device get no warning.

### Consequences

- Good: the warning is never a guess.
- Bad: a commit log on its own partition or volume of the same physical disk as the data gets no warning.

## More information

The design record in `docs/design/CLD-commitlog-disk-check/` applies this decision in REQ-CLD-001 to REQ-CLD-003, in its New terms, and in the known limitations of section 13.
