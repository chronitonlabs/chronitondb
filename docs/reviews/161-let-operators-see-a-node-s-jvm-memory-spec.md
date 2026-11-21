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

# Review record: feature spec of #161 Let operators see a node's JVM memory pools from CQL

| Field | Value |
|---|---|
| Title | Review record: feature spec of #161 Let operators see a node's JVM memory pools from CQL |
| Document type | Record (ISO/IEC/IEEE 15289) |
| Status | Open |
| Work product | Feature spec: `docs/design/JVMEM-jvm-memory-pools-view/feature-spec.md` |
| Pull request | #162 |
| Version reviewed | `f83b59022b` |
| Review type | Technical review (ISO/IEC 20246) |
| Reviewer | The project's review App |
| Author | Architect: chronitondb-agent |
| Decision maker | The maintainer who merges the pull request |
| References | Issue #161. The feature spec `docs/design/JVMEM-jvm-memory-pools-view/feature-spec.md` and its decision records `DEC-JVMEM-0001` to `DEC-JVMEM-0010` under `docs/design/JVMEM-jvm-memory-pools-view/decisions/`. |

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
| 1 | 2026-11-21 | `f83b59022b` | The whole change | Changes requested | 0 | 2 | 7 | 2 |

## 2. Anomaly list

One row per finding, in the reviewer's order. The id is `R<round>-<number>`. A finding raised again in a later round gets a new id and names the earlier one. The source says which checklist raised the finding, or that the security engineer's review did. On Critical risk work the security engineer's findings reach the record only through the reviewer, and stand here as rows like any other.

| Id | Location | Description | Source | Classification | Disposition |
|---|---|---|---|---|---|
| R1-1 | Item 3 of `Decision outcome`, `docs/design/JVMEM-jvm-memory-pools-view/decisions/DEC-JVMEM-0001-jvm-memory-pools-view-has-no-switch.md:67` at `f83b59022b` | The record chooses no hold back and does not say whether that departs from PRINCIPLE-003 and the edge of PRINCIPLE-089. Section 11 leaves the point to a design record, which cannot settle it. | compatibility | Minor | Open: the maintainers decide whether the record states an exception to PRINCIPLE-003 and PRINCIPLE-089 or a reading that they do not apply to a virtual table. |
| R1-2 | Case 2 of `2.2 Building blocks`, `docs/design/JVMEM-jvm-memory-pools-view/feature-spec.md:139` at `f83b59022b` | A plain aggregate with no page size is one read with no limit. The 10000 rows hold for `GROUP BY` only. Fact 17 and DEC-JVMEM-0008 carry the same statement. | correctness | Major | Fixed in `9dc090163b` |
| R1-3 | Item 4 of `2.5 Cross cutting concepts`, `docs/design/JVMEM-jvm-memory-pools-view/feature-spec.md:187` at `f83b59022b` | Three behaviours are stated inexactly: the DEBUG line holds for subnets, the heap histogram property changes the handling of an out of memory error, and a JVM can make a call throw. DEC-JVMEM-0010 carries the same statements. | docs | Major | Fixed in `f48f3be590` |
| R1-4 | Item 4 of `2.5 Cross cutting concepts`, `docs/design/JVMEM-jvm-memory-pools-view/feature-spec.md:187` at `f83b59022b` | The text says one or two ERROR lines. Each log call is given the exception, so each entry carries a stack trace. | correctness | Minor | Fixed in `041f3e6b7b` |
| R1-5 | The Touches row of `Feature spec: JVM memory pools view in CQL`, `docs/design/JVMEM-jvm-memory-pools-view/feature-spec.md:33` at `f83b59022b` | Needs verification: the reads of a statement with `IN` grow with the names listed, which may be a request path under classification.md. | correctness | Minor | Open: the maintainers decide whether the Touches row names a request path. |
| R1-6 | Item 1 of `7.4 Rollback path`, `docs/design/JVMEM-jvm-memory-pools-view/feature-spec.md:323` at `f83b59022b` | The pointer to item 2 of the list below reaches "Nothing else is removed". It means the second of the four places where a grant row is read. | correctness | Minor | Fixed in `6419c3d0d2` |
| R1-7 | Facts 14 and 17 of `12. Prior art`, `docs/design/JVMEM-jvm-memory-pools-view/feature-spec.md:413` at `f83b59022b`, and line 416 | `Config.java:876` and `SelectStatement.java:773` in the Apache Cassandra columns name no symbol. | correctness | Minor | Fixed in `c0d4940222` and `9dc090163b` |
| R1-8 | Item 3 of the context and one consequence, `Context and problem statement`, `docs/design/JVMEM-jvm-memory-pools-view/decisions/DEC-JVMEM-0005-type-column-shows-heap-and-non-heap-as-jmx-does.md:46` at `f83b59022b` | "Shown by no surface of the JVM" and "unlike most text values" name no code that was read. | docs | Minor | Fixed in `5371654e96` |
| R1-9 | The pull request body, Open points | Two lines tell how the work went and not what stands open. The open points are to be stated as facts. | docs | Minor | Fixed in the pull request body |
| R1-10 | Item 4 of `2.5 Cross cutting concepts`, `docs/design/JVMEM-jvm-memory-pools-view/feature-spec.md:187` at `f83b59022b` | One list item of about 3,200 characters. It reads better split into answered, logged and not covered. | docs | Nit | Fixed in `0d4cfe5243` |
| R1-11 | `ThreadPoolsTable.ThreadPoolsTable`, `docs/design/JVMEM-jvm-memory-pools-view/decisions/DEC-JVMEM-0004-view-is-named-jvm-memory-pools.md:57` at `f83b59022b` | The citation names line 40, the header of the constructor. The key column is set at line 45. | docs | Nit | Fixed in `7d0ebe2eff` |

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
