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

# Working with Apache Cassandra upstream

ChronitonDB relates to Apache Cassandra as Ubuntu relates to Debian. Apache Cassandra is upstream. Each ChronitonDB line is a superset of the Apache Cassandra releases of its major version: it contains every Apache patch release we have imported, plus the changes in the [delta register](../delta/README.md).

The integrator does this work: it watches Apache, prepares every import pull request, resolves conflicts, runs the tests and writes the import record. The reviewer reviews each import pull request and posts its review. A maintainer merges it. See [roles.md](roles.md#integrator).

## Apache files stay untouched

Apache Cassandra's own files stay as Apache has them, so imports never conflict on them. This covers `CHANGES.txt`, `NEWS.txt`, `README.asc`, `doc/`, the root `CONTRIBUTING.md`, `.asf.yaml`, `debian/`, `redhat/`, the Jenkins and CI files and the like.

1. ChronitonDB's own files sit beside them: `.github/README.md`, `CHANGES-chronitondb.txt`, `NEWS-chronitondb.txt`, `docs/`, `packaging/`, `.github/CONTRIBUTING.md` and our own workflows. See [conventions.md](conventions.md#where-things-live).
2. A change to an Apache file is made only where we need it, and it gets its [delta entry](../delta/README.md).

## Imports keep their upstream identity

Every import pull request, a whole release or a single cherry-pick, is merged by a maintainer with a merge commit. The imported commits keep their Apache author, their message and, for a cherry-pick, the `(cherry picked from commit <full hash>)` line. Import pull requests are the only pull requests merged with a merge commit. All our own work is squash merged. See [branching-and-review.md](branching-and-review.md#history-rules).

## Whole Apache releases

1. Every Apache Cassandra patch release of a line's major version is imported into that line in whole, as one import item. The release is always taken.
2. The integrator merges the Apache release tag into an import branch named after the Apache release tag, `import/cassandra-<x.y.z>/<line>`, cut from the line. That merge commit's subject is `import(apache-<version>): merge Apache Cassandra <version>`. A maintainer then merges the import pull request into the line with a merge commit. Every Apache commit keeps its identity, so git itself shows which Apache releases a line contains.
3. Each import is assessed on its merits before its pull request opens: the code checks and the reviewer's checklists run on the imported diff. The integrator resolves conflicts with the ChronitonDB delta. A finding or conflict it cannot resolve goes to the maintainers as a decision: adjust the imported code, offer a fix upstream, or wait for a conflict to be resolved before the merge. An import is never changed for style alone.
4. Apache's own `CHANGES.txt` and `NEWS.txt` arrive with the import and are never edited.

## Before Apache's first release of a major version

Until Apache releases `x.0.0` of a major version, the matching line follows the Apache branch:

1. Every week that Apache's `cassandra-x.y` branch has new commits, the integrator merges it into an import branch named `import/cassandra-x.y-<short hash>/chronitondb-x.y`, cut from the line, and opens an import pull request. That merge commit's subject is `import(apache-<x.y>-branch): merge Apache cassandra-<x.y> at <short hash>`.
2. A maintainer merges the import pull request into the line with a merge commit, like a release import.
3. From Apache's `x.0.0` release onwards, release tags are merged instead.

## Single fixes taken early

A single Apache fix MAY be cherry-picked into a line ahead of the Apache release that contains it, when it is needed early. The integrator proposes it against these criteria: a security fix, a fix our own work depends on, or a fault our users hit. It opens the import pull request with the criterion that applies. The maintainers decide by merging it, and closing it declines the fix.

1. The cherry-picked commit keeps its original Apache author and message, with the `(cherry picked from commit <full hash>)` line added by `git cherry-pick -x`.
2. The import carries the regression test of the original fix.
3. The branch is named `import/CASSANDRA-<n>/<line>`.
4. A maintainer merges the import pull request with a merge commit, so the cherry-picked commit reaches the line unchanged. That merge commit's subject is `import(CASSANDRA-<n>): <original Apache subject>` and its body, taken from the import pull request's description, names the Apache commit hash. See [conventions.md](conventions.md#commit-messages).

## The import record

Each import has a short import record at `docs/imports/<apache-version-or-range>.md`, written from [templates/import-record.md](templates/import-record.md) by the integrator, in the import pull request. It covers:

1. What came in: the Apache release or commit, and the range of commits.
2. Conflicts with ChronitonDB changes, and how each was resolved.
3. Delta entries that Apache has now fixed, which are dropped in the same import.
4. Tests run, in the five test lists of a design record's Testing section. The results go in the evidence of the import pull request.
5. Confirmation that stock behaviour is unchanged with every fork feature off: the parity suite passes.
6. Configuration changes: every changed setting in Apache's two yaml files and every changed default in `Config.java`, each mapped to our own file. See [Configuration changes](#configuration-changes).

Tests for this change MAY be none only with a written reason in the record. For example, the range changes only build files and documentation, or an Apache fix merged without a test and the suites at risk cover the changed code. A bare none is refused. The suites at risk and the stock suites still run, and the reviewer checks the reason.

## Configuration changes

ChronitonDB ships its own configuration file, `conf/cassandra_chronitondb.yaml`. Apache's `conf/cassandra.yaml` and `conf/cassandra_latest.yaml` stay untouched. See [release.md](release.md#the-configuration-file). Every import, a whole release, a weekly branch merge or a single fix, is checked for configuration changes over the imported range:

1. Every setting in Apache's two yaml files that was added, removed, or changed in value or comment.
2. Every default that changed, meaning the value a node runs with when its yaml file leaves the setting out: the defaults in `Config.java`, nested options named with dots such as `sstable.selected_format`, and the defaults a node computes at startup. A setting a cluster's yaml file leaves out takes its default, so a changed default changes running clusters too.

The integrator lists each change in the import record's Configuration changes section and maps it to our file:

1. **Taken:** our file follows Apache.
2. **Taken with a different value:** our file has the setting with our value, and the record gives the value and the reason.
3. **Not taken:** our file leaves it out or keeps its old value, and the record gives the reason.

A change to a setting of the line's minimum setup is also flagged for the line's upgrade runbook. The reviewer checks the mapping, and a maintainer approves it by merging the import. Within a line, the values our file ships change only for a fix. Upgrading within a line never changes behaviour by itself, so any other value change waits for the next line.

## The delta register

The [delta register](../delta/README.md) lists every change ChronitonDB carries on top of Apache Cassandra: features, fixes to stock code, and build changes. Each entry has a header that follows Debian's [DEP-3 patch header convention](https://dep-team.pages.debian.net/deps/dep3/). It says what the change is, why we carry it, where it came from, and in its Forwarded field whether it has gone to Apache Cassandra:

1. **Offered,** with the Apache JIRA.
2. **Declined,** with the Apache JIRA and a one line reason.
3. **Not needed,** with the reason.

Every pull request that changes stock code or stock behaviour adds or updates its entry. The reviewer checks this. Entries that Apache has since fixed are dropped at the next import.

## Offering changes upstream

1. Every fix to stock code gets an Apache JIRA. A maintainer starts each offer. The integrator drafts the JIRA and the patch, and the maintainers file them.
2. Features are offered upstream only when the maintainers decide, case by case.
3. Code offered to Apache is reformatted to Apache Cassandra's style and follows Apache Cassandra's contribution process.

## The upstream radar

The upstream radar is the integrator's daily watch of Apache Cassandra, summed up for the maintainers in a weekly digest. It looks for:

1. New Apache Cassandra releases on each line's major version.
2. New commits on the Apache branch of a line whose major version Apache has not yet released.
3. Apache JIRAs and commits that touch areas in the delta register, or look like security fixes.
4. Apache fixes worth taking early, as single cherry-picks.
5. Delta entries that Apache has since fixed.

The security engineer watches Apache security announcements and dependency advisories with the integrator. See [security.md](security.md). Whole releases and the weekly branch merges are always imported. The integrator proposes single fixes to take early against the criteria in [Single fixes taken early](#single-fixes-taken-early), and the maintainers decide by merging. Each import gets a public GitHub issue and follows this page.

## Security coordination with Apache

When a vulnerability affects stock Apache Cassandra code, we follow the norm Linux distributions use. The full process is in [security.md](security.md#when-stock-apache-cassandra-is-affected). The steps below are the whole rule.

1. We fix it privately at once.
2. We notify the Apache Cassandra security team at once, with the fix.
3. We release our fix at most 14 days later. Sooner if it becomes public or is exploited. At once if it is already public.
4. If we learned of the vulnerability from Apache under their embargo, their terms bind us.
