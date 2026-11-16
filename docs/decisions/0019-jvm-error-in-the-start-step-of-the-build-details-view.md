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

# 0019. A JVM error in the start step of the build details view is handled as Apache Cassandra handles it

| Field | Value |
|---|---|
| Document type | Record (ISO/IEC/IEEE 15289), MADR |
| Status | Superseded by 0022 |
| Date | 2026-11-16 |
| Deciders | The maintainers |
| References | Issue #141, the feature spec in `docs/design/BUILD-build-details-view/`, decision record 0016 |

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in BCP 14 (RFC 2119, RFC 8174) when, and only when, they appear in all capitals, as shown here.

## Contents

- [Context and problem statement](#context-and-problem-statement)
- [Considered options](#considered-options)
- [Decision outcome](#decision-outcome)
  - [Consequences](#consequences)
- [More information](#more-information)

## Context and problem statement

Decision record 0016 says that a node goes on with its start, with the build details view hidden, when the start step of the view fails. Apache Cassandra's own start code does not treat every fault alike. Where it catches a throwable and goes on, it first hands the throwable to its JVM stability check, `JVMStabilityInspector.inspectThrowable`. That check throws an `OutOfMemoryError` again, throws for an interrupt, and stops the JVM for a state it rates unstable. The feature had to know whether such a fault in the start step of the view stops the start of the node, or is kept in like any other fault.

## Considered options

1. The start step hands each throwable it catches to Apache Cassandra's JVM stability check first, as Apache Cassandra's own start code does.
2. The start step keeps every throwable in, and the node goes on with its start.

## Decision outcome

Chosen option: "The start step hands each throwable it catches to Apache Cassandra's JVM stability check first, as Apache Cassandra's own start code does", because a node then never goes on to serve reads and writes in a JVM that Apache Cassandra would have stopped.

Each guard of the start step of the view MUST hand a throwable it catches to `JVMStabilityInspector.inspectThrowable` before it does anything else with it. When that call returns, decision record 0016 applies: the start step undoes what it did, logs its ERROR line and returns normally. When that call does not return, the node handles the throwable as Apache Cassandra handles the same throwable anywhere else in its start, and the start step MUST NOT keep it in.

This narrows decision record 0016 to a throwable that the JVM stability check returns from. Decision record 0016 stays in force for every such throwable.

### Consequences

- Good: out of memory, an interrupt and an unstable state are handled in the start step as in the rest of Apache Cassandra's start.
- Good: the start step adds no rule of its own for what an unstable JVM is.
- Bad: on a node whose configuration turns the view on, out of memory in the start step of the view stops the start of the node.
- Bad: a JVM error of another kind that leaves Apache Cassandra's registration call can leave the table id of the view in the registry of a node that hides the view. No CQL statement, listing or grant reaches the view through that id.

## More information

Decision record 0022 supersedes this record. The start step of the view has no guard any more, so it hands no throwable to the JVM stability check: every throwable ends the start of the node.
