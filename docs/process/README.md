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

## Work intake

Every piece of work has a GitHub issue. Work may start committed, with its kind label, as described below. Two optional labels mark work that is not committed yet:

1. `idea`: should we do this? The requirements analyst writes a short decision brief, and the maintainers decide to do it, not to do it, or to ask for a spike.
2. `spike`: how would we do this, or can it be done? The architect investigates and writes a research report in `docs/research/`, which a maintainer merges.

A spike issue carries documentation labels while it is researched. On do it, a decision record holds the go and its reasons, and the work's own kind and class labels go on. On do not, the issue is closed as not planned, with the reason. [additive.md](additive.md#work-intake) has the detail.

## Pick the path for a change

Every change has one maintenance category from ISO/IEC/IEEE 14764:2022. The category and the size of the change pick the path.

| Category | What it is | Path | Page |
|---|---|---|---|
| Additive, several items | A new feature that needs more than one item | Feature spec, plan with delivery plan, item design records | [additive.md](additive.md) |
| Additive, one item | A new feature small enough for one item | One item with a design record | [additive.md](additive.md) |
| Corrective | A fix for a fault someone found | Fix record with its reproducing test, one pull request per affected line | [maintenance.md](maintenance.md) |
| Emergency | Any urgent corrective work, security fixes among them. The standard counts it as corrective. It goes ahead of the queue, and a security fix with a security advisory is also worked on in private | Corrective order, ahead of the queue, private only for a security fix with an advisory | [maintenance.md](maintenance.md), [security.md](security.md) |
| Preventive | A fix for a latent fault before it causes a failure | One item with a design record | [maintenance.md](maintenance.md) |
| Adaptive | A change that keeps ChronitonDB working in a changed environment | One item with a design record | [maintenance.md](maintenance.md) |
| Perfective | An improvement to performance, maintainability or documentation | One item with a design record, documentation only changes without one | [maintenance.md](maintenance.md) |

Each issue and each pull request of a change carries exactly one kind label: `kind:additive`, `kind:corrective`, `kind:emergency`, `kind:preventive`, `kind:adaptive` or `kind:perfective`. A maintainer sets it on the issue at triage, an item the integrator, the security engineer or the release engineer opens carries its kind from the start, and a pull request copies its issue's kind. An issue also carries a line label, `chronitondb-5.0` or `chronitondb-6.0`, for each line the problem affects. A pull request's line is its base branch. A release proposal or promotion pull request, which changes only `docs/releases/`, has no category and carries no kind label.

A change that comes from Apache Cassandra follows [upstream.md](upstream.md). A whole Apache release import and the weekly Apache branch merge are adaptive maintenance: they keep ChronitonDB current with upstream. A single cherry-picked Apache fix takes the category of the fix it brings, usually corrective. A commit taken unchanged from another project follows the same page and takes the category of the change it brings. Work that changes no code, such as the scheduled checks, release runs and reviews, has no category.

When the category is unclear, open an issue that says what should change. The maintainers set the category.

Each change also has a class, its risk and its size, carried by one `risk:`, one `size:` and one `reach:` label on the issue and on each pull request. The class sets how deep the documents go, which checks and reviews the change gets and which approval steps it passes. See [classification.md](classification.md).

## Roles

The maintainers decide stakeholder needs, scope, priority, releases and security disclosure, and approve every step by merging its pull request. Eight roles do the work:

1. The requirements analyst asks the maintainers what new work is for and writes the requirements brief they confirm, and the decision brief of an idea.
2. The architect writes the feature spec, the plan, the delivery plan and the milestone reports of a large feature, and the research report of a spike.
3. The designer writes the design record or fix record of one item.
4. The developer writes the code, its tests and its documentation.
5. The reviewer reviews every pull request and posts its verdict on it, one short review for each round.
6. The integrator keeps the lines current with Apache Cassandra and prepares the import pull requests.
7. The security engineer watches every shipped library for vulnerabilities and triages private reports.
8. The release engineer proposes each release and runs the release pipeline once a maintainer approves it.

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
14. [quality-requirements.md](quality-requirements.md): the quality checklist a feature spec and a design record answer. Its rules are stated in full in principles.md.
15. [principles.md](principles.md): the architectural and design rules the project holds to, each with the id a document cites it by.
16. [classification.md](classification.md): the risk and size of a change, and what each class changes.
17. [areas.md](areas.md): the areas a document and an issue name, and the sources a change comes from.
18. [templates/](templates/): the document templates.
19. [The delta register](../delta/README.md): every change ChronitonDB carries on top of Apache Cassandra.
20. [Decision records](../decisions/README.md): answered questions that settle behaviour, scope or process.
21. [The generated indexes](../index/documents.md): every document by kind, [every decision record](../index/decisions.md), and [every document by area](../index/areas.md).

