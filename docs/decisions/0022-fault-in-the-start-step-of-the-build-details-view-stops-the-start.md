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

# 0022. A fault in the start step of the build details view stops the start of the node

| Field | Value |
|---|---|
| Document type | Record (ISO/IEC/IEEE 15289), MADR |
| Status | Accepted |
| Date | 2026-11-16 |
| Deciders | The maintainers |
| References | Issue #141, the feature spec in `docs/design/BUILD-build-details-view/`, [classification.md](../process/classification.md), decision records 0010, 0013, 0016, 0017 and 0019 |

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in BCP 14 (RFC 2119, RFC 8174) when, and only when, they appear in all capitals, as shown here.

## Contents

- [Context and problem statement](#context-and-problem-statement)
- [Considered options](#considered-options)
- [Decision outcome](#decision-outcome)
  - [Consequences](#consequences)
- [More information](#more-information)

## Context and problem statement

Decision record 0016 chose that a node goes on with its start, with the build details view hidden, when the start step of the view fails. Decision record 0019 narrowed that to a throwable that Apache Cassandra's JVM stability check returns from. That design needs a guard around the start step, an undo of what the step did, and a rule for a fault in the undo and in each log call. It could not be closed. The registry of virtual keyspaces on this line has no call that takes a table id out once a registration wrote it, so an undo after a fault inside the registration can never be complete. Each guard added to cover one case also needed an answer for its own fault.

Apache Cassandra registers its own virtual keyspaces at start with no guard around the call. A throwable there ends the start of the node.

The feature had to choose again what a node does when the start step of the view hits a fault. Decision record 0017 kept the work at Normal risk on the ground that a start step lets no throwable out, so the class of the work had to be settled again with the answer.

## Considered options

1. The start step catches no throwable. The node ends its start, as for a fault in the registration of Apache Cassandra's own virtual keyspaces.
2. The start step keeps its guards and its undo, and the feature accepts the cases they leave open.
3. The feature is stopped.

## Decision outcome

Chosen option: "The start step catches no throwable. The node ends its start, as for a fault in the registration of Apache Cassandra's own virtual keyspaces", because the start step then needs no guard and no undo, so no node that finished its start holds a view that is partly registered, and a node treats a fault of the view as it treats a fault of Apache Cassandra's own virtual keyspaces.

The start step of the view MUST NOT catch a throwable that is thrown in it. On a node whose configuration turns the view on, a throwable in the start step therefore ends the start of the node. The feature MUST NOT add a log line, a metric or a setting of its own for such a fault. The log line is the one Apache Cassandra writes, `Exception encountered during startup`, with the throwable.

The start step MUST still return right after it read the setting as `false`, so a node whose configuration leaves the view off runs no other code of the feature at start. A node that a fault in the start step stopped therefore starts without the view once the setting is removed from its `cassandra.yaml` or set to `false`. The reference page of the feature MUST say what a throwable in the start step does and give that way back.

Decision record 0013 is not changed: a node whose configuration turns the view on before the final gate registers nothing, logs its warning and does not refuse to start because of the setting.

The work on the build details view stays at Normal risk, and the label on the issue is not changed. The feature spec MUST name two faults in its Risk row and in its section on where problems could occur. The first is a fault in what every node runs at start, the hook line and the read of the setting, which the requirements of the feature keep down to the load of one class and the read of one boolean field. The second is the stop of the start that this record chooses for a node whose configuration turns the view on. [classification.md](../process/classification.md) rates a node that does not start as an Availability fault of Critical risk. Keeping Normal risk is a departure from that row of its class table, made for this feature only.

This record supersedes decision records 0016, 0017 and 0019.

### Consequences

- Good: the start step is a few steps in a row, with no guard, no undo and no state between shown and hidden on a node that finished its start.
- Good: a fault of the view is handled as a fault of Apache Cassandra's own virtual keyspaces is, by Apache Cassandra's own code.
- Good: the fault cannot be missed. The node does not start, and its log holds the throwable.
- Good: the feature no longer departs from the rule on automatic fallbacks in quality-requirements.md, since no fallback is left.
- Bad: on a node whose configuration turns the view on, a fault of one read-only table keeps the node down until the fault is fixed or the setting is removed from its `cassandra.yaml`.
- Bad: a fault that every node of a cluster shares stops each node that is restarted with the view on. A rolling restart shows it on the first node.
- Bad: the class of this work differs from what the class table says for a node that does not start, so the table cannot be read alone for this feature.

## More information

The feature spec in `docs/design/BUILD-build-details-view/feature-spec.md` applies this decision in FREQ-BUILD-027, FREQ-BUILD-028 and FREQ-BUILD-037, in its Risk row, in its sections 2.2 and 9, and in problem 1 of its section 4.

The code read for this decision, in ChronitonDB chronitondb-sandbox at `17e0b84a36`:

1. Apache Cassandra calls the registration of its virtual keyspaces at start with no guard: `CassandraDaemon.setup`, `src/java/org/apache/cassandra/service/CassandraDaemon.java:229`, the call at line 291.
2. A throwable that leaves the start code is logged and the node exits: `CassandraDaemon.activate`, `src/java/org/apache/cassandra/service/CassandraDaemon.java:718`, the catch at line 746 and the call of `exitOrFail` at line 759.
3. Registering a keyspace writes the id of each of its tables, and the registry has no call that takes one out: `VirtualKeyspaceRegistry.register`, `src/java/org/apache/cassandra/db/virtual/VirtualKeyspaceRegistry.java:41`.

Apache Cassandra cassandra-6.0 at `383ed3c5ad` and trunk at `30b73cadf3` keep the first two: `CassandraDaemon.setup`, `CassandraDaemon.java:244`, the call at line 331, and `CassandraDaemon.activate` at line 833, the catch at line 861. There the registry has a call that takes a keyspace and the ids of its tables out, `VirtualKeyspaceRegistry.unregister`, `VirtualKeyspaceRegistry.java:51`.
