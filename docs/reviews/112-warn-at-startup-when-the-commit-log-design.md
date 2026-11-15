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

# Review record: design record of #112 Warn at startup when the commit log shares a disk with the data directories

| Field | Value |
|---|---|
| Title | Review record: design record of #112 Warn at startup when the commit log shares a disk with the data directories |
| Document type | Record (ISO/IEC/IEEE 15289) |
| Status | Open |
| Work product | Design record: `docs/design/CLD-commitlog-disk-check/design-record.md` |
| Pull request | #116 |
| Version reviewed | Not reviewed yet |
| Review type | Technical review (ISO/IEC 20246) |
| Reviewer | chronitondb-agent |
| Author | Designer: chronitondb-agent |
| Decision maker | The maintainer who merges the pull request |
| References | Issue #112. The design record `docs/design/CLD-commitlog-disk-check/design-record.md`, its coverage file `docs/design/CLD-commitlog-disk-check/ac-coverage.md`, the page skeleton `docs/design/CLD-commitlog-disk-check/page-commitlog-disk-check.md` and decision records 0004 to 0006 under `docs/decisions/`. |

Change history: the git history of this file.

Location: `docs/reviews/<work>.md`, the pull request's branch without `agent/` and without the line, `import/` read as `import-`. Process: [branching-and-review.md](../process/branching-and-review.md#the-review-record). Structure: the review record of ISO/IEC 20246 and the review report and anomaly list of IEEE 1028.

The author keeps this record current and commits it with the change: when the pull request opens, after each review round and after the last one. It states in the third person what each round found, what was done about each finding and what the maintainers decided.

## Contents

- [1. Rounds](#1-rounds)
- [2. Anomaly list](#2-anomaly-list)
- [3. Decisions](#3-decisions)
- [4. Limits](#4-limits)
- [5. Exit decision](#5-exit-decision)

## 1. Rounds

| Round | Date | Version reviewed | Scope | Verdict | Blockers | Majors | Minors | Nits |
|---|---|---|---|---|---|---|---|---|

## 2. Anomaly list

One row per finding, in the reviewer's order. The id is `R<round>-<number>`. A finding raised again in a later round gets a new id and names the earlier one.

| Id | Location | Description | Classification | Disposition |
|---|---|---|---|---|

1. **Fixed in `<hash>`**: the commit that fixes the finding. Several commits are joined with "and". A finding on the pull request's title or body is "Fixed in the pull request title" or "body".
2. **Accepted: `<reason>`**: the work product stays as it is, for the reason given. The reviewer judges the reason in the next round.
3. **Waived by `<the maintainers>`: `<reason>`**: the maintainers decided the finding needs no change, as "the maintainers" or "a maintainer, `<GitHub username>`".
4. **Open: `<what settles it>`**: no disposition yet, while the maintainers decide. A clean review leaves none open from an earlier round.

## 3. Decisions

No decisions.

## 4. Limits

None.

## 5. Exit decision

Open.
