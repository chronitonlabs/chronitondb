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
2. The description is imperative and in plain words, for example `feat(fulltext): add the phrase operator` or `fix(compaction): count a skipped sstable once`.
3. The subject is at most 72 characters. A trailing ` (chronitondb-<line>)` that names the line is not counted, nor GitHub's ` (#<number>)` on the commit on the line. An import subject carries the original subject unchanged, so it has no length limit, and it keeps its exact import form.
4. The subject never lists files. A subject such as `Update <path>`, as GitHub writes for a suggestion, is refused. Apply suggestions locally with a real subject.
5. The scope names the area of the change, for example `fulltext`, `compaction`, `build` or `github`.

### Types

| Type | Use | In release notes |
|---|---|---|
| `feat` | A new feature or user visible capability | Yes |
| `fix` | A fault fixed | Yes |
| `perf` | A performance improvement | Yes |
| `security` | A security fix, used only after the advisory is public. Before that, a security fix uses `fix` with a neutral description | Yes, in its own section |
| `import` | A change taken from Apache Cassandra, or taken unchanged from another project | Yes |
| `refactor` | A code change with no behaviour change | No |
| `test` | Tests only | No |
| `docs` | Documentation only | No |
| `build` | Build system or dependencies | No |
| `ci` | Continuous integration | No |
| `chore` | Anything else that changes no shipped behaviour | No |

### Breaking changes

