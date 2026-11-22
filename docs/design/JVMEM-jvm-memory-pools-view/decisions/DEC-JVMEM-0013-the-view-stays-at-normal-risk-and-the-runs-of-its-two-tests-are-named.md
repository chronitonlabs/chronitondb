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

# DEC-JVMEM-0013. The JVM memory pools view stays at Normal risk, and the runs of its two tests are named

| Field | Value |
|---|---|
| Document type | Record (ISO/IEC/IEEE 15289), MADR |
| Status | Accepted |
| Date | 2026-11-22 |
| Deciders | The maintainers |
| References | Issue #161, the [feature spec](../feature-spec.md), the [delivery plan](../delivery-plan.md), the [plan](../plan.md), [DEC-JVMEM-0012](DEC-JVMEM-0012-the-test-runs-the-gate-needs-are-built-outside-the-feature.md), [classification.md](../../../process/classification.md#risk), [testing.md](../../../process/testing.md#when-each-test-runs), [PRINCIPLE-054](../../../process/principles.md#principle-054), [PRINCIPLE-069](../../../process/principles.md#principle-069), [PRINCIPLE-072](../../../process/principles.md#principle-072) |
| Areas | observability |
| Supersedes | DEC-JVMEM-0003 |

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in BCP 14 (RFC 2119, RFC 8174) when, and only when, they appear in all capitals, as shown here.

## Contents

