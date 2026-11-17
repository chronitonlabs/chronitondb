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

# 0009. The node uptime view shows the start time read once at start

| Field | Value |
|---|---|
| Document type | Record (ISO/IEC/IEEE 15289), MADR |
| Status | Accepted |
| Date | 2026-11-17 |
| Deciders | The maintainers |
| References | Issue #143, the feature spec in `docs/design/UPT-node-uptime-view/` |

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in BCP 14 (RFC 2119, RFC 8174) when, and only when, they appear in all capitals, as shown here.

## Contents

- [Context and problem statement](#context-and-problem-statement)
- [Considered options](#considered-options)
- [Decision outcome](#decision-outcome)
  - [Consequences](#consequences)
- [More information](#more-information)

## Context and problem statement

The node uptime view shows the start time of the node's process and its uptime. Both come from the JVM of the node, the source of the uptime `nodetool info` prints (`NodeProbe.getUptime`, `src/java/org/apache/cassandra/tools/NodeProbe.java:874`, ChronitonDB chronitondb-sandbox at `17e0b84a36`, the same in Apache Cassandra cassandra-5.0 at `41fb172e73`, and at line 942 in Apache Cassandra trunk at `1085b1823f`). The clock of a machine can be set back or forward while a node runs. The Java API documentation calls the start time of the JVM approximate, and how the JVM computes its uptime was not read. The feature had to know which start time the view shows after such a change of the clock.

## Considered options

1. The start time the node read once at start. It stays the same until the node restarts.
2. The clock of the node at the read, less the uptime. The start time and the uptime then always add up to the clock.

## Decision outcome

Chosen option: "The start time the node read once at start", because the start time then changes only when the node restarts, and a tool that compares two reads of it never sees a restart that did not happen.

The view MUST show, at every read, the start time the node read once from its JVM at start. The view MUST NOT work the start time out again from the clock. The reference page MUST say that after a change of the clock on a running node the start time plus the uptime can differ from the clock of the node.

### Consequences

- Good: a changed start time always means a restart.
- Good: the view holds no rule of its own for a clock that moves.
- Bad: after a change of the clock, the start time plus the uptime can differ from the clock of the node, and an operator who compares them has to know why.

## More information

The feature spec in `docs/design/UPT-node-uptime-view/feature-spec.md` applies this decision in FREQ-UPT-003 and FREQ-UPT-026 and in its section 2.2.
