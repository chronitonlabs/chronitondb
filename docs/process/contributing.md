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

# Contributing to ChronitonDB

This page is for people outside the project who want to raise an issue or contribute a change. It adds ChronitonDB's rules to the [Chroniton Labs contributing guide](https://github.com/chronitonlabs/.github/blob/main/CONTRIBUTING.md), which applies to every Chroniton Labs project. The short ChronitonDB guide is in [.github/CONTRIBUTING.md](../../.github/CONTRIBUTING.md).

The `CONTRIBUTING.md` at the top of this repository is Apache Cassandra's guide. It still applies to building, testing and code style in stock files, except where these pages say otherwise.

## Raising an issue

### Ideas and questions

Ideas, questions and anything you want to discuss before writing code start in the organisation's [GitHub Discussions](https://github.com/orgs/chronitonlabs/discussions). A feature idea that the maintainers agree to take on becomes an issue. A large one becomes a feature spec, as described in [additive.md](additive.md).

### Bugs and agreed work

Bugs and agreed pieces of work go in the project's [GitHub Issues](https://github.com/chronitonlabs/chronitondb/issues), not the Apache Cassandra JIRA. A bug report SHOULD include:

1. The ChronitonDB version and line, or the commit you built.
2. The Java version and operating system.
3. The steps to reproduce it, as small as you can make them: the schema, the statements and the settings that differ from the defaults.
4. What you expected and what happened.
5. The relevant log lines and stack traces.
6. Whether the same steps fail on the matching Apache Cassandra release, if you know.

### Security problems

Never report a security problem in a public issue, pull request or discussion. Report it privately through GitHub: open the **Security** tab of the repository and choose **Report a vulnerability**. See [security.md](security.md) and the [Chroniton Labs security policy](https://github.com/chronitonlabs/.github/blob/main/SECURITY.md).

## Contributing a change

### Before you start

1. Talk to us first for anything larger than a small fix, so the approach can be agreed before you write the code.
2. Sign the contributor agreement. Every individual contributor signs the Chroniton Labs Individual Contributor Assignment Agreement, and an employer that owns rights in the contribution signs the Entity Contributor Assignment Agreement. The agreements are in [contributor-agreements](https://github.com/chronitonlabs/contributor-agreements). The CLA Assistant check runs on every pull request. A pull request cannot be merged until every contributor to it has signed.

### Making the change

1. Fork the repository and work on a branch in your fork, named `<github-username>/<issue>-<slug>/<line>`.
2. Base the branch on the line the change is for, `chronitondb-5.0` or `chronitondb-6.0`. A fix needed on several lines gets one pull request per affected line, oldest line first. Open yours against the oldest affected line and say in it which other lines need the fix. A maintainer opens the pull requests for the other lines.
3. Keep the branch current by merging its line into it, for example with GitHub's **Update branch** button. Do not rebase it, and never force push.
4. Sign every commit.
5. Follow [conventions.md](conventions.md): commit messages in Conventional Commits form, code layout and style, licence headers, names.
6. Follow [branching-and-review.md](branching-and-review.md) for history rules and pull requests.

### What a pull request needs

1. **Its category or its feature.** Say which maintenance category the change is (corrective, preventive, adaptive, perfective or additive), or name the feature spec item it delivers. See [README.md](README.md).
2. **An issue.** Link it with `Fixes #<issue>`.
3. **Tests.** A fix includes a test that fails without it and passes with it. A new behaviour includes tests for each of its requirements. See [testing.md](testing.md).
4. **Documentation.** User and operator documentation and runbook entries the change affects, in the same pull request.
5. **A delta entry,** if the change touches stock Apache Cassandra code or behaviour. See [the delta register](../delta/README.md).
6. **A title and commits** in Conventional Commits form. The title becomes the commit subject on the line.
7. **The pull request template,** filled in.

Changes that need a design record follow [maintenance.md](maintenance.md) or [additive.md](additive.md). The maintainers will say if your change needs one before review.

### Checks and review

1. Workflow runs on pull requests from first time and outside contributors wait for a maintainer's approval before CI runs.
2. Your pull request runs the GitHub checks and the tests of the changed areas on GitHub's own runners. The required checks MUST pass. See [branching-and-review.md](branching-and-review.md#required-checks) and [testing.md](testing.md#full-test-suites).
3. Changes to sensitive paths need a review from a code owner. See [branching-and-review.md](branching-and-review.md#sensitive-paths).
4. The reviewer reviews your pull request first and posts its review on it. Review follows [branching-and-review.md](branching-and-review.md#reviews). Answer each finding with its own commit.
5. Only maintainers and committers merge, after the review is posted. See [governance.md](governance.md).

### AI assistance

AI-assisted contributions are welcome. You are responsible for every line you submit. You MAY note AI assistance with an `Assisted-by:` trailer, as the organisation's guide describes.

## Becoming a committer

[governance.md](governance.md) sets out how commit rights work: who may merge into the lines, how someone is nominated and accepted, and how rights lapse or are removed.

## Code of conduct

ChronitonDB follows the [Contributor Covenant, version 2.1](https://www.contributor-covenant.org/version/2/1/code_of_conduct/). It applies in every project space: issues, pull requests, discussions and any other channel. Report conduct concerns to the contact named in the organisation's `CODE_OF_CONDUCT.md`.
