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

# Milestone report: {feature name}, milestone {n}

| Field | Value |
|---|---|
| Title | {feature name}, milestone {n}: {name} |
| Document type | Report (ISO/IEC/IEEE 15289), test completion report per ISO/IEC/IEEE 29119 |
| Status | Draft, Approved or Superseded |
| Version | {n} |
| Author | Architect: {GitHub username} |
| Approver | The maintainer who merges the pull request, which approves the gate |
| References | Feature spec, plan, delivery plan, the merged pull requests of the milestone |

Change history: the git history of this file.

Location: `docs/design/<KEY>-<slug>/milestones/`. Process: [additive.md](../additive.md#milestone-gates).

## Contents

- [1. Summary](#1-summary)
- [2. What was tested](#2-what-was-tested)
- [3. Results against the exit criteria](#3-results-against-the-exit-criteria)
- [4. Requirements delivered](#4-requirements-delivered)
  - [Behaviour nobody asked for](#behaviour-nobody-asked-for)
- [5. Deviations](#5-deviations)
- [6. Documentation](#6-documentation)
- [7. Risk review](#7-risk-review)
  - [New risks](#new-risks)
  - [Re-ordering](#re-ordering)
- [8. Remaining risks](#8-remaining-risks)
- [9. Recommendation](#9-recommendation)

## 1. Summary

{What the milestone delivered, in a few lines.}

## 2. What was tested

{The items and validation items, the test levels used for each, and the environments.}

## 3. Results against the exit criteria

| Exit criterion | Result | Evidence |
|---|---|---|

## 4. Requirements delivered

{The architect fills this section from a fresh check of the merged code against the feature requirements. The reviewer checks it by tracing each row: the FREQ's acceptance criteria in the plan, the items' REQ ids that cite them, the scenarios tagged with those ids, and the requirement to test table in each item's evidence. A requirement proven only by a `@wip` scenario is not delivered. One row per feature requirement an item of this milestone delivers, as the plan's Delivers and Milestone lines give it: its id, the items and pull requests that deliver it, the scenarios or tests that prove it, and its status: delivered, delivered in part, as planned (the plan spreads its items over several milestones, name the milestone that completes it), or not delivered. A requirement not delivered has its reason in Deviations. The feature's last milestone report has no "delivered in part, as planned" row: each requirement is delivered, or not delivered with its reason in Deviations.}

| Requirement | Delivered by | Proven by | Status |
|---|---|---|---|
| {FREQ-<KEY>-nnn} | {items #issue, pull requests #n} | {scenarios by feature file and name, or test classes} | {delivered, delivered in part, as planned, or not delivered} |

### Behaviour nobody asked for

{Behaviour of the merged code that no feature requirement asks for, found by the same check. Write "None found." when the check found none. Otherwise list each finding: what the code does and where.}

## 5. Deviations

{Every difference from the test plan or the delivery plan, with the reason, including every exit criterion that could not run because the continuous integration it needs does not exist yet. For the final milestone such a deviation means no-go.}

## 6. Documentation

{Whether the feature's documentation reads as one whole so far, and the gaps.}

## 7. Risk review

{Every risk in the feature spec, with its status now.}

| Risk | Status (open, reduced, closed, happened) | Note |
|---|---|---|

### New risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|

### Re-ordering

{Whether the remaining milestones should be re-ordered, and why. A change follows the change control path in [additive.md](../additive.md#change-control-after-a-merge).}

## 8. Remaining risks

{What is still unproven after this milestone.}

## 9. Recommendation

{Go or no-go for the next milestone, with the reason.}
