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
| Version reviewed | `d988ad69e1` |
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
| 1 | 2026-11-22 | `83664ea0f4` | The whole change | Changes requested | 0 | 1 | 13 | 3 |
| 2 | 2026-11-22 | `d988ad69e1` | The changes since round 1 | Changes requested | 0 | 1 | 7 | 0 |

## 2. Anomaly list

One row per finding, in the reviewer's order. The id is `R<round>-<number>`. A finding raised again in a later round gets a new id and names the earlier one. The source says which checklist raised the finding, or that the security engineer's review did. On Critical risk work the security engineer's findings reach the record only through the reviewer, and stand here as rows like any other.

| Id | Location | Description | Source | Classification | Disposition |
|---|---|---|---|---|---|
| R1-1 | Exit criterion 4 of `Milestone 1: The view`, `docs/design/JVMEM-jvm-memory-pools-view/delivery-plan.md:65` at `83664ea0f4`, and the paragraph after the fields of `Item 1: The view, its hook, its tests and its reference page`, `docs/design/JVMEM-jvm-memory-pools-view/plan.md:93` at `83664ea0f4` | DEC-JVMEM-0003 has two start tests run on every build of the feature. Exit criterion 4 checked one commit and no check of the line runs a test, so a view that stops a node start could sit on the line. | correctness, plan consistency | Major | Fixed in `f68dd74679` |
| R1-2 | Exit criterion 5 of `Milestone 1: The view`, `docs/design/JVMEM-jvm-memory-pools-view/delivery-plan.md:66` at `83664ea0f4` | The tests of Apache Cassandra named leave out its grant tests on `system_views` and its in-JVM distributed tests `VirtualTableFromInternodeTest` and `VirtualTableLogsTest`, though the view enters that handling. | compatibility | Minor | Fixed in `43a8121dc2` |
| R1-3 | Criterion 11 of `Item 2: End to end tests of the view on a cluster`, `docs/design/JVMEM-jvm-memory-pools-view/plan.md:123` at `83664ea0f4`, and criterion 11 of `Item 1: The view, its hook, its tests and its reference page`, `docs/design/JVMEM-jvm-memory-pools-view/plan.md:76` at `83664ea0f4` | No fixed list of the expected tables. A test that takes its names from the running keyspace passes when the hook drops a table of Apache Cassandra from `system_views`. | correctness | Minor | Fixed in `d2de8e393a` |
| R1-4 | Criterion 13 of `Item 2: End to end tests of the view on a cluster`, `docs/design/JVMEM-jvm-memory-pools-view/plan.md:125` at `83664ea0f4` | Both items send `GRANT` and `REVOKE` as a superuser only, so a check of the feature's own on another role passes every test. A role that is no superuser is needed, with `AUTHORIZE` and without it. | plan consistency | Minor | Fixed in `57f2f51ebe` |
| R1-5 | Criterion 15 of `Item 2: End to end tests of the view on a cluster`, `docs/design/JVMEM-jvm-memory-pools-view/plan.md:127` at `83664ea0f4`, the paragraph after the fields of `Item 2: End to end tests of the view on a cluster`, `docs/design/JVMEM-jvm-memory-pools-view/plan.md:141` at `83664ea0f4`, limit 2 and the row of FREQ-JVMEM-018 | The plan says criterion 15 cannot tell a view that wraps what it caught from one that passes it on, yet the traceability row names it as the validation of FREQ-JVMEM-018. | plan consistency | Minor | Fixed in `3652b0772a` |
| R1-6 | Limit 7 of `2. Validation items`, `docs/design/JVMEM-jvm-memory-pools-view/plan.md:155` at `83664ea0f4` | The reason given, that a statement through CQL does not show memory, does not hold for item 2, whose tests look inside a node. Criterion 6 misses a view that keeps each read's values and writes over them. | plan consistency | Minor | Fixed in `0a18f39bd6` |
| R1-7 | Criterion 22 of `Item 2: End to end tests of the view on a cluster`, `docs/design/JVMEM-jvm-memory-pools-view/plan.md:134` at `83664ea0f4` | For the first of the four places, section 7.4 of the feature spec states no outcome a test can assert. Problem 7 of its section 4.1 gives one. The criterion is to name the four outcomes. | plan consistency | Minor | Fixed in `e0e3457238` |
| R1-8 | Criterion 18 of `Item 1: The view, its hook, its tests and its reference page`, `docs/design/JVMEM-jvm-memory-pools-view/plan.md:83` at `83664ea0f4`, and the note on criterion 18 in `1. Items`, `docs/design/JVMEM-jvm-memory-pools-view/plan.md:102` at `83664ea0f4` | Where the place of criterion 15 is on the view class, the class and its static initialiser load before the place throws. The test then misses a static initialiser that calls the JVM. | plan consistency | Minor | Fixed in `7be2ff3bff` |
| R1-9 | Criterion 18 of `Item 1: The view, its hook, its tests and its reference page`, `docs/design/JVMEM-jvm-memory-pools-view/plan.md:83` at `83664ea0f4`, and criterion 9 of `Item 1: The view, its hook, its tests and its reference page`, `docs/design/JVMEM-jvm-memory-pools-view/plan.md:74` at `83664ea0f4` | Each criterion joins several requirements. Criterion 18 joins no setting read and no call to the JVM when built, proved in two ways. Criterion 9 joins FREQ-JVMEM-009, 010 and 017. | correctness | Minor | Fixed in `0f3ca7a151` |
| R1-10 | The rows of FREQ-JVMEM-002, 013 and 020 in `3. Traceability`, `docs/design/JVMEM-jvm-memory-pools-view/plan.md:163` at `83664ea0f4` | Rows cite criteria of item 2 whose tags name other requirements: criteria 15 and 17 in the row of 002, criterion 13 in the row of 013 and criterion 15 in the row of 020. | correctness | Minor | Fixed in `860a4439b8` |
| R1-11 | Exit criterion 5 of `Milestone 1: The view`, `docs/design/JVMEM-jvm-memory-pools-view/delivery-plan.md:66` at `83664ea0f4` | Exit criteria 2 and 3 name Java 17 and a test configuration. Exit criterion 5 names neither for the tests of Apache Cassandra. | correctness | Minor | Fixed in `2430928eb9` |
| R1-12 | Item 3 of the test environments in `6. Test plan`, `docs/design/JVMEM-jvm-memory-pools-view/delivery-plan.md:132` at `83664ea0f4`, and rows 2, 3 and 5 of the table of exit criteria | A run on the build machines reads as enough for the gate, but exit criterion 10 needs criteria 2, 3 and 5 run in continuous integration. | docs | Minor | Fixed in `f7990fd837` |
| R1-13 | Fact F of `6. Test plan`, `docs/design/JVMEM-jvm-memory-pools-view/delivery-plan.md:166` at `83664ea0f4`, and the note on criterion 19 in `1. Items`, `docs/design/JVMEM-jvm-memory-pools-view/plan.md:103` at `83664ea0f4` | The fact says a library outside the checkout decides the classes the nodes share. `AbstractCluster.getSharedClassPredicate` builds that test in the checkout, from classes marked `Shared` under `org.apache.cassandra` and the library's default filter. | reviewer, correctness | Minor | Fixed in `d705e34960` |
| R1-14 | Facts A, B, C, E, F and G of `6. Test plan`, `docs/design/JVMEM-jvm-memory-pools-view/delivery-plan.md:161` at `83664ea0f4` | Nine citations name their project, branch and commit only once, at the end of the cell, so a citation read alone has no tree. | reviewer | Minor | Fixed in `24d6810c6e` and `d705e34960` |
| R1-15 | Fact C of `6. Test plan`, `docs/design/JVMEM-jvm-memory-pools-view/delivery-plan.md:163` at `83664ea0f4` | The job `ant-check` is at line 15 of the workflow file. Line 28, which the fact cites, is its run step. | reviewer | Nit | Fixed in `1311ed368c` |
| R1-16 | Fact G of `6. Test plan`, `docs/design/JVMEM-jvm-memory-pools-view/delivery-plan.md:167` at `83664ea0f4` | `CoordinatorHelper.unsafeExecuteInternal` has two overloads, and the fact does not say which one it cites. It is the one that takes `Dispatcher.RequestTime`. | docs | Nit | Fixed in `0b650fda39` and `24d6810c6e` |
| R1-17 | Fact C of `6. Test plan`, `docs/design/JVMEM-jvm-memory-pools-view/delivery-plan.md:163` at `83664ea0f4` | The shape workflow runs `ant resolver-retrieve-build` a second time, at line 127, which the fact leaves out. | docs | Nit | Fixed in `a927ced5ff` |
| R2-1 | Entry 4 of "Where the two tests of DEC-JVMEM-0003 run" in `6. Test plan`, `docs/design/JVMEM-jvm-memory-pools-view/delivery-plan.md:155` at `d988ad69e1`, and the paragraph after the entries in `6. Test plan`, `docs/design/JVMEM-jvm-memory-pools-view/delivery-plan.md:157` at `d988ad69e1`. Follows R1-1 | DEC-JVMEM-0003, an approved record, has both start tests run on every build of the feature. The plan says no build after a merge of other work runs them, and neither names that departure nor routes it to change control. | correctness, docs, compatibility, plan consistency | Major | Open: the maintainers' decision, by change control, on whether item 3 of the outcome of DEC-JVMEM-0003 changes or the first part of continuous integration is merged before item 1. What the full run before an import holds is added in `8160884db7` |
| R2-2 | Exit criterion 4 of `Milestone 1: The view`, `docs/design/JVMEM-jvm-memory-pools-view/delivery-plan.md:65` at `d988ad69e1`, and criterion 26 of `Item 1: The view, its hook, its tests and its reference page`, `docs/design/JVMEM-jvm-memory-pools-view/plan.md:91` at `d988ad69e1` | Criterion 26 and entry 1 of section 6 ask for both tests only from the commit that adds them. A commit that adds the view to the hook before the tests is a build of the feature with neither test. | correctness, docs | Minor | Fixed in `de53145dc5` |
| R2-3 | Criterion 24 of `Item 2: End to end tests of the view on a cluster`, `docs/design/JVMEM-jvm-memory-pools-view/plan.md:145` at `d988ad69e1` | The criterion expects the same error as for a table of Apache Cassandra in `system_views`. `ClientState.ensurePermissionOnResourceChain` writes a message that names the resource, so the two messages differ by the name of the table. | correctness | Minor | Fixed in `04126022d5` |
| R2-4 | The row of FREQ-JVMEM-002 in `3. Traceability`, `docs/design/JVMEM-jvm-memory-pools-view/plan.md:175` at `d988ad69e1`, and criterion 15 of `Item 2: End to end tests of the view on a cluster`, `docs/design/JVMEM-jvm-memory-pools-view/plan.md:136` at `d988ad69e1` | FREQ-JVMEM-002 holds a row for every pool whichever rows the statement asks for. Only criterion 15, a read of another pool by name that fails, shows that part. It is neither tagged with the requirement nor in its row. | plan consistency | Minor | Fixed in `eaf2ebee02` |
| R2-5 | Exit criteria 2, 3, 5 and 10 of `Milestone 1: The view`, `docs/design/JVMEM-jvm-memory-pools-view/delivery-plan.md:63` at `d988ad69e1`, and the paragraph on the parts of continuous integration in `6. Test plan`, `docs/design/JVMEM-jvm-memory-pools-view/delivery-plan.md:164` at `d988ad69e1` | Exit criteria 2, 3 and 5 run at the last merge of the milestone. Parts of continuous integration that are merged after item 2 cannot run at that commit, so the gate cannot pass without a new plan. | plan consistency | Minor | Fixed in `cb5515dad8` |
| R2-6 | The note on criterion 17 in `1. Items`, `docs/design/JVMEM-jvm-memory-pools-view/plan.md:106` at `d988ad69e1`, and limit 2 of `2. Validation items`, `docs/design/JVMEM-jvm-memory-pools-view/plan.md:162` at `d988ad69e1` | The note says the tests of criterion 7 show that the view catches nothing. A view that catches, writes a log line and throws the same object again passes criteria 7 and 22. | plan consistency | Minor | Fixed in `c64989090a` |
| R2-7 | Limit 7 of `2. Validation items`, `docs/design/JVMEM-jvm-memory-pools-view/plan.md:167` at `d988ad69e1` | The limit says one test of item 1 alone proves no value is kept. That test reads the object of the view class, so a value kept in a static field or another object passes it. | plan consistency | Minor | Fixed in `d0fd18aba3` |
| R2-8 | Criterion 22 of `Item 2: End to end tests of the view on a cluster`, `docs/design/JVMEM-jvm-memory-pools-view/plan.md:143` at `d988ad69e1` | The first outcome names no kind of role. A superuser passes a permission check whatever the row does, and a role with no grant on the other table fails it although the row did nothing. | plan consistency | Minor | Fixed in `03713c6b6e` |

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
