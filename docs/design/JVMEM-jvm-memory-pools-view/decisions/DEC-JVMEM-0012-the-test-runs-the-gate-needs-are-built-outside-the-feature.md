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

# DEC-JVMEM-0012. The test runs that the gate needs are built outside the feature

| Field | Value |
|---|---|
| Document type | Record (ISO/IEC/IEEE 15289), MADR |
| Status | Accepted |
| Date | 2026-11-22 |
| Deciders | The maintainers |
| References | Issue #161, the [delivery plan](../delivery-plan.md), the [plan](../plan.md), [additive.md](../../../process/additive.md#milestone-gates), [areas.md](../../../process/areas.md), [classification.md](../../../process/classification.md#size), [PRINCIPLE-054](../../../process/principles.md#principle-054) |
| Areas | observability, build-and-test |
| Supersedes | None |

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in BCP 14 (RFC 2119, RFC 8174) when, and only when, they appear in all capitals, as shown here.

## Contents

- [Context and problem statement](#context-and-problem-statement)
- [Considered options](#considered-options)
- [Decision outcome](#decision-outcome)
  - [Consequences](#consequences)
- [More information](#more-information)

## Context and problem statement

The JVM memory pools view is delivered in one milestone, which is its final one. The continuous integration that a milestone gate needs is in place before the final milestone of a feature, and the report of a final milestone recommends no-go without it ([additive.md](../../../process/additive.md#milestone-gates)).

The gate of this milestone needs two parts of continuous integration. Section 6 of the [delivery plan](../delivery-plan.md#6-test-plan) names them:

1. A run of the project's own unit tests and of its own in-JVM distributed tests, on a pull request to the line and on the line itself.
2. A run of the tests of Apache Cassandra that the delivery plan names, unchanged, on the line.

Neither part exists on the line. Fact C in section 6 of the delivery plan gives the workflow files that were read, with the tree they were read in: no workflow of the line runs a test target of the build. The repository holds no plan for either part.

A workflow of the project is work of the area `build-and-test` ([areas.md](../../../process/areas.md)). The feature works in the area `observability` and its reach is one area. The feature spec plans one build item and one validation item.

The question was who builds the two parts.

## Considered options

1. The maintainers, as work of its own. The two parts are planned and opened outside the feature, in the area `build-and-test`.
2. The feature, as a third item of its plan. The feature then works in two areas, so its reach becomes cross-cutting ([classification.md](../../../process/classification.md#size)), and the feature spec changes, because it plans two items.

## Decision outcome

Chosen option: "The maintainers, as work of its own", because the feature then stays in its one area with nothing added to it ([PRINCIPLE-054](../../../process/principles.md#principle-054)). A view of one class and one hook does not need a workflow of its own, and a workflow that runs the tests of the line is not part of what the view delivers.

1. The two parts of continuous integration that section 6 of the delivery plan names MUST NOT be items of this feature. The maintainers plan and open them as work of its own on the line, in the area `build-and-test`.
2. The plan of the feature keeps its two items, and the reach of the feature stays one area.
3. The gate of milestone 1 waits for both parts. The milestone report MUST NOT recommend go before both parts exist and the tests of exit criteria 2, 3 and 5 of the delivery plan have run in them, which is exit criterion 10.
4. This record decides who builds the two parts, and nothing else. [DEC-JVMEM-0013](DEC-JVMEM-0013-the-view-stays-at-normal-risk-and-the-runs-of-its-two-tests-are-named.md) decides in which runs the two tests that catch the faults of the view pass before the first part exists.

### Consequences

- Good: the feature stays one view class, one hook and their tests, in one area, with the checks and the review of its class.
- Good: this decision makes neither item of the feature wait. The delivery plan sets the order of the items.
- Bad: the gate of the feature waits for work that has no plan yet, and so does the release that ships the view as a finished feature.
- Bad: if item 2 is merged before both parts exist, the milestone report recommends no-go, which is re-plan trigger 8 of the delivery plan.

## More information

- The [delivery plan](../delivery-plan.md): exit criterion 10 of milestone 1, re-plan trigger 8, and in section 6 the two parts and fact C.
- [additive.md](../../../process/additive.md#milestone-gates): what the gate of a final milestone needs.
