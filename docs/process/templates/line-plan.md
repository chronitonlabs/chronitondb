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


# Line plan: {line}

| Field | Value |
|---|---|
| Title | ChronitonDB {line} line plan |
| Document type | Plan (ISO/IEC/IEEE 15289), line release plan |
| Status | Draft, Approved or Superseded |
| Version | {n} |
| Author | {GitHub username} |
| Approver | The maintainer who merges the pull request |
| References | {the line, its feature specs and delivery plans} |

Change history: the git history of this file.

Location: `docs/releases/<line>-plan.md`, one per line. It changes only by a pull request a maintainer merges. Process: [release.md](../release.md).

## Contents

- [1. First release](#1-first-release)
- [2. Feature freeze](#2-feature-freeze)
- [3. Support](#3-support)

## 1. First release

Planned first release date: {YYYY-MM-DD, or "not set"}

{What the first release is planned to ship, by feature and its delivery plan. Once the first release ships, its date and version, for example `5.0-chronitondb1`.}

## 2. Feature freeze

Feature freeze starts: {YYYY-MM-DD, 4 weeks before the planned first release date, or "not set"}

## 3. Support

LTS: {yes or no, as the maintainers designated the line}

{For an LTS line, its end date once its first release ships. For a standard line, its end date once the next line's first release ships. See [release.md](../release.md#support-lifetime).}
