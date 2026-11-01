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

# Delta: run-ci routes 6.0 versions on the 5.0 line

| Field | Value |
|---|---|
| Title | run-ci routes 6.0 versions on the 5.0 line |
| Document type | Record (ISO/IEC/IEEE 15289) |
| Status | Current |
| Version | 2 |
| Author | The maintainers |
| Approver | The maintainer who merges the pull request |
| References | The Origin, Bug, Bug-ChronitonDB and Pull requests fields below. |

Change history: the git history of this file.

## Header

The fields follow Debian's [DEP-3 patch header convention](https://dep-team.pages.debian.net/deps/dep3/). See [the delta register](README.md#fields).

| Field | Value |
|---|---|
| Description | The `.build/run-ci` part of an Apache change that sends 6.0 versions to the `cassandra-6.0` job. |
| Origin | Backport of Apache commit [`3f1593064c`](https://github.com/apache/cassandra/commit/3f1593064cc89f3884e982dd74cb41b9d825bc1f). Only the `.build/run-ci` part is taken. |
| Bug | [CASSANDRA-21319](https://issues.apache.org/jira/browse/CASSANDRA-21319) |
| Bug-ChronitonDB | none |
| Forwarded | Not needed. The change is Apache's own, on its 6.0 branch but not on `cassandra-5.0`. We carry it until an Apache 5.0 release brings it. |
| Added | 2026-10-30 |
| Last-Update | 2026-10-31 |
| Pull requests | `chronitondb-5.0`: [#37](https://github.com/chronitonlabs/chronitondb/pull/37), commit `b8c7408a5f`. |

## What

The `.build/run-ci` part of an Apache change: versions of 6.0 are sent to the `cassandra-6.0` job. The other parts of that Apache change concern the 6.0 branch and were not taken.

## Why

The 5.0 line already carries Apache's `run-ci` test that expects this mapping, but not the mapping itself, so the Build Scripts workflow failed on that test.

## Area

Build scripts: `.build/run-ci`.

## Lines

`chronitondb-5.0`. The 6.0 line has it from Apache.
