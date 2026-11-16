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

# 0010. The build details view stays at Normal risk

| Field | Value |
|---|---|
| Document type | Record (ISO/IEC/IEEE 15289), MADR |
| Status | Accepted |
| Date | 2026-11-16 |
| Deciders | The maintainers |
| References | Issue #141, the feature spec in `docs/design/BUILD-build-details-view/`, [classification.md](../process/classification.md) |

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in BCP 14 (RFC 2119, RFC 8174) when, and only when, they appear in all capitals, as shown here.

## Contents

- [Context and problem statement](#context-and-problem-statement)
- [Considered options](#considered-options)
- [Decision outcome](#decision-outcome)
  - [Consequences](#consequences)
- [More information](#more-information)

## Context and problem statement

The work on the build details view is labelled Normal risk. Its worst Bug Category was named as Availability, a response crash, where a read fails. The threat model of the feature spec also names information disclosure: a fault in the rule that hides the view, or a design that adds its own permission check, could show a node's build details to a client that should not see them. [classification.md](../process/classification.md) lists information leakage under the Security category, which it rates Critical. The class had to be settled before the spec could go to review, since the class decides the depth of the checks and the review.

## Considered options

1. Critical risk. The work follows the Security row of the class table as written. The checks of the spec end by the Critical rule, and the security engineer reviews every code pull request.
2. Normal risk, as labelled.

## Decision outcome

Chosen option: "Normal risk, as labelled", because what such a fault could show is three version strings of one node, and the feature adds no permission code of its own.

The work on the build details view stays at Normal risk. The label on the issue is not changed. A fault that shows the build details to a client that should not see them is rated with the rest of the feature. This is a departure from the Security row of the class table in [classification.md](../process/classification.md), made for this feature only. A design of this feature that changes permission code MUST NOT be built under this decision, since such a change meets the Critical floor of that page.

### Consequences

- Good: the spec, the plan and the code follow the Normal path, with the stop rule and the review of that class.
- Good: the security review lens still reads the spec and the code, because the feature adds a new input.
- Bad: the security engineer does not review every code pull request, as Critical work would require.
- Bad: the class of this work differs from what the class table says for information leakage, so the table cannot be read alone for this feature.

## More information

The feature spec in `docs/design/BUILD-build-details-view/feature-spec.md` carries this decision in its Risk row, in problem 3 of its section 4 and in its section 6. FREQ-BUILD-009 keeps the feature out of the permission code.
