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

# Branching and review

ChronitonDB uses trunk-based development. Each line is a trunk. Work reaches a line only through a reviewed pull request that a maintainer merges.

## The lines

| Line | Based on | Use |
|---|---|---|
| `chronitondb-5.0` (default branch) | Apache Cassandra 5.0 | The ChronitonDB 5.0 line |
| `chronitondb-6.0` | Apache Cassandra 6.0 | The ChronitonDB 6.0 line |

1. There is one line per Apache Cassandra major version. A new line is added when the maintainers decide to follow a new Apache major version.
2. The lines are protected. A change reaches a line only by pull request. Every required check MUST pass. Every commit MUST be signed. Only maintainers and committers merge, each within their rights. See [governance.md](governance.md). Nobody force pushes. A line is never deleted.
3. There are no feature branches and no milestone branches. Every item merges into its line once reviewed.

## Every fork feature is off by default

1. Every fork feature sits behind its feature switch: a yaml setting and a nodetool toggle.
2. Before the feature's final milestone gate, the switch refuses to turn on.
3. After the gate, operators MAY turn the feature on with yaml or nodetool. Its default stays off for the life of the line.
4. A feature's default MAY be on only in a new line. Upgrading within a line never changes behaviour by itself. See [release.md](release.md#what-a-release-may-contain).
5. With a feature off, the line MUST behave exactly as stock Apache Cassandra: new CQL syntax is refused, no new files are written, no new threads start and no new memory is used.
6. "Stock behaviour unchanged with the feature off" is a required property of every line. The parity suite proves it. See [testing.md](testing.md).
7. Every merged item keeps the line releasable. The switch hides unfinished work.

## Work branches

1. Work branches are short lived. One branch carries one item for one line.
2. A work branch is named for the person or agent, the item's GitHub issue number, a short slug and the target line:
   - People: `<github-username>/<issue>-<slug>/<line>`, for example `octocat/42-phrase-query/chronitondb-5.0`.
   - Automated agents: `agent/<issue>-<slug>/<line>`.
   - A design or fix record that is approved before the code starts has its own pull request, from a branch with `-design` added to the slug, for example `agent/42-phrase-query-design/chronitondb-5.0`.
3. Import branches have three forms: `import/<release>/<line>` for a whole Apache release, `import/cassandra-<x.y>-<short hash>/<line>` for the weekly Apache branch merge, and `import/CASSANDRA-<n>/<line>` for a single cherry-picked fix. See [upstream.md](upstream.md).
4. People outside the project work on a fork of the repository and open a pull request from it. See [contributing.md](contributing.md).
5. An item affected on several lines carries all of them. It gets one pull request per affected line, oldest line first, and is done when all of them are merged.

## History rules

1. A work branch is kept current by merging its line into it, for example with GitHub's **Update branch** button. A work branch is never rebased.
2. Nothing is ever force pushed, on any branch. During review, answers to findings are added as new commits.
3. Our own pull requests are squash merged. The line gets one signed commit whose subject is the pull request title, in Conventional Commits form. Merge commits on a work branch therefore never reach the line, and each line stays linear apart from imports.
4. Import pull requests, a whole Apache release or a single cherry-pick, are merged with a merge commit, so the imported commits keep their Apache author, message and cherry-pick line. These are the only merge commits on a line. See [upstream.md](upstream.md).
5. Rebase merging is not used.
6. Every commit is signed, on work branches and on lines.

## Tags

1. A release tag is created only after a maintainer approves that release.
2. Every release tag is signed with the dedicated ChronitonDB release key, whose public key is published for users. No person's own key signs a release tag.
3. A tag is never moved or deleted.
4. Anything that installs or releases from a tag verifies its signature first.

