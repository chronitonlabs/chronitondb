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

# 0013. A node starts with the build details view hidden when its configuration turns the view on before the final gate

| Field | Value |
|---|---|
| Document type | Record (ISO/IEC/IEEE 15289), MADR |
| Status | Accepted |
| Date | 2026-11-16 |
| Deciders | The maintainers |
| References | Issue #141, the feature spec in `docs/design/BUILD-build-details-view/`, [branching-and-review.md, Feature switches and defaults](../process/branching-and-review.md#feature-switches-and-defaults), decision record 0011 |

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in BCP 14 (RFC 2119, RFC 8174) when, and only when, they appear in all capitals, as shown here.

## Contents

- [Context and problem statement](#context-and-problem-statement)
- [Considered options](#considered-options)
- [Decision outcome](#decision-outcome)
  - [Consequences](#consequences)
- [More information](#more-information)

## Context and problem statement

The switch rules say that before a feature's final milestone gate its switch refuses to turn on, whatever its default. They name no form for the refusal. The switch of the build details view is a yaml setting the node reads at start (decision record 0011), so the only moment a refusal can happen is the start of a node whose configuration sets `build_view_enabled` to `true`. A build cut between two milestones can meet such a configuration. The feature had to know what that node does.

## Considered options

1. The node starts, keeps the view hidden and logs one warning that names the setting.
2. The node refuses to start, with an error that names the setting.

## Decision outcome

Chosen option: "The node starts, keeps the view hidden and logs one warning that names the setting", because a setting left in a configuration then never keeps a node down, and the view is one read-only table that no other part of the node depends on.

Before the final gate of the feature, a node whose loaded configuration sets `build_view_enabled` to `true` MUST start as any other node does. It MUST keep the view hidden, and it MUST log one WARN line at start that names the setting. The node MUST NOT refuse to start because of the setting. The feature MUST NOT change the loaded value of the setting, so `system_views.settings` shows `true` on such a node while the view is hidden.

### Consequences

- Good: no fault and no leftover line in `cassandra.yaml` stops a node because of this view.
- Good: the refusal is visible where an operator looks first after a start, in the log, with the name of the setting.
- Bad: `system_views.settings` shows `true` on a node that hides the view. An operator who reads only that table can believe the view is on.
- Bad: an operator who does not read the start log learns that the view is not there only from the answer for a table that does not exist.

## More information

The feature spec in `docs/design/BUILD-build-details-view/feature-spec.md` applies this decision in FREQ-BUILD-014 and FREQ-BUILD-018, in its section 2.2 and in problem 9 of its section 4.
