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

# Delivery plan: {feature name}

| Field | Value |
|---|---|
| Title | Delivery plan for {feature name} |
| Document type | Plan (ISO/IEC/IEEE 15289), project plan content per ISO/IEC/IEEE 16326 |
| Status | Draft, Approved or Superseded |
| Version | {n} |
| Author | Architect: {GitHub username} |
| Approver | The maintainer who merges the pull request |
| References | {feature spec, plan, decision records} |

Change history: the git history of this file.

Location: `docs/design/<KEY>-<slug>/delivery-plan.md`. Process: [additive.md](../additive.md).

## Contents

- [1. Milestones](#1-milestones)
  - [Milestone {n}: {name}](#milestone-n-name)
- [2. Order rationale](#2-order-rationale)
- [3. Line choice](#3-line-choice)
- [4. Parallel work limit](#4-parallel-work-limit)
- [5. Re-plan triggers](#5-re-plan-triggers)
- [6. Test plan](#6-test-plan)

## 1. Milestones

{Each milestone is an increment that can be tested and shown. One entry per milestone.}

### Milestone {n}: {name}

- **Items:** {item numbers from the plan, build and validation}
- **What it makes testable:** {one or two lines}
- **Exit criteria:** {numbered, each checkable. Upgrade and rollback tests for any on-disk format change this milestone introduces}
- **Release and line:** {the line, and the release it is planned to ship in. The feature becomes switchable at the final gate, with the default the feature spec sets for the line, or off when the final gate passes after the line's first release}

## 2. Order rationale

{Why the milestones come in this order, for example the riskiest part first.}

## 3. Line choice

{The line the feature is built on first, and when the other line follows, if it does. There is no standing default.}

## 4. Parallel work limit

{How many items may be in progress at once, and why.}

## 5. Re-plan triggers

{The events that cause a re-plan, for example a failed exit criterion, a risk that happened, or a change in an Apache release.}

## 6. Test plan

{The ISO/IEC/IEEE 29119 test plan for the feature: test levels used, what each milestone tests at which level, test environments, the parity suite, upgrade and rollback tests, benchmarks with thresholds, and golden corpora if any. For each exit criterion, where it runs: on continuous integration or on the build machines. Until continuous integration exists, the parts of it the milestone gates need, which are in place before the final milestone. See [testing.md](../testing.md).}
