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

# 0008. A node starts with the node uptime view hidden when its configuration turns the view on before the final gate

| Field | Value |
|---|---|
| Document type | Record (ISO/IEC/IEEE 15289), MADR |
| Status | Accepted |
| Date | 2026-11-17 |
| Deciders | The maintainers |
| References | Issue #143, the feature spec in `docs/design/UPT-node-uptime-view/`, [branching-and-review.md, Feature switches and defaults](../process/branching-and-review.md#feature-switches-and-defaults), [additive.md, Milestone gates](../process/additive.md#milestone-gates) |

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in BCP 14 (RFC 2119, RFC 8174) when, and only when, they appear in all capitals, as shown here.

## Contents

- [Context and problem statement](#context-and-problem-statement)
- [Considered options](#considered-options)
- [Decision outcome](#decision-outcome)
  - [Consequences](#consequences)
- [More information](#more-information)

## Context and problem statement

Until the final milestone gate of a feature, its switch refuses to turn on, whatever its default. The rule names no form for the refusal. The node uptime view is switched by a yaml setting that the node reads at start (decision record 0007). A build cut before the final gate can meet a `cassandra.yaml` that sets `uptime_view_enabled` to `true`. The feature had to know what such a node does.

## Considered options

1. The node starts as any other node, keeps the view hidden and logs one warning that names the setting.
2. The node refuses to start, with an error that names the setting.

## Decision outcome

Chosen option: "The node starts as any other node, keeps the view hidden and logs one warning that names the setting", because a setting left in `cassandra.yaml` then never keeps a node down.

Before the final gate, a node whose loaded configuration sets `uptime_view_enabled` to `true` MUST keep the view hidden. It MUST log one WARN line at start that names the setting. It MUST NOT refuse to start because of the setting. The feature MUST NOT write the field of the setting, so `system_views.settings` shows the value the node loaded.

### Consequences

- Good: no node stays down because of this setting on a build that is not finished.
- Good: the log tells the operator why the view is not there.
- Bad: on such a node `system_views.settings` shows `true` while the view is hidden.
- Bad: an operator who does not read the log sees only that the table does not exist.

## More information

The feature spec in `docs/design/UPT-node-uptime-view/feature-spec.md` applies this decision in FREQ-UPT-013, FREQ-UPT-014 and FREQ-UPT-015 and in its sections 2.2 and 2.8.