- [Context and problem statement](#context-and-problem-statement)
- [Considered options](#considered-options)
- [Decision outcome](#decision-outcome)
  - [Consequences](#consequences)
- [More information](#more-information)

## Context and problem statement

This record replaces DEC-JVMEM-0003. That record kept the work on the JVM memory pools view at Normal risk and named two faults of the view that the class table of [classification.md](../../../process/classification.md#risk) rates Critical. This record keeps the class and the two faults. It changes one rule of that record: where the two tests that catch the faults run.

The two faults are these.

1. **A wrong value.** The view could show a size, a type or a set of pools that is not what the JVM reports. The class table rates an incorrect response as a Correctness fault of Critical risk.
2. **A node that does not start.** Apache Cassandra builds the tables of `system_views` once, when a node starts: `CassandraDaemon.setupVirtualKeyspaces`, `src/java/org/apache/cassandra/service/CassandraDaemon.java:534`, ChronitonDB chronitondb-sandbox at `34fdee9fd9`, registers `SystemViewsKeyspace.instance` at line 537. The same code stands at the same lines in the base of the line, Apache Cassandra cassandra-5.0 at `76550e9314`, and in cassandra-5.0 at `3e3892ce99`, and at lines 641 and 644 in Apache Cassandra cassandra-6.0 at `243566b968` and trunk at `25cb50d1f7`. The feature adds its view class to that list. A view class whose constructor or static initialiser throws would stop that step on every node that runs the release. The class table rates a node that is unavailable as an Availability fault of Critical risk.

Two tests catch them: a test that starts a node and reads the view, and a test that compares the view with the memory pools of the same JVM. Item 3 of the outcome of DEC-JVMEM-0003 had both run on every build of the feature, and the reason of that record for Normal risk was that no such fault could then pass a build unseen.

The line cannot meet that rule as written. No workflow of the line runs a test target of the build, which is fact C in section 6 of the [delivery plan](../delivery-plan.md#6-test-plan). The gate of the feature needs two parts of continuous integration, and the first of them runs the project's own tests on each pull request to the line and on the line itself. [DEC-JVMEM-0012](DEC-JVMEM-0012-the-test-runs-the-gate-needs-are-built-outside-the-feature.md) decides that both parts are built outside the feature and that the items of the feature do not wait for them. Until the first part exists, the two tests run where the work of the feature runs them: before each commit of its two items, and at its gate. A pull request of other work that is merged to the line after item 1 makes a build of the line that holds the view, and nothing runs the two tests on that build.

Both tests are unit tests of the feature, as section 4.1 of the [feature spec](../feature-spec.md) plans them. A full run of a unit test target of the build takes every unit test class, the project's own among them, which is fact J in section 6 of the delivery plan. So two runs that the process already has hold both tests: the full test suites before an import from Apache Cassandra is merged, and the full test suites of a release candidate before its promotion ([testing.md](../../../process/testing.md#when-each-test-runs)).

The question was whether a merge of other work may go without the two tests until the first part of continuous integration exists, or whether item 1 waits for that part.

## Considered options

1. The runs are named. The two tests run in the runs that this record names. Until the first part of continuous integration exists, a merge of other work of the project goes without them.
2. DEC-JVMEM-0003 stands as written. Item 1 waits until the first part of continuous integration is merged on the line, so that every pull request and the line itself get both tests from the first commit of item 1 on.

## Decision outcome

Chosen option: "The runs are named", because the feature then does not wait for work that has no plan yet ([PRINCIPLE-054](../../../process/principles.md#principle-054)), and because what can go unseen meanwhile is bounded. The view stores nothing and sends nothing, so neither fault can damage data or reach another node. A fault that a merge of other work brings to the view is found by the next run that holds both tests, and the feature is not finished before both tests have passed in continuous integration.

1. The work on the JVM memory pools view stays at Normal risk. The label on the issue is not changed.
2. The feature spec MUST name both faults in its Risk row and in its section on where problems could occur, each with the test that catches it.
3. The test that starts a node and reads the view, and the test that compares the view with the memory pools of the same JVM, MUST pass in each of these runs:
   1. The test run before each commit of the pull request of an item of the feature, from the commit that adds the view to the tables of `system_views` on. A commit before that one builds no node that holds the view.
   2. The run of the tests of the feature on the line at the gate of its final milestone.
   3. Each run of the first part of continuous integration, on a pull request to the line and on the line itself, from the day that part exists.
4. Until the first part of continuous integration exists, a pull request of other work of the project, which is no import from Apache Cassandra, MAY be merged to the line with no run of the two tests.
5. This record changes nothing of the gate. Item 3 of the outcome of [DEC-JVMEM-0012](DEC-JVMEM-0012-the-test-runs-the-gate-needs-are-built-outside-the-feature.md) holds it to both parts of continuous integration.
6. This is a departure from the Correctness and Availability rows of the class table in [classification.md](../../../process/classification.md#risk), made for this view only. It changes no rule of that page, and the class of other work is decided by its own facts.

### Consequences

- Good: item 1 and item 2 are designed, built, reviewed and merged without waiting for continuous integration.
- Good: the spec, the plan and the code follow the Normal path, with the checks and the review of that class, which fit one read only view.
- Good: every build that a pull request of the feature makes from the hook on has both tests, and so has the gate.
- Bad: until the first part of continuous integration exists, a fault that a merge of other work brings to the view is not found at that merge. A wrong value, or a view class that stops the start of a node, then stays on the line until the next run of item 3, the next full run before an import, or the test run of a later change that touches the view class or the hook file. No release candidate of the line is promoted without the full test suites, which hold both tests.
- Bad: no requirement can exclude a fault in the constructor of the view class. Only the tests show that it is absent on the builds they run on.
- Bad: the class of this work differs from what the class table says for an incorrect response and for a node that is unavailable, so the table cannot be read alone for this feature.

## More information

- The [delivery plan](../delivery-plan.md): exit criterion 4 of milestone 1, and in section 6 the entries on where the two tests run, with facts C and J.
- The [plan](../plan.md): criterion 26 of item 1 and criterion 25 of item 2, which put both tests into the test run before each commit.
- The [feature spec](../feature-spec.md): its Risk row, and problems 1 and 2 of section 4 with their tests in section 4.1. The feature spec cites DEC-JVMEM-0003 in its References row, its Risk row, section 10 and section 11. It is an approved document, so it is brought to this record through change control, in a pull request of its own that cites this record, and work that depends on the changed text waits for that pull request ([additive.md](../../../process/additive.md#change-control-after-a-merge)).
- [PRINCIPLE-069](../../../process/principles.md#principle-069): the risk of a change is the worst it could cause, and a maintainer may change the class of a change at any time.
