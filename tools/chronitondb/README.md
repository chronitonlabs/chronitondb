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

# ChronitonDB code checks

One check for the Java files under `org/chronitondb` that a change adds or modifies, the shape limits, and one for the process documents, `doclint.py`. Apache code is never measured by the shape check. It runs on the staged files before each commit, and in the CI workflow `.github/workflows/chronitondb-shape.yml` on every pull request into a `chronitondb-*` branch. The rules are in [conventions.md](../../docs/process/conventions.md#shape-limits).

## Shape limits: `shape-check.sh`

Measured limits on production code, every finding blocks:

| Limit | Value | Tool |
| --- | --- | --- |
| Cyclomatic complexity per method (a `switch` counts once) | 10 | checkstyle CyclomaticComplexity |
| NPath complexity per method | 200 | checkstyle NPathComplexity |
| Boolean expression complexity | 3 operators | checkstyle BooleanExpressionComplexity |
| Method length (blank and comment lines included) | 80 lines | checkstyle MethodLength |
| Parameters per method | 7 | checkstyle ParameterNumber |
| Nested `if` depth | 3 | checkstyle NestedIfDepth |
| Nested loop depth (`for` loops, checkstyle has no module for `while`) | 2 | checkstyle NestedForDepth |
| Class fan out | 20 classes | checkstyle ClassFanOutComplexity |
| File length | 1,000 lines | checkstyle FileLength |
| Cognitive complexity per method | 15 | PMD CognitiveComplexity |
| Duplicated block | 50 tokens | PMD CPD |

Tests and benchmarks are measured with their own limits, and their findings are warnings only: cyclomatic complexity 5, method length 150, file length 1,000, cognitive complexity 15, duplication 50 tokens. A test or a benchmark is any path with a `test/` directory before `org/chronitondb`: `test/unit`, `test/distributed`, `test/microbench`, `test/burn`. Testing a database is complicated, long setup is not a finding.

The rules live in `checkstyle-shape.xml` (production), `checkstyle-shape-tests.xml` (tests) and `pmd-ruleset.xml` (cognitive complexity, plus the CPD setting and the PMD pin). Changing a limit is a one line change there.

Output, one line per finding, then a summary:

    ERROR src/java/org/chronitondb/index/Foo.java:42:5 CyclomaticComplexity value=12 limit=10: Cyclomatic Complexity is 12 (max allowed is 10).
    WARN test/unit/org/chronitondb/index/FooTest.java:88:5 MethodLength value=162 limit=150: Method verify length is 162 lines (max allowed is 150).
    shape-check: 1 production finding(s) that block, 1 test warning(s), 1 production and 1 test file(s) checked

Exit 0 when nothing blocks, 1 on a production finding, 2 when the check could not run.

## Code style

The files under `org/chronitondb` follow Apache Cassandra's code style on each line, see [conventions.md](../../docs/process/conventions.md#code-style). Apache's own checkstyle (`.build/checkstyle.xml`) runs over the whole tree in `ant check`, these files included. There is no formatter and no formatting check here.

## Running

    tools/chronitondb/shape-check.sh FILE...            these files
    tools/chronitondb/shape-check.sh                    the staged files (what runs before a commit)
    tools/chronitondb/shape-check.sh --base origin/chronitondb-6.0   the files changed since the merge base (what CI does)
    tools/chronitondb/shape-check.sh --self-test        the fixtures under test/
    tools/chronitondb/shape-check.sh --tree DIR --base origin/chronitondb-5.0   the same check on the files of DIR, another checkout

`--tree DIR` goes first. It checks the files of DIR with the script, the limits and the tools of the tree the script is in. CI checks out the base branch beside the pull request and runs the script of the base branch on the pull request's files this way, so a pull request cannot loosen the limits it is measured by. The checkstyle classpath is resolved in the tree of the base branch too, with the JDK its `build.xml` names as `java.default`: 17 on the 5.0 line, 21 on the 6.0 line. The Semgrep and SpotBugs scripts take `--tree` the same way.

Paths that are not `org/chronitondb/**/*.java` are ignored. The changed files are listed by their names as they are on disk, so a file whose name git would print in quotes is not passed over. A Java file under `org/chronitondb` whose path holds anything but ASCII letters, digits and `_ $ . - + @ /` stops the check, exit 2, since the tools could not take it from their file lists. So does a changed file with a control character in its name, and a base ref that does not exist. Checkstyle comes from the build's own test classpath, `build/test/lib/jars`, so run `ant resolver-retrieve-build` (or any build) once. On 6.0 that target also builds the `modules/accord` submodule, so run `git submodule update --init` first. PMD is downloaded into `build/chronitondb-shape` on first use and refused unless its sha256 matches the pin. Nothing is added to `lib/` or `build.xml`, nothing is shipped, `build/` is not committed. `SHAPE_PMD_HOME` points at a copy already on disk, for offline use.

Pins:

- checkstyle 10.26.1, the version Apache's build declares in `.build/parent-maven-pom.xml` on the 6.0 line.
- PMD 7.29.0, `pmd-dist-7.29.0-bin.zip` from the PMD GitHub release, sha256 recorded in `pmd-ruleset.xml` after the release signature verified against the PMD release signing key.

## Tests

`test/src` and `test/test` hold one fixture per limit that breaks it and a few that pass (a 15 case `switch` with cyclomatic complexity 2, a method at cognitive complexity 15 exactly, a 100 line test method). `test/expected.txt` lists the finding each fixture must produce. `--self-test` stages them as `src/java` and `test/unit` files, runs the real tools and compares. The fixtures are skipped when given to the checks by their own path, so staging them never fails a commit. The self-test also checks the changed files of a small repository and ends with the staging tree checked through `--tree`. CI runs the self-test of the base branch's check before the check, and in a job of its own, `shape-tests`, the self-test of the check a pull request brings when it changes `tools/chronitondb`.

## Waivers

A production limit can be exceeded only with a waiver recorded in the design record of the change and approved with it, naming the method, the rule and why the shape is right there. A suppression comment in the code is not a waiver and the rules files have no suppression filter. PMD and CPD obey markers in the code, so the check reports each of them as a finding of the rule `Suppression`: `NOPMD`, `CPD-OFF`, `CPD-START` and a `SuppressWarnings` of a PMD rule. The reviewer reads the check output next to the design record and treats a broken limit without a recorded waiver as a major finding.

## Security checks

Two more checks. CI runs them on every pull request into a `chronitondb-*` branch, in `.github/workflows/chronitondb-semgrep.yml` and `chronitondb-spotbugs.yml`, each after its self-test. Both are required checks on every line, see [branching-and-review.md](../../docs/process/branching-and-review.md#required-checks). In both workflows the script, its rules and its pins come from the base branch and the pull request's files are read as data, as for the shape check. The jobs `semgrep-tests` and `spotbugs-tests` run the self-test of the copy a pull request brings when it changes `tools/chronitondb`.

### Semgrep: `semgrep-check.sh`

Semgrep CE from its container image, pinned by digest in the script, run with docker without network. The rules are in `semgrep/`, one file per topic:

| File | Finds | Paths |
| --- | --- | --- |
| `banned-apis.yml` | the APIs `.build/checkstyle.xml` bans in main code | `src/java/org/chronitondb` |
| `non-ascii-identifiers.yml` | a non-ASCII character outside strings and comments | any `org/chronitondb` path |
| `process-exec.yml` | `Runtime.exec` and `ProcessBuilder` with a command that is not a string literal | every Java file |
| `deserialization.yml` | `ObjectInputStream` | every Java file |
| `bidi.yml` | Unicode bidirectional control characters | every file |

    tools/chronitondb/semgrep-check.sh FILE...          these files
    tools/chronitondb/semgrep-check.sh                  the staged files
    tools/chronitondb/semgrep-check.sh --base origin/chronitondb-5.0   the files changed since the merge base, without the findings already there (what CI does)
    tools/chronitondb/semgrep-check.sh --self-test      the fixtures under test/semgrep
    tools/chronitondb/semgrep-check.sh --tree DIR --imported --base origin/chronitondb-5.0   an import in DIR, another checkout

`--imported` says the change is an import. A finding in a file outside `org/chronitondb` is then in imported code: it is printed as `REPORT`, not `ERROR`, and does not fail the check. It goes into the import's assessment, and the maintainers decide it before the import merges, as [upstream.md](../../docs/process/upstream.md#whole-apache-releases) says. A finding in an `org/chronitondb` file still fails. CI passes `--imported` only for a pull request whose head branch is an import from Apache Cassandra, a branch `import/cassandra-<...>` or `import/CASSANDRA-<n>` of this repository. A commit of another project is checked as the project's own change, since no check can read whether the maintainers approved its source. The author of a pull request from a fork chooses its branch name, so a fork's branch never counts: an import that starts on a fork is pushed to an `import/` branch of this repository by a maintainer.

Semgrep runs with `--disable-nosem`, so a `nosemgrep` comment hides nothing, and a checkstyle `permit` comment does not hide a banned API from Semgrep. Needs docker and jq. `--self-test` runs `semgrep --test` on `test/semgrep` (each `ruleid` line must be reported, each `ok` line must not), then checks the path scoping, which `--test` ignores, then `--tree` and `--imported` on a staged tree, and last the changed files of a small repository, one of them with a name outside ASCII, which is scanned as any other. The bidi fixture is written at test time, so no committed file carries a bidi control character.

### SpotBugs: `spotbugs-check.sh`

SpotBugs 4.10.5 with the FindSecBugs 1.14.0 plugin on the compiled `org.chronitondb` classes, report only: findings are printed and never fail the check. Apache classes are read to resolve types and never analysed.

    tools/chronitondb/spotbugs-check.sh                 the classes under build/classes/main (run ant jar first)
    tools/chronitondb/spotbugs-check.sh CLASSES         the classes under another directory
    tools/chronitondb/spotbugs-check.sh --self-test     compile test/spotbugs and expect COMMAND_INJECTION and OBJECT_DESERIALIZATION
    tools/chronitondb/spotbugs-check.sh --tree DIR      the classes under build/classes/main of DIR, another checkout

In CI the self-test of the base branch's script runs first, then the pull request's own build, since its classes are what is analysed. A build runs the build file the pull request brings, so this job reports and is never a gate on a finding.

The jars come from Maven Central into `build/chronitondb-shape/spotbugs-4.10.5`, each refused unless its sha256 matches the pin in the script. The set is the `lib/` of the SpotBugs release, so `java -jar spotbugs.jar` finds them through its manifest.

## Commit subjects: `subjectlint.py`

Checks commit subjects against [conventions.md](../../docs/process/conventions.md#commit-messages), Commit messages: the form `type(scope): description` with a type of the Types table and a scope, at most 72 characters not counting a trailing ` (chronitondb-<line>)` or GitHub's ` (#<number>)`, no file listed, `!` together with a `BREAKING CHANGE:` footer in a commit message, and for an import, which has no length limit, one of the forms `import(CASSANDRA-<n>)`, `import(apache-<version>)`, `import(apache-<x.y>-branch)` and `import(<owner>/<repo>@<12 character hash>)`. With `--branch NAME`, a title of type `import` is taken only when NAME starts with `import/`: the type lifts the length rule and the file rule, so it is kept for imports. CI gives the head branch's name only for a branch of this repository and an empty name for a branch of a fork. It also checks the attribution rule of [Trailers](../../docs/process/conventions.md#trailers) in the messages of the pull request's commits and in its description: no `Co-authored-by` line that names an AI tool or model, no link to a session of an AI tool and no line that says a tool generated the text. `Assisted-by:`, `Requested-by:` and a `Co-authored-by` line of a person pass. The commits of an import are not read, since their messages are someone else's. The type list and the length limit are read from conventions.md on the ref given with `--rules`, the line. Python 3 only, no other dependency.

    tools/chronitondb/subjectlint.py title --repo . --rules origin/chronitondb-5.0 --commits origin/chronitondb-5.0..HEAD --body DESCRIPTION-FILE --branch BRANCH "feat(compaction): count a skipped sstable once"
    tools/chronitondb/subjectlint.py commits --repo . --rules origin/chronitondb-5.0 origin/chronitondb-5.0~5..origin/chronitondb-5.0

The repository makes the pull request title the subject of the squash or merge commit, so the CI workflow `.github/workflows/chronitondb-subjects.yml` runs `title` on every pull request into a line, with this file taken from the base branch. It reads the footer from the pull request's commit messages, which the squash commit carries, and refuses a footer that is only in the description. On each push to a line it runs `commits` on the new commits of the line's first parent history, the squash and merge commits, never the commits an import merge brings, and checks the subject and the attribution of each. GitHub's ` (#<number>)` at the end of those subjects is not counted. Exit 0 when nothing is found, 1 on a finding, 2 on a usage error.

`test/subjectlint/` holds its unit tests, run by the same workflow:

    python3 -m unittest discover -s tools/chronitondb/test/subjectlint

## Import history: `importlint.py`

Checks the commits an import branch adds to its line against [upstream.md](../../docs/process/upstream.md#the-import-history-check). The CI workflow `.github/workflows/chronitondb-import.yml` runs it on every pull request from an `import/` branch of this repository, with this file, `doclint.py` and `markdown.py` taken from the base branch. Python 3 and git 2.40 or later, no other dependency.

    tools/chronitondb/importlint.py history --repo . --base origin/chronitondb-5.0 --head HEAD --branch import/cassandra-5.0.8/chronitondb-5.0
    tools/chronitondb/importlint.py history --repo . --base origin/chronitondb-5.0 --head HEAD --branch BRANCH --body DESCRIPTION-FILE --reviews REVIEWS-FILE

The branch name gives the form. A release import and a branch import have one merge commit whose second parent is the commit of Apache Cassandra's tag, or the commit of its branch that the short hash names. A single fix has one commit made by `git cherry-pick -x` from a commit of an Apache branch whose message names the ticket, with its author, date and message kept. A commit of another project is held the same way against the repository the description's `Origin:` line names. Any other commit changes only the project's own files or merges the line into the branch.

The checker fetches Apache Cassandra's tag or branches from `https://github.com/apache/cassandra.git` into refs of its own under `refs/import-check/`, so it needs the network. A tag or a branch of the clone is no proof. It makes each merge and each cherry-pick again with `git merge-tree` and compares the result with the commit, so a line in another place or with other whitespace is seen. Where they differ it prints the files on `RESOLVED` lines and fails, until `--reviews` holds an approving review by a maintainer of `docs/governance/committers.md` on the line, at a commit that holds the resolved one. The reviews file is the answer of the GitHub API for the reviews of the pull request.

    RESOLVED src/java/org/apache/cassandra/service/StorageService.java
    import-history failed

`test/importlint/` holds its unit tests, run by the same workflow. Each builds a stand-in for the public repositories in a directory:

    python3 -m unittest discover -s tools/chronitondb/test/importlint

## Review verdict: `reviewlint.py`

Checks the review verdict of a pull request against [branching-and-review.md](../../docs/process/branching-and-review.md#the-review-record). The CI workflow `.github/workflows/chronitondb-review-verdict.yml` runs it on every pull request into a line, and again when a review is posted, edited or dismissed and when a label is set or taken off. It only reads: it starts no review and asks for none. This file, `markdown.py`, `tools/chronitondb/review-app.json` and `docs/governance/committers.md` are taken from the base branch. Python 3 only, no other dependency.

    tools/chronitondb/reviewlint.py verdict --app tools/chronitondb/review-app.json --maintainers docs/governance/committers.md --pull PULL-FILE --events EVENTS-FILE --reviews REVIEWS-FILE --edits EDITS-FILE

The four last files are answers of the GitHub API: the pull request, its events as an issue, its reviews, and the GraphQL answer that gives `fullDatabaseId`, `lastEditedAt` and `editor` of each review.

`tools/chronitondb/review-app.json` names the project's review App and the accounts the project's automation writes pull requests as:

| Key | Value |
|---|---|
| `app_id` | The id of the GitHub App, from its settings page. No answer of GitHub carries it on a review, so no check compares it. It is kept for people |
| `app_slug` | The App's name in addresses. Its reviews come from the user `<app_slug>[bot]` |
| `bot_user_id` | The id of that user: `gh api 'users/<app_slug>[bot]' --jq .id` |
| `automation_user_ids` | The ids of the accounts the project's automation writes pull requests as, a list of numbers |

A placeholder is `0`, `""` or an empty list. While any value is a placeholder the check fails on every pull request and says which file to fill, so the check is made a required check only after the filled file is on every line.

A verdict is due on a pull request whose author is one of `automation_user_ids`, and on one a maintainer of the table Maintainers accepted with the label `triage:accepted`: of the events of that label only those whose actor is a maintainer count, and the newest of them set it. A label set or taken off by anyone else changes nothing. A pull request that carries the label or has an event of it fails while the table Maintainers names nobody. Any other pull request passes with the line `no review verdict is due`. Where a verdict is due, the newest review of the App's user (type `Bot`, login `<app_slug>[bot]`, id `bot_user_id`, all three) has the state `COMMENTED`, is a review of the head commit, holds a verdict block whose `"head"` is that commit (the last fenced `json` block that names `"lenses"`, one JSON object, with each fence at the margin of its line and nothing after it but spaces or tabs), and was never edited. The newest review of the App decides. A review of the App with no verdict block fails as holding no verdict: the App posts nothing but verdicts, so an older verdict never counts in its place. A review of any other account counts for nothing. Once the checker is on the line, a line that lacks `review-app.json` or `docs/governance/committers.md` fails the check as a file that cannot be read.

The verdict is also clean, or the check fails: in the block `"ready"` is `true`, `"approve"` is `true`, `"lenses"` is an object that names one checklist or more, each with the result `true`, and `"blockers"` and `"majors"`, where the block carries them, are the number `0`. A verdict with an open blocker or major finding leaves the check failed until a later verdict on the head is clean. The check reads no waiver: when a maintainer waives a finding, the reviewer posts a new verdict that records the waiver, and that verdict is the one read.

    the review 5970525038 of example-review[bot] is the clean verdict on the commit 34103ea892f7e67e8160e023504d565a8a16104f
    review-verdict passed

`test/reviewlint/` holds its unit tests, run by the same workflow, against recorded answers of the API under `test/reviewlint/shapes/`:

    python3 -m unittest discover -s tools/chronitondb/test/reviewlint

## Process documents: `doclint.py`

Checks the process documents under `docs/` against their templates on the line, and the rules [docs/process/](../../docs/process/README.md) sets for them: the document control table, every numbered section in order, the Contents index, the revision history and its link to the file's commits, no template placeholder and no `[NEEDS CLARIFICATION` marker left, and per document type the feature spec, plan, milestone report, decision record and delta entry rules. It also checks the feature keys and requirement ids of [additive.md](../../docs/process/additive.md#feature-keys-and-requirement-ids) across the lines. Two more commands check the library declarations of [compliance.md](../../docs/process/compliance.md) (`dependencies`) and that `conf/cassandra_chronitondb.yaml` holds every setting of Apache's two yaml files (`settings`, [release.md](../../docs/process/release.md#the-configuration-file)). No CI workflow runs these two yet. Both have unit tests, and `settings` has nothing to compare until the file exists. `markdown.py` beside it is its Markdown reader. Python 3 only, no other dependency.

    tools/chronitondb/doclint.py document --repo . --templates origin/chronitondb-5.0 --source index docs/design/VER-release-version/feature-spec.md
    tools/chronitondb/doclint.py keys --repo . --base origin/chronitondb-5.0 --source index
    tools/chronitondb/doclint.py index --write docs/design/VER-release-version/feature-spec.md

The rules are read from the ref given with `--templates` or `--base`, the line, never from the change being checked. The CI workflow `.github/workflows/chronitondb-documents.yml` runs `document` on the process documents a pull request changes, and `keys` when it changes `docs/design/` or `test/bdd/`, with this file taken from the base branch. It also checks that a delta entry's issue exists, that a new feature key is not in use by another open pull request, and that the generated indexes and the document graph are what the documents give. Run `doclint.py` without arguments for every subcommand and option.

Findings, one per line, then a summary:

    docs/design/VER-release-version/feature-spec.md:45: FREQ-VER-002 has 2 BCP 14 keywords, a requirement has exactly one (split it)
    documents 1 checked 1 failed

Exit 0 when nothing is found, 1 on a finding, 2 on a usage error.

### The delta register

`doclint.py delta` is the check of [the delta register](../../docs/delta/README.md#keeping-it-current), run by the CI workflow `.github/workflows/chronitondb-delta.yml` on every pull request into a `chronitondb-*` branch, with this file taken from the base branch.

    tools/chronitondb/doclint.py delta --repo . --base origin/chronitondb-5.0 --source worktree
    tools/chronitondb/doclint.py delta --repo . --base origin/chronitondb-5.0 --source HEAD --branch BRANCH --body DESCRIPTION-FILE

A file is ChronitonDB's own when it falls under a path of the table Where things live in [conventions.md](../../docs/process/conventions.md#where-things-live), read from the line. Every other file is a stock file. A change that adds, edits, deletes or renames a stock file adds or changes an entry under `docs/delta/`, unless its branch imports a whole Apache release or Apache's branch (`import/cassandra-<...>`), or its description has a line `No delta entry: <reason>`. That line is for a feature's change that touches only log lines Apache Cassandra writes. The checker reads only that it is there, the reviewer judges it against the change, and any other use of it is a decision of the maintainers at review. The checker takes the branch name as given. CI gives it only when the head branch is in this repository, never for the branch of a fork, whose author chooses its name. An import that starts on a fork is pushed to an import branch of this repository by a maintainer, and its pull request is opened from there. Each entry it adds or changes passes the delta entry rules of `document`, with an Origin commit link, its index row with the same Area and Lines, and on an update a new Last-Update. No entry is renamed or deleted. It prints `stock PATH` for each stock file it finds.

### Stock test files

`doclint.py stock-tests` is the check of [testing.md](../../docs/process/testing.md#policy), Policy 4, run by the CI workflow `.github/workflows/chronitondb-stock-tests.yml` on every pull request into a `chronitondb-*` branch, with this file taken from the base branch.

    tools/chronitondb/doclint.py stock-tests --repo . --base origin/chronitondb-5.0 --source worktree --body DESCRIPTION-FILE
    tools/chronitondb/doclint.py stock-tests --repo . --base origin/chronitondb-5.0 --source HEAD --branch BRANCH --body DESCRIPTION-FILE --issue ISSUE-STATE-FILE
    tools/chronitondb/doclint.py stock-tests-issue --branch BRANCH --body DESCRIPTION-FILE

A stock test file is a file the line has, in a directory named `test` or named `*Test.java`, `*Tests.java`, `test_*.py` or `*_test.py`, that is not the project's own by the table Where things live. A change to one passes in an import from Apache Cassandra, by its branch name `import/cassandra-<...>` or `import/CASSANDRA-<n>`, which CI gives only for a branch of this repository. Otherwise a record of the pull request's own issue on the line permits the change: the fix record lists the file as `test` in its Planned file list, a design record or fix record names it on a line `Pinned listing: <path>` and the change only adds lines of the listing, or an accepted decision record has the line `Approved stock test change: <path> for #<issue>, because <explanation>`, with an explanation of eight different words or more and no placeholder left. A word has two letters or more, and the case of letters is ignored. A placeholder is one of the words `TBD`, `TODO`, `FIXME`, `XXX` and `lorem` in any case of letters, three full stops or an ellipsis, a text in braces or lower case words in angle brackets. So an explanation that is only `n/a` or `none` approves nothing. The records are read at `--base`, never from the change, so a pull request cannot write its own permit.

The pull request's own issue is the issue of `--branch` when it is given, which is then a work branch `<name>/<issue>-<slug>/<line>`, and the description names it on a line `Fixes #<issue>` or `Part of #<issue>`. With no branch name it is the one issue the description names. `stock-tests-issue` prints that issue. CI reads its state from the GitHub API and gives the answer with `--issue`: a closed issue, a pull request's number and an answer that cannot be read permit nothing. A permit is used up once a change to the file has reached `--base`, on its first parent history, with the last change of the record or after it. Lines added to a pinned listing are any lines in a file of plain data (no extension, `.txt`, `.json`, `.csv`), and in any other file only whole lines of the listing, in the forms [testing.md](../../docs/process/testing.md#policy), Policy 4, gives, with the one line a change to a Java file may alter. A line of a hunk that opens with `+` is an added line, also one whose text opens with `++`. A permit line indented by four spaces or a tab is code and permits nothing. A stock test file that is deleted, renamed, binary or a symbolic link passes only in an import.

    test/unit/org/apache/cassandra/tools/nodetool/VersionTest.java: the file is a pre-existing test file of Apache Cassandra and no record on origin/chronitondb-5.0 of #142 permits the change
    stock-tests 1 checked 1 failed

### The Contents index

When a document's template on the line has a `## Contents` section, the document must have one too, as [conventions.md](../../docs/process/conventions.md#contents-index-of-process-documents) sets out: the first section after the title, a nested list with one link per heading below the title, in order, each entry two spaces deeper than the nearest heading above it of a higher level (a `##` not indented), each showing its heading's text and linking its GitHub anchor. Duplicate headings link `-1`, `-2` as GitHub numbers them. A decision record is asked for its index only when it is new, not yet on the line, since a merged record is never edited. A new record also takes the next number after the highest one merged on the line. The check refuses a missing or misplaced section, a heading left out, an entry out of order or at the wrong depth, a link no heading of the file answers, and any other text in the section.

    tools/chronitondb/doclint.py index FILE              print the Contents section FILE needs
    tools/chronitondb/doclint.py index --write FILE...   put it in the file, in place of the old one, refused when that one holds other text
    tools/chronitondb/doclint.py index --check FILE...   report what is wrong with the index, also for a template

`index` reads the working tree and works on any Markdown file. Authors and agents run `index --write` after any heading changes and before each commit of a document.

A coverage file, `ac-coverage.md` in a design directory, is checked against the coverage file template.

A research report, `docs/research/<issue>-<slug>.md`, is checked against the research report template, and its References row names the issue in its file name. `docs/research/README.md` is not a report.

A review record, `docs/reviews/<work>.md`, is checked against the review record template: its document control table with Status Open or Closed, its five numbered sections in order, its Contents index and no placeholder left. A line that has no review record template yet passes the record over.

### The revision history

    tools/chronitondb/doclint.py history --repo . --templates origin/<line> FILE              print the history link FILE needs
    tools/chronitondb/doclint.py history --repo . --templates origin/<line> --write FILE...   put the link in, and start the revision history of a document that still has the old change history line
    tools/chronitondb/doclint.py history --repo . --templates origin/<line> --check FILE...   report what is wrong with the revision history and its link

`history` reads the working tree. FILE is a path from the repository root. The link is the commits of the file on its line, on the repository the line is fetched from, so it is written the same way after the repository moves or is renamed. `--write` on a document that still carries `Change history: the git history of this file.` puts the table in its place, with one row for the document's version and today's date, and leaves what changed and the decision record for the author to fill in. See [conventions.md](../../docs/process/conventions.md#versions-and-revision-history).

### Decision records

A decision record is checked from where it lives: `docs/design/<dir>/decisions/` for a feature or other work, `docs/decisions/` for the whole project. A record new to the line is named `DEC-<KEY>-nnnn-<slug>.md` with the key of its place, its title opens with its id, no other record has that id, and its number is the next of its key. A record merged on the line is never edited, so it is not held to rules made after it. See [the decision records](../../docs/decisions/README.md#rules).

### Areas, sources and the generated indexes

A document's `Areas` row names areas of the list in [areas.md](../../docs/process/areas.md), read from the line, and an import record's `Source` row one of its sources. Supersede links between decision records are checked both ways. The `Exceptions` row of a design record or fix record says `None` or names each principle the record departs from by its id, joined by commas, each one a principle of [principles.md](../../docs/process/principles.md) on the line. A record merged before the row keeps none until its next version.

    tools/chronitondb/doclint.py indexes --repo . --templates origin/<line>           report each generated index that is not what the documents give
    tools/chronitondb/doclint.py indexes --repo . --templates origin/<line> --write   write them: docs/index/documents.md, decisions.md and areas.md, and INDEX.md in each feature directory

`indexes` reads the header of every document under `docs/`. Once a record names a principle in its `Exceptions` row, `documents.md` ends with the section Exceptions to principles, which lists every such record under each principle. See [conventions.md](../../docs/process/conventions.md#generated-indexes).

### The document graph: `docgraph.py`

    tools/chronitondb/docgraph.py --repo . --templates origin/<line>           exit 1 when docs/index/graph.json is not what the documents give
    tools/chronitondb/docgraph.py --repo . --templates origin/<line> --write   write it

Writes the links between the documents as JSON-LD, from the headers `doclint.py indexes` reads, with the context in `docs/index/context.json`. The same tree gives the same bytes. Python 3, no other dependency. The documents workflow runs the check, with this file taken from the base branch, on every pull request that changes a file under `docs/`, next to the check of the generated indexes. A unit test compares the committed graph with the one the documents of the tree give. See [conventions.md](../../docs/process/conventions.md#the-document-graph).

### The class

The class of a change, its risk, size and reach, is set out in [classification.md](../../docs/process/classification.md). When the template on the line carries the class rows, a feature spec's Risk, Size and Reach rows each hold the level, a colon and the reason, and its Touches row lists what the change touches or says none. The row takes the phrases of the template's row, among them the five that name what the code does on the Critical floor: on-disk files, flush, compaction, streaming and repair. A Low risk that touches a public interface or stock behaviour is refused. Each section the class requires holds its content. Every other section holds its content or the one line `Not applicable: <reason>`, which covers the section's subsections. The section Where problems could occur and its Test plan never say none or low. A plan and a milestone report repeat the feature spec's levels, and a fix record, and a design record not covered by a feature spec, write Where problems could occur in full.

### Tests

`test/doclint/` holds the checker's unit tests, Python's `unittest`, no other dependency. They include a test that every template in `docs/process/templates/` carries a correct index, and tests that run the steps of the workflows as the shell scripts they are, with the environment each workflow gives its step: the check that runs is the one of the base branch, and the name of an import branch counts for a branch of the repository and never for the branch of a fork. The CI workflow runs them in a job of its own, apart from the job that checks the documents with the line's checker.

    python3 -m unittest discover -s tools/chronitondb/test/doclint
