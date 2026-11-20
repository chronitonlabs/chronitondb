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

# DEC-JVMEM-0001. The JVM memory pools view has no switch and is not held back

| Field | Value |
|---|---|
| Document type | Record (ISO/IEC/IEEE 15289), MADR |
| Status | Accepted |
| Date | 2026-11-20 |
| Deciders | The maintainers |
| References | Issue #161, the [feature spec](../feature-spec.md), [PRINCIPLE-003](../../../process/principles.md#principle-003), [PRINCIPLE-016](../../../process/principles.md#principle-016), [PRINCIPLE-089](../../../process/principles.md#principle-089) |
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

The feature adds one read only virtual table to `system_views`, a keyspace that Apache Cassandra defines in code. Two rules of the project read differently for such a table.

[PRINCIPLE-003](../../../process/principles.md#principle-003) and the edge of [PRINCIPLE-089](../../../process/principles.md#principle-089) say that a definition the project adds to a keyspace that Apache Cassandra defines in code is added only by a feature that is held back until every node has it. Read by the letter, the view would ship off behind a switch.

[PRINCIPLE-016](../../../process/principles.md#principle-016) holds a feature back when it sends, gossips, streams or commits something a node without it cannot read. It gives any other purely additive feature a switch only when something needs the feature turned off. The view does none of the four, and nothing needs it turned off.

The question was which of the two decides for this view.

## Considered options

1. No switch. The view is present on every node that runs a release with the feature, from startup.
2. Held back. The view ships off behind a node switch, and an operator turns it on after every node is upgraded.

## Decision outcome

Chosen option: "No switch", because nodes share nothing of the view. A hold back protects a node from state it cannot read, and the view gives no node such state.

1. A virtual keyspace is kept in two maps of the node's own registry: `VirtualKeyspaceRegistry.register`, `src/java/org/apache/cassandra/db/virtual/VirtualKeyspaceRegistry.java:41`, ChronitonDB chronitondb-sandbox at `ffa1bc742d`. The same code stands at the same line in Apache Cassandra cassandra-5.0 at `76550e9314`, the base of the line, and at `47227d98bf`, and at line 42 in Apache Cassandra cassandra-6.0 at `a02931dea8` and trunk at `45c325a01b`.
2. The definition of the view is built in the memory of each node at startup. It is not written to the schema tables, to a data file or to the commit log, and no node sends it to another.
3. A read of all rows of the view is answered by the node that receives it, with no message to another node: `PartitionRangeReadCommand.VirtualTablePartitionRangeReadCommand.execute`, `src/java/org/apache/cassandra/db/PartitionRangeReadCommand.java:547`, ChronitonDB chronitondb-sandbox at `ffa1bc742d`. The same code stands at the same line in Apache Cassandra cassandra-5.0 at `76550e9314` and at `47227d98bf`, and at line 646 in Apache Cassandra cassandra-6.0 at `a02931dea8` and trunk at `45c325a01b`.

The decision binds as follows.

1. The view MUST be present on every node that runs a release with the feature, from startup.
2. The feature MUST NOT add a setting, a command or any other switch for the view.
3. This record decides for this view only. It changes no principle, and another definition in a keyspace that Apache Cassandra defines in code is decided by its own record.

### Consequences

- Good: an operator has nothing to set and nothing to turn on, and the feature has no off state to build, test or document.
- Good: the view answers on each node from the moment that node runs the release, during a rolling upgrade too.
- Bad: while some nodes do not have the view yet, a read sent to such a node is refused as a read of a table that does not exist. The feature spec states this in its compatibility section.
- Bad: an operator cannot hide the view on one node. Who may read it is set by grants alone.
- Bad: a grant an operator gives on the view by name is a row of the auth tables that names the view. Apache Cassandra writes that row in its own form, and the steps for moving back name its removal.

## More information

- The [feature spec](../feature-spec.md), section 2.8 for the feature class, and section 7 for a cluster with nodes on different releases and for moving back.
- [PRINCIPLE-017](../../../process/principles.md#principle-017): a purely additive feature is on by default.
