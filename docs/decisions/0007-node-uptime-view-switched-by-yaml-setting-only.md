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

# 0007. The node uptime view is switched by its yaml setting only

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

The node uptime view is a virtual table that shows the start time and the uptime of the node a client is connected to. The switch rules ask for a yaml setting and a nodetool toggle for every fork feature. Apache Cassandra builds the table list of `system_views` once, at start, and registers it once (`SystemViewsKeyspace.SystemViewsKeyspace`, `src/java/org/apache/cassandra/db/virtual/SystemViewsKeyspace.java:30`, and `CassandraDaemon.setupVirtualKeyspaces`, `src/java/org/apache/cassandra/service/CassandraDaemon.java:534`, ChronitonDB chronitondb-sandbox at `17e0b84a36`, the same in Apache Cassandra cassandra-5.0 at `41fb172e73`). A toggle would have to change that list on a running node, under statements that are being executed. Its commands and its MBean would also exist on every node, also on a node that never turns the view on. The feature had to know whether the view has a nodetool toggle.

## Considered options

1. The yaml setting only. The node reads it at start, and a change needs a restart of the node.
2. The yaml setting and a nodetool toggle that changes the running value.

## Decision outcome

Chosen option: "The yaml setting only", because a node with the view off then differs from Apache Cassandra by one row of its settings table and nothing else, and the table list of a running node never changes.

The view MUST be switched by the yaml setting `uptime_view_enabled` only, which the node reads at start. The feature MUST NOT add a nodetool command, or an MBean that reads or changes the switch. The state of the view on a node MUST NOT change while the node runs. The reference page MUST say that a change of the setting needs a restart of the node.

One thing is accepted on every node, whatever the setting says: `system_views.settings` and the start log line that prints the configuration show the setting, because Apache Cassandra lists every field of its configuration (`SettingsTable.getProperties`, `src/java/org/apache/cassandra/db/virtual/SettingsTable.java:151`, and `Config.log`, `src/java/org/apache/cassandra/config/Config.java:1347`, ChronitonDB chronitondb-sandbox at `17e0b84a36`, the same in Apache Cassandra cassandra-5.0 at `41fb172e73`).

This is a departure from the rule that every fork feature has a yaml setting and a nodetool toggle, made for this view only.

### Consequences

- Good: a node with the view off holds no command and no MBean of the feature.
- Good: nothing registers virtual tables on a running node.
- Bad: an operator who wants to show or hide the view restarts the node.
- Bad: a node with the view off still shows one more row in its settings table than Apache Cassandra.

## More information

The feature spec in `docs/design/UPT-node-uptime-view/feature-spec.md` applies this decision in FREQ-UPT-010, FREQ-UPT-011 and FREQ-UPT-024 and in its section 2.8.
