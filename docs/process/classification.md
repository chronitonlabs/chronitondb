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

# Classification of work

Every change is classified on two axes, risk and size, and the approach to it follows the class: how deep its documents go, which sections they fill in full, which checks and reviews it gets, and which approval steps it passes. The maintenance category, the kind label of [README.md](README.md#pick-the-path-for-a-change), stays a separate third axis. A corrective fix and a new feature can each be of any class.

The words come from Apache Cassandra's own JIRA fields, so a finding here maps onto an Apache ticket in the same terms. The ideas of a risk section and of a release critical finding come from Ubuntu and Debian, the model this project follows as a downstream distribution.

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in BCP 14 (RFC 2119, RFC 8174) when, and only when, they appear in all capitals, as shown here.

## Risk

The risk of a change is the worst Bug Category it could cause if it were wrong, recorded with a Severity, as Apache Cassandra's JIRA records a bug.

| Bug Category | What it covers | Risk |
|---|---|---|
| Correctness | Unrecoverable corruption or loss, recoverable corruption or loss, a transient incorrect response, a consistency fault, a fault in an API or its semantics or implementation | Critical |
| Correctness | A test failure, where only a test is wrong | Low |
| Availability | A cluster crash, a process crash, a node or service unavailable | Critical |
| Availability | A response crash | Normal |
| Degradation | Performance, resource management, a slow use case, another exception with no other effect | Normal |
| Security | Remote code execution, privilege escalation, information leakage, denial of service | Critical |
| Packaging | How the software is built, packaged and installed, the source or the package distribution | Low |
| Documentation | What the documentation says | Low |
| Code | A bug whose impact is unclear | Critical until the author names the category the change could cause, as anything unknown counts as its strictest value |

The table gives each category the level it takes by the definitions below. The worst row the change could cause decides. The three levels are Cassandra's Severity values:

| Risk | When | Label |
|---|---|---|
| Critical | The change could cause corruption or loss, wrong results, an inconsistency, a cluster or process crash, a node or service unavailable, or a security breach, a denial of service included | `risk:critical` |
| Normal | The change could cause a degradation or a response crash, or it changes a public interface or stock behaviour | `risk:normal` |
| Low | The change is documentation, packaging, code clarity or tests only. Code clarity is this project's rule, not a JIRA category | `risk:low` |

### The floor

A change that touches a public interface or stock behaviour is at least Normal, whatever its worst Bug Category. The public interfaces are the compatibility areas Apache Cassandra's enhancement proposal process names: CQL and the native protocol, JMX and its metrics, virtual tables, the yaml configuration, the tools such as nodetool, and the on-disk formats. Stock behaviour is anything stock Apache Cassandra already does: results, errors, warnings, metrics and the performance of existing operations.

A change to a file that guards the process is never Low either: it is at least Normal. These files are the CI workflows and scripts (`.github/`, `.build/`, `.circleci/`, `.jenkins/`), the build file `build.xml`, the test configuration under `test/conf/`, the project's checkers under `tools/chronitondb/`, the process pages and templates under `docs/process/`, and the instructions for contributors' tools, `.claude/` and any `CLAUDE.md` or `AGENTS.md` at any depth.

### Where problems could occur

Every feature spec, fix record, design record that is not covered by its feature spec, and pull request body of Low risk work carries a section "Where problems could occur" with its test plan, after the section of the same name in Ubuntu's stable release update template. It says where the change could go wrong if a part of it is wrong, worst case first: what a user or operator would see, on which request path, and from which part of the change. It is never "None" or "Low", and never an argument that the change is safe. The test plan names, for each problem, the test that would catch it, or why no test can and how it is watched instead.

### Release critical findings

A review finding at the top severity, a blocker, blocks the merge of its pull request and any release that would carry the change, until it is fixed. This is Debian's release critical idea: severities critical, grave and serious keep a package out of a release until fixed.

## Size

The size of a change is Cassandra's JIRA Complexity, plus its reach.

| Complexity | When | Label |
|---|---|---|
| Low Hanging Fruit | Trivial, no dependencies, local, open to new contributors | `size:low-hanging-fruit` |
| Normal | Unremarkable, the default | `size:normal` |
| Challenging | Local, but it needs careful analysis to understand | `size:challenging` |
| Byzantine | It affects many components and needs careful analysis to understand | `size:byzantine` |

| Reach | When | Label |
|---|---|---|
| One area | The change stays in one area of the code, one package group or one stock subsystem | `reach:one-area` |
| Cross-cutting | The change spans several areas and needs coordination between them | `reach:cross-cutting` |

Reach follows Debian, which separates a single upload from a transition that moves many packages together, and Fedora, which separates a Self-Contained change from a System-Wide one. Complexity sets the depth of the documents. Reach sets the plan and the coordination. The plan's list of packages touched is checked against the reach.

## What each class changes

### The sections of a feature spec

One template serves every class, [templates/feature-spec.md](templates/feature-spec.md). Each section says which class requires it. A required section holds its content. Any other section holds its content or the one line `Not applicable: <reason>`, and a section that says Not applicable covers its subsections, which are then left out. The process document check refuses a required section that says Not applicable, in any wording: "Not applicable" with any punctuation, "because", "here" or "for this feature" after it, or "N/A". Only text that applies the section to something named, such as "Not applicable to clusters without the index", counts as content. The reviewer checks the claimed class.

| Class | Sections required in full |
|---|---|
| Every class | Purpose and scope with non-goals, the short architecture section, Feature class and switches, Feature requirements, Where problems could occur with its test plan, Decisions, Prior art (one line is enough at Low Hanging Fruit) |
| Normal size adds | Context and scope, Building blocks, Package dependencies and hook points, Milestones outline |
| Challenging and Byzantine size | Every section, the Glossary included |
| Cross-cutting reach adds | Dependencies, Risks, Milestones outline |
| Critical risk adds | Threat model and Compatibility, in full, and Dependencies when it adds a dependency |
| Normal risk adds | Threat model when the change adds new input or privilege, Compatibility when it touches a public interface or stock behaviour, Dependencies when it adds a dependency |

Compatibility in full means its parts: the statement that the feature changes no format, schema or protocol may stand in for the on-disk format changes only, and the mixed-version cluster, upgrade, rollback and runbook parts are still written. Non-goals are part of Purpose and scope and never say Not applicable.

The control table of the spec carries the class: rows Risk, Size and Reach, each with the level and its reason, and a row Touches naming what the change touches: a public interface, stock behaviour, new input or privilege, a new dependency, shared state (threads, pools or shared state), a request path (a read, write or query path), a new feature or switch, or none. The plan and the milestone reports repeat the spec's class. A design record and a fix record carry the class of their item.

### Checks and review

Before a document goes to review, its author runs independent checks on it in rounds: a comprehension check, an ambiguity check and a simplicity and reuse check. A round is clean when it finds nothing new that blocks, and the loop ends after two clean rounds in a row or at the round cap. The cap is set by the higher of size and risk.

| Class | Independent checks each round | Review lenses | Threat model and compatibility |
|---|---|---|---|
| Critical risk | All three | Every lens of the review mode, and every citation checked | In full |
| Normal risk | All three | For a document: correctness and documentation always, compatibility when a public interface or stock behaviour is touched, security for new input or privilege, compliance for a new dependency. For code: correctness, tests, documentation, maintainability and the review patterns always, and by what the change touches compatibility, security and compliance as for a document, concurrency for shared state, performance for a request path, observability for a new feature or switch. Every citation checked | Compatibility in full when the floor applies, the threat model in full for new input or privilege, else Not applicable with the reason |
| Low risk | Comprehension and ambiguity | Correctness and documentation | Not applicable |

| Higher of size and risk | Round cap |
|---|---|
| Low Hanging Fruit size or Low risk | 3 |
| Normal size or Normal risk | 5 |
| Challenging size | 8 |
| Byzantine size or Critical risk | 10 |

The author of the spec names what the change touches in the Touches row, and the reviewer checks it against the change. Drafting and review get more reasoning effort at Critical risk than at Normal, and Normal more than Low. An automated role's settings follow the class of its task.

### Stages and approvals

| Risk | Stages |
|---|---|
| Critical | Before drafting, the author asks the maintainers one question that confirms the class and the scope. Then the spec, the plan and the code, each merged by a maintainer. The security engineer reviews every code pull request. A release that carries the change needs the full upgrade and mixed-version tests |
| Normal | The spec, the plan and the code, each merged by a maintainer. The maintainer confirms the class when merging the spec |
| Low | No spec or plan stage. The work goes straight to a pull request whose body carries Where problems could occur and its test plan. A maintainer merges it |

A one-item change takes the same stages with its design record or fix record in place of the spec and plan. Only maintainers merge, at every level.

## Labels

The class is three label families on the issue, mirrored on each of its pull requests: one `risk:` label, one `size:` label and one `reach:` label.

1. The first contributor or role to pick up the issue sets the three labels, with a comment on the issue, next to the labels, that gives the reasons: the worst Bug Category, the floor if it applied, and why that size and reach. The comment is public, like the rest of the issue. For a feature that is the architect, for a Low risk fix the developer.
2. The reviewer checks the labels at every review, against the change and the reasons.
3. A maintainer confirms the class: through the class and scope question for Critical work, at the spec merge for Normal work, at the pull request merge for Low work. A maintainer may change any label at any time, and the change takes effect from the next step of the work.
4. Work that carries no class yet, or a family with no label or with two, is treated as the strictest value of that family: Critical, Byzantine and Cross-cutting.
5. A pull request check, required once the maintainers make it so, refuses a pull request that does not carry exactly one label of each family, as the kind label check does for the maintenance category. A release proposal or promotion pull request, which changes only `docs/releases/`, has no class, as it has no kind.

## Sources

1. Apache Cassandra, [JIRA Workflow Proposals](https://cwiki.apache.org/confluence/spaces/CASSANDRA/pages/97551605/JIRA+Workflow+Proposals): the Bug Category, Severity and Complexity fields, as used on the [CASSANDRA project in JIRA](https://issues.apache.org/jira/projects/CASSANDRA).
2. Apache Cassandra, [Cassandra Enhancement Proposals](https://cwiki.apache.org/confluence/spaces/CASSANDRA/pages/95652201/Cassandra+Enhancement+Proposals+CEP): the compatibility areas of a public interface.
3. Ubuntu, [Stable Release Updates, the bug template](https://ubuntu.com/project/docs/SRU/reference/bug-template/): its Test Plan and Where problems could occur sections.
4. Debian, [bug severity levels](https://www.debian.org/Bugs/Developer#severities) and the [release critical bug policy](https://release.debian.org/testing/rc_policy.txt).
5. Debian, [transitions](https://wiki.debian.org/Teams/ReleaseTeam/Transitions), and Fedora, [the Changes policy](https://docs.fedoraproject.org/en-US/program_management/changes_policy/) with its Self-Contained and System-Wide changes.
