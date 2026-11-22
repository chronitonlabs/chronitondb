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

# DEC-JVMEM-0003. The JVM memory pools view stays at Normal risk with two faults named

| Field | Value |
|---|---|
| Document type | Record (ISO/IEC/IEEE 15289), MADR |
| Status | Superseded by DEC-JVMEM-0013 |
| Date | 2026-11-20 |
| Deciders | The maintainers |
| References | Issue #161, the [feature spec](../feature-spec.md), [classification.md](../../../process/classification.md#risk), [PRINCIPLE-069](../../../process/principles.md#principle-069), [PRINCIPLE-072](../../../process/principles.md#principle-072) |
| Areas | observability |
| Supersedes | None |

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in BCP 14 (RFC 2119, RFC 8174) when, and only when, they appear in all capitals, as shown here.

## Contents

- [Context and problem statement](#context-and-problem-statement)
- [Considered options](#considered-options)
- [Decision outcome](#decision-outcome)
  - [Consequences](#consequences)
- [More information](#more-information)

## Context and problem statement

The work on the JVM memory pools view is labelled Normal risk. The reason of the label is that the view is a new virtual table, which is a public interface, and that the worst the view was expected to cause is a read that fails.

Two faults of the view go beyond that reason. The class table of [classification.md](../../../process/classification.md#risk) rates each of them Critical.

1. **A wrong value.** The view could show a size, a type or a set of pools that is not what the JVM reports. The class table rates an incorrect response as a Correctness fault of Critical risk.
2. **A node that does not start.** Apache Cassandra builds the tables of `system_views` once, when a node starts: `CassandraDaemon.setupVirtualKeyspaces`, `src/java/org/apache/cassandra/service/CassandraDaemon.java:534`, ChronitonDB chronitondb-sandbox at `ffa1bc742d`, registers `SystemViewsKeyspace.instance` at line 537. The same code stands at the same lines in Apache Cassandra cassandra-5.0 at `76550e9314`, the base of the line, and at `47227d98bf`, and at lines 641 and 644 in Apache Cassandra cassandra-6.0 at `a02931dea8` and trunk at `45c325a01b`. The feature adds its view class to that list. A view class whose constructor or static initialiser throws would stop that step on every node that runs the release. The class table rates a node that is unavailable as an Availability fault of Critical risk.

The class decides the depth of the checks and of the review, so it had to be settled with both faults named.

## Considered options

1. Normal risk, as labelled. The feature spec names both faults with the tests that catch them.
2. Critical risk. The checks of the spec end by the Critical rule, every review checklist applies, and the security engineer reviews every code pull request.

## Decision outcome

Chosen option: "Normal risk, as labelled", because the view stores nothing and sends nothing, so neither fault can damage data or reach another node, and both are caught by tests that run on every build. The view reads values the JVM holds and writes none. A wrong value misleads the operator who reads the view and changes nothing a node does. A view class that stops the start fails every test that starts a node, so such a fault cannot pass the build unseen.

1. The work on the JVM memory pools view stays at Normal risk. The label on the issue is not changed.
2. The feature spec MUST name both faults in its Risk row and in its section on where problems could occur, each with the test that catches it.
3. A test that starts a node and reads the view, and a test that compares the view with the memory pools of the same JVM, MUST run on every build of the feature.
4. This is a departure from the Correctness and Availability rows of the class table in [classification.md](../../../process/classification.md#risk), made for this view only. It changes no rule of that page, and the class of other work is decided by its own facts.

### Consequences

- Good: the spec, the plan and the code follow the Normal path, with the checks and the review of that class, which fit one read only view.
- Good: both faults are named where the maintainers and the reviewer read the class, with their tests.
- Bad: no requirement can exclude a fault in the constructor of the view class. Only the tests show that it is absent on the builds they run on.
- Bad: the class of this work differs from what the class table says for an incorrect response and for a node that is unavailable, so the table cannot be read alone for this feature.

## More information

- The [feature spec](../feature-spec.md), its Risk row, and problems 1 and 2 of section 4 with their tests in section 4.1.
- [PRINCIPLE-069](../../../process/principles.md#principle-069): the risk of a change is the worst it could cause, and a maintainer may change the class of a change at any time.
