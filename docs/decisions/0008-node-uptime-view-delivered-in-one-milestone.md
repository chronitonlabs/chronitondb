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

# 0008. The node uptime view is delivered in one milestone

| Field | Value |
|---|---|
| Document type | Record (ISO/IEC/IEEE 15289), MADR |
| Status | Accepted |
| Date | 2026-11-17 |
| Deciders | The maintainers |
| References | Issue #144, the feature spec in `docs/design/UPTIM-node-uptime-view/`, [additive.md, Milestone gates](../process/additive.md#milestone-gates) |

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in BCP 14 (RFC 2119, RFC 8174) when, and only when, they appear in all capitals, as shown here.

## Contents

- [Context and problem statement](#context-and-problem-statement)
- [Considered options](#considered-options)
- [Decision outcome](#decision-outcome)
  - [Consequences](#consequences)
- [More information](#more-information)

## Context and problem statement

A feature that needs several items is delivered in milestones, and each milestone ends with a report that a maintainer merges as its gate. The node uptime view is a small feature: one view, its switch with two nodetool commands, one error, one counter and its documentation. The feature spec had to know how many milestones its outline has.

## Considered options

1. One milestone: the view, the switch, the commands, the tests and the documentation. Its report is the final gate.
2. Two milestones. First the view and its switch, reachable by tests only. Then the documentation and the passing of the final gate.

## Decision outcome

Chosen option: "One milestone", because a feature of this size needs one gate, and one report is then reviewed and merged.

The feature spec of the node uptime view MUST outline one milestone, which is the final milestone. The last item of that milestone passes the final gate in the code. Until that item is merged, the switch refuses to turn on, as decision record 0007 says.

### Consequences

- Good: one milestone report to write, review and merge.
- Bad: the code and the documentation are judged at the same gate, so a fault in the view is found no earlier than the end of the feature.

## More information

The feature spec applies this decision in section 11. The delivery plan gives the items and their order.
