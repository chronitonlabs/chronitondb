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

# 0015. A command of the node uptime view logs its change once the change is made

| Field | Value |
|---|---|
| Document type | Record (ISO/IEC/IEEE 15289), MADR |
| Status | Accepted |
| Date | 2026-11-17 |
| Deciders | The maintainers |
| References | Issue #144, the feature spec in `docs/design/UPTIM-node-uptime-view/`, decision records 0011 and 0013 |

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in BCP 14 (RFC 2119, RFC 8174) when, and only when, they appear in all capitals, as shown here.

## Contents

- [Context and problem statement](#context-and-problem-statement)
- [Considered options](#considered-options)
- [Decision outcome](#decision-outcome)
  - [Consequences](#consequences)
- [More information](#more-information)

## Context and problem statement

A nodetool command of the node uptime view that changes a node logs one INFO line with the name of the setting and its running value before and after. The draft of the feature spec logged that line before the command changed anything, with the value the command asked for. A step of the command can throw, and the feature does not undo the steps already done (decision record 0011). The log of such a node then held a change the node never made, and nothing in the log said that the command had failed. The feature spec had to know when the line is logged and what the log holds for a command that a step ended.

## Considered options

1. The INFO line is logged once the change is made, with the running value before and after the command. A command that a step ended logs one ERROR line in its place.
2. The INFO line is logged before the change, with the value the command asks for. A failed command is reported by nodetool only.

## Decision outcome

Chosen option: "The INFO line is logged once the change is made", because the log of a node then names only changes the node has made, and a command that failed leaves a line of its own.

When a command of the feature has made its change with no step that threw, the node MUST log one INFO line that holds the name `uptime_view_enabled`, the running value before the command and the running value after it.

If a step of a command of the feature throws, the node MUST log one ERROR line that holds the name `uptime_view_enabled` and the throwable, and MUST NOT log an INFO line for that command.

A command that is refused, and a command that finds the node as it asks for, log no line of the feature.

### Consequences

- Good: an INFO line of the feature always names a value the node has.
- Good: a command that a step ended is in the log of the node, and not only in the output of nodetool.
- Bad: the feature has two kinds of line for its commands.
- Bad: a `nodetool disableuptimeview` that brings a node back from between on and off can log the same value before and after. That happens where the command that failed had not yet set the running value.

## More information

The feature spec applies this decision in section 2.2, in the list of log lines of section 2.8 and in FREQ-UPTIM-014 and FREQ-UPTIM-046. Problem 6 of its section 4 names the tests. The start of a node logs neither line: a throwable from the start step is logged by Apache Cassandra's own start code.
