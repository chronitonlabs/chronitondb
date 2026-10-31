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

# Plan: {feature name}

| Field | Value |
|---|---|
| Title | Plan for {feature name} |
| Document type | Plan (ISO/IEC/IEEE 15289) |
| Status | Draft, Approved or Superseded |
| Version | {n} |
| Author | Architect: {GitHub username} |
| Approver | The maintainer who merges the pull request |
| References | {feature spec, delivery plan, decision records} |

Change history: the git history of this file.

Location: `docs/design/<feature>/plan.md`. Process: [additive.md](../additive.md).

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in BCP 14 (RFC 2119, RFC 8174) when, and only when, they appear in all capitals, as shown here.

## 1. Items

{One entry per item. Lower levels cite this plan, never restate it. Split only at a real boundary: a real prerequisite, output built in parallel, or a part that needs its own review.}

### Item {n}: {title}

- **Delivers:** {FREQ ids from the feature spec}
- **Acceptance criteria:** {numbered, each testable, written as EARS requirements with one BCP 14 key word}
- **Depends on:** {item numbers, or none}
- **Line:** {chronitondb-5.0 or chronitondb-6.0}
- **Milestone:** {milestone from the delivery plan}
- **Parallel:** {whether it can run in parallel with other items}
- **Item type:** {build item or validation item}

## 2. Validation items

{For each milestone, the validation items: end to end tests written from the feature requirements, as in-JVM distributed tests and Python distributed tests where needed.}

## 3. Traceability

{Every FREQ maps to at least one item. A FREQ with no item blocks approval.}

| FREQ | Items | Validation item |
|---|---|---|
