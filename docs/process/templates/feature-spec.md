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

Location: `docs/design/<KEY>-<slug>/feature-spec.md` on the line the feature targets, with the [feature key](../additive.md#feature-keys-and-requirement-ids) in the directory name. Process: [additive.md](../additive.md).

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

### 2.7 Package dependencies and hook points

{For each ChronitonDB package under `org/chronitondb`: the packages it MAY import. A check refuses any other import, and changing these rules is a change to this spec. Then the hook points: each stock Apache Cassandra file that imports ChronitonDB code, why it must, and its [delta entry](../../delta/README.md). Keep the hook points few, since each one is a place where an Apache import can conflict.}

### 2.8 Feature class and switches

{Mandatory. The class of the feature and of each switch, each with its reason. A purely additive feature or switch is reachable only through new syntax, new index types or new settings that stock Apache Cassandra rejects. Its default MAY be on from a line's first release. A behaviour-changing feature or switch changes something stock Apache Cassandra already does: results, errors, warnings or the performance of existing operations. Its default MUST be off on every line. A default never changes within a line. A feature that passes its final milestone gate after a line's first release is off by default on that line. Name the stock operations each behaviour-changing switch changes. Each departure in a design record's stock behaviour table links to its switch's row here. See [branching-and-review.md](../branching-and-review.md#feature-switches-and-defaults).}

Feature class: {purely additive or behaviour-changing}, because {reason}.

| Switch | Class | Reason | Default per line | Stock operations it changes |
|---|---|---|---|---|
| {yaml setting and nodetool toggle} | {class} | {reason} | {line: on or off} | {operations, or none} |

## 3. Feature requirements

{One requirement per entry, on one line: an id `FREQ-<KEY>-nnn` with the feature key and three digits, one EARS shape, one BCP 14 key word, and a source. Each requirement passes the ISO/IEC/IEEE 29148 checklist in [design-record.md](design-record.md).}

FREQ-{KEY}-001 ({shape}): {requirement}. Source: {issue, decision record, risk or stakeholder need}.

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

{Supported upgrade paths and what MUST be true before each starts. Each setting the feature needs in the line's minimum setup, the setup an existing Apache Cassandra cluster MUST reach before it switches, is stated here with its evidence: what the setting changes, its record in Apache's releases and JIRA, and how it was tested. The line's upgrade runbook takes the list from here. See [release.md](../release.md#the-configuration-file).}

### 6.4 Rollback path

{How to go back, including what MUST be dropped or rebuilt first.}

### 6.5 Runbook entries

{The runbook pages this feature adds or changes, by name.}

## 7. Dependencies

{Each new library or version change, one row each. Name a library by its Maven `group:artifact` or artifact, its pip name, its file name under `lib/` without the version, or `accord` for the Accord submodule, and give the exact version. Or "No new dependency".}

| Library | Version | ASF category | NOTICE and credit lines | Known vulnerabilities | Why it is needed |
|---|---|---|---|---|---|

## 8. Risks

| Id | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|

## 9. Decisions

{Links to the decision records in `docs/decisions/` that shape this feature, each with a one line reminder.}

## 10. Milestones outline

{The milestones in order, one line each, with what each makes testable. The delivery plan gives the detail.}

## 11. Prior art

{Mandatory. How other systems and projects solved this problem, what each got right and wrong, and why ChronitonDB chooses differently where it does. Cite each source.}

These rules apply to every source:

1. Describe and cite behaviour, published designs, papers, public documentation and code under licences compatible with the Apache License 2.0.
2. Code or text under an incompatible licence, for example the Elastic License, SSPL, BUSL or a proprietary licence, MUST NOT be copied. The behaviour of such a system is taken only from its public documentation. Code under a compatible licence MAY be used only with credit. See [conventions.md](../conventions.md#code-from-elsewhere).
3. Contributors working on the project's behalf MUST NOT search for or read patents for design work. Any patent concern goes to the maintainers.

## Glossary

{One row per domain term this feature uses. Every design record, class, CQL option, metric and page of the feature uses these names. The reviewer checks new names against this table. A design record that needs a new term defines it under its own "New terms" heading, and the architect adds it here through change control.}

| Term | Definition | Name in code, CQL and docs |
|---|---|---|
| {term} | {one line} | {names} |
