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

# Delta: Apache's pull request template removed

| Field | Value |
|---|---|
| Title | Apache's pull request template removed |
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
| Description | Apache's `.github/pull_request_template.md` is deleted, so pull requests use the Chroniton Labs template. |
| Origin | ChronitonDB. |
| Bug | none |
| Bug-ChronitonDB | none |
| Forwarded | Not needed. Apache's template serves Apache's own contribution process. |
| Added | 2026-10-27 |
| Last-Update | 2026-11-15 |
| Pull requests | `chronitondb-5.0`: [#30](https://github.com/chronitonlabs/chronitondb/pull/30), commit `abfb7b6487`. `chronitondb-6.0`: [#31](https://github.com/chronitonlabs/chronitondb/pull/31), commit `04abcb155c`. |

## What

Apache Cassandra's pull request template, `.github/pull_request_template.md`, is deleted. GitHub then fills a new pull request with the template of the organisation, from `chronitonlabs/.github`, which it uses only when a repository has none of its own.

## Why

Apache's template asks for a `CASSANDRA` JIRA ticket and Apache's review steps. ChronitonDB pull requests follow this repository's process, which the Chroniton Labs template asks for: what and why, how it was tested, other branches and the contributor agreement.

## Area

GitHub: `.github/pull_request_template.md`, deleted.

## Lines

`chronitondb-5.0` and `chronitondb-6.0`.
