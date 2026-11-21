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

# Delivery plan: JVM memory pools view in CQL

| Field | Value |
|---|---|
| Title | Delivery plan for JVM memory pools view in CQL |
| Document type | Plan (ISO/IEC/IEEE 15289), project plan content per ISO/IEC/IEEE 16326 |
| Status | Draft |
| Version | 1 |
| Author | Architect: chronitondb-agent |
| Approver | The maintainer who merges the pull request |
| References | The [feature spec](feature-spec.md) and the [plan](plan.md). Decision records [DEC-JVMEM-0001](decisions/DEC-JVMEM-0001-jvm-memory-pools-view-has-no-switch.md), [DEC-JVMEM-0003](decisions/DEC-JVMEM-0003-jvm-memory-pools-view-stays-at-normal-risk.md) and [DEC-JVMEM-0011](decisions/DEC-JVMEM-0011-a-read-of-the-view-is-no-request-path.md). Line `chronitondb-sandbox`. |
| Areas | observability |

Revision history, one row for each version:

| Version | Date | Change | Decision record |
|---|---|---|---|
| 1 | 2026-11-21 | First version | None |

Full history in git: [commits of this file](https://github.com/chronitonlabs/chronitondb/commits/chronitondb-sandbox/docs/design/JVMEM-jvm-memory-pools-view/delivery-plan.md)

Location: `docs/design/JVMEM-jvm-memory-pools-view/delivery-plan.md` on the line `chronitondb-sandbox`. Process: [additive.md](../../process/additive.md).

"Section" with a number and no other document named is a section of the feature spec, and "problem" with a number is a problem of its section 4. "Item" with a number is an item of the plan. A fact about the build or the checks of the line is cited by its letter, as fact A to fact D, and section 6 holds each one with the tree it was read in.

## Contents

- [1. Milestones](#1-milestones)
  - [Milestone 1: The view](#milestone-1-the-view)
- [2. Order rationale](#2-order-rationale)
- [3. Line choice](#3-line-choice)
- [4. Parallel work limit](#4-parallel-work-limit)
- [5. Re-plan triggers](#5-re-plan-triggers)
- [6. Test plan](#6-test-plan)

## 1. Milestones

The feature has one milestone. It is the first and the final one.

### Milestone 1: The view

- **Items:** 1, the build item, and 2, the validation item.
- **What it makes testable:** every feature requirement of section 3: the view on a started node and on a started cluster, and its reference page.
- **Exit criteria:**
  1. The pull requests of item 1 and item 2 are merged on the line, each with its required checks passed and a clean review on the commit that was merged.
  2. Every test that item 1 adds passes on the line at the last merge of the milestone, in the unit test configuration `test-latest`, on Java 17.
  3. Every validation test of item 2 passes on the line at the same commit, in the latest configuration of the in-JVM distributed tests, on Java 17.
  4. The two tests that item 3 of the outcome of [DEC-JVMEM-0003](decisions/DEC-JVMEM-0003-jvm-memory-pools-view-stays-at-normal-risk.md) names, one that starts a node and reads the view and one that compares the view with the memory pools of the same JVM, are among the tests of criterion 2 and pass.
  5. The unit tests of Apache Cassandra for its virtual tables, the 18 test classes of fact D, and every other suite of Apache Cassandra that the design record of an item names, pass unchanged at the same commit.
  6. The test of a grant row left behind, which problem 7 in section 4.1 names, is among the tests of criterion 2 and passes. It is the one test of the way back that the feature has.
  7. Every feature requirement of section 3 is delivered, by the check of the merged code against the requirements that the milestone report holds, with no behaviour that no requirement asks for.
  8. The reference page reads as one whole and holds every statement that FREQ-JVMEM-012, FREQ-JVMEM-013, FREQ-JVMEM-015, FREQ-JVMEM-016, FREQ-JVMEM-019 and FREQ-JVMEM-020 name.
  9. No blocker and no major finding of a review is open on either item.
  10. The two parts of continuous integration that section 6 names exist, and criteria 2, 3 and 5 have run in them. The maintainers plan those parts outside this feature, as section 6 says.
- **Release and line:** the line `chronitondb-sandbox`. The view ships in the first release of that line that is cut after this milestone's report is merged. The repository holds no release proposal and no line plan for the line yet, so this plan names no version. The feature has no switch, so the gate makes nothing switchable: the view is present on every node that runs that release, which is the default section 2.8 sets for the line. Item 2 of section 2.8 says that the view is present whether the feature is finished before or after the line's first release, so the edge of [PRINCIPLE-018](../../process/principles.md#principle-018) does not turn it off.

No upgrade test, no rollback test and no mixed version test is among the exit criteria. The milestone brings no on-disk format, no message between nodes and no row of a schema table (section 7.1), so the rule of [PRINCIPLE-062](../../process/principles.md#principle-062) for a milestone with an on-disk format change does not apply. Section 7.2 and section 7.4 state the behaviour in a cluster of mixed versions and the way back, and section 4.1 says for problems 6 and 7 why no test on this line starts a node without the view. Criterion 6 names the test that stands for the way back.

No benchmark is among the exit criteria, for the reason item 2 of section 2.5 and [DEC-JVMEM-0011](decisions/DEC-JVMEM-0011-a-read-of-the-view-is-no-request-path.md) give.

## 2. Order rationale

There is one milestone, because the feature has no switch. A feature with no switch merges no item that makes unfinished work reachable ([PRINCIPLE-020](../../process/principles.md#principle-020)), and the hook makes the view reachable. So the view cannot be spread over milestones without a switch that nothing else needs ([PRINCIPLE-016](../../process/principles.md#principle-016), [DEC-JVMEM-0001](decisions/DEC-JVMEM-0001-jvm-memory-pools-view-has-no-switch.md)). Section 2.8 and section 11 say the same.

Inside the milestone item 1 comes first and item 2 second. Item 2 tests the merged view and its merged reference page, so it cannot start before item 1 is merged. The riskiest part, a node that does not start because of the view (problem 1), is in item 1, and every test of item 1 that starts a node catches it.

## 3. Line choice

The feature is built on the line `chronitondb-sandbox`. The issue of the feature carries that line label and no other, the feature spec is approved on that line, and every code fact of the spec was read in its tree.

This plan plans no port to the line `chronitondb-5.0` or `chronitondb-6.0`. A port would be later milestones, made of items whose `Line` names the other line, and it would come into this plan through change control. Section 12 of the feature spec gives the lines of the same code in Apache Cassandra `cassandra-6.0` and trunk, for the work of such a port.

## 4. Parallel work limit

The limit is 1. Item 2 depends on item 1, so the two items cannot be in progress at once, and the feature has no third item.

## 5. Re-plan triggers

1. An exit criterion of milestone 1 fails, or cannot run where section 6 says it runs.
2. The design record of item 1 finds that the view cannot be delivered whole in one pull request, or that it needs a change to a file of Apache Cassandra other than the hook of section 2.7.
3. The design record of an item finds that a test of Apache Cassandra asserts behaviour that the view changes, or pins a listing in which the view would alter or remove a line that is there.
4. Risk R1 of section 9 happens: an import from Apache Cassandra brings a table of the same name, or changes the hook file so that the hook no longer fits.
5. Risk R2 of section 9 happens: the line starts to build on a JDK other than Java 17, or a test finds a JDK or a collector that reports its memory pools in a way the view does not show as section 2.2 says.
6. An import from Apache Cassandra changes code that a fact of section 12 cites before the item that rests on that fact is merged.
7. A decision of the maintainers changes the feature spec, the class of the feature or the line.
8. The parts of continuous integration that section 6 names do not exist when item 2 is merged. The milestone report then recommends no-go and asks the maintainers.
9. The line gets its scenario module before the design record of an item is merged. Section 4.1 plans the tests without one.

A re-plan goes through change control, as [additive.md](../../process/additive.md#change-control-after-a-merge) says.

## 6. Test plan

This is the test plan of the feature in the sense of ISO/IEC/IEEE 29119. It rests on section 4.1, which names each test and the problem it catches, and it does not restate that section. Each item's design record and coverage file name the test classes.

**Test levels used.**

| Level | Used | What it holds for this feature |
|---|---|---|
| Unit tests | Yes | Every test that section 4.1 names for item 1, under `test/unit/org/chronitondb/virtual/`: the view on a test node through CQL, rows built from pools of the test's own, permissions, refusals, grants, the grant row left behind and no work when nothing reads the view. |
| Documentation tests | Yes | The tests of the reference page that problems 3, 6, 7, 8 and 10 in section 4.1 name. They are unit tests of item 1 that read the page. |
| In-JVM distributed tests | Yes | The validation tests of item 2 on a started cluster of 2 nodes, under `test/distributed/org/chronitondb/virtual/test/`. |
| Scenarios | No | The line has no scenario module (section 4.1, [testing.md](../../process/testing.md#test-levels)). Each requirement is proven by a unit test or an in-JVM distributed test, named in the coverage file of its item. |
| Python distributed tests | No | No criterion of the plan needs a node process or a tool of its own. |
| Upgrade and rollback tests | No | The feature brings no on-disk format, no message and no schema row (section 7.1). No test on this line starts a node of an earlier release (problems 6 and 7 in section 4.1). |
| Benchmarks | No | The feature touches no request path of Apache Cassandra and no background path that competes with requests (item 2 of section 2.5, [DEC-JVMEM-0011](decisions/DEC-JVMEM-0011-a-read-of-the-view-is-no-request-path.md)). |
| Golden corpora | No | The feature has no output that must stay identical across library versions. |
| Parity suite | No | It is not built yet ([testing.md](../../process/testing.md#test-levels)). Until it is, the suites of Apache Cassandra that each design record names run unchanged, which is exit criterion 5. |

**What milestone 1 tests at which level.** Item 1 is tested at the unit level, with the documentation tests. Item 2 is the in-JVM distributed level. The traceability table of the [plan](plan.md#3-traceability) maps each feature requirement to the criteria of both items.

**Test environments.**

1. **JDK.** The line builds on Java 17 only (fact A). Section 4.1 says the tests run on each JDK the line's build supports, and on this line that is Java 17. Re-plan trigger 5 covers a change of that.
2. **Configuration.** The project's own tests run on the options that `test-latest` and the latest configuration of the in-JVM distributed tests set ([testing.md](../../process/testing.md#test-levels), [PRINCIPLE-067](../../process/principles.md#principle-067), fact B). The view class reads no setting, so no other test configuration applies to it.
3. **The build machines.** Until continuous integration runs the tests, each test runs on the project's build machines with the commands of the checks every commit passes, in a checkout of the line at the last merge of the milestone ([additive.md](../../process/additive.md#milestone-gates)).
4. **Continuous integration.** The checks that run on a pull request to the line today run no test of the build (fact C).

**Where each exit criterion runs.**

| Exit criterion | Where it runs |
|---|---|
| 1. Both pull requests merged, checks passed, reviews clean | Read from GitHub. |
| 2. The tests of item 1 | On the build machines until the parts below exist, then in continuous integration. |
| 3. The validation tests of item 2 | On the build machines until the parts below exist, then in continuous integration. |
| 4. The two tests of DEC-JVMEM-0003 | With criterion 2. |
| 5. The unchanged suites of Apache Cassandra, those of fact D and those the design records name | On the build machines until the parts below exist, then in continuous integration. |
| 6. The test of a grant row left behind | With criterion 2. |
| 7. Requirements delivered | A read of the merged code against section 3, for the milestone report. |
| 8. The reference page as one whole | A read of the merged page, for the milestone report. |
| 9. No blocker or major finding open | Read from the review records of both items. |
| 10. The parts of continuous integration | Read from GitHub. |

**The parts of continuous integration the gate needs.** Milestone 1 is the final milestone of the feature, the one that becomes a release. The continuous integration that the milestone gate needs is in place before it, and the report of a final milestone recommends no-go without it ([additive.md](../../process/additive.md#milestone-gates)). The gate of this milestone needs two parts, and neither exists on the line today (fact C):

1. A run, on Java 17, of the project's own unit tests in `test-latest` and of its own in-JVM distributed tests in their latest configuration, on a pull request to the line and on the line itself. It holds exit criteria 2, 3, 4 and 6.
2. A run of the unit tests of Apache Cassandra for its virtual tables (fact D), and of every other suite of Apache Cassandra that a design record names, unchanged, on the line. It holds exit criterion 5.

The repository holds no plan for either part. They are not items of this feature: a workflow of the project is work of the area `build-and-test`, outside the one area of this feature. Both parts are work for the maintainers to plan and to open, as work of its own on the line, and merging this plan accepts that the gate of this feature waits for them. The items of this feature do not wait: item 1 and item 2 are designed, built, reviewed and merged without the two parts, and only the milestone report needs them. Exit criterion 10 and re-plan trigger 8 hold the gate to them.

**Facts about the build and the checks of the line.**

| Fact | Claim | Our line | Its base and Apache Cassandra now |
|---|---|---|---|
| A | The build accepts Java 17 and no other JDK. | The property `java.supported`, `build.xml:48`, with the value `17`, ChronitonDB chronitondb-sandbox at `34fdee9fd9`. The delta entry [java-version-per-line.md](../../delta/java-version-per-line.md) records the difference. | The value is `11,17` at line 48 in the base, Apache Cassandra cassandra-5.0 at `76550e9314`, and in cassandra-5.0 at `3e3892ce99`. It is `11,17,21` at line 48 in cassandra-6.0 at `243566b968` and trunk at `25cb50d1f7`. |
| B | The build has a target for the unit tests in the latest configuration and one for chosen in-JVM distributed tests in the latest configuration. | The target `test-latest`, `build.xml:1436`, and the target `test-jvm-dtest-latest-some`, `build.xml:1839`, ChronitonDB chronitondb-sandbox at `34fdee9fd9`. | The same lines in the base, Apache Cassandra cassandra-5.0 at `76550e9314`. Lines 1439 and 1842 in cassandra-5.0 at `3e3892ce99`, lines 1723 and 2157 in cassandra-6.0 at `243566b968`, and lines 1731 and 2165 in trunk at `25cb50d1f7`. |
| C | No workflow of the line runs a test target of the build. Of the 15 workflow files, three call the build: the job `ant-check` runs Apache Cassandra's code checks, and the shape and SpotBugs workflows fetch the libraries and build the jar. | The job `ant-check`, `.github/workflows/code-check.yaml:28`. The step that runs `ant resolver-retrieve-build`, `.github/workflows/chronitondb-shape.yml:80`. The step that runs `ant jar`, `.github/workflows/chronitondb-spotbugs.yml:86`. All ChronitonDB chronitondb-sandbox at `34fdee9fd9`. | The base, Apache Cassandra cassandra-5.0 at `76550e9314`, holds three of those files, `build-scripts.yaml`, `code-check.yaml` and `jenkins-check.yaml`, and so do cassandra-5.0 at `3e3892ce99` and trunk at `25cb50d1f7`. The other 12 are the project's own, which Apache Cassandra does not have. What the three files run in Apache Cassandra was not read, and cassandra-6.0 was not read. |
| D | Apache Cassandra has 18 unit test classes for its virtual tables, and the line has changed none of them. | The directory `test/unit/org/apache/cassandra/db/virtual/`, with `SettingsTableTest`, `test/unit/org/apache/cassandra/db/virtual/SettingsTableTest.java`, among its 18 classes, ChronitonDB chronitondb-sandbox at `34fdee9fd9`. | The same 18 classes in the base, Apache Cassandra cassandra-5.0 at `76550e9314`, with no difference between the two trees in that directory. Apache Cassandra now was not read. |
