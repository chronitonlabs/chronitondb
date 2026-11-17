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

# 0010. The node uptime view stays at Normal risk

| Field | Value |
|---|---|
| Document type | Record (ISO/IEC/IEEE 15289), MADR |
| Status | Accepted |
| Date | 2026-11-17 |
| Deciders | The maintainers |
| References | Issue #144, the feature spec in `docs/design/UPTIM-node-uptime-view/`, [classification.md, Risk](../process/classification.md#risk) |

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in BCP 14 (RFC 2119, RFC 8174) when, and only when, they appear in all capitals, as shown here.

## Contents

- [Context and problem statement](#context-and-problem-statement)
- [Considered options](#considered-options)
- [Decision outcome](#decision-outcome)
  - [Consequences](#consequences)
- [More information](#more-information)

## Context and problem statement

The risk of a change is the worst Bug Category it could cause if it were wrong, and the worst row of the class table decides. The issue of the node uptime view carries the label `risk:normal`. Its worst fault by that label is a read of the view that fails, a response crash. The class table rates two other faults of this feature Critical:

1. A wrong value in the view. This is a transient incorrect response, in the category Correctness.
2. A node that does not start because of the view. This is a node unavailable, in the category Availability.

By the table the feature is Critical. The feature spec had to know which class its work runs at.

## Considered options

1. Keep Normal risk, as an exception to the class table recorded here.
2. Raise the feature to Critical risk.

## Decision outcome

Chosen option: "Keep Normal risk, as an exception to the class table recorded here", because the maintainers set the class with both faults known, and the feature spec names each fault with its tests.

The issue of the node uptime view keeps the label `risk:normal`. The feature spec, the plan and the code of the feature MUST take the checks of Normal risk.

The feature spec MUST name both faults in its section Where problems could occur, each with the tests that catch it.

The exception covers these two faults of this feature and nothing else. It is no rule for another feature, and the class table stays as it is.

### Consequences

- Good: a small read-only view takes the checks of its size, with at most five rounds of checks on its spec and the review of Normal risk.
- Bad: the feature does not take the checks the class table asks for its worst fault: the review of every code pull request by the security engineer, and every review lens.
- Bad: a reader who compares the label with the class table finds a difference, and needs this record to explain it.

## More information

The feature spec carries this decision in the Risk row of its control table. Problems 1 and 4 of its section 4 name the two faults and their tests.
