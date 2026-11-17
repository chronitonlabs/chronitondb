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

# 0010. A hidden node uptime view answers as a table that does not exist

| Field | Value |
|---|---|
| Document type | Record (ISO/IEC/IEEE 15289), MADR |
| Status | Accepted |
| Date | 2026-11-17 |
| Deciders | The maintainers |
| References | Issue #143, the feature spec in `docs/design/UPT-node-uptime-view/`, [branching-and-review.md, Feature switches and defaults](../process/branching-and-review.md#feature-switches-and-defaults), [quality-requirements.md](../process/quality-requirements.md) |

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in BCP 14 (RFC 2119, RFC 8174) when, and only when, they appear in all capitals, as shown here.

## Contents

- [Context and problem statement](#context-and-problem-statement)
- [Considered options](#considered-options)
- [Decision outcome](#decision-outcome)
  - [Consequences](#consequences)
- [More information](#more-information)

## Context and problem statement

The node uptime view is a table that exists only while its switch is on. The switch rules and the quality checklist say that a feature's syntax, with the feature off, is refused with an error that names the switch. The view has no syntax of its own: it is read with an ordinary `SELECT`. Apache Cassandra answers a statement on a table a keyspace does not hold with `table <name> does not exist` (`Schema.validateTable`, `src/java/org/apache/cassandra/schema/Schema.java:429`, ChronitonDB chronitondb-sandbox at `17e0b84a36`, the same in Apache Cassandra cassandra-5.0 at `41fb172e73`). An error that names the switch would need a change to that table lookup, which every statement uses, and a node with the view off would then answer differently from Apache Cassandra. The feature had to know what a statement that names the view gets while the view is off.

## Considered options

1. The Apache Cassandra answer for a table that does not exist. The view is absent while off, and no Apache Cassandra code changes.
2. An error that names the yaml setting, raised from a hook in the table lookup.

## Decision outcome

Chosen option: "The Apache Cassandra answer for a table that does not exist", because a node with the view off then answers and lists its tables exactly as Apache Cassandra does, and the table lookup stays untouched.

While the view is hidden, a statement that names it MUST get the answer Apache Cassandra gives the same statement for a table that `system_views` does not hold. The answer MUST NOT name the switch. The table listings of the node MUST NOT show the view. The reference page MUST name the switch as the way to show the view. This is a departure from the rule that a feature's syntax is refused with an error that names the switch, made for this view only.

### Consequences

- Good: with the view off, CQL answers and listings are the ones of Apache Cassandra, and no hook is added to the table lookup.
- Bad: an operator who reads the view on a node where it is off sees only that the table does not exist, and has to know from the documentation that a switch shows it.

## More information

The feature spec in `docs/design/UPT-node-uptime-view/feature-spec.md` applies this decision in FREQ-UPT-016 and FREQ-UPT-017 and in its section 2.8.