A release tag is the version itself, for example `5.0.10-chronitondb1`, next to Apache's own `cassandra-5.0.10` tag. A release candidate tag adds `-rc<k>`, for example `5.0.10-chronitondb1-rc1`, since git does not allow `~` in a tag name. Release tags are signed with the dedicated ChronitonDB release key, not a person's key. See [release.md](release.md#version-numbers).

## Required checks

These checks run on every pull request to a line. Each MUST pass before a maintainer can merge.

| Check | What it checks |
|---|---|
| `ant-check` | Apache Cassandra's own checks: licence headers (RAT), checkstyle and the rest of `ant check` |
| `shape` | Google Java Style and the shape limits on ChronitonDB Java code. See [conventions.md](conventions.md) |
| `semgrep` | Banned APIs, unsafe process and deserialisation calls, non-ASCII identifiers and bidirectional control characters |
| `spotbugs` | SpotBugs with FindSecBugs on the compiled ChronitonDB classes. Findings are reported. The check fails when its self-test fails |
| `instruction-files` | No instruction files for automated coding tools anywhere in the tree, such as `AGENTS.md` |
| CodeQL | Code scanning. Blocks on high or critical security alerts and on errors |

Apache's Build Scripts check also runs on pull requests that touch `.build/` or the workflows. It is advisory, since a check filtered by path cannot be required.

The parity suite becomes a required check once it exists.

Workflow runs on pull requests from first time and outside contributors wait for a maintainer's approval before they start.

## Sensitive paths

A change to a sensitive path requests a review from the code owners in `.github/CODEOWNERS`. The sensitive paths are:

1. Authentication, transport, network and security code: `src/java/org/apache/cassandra/auth/`, `transport/`, `net/`, `security/`, `service/ClientState.java`, and the authentication and network code under `org/chronitondb/`.
2. The build and its inputs: `build.xml`, `.build/`, `lib/`.
3. Configuration and packaging: `conf/`, `bin/`, `packaging/`, `debian/`, `redhat/`.
4. The project's own tooling and automation: `tools/chronitondb/`, `.github/`, `CODEOWNERS`.

Query parsing and analyzers are not sensitive paths.

## Reviews

Reviews follow ISO/IEC 20246. Every pull request is reviewed by the reviewer first: our own, outside contributors', imports and dependency updates. The reviewer posts its review on the pull request. A maintainer reads it and then merges, or requests changes.

| Work product | Review type | Reviewed by | Approver |
|---|---|---|---|
| Code pull request, from anyone | Inspection | Reviewer | Maintainer |
| Design record or fix record | Technical review | The designer's own check of the design against the code and a scope review, then the reviewer | Maintainer |
| Feature spec, plan, delivery plan, milestone report | Technical review | Reviewer, then the maintainer, with the architect as author | Maintainer |
| Import pull request | Inspection of the imported diff | Reviewer | Maintainer |
| Dependency update | Inspection | Reviewer | Maintainer |
| Release proposal and promotion | Technical review | Reviewer | Maintainer |

### The inspection of a code pull request

1. The pull request opens as a draft.
2. The reviewer inspects it against the approved design record and the review checklists: correctness, concurrency, security, compatibility, tests, observability, performance, documentation, compliance and maintainability.
3. Each finding has a severity: blocker, major, minor or nit.
4. The reviewer posts the review as a comment with a verdict. A clean review marks the pull request ready.
5. A maintainer then approves and merges, or requests changes with the rework listed.

### Two review standards, picked by file

1. **Stock Apache Cassandra files** get the strict Apache review: the smallest diff that does the job, no new helpers, existing tests extended in place, every behaviour change behind a switch.
2. **New ChronitonDB files** are reviewed against their approved design. Every other check still applies.

### Review rounds

1. The author answers each finding with its own commit that names the finding, so a reviewer can drop one without the rest.
2. A work product gets at most three review rounds. After the third round, the open points go to a maintainer as a decision.

### The review record

The record of a review lives on the pull request: the reviewer's comment with its findings and verdict, then the maintainer's decision through GitHub (approve, or request changes with the rework listed) and the merge.

## Pull requests

1. The pull request title uses Conventional Commits form. It becomes the commit subject on the line. See [conventions.md](conventions.md).
2. The body follows the organisation's pull request template: what and why, how it was tested, other branches, and the checklist.
3. ChronitonDB adds to it: the impact, waived findings with their reasons, the upgrade and rollback story, the default of any new setting and why, which tests prove which claim, a per-line differences table when the change exists on both lines, and `Fixes #<issue>`.
4. The body describes the final change, never the order of the work. It is kept current at every push.
5. After the line is merged into the work branch, one short comment gives the line commit merged in, what it touched and the tests run.

## Commit messages and trailers

Commit messages follow [conventions.md](conventions.md#commit-messages). In short:

1. Conventional Commits form, `type(scope): description`.
2. A person MAY add an `Assisted-by:` trailer naming the AI tool used, as the organisation's guide describes.
3. A commit written by an automated agent carries two trailers: `Assisted-by: <tool>:<model>` and `Requested-by: <GitHub username> <GitHub no-reply address>` of the maintainer who asked for the work. For work items from an approved plan, that is the maintainer who approved the plan. For an item opened from one of the project's scheduled checks, it is the maintainer who set up that check.
