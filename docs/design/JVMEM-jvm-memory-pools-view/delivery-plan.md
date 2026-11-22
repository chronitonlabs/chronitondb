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
| References | The [feature spec](feature-spec.md) and the [plan](plan.md). Decision records [DEC-JVMEM-0001](decisions/DEC-JVMEM-0001-jvm-memory-pools-view-has-no-switch.md), [DEC-JVMEM-0011](decisions/DEC-JVMEM-0011-a-read-of-the-view-is-no-request-path.md), [DEC-JVMEM-0012](decisions/DEC-JVMEM-0012-the-test-runs-the-gate-needs-are-built-outside-the-feature.md) and [DEC-JVMEM-0013](decisions/DEC-JVMEM-0013-the-view-stays-at-normal-risk-and-the-runs-of-its-two-tests-are-named.md). Line `chronitondb-sandbox`. |
| Areas | observability |

Revision history, one row for each version:

| Version | Date | Change | Decision record |
|---|---|---|---|
| 1 | 2026-11-21 | First version | None |

Full history in git: [commits of this file](https://github.com/chronitonlabs/chronitondb/commits/chronitondb-sandbox/docs/design/JVMEM-jvm-memory-pools-view/delivery-plan.md)

Location: `docs/design/JVMEM-jvm-memory-pools-view/delivery-plan.md` on the line `chronitondb-sandbox`. Process: [additive.md](../../process/additive.md).

"Section" with a number and no other document named is a section of the feature spec, and "problem" with a number is a problem of its section 4. "Item" with a number is an item of the plan. A fact about the build, the checks or the test code of the line, or about code of Apache Cassandra that a criterion of the plan rests on, is cited by its letter, as fact A to fact J, and section 6 holds each one with the tree it was read in.

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
- **The gate commit:** the one commit of the line at which the tests of exit criteria 2, 3 and 5 run for the milestone report. The report names it. It is the first commit of the line, at the merge of item 2 or after it, at which both parts of continuous integration that section 6 names have run those tests. Where both parts exist when item 2 is merged and both run at that merge, it is the merge of item 2. Where a part is merged after item 2, or does not run at that merge because it runs at set times or when it is asked for, it is a later commit of the line. That commit holds item 1, item 2, both parts and the other work that was merged meanwhile.
- **Exit criteria:**
  1. The pull requests of item 1 and item 2 are merged on the line, each with its required checks passed and a clean review on the commit that was merged.
  2. Every test that item 1 adds passes on the line at the gate commit, on Java 17: its unit tests in the configuration `test-latest`, and its one in-JVM distributed test, which criterion 19 of item 1 names, in the latest configuration of the in-JVM distributed tests.
  3. Every validation test of item 2 passes on the line at the same commit, in the latest configuration of the in-JVM distributed tests, on Java 17.
  4. The two tests that item 3 of the outcome of [DEC-JVMEM-0013](decisions/DEC-JVMEM-0013-the-view-stays-at-normal-risk-and-the-runs-of-its-two-tests-are-named.md) names, one that starts a node and reads the view and one that compares the view with the memory pools of the same JVM, pass in every run that section 6 names for them: the test log of the commit of the pull request of item 1 that adds the view to the hook and of each commit of that pull request after it, the test log of each commit of the pull request of item 2, and the run of criterion 2 on the line at the gate commit. From the day the first part of continuous integration that section 6 names exists, they also pass in each of its runs on the line from the merge of item 1 on, and in each of its runs on those two pull requests at a commit that holds the view in the hook. A run of that part on a pull request of other work holds both tests too. A failure there fails the check of that pull request, and this criterion does not read it.
  5. The tests of Apache Cassandra that fact D, fact E and fact H name pass unchanged at the same commit, on Java 17, the unit test classes among them in the configuration `test-latest` and the in-JVM distributed test classes in the latest configuration of the in-JVM distributed tests: its 18 unit test classes for its virtual tables, its test `JMXCompatibilityTest` of the MBeans of a node, its 47 unit test classes for nodetool commands, its unit test class `GrantAndRevokeTest` of grants, which grants and revokes on the keyspace `system_views`, and its 2 in-JVM distributed test classes `VirtualTableFromInternodeTest` and `VirtualTableLogsTest`, which read tables of `system_views` on a cluster. So does every other suite of Apache Cassandra that the design record of an item names, on the same JDK and in the same two configurations. A test among them that pins a complete listing to which the view adds a line passes with the lines that the design record of item 1 names as added, and with no other change ([PRINCIPLE-013](../../process/principles.md#principle-013)).
  6. The test of a grant row left behind, which problem 7 in section 4.1 names, is among the tests of criterion 2 and passes. Its counterpart on a started cluster, criterion 22 of item 2, is among the tests of criterion 3 and passes. Both test what a grant row does after a cluster moved back. The step that section 7.4 has an operator take before moving back is tested by criterion 13 of item 2, which criterion 3 holds.
  7. Every feature requirement of section 3 is delivered, by the check of the merged code against the requirements that the milestone report holds, with no behaviour that no requirement asks for.
  8. The reference page reads as one whole, holds every statement that FREQ-JVMEM-012, FREQ-JVMEM-013, FREQ-JVMEM-015, FREQ-JVMEM-016, FREQ-JVMEM-019 and FREQ-JVMEM-020 name, and gives each column the meaning that section 2.2 gives it.
  9. No blocker and no major finding of a review is open on either item.
  10. The two parts of continuous integration that section 6 names exist, and criteria 2, 3 and 5 have run in them at the gate commit. The maintainers plan those parts outside this feature, as section 6 says.
- **Release and line:** the line `chronitondb-sandbox`. The view ships in the first release of that line that is cut after this milestone's report is merged. The repository holds no release proposal and no line plan for the line yet, so this plan names no version. The feature has no switch, so the gate makes nothing switchable: the view is present on every node that runs that release, which is the default section 2.8 sets for the line. Item 2 of section 2.8 says that the view is present whether the feature is finished before or after the line's first release, so the edge of [PRINCIPLE-018](../../process/principles.md#principle-018) does not turn it off.

No upgrade test, no rollback test and no mixed version test is among the exit criteria. The milestone brings no on-disk format, no message between nodes and no row of a schema table (section 7.1), so the rule of [PRINCIPLE-062](../../process/principles.md#principle-062) for a milestone with an on-disk format change does not apply. Section 7.2 and section 7.4 state the behaviour in a cluster of mixed versions and the way back, and section 4.1 says for problems 6 and 7 why no test on this line starts a node without the view. Three tests stand for the way back: the two tests of a grant row left behind, which criterion 6 names, and the test of the step of section 7.4, which is criterion 13 of item 2 and runs with criterion 3.

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
2. The design record of item 1 finds that the view cannot be delivered whole in one pull request, that it needs a change to a file of Apache Cassandra other than the hook of section 2.7, or that a test cannot supply a memory pool on one node of an in-JVM cluster only, as criterion 19 of item 1 needs.
3. The design record of an item finds that a test of Apache Cassandra asserts behaviour that the view changes, or pins a listing in which the view would alter or remove a line that is there.
4. Risk R1 of section 9 happens: an import from Apache Cassandra brings a table of the same name, or changes the hook file so that the hook no longer fits.
5. Risk R2 of section 9 happens: the line starts to build on a JDK other than Java 17, or a test finds a JDK or a collector that reports its memory pools in a way the view does not show as section 2.2 says.
6. An import from Apache Cassandra changes code that a fact of section 12 cites before the item that rests on that fact is merged.
7. A decision of the maintainers changes the feature spec, the class of the feature or the line.
8. The parts of continuous integration that section 6 names do not exist when item 2 is merged. The milestone report then recommends no-go and asks the maintainers. The order of the merges needs no change to this plan: when both parts exist, exit criteria 2, 3 and 5 run at the gate commit, as milestone 1 defines it, and a new report reads that run.
9. The line gets its scenario module before the design record of an item is merged. Section 4.1 plans the tests without one.

A re-plan goes through change control, as [additive.md](../../process/additive.md#change-control-after-a-merge) says.

## 6. Test plan

This is the test plan of the feature in the sense of ISO/IEC/IEEE 29119. It rests on section 4.1, which names each test and the problem it catches, and it does not restate that section. Each item's design record and coverage file name the test classes.

**Test levels used.**

| Level | Used | What it holds for this feature |
|---|---|---|
| Unit tests | Yes | Every test that section 4.1 names for item 1, under `test/unit/org/chronitondb/virtual/`: the view on a test node through CQL, rows built from pools of the test's own, permissions, refusals, grants, the grant row left behind and no work when nothing reads the view. |
| Documentation tests | Yes | The tests of the reference page that problems 3, 6, 7, 8 and 10 in section 4.1 name. They are unit tests of item 1 that read the page. |
| In-JVM distributed tests | Yes | The validation tests of item 2 on a started cluster of 2 nodes, and the one test of item 1 that criterion 19 of item 1 names, under `test/distributed/org/chronitondb/virtual/test/`. |
| Scenarios | No | The line has no scenario module (section 4.1, [testing.md](../../process/testing.md#test-levels)). Each requirement is proven by a unit test or an in-JVM distributed test, named in the coverage file of its item. |
| Python distributed tests | No | No criterion of the plan needs a node process or a tool of its own. |
| Upgrade and rollback tests | No | The feature brings no on-disk format, no message and no schema row (section 7.1). No test on this line starts a node of an earlier release (problems 6 and 7 in section 4.1). |
| Benchmarks | No | The feature touches no request path of Apache Cassandra and no background path that competes with requests (item 2 of section 2.5, [DEC-JVMEM-0011](decisions/DEC-JVMEM-0011-a-read-of-the-view-is-no-request-path.md)). |
| Golden corpora | No | The feature has no output that must stay identical across library versions. |
| Parity suite | No | It is not built yet ([testing.md](../../process/testing.md#test-levels)). Until it is, the tests of Apache Cassandra that facts D, E and H name, and the suites that each design record names, run unchanged, which is exit criterion 5. |

**What milestone 1 tests at which level.** Item 1 is tested at the unit level, with the documentation tests, and by one in-JVM distributed test of the place where a test supplies memory pools. Item 2 is the in-JVM distributed level. The traceability table of the [plan](plan.md#3-traceability) maps each feature requirement to the criteria of both items.

**Test environments.**

1. **JDK.** The line builds on Java 17 only (fact A). Section 4.1 says the tests run on each JDK the line's build supports, and on this line that is Java 17. Re-plan trigger 5 covers a change of that.
2. **Configuration.** The project's own tests run on the options that `test-latest` and the latest configuration of the in-JVM distributed tests set ([testing.md](../../process/testing.md#test-levels), [PRINCIPLE-067](../../process/principles.md#principle-067), fact B). The view class reads no setting (criterion 25 of item 1), so no other test configuration applies to it. The tests of Apache Cassandra that exit criterion 5 names run on the same options and the same JDK as the project's own tests: the line builds on no other JDK (fact A), and the project supports no setup but those options ([PRINCIPLE-067](../../process/principles.md#principle-067)).
3. **The build machines.** Until continuous integration runs the tests, the tests that exit criteria 2, 3 and 5 name can run on the project's build machines, with the commands of the checks every commit passes, in a checkout of the line at the merge of item 2 ([additive.md](../../process/additive.md#milestone-gates)). Such a run shows whether those tests pass at that commit. It is no run of exit criteria 2, 3 and 5, which run in continuous integration at the gate commit, and it does not meet exit criterion 10. So the report of a milestone whose tests ran on the build machines only gives that run as what is known so far and recommends no-go.
4. **Continuous integration.** The checks that run on a pull request to the line today run no test of the build (fact C).

**Where each exit criterion runs.**

| Exit criterion | Where it runs |
|---|---|
| 1. Both pull requests merged, checks passed, reviews clean | Read from GitHub. |
| 2. The tests of item 1 | In continuous integration, at the gate commit. Until both parts below exist, a run on the build machines shows whether the tests pass, and it is no run of this criterion. |
| 3. The validation tests of item 2 | In continuous integration, at the gate commit. Until both parts below exist, a run on the build machines shows whether the tests pass, and it is no run of this criterion. |
| 4. The two tests of DEC-JVMEM-0013 | Read from the test logs of both pull requests, and with criterion 2. The paragraph below this table says in which runs the two tests pass. |
| 5. The unchanged tests of Apache Cassandra, those of facts D, E and H and those the design records name | In continuous integration, at the gate commit. Until both parts below exist, a run on the build machines shows whether the tests pass, and it is no run of this criterion. |
| 6. The two tests of a grant row left behind | With criteria 2 and 3. |
| 7. Requirements delivered | A read of the merged code against section 3, for the milestone report. |
| 8. The reference page as one whole | A read of the merged page, for the milestone report. |
| 9. No blocker or major finding open | Read from the review records of both items. |
| 10. The parts of continuous integration | Read from GitHub. |

**Where the two tests of DEC-JVMEM-0013 run.** Item 3 of the outcome of [DEC-JVMEM-0013](decisions/DEC-JVMEM-0013-the-view-stays-at-normal-risk-and-the-runs-of-its-two-tests-are-named.md) names the runs in which two tests pass, and the Normal risk of the feature rests on them: a test that starts a node and reads the view, and a test that compares the view with the memory pools of the same JVM. Both are unit tests of item 1. No workflow of the line runs a test today (fact C), so the first part of continuous integration below, which that record names as one of those runs, does not exist yet. Until it does, the two tests run here:

1. **Each commit of item 1 from the hook on.** A commit of item 1 that comes before the view is added to the hook builds no node that holds the view, so it is no build of the feature. The commit that adds the view to the hook is the first build of the feature. Criterion 26 of item 1 asks for both tests in the test log of that commit and of each commit of the pull request after it, so the item adds both tests no later than that commit. The test run before each commit holds the tests that the item adds ([testing.md](../../process/testing.md#when-each-test-runs)), and its results are the test log of that commit, attached to the pull request.
2. **Each commit of item 2.** Item 2 changes no code that the two tests cover, so the test run before its commits would not hold them by that rule. Criterion 25 of item 2 puts them in it. Item 2 starts from the line after item 1 is merged, so its first test log is the first run of both tests on the line as merged.
3. **The gate.** Both tests are among the tests of exit criterion 2, which run on the line at the gate commit.
4. **A merge to the line.** Nothing runs the two tests when a pull request is merged, and item 4 of the outcome of [DEC-JVMEM-0013](decisions/DEC-JVMEM-0013-the-view-stays-at-normal-risk-and-the-runs-of-its-two-tests-are-named.md) allows a merge of other work of the project to go without them until the first part of continuous integration exists. The test log of a pull request is of its head commit, and the commit that the merge puts on the line differs from it when the line moved meanwhile. A fault that a merge brings to the view is found by the next run of 1, 2 or 3, or by the test run of a later change that touches the view class or the hook file. It is not found at the merge. One kind of merge has a run of both tests before it. The full test suites run before an import from Apache Cassandra is merged ([testing.md](../../process/testing.md#when-each-test-runs)), and a full run of a unit test target of the build holds both tests, because such a target takes every class under `test/unit` whose name ends in `Test`, the project's own among them (fact J). No workflow makes that run today (fact C), so until continuous integration exists it is a run on the build machines, on the branch of the import. A merge of other work of the project has no such run. The first part of continuous integration below closes that, since it runs both tests on each pull request to the line and on the line itself.

Exit criterion 4 reads the test logs of 1 and 2 and the run of 3, and the runs of that first part from the day it exists. Until then, a build of the line after a merge of other work of the project, which is no import from Apache Cassandra, is a build that holds the view and on which the two tests have not run. [DEC-JVMEM-0013](decisions/DEC-JVMEM-0013-the-view-stays-at-normal-risk-and-the-runs-of-its-two-tests-are-named.md) accepts that for this view and replaces the rule of the record before it, which had both tests run on every build of the feature. The bound is the first part of continuous integration: from the day it exists every pull request to the line and the line itself get both tests, and the gate of the feature does not pass before both parts exist (exit criterion 10). The full test suites of a release candidate, which run before its promotion ([testing.md](../../process/testing.md#when-each-test-runs)), hold both tests for the reason that the full run before an import does (fact J).

**The parts of continuous integration the gate needs.** Milestone 1 is the final milestone of the feature, the one that becomes a release. The continuous integration that the milestone gate needs is in place before it, and the report of a final milestone recommends no-go without it ([additive.md](../../process/additive.md#milestone-gates)). The gate of this milestone needs two parts, and neither exists on the line today (fact C):

1. A run, on Java 17, of the project's own unit tests in `test-latest` and of its own in-JVM distributed tests in their latest configuration, on a pull request to the line and on the line itself. It holds exit criteria 2, 3, 4 and 6.
2. A run of the tests of Apache Cassandra that facts D, E and H name, and of every other suite of Apache Cassandra that a design record names, unchanged, on the line, on the JDK and in the configurations that exit criterion 5 names. It holds exit criterion 5.

The repository holds no plan for either part. They are not items of this feature: a workflow of the project is work of the area `build-and-test`, outside the one area of this feature. [DEC-JVMEM-0012](decisions/DEC-JVMEM-0012-the-test-runs-the-gate-needs-are-built-outside-the-feature.md) decides that both parts are work for the maintainers to plan and to open, as work of its own on the line, and that the gate of this feature waits for them. The items of this feature do not wait: item 1 and item 2 are designed, built, reviewed and merged without the two parts, and only the milestone report needs them. A part that is merged after item 2 cannot run at the merge of item 2, so exit criteria 2, 3 and 5 run at the gate commit, which milestone 1 defines for both orders of the merges and for a part that does not run at every commit of the line. Exit criterion 10 and re-plan trigger 8 hold the gate to them.

**Facts about the build and the checks of the line.**

| Fact | Claim | Our line | Its base and Apache Cassandra now |
|---|---|---|---|
| A | The build accepts Java 17 and no other JDK. | The property `java.supported`, `build.xml:48`, ChronitonDB chronitondb-sandbox at `34fdee9fd9`, with the value `17`. The delta entry [java-version-per-line.md](../../delta/java-version-per-line.md) records the difference. | The value is `11,17` at line 48 in the base, Apache Cassandra cassandra-5.0 at `76550e9314`, and in cassandra-5.0 at `3e3892ce99`. It is `11,17,21` at line 48 in cassandra-6.0 at `243566b968` and trunk at `25cb50d1f7`. |
| B | The build has a target for the unit tests in the latest configuration and one for chosen in-JVM distributed tests in the latest configuration. | The target `test-latest`, `build.xml:1436`, ChronitonDB chronitondb-sandbox at `34fdee9fd9`, and the target `test-jvm-dtest-latest-some`, `build.xml:1839`, ChronitonDB chronitondb-sandbox at `34fdee9fd9`. | The same lines in the base, Apache Cassandra cassandra-5.0 at `76550e9314`. Lines 1439 and 1842 in cassandra-5.0 at `3e3892ce99`, lines 1723 and 2157 in cassandra-6.0 at `243566b968`, and lines 1731 and 2165 in trunk at `25cb50d1f7`. |
| C | No workflow of the line runs a test target of the build. Of the 15 workflow files, three call the build: the job `ant-check` runs Apache Cassandra's code checks, and the shape and SpotBugs workflows fetch the libraries and build the jar. | The job `ant-check`, `.github/workflows/code-check.yaml:15`, ChronitonDB chronitondb-sandbox at `34fdee9fd9`, with its run step at line 28. The two steps that run `ant resolver-retrieve-build`, `.github/workflows/chronitondb-shape.yml:80`, ChronitonDB chronitondb-sandbox at `34fdee9fd9`, for a checkout of the line, and line 127 of that file for the checkout of the pull request. The step that runs `ant jar`, `.github/workflows/chronitondb-spotbugs.yml:86`, ChronitonDB chronitondb-sandbox at `34fdee9fd9`. | The base, Apache Cassandra cassandra-5.0 at `76550e9314`, holds three of those files, `build-scripts.yaml`, `code-check.yaml` and `jenkins-check.yaml`, and so do cassandra-5.0 at `3e3892ce99` and trunk at `25cb50d1f7`. The other 12 are the project's own, which Apache Cassandra does not have. What the three files run in Apache Cassandra was not read, and cassandra-6.0 was not read. |
| D | Apache Cassandra has 18 unit test classes for its virtual tables, and the line has changed none of them. | The directory `test/unit/org/apache/cassandra/db/virtual/`, with `SettingsTableTest`, `test/unit/org/apache/cassandra/db/virtual/SettingsTableTest.java`, among its 18 classes, ChronitonDB chronitondb-sandbox at `34fdee9fd9`. | The same 18 classes in the base, Apache Cassandra cassandra-5.0 at `76550e9314`, with no difference between the two trees in that directory. Apache Cassandra now was not read. |
| E | Apache Cassandra has a unit test that compares the MBeans of a test node, the metrics among them, with the MBeans that four of its earlier releases had, and 47 unit test classes for nodetool commands. The line has changed none of them. | `JMXCompatibilityTest.diff`, `test/unit/org/apache/cassandra/tools/JMXCompatibilityTest.java:218`, ChronitonDB chronitondb-sandbox at `34fdee9fd9`, which compares the MBeans of the test node with the four files under `test/data/jmxdump/`. The 47 test classes that lie directly in the directory `test/unit/org/apache/cassandra/tools/nodetool/`, with `TpStatsTest`, `test/unit/org/apache/cassandra/tools/nodetool/TpStatsTest.java`, among them, in the same tree. | The same test at the same line, the same four files and the same 47 classes in the base, Apache Cassandra cassandra-5.0 at `76550e9314`, with no difference between the two trees in those paths. The same test at line 218 and 47 classes in cassandra-5.0 at `3e3892ce99`. The test at line 253 in cassandra-6.0 at `243566b968`, with 55 classes, and in trunk at `25cb50d1f7`, with 57 classes. |
| F | Every node of an in-JVM cluster runs in the JVM of the test, with a class loader of its own for the classes that the nodes do not share. The code of the cluster decides which classes the nodes share, with one filter of a library. | `AbstractCluster.Wrapper.newInstance`, `test/distributed/org/apache/cassandra/distributed/impl/AbstractCluster.java:299`, ChronitonDB chronitondb-sandbox at `34fdee9fd9`, which gives each node a new `InstanceClassLoader` at line 303. `AbstractCluster.getSharedClassPredicate`, `test/distributed/org/apache/cassandra/distributed/impl/AbstractCluster.java:1186`, ChronitonDB chronitondb-sandbox at `34fdee9fd9`, the overload with three parameters, builds the test that tells a shared class. The nodes share a class that carries the annotation `Shared` and that `AbstractCluster.findClassesMarkedWith`, `test/distributed/org/apache/cassandra/distributed/impl/AbstractCluster.java:1200`, ChronitonDB chronitondb-sandbox at `34fdee9fd9`, finds, and it scans the package `org.apache.cassandra` and no other, at line 1202. They also share a class that the test names when it builds its cluster, a class that the default filter of `InstanceClassLoader` takes, at line 1195, and a class of Byteman. A class that carries the annotation `Isolated` is not shared. The default filter of `InstanceClassLoader` is in a library that the checkout of the line does not hold, and it was not read. | The same file with no difference in the base, Apache Cassandra cassandra-5.0 at `76550e9314`. The same three methods at lines 299, 1186 and 1200 in cassandra-5.0 at `3e3892ce99`. Lines 353, 1310 and 1324 in cassandra-6.0 at `243566b968` and trunk at `25cb50d1f7`, where the scan names the same one package at line 1326. |
| G | The coordinator of an in-JVM cluster runs a statement inside the node, with a client state of its own making and no connection of a client. | `CoordinatorHelper.unsafeExecuteInternal`, `test/distributed/org/apache/cassandra/distributed/impl/CoordinatorHelper.java:50`, ChronitonDB chronitondb-sandbox at `34fdee9fd9`, the overload that takes a `Dispatcher.RequestTime`, which calls the `execute` method of the statement at line 67. `Coordinator.executeWithResult`, `test/distributed/org/apache/cassandra/distributed/impl/Coordinator.java:59`, ChronitonDB chronitondb-sandbox at `34fdee9fd9`, runs it on the node. | The same two files with no difference in the base, Apache Cassandra cassandra-5.0 at `76550e9314`, and the same overload at line 50 in cassandra-5.0 at `3e3892ce99`. The same overload at line 52 in cassandra-6.0 at `243566b968` and trunk at `25cb50d1f7`. |
| H | Apache Cassandra has a unit test class of grants with a test that grants and revokes on the keyspace `system_views`, and two in-JVM distributed test classes that read tables of `system_views` on a cluster. The line has changed none of them. | `GrantAndRevokeTest.testGrantOnVirtualKeyspaces`, `test/unit/org/apache/cassandra/auth/GrantAndRevokeTest.java:479`, ChronitonDB chronitondb-sandbox at `34fdee9fd9`. `VirtualTableFromInternodeTest`, `test/distributed/org/apache/cassandra/distributed/test/VirtualTableFromInternodeTest.java:40`, ChronitonDB chronitondb-sandbox at `34fdee9fd9`, which reads `system_views.settings` from another node. `VirtualTableLogsTest`, `test/distributed/org/apache/cassandra/distributed/test/VirtualTableLogsTest.java:50`, ChronitonDB chronitondb-sandbox at `34fdee9fd9`, which reads the table of log messages in `system_views`. | The same three files with no difference in the base, Apache Cassandra cassandra-5.0 at `76550e9314`, and the same lines 479, 40 and 50 in cassandra-5.0 at `3e3892ce99`. In cassandra-6.0 at `243566b968` and trunk at `25cb50d1f7` the test of grants stands at line 578, `VirtualTableFromInternodeTest` at line 41 and `VirtualTableLogsTest` at line 50. |
| I | When a role lacks a permission that a statement needs, a `GRANT` or a `REVOKE` among them, Apache Cassandra refuses the statement with an `UnauthorizedException` whose message names the role, the permission and the resource of the statement. So the refusals of the same statement on two tables differ in the name of the table. | `ClientState.ensurePermissionOnResourceChain`, `src/java/org/apache/cassandra/service/ClientState.java:528`, ChronitonDB chronitondb-sandbox at `34fdee9fd9`, the overload that takes a list of resources, which throws at line 538 with the text `User %s has no %s permission on %s or any of its parents`, where the last value is the first resource of the list, the one the statement names. `ClientState.ensurePermission`, `src/java/org/apache/cassandra/service/ClientState.java:475`, ChronitonDB chronitondb-sandbox at `34fdee9fd9`, the overload that takes a resource, reaches it at lines 497 and 503. `PermissionsManagementStatement.authorize`, `src/java/org/apache/cassandra/cql3/statements/PermissionsManagementStatement.java:61`, ChronitonDB chronitondb-sandbox at `34fdee9fd9`, calls that overload for `AUTHORIZE` at line 67. | The same two files with no difference in the base, Apache Cassandra cassandra-5.0 at `76550e9314`. In cassandra-5.0 at `3e3892ce99` the same lines 528, 538, 475, 497 and 503 of `ClientState.java`. In cassandra-6.0 at `243566b968` and trunk at `25cb50d1f7` the overload stands at line 563 and throws at line 573 with the same text, and `ClientState.ensurePermission` stands at line 510 and reaches it at lines 532 and 538. `PermissionsManagementStatement.authorize` was not read again in Apache Cassandra now: fact 19 of the feature spec gives its lines there. |
| J | A full run of a unit test target of the build takes every class under the directory of the unit tests whose file name ends in `Test`, the project's own classes among them, and the build checks that the name of a class with a JUnit test ends in `Test`. | The property `test.name`, `build.xml:74`, ChronitonDB chronitondb-sandbox at `34fdee9fd9`, with the value `*Test`. The target `test-latest`, `build.xml:1436`, ChronitonDB chronitondb-sandbox at `34fdee9fd9`, takes the files `**/${test.name}.java` under `test/unit` at line 1438, and the target `test`, `build.xml:1665`, ChronitonDB chronitondb-sandbox at `34fdee9fd9`, takes them at line 1667. The target `_check-test-names`, `build.xml:1091`, ChronitonDB chronitondb-sandbox at `34fdee9fd9`, checks at line 1092 the name of each class with a JUnit test against the pattern `.*Test$`. | The same lines in the base, Apache Cassandra cassandra-5.0 at `76550e9314`. In cassandra-5.0 at `3e3892ce99` the property at line 74, `test-latest` at line 1439 with its files at line 1441, `test` at line 1668 and the check at line 1092. In cassandra-6.0 at `243566b968` the property at line 74, `test-latest` at line 1723 with its files at line 1725, `test` at line 1954 and the check at line 1369. In trunk at `25cb50d1f7` the property at line 74, `test-latest` at line 1731 with its files at line 1733, `test` at line 1962 and the check at line 1377. Apache Cassandra has no class of the project, so the claim about the project's own classes is of the line only. |
