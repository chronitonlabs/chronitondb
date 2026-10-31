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
| Version | 1 |
| Author | The maintainers |
| Approver | The maintainer who merges the pull request |
| References | Pull requests #39 (`chronitondb-5.0`, commit `fb50ef9a74`) and #40 (`chronitondb-6.0`, commit `7306c3f56e`). |

Change history: the git history of this file.

## What

Every GitHub Action used in Apache's own workflows is pinned to a full commit hash, with its version tag in a comment.

## Why

A tag can be moved to other code. A commit hash cannot. Pinning keeps the workflows from running code nobody reviewed.

## Area

Continuous integration: `.github/workflows/build-scripts.yaml`, `.github/workflows/code-check.yaml` and `.github/workflows/jenkins-check.yaml`.

## Lines

`chronitondb-5.0` and `chronitondb-6.0`.

## Upstream status

Ours only. The maintainers may decide later to offer it to Apache Cassandra.

## Date

2026-10-30
