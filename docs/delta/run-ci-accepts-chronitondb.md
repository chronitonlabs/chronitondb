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

# Delta: run-ci accepts this repository

| Field | Value |
|---|---|
| Title | run-ci accepts this repository |
| Document type | Record (ISO/IEC/IEEE 15289) |
| Status | Current |
| Version | 1 |
| Author | The maintainers |
| Approver | The maintainer who merges the pull request |
| References | Commits `1fc1183e4c` (`chronitondb-5.0`) and `d2b5abc401` (`chronitondb-6.0`). |

Change history: the git history of this file.

## What

The repository check in `.build/run-ci` accepts the `chronitonlabs/chronitondb` repository as well as forks of `apache/cassandra`. A test in `.build/run-ci.d/run-ci-test.py` covers it.

## Why

Without it, `run-ci` and the Build Scripts workflow refuse this repository.

## Area

Build scripts: `.build/run-ci` and `.build/run-ci.d/run-ci-test.py`.

## Lines

`chronitondb-5.0` and `chronitondb-6.0`.

## Upstream status

Ours only. The change names this repository.

## Date

2026-10-30