The top level `CONTRIBUTING.md` in this repository is Apache Cassandra's guide. ChronitonDB does not edit it. ChronitonDB's own guide is in [.github/CONTRIBUTING.md](../../.github/CONTRIBUTING.md) and in [contributing.md](contributing.md).

## Not defined yet

1. The CVSS version used for severity scores.
2. The folder layout of the user and operator documentation, which comes with the documentation site.

## Glossary

1. **Line**: a long lived branch that ships releases, one per Apache Cassandra major version. Today `chronitondb-5.0` and `chronitondb-6.0`.
2. **Stock**: code or behaviour exactly as Apache Cassandra has it. A claim about code says Apache Cassandra instead, with its branch and commit. See [conventions.md](conventions.md#claims-about-code).
3. **Item**: one unit of work with one public GitHub issue, one design record or fix record, and one pull request per line it targets. A security fix has no public issue until disclosure. It is tracked in its private advisory.
4. **Feature spec**: the top level description of a large feature, with feature requirements `FREQ-<KEY>-nnn`.
5. **Plan**: the list of items that deliver a feature spec.
6. **Delivery plan**: the order of the items in milestones, with exit criteria.
7. **Milestone gate**: the approval of a milestone report before the next milestone starts.
8. **Design record**: the low level design of one item, with requirements `REQ-<KEY>-nnn` for feature work or `REQ-n` otherwise.
9. **Fix record**: the short design record of a corrective change.
10. **Coverage file**: the file in an item's design folder that names the test of each requirement no scenario proves, and the reason for each requirement deliberately not tested.
11. **EARS**: the five sentence shapes every requirement uses.
12. **Feature switch**: the means an operator has to turn a fork feature on or off, chosen in the feature's design. For example a node setting with a runtime command, or an option on a schema object. Before the feature's final milestone gate the switch refuses to turn on. After it, operators may turn the feature on or off. A behaviour-changing feature always has one, and so does a feature built in more than one milestone. Any other purely additive feature has one only when something needs it to be turned off. Its default depends on the feature class and does not change within a line.
13. **Parity suite**: the tests that prove a line behaves as stock with every fork feature off, apart from the fixes and differences the delta register lists.
14. **Import**: bringing an Apache Cassandra release or fix into a line.
15. **Delta entry**: one record in the delta register for a change ChronitonDB carries on top of Apache Cassandra. Its header follows Debian's DEP-3 patch header convention.
16. **Upstream radar**: the integrator's daily watch of Apache Cassandra releases, branches, JIRAs and commits, summed up in a weekly digest for the maintainers.
17. **Decision record**: a short record, in MADR format, of an answered question.
18. **Release candidate**: a release published as a GitHub pre-release and in the proposed package repositories for verification and a soak before it is promoted unchanged.
19. **Scheduled check**: a daily check the project runs on its own: the integrator's check of Apache Cassandra, the security engineer's check of shipped libraries and private vulnerability reports, and the release engineer's check of the latest CI results. Items it opens are requested by the maintainer who set it up.
20. **Feature key**: 3 to 5 capital letters that name a fork feature, used in its directory `docs/design/<KEY>-<slug>/` and in its requirement ids.
21. **Feature class**: purely additive, for a feature reachable only through something stock Apache Cassandra does not have, such as new syntax, a new nodetool command or a new setting, or behaviour-changing, for a feature that changes what an application sees from something stock Apache Cassandra already does. A purely additive feature is on by default. A behaviour-changing feature is always off by default. See [quality-requirements.md](quality-requirements.md#compatibility-with-apache-cassandra).
22. **Scenario**: the executable form of a fork feature's EARS requirements, written in Gherkin and kept in `test/bdd/`.
23. **Idea**: an issue labelled `idea`, work the maintainers have not yet decided to do.
24. **Spike**: an issue labelled `spike`, a question of how to do something or whether it can be done, answered by a research report.
25. **Research report**: the architect's report on a spike, in `docs/research/<issue>-<slug>.md`.
26. **Principle**: one architectural or design rule of the project, stated once in [principles.md](principles.md) with an id `PRINCIPLE-nnn` that is never reused or renumbered. A document cites a rule by that id.
