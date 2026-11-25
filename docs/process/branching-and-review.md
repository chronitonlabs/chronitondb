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
2. The lines are protected. A change reaches a line only by pull request. Every required check MUST pass. Every commit the project makes MUST be signed, see [History rules](#history-rules). Only maintainers and committers merge, each within their rights. See [governance.md](governance.md). Nobody force pushes. A line is never deleted.
3. There are no feature branches and no milestone branches. Every item merges into its line once reviewed.

## Feature switches and defaults

The rules of this section are stated in full in [principles.md](principles.md), [PRINCIPLE-016](principles.md#principle-016) to [PRINCIPLE-020](principles.md#principle-020). Each item below keeps one sentence of its rule and the id.

1. A behaviour-changing feature always has a feature switch, and the switch is off by default. A feature built in more than one milestone always has a switch, whatever its class. So does a feature that sends, gossips, streams or commits anything a node without it cannot read, which is not used until every node has it. Any other purely additive feature has a switch only when something needs it to be turned off, and work with nothing to turn off has none: [PRINCIPLE-016](principles.md#principle-016). With a switch an operator can turn the feature off, and how the switch is set is the design's choice.
2. Before a feature's final milestone gate, its switch refuses to turn on, whatever its default. A feature built in more than one milestone always has that switch, so it cannot be reached before it is finished. See [PRINCIPLE-020](principles.md#principle-020).
3. A purely additive feature is reachable only through something stock Apache Cassandra does not have. For example new CQL syntax, a new index type, a new nodetool command, a new virtual table or a new setting. It is on by default: [PRINCIPLE-017](principles.md#principle-017). A statement that Apache Cassandra accepts as valid and refuses for a reason is stock behaviour, and a feature that makes it succeed is behaviour-changing: [PRINCIPLE-005](principles.md#principle-005). A cluster that does not use a purely additive feature behaves exactly as Apache Cassandra.
4. A behaviour-changing feature changes what an application sees from something stock Apache Cassandra already does: results, errors, warnings or the bytes on the wire. Its default MUST be off on every line, and operators opt in: [PRINCIPLE-017](principles.md#principle-017) and [PRINCIPLE-001](principles.md#principle-001). The performance of operations that do not use a feature has its own rule: [PRINCIPLE-052](principles.md#principle-052). A difference in what operators see does not by itself make a feature behaviour-changing: [PRINCIPLE-002](principles.md#principle-002). A fix to a defect in stock is not a feature and is not gated: [PRINCIPLE-004](principles.md#principle-004). See [quality-requirements.md](quality-requirements.md#compatibility-with-apache-cassandra).
5. An upgrade within a line changes what a running cluster does only through a fix, a security fix or an import from Apache Cassandra, each named in the release notes. A feature's default does not change within a line. A new purely additive feature arrives switched on, with one edge for a feature finished after its line's first release: [PRINCIPLE-018](principles.md#principle-018). See [release.md](release.md#what-a-release-may-contain).
6. The feature spec states the class of the feature and of each switch, with the reason, the default on each line and, for a behaviour-changing feature, the stock operations it changes. A maintainer approves the class with the spec. A feature that fits one item states the same in its design record.
7. With a feature off, the feature MUST change nothing that stock Apache Cassandra does, and the tests of the feature's off state prove it: [PRINCIPLE-019](principles.md#principle-019).
8. "Stock behaviour unchanged with the feature off" is a required property of every line, apart from the fixes to stock code and the differences in what operators see that the [delta register](../delta/README.md) lists. The parity suite proves it once it exists. See [testing.md](testing.md). The rule is [PRINCIPLE-020](principles.md#principle-020).
9. Every merged item keeps the line releasable. The switch of a feature built in more than one milestone hides its unfinished work. A feature with no switch merges no item that makes unfinished work reachable. See [PRINCIPLE-020](principles.md#principle-020).

## Work branches

1. Work branches are short lived. One branch carries one item for one line.
2. A work branch is named for the person or agent, the item's GitHub issue number, a short slug and the target line:
   - People: `<github-username>/<issue>-<slug>/<line>`, for example `octocat/42-disk-check/chronitondb-5.0`.
   - Automated agents: `agent/<issue>-<slug>/<line>`.
   - A design or fix record that is approved before the code starts has its own pull request, from a branch with `-design` added to the slug, for example `agent/42-disk-check-design/chronitondb-5.0`.
   - The pull requests of a large feature come from branches named for the feature's issue, with `-spec` added to the slug for the feature spec, `-plan` for the plan and delivery plan, and `-change-<k>` for a change control update. A release promotion's branch adds `-promotion` to the slug of its proposal's branch.
   - An automated agent also saves its unfinished work to a side branch of its work branch, with `checkpoint/` before the line, for example `agent/42-disk-check/checkpoint/chronitondb-5.0`, so a run that is cut off can resume. A checkpoint branch never has a pull request and is never merged. It is deleted a day after the item's pull requests are merged or closed.
3. Import branches have four forms: `import/cassandra-<x.y.z>/<line>` for a whole Apache release, named after its Apache release tag, `import/cassandra-<x.y>-<short hash>/<line>` for the weekly Apache branch merge, `import/CASSANDRA-<n>/<line>` for a single cherry-picked fix, and `import/<owner>-<repo>-<12 character hash>/<line>` for a single commit taken unchanged from another project. See [upstream.md](upstream.md).
4. People outside the project work on a fork of the repository and open a pull request from it. See [contributing.md](contributing.md). Today only maintainers create branches outside `agent/` in this repository. The integrator's `import/` branches wait until the project's automation is allowed to create them.
5. An item affected on several lines carries all of them. It gets one pull request per affected line, oldest line first, and is done when all of them are merged.

## History rules

1. A work branch is kept current by merging its line into it, for example with GitHub's **Update branch** button. A work branch is never rebased.
2. Nothing is ever force pushed, on any branch. During review, answers to findings are added as new commits.
3. Our own pull requests are squash merged. The line gets one signed commit whose subject is the pull request title, in Conventional Commits form. Merge commits on a work branch therefore never reach the line, and each line stays linear apart from imports.
4. Import pull requests, a whole Apache release or a single cherry-pick, are merged with a merge commit, so the imported commits keep their original author, message and cherry-pick line. These are the only merge commits on a line. See [upstream.md](upstream.md).
5. Rebase merging is not used. GitHub offers both squash and merge commits on every pull request, so the maintainer who merges picks the method by the kind of pull request.
6. Every commit the project makes is signed, on work branches and on lines: its own commits, the squash commit of a pull request, the commit of a cherry-pick and the merge commit of an import. The commits of Apache Cassandra's own history that the import of a release or a branch merges stay as Apache Cassandra made them, signed or not, and are never rewritten to add a signature: [PRINCIPLE-075](principles.md#principle-075). On the lines GitHub refuses an unsigned commit of ours. A maintainer with the Admin role MAY bypass the signature rule for the merge of an import of Apache Cassandra's own history, through the import's pull request, and for nothing else. On work branches and forks signing is every contributor's own rule.

## Tags

1. A release tag is created only after a maintainer approves that release.
2. Every release tag is signed with the dedicated ChronitonDB release key, whose public key is published for users. No person's own key signs a release tag.
3. A tag is never moved or deleted.
4. Anything that installs or releases from a tag verifies its signature first.

A release tag is the version itself, for example `5.0-chronitondb3`. It cannot clash with Apache's own tags, which start with `cassandra-`. A release candidate tag adds `-rc<k>`, for example `5.0-chronitondb3-rc1`, since git does not allow `~` in a tag name. Release tags are signed with the dedicated ChronitonDB release key, not a person's key. See [release.md](release.md#version-numbers).

## Required checks

These checks run on every pull request to a line. Each MUST pass before a maintainer can merge.

| Check | What it checks |
|---|---|
| `ant-check` | Apache Cassandra's own checks: licence headers (RAT), checkstyle and the rest of `ant check` |
| `shape` | The shape limits on ChronitonDB Java code. See [conventions.md](conventions.md#shape-limits). The script and the rules come from the line, never from the pull request |
| `semgrep` | Banned APIs, unsafe process and deserialisation calls, non-ASCII identifiers and bidirectional control characters. The script and the rules come from the line, never from the pull request. On an import from Apache Cassandra, a finding in Apache Cassandra's own code is reported for the import's assessment and does not fail the check: [PRINCIPLE-074](principles.md#principle-074) |
| `spotbugs` | SpotBugs with FindSecBugs on the compiled ChronitonDB classes. Findings are reported. The check fails when its self-test fails. The script and the rules come from the line, never from the pull request |
| `shape-tests` | The self-test of the shape check, as the pull request changes it |
| `semgrep-tests` | The self-test of the Semgrep check, as the pull request changes it |
| `spotbugs-tests` | The self-test of the SpotBugs check, as the pull request changes it |
| `instruction-files` | No instruction files for automated coding tools anywhere in the tree, such as `AGENTS.md`, in any case of letters |
| `license/cla` | Every contributor to the pull request has signed the contributor agreement. See [contributing.md](contributing.md) |
| `kind-label` | The pull request carries exactly one kind label. See [README.md](README.md) |
| `class-label` | The pull request carries exactly one `risk:`, one `size:` and one `reach:` label. See [classification.md](classification.md) |
| `pr-title` | The pull request title, the subject of its commit on the line, follows the Conventional Commits rules and the import forms of [conventions.md](conventions.md#commit-messages). The checker and the rules come from the line. A title of type `import` is taken only from an `import/` branch of this repository. The check also refuses a commit message or a description that names an AI tool or model as a co-author, links a session of an AI tool or says a tool generated the text. See [conventions.md](conventions.md#trailers) |
| `subjectlint-tests` | The unit tests of the subject checker, as the pull request changes it |
| `documents` | The process documents and feature keys the pull request changes: the template rules, the Contents index of each document (see [conventions.md](conventions.md#contents-index-of-process-documents)), its revision history (see [conventions.md](conventions.md#versions-and-revision-history)), the id and place of each new decision record, the areas and the source each document names (see [areas.md](areas.md)), the generated indexes and the document graph (see [conventions.md](conventions.md#generated-indexes) and [conventions.md](conventions.md#the-document-graph)), the clarification markers and the feature key and requirement id rules in [additive.md](additive.md#feature-keys-and-requirement-ids). The checker and the templates come from the line, never from the pull request |
| `doclint-tests` | The unit tests of the process document checker, as the pull request changes it |
| `stock-tests` | A pull request that changes a pre-existing test file of Apache Cassandra does so in one of the four ways of [PRINCIPLE-013](principles.md#principle-013), by an import or with the merged record of its own issue that permits the change, while that issue is open and the permit is unused. See [testing.md](testing.md#policy). The checker and the records come from the line, never from the pull request |
| `delta-register` | A pull request that changes a stock file adds or updates its entry in the [delta register](../delta/README.md#keeping-it-current), and each entry it adds or changes is in its template's form with its index row. The checker and the rules come from the line, never from the pull request |
| `import-history` | A pull request from an `import/` branch of this repository brings Apache Cassandra's own history, or one commit taken unchanged, and changes no other file of Apache Cassandra. A conflict resolved by hand waits for a maintainer's approving review. See [upstream.md](upstream.md#the-import-history-check). The checker and the rules come from the line, never from the pull request |
| `importlint-tests` | The unit tests of the import history checker, as the pull request changes it |
| `review-verdict` | Where a review verdict is due, the newest review of the project's review App on the pull request is a clean verdict on the commit the pull request is at now, and nobody edited it. A review of the App with no verdict in it fails the check: the App posts nothing but verdicts, so an older verdict never counts in its place. A clean verdict says the pull request is ready, every checklist it ran passed, and no blocker and no major finding is open. A verdict with such a finding open fails the check until a later verdict on that commit is clean, and a waived finding counts once a new verdict of the reviewer records the waiver. A verdict is due on a pull request the project's automation wrote, told by the id of its author, and on one a maintainer of [docs/governance/committers.md](../governance/committers.md) accepted with the label `triage:accepted`: only a maintainer's events of that label count, and the newest of them decides. Any other pull request passes. A review of any other account is no verdict. See [The review record](#the-review-record). The checker, the list of maintainers and the file that names the App and the automation's accounts, `tools/chronitondb/review-app.json`, come from the line, never from the pull request |
| `reviewlint-tests` | The unit tests of the review verdict checker, as the pull request changes it |
| CodeQL | GitHub's code scanning default setup, configured in the repository's settings, not by a workflow in this tree. Blocks on high or critical security alerts and on errors |

The `kind-label` and `class-label` checks pass a release proposal or promotion pull request, which changes only `docs/releases/` and carries no kind or class. The `documents` check runs on every pull request, a person's or an agent's, and passes one that changes no file under `docs/` or `test/bdd/`.

On each push to a line, the `line-subjects` check runs the same rules on the subject of every new commit on the line. It cannot block a merge that has happened. It fails the run on that commit, and GitHub notifies the maintainer who merged.

Apache's Build Scripts check also runs on pull requests that touch `.build/` or the workflows, and Apache's CI Check on pull requests that touch `.jenkins/` or the CI scripts under `.build/`. Both are advisory, since a check filtered by path cannot be required. Apache Cassandra's workflow files are its own and are not edited. They declare no permissions, so their jobs get the repository's default token: the maintainers keep that default read only in the repository's settings.

The parity suite becomes a required check once it exists.

Workflow runs on pull requests from first time and outside contributors wait for a maintainer's approval before they start.

## Sensitive paths

A change to a sensitive path requests a review from the code owners in `.github/CODEOWNERS`. The sensitive paths are:

1. Authentication, transport, network and security code: `src/java/org/apache/cassandra/auth/`, `transport/`, `net/`, `security/`, `service/ClientState.java`, and the authentication and network code under `org/chronitondb/`.
2. The build and its inputs: `build.xml`, `.build/`, `lib/`.
3. Configuration and packaging: `conf/`, `bin/`, `packaging/`, `debian/`, `redhat/`. `packaging/` does not exist yet. The pull request that creates it adds it to `.github/CODEOWNERS`.
4. The project's own tooling and automation: `tools/chronitondb/`, `.github/`, `CODEOWNERS`. The checks of a pull request run from these folders, and a pull request runs the workflow files it brings, so the maintainers are their code owners. Once the ruleset of each line requires code owner review, a pull request that changes a file under `.github/` or `tools/chronitondb/` merges only with an approving review from a code owner of that path in `.github/CODEOWNERS`. The rule binds only while the team that owns a path has write access to the repository: GitHub ignores an owner without it, and a path whose only owner is ignored needs no review. So the maintainers' team keeps write access, and the ruleset also dismisses an approval when a new commit is pushed.

## Two tiers

The files a change touches pick its tier. A change that touches a file on [the paths of the Critical floor](classification.md#the-paths-of-the-floor) takes the full path. The full path is the process the other sections and pages describe. The short path follows Ubuntu's stable release update: one record in a fixed form, one independent review, and a merge by someone other than the author.

The short path is for a change to code, tests or the files that guard the process that touches no path of the floor and has no lighter path of its own. Low risk work, a change to documentation only, a dependency patch-version update, a release proposal and an import from Apache Cassandra keep their own paths and rules, and need no short record.

1. A program gives its answer: `tools/chronitondb/doclint.py tier --repo . --base origin/<line>` prints the tier and the files that set it. It reads the paths of the floor from the line before the change, never from the pull request, so a pull request that edits the table cannot lower its own tier.
2. The tier of a change is the higher of the program's answer and any raise by a maintainer. A maintainer MAY raise a change to the full path at any time. Nobody lowers the tier.
3. A change whose risk is Critical takes the full path, whatever the program answers, as [classification.md](classification.md#stages-and-approvals) says. The class labels stay as [classification.md](classification.md#labels) sets them. On the short path the tier picks the stages, not the class.
4. The files that guard the process, as [classification.md](classification.md#the-floor) lists them, are not on the floor. A change to them on the short path is held by three controls:
   1. The ruleset of each line requires an approving review from a code owner. `.github/CODEOWNERS` names the maintainers as the owners of `.github/`, `tools/chronitondb/` and the process pages, and the sensitive reviewers as the owners of `build.xml`, `.build/`, `lib/`, `conf/` and `bin/`. It names no owner for `.circleci/` and `.jenkins/`.
   2. The review of the short path includes a security read.
   3. The tier is read from the line before the change, never from the pull request.

### The short path

1. Before writing, the author asks the maintainers the visible choices of the change, such as names, defaults and what an operator sees. The author asks once, in one batch, and records each answer in the short record.
2. The change is one pull request. It carries the short record, the code and the tests together. The short record is written from [templates/short-record.md](templates/short-record.md) and lives where [conventions.md](conventions.md#where-things-live) says.
3. A short path change that must change a pre-existing test file of Apache Cassandra gets that change permitted first, in its own small pull request, as [testing.md](testing.md#policy) says.
4. One independent review covers the record, the code and the tests. It includes a security read. The reviewer is never the author.
5. The reviews posted on the pull request are the review record. No review record file is kept. The reviewer posts its findings. The author answers each with the commit that fixes it. The reviewer posts its final verdict on the head commit.
6. A confirmation pass is needed only when the author changes something after a clean verdict. It runs as [Review rounds](#review-rounds) says.
7. A maintainer merges.

## Reviews

Reviews follow ISO/IEC 20246. A pull request the project's own automation wrote, or one a maintainer accepted for review with the label `triage:accepted`, is reviewed by the project's review roles before a maintainer merges it. Imports and dependency updates the automation wrote are among them. A maintainer's own pull request, and an outside contributor's that no maintainer accepted, have no such verdict: a maintainer reviews them directly. A review by the project's review roles never runs on submission alone. See [contributing.md](contributing.md#checks-and-review). Where the review roles review, the reviewer's verdict for each round is posted on the pull request as one short review, by the project's review App. The findings of a pull request on the full path that the project's own automation wrote are kept in the review record, a file that pull request commits. On any other pull request, one on the short path and an outside contributor's among them, the verdict's own review comment for the round carries the findings, one row for each finding, and no committed review record is kept: see [The review record](#the-review-record). A maintainer reads the verdict and the findings and then merges, or requests changes.

The table says who reviews a pull request that the review roles review. On any other pull request the maintainer who reviews it is the reviewer, and what these pages ask the reviewer to check, that maintainer checks.

| Work product | Review type | Reviewed by | Approver |
|---|---|---|---|
| Code pull request | Inspection | Reviewer | Maintainer |
| Design record or fix record | Technical review | The designer's own check of the design against the code and a scope review, then the reviewer | Maintainer |
| Feature spec, plan, delivery plan, milestone report | Technical review | Reviewer, then the maintainer, with the architect as author | Maintainer |
| Import pull request | Inspection of the imported diff | Reviewer | Maintainer |
| Dependency update | Inspection | Reviewer | Maintainer |
| Release proposal and promotion | Technical review | Reviewer | Maintainer |
| Research report | Technical review | Reviewer | Maintainer |

### The inspection of a code pull request

1. The pull request opens as a draft.
2. The reviewer inspects it against the approved design record, or the short record it carries on the short path, and the review checklists: correctness, concurrency, security, compatibility, tests, observability, performance, documentation, compliance and maintainability, and a set of known bug patterns adapted from Apache Cassandra's own targeted review.
3. Each finding has a severity: blocker, major, minor or nit.
4. The reviewer posts its verdict as one short review, with the count of findings at each severity, and gives the author the findings. A review is clean when it says the pull request is ready, every checklist it ran passed, and no blocker and no major finding is open.
5. Where a review record is kept, the author closes it after the clean review, and the reviewer reads the commits made since in one confirmation pass: see [Review rounds](#review-rounds). The clean verdict on the commit the pull request is at marks the pull request ready.
6. A maintainer then approves and merges, or requests changes with the rework listed.

### Two review standards, picked by file

1. **Stock Apache Cassandra files** get the strict Apache review: the smallest diff that does the job, and a new helper only where it lets fork code share stock logic in place of a copy. The tests of an approved fix to stock extend the existing stock test classes. A feature's tests go in its own files and leave the stock test files as they are, see [testing.md](testing.md#policy). A behaviour change that belongs to a feature sits behind the feature's switch. A fix to a defect in stock is applied and is not gated: it carries its fix record, its delta entry and a release note. It is a fix only once the maintainers have merged its fix record. See [maintenance.md](maintenance.md#corrective-fixing-a-fault). A stock file that imports ChronitonDB code is a hook point: it MUST be listed in the feature spec with its delta entry. The rules are [PRINCIPLE-009](principles.md#principle-009), [PRINCIPLE-010](principles.md#principle-010), [PRINCIPLE-013](principles.md#principle-013) and [PRINCIPLE-004](principles.md#principle-004).
2. **New ChronitonDB files** are reviewed against their approved design. Every other check still applies.

### Review rounds

1. The author answers each finding with its own commit that names the finding, so a reviewer can drop one without the rest, or with the reason no change is made: as a disposition in the review record, or in a reply to the round's review comment where no review record is kept.
2. A work product gets at most three review rounds. After the third round, the open points go to a maintainer as a decision.
3. A commit made on a pull request after the newest clean verdict needs one confirmation pass before the merge. After a clean verdict the author MAY fix the minor findings and the nits of that round, one commit for each finding, and closes the review record. The commits that only close the record and write its generated index pages again are covered by the same pass. The author closes the record before asking for the pass, so the pull request does not change again after it.
4. A confirmation pass is not a review round and does not count toward the three. The reviewer reads only the commits made since the commit the clean verdict names, and reopens no finding that is settled. Each commit made since is a fix of one finding of the clean round, inside the files that round read, or a commit that closes the record. A commit that closes the record changes only the review record of that pull request and the generated index pages. The reviewer reads every commit that is not such a closing commit, with the checklists that read the round. Where the security engineer read the round, it reads the fixes too, before the reviewer does.
5. The reviewer posts the result as a new verdict on the commit the pull request is now at. The verdict names the commit it confirms from. When every commit made since is a fix or closes the record, the verdict is clean and the `review-verdict` check passes on it. When a commit does more, such as a new claim, a new requirement or a change to a file the round did not read, the verdict is not clean and the open points go to a maintainer as a decision, as after a third round. A pass that could not be run, because a commit could not be read, is run again and posts no verdict.
6. There is one confirmation pass for a clean round. A commit made after it goes to a maintainer as a decision the same way, and no review round follows a clean verdict by itself. A maintainer who wants a change after a clean verdict requests changes on the pull request: that starts a review round while one of the three is left, and its clean round gets its own confirmation pass. After a third round no round is left, and a commit made for such a request gets the confirmation pass if it is not used yet, and otherwise goes to a maintainer as a decision. With no commit since the clean verdict there is no pass, and the clean verdict stands.

### The review record

The record of the review of a pull request on the full path that the project's own automation wrote is a file that pull request commits, `docs/reviews/<work>.md`, written from [templates/review-record.md](templates/review-record.md), after the review record of ISO/IEC 20246. Only the project's own automation keeps this committed file. On a pull request of any other author, an outside contributor's among them, and on any pull request on the short path, see [The short path](#the-short-path), the verdict's own review comment for the round carries the findings, one row for each finding, and no committed review record is kept.

1. The automation that wrote the pull request writes the record and keeps it current: when the pull request opens, after each review round and after the last one. After a clean round it closes the record, and the exit decision then says in one line which commit the clean round read and which findings were fixed after it. The confirmation pass covers the commits that close the record, and the record is not written again after the pass. It holds the rounds, each finding with its severity, its source and what was done about it, the decisions the maintainers took, what a round did not read, and the exit decision. The source is the checklist that raised the finding, or the security engineer's review. On Critical risk work the security engineer posts nothing on the pull request: its findings go to the reviewer, the reviewer's verdict counts them, and each stands in the record as a row like any other.
2. The reviewer is never the author. The reviewer's verdict for each round is one short review of the pull request, posted by the project's review App: the verdict, the count of findings at each severity and the commit it read. No account that writes a pull request holds the App's key. Where the key is kept, and which runs may ask the App for a verdict, is a matter of how the project deploys its roles, not something GitHub enforces. The check proves that the App's user posted the verdict on the commit the pull request is at and that nobody edited it since. It does not prove which run asked the App to post it. A verdict is due where a review runs: on a pull request the project's automation wrote, and on one that carries the label `triage:accepted` set by a maintainer. There the `review-verdict` check passes only when the newest review of the App is a clean verdict on the commit the pull request is at now, and nobody edited it after it was posted. A review of the App with no verdict in it fails the check: the App posts nothing but verdicts, so an older verdict never counts in its place. A clean verdict says the pull request is ready, every checklist it ran passed, and no blocker and no major finding is open. A verdict with such a finding open leaves the check failed until a later verdict on that commit is clean. The check reads no waiver: when a maintainer waives a finding, the reviewer posts a new verdict that records the waiver, and that verdict is the one the check reads. A later commit needs a new verdict. After a clean verdict that is the verdict of the one confirmation pass, see [Review rounds](#review-rounds), which is posted the same way and also names the commit it confirms from. On any other pull request the check passes and says that no verdict is due. The check only reads: it starts no review. Where the automation wrote a pull request on the full path, the pull request carries no findings: they stand in the committed review record, which is the record of the review. The project's own roles work from it, and the author answers in the record and by commits, never in a comment. On any other pull request the verdict's own review comment for the round carries the findings, one row for each finding, and the author answers by commits and in replies to that comment.
3. Where a record is kept, the reviewer checks each row of it against its own findings.
4. Only the maintainers waive a finding or take a decision the review raises. A waiver or a decision counts only as one whole line in a set form, outside a code block and outside a quotation, with at most three spaces before it: `Waived: R1-3` for a waiver and `Decided: D1 B` for a decision. A line set in by four spaces or more or by a tab is a code block and counts for nothing. So does a line inside an HTML comment, inside a `<pre>` or a `<details>` block, and a line straight after a quoted line with no blank line between. A waiver line names the finding by its id and may name several, as in `Waived: R1-3, R1-4 and R2-1`. A decision line names the decision by its id and the letter that the Chosen line of the review record gives. A reason may follow on the same line after a full stop, as in `Waived: R1-3. A known limit.` The line is written by a maintainer listed in [docs/governance/committers.md](../governance/committers.md) on the line, in a comment or a review on the pull request, posted after the review that raised the finding, and edited by nobody else. Any other wording counts for nothing, whoever writes it.
5. The maintainer's decision is made through GitHub: approve, or request changes with the rework listed, and the merge.
6. The review record of a security fix is kept in its private advisory and stays there, private, after disclosure too. It is no file of the branch that lands. At disclosure the public line gets the fix and its fix record, and the fix record says in one line that the fix was reviewed under the private process: [PRINCIPLE-048](principles.md#principle-048).

## Pull requests

1. The pull request title uses Conventional Commits form. It becomes the commit subject on the line. See [conventions.md](conventions.md).
2. The body follows the organisation's pull request template: what and why, how it was tested, other branches, and the checklist. A pull request from an automated agent opens with a short block for the maintainer, what it needs from them, a summary and what to check before merging, and puts the rest under Details.
3. ChronitonDB adds to it: the impact, waived findings with their reasons, the upgrade and rollback story, the default of any new setting and why, which tests prove which claim, a per-line differences table when the change exists on both lines, and `Fixes #<issue>`. A change made on several lines writes `Fixes #<issue>` only on the newest line's pull request, which merges last, and `Part of #<issue>` on the others, so the issue closes when the last line has the change.
4. The body describes the final change, never the order of the work. It is kept current at every push.

## Commit messages and trailers

Commit messages follow [conventions.md](conventions.md#commit-messages). In short:

1. Conventional Commits form, `type(scope): description`.
2. A person MAY add an `Assisted-by:` trailer naming the AI tool used, as the organisation's guide describes.
3. A commit written by an automated agent carries two trailers: `Assisted-by: <tool>:<model>` and `Requested-by: <GitHub username> <GitHub no-reply address>` of the maintainer who asked for the work. For work items from an approved plan, that is the maintainer who approved the plan. For an item opened from one of the project's scheduled checks, it is the maintainer who set up that check.
