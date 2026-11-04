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

# Delta: Apache workflow actions pinned to commits

| Field | Value |
|---|---|
| Title | Apache workflow actions pinned to commits |
| Document type | Record (ISO/IEC/IEEE 15289) |
| Status | Current |
| Version | 3 |
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
| Description | Every GitHub Action in Apache's own workflows is pinned to a commit hash. |
| Origin | ChronitonDB. |
| Bug | none |
| Bug-ChronitonDB | none |
| Forwarded | Not needed. The maintainers may decide later to offer it to Apache Cassandra. |
| Added | 2026-10-30 |
| Last-Update | 2026-11-04 |
| Pull requests | `chronitondb-5.0`: [#39](https://github.com/chronitonlabs/chronitondb/pull/39), commit `fb50ef9a74`. `chronitondb-6.0`: [#40](https://github.com/chronitonlabs/chronitondb/pull/40), commit `7306c3f56e`. |

## What

Every GitHub Action used in Apache's own workflows is pinned to a full commit hash, with its version tag in a comment.

## Why

A tag can be moved to other code. A commit hash cannot. Pinning keeps the workflows from running code nobody reviewed.

## Area

Continuous integration: `.github/workflows/build-scripts.yaml`, `.github/workflows/code-check.yaml` and `.github/workflows/jenkins-check.yaml`.

## Lines

`chronitondb-5.0` and `chronitondb-6.0`.
