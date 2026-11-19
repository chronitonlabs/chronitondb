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
| Status | Dropped |
| Version | 5 |
| Author | The maintainers |
| Approver | The maintainer who merges the pull request |
| References | The Origin, Bug, Bug-ChronitonDB and Pull requests fields below. |

Revision history, one row for each version:

| Version | Date | Change | Decision record |
|---|---|---|---|
| 5 | 2026-11-19 | The suppression is removed and the entry is Dropped, since the project's own code follows Apache Cassandra's code style | None |

Full history in git: [commits of this file](https://github.com/chronitonlabs/chronitondb/commits/chronitondb-sandbox/docs/delta/checkstyle-import-order-suppression.md)

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
| Last-Update | 2026-11-19 |
| Pull requests | `chronitondb-6.0`: [#36](https://github.com/chronitonlabs/chronitondb/pull/36) and [#66](https://github.com/chronitonlabs/chronitondb/pull/66), commits `bd0a4f3a85` and `9f9b4f94b4`. The suppression is removed by [#147](https://github.com/chronitonlabs/chronitondb/pull/147), commit `60f73fcbc1`. |

## What

Apache's checkstyle suppressions skipped the `ImportOrder` check for files under `org/chronitondb`. Pull request [#147](https://github.com/chronitonlabs/chronitondb/pull/147), commit `60f73fcbc1`, removed the suppression.

## Why

The suppression was carried while ChronitonDB code followed another import order. ChronitonDB code now follows Apache Cassandra's code style on each line, its import order included, so the suppression is removed and this entry is Dropped.

## Area

Build: `.build/checkstyle_suppressions.xml`.

## Lines

`chronitondb-6.0`.
