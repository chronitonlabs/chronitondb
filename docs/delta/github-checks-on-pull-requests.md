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

# Delta: Apache GitHub checks run on pull requests to the lines

| Field | Value |
|---|---|
| Title | Apache GitHub checks run on pull requests to the lines |
| Document type | Record (ISO/IEC/IEEE 15289) |
| Status | Current |
| Version | 4 |
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
| Description | Apache's Ant Check and Build Scripts workflows run on pull requests to the lines. |
| Origin | ChronitonDB. |
| Bug | none |
| Bug-ChronitonDB | none |
| Forwarded | Not needed. The triggers and job name fit this repository's branch names and required checks. |
| Added | 2026-10-31 |
| Last-Update | 2026-11-15 |
| Pull requests | `chronitondb-5.0`: [#47](https://github.com/chronitonlabs/chronitondb/pull/47), [#50](https://github.com/chronitonlabs/chronitondb/pull/50), [#51](https://github.com/chronitonlabs/chronitondb/pull/51) and [#65](https://github.com/chronitonlabs/chronitondb/pull/65), commits `47c549d102`, `757e5bba84`, `11a4cd80c8` and `5cb388f9a6`. `chronitondb-6.0`: [#48](https://github.com/chronitonlabs/chronitondb/pull/48), [#52](https://github.com/chronitonlabs/chronitondb/pull/52) and [#66](https://github.com/chronitonlabs/chronitondb/pull/66), commits `9c9cb0b00b`, `6363396f38` and `9f9b4f94b4`. |

## What

Apache's Ant Check and Build Scripts workflows run on every pull request to a `chronitondb-*` line and on pushes to the lines, not on every branch push. The Ant Check job is named `ant-check` on both lines. Build Scripts keeps its path filter. A comment starting `ChronitonDB:` in each workflow says what changed. #65 and #66 reworded those comments only.

## Why

A check that runs only on branch pushes gives no result on a pull request from a fork, so it cannot be a required check. Running Ant Check on every pull request lets the lines require it. The one job name lets one rule set require it on both lines.

## Area

Continuous integration: `.github/workflows/code-check.yaml` and `.github/workflows/build-scripts.yaml`.

## Lines

`chronitondb-5.0` and `chronitondb-6.0`.
