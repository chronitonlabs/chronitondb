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

# Delta: Import order check suppressed for ChronitonDB code

| Field | Value |
|---|---|
| Title | Import order check suppressed for ChronitonDB code |
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
| Description | Apache's checkstyle suppressions skip the import order check for ChronitonDB code. |
| Origin | ChronitonDB. |
| Bug | none |
| Bug-ChronitonDB | none |
| Forwarded | Not needed. It applies to ChronitonDB code only. |
| Added | 2026-10-30 |
| Last-Update | 2026-11-04 |
| Pull requests | `chronitondb-6.0`: [#36](https://github.com/chronitonlabs/chronitondb/pull/36), commit `bd0a4f3a85`. |

## What

Apache's checkstyle suppressions skip the `ImportOrder` check for files under `org/chronitondb`. The suppression carries a comment saying why.

## Why

ChronitonDB code follows Google Java Style, whose import order differs from Apache Cassandra's. The 6.0 line enforces Apache's import order. The 5.0 line has no import order rule, so it needs no suppression.

## Area

Build: `.build/checkstyle_suppressions.xml`.

## Lines

`chronitondb-6.0`.
