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

# 0017. The build details view stays at Normal risk with its start fault named

| Field | Value |
|---|---|
| Document type | Record (ISO/IEC/IEEE 15289), MADR |
| Status | Superseded by 0022 |
| Date | 2026-11-16 |
| Deciders | The maintainers |
| References | Issue #141, the feature spec in `docs/design/BUILD-build-details-view/`, [classification.md](../process/classification.md), the [design record of the commit log disk check](../design/CLD-commitlog-disk-check/design-record.md), decision records 0010 and 0016 |

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in BCP 14 (RFC 2119, RFC 8174) when, and only when, they appear in all capitals, as shown here.

## Contents

- [Context and problem statement](#context-and-problem-statement)
- [Considered options](#considered-options)
- [Decision outcome](#decision-outcome)
  - [Consequences](#consequences)
- [More information](#more-information)

## Context and problem statement

The work on the build details view is labelled Normal risk, and decision record 0010 kept that class for a fault that shows the build details. Every node runs one line of the feature at start, the switch off included: the hook line, which loads the class of the start step, and then the read of the setting. A fault there would stop a node from starting, and so would a start step that let a throwable out. [classification.md](../process/classification.md) rates a node that is unavailable as an Availability fault of Critical risk. The class decides the depth of the checks and the review, so it had to be settled with this fault named.

## Considered options

1. Normal risk, as labelled. The feature spec names the fault, the requirements that exclude it and their tests.
2. Critical risk. The checks of the spec end by the Critical rule, and the security engineer reviews every code pull request.

## Decision outcome

Chosen option: "Normal risk, as labelled", because the requirements of the feature exclude the fault and its tests run on every build, and the merged design record of the commit log disk check stayed at Normal risk in the same way for a start fault its requirements exclude.

The work on the build details view stays at Normal risk. The label on the issue is not changed. The feature spec MUST name the fault in its Risk row and in its section on where problems could occur. It MUST keep the requirements that exclude the fault: a start step that returns right after it read the setting as `false`, and a start step that lets no throwable out once it read the setting as `true`. Tests of both MUST run on every build. This is a departure from the Availability row of the class table in [classification.md](../process/classification.md), made for this feature only.

### Consequences

- Good: the spec, the plan and the code follow the Normal path, with the stop rule and the review of that class.
- Good: the fault is named where the maintainers and the reviewer read the class, with the requirements and the tests that exclude it.
- Bad: the hook line and the read of the setting run before the guard of the start step. No requirement can catch a fault there, and only tests show that it is absent on the builds they run on.
- Bad: the class of this work differs from what the class table says for a node that is unavailable, so the table cannot be read alone for this feature.

## More information

Decision record 0022 supersedes this record. It keeps the work at Normal risk and names the start faults as they are now. The feature spec in `docs/design/BUILD-build-details-view/feature-spec.md` carries that in its Risk row and in problem 1 of its section 4.
