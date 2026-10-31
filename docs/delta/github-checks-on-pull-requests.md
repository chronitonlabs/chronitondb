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
| Version | 1 |
| Author | The maintainers |
| Approver | The maintainer who merges the pull request |
| References | Pull requests #47, #50 and #51 (`chronitondb-5.0`, commits `47c549d102`, `757e5bba84`, `11a4cd80c8`) and #48 and #52 (`chronitondb-6.0`, commits `9c9cb0b00b`, `6363396f38`). |

Change history: the git history of this file.

## What

Apache's Ant Check and Build Scripts workflows run on every pull request to a `chronitondb-*` line and on pushes to the lines, not on every branch push. The Ant Check job is named `ant-check` on both lines. Build Scripts keeps its path filter.

## Why

A check that runs only on branch pushes gives no result on a pull request from a fork, so it cannot be a required check. Running Ant Check on every pull request lets the lines require it. The one job name lets one rule set require it on both lines.

## Area

Continuous integration: `.github/workflows/code-check.yaml` and `.github/workflows/build-scripts.yaml`.

## Lines

`chronitondb-5.0` and `chronitondb-6.0`.

## Upstream status

Ours only. The triggers and job name fit this repository's branch names and required checks.

## Date

2026-10-31
