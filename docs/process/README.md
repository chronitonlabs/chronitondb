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

# How we work on ChronitonDB

These pages describe how a change to ChronitonDB goes from an idea to a merged commit. They cover every kind of change: new features, bug fixes, security fixes, imports from Apache Cassandra and documentation.

ChronitonDB is a downstream distribution of Apache Cassandra, in the way Ubuntu is downstream of Debian. Each ChronitonDB line contains every Apache Cassandra patch release of its major version (before Apache's first release of that major, Apache's branch for it), plus the changes listed in the [delta register](../delta/README.md).

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in these documents are to be interpreted as described in BCP 14 (RFC 2119, RFC 8174) when, and only when, they appear in all capitals, as shown here.

## Pick the path for a change

Every change has one maintenance category from ISO/IEC/IEEE 14764:2022. The category and the size of the change pick the path.

| Category | What it is | Path | Page |
|---|---|---|---|
| Additive, several items | A new feature that needs more than one item | Feature spec, plan with delivery plan, item design records | [additive.md](additive.md) |
| Additive, one item | A new feature small enough for one item | One item with a design record | [additive.md](additive.md) |
| Corrective | A fix for a fault someone found | Fix record with its reproducing test, one pull request per affected line | [maintenance.md](maintenance.md) |
| Emergency | Urgent corrective work, security fixes among them. The standard counts it as corrective, it has its own path because security work stays private | Corrective order, ahead of the queue, private for security | [maintenance.md](maintenance.md), [security.md](security.md) |
| Preventive | A fix for a latent fault before it causes a failure | One item with a design record | [maintenance.md](maintenance.md) |
| Adaptive | A change that keeps ChronitonDB working in a changed environment | One item with a design record | [maintenance.md](maintenance.md) |
| Perfective | An improvement to performance, maintainability or documentation | One item with a design record, documentation only changes without one | [maintenance.md](maintenance.md) |

A change that comes from Apache Cassandra follows [upstream.md](upstream.md). A whole Apache release import and the weekly Apache branch merge are adaptive maintenance: they keep ChronitonDB current with upstream. A single cherry-picked Apache fix takes the category of the fix it brings, usually corrective. Work that changes no code, such as the scheduled checks, release runs and reviews, has no category.

If you are not sure of the category, open an issue and say what you want to change. The maintainers set the category.

## Roles

The maintainers decide scope, priority, releases and security disclosure, and approve every step by merging its pull request. Seven roles do the work:

1. The architect writes the feature spec, the plan, the delivery plan and the milestone reports of a large feature.
2. The designer writes the design record or fix record of one item.
3. The developer writes the code, its tests and its documentation.
4. The reviewer reviews every pull request and posts its review on it.
5. The integrator keeps the lines current with Apache Cassandra and prepares the import pull requests.
6. The security engineer watches every shipped library for vulnerabilities and triages private reports.
7. The release engineer proposes each release and runs the release pipeline once a maintainer approves it.

A role MAY be carried out by a person or by an automated agent. Approvals are always made by a maintainer, or by a committer for a pull request within their area or line. [roles.md](roles.md) has the detail, and [governance.md](governance.md) says how someone becomes a committer or a maintainer.

## Pages

1. [contributing.md](contributing.md): how people outside the project raise issues and contribute changes.
2. [standards.md](standards.md): the standards we adopt and what each one governs here.
3. [roles.md](roles.md): who does what, and who approves.
4. [governance.md](governance.md): maintainers, committers, and how commit rights are given, lapse and are removed.
5. [additive.md](additive.md): new features, from feature spec to milestone gates.
6. [maintenance.md](maintenance.md): corrective, emergency, preventive, adaptive and perfective changes.
7. [upstream.md](upstream.md): how Apache Cassandra releases and fixes come into the lines, and the delta register.
8. [branching-and-review.md](branching-and-review.md): lines, branches, history rules, required checks, reviews and pull requests.
9. [conventions.md](conventions.md): commit messages, code layout and style, licence headers, names and documentation locations.
10. [testing.md](testing.md): test policy and strategy.
11. [release.md](release.md): release cadence, support lifetime, release candidates, freezes and version numbers.
12. [security.md](security.md): how vulnerabilities are reported, fixed and disclosed.
13. [compliance.md](compliance.md): open source licence compliance, notices, SBOM and VEX.
14. [quality-requirements.md](quality-requirements.md): the quality checklist every feature spec and design record answers.
15. [templates/](templates/): the document templates.
16. [The delta register](../delta/README.md): every change ChronitonDB carries on top of Apache Cassandra.
17. [Decision records](../decisions/README.md): answered questions that settle behaviour, scope or process.

The top level `CONTRIBUTING.md` in this repository is Apache Cassandra's guide. ChronitonDB does not edit it. ChronitonDB's own guide is in [.github/CONTRIBUTING.md](../../.github/CONTRIBUTING.md) and in [contributing.md](contributing.md).

## Not defined yet

1. The CVSS version used for severity scores.
2. The folder layout of the user and operator documentation, which comes with the documentation site.

## Glossary

1. **Line**: a long lived branch that ships releases, one per Apache Cassandra major version. Today `chronitondb-5.0` and `chronitondb-6.0`.
2. **Stock**: code or behaviour exactly as Apache Cassandra has it.
3. **Item**: one unit of work with one public GitHub issue, one design record or fix record, and one pull request per line it targets. A security fix has no public issue until disclosure. It is tracked in its private advisory.
4. **Feature spec**: the top level description of a large feature, with feature requirements `FREQ-n`.
5. **Plan**: the list of items that deliver a feature spec.
6. **Delivery plan**: the order of the items in milestones, with exit criteria.
7. **Milestone gate**: the approval of a milestone report before the next milestone starts.
8. **Design record**: the low level design of one item, with requirements `REQ-n`.
9. **Fix record**: the short design record of a corrective change.
10. **Coverage file**: the file in an item's design folder that maps each requirement to its test.
11. **EARS**: the five sentence shapes every requirement uses.
12. **Feature switch**: the yaml setting and nodetool toggle that turn a fork feature on or off. Before the feature's final milestone gate the switch refuses to turn on. After it, operators may turn the feature on, and its default stays off for the life of the line.
13. **Parity suite**: the tests that prove a line behaves as stock with every fork feature off.
14. **Import**: bringing an Apache Cassandra release or fix into a line.
15. **Delta entry**: one record in the delta register for a change ChronitonDB carries on top of Apache Cassandra.
16. **Upstream radar**: the integrator's daily watch of Apache Cassandra releases, branches, JIRAs and commits, summed up in a weekly digest for the maintainers.
17. **Decision record**: a short record, in MADR format, of an answered question.
18. **Release candidate**: a release published as a GitHub pre-release and in the proposed package repositories for verification and a soak before it is promoted unchanged.
19. **Scheduled check**: a daily check the project runs on its own: the integrator's check of Apache Cassandra, the security engineer's check of shipped libraries and private vulnerability reports, and the release engineer's check of the latest CI results. Items it opens are requested by the maintainer who set it up.
