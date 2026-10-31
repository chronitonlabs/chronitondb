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

# Conventions

This page lists the repository and code conventions of ChronitonDB. They add to the [Chroniton Labs contributing guide](https://github.com/chronitonlabs/.github/blob/main/CONTRIBUTING.md), which applies to every Chroniton Labs project. Branches, merging and reviews are in [branching-and-review.md](branching-and-review.md).

Two kinds of file follow different rules:

1. A **ChronitonDB file** is a file ChronitonDB adds.
2. A **stock file** is any file that came from Apache Cassandra, edited or not.

## Commit messages

ChronitonDB uses Conventional Commits. This is a project rule on top of the organisation's general commit message guidance.

### Subject

1. The subject has the form `type(scope): description`.
2. The description is imperative and in plain words, for example `feat(fulltext): add the phrase operator`.
3. The subject is at most 72 characters.
4. The subject never lists files. A subject such as `Update <path>`, as GitHub writes for a suggestion, is refused. Apply suggestions locally with a real subject.
5. The scope names the area of the change, for example `fulltext`, `analyzer`, `build` or `github`.

### Types

| Type | Use | In release notes |
|---|---|---|
| `feat` | A new feature or user visible capability | Yes |
| `fix` | A fault fixed | Yes |
| `perf` | A performance improvement | Yes |
| `security` | A security fix, used only after the advisory is public. Before that, a security fix uses `fix` with a neutral description | Yes, in its own section |
| `import` | A change taken from Apache Cassandra | Yes |
| `refactor` | A code change with no behaviour change | No |
| `test` | Tests only | No |
| `docs` | Documentation only | No |
| `build` | Build system or dependencies | No |
| `ci` | Continuous integration | No |
| `chore` | Anything else that changes no shipped behaviour | No |

### Breaking changes

A breaking change takes `!` after the type or scope, for example `feat(fulltext)!: rename the analyzer option`. It also takes a footer `BREAKING CHANGE: <what breaks and what to do>`. One without the other is refused.

### Body

1. The body says the problem, the cause and the fix, in plain sentences.
2. The body describes the code as it is. It does not tell the story of the work.
3. The commit that completes an issue ends with `Fixes #<issue>`.
4. A fix to a fault that also exists in Apache Cassandra names its `CASSANDRA-<n>` ticket in the message.
5. A port or adaptation of someone else's work names the source repository as `owner/name`, the full 40 character commit hash and the ticket, then lists the adaptations.
6. Before a security advisory is public, no commit names a CVE or describes the issue as a vulnerability. See [security.md](security.md).
7. No commit carries a person's email address, other than in the trailers below.
8. Every commit is signed.

### Imports from Apache Cassandra

1. A single Apache commit taken early keeps its original Apache author and message, with the `(cherry picked from commit <full hash>)` line added by `git cherry-pick -x`.
2. Its import pull request is merged with a merge commit. The merge commit carries the Conventional Commits subject `import(CASSANDRA-<n>): <original Apache subject>` and its body names the Apache commit hash.
3. For a whole release import, the integrator merges the Apache release tag into the import branch. That merge commit's subject is `import(apache-<version>): merge Apache Cassandra <version>`, for example `import(apache-5.0.8): merge Apache Cassandra 5.0.8`. A maintainer then merges the import pull request into the line with a merge commit.
4. For a weekly merge of an Apache branch, before Apache's first release of its major version, the integrator's merge into the import branch has the subject `import(apache-<x.y>-branch): merge Apache cassandra-<x.y> at <short hash>`, for example `import(apache-6.0-branch): merge Apache cassandra-6.0 at 1a2b3c4d5e`.

See [upstream.md](upstream.md).

### Trailers

1. A person MAY note AI assistance with an `Assisted-by:` trailer naming the tool, as the organisation's guide describes.
2. A commit written by an automated agent carries two trailers: `Assisted-by: <tool>:<model>` and `Requested-by: <GitHub username> <GitHub no-reply address>` of the maintainer who asked for the work. For work items from an approved plan, that is the maintainer who approved the plan. For an item opened from one of the project's scheduled checks, it is the maintainer who set up that check. The squash commit on the line keeps these trailers. The username has no `@`, so it is never a mention.
3. An AI tool is never listed as an author or co-author.
4. Adapted work by another person carries `Co-authored-by:` for each of its authors.

### Pull request titles

Our own pull requests are squash merged, and the title becomes the subject of the commit on the line. The title MUST follow the same Conventional Commits rules. Import pull requests are merged with a merge commit, so the imported commits reach the line as they are.

## Change logs and release notes

1. `CHANGES-chronitondb.txt` is generated at release from the `feat`, `fix`, `perf`, `security` and `import` commits and the import merge commits. It is never edited by hand. Each line has the form ` * <Imperative description> (#<issue>)`. Security fixes have their own section.
2. `NEWS-chronitondb.txt` carries upgrade notes per release and anything user facing or upgrade relevant: for example the cleanup statements to run before a downgrade. It is written in the pull request that makes the change.
3. Apache's `CHANGES.txt` and `NEWS.txt` are never edited. They change only through imports.
4. Release notes are built from our commits and `NEWS-chronitondb.txt`. The commit subject is the text a user reads.

## Where things live

| Kind | Path |
|---|---|
| ChronitonDB Java code | `src/java/org/chronitondb/<area>/` |
| ChronitonDB tests | `test/unit/org/chronitondb/`, `test/distributed/org/chronitondb/`, in the same packages as the code they test |
| ChronitonDB tooling and code checks | `tools/chronitondb/` |
| Parity suite tooling | `test/parity/` |
| Benchmark results per release | `bench/` |
| Process documentation | `docs/process/` |
| Feature spec, plan and delivery plan of a feature | `docs/design/<feature>/` |
| Milestone reports of a feature | `docs/design/<feature>/milestones/` |
| Design record or fix record of one item, with its coverage file | `docs/design/<issue>-<slug>/` |
| Decision records | `docs/decisions/NNNN-<slug>.md` |
| Import records | `docs/imports/<apache-version-or-range>.md` |
| Release proposals and their verification results | `docs/releases/<version>.md` |
| Delta register | `docs/delta/` |
| User and operator documentation | `docs/` |
| Change logs | `CHANGES-chronitondb.txt`, `NEWS-chronitondb.txt` |
| Repository front page | `.github/README.md` |
| Packaging: Debian, Red Hat and the tarball script | `packaging/debian/`, `packaging/redhat/`, `packaging/` |
| Governance records | `docs/governance/` |
| Contribution guide | `.github/CONTRIBUTING.md` |
| Our CI workflows | `.github/workflows/chronitondb-*.yml` |

1. Apache's own files stay untouched: `CHANGES.txt`, `NEWS.txt`, `README.asc`, `doc/`, the root `CONTRIBUTING.md`, `.asf.yaml`, `debian/`, `redhat/`, the Jenkins and CI files and the like. ChronitonDB's files sit beside them, as listed above. A change to an Apache file is made only where we need it, with its [delta entry](../delta/README.md). See [upstream.md](upstream.md#apache-files-stay-untouched).
2. All ChronitonDB documentation lives in `docs/`.
3. User and operator documentation follows Diátaxis: tutorials, how-to guides, reference and explanation, one kind per page. Its folder layout will be defined with the documentation site.
4. Each line keeps its own documentation on its own branch.
5. Documentation changes ship in the same pull request as the code they describe.
6. Requirements and prerequisites in reference pages and how-to guides use BCP 14 key words. Tutorials and explanations use plain prose.

## Code layout

1. Fork logic lives in classes under `org.chronitondb`, in packages named for what they are, for example `org.chronitondb.fulltext`.
2. Fork logic MUST NOT be added as a new class under `org.apache.cassandra`. A fork class that needs package private access to a stock package is a design decision, named in the design record and approved with it.
3. An edit to a stock file is small and additive. It is the hook that calls fork code, nothing more.
4. Code defaults in stock classes, such as `Config.java`, stay exactly as Apache Cassandra has them.
5. A test that existed before a change is not weakened. A change to a pre-existing test is additive and named in the design record.

## Code style

### ChronitonDB Java files

1. Files under `org/chronitondb` follow Google Java Style. `tools/chronitondb/format-check.sh` checks it with google-java-format, in the `shape` check of every pull request. Formatting has no exceptions.
2. The `.editorconfig` at the repository root carries the matching editor settings for those paths only.
3. The 5.0 line uses Java 17. The 6.0 line uses Java 21. Code meant for both lines uses Java 17 features only.
4. Apache Cassandra's banned API rules apply to fork code too. `var` is not used.

### Shape limits

`tools/chronitondb/shape-check.sh` measures ChronitonDB Java files a change adds or modifies. Apache code is never measured. On production code every finding blocks:

| Limit | Value |
|---|---|
| Cyclomatic complexity per method (a `switch` counts once) | 10 |
| NPath complexity per method | 200 |
| Boolean expression complexity | 3 operators |
| Method length | 80 lines |
| Parameters per method | 7 |
| Nested `if` depth | 3 |
| Nested loop depth | 2 |
| Class fan out | 20 classes |
| File length | 1,000 lines |
| Cognitive complexity per method | 15 |
| Duplicated block | 50 tokens |

Tests and benchmarks are measured with looser limits (cyclomatic complexity 5, method length 150, file length 1,000, cognitive complexity 15, duplication 50 tokens). Their findings are warnings only.

A production limit MAY be exceeded only with a waiver recorded in the item's design record and approved with it, naming the method, the rule and the reason. A suppression comment in code is not a waiver.

### Stock files

1. Stock files, and every line added inside them, keep Apache Cassandra's style and checkstyle rules. Apache's checkstyle configuration is not changed for style.
2. Make the smallest change that does the job. Do not reformat untouched lines. Every extra difference makes future imports harder.
3. Stock files keep their comments, ticket numbers included.

### Comments in ChronitonDB code

1. Comments say why, in their own words.
2. Every public type and method has Javadoc that says what it does.
3. Comments carry no issue numbers (`#<n>`) and no Apache ticket ids (`CASSANDRA-<n>`). Those belong in commit messages and pull requests.
4. Comments describe the code as it is, without history words such as "previously" or "no longer".
5. No `TODO` comments. Open work goes in an issue.
6. Comments, assertion messages and log text are plain language: short sentences, no semicolons and no dashes as punctuation.

## Licence headers

1. Every new ChronitonDB file that Apache RAT checks carries a header with three parts: the line `Copyright <year> AxonOps Limited`, the line `SPDX-License-Identifier: Apache-2.0` and the standard Apache License 2.0 notice. This includes Markdown and text files such as documentation, design records and decision records.
2. The year is the year the file is created. It is never a range and never updated on later edits.
3. Markdown files carry the header in an HTML comment. Shell, YAML and Python files carry it behind `#`.
4. Stock files keep their Apache Software Foundation header. The AxonOps Limited line is never added to a stock file.
5. A new file without its header fails `ant-check`.

## Code from elsewhere

| Source | The file keeps | The commit carries |
|---|---|---|
| An Apache commit, cherry-picked | Its Apache headers, unchanged | The original author, the `import` subject and the upstream hash |
| Another project's commit, cherry-picked | Its headers as they are | The original author, the source repository, the full hash and the ticket if any |
| Another project's work, adapted into a new file | Its original header and author line, with the AxonOps Limited line added above when the file was adapted | `Co-authored-by:` for each author, the source and hash in the body, and a NOTICE entry where the licence asks for one |
| An idea from elsewhere, code written fresh | The ChronitonDB header | A line in the body naming the source of the idea |

An import whose author has not signed the contributor agreement fails the agreement check. That is expected. The author is never rewritten to pass it. A maintainer decides the merge. See [compliance.md](compliance.md).

## Names

1. New user facing names (yaml keys, nodetool commands, MBeans, metric types, packages) never contain "cassandra" or "axon". No key or value contains "stock".
2. Settings that apply across the fork are named for what they do.
3. ChronitonDB MBeans use the JMX domain `org.chronitondb`.
4. Fork metrics use their own metric types. Stock metric types gain no new metrics.
5. ChronitonDB versions have the form `<Apache version>-chronitondb<n>`, for example `5.0.10-chronitondb1`. Release candidate package versions add `~rc<k>`. The git tag of a release is the version itself. The git tag of a release candidate adds `-rc<k>`, for example `5.0.10-chronitondb1-rc1`, since git does not allow `~` in a tag name. See [release.md](release.md#version-numbers).
6. The package and its service are named `chronitondb`. A new install uses the configuration directory `/etc/chronitondb`, the data directory `/var/lib/chronitondb` and the system user `chronitondb`. See [release.md](release.md#packaging).
7. Timestamps in our records, evidence, documentation and release notes use RFC 3339.

## Dependencies

No new dependency, and no version change of an existing one, is used before it is declared and approved in a feature spec or design record. The one exception is a patch-version update of an approved library for a bug or security fix. See [compliance.md](compliance.md) and [maintenance.md](maintenance.md#dependency-patch-version-updates).
