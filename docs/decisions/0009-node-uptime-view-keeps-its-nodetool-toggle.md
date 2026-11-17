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

# 0009. The node uptime view keeps its nodetool toggle

| Field | Value |
|---|---|
| Document type | Record (ISO/IEC/IEEE 15289), MADR |
| Status | Accepted |
| Date | 2026-11-17 |
| Deciders | The maintainers |
| References | Issue #144, the feature spec in `docs/design/UPTIM-node-uptime-view/`, [branching-and-review.md, Feature switches and defaults](../process/branching-and-review.md#feature-switches-and-defaults) |

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in BCP 14 (RFC 2119, RFC 8174) when, and only when, they appear in all capitals, as shown here.

## Contents

- [Context and problem statement](#context-and-problem-statement)
- [Considered options](#considered-options)
- [Decision outcome](#decision-outcome)
  - [Consequences](#consequences)
- [More information](#more-information)

## Context and problem statement

The switch rules ask two things of every feature. Item 1 asks for a yaml setting and a nodetool toggle. Item 7 asks that with the feature off the line behaves exactly as Apache Cassandra. For the node uptime view the two cannot both hold in full. A toggle that can turn the view on has to exist while the view is off: the field of the setting, the two nodetool commands and the MBean they call. So every node of a build that holds the feature differs from Apache Cassandra in these parts, whatever the switch says. The feature spec had to know whether that is accepted.

## Considered options

1. The yaml setting and the two nodetool commands, `enableuptimeview` and `disableuptimeview`.
2. The yaml setting only, read at start.

## Decision outcome

Chosen option: "The yaml setting and the two nodetool commands", because an operator then turns the view on and off on a running node, with no restart.

The switch of the node uptime view MUST be the yaml setting `uptime_view_enabled` together with the two nodetool commands `enableuptimeview` and `disableuptimeview`.

Every node of a build that holds the feature MAY differ from Apache Cassandra in these three parts, whatever the switch says:

1. One row for `uptime_view_enabled` in `system_views.settings`, and the name of the setting in the start log line that prints the configuration.
2. The two commands in the output of `nodetool help`.
3. One MBean, `org.chronitondb.uptime:type=UptimeView`.

Section 2.8 of the feature spec says in full by what a node whose view is off differs from Apache Cassandra, its log lines included. Any other difference is a fault.

### Consequences

- Good: the view is turned on and off with no restart, which is when an operator in a rolling restart needs it.
- Good: the feature follows item 1 of the switch rules as written.
- Bad: every node of the build shows a settings row, two commands and one MBean of a feature it may never use.
- Bad: a toggle on a running node brings a switch change that can fail part way. Decision record 0011 says what the node does then.

## More information

The feature spec applies this decision in section 2.2 and in section 2.8. Problem 7 of its section 4 names the test that reads the settings rows, the nodetool commands and the MBean names of a node whose view is off.
