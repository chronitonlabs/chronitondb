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
| Risk | {Critical, Normal or Low}: {the worst Bug Category the feature could cause if wrong, and the floor if one applied} |
| Size | {Low Hanging Fruit, Normal, Challenging or Byzantine}: {why} |
| Reach | {One area or Cross-cutting}: {why, naming the packages touched} |
| Touches | {public interface (name which), stock behaviour, new input or privilege, new dependency, shared state (threads, pools or shared state), request path (a read, write or query path), new feature or switch, or none} |

Change history: the git history of this file.

Location: `docs/design/<KEY>-<slug>/feature-spec.md` on the line the feature targets, with the [feature key](../additive.md#feature-keys-and-requirement-ids) in the directory name. Process: [additive.md](../additive.md).

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in BCP 14 (RFC 2119, RFC 8174) when, and only when, they appear in all capitals, as shown here.

The Risk, Size and Reach rows are the feature's class, as [classification.md](../classification.md) defines it, and match the issue's `risk:`, `size:` and `reach:` labels. Each value is the level, a colon and the reason. Touches lists what the feature touches, from the four phrases in the row, or says none. A public interface or stock behaviour in Touches means the risk is Normal or Critical. The class decides which sections are required, as each section says. A required section holds its content. Any other section holds its content or the one line `Not applicable: <reason>`. A section that says Not applicable covers its subsections, which are then left out.

## Contents

- [1. Purpose and scope](#1-purpose-and-scope)
  - [Non-goals](#non-goals)
- [2. Architecture](#2-architecture)
  - [2.1 Context and scope](#21-context-and-scope)
  - [2.2 Building blocks](#22-building-blocks)
  - [2.3 Runtime view](#23-runtime-view)
  - [2.4 Data and formats](#24-data-and-formats)
  - [2.5 Cross cutting concepts](#25-cross-cutting-concepts)
  - [2.6 Deployment](#26-deployment)
  - [2.7 Package dependencies and hook points](#27-package-dependencies-and-hook-points)
  - [2.8 Feature class and switches](#28-feature-class-and-switches)
- [3. Feature requirements](#3-feature-requirements)
- [4. Where problems could occur](#4-where-problems-could-occur)
  - [4.1 Test plan](#41-test-plan)
- [5. Quality requirements](#5-quality-requirements)
- [6. Threat model](#6-threat-model)
- [7. Compatibility](#7-compatibility)
  - [7.1 On-disk format changes](#71-on-disk-format-changes)
  - [7.2 Mixed-version cluster](#72-mixed-version-cluster)
  - [7.3 Upgrade path and prerequisites](#73-upgrade-path-and-prerequisites)
  - [7.4 Rollback path](#74-rollback-path)
  - [7.5 Runbook entries](#75-runbook-entries)
- [8. Dependencies](#8-dependencies)
- [9. Risks](#9-risks)
- [10. Decisions](#10-decisions)
- [11. Milestones outline](#11-milestones-outline)
- [12. Prior art](#12-prior-art)
- [Glossary](#glossary)

## 1. Purpose and scope

{Required for every class. What the feature does and why, in plain words. Who uses it.}

### Non-goals

{What the feature will not do, each with a short reason.}

## 2. Architecture

{Required for every class, a few lines at Low Hanging Fruit. Short arc42 form. Each heading a few lines or a diagram.}

### 2.1 Context and scope

{Required from Normal size. The feature's boundary: clients, operators, other subsystems and external systems it talks to.}

### 2.2 Building blocks

{Required from Normal size. The components, where each lives in the tree, and the interfaces between them.}

### 2.3 Runtime view

{Required from Challenging size. The main request paths: coordinator, replica read, memtable write, flush, compaction, streaming, repair. One line each for the paths touched.}

### 2.4 Data and formats

{Required from Challenging size. On-disk files, wire forms, schema and cluster metadata the feature adds or changes.}

### 2.5 Cross cutting concepts

{Required from Challenging size. Settings, limits, observability, error handling and security concepts shared across components.}

### 2.6 Deployment

{Required from Challenging size. What changes for an operator: new settings, new nodetool commands, new files on disk.}

### 2.7 Package dependencies and hook points

{Required from Normal size. For each ChronitonDB package under `org/chronitondb`: the packages it MAY import. A check refuses any other import, and changing these rules is a change to this spec. Then the hook points: each stock Apache Cassandra file that imports ChronitonDB code, why it must, and its [delta entry](../../delta/README.md). Keep the hook points few, since each one is a place where an Apache import can conflict.}

### 2.8 Feature class and switches

{Required for every class. The class of the feature and of each switch, each with its reason. A purely additive feature or switch is reachable only through new syntax, new index types or new settings that stock Apache Cassandra rejects. Its default MAY be on from a line's first release. A behaviour-changing feature or switch changes something stock Apache Cassandra already does: results, errors, warnings or the performance of existing operations. Its default MUST be off on every line. A default never changes within a line. A feature that passes its final milestone gate after a line's first release is off by default on that line. Name the stock operations each behaviour-changing switch changes. Each departure in a design record's stock behaviour table links to its switch's row here. See [branching-and-review.md](../branching-and-review.md#feature-switches-and-defaults).}

Feature class: {purely additive or behaviour-changing}, because {reason}.

| Switch | Class | Reason | Default per line | Stock operations it changes |
|---|---|---|---|---|
| {yaml setting and nodetool toggle} | {class} | {reason} | {line: on or off} | {operations, or none} |

## 3. Feature requirements

{Required for every class. One requirement per entry, on one line: an id `FREQ-<KEY>-nnn` with the feature key and three digits, one EARS shape, one BCP 14 key word, and a source. Each requirement passes the ISO/IEC/IEEE 29148 checklist in [design-record.md](design-record.md).}

FREQ-{KEY}-001 ({shape}): {requirement}. Source: {issue, decision record, risk or stakeholder need}.

## 4. Where problems could occur

{Required for every class, never Not applicable. Where the feature could go wrong if a part of it is wrong, worst case first: what a user or an operator would see (a wrong result, an error, a crash, a slow request, a changed file on disk), on which request path, and from which part of the change. Never "None" or "Low", and never an argument that the feature is safe. After the "Where problems could occur" section of Ubuntu's stable release update template.}

### 4.1 Test plan

{Required for every class, never Not applicable. For each problem above, the test that would catch it and what it checks: unit, scenario, in-JVM distributed, upgrade or mixed-version, stress or benchmark. A problem no test covers says why, and how it is watched instead.}

## 5. Quality requirements

{Required from Challenging size. The checklist table from [quality-requirements.md](../quality-requirements.md), every line answered with FREQ ids or a stated reason it does not apply.}

## 6. Threat model

{Required from Challenging size, at Critical risk, and at Normal risk when Touches names new input or privilege. Every new entry point (syntax, settings, commands, files, network) checked with STRIDE: spoofing, tampering, repudiation, information disclosure, denial of service, elevation of privilege. Each mitigation is a FREQ. Or the statement "This feature adds no new entry point" with the reason.}

| Entry point | Threat (STRIDE) | Mitigation | FREQ |
|---|---|---|---|

## 7. Compatibility

{Required from Challenging size, at Critical risk, and at Normal risk when Touches names a public interface or stock behaviour. In full, or the statement "This feature changes no format, schema or protocol" with the reason.}

### 7.1 On-disk format changes

{Each change with its version marker, and how a reader that predates it behaves.}

### 7.2 Mixed-version cluster

{Behaviour during a rolling upgrade, one sentence per path.}

### 7.3 Upgrade path and prerequisites

{Supported upgrade paths and what MUST be true before each starts. Each setting the feature needs in the line's minimum setup, the setup an existing Apache Cassandra cluster MUST reach before it switches, is stated here with its evidence: what the setting changes, its record in Apache's releases and JIRA, and how it was tested. The line's upgrade runbook takes the list from here. See [release.md](../release.md#the-configuration-file).}

### 7.4 Rollback path

{How to go back, including what MUST be dropped or rebuilt first.}

### 7.5 Runbook entries

{The runbook pages this feature adds or changes, by name.}

## 8. Dependencies

{Required from Challenging size, for Cross-cutting reach, and at Normal or Critical risk when Touches names a new dependency. Each new library or version change, one row each. Name a library by its Maven `group:artifact` or artifact, its pip name, its file name under `lib/` without the version, or `accord` for the Accord submodule, and give the exact version. Or "No new dependency".}

| Library | Version | ASF category | NOTICE and credit lines | Known vulnerabilities | Why it is needed |
|---|---|---|---|---|---|

## 9. Risks

{Required from Challenging size and for Cross-cutting reach.}

| Id | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|

## 10. Decisions

{Required for every class. Links to the decision records in `docs/decisions/` that shape this feature, each with a one line reminder.}

## 11. Milestones outline

{Required from Normal size and for Cross-cutting reach. The milestones in order, one line each, with what each makes testable. The delivery plan gives the detail.}

## 12. Prior art

{Required for every class, one line at Low Hanging Fruit. How other systems and projects solved this problem, what each got right and wrong, and why ChronitonDB chooses differently where it does. Cite each source.}

These rules apply to every source:

1. Describe and cite behaviour, published designs, papers, public documentation and code under licences compatible with the Apache License 2.0.
2. Code or text under an incompatible licence, for example the Elastic License, SSPL, BUSL or a proprietary licence, MUST NOT be copied. The behaviour of such a system is taken only from its public documentation. Code under a compatible licence MAY be used only with credit. See [conventions.md](../conventions.md#code-from-elsewhere).
3. Contributors working on the project's behalf MUST NOT search for or read patents for design work. Any patent concern goes to the maintainers.

## Glossary

{Required from Challenging size. One row per domain term this feature uses. Every design record, class, CQL option, metric and page of the feature uses these names. The reviewer checks new names against this table. A design record that needs a new term defines it under its own "New terms" heading, and the architect adds it here through change control.}

| Term | Definition | Name in code, CQL and docs |
|---|---|---|
| {term} | {one line} | {names} |
