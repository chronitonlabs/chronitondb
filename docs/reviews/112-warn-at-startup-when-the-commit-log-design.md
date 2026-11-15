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
| Status | Closed |
| Work product | Design record: `docs/design/CLD-commitlog-disk-check/design-record.md` |
| Pull request | #116 |
| Version reviewed | `20b18cc901` |
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
| 1 | 2026-11-15 | `b210d52a66` | The whole change | Changes requested | 0 | 1 | 6 | 0 |
| 2 | 2026-11-15 | `20b18cc901` | The changes since `b210d52a66` | Clean | 0 | 0 | 2 | 0 |

## 2. Anomaly list

One row per finding, in the reviewer's order. The id is `R<round>-<number>`. A finding raised again in a later round gets a new id and names the earlier one.

| Id | Location | Description | Classification | Disposition |
|---|---|---|---|---|
| R1-1 | `14. Testing`, `design-record.md:397` at `b210d52a66` | Test 19 asserts that neither other counter exists, but step 3 of the run and REQ-CLD-021 leave the order of those two counters open. A correct build fails the test. | Major | Fixed in `e83b7e3976` |
| R1-2 | `8. Observability`, `design-record.md:314` at `b210d52a66` | The unreadable warning says "left that directory out" for the commit log directory too, where step 5 of the run compares nothing. Lines 57 and 90 of the page skeleton disagree. | Minor | Fixed in `5d1408a7ba` |
| R1-3 | `8. Observability`, `design-record.md:312` at `b210d52a66` | The record and line 75 of the page skeleton say the failed warning shows a missing or stale counter. Its text names no counter. | Minor | Fixed in `7acd225289` |
| R1-4 | `4. Prior art reviewed`, `design-record.md:217` at `b210d52a66` | `YamlConfigurationLoader.loadConfig` catches `YAMLException` only, `YamlConfigurationLoader.java:146` at `8d744bb0ac`, not any failure. The conclusion holds. | Minor | Fixed in `b629bdeb53` |
| R1-5 | `4. Prior art reviewed`, `design-record.md:210` at `b210d52a66` | The citations at lines 210, 222 and 331 give one commit after several line ranges, so each earlier range reads as a bare file and line. The claims were verified. | Minor | Fixed in `02d6292df5` |
| R1-6 | `4. Prior art reviewed`, `design-record.md:223` at `b210d52a66` | The 6.0 port claim omits that `StartupChecks.withServiceLoaderTests`, `StartupChecks.java:199` at `2249e37b51`, refuses a name Apache also uses. The record should name the risk. | Minor | Fixed in `99687daaf5` |
| R1-7 | `3. Stock behaviour preservation`, `design-record.md:183` at `b210d52a66` | The record never says how item 2 of Feature switches and defaults, refuse to turn on before the final gate, applies to a feature that fits one item. | Minor | Fixed in `3a9e890e55` |
| R2-1 | `4. Prior art reviewed`, `design-record.md:219` at `20b18cc901` | The fix of R1-4 says `YamlConfigurationLoader.loadConfig` catches one exception type. It also catches `IOException` and throws `AssertionError`, `YamlConfigurationLoader.java:129` to `133` at `8d744bb0ac`. Only the try that builds the Config catches one type. | Minor | Fixed in `edd8f309d0` |
| R2-2 | `4. Prior art reviewed`, `design-record.md:212` at `20b18cc901` | Stock item 1 says the checks run before the node changes any local state. `CassandraDaemon.setup` runs `migrateSystemDataIfNeeded` and `CommitLog.instance.start` first, `CassandraDaemon.java:239` and `256` at `8d744bb0ac`. Nothing depends on it. | Minor | Fixed in `ac585d3604` |

1. **Fixed in `<hash>`**: the commit that fixes the finding. Several commits are joined with "and". A finding on the pull request's title or body is "Fixed in the pull request title" or "body".
2. **Accepted: `<reason>`**: the work product stays as it is, for the reason given. The reviewer judges the reason in the next round.
3. **Waived by `<the maintainers>`: `<reason>`**: the maintainers decided the finding needs no change, as "the maintainers" or "a maintainer, `<GitHub username>`".
4. **Open: `<what settles it>`**: no disposition yet, while the maintainers decide. A clean review leaves none open from an earlier round.

## 3. Decisions

No decisions.

## 4. Limits

Round 1 did not read the class loader filter of the in-JVM test library, which problem 8 of the design record rests on. Its source is outside what the review could read, as the design record says.

Round 2 did not read it either, for the same reason. Round 2 read the changes up to `20b18cc901`. The two fixes of its findings, `edd8f309d0` and `ac585d3604`, came after it and no round read them.

## 5. Exit decision

Accept: round 2 on `20b18cc901` found no blocker and no major, and every finding has a disposition. The maintainers decide by merging.
