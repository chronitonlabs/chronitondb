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

# 0007. A node starts with the node uptime view off when its configuration turns the view on before the final gate

| Field | Value |
|---|---|
| Document type | Record (ISO/IEC/IEEE 15289), MADR |
| Status | Accepted |
| Date | 2026-11-17 |
| Deciders | The maintainers |
| References | Issue #144, the feature spec in `docs/design/UPTIM-node-uptime-view/`, [branching-and-review.md, Feature switches and defaults](../process/branching-and-review.md#feature-switches-and-defaults), [additive.md, Milestone gates](../process/additive.md#milestone-gates) |

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in BCP 14 (RFC 2119, RFC 8174) when, and only when, they appear in all capitals, as shown here.

## Contents

- [Context and problem statement](#context-and-problem-statement)
- [Considered options](#considered-options)
- [Decision outcome](#decision-outcome)
  - [Consequences](#consequences)
- [More information](#more-information)

## Context and problem statement

The switch rules say that before a feature's final milestone gate its switch refuses to turn on, whatever its default. The node uptime view has a yaml setting, `uptime_view_enabled`, and two nodetool commands. A build cut between two merged items of the feature is a build before the final gate. The rules name no form for the refusal when a node of such a build starts with the setting `true` in its `cassandra.yaml`. The feature spec had to know what that node does.

## Considered options

1. The node starts, keeps the view off and logs one warning that names the setting.
2. The node refuses to start, with an error that names the setting.

## Decision outcome

Chosen option: "The node starts, keeps the view off and logs one warning that names the setting", because a setting for a read-only view then never keeps a node down.

If a node starts with `uptime_view_enabled` set to `true` before the feature's final milestone gate, the node MUST finish its start with the view off. It MUST log one WARN line that names `uptime_view_enabled`. It MUST NOT refuse to start because of the setting.

Before the final gate, `nodetool enableuptimeview` MUST be refused with an error, and the view MUST stay off.

The feature does not change the value the node loaded. On such a node the row of `uptime_view_enabled` in `system_views.settings` shows `true` while the view is off.

### Consequences

- Good: a setting left in `cassandra.yaml` never stops a node of a build before the final gate.
- Good: the refusal has one visible trace at start, the warning, and one at a command, its error.
- Bad: the operator has to read the log to learn that the setting had no effect.
- Bad: on such a node the settings row says `true` while the view is off.

## More information

The feature spec applies this decision in section 2.2, in section 2.8 and in FREQ-UPTIM-022 to FREQ-UPTIM-024. Problem 10 of its section 4 names the tests.