A breaking change takes `!` after the type or scope, for example `feat(fulltext)!: rename the analyzer option`. It also takes a footer `BREAKING CHANGE: <what breaks and what to do>` in a commit message of the pull request. The squash commit on the line carries the messages of the pull request's commits, never its description, so a footer only in the description is refused. One without the other is refused.

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
5. A single commit taken unchanged from a project other than Apache keeps its original author, date and message, with the `(cherry picked from commit <full hash>)` line added by `git cherry-pick -x`. Its import pull request is merged with a merge commit. The merge commit carries the Conventional Commits subject `import(<owner>/<repo>@<12 character hash>): <original subject>`, the pull request title, and its message ends with the trailer `Origin: https://github.com/<owner>/<repo>/commit/<full hash>`, the DEP-3 Origin form the [delta entries](../delta/README.md) use. Code ported from another project and rewritten stays our own commit, with credit to its authors. See [Code from elsewhere](#code-from-elsewhere).

See [upstream.md](upstream.md).

### Trailers

1. A person MAY note AI assistance with an `Assisted-by:` trailer naming the tool, as the organisation's guide describes.
2. A commit written by an automated agent carries two trailers: `Assisted-by: <tool>:<model>` and `Requested-by: <GitHub username> <GitHub no-reply address>` of the maintainer who asked for the work. For work items from an approved plan, that is the maintainer who approved the plan. For an item opened from one of the project's scheduled checks, it is the maintainer who set up that check. The squash commit on the line keeps these trailers. The username has no `@`, so it is never a mention.
3. An AI tool is never listed as an author or co-author.
4. Adapted work by another person carries `Co-authored-by:` for each of its authors.

### Pull request titles

Our own pull requests are squash merged, and the title becomes the subject of the commit on the line. The title MUST follow the same Conventional Commits rules. Import pull requests are merged with a merge commit, so the imported commits reach the line as they are. The `pr-title` check refuses a title that breaks these rules or the import forms, and reads the `BREAKING CHANGE:` footer from the pull request's commit messages. The `line-subjects` check runs on each push to a line and fails on a new commit whose subject breaks them, such as a subject edited in the merge dialog.

## Change logs and release notes

1. `CHANGES-chronitondb.txt` is generated at release from the `feat`, `fix`, `perf`, `security` and `import` commits and the import merge commits. It is never edited by hand. Each line has the form ` * <Imperative description> (#<issue>)`. Security fixes have their own section.
2. `NEWS-chronitondb.txt` carries upgrade notes per release and anything user facing or upgrade relevant: for example the cleanup statements to run before a downgrade. It is written in the pull request that makes the change.
3. Apache's `CHANGES.txt` and `NEWS.txt` are never edited. They change only through imports.
4. Release notes are built from our commits and `NEWS-chronitondb.txt`. The commit subject is the text a user reads. They also name the newest Apache Cassandra release the line fully contains and every change cherry-picked on top of it, taken from the import merge commits. See [release.md](release.md#what-a-release-contains).

## Where things live

| Kind | Path |
|---|---|
| ChronitonDB Java code | `src/java/org/chronitondb/<area>/` |
| ChronitonDB tests | `test/unit/org/chronitondb/`, `test/distributed/org/chronitondb/`, in the same packages as the code they test |
| ChronitonDB tooling and code checks | `tools/chronitondb/` |
| Scenarios of fork features and their shared step library | `test/bdd/` |
| Parity suite tooling | `test/parity/` |
| Benchmark results per release | `bench/` |
| Process documentation | `docs/process/` |
| Feature spec, plan and delivery plan of a feature | `docs/design/<KEY>-<slug>/` |
| Milestone reports of a feature | `docs/design/<KEY>-<slug>/milestones/` |
| Design record or fix record of one item, with its coverage file | `docs/design/<issue>-<slug>/`, or `docs/design/<KEY>-<slug>/` for a fork feature that fits one item |
| Decision records of one feature | `docs/design/<KEY>-<slug>/decisions/DEC-<KEY>-nnnn-<slug>.md` |
| Decision records of work with no feature key | `docs/design/<issue>-<slug>/decisions/DEC-<issue>-nnnn-<slug>.md` |
| Decision records of the whole project | `docs/decisions/DEC-GOV-nnnn-<slug>.md`. The records there named by a number alone, `NNNN-<slug>.md`, were merged before records had ids |
| Generated indexes of the documents | `docs/index/documents.md`, `docs/index/decisions.md`, `docs/index/areas.md`, and `INDEX.md` in each feature directory `docs/design/<KEY>-<slug>/` |
| Generated graph of the documents and its context | `docs/index/graph.json`, `docs/index/context.json` |
| Research reports of spikes | `docs/research/<issue>-<slug>.md` |
| Import records | `docs/imports/<apache-version-or-range>.md`, or `docs/imports/<owner>-<repo>-<12 character hash>.md` for a commit from another project |
| Release proposals and their verification results | `docs/releases/<version>.md` |
| Line plan: first release date, feature freeze and LTS designation | `docs/releases/<line>-plan.md` |
| Delta register | `docs/delta/` |
| User and operator documentation | `docs/` |
| Change logs | `CHANGES-chronitondb.txt`, `NEWS-chronitondb.txt` |
| Repository front page | `.github/README.md` |
| Packaging: Debian, Red Hat and the tarball script | `packaging/debian/`, `packaging/redhat/`, `packaging/` |
| Governance records | `docs/governance/` |
| Contribution guide | `.github/CONTRIBUTING.md` |
| Our CI workflows | `.github/workflows/chronitondb-*.yml` |
| Code owners of the sensitive paths | `.github/CODEOWNERS` |
| Editor settings for ChronitonDB code | `.editorconfig` |
| ChronitonDB's configuration file | `conf/cassandra_chronitondb.yaml` |

1. Apache's own files stay as Apache has them: `CHANGES.txt`, `NEWS.txt`, `README.asc`, `doc/`, the root `CONTRIBUTING.md`, `.asf.yaml`, `debian/`, `redhat/`, the Jenkins and CI files and the like. ChronitonDB's files sit beside them, as listed above. A change to an Apache file is made only where we need it, with its [delta entry](../delta/README.md). See [upstream.md](upstream.md#apache-files-change-only-where-needed). The `delta-register` check reads the table above: a file under none of its paths is a stock file.
2. All ChronitonDB documentation lives in `docs/`.
3. User and operator documentation follows Diátaxis: tutorials, how-to guides, reference and explanation, one kind per page. Its folder layout will be defined with the documentation site.
4. Each line keeps its own documentation on its own branch.
5. Documentation changes ship in the same pull request as the code they describe.
6. Requirements and prerequisites in reference pages, how-to guides, runbooks, the process pages and templates, and design and decision records use BCP 14 key words. Tutorials and explanations use plain prose.
7. Product documentation, meaning reference pages, operator guides, runbooks and design and decision records, never addresses the reader as "you". Pages that address people taking part may: [contributing.md](contributing.md), `.github/CONTRIBUTING.md`, the reporting part of [security.md](security.md) and the How we work section of `.github/README.md`.

## Contents index of process documents

Each document is one file, so each carries an index of its headings near the top.

1. Every template in [templates/](templates/) has a `## Contents` section, and every document written from a template keeps it. The decision record template in [docs/decisions/README.md](../decisions/README.md#template) has one too, and every new record keeps it. A record already merged is never edited except for its status, so it stays as it was merged, with or without an index.
2. The Contents section is the first section after the title, below the document control table and the opening lines. It holds only a nested list: one link per heading below the title, in the order of the headings. A `##` heading is not indented. Every other heading is indented two spaces more than the nearest heading above it of a higher level, so a heading that skips a level is still one step below its parent.
3. Each entry shows its heading's text and links the heading's anchor. The anchor follows GitHub's rules: the text GitHub shows for the heading in lower case, every character that is not a letter, a digit, `_`, `-` or a space removed, and each space a hyphen. A heading whose anchor is taken already gets `-1`, then `-2`. For example `## 2.1 Context and scope` is `#21-context-and-scope`.
4. The index is never written by hand. After any heading is added, removed or renamed, and before the commit, the author regenerates it with `tools/chronitondb/doclint.py index --write <file>`. It refuses, and leaves the file unchanged, when the Contents section holds anything but the list. `tools/chronitondb/doclint.py index <file>` prints it, and `index --check <file>` reports what is wrong with it.
5. The process document check refuses a document of a templated kind, a decision record only when it is new to the line, whose index is missing, not first, misses a heading, lists a heading out of order or at the wrong depth, or links an anchor that no heading of the file has. It also refuses a new decision record that is not named by its id in the place its key gives it, whose title does not open with that id, whose id another record has, or that does not take the next number of its key after the highest one merged on the line. See [the tools README](../../tools/chronitondb/README.md#process-documents-doclintpy).

## Versions and revision history

A document that can change after it is merged carries its version and says what each version changed.

1. Every template in [templates/](templates/) with a `Version` row in its document control table has a revision history under that table: a table with one row for each version. The row gives the version, its RFC 3339 date, what changed, and the id of the decision record behind the change, or `None`. The first version's row says `First version`.
2. A change to a merged document raises its `Version` by one and adds one row. A merged version keeps its row as it was merged.
3. Under the table one line links the commits of the file on its line on GitHub: `Full history in git: [commits of this file](<address>)`. The address is never written by hand. `tools/chronitondb/doclint.py history --repo . --templates origin/<line> --write <file>` writes it from the file's path, the line and the repository the line is fetched from, so it stays right when the repository moves or is renamed.
4. A document merged before its template had the table keeps the line `Change history: the git history of this file.` until its next version. That version adds the table with its own row, which `history --write` starts.
5. A decision record has no version. It is never edited, and the record that supersedes it is its history. See [the decision records](../decisions/README.md#rules).
6. The process document check refuses a document that is new to the line, or at another version than on the line, without its revision history. It refuses rows out of order or with a gap, a last row that is not the document's version, a row with no date, change or decision record, a changed row of a merged version, and a history link that is not the commits of the file on its line. `history --check <file>` reports the same.

## Generated indexes

The documents are found through four indexes that the document checker writes from each document's own header. No index is written or edited by hand.

1. [docs/index/documents.md](../index/documents.md) lists every document under `docs/` that carries the common header, by kind, with its status, version and areas. A document counts when its document control table has a `Document type` row, whatever its file is called. An import record is listed with its line, its source, the Apache JIRA tickets and the release or commit its header names.
2. [docs/index/decisions.md](../index/decisions.md) lists every decision record of the project and of its features, by key and number, with its status, date, areas and the records it supersedes.
3. [docs/index/areas.md](../index/areas.md) lists the same documents and records under each of the [areas](areas.md) their `Areas` row names. A document of a kind with no `Areas` row, or merged before the row, is listed last.
4. `INDEX.md` in each feature directory lists the documents of that feature, the design records of its items and its decision records.
5. After a document is added, or its title, status, version, areas or supersede row changes, the author regenerates the indexes with `tools/chronitondb/doclint.py indexes --repo . --templates origin/<line> --write` and commits them with the change. Two pull requests that both add a document change the same pages: the one merged second runs the command again after it takes in the line.
6. The process document check refuses a pull request whose indexes are not what the documents give: `tools/chronitondb/doclint.py indexes --repo . --templates origin/<line>` reports each stale page.

## The document graph

The links between the documents are also written as one graph, for tools that read data and not pages.

1. `docs/index/graph.json` is generated by `tools/chronitondb/docgraph.py --repo . --templates origin/<line> --write` from the same headers the indexes read. The documents are the source of truth. The file is never edited by hand, and says so in its `description`.
2. Its nodes are the documents the indexes list, the feature directories, the areas a document names, and the Apache JIRA tickets, releases and commits an import record names.
3. A link is written only where a header or a table states it: a document's areas, the feature it belongs to, the records a decision record supersedes, the decision records the revision history of a document names, the feature spec a design record's References row links, and what an import was taken from. No link is read from prose.
4. It is JSON-LD, in files named `.json` so that the licence audit, which passes over JSON, needs no change to Apache Cassandra's build files. It uses established terms: Dublin Core terms for titles, types, subjects, parts, replacements and references, schema.org for a document and its version, PROV for what an import derives from, SKOS for an area, and OSLC for a status and for a record that elaborates a spec. ChronitonDB's own terms are four, where no established one fits: `line`, the line a document is written for, `source`, how a change came in, `upstreamRevision`, a commit named where no address of it can be built from the header, and `Feature`, a feature directory.
5. The context is the file `docs/index/context.json`, kept by hand beside the graph. Every address in the graph is relative to the graph file or is Apache's own, and the project's own terms are relative to the context file, so nothing in it names the repository or its owner.
6. The same tree gives the same bytes: nodes in the order of their ids, keys sorted, no date of writing and no path of the machine. `tools/chronitondb/docgraph.py --repo . --templates origin/<line>` exits 1 when the committed file is not what the documents give.

## Claims about code

A claim about what code does names the code it was read in. This applies to the process pages and to every document written from a template.

1. A claim about Apache Cassandra code says "Apache Cassandra", never "stock".
2. Each claim names the project, the branch and the commit, in the form `<project> <branch> at <hash>`. For example `Apache Cassandra cassandra-5.0 at <hash>`, `Apache Cassandra trunk at <hash>` or `ChronitonDB chronitondb-6.0 at <hash>`. Next to it stand the symbol and the file and line, for example `CompactionManager.submitBackground`, `src/java/org/apache/cassandra/db/compaction/CompactionManager.java:<line>`.
3. Analysis keeps three sources apart and says which one each claim holds for: our line, the Apache Cassandra release our line is based on, and Apache Cassandra upstream now, meaning the head of the same branch, the next major version's branch and trunk.
4. "Stock behaviour" still names what the compatibility rule protects: what an application and an operator see from Apache Cassandra. See [quality-requirements.md](quality-requirements.md#compatibility-with-apache-cassandra).

## Code layout

1. Fork logic lives in classes under `org.chronitondb`, in packages named for what they are, for example `org.chronitondb.fulltext`.
2. Fork logic MUST NOT be added as a new class under `org.apache.cassandra`. A fork class that needs package private access to a stock package is a design decision, named in the design record and approved with it.
3. An edit to a stock source file is the smallest that does the job. It is a hook that calls fork code, a fix to a defect in stock, or a refactor that lets fork code share stock logic in place of a copy. A refactor is named in the design record and reviewed with it.
4. Code defaults in stock classes, such as `Config.java`, stay exactly as Apache Cassandra has them.
5. A test that existed before a change is not weakened. A pre-existing stock test file is not edited in feature work: a fork feature puts its tests in its own files. A stock test file changes only in a fix to stock the maintainers approved, unchanged in an import from Apache Cassandra, or by a decision record that approves the named change. A change to a pre-existing ChronitonDB test only adds, and is named in the design record. See [testing.md](testing.md#policy).
6. A name that a client supplies never picks code to load unless it is on an allow list. ChronitonDB's own list is fixed in the code, proposed by the design with a reason for each entry, and approved by the maintainers in a decision record. A new entry is a new decision. An operator's extension of the list in a node's configuration, for code the operator has placed on the node, is not ruled out: it is designed and decided when a feature needs it.

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
2. Every public type has Javadoc that says what it does, and so has every public method whose behaviour is not obvious from its name. A method that overrides an interface or superclass method inherits that Javadoc, and a plain accessor needs none.
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
| An Apache commit, cherry-picked | Its Apache headers, unchanged | The original author and the Apache message unchanged, with the `(cherry picked from commit <full hash>)` line. The maintainer's merge of the import pull request carries the `import` subject |
| Another project's commit, cherry-picked | Its headers as they are | The original author, date and message unchanged, with the `(cherry picked from commit <full hash>)` line added by `git cherry-pick -x`. The maintainer's merge of the import pull request carries the `import(<owner>/<repo>@<12 character hash>)` subject and the `Origin:` trailer with the full hash |
| Another project's work, adapted into a new file | Its original header and author line, with the AxonOps Limited line added above when the file was adapted | `Co-authored-by:` for each author, the source and hash in the body, and a NOTICE entry where the licence asks for one |
| An idea from elsewhere, code written fresh | The ChronitonDB header | A line in the body naming the source of the idea |

An import whose author has not signed the contributor agreement fails the agreement check. That is expected. The author is never rewritten to pass it. A maintainer decides the merge. See [compliance.md](compliance.md).

## Names

1. New user facing names (yaml keys, nodetool commands, MBeans, metric types, packages) never contain "cassandra" or "axon". No key or value contains "stock".
2. Settings that apply across the fork are named for what they do.
3. ChronitonDB MBeans use the JMX domain `org.chronitondb`.
4. Fork metrics use their own metric types. Stock metric types gain no new metrics.
5. ChronitonDB release versions have the form `<line>-chronitondb<n>`, for example `5.0-chronitondb3`, with `n` from 1 on each line. They never carry an Apache patch number. Release candidate package versions add `~rc<k>`, for example `5.0-chronitondb3~rc1`. The git tag of a release is the version itself. The git tag of a release candidate adds `-rc<k>`, for example `5.0-chronitondb3-rc1`, since git does not allow `~` in a tag name. See [release.md](release.md#version-numbers).
6. The package and its service are named `chronitondb`. A new install uses the configuration directory `/etc/chronitondb`, the data directory `/var/lib/chronitondb` and the system user `chronitondb`. See [release.md](release.md#packaging).
7. Timestamps in our records, evidence, documentation and release notes use RFC 3339.

## Dependencies

No new dependency, and no version change of an existing one, is used before it is declared and approved in a feature spec or design record. The one exception is a patch-version update of an approved library for a bug or security fix. See [compliance.md](compliance.md) and [maintenance.md](maintenance.md#dependency-patch-version-updates).
