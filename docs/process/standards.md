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

# Standards

ChronitonDB uses published standards in place of house rules wherever one fits. This page lists each standard and what it governs here. Where a page in this folder and a standard differ, the page says why.

## Process and roles

**ISO/IEC/IEEE 12207 (software life cycle processes).** Our roles follow its technical processes. Stakeholder needs belong to the maintainers. System requirements and architecture definition belong to the architect. Design definition belongs to the designer. Implementation belongs to the developer. Verification belongs to the reviewer. Integration of Apache Cassandra changes belongs to the integrator. Transition, the making of releases, belongs to the release engineer. Validation is done by validation items in each milestone. Project planning is the delivery plan. See [roles.md](roles.md) and [release.md](release.md).

**ISO/IEC/IEEE 14764:2022 (software maintenance).** Every change to released software has one of its five maintenance categories: corrective, preventive, adaptive, perfective or additive. Urgent corrective maintenance has its own path, called emergency here. See [maintenance.md](maintenance.md) and [additive.md](additive.md).

**ISO/IEC/IEEE 16326 (project management plans).** The delivery plan of a feature follows it: milestones, the reason for their order, exit criteria, the release and line each milestone ships in, the limit on parallel work and what triggers a re-plan. See [additive.md](additive.md).

**ISO/IEC/IEEE 15289 (content of life cycle information items).** Every template is based on its 15289 document type and carries the common header: title, document type, status, version, author, approver and references. Git holds the change history. The merge that approves a document records its approver. See [templates/](templates/).

## Requirements and architecture

**ISO/IEC/IEEE 29148 (requirements engineering).** Requirements are written at three levels: feature requirements in the feature spec, acceptance criteria in the plan, and item requirements in the design record. Each requirement is checked against seven qualities: necessary, unambiguous, singular, verifiable, feasible, consistent and traceable. See [templates/design-record.md](templates/design-record.md).

**EARS (Easy Approach to Requirements Syntax).** Every requirement uses one of five shapes: ubiquitous, event driven (When), state driven (While), optional feature (Where) and unwanted behaviour (If, then). A requirement that fits none of them is rewritten until it fits one.

**BCP 14 (RFC 2119 and RFC 8174).** Normative text uses the BCP 14 key words in capitals. Each requirement carries exactly one key word. Explanations and examples use plain prose.

**ISO/IEC/IEEE 42010 and arc42 (architecture description).** The architecture section of a feature spec follows arc42 headings in short form, which give a 42010 conforming description: context and scope, building blocks, runtime behaviour, deployment, cross cutting concepts and decisions. See [templates/feature-spec.md](templates/feature-spec.md).

**ISO/IEC 25010 (product quality model).** The quality requirements of every feature spec and design record are organised by its quality characteristics. Our standing project rules sit under those characteristics as a checklist. See [quality-requirements.md](quality-requirements.md).

**MADR (Markdown Architectural Decision Records).** Every answered question that changes or settles behaviour, scope or process gets a decision record in MADR format. See [../decisions/README.md](../decisions/README.md).

**STRIDE (threat modelling).** Every new entry point in a feature (syntax, settings, commands, files, network) is checked against spoofing, tampering, repudiation, information disclosure, denial of service and elevation of privilege. Each mitigation becomes a feature requirement.

## Testing and review

**ISO/IEC/IEEE 29119 (software testing).** Our test policy and strategy, test plans, test design, test logs and test completion reports use its names and required contents. See [testing.md](testing.md).

**ISO/IEC 20246 (work product reviews).** Code pull requests get an inspection. Design records, fix records, feature specs, plans, delivery plans and milestone reports get a technical review. The review record lives on the pull request. See [branching-and-review.md](branching-and-review.md).

## Security

**ISO/IEC 29147 (vulnerability disclosure) and ISO/IEC 30111 (vulnerability handling).** They govern how we receive a report, verify it, fix it, release the fix and disclose it. See [security.md](security.md).

**CVSS (Common Vulnerability Scoring System).** It gives the severity of each vulnerability. The CVSS version is not defined yet.

**OpenVEX.** Each release states, for each known vulnerability in a shipped component, whether the release is affected, not affected with the reason, fixed, or under investigation.

**SLSA and OpenSSF Scorecard.** With the release pipeline, release artefacts will carry SLSA Build Level 3 provenance through GitHub artifact attestations, and the repository will run OpenSSF Scorecard weekly with public results.

## Open source compliance

**ISO/IEC 5230 (OpenChain licence compliance) and ISO/IEC 18974 (OpenChain security assurance).** Together they form our compliance programme. See [compliance.md](compliance.md).

**ISO/IEC 5962 (SPDX) and ECMA-424 (CycloneDX).** Each release ships its software bill of materials in both formats.

**The ASF licence categories.** Every third party dependency is checked against the Apache Software Foundation categories A, B and X before use, as Apache Cassandra does.

## Code and history

**Conventional Commits.** Every commit subject and pull request title uses its form `type(scope): description`. See [conventions.md](conventions.md).

**Trunk-based development.** Work merges into the lines in small, short lived branches. Unfinished features stay off behind their switch. See [branching-and-review.md](branching-and-review.md).

**Google Java Style.** New ChronitonDB Java code follows it. Apache Cassandra code keeps Apache's style. See [conventions.md](conventions.md).

**The Ubuntu and Debian version pattern.** A ChronitonDB version is the Apache Cassandra version it contains followed by `-chronitondb<n>`, for example `5.0.10-chronitondb1`, with `~rc<k>` in the package version of a release candidate and `-rc<k>` in its git tag. Debian and Red Hat package tools order these versions correctly. In strict Semantic Versioning the hyphen marks a pre-release, which we accept as Ubuntu does. See [release.md](release.md#version-numbers).

**RFC 3339.** Timestamps in our records, evidence, documentation and release notes use RFC 3339. Apache Cassandra's own log format is unchanged.

**Diátaxis.** User and operator documentation is split into tutorials, how-to guides, reference and explanation, one kind per page.

## Community

**Contributor Covenant 2.1.** The code of conduct for every Chroniton Labs project. See [contributing.md](contributing.md#code-of-conduct).

## The relationship with Apache Cassandra

**The Debian and Ubuntu model.** ChronitonDB relates to Apache Cassandra as Ubuntu relates to Debian. Each line takes every Apache Cassandra patch release of its major version in whole. Single fixes can be taken ahead of an Apache release. Every change we carry on top is listed in the delta register with its upstream status. Fixes to stock code are offered to Apache Cassandra. Security issues that affect Apache Cassandra are coordinated with its security team by the norms Linux distributions use. See [upstream.md](upstream.md).
