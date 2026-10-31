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

# Feature spec: {feature name}

| Field | Value |
|---|---|
| Title | {feature name} |
| Document type | Specification and description (ISO/IEC/IEEE 15289) |
| Status | Draft, Approved or Superseded |
| Version | {n} |
| Author | Architect: {GitHub username} |
| Approver | The maintainer who merges the pull request |
| References | {line, Apache base commit, related issues, decision records} |

Change history: the git history of this file.

Location: `docs/design/<feature>/feature-spec.md` on the line the feature targets. Process: [additive.md](../additive.md).

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in BCP 14 (RFC 2119, RFC 8174) when, and only when, they appear in all capitals, as shown here.

## 1. Purpose and scope

{What the feature does and why, in plain words. Who uses it.}

### Non-goals

{What the feature will not do, each with a short reason.}

## 2. Architecture

{Short arc42 form. Each heading a few lines or a diagram.}

### 2.1 Context and scope

{The feature's boundary: clients, operators, other subsystems and external systems it talks to.}

### 2.2 Building blocks

{The components, where each lives in the tree, and the interfaces between them.}

### 2.3 Runtime view

{The main request paths: coordinator, replica read, memtable write, flush, compaction, streaming, repair. One line each for the paths touched.}

### 2.4 Data and formats

{On-disk files, wire forms, schema and cluster metadata the feature adds or changes.}

### 2.5 Cross cutting concepts

{Settings, limits, observability, error handling and security concepts shared across components.}

### 2.6 Deployment

{What changes for an operator: new settings, new nodetool commands, new files on disk.}

## 3. Feature requirements

{One requirement per entry: an id `FREQ-n`, one EARS shape, one BCP 14 key word, and a source. Each requirement passes the ISO/IEC/IEEE 29148 checklist in [design-record.md](design-record.md).}

FREQ-1 ({shape}): {requirement}. Source: {issue, decision record, risk or stakeholder need}.

## 4. Quality requirements

{The checklist table from [quality-requirements.md](../quality-requirements.md), every line answered with FREQ ids or a stated reason it does not apply.}

## 5. Threat model

{Every new entry point (syntax, settings, commands, files, network) checked with STRIDE: spoofing, tampering, repudiation, information disclosure, denial of service, elevation of privilege. Each mitigation is a FREQ. Or the statement "This feature adds no new entry point" with the reason.}

| Entry point | Threat (STRIDE) | Mitigation | FREQ |
|---|---|---|---|

## 6. Compatibility

{Or the statement "This feature changes no format, schema or protocol" with the reason.}

### 6.1 On-disk format changes

{Each change with its version marker, and how a reader that predates it behaves.}

### 6.2 Mixed-version cluster

{Behaviour during a rolling upgrade, one sentence per path.}

### 6.3 Upgrade path and prerequisites

{Supported upgrade paths and what MUST be true before each starts.}

### 6.4 Rollback path

{How to go back, including what MUST be dropped or rebuilt first.}

### 6.5 Runbook entries

{The runbook pages this feature adds or changes, by name.}

## 7. Dependencies

{Each new library or version change. Or "No new dependency".}

| Library | Version | ASF category | NOTICE and credit lines | Known vulnerabilities | Why it is needed |
|---|---|---|---|---|---|

## 8. Risks

| Id | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|

## 9. Decisions

{Links to the decision records in `docs/decisions/` that shape this feature, each with a one line reminder.}

## 10. Milestones outline

{The milestones in order, one line each, with what each makes testable. The delivery plan gives the detail.}
