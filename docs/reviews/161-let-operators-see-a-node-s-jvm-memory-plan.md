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

# Review record: plan and delivery plan of #161 Let operators see a node's JVM memory pools from CQL

| Field | Value |
|---|---|
| Title | Review record: plan and delivery plan of #161 Let operators see a node's JVM memory pools from CQL |
| Document type | Record (ISO/IEC/IEEE 15289) |
| Status | Open |
| Work product | Plan and delivery plan: `docs/design/JVMEM-jvm-memory-pools-view/plan.md` |
| Pull request | #166 |
| Version reviewed | Not reviewed yet |
| Review type | Technical review (ISO/IEC 20246) |
| Reviewer | The project's review App |
| Author | Architect: chronitondb-agent |
| Decision maker | The maintainer who merges the pull request |
| References | Issue #161. The feature spec `docs/design/JVMEM-jvm-memory-pools-view/feature-spec.md`, the plan `docs/design/JVMEM-jvm-memory-pools-view/plan.md` and the delivery plan `docs/design/JVMEM-jvm-memory-pools-view/delivery-plan.md`. |

A review record has no version. Its history is the commits of this file.

Location: `docs/reviews/<work>.md`, where `<work>` is the pull request's branch without its first part, `agent/` or a username, and without the line. An import branch keeps its first part, as `import-`. Process: [branching-and-review.md](../process/branching-and-review.md#the-review-record). Structure: the review record of ISO/IEC 20246 and the review report and anomaly list of IEEE 1028. The review record of a security fix is not committed to the branch that lands: it is kept in the private advisory and stays there after disclosure, see [security.md](../process/security.md#private-until-disclosure).

Only the project's own automation keeps this record: it is the committed record of the review of a pull request the automation wrote. An outside contributor writes none, and on such a pull request the verdict's own review comment for the round carries the findings, one row for each finding. The author keeps this record current and commits it with the change: when the pull request opens, after each review round and after the last one. It states in the third person what each round found, what was done about each finding and what the maintainers decided.

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

One row per finding, in the reviewer's order. The id is `R<round>-<number>`. A finding raised again in a later round gets a new id and names the earlier one. The source says which checklist raised the finding, or that the security engineer's review did. On Critical risk work the security engineer's findings reach the record only through the reviewer, and stand here as rows like any other.

| Id | Location | Description | Source | Classification | Disposition |
|---|---|---|---|---|---|

1. **Fixed in `<hash>`**: the commit that fixes the finding, a commit of the pull request's branch. Several commits are joined with "and". A finding on the pull request's title or body is "Fixed in the pull request title" or "body".
2. **Accepted: `<reason>`**: the work product stays as it is, for the reason given. The reviewer judges the reason in the next round.
3. **Waived by `<the maintainers>`: `<reason>`**: the maintainers decided the finding needs no change, as "the maintainers" or "a maintainer, `<GitHub username>`". A waiver counts only as a maintainer's line in the set form on the pull request, such as `Waived: R1-3`: see [branching-and-review.md](../process/branching-and-review.md#the-review-record), item 4. Until then the disposition is Open.
4. **Open: `<what settles it>`**: no disposition yet, while the maintainers decide. A clean review leaves none open from an earlier round.

## 3. Decisions

No decisions.

## 4. Limits

None.

## 5. Exit decision

Open.
