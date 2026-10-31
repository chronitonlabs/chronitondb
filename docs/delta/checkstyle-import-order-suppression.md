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
| Version | 1 |
| Author | The maintainers |
| Approver | The maintainer who merges the pull request |
| References | Pull request #36 (`chronitondb-6.0`, commit `bd0a4f3a85`). |

Change history: the git history of this file.

## What

Apache's checkstyle suppressions skip the `ImportOrder` check for files under `org/chronitondb`. The suppression carries a comment saying why.

## Why

ChronitonDB code follows Google Java Style, whose import order differs from Apache Cassandra's. The 6.0 line enforces Apache's import order. The 5.0 line has no import order rule, so it needs no suppression.

## Area

Build: `.build/checkstyle_suppressions.xml`.

## Lines

`chronitondb-6.0`.

## Upstream status

Ours only. It applies to ChronitonDB code only.

## Date

2026-10-30
