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

# Import: {Apache release, CASSANDRA-n or owner/repo@12 character hash} into {line}

| Field | Value |
|---|---|
| Title | Import of {Apache release, CASSANDRA-n or owner/repo@12 character hash} into {line} |
| Document type | Record (ISO/IEC/IEEE 15289) |
| Status | Draft, Approved or Superseded |
| Version | {n} |
| Author | Integrator: {GitHub username} |
| Approver | The maintainer who merges the import pull request |
| References | Issue #{issue}. Apache release tag or commit hash, or the other project's commit link. Import pull request. |
| Areas | {one or more areas of [areas.md](../areas.md), joined by commas} |
| Source | {apache-cherry-pick, apache-merge or third-party, as [areas.md](../areas.md#the-sources) names them} |

Revision history, one row for each version:

| Version | Date | Change | Decision record |
|---|---|---|---|
| 1 | {RFC 3339 date} | First version | {the id of the decision record behind this version, or None} |

Full history in git: [commits of this file]({the address `tools/chronitondb/doclint.py history --write` puts here})

Location: `docs/imports/<apache-version-or-range>.md`, or `docs/imports/<owner>-<repo>-<12 character hash>.md` for a commit from another project, added in the import pull request. Process: [upstream.md](../upstream.md).

## Contents

- [1. What came in](#1-what-came-in)
- [2. Assessment](#2-assessment)
- [3. Conflicts with ChronitonDB changes](#3-conflicts-with-chronitondb-changes)
- [4. Delta entries dropped](#4-delta-entries-dropped)
- [5. Tests run](#5-tests-run)
  - [Tests for this change](#tests-for-this-change)
  - [Existing suites at risk](#existing-suites-at-risk)
  - [Apache Cassandra suites run unchanged](#apache-cassandra-suites-run-unchanged)
  - [Tracing test](#tracing-test)
  - [Formats and configurations](#formats-and-configurations)
- [6. Apache Cassandra behaviour confirmed](#6-apache-cassandra-behaviour-confirmed)
- [7. Security](#7-security)
- [8. Configuration changes](#8-configuration-changes)

## 1. What came in

{Whole release: the Apache release tag and the commit range since the last import. Before Apache's first release of the major version: the Apache branch commit range merged this week. Single fix: the Apache JIRA, the Apache commit hash and the line `Reason: <why the line takes it now>`, in plain words and from no fixed list. Commit from another project: the repository, the full commit hash, its author and subject, the branch of that repository that holds it, its approved licence, the `Reason:` line and the line `Origin: https://github.com/<owner>/<repo>/commit/<full hash>`.}

## 2. Assessment

{The code checks and review checklists run on the imported diff. Each correctness, security or performance finding of major severity or worse in the imported code, and each conflict with something ChronitonDB adds, with its evidence and the maintainers' decision: reported to Apache Cassandra, import held, fixed as a fix to stock, or accepted. Findings on shape limits and style in Apache Cassandra's own code are listed and go no further. An import ahead of an Apache Cassandra release, a branch merge or a single fix taken early, also names each stored form it changes, such as an on-disk version, with the maintainers' decision on it, or says in one line that it changes none: until Apache Cassandra releases that form, a cluster on the line has no Apache Cassandra release to move back to. See [upstream.md](../upstream.md#whole-apache-releases) and [PRINCIPLE-003](../principles.md#principle-003).}

## 3. Conflicts with ChronitonDB changes

{Each conflict: the files, our change involved, and how it was resolved.}

## 4. Delta entries dropped

{Entries in the delta register that this import makes obsolete, because Apache now has the change.}

## 5. Tests run

{The tests this import runs, in the five lists of the design record's Testing section, with the same headings and format. Keep the headings exact, since a check may read the lists. One fully qualified test class per line. Write `none` under a heading that has no entry, except Tests for this change, which takes a written reason. The results go in the evidence of the import pull request, not in this record. See [design-record.md](design-record.md#14-testing).}

### Tests for this change

{The regression tests of the imported fixes. When there are none, one line `none, because` with the reason, for example `none, because this range changes only build files and documentation`, or `none, because CASSANDRA-n merged without a test and the suites at risk cover the changed code`. A bare `none` is refused. The suites at risk and the stock suites still run, and the reviewer checks the reason.}

### Existing suites at risk

{Unit test suites and in-JVM distributed test suites around the changed areas.}

### Apache Cassandra suites run unchanged

{Apache Cassandra's own suites, which run as [testing.md](../testing.md#full-test-suites) says, with fork features off and with them on, and pass without modification.}

### Tracing test

{The test that shows the imported change in query tracing, for a change on a traced request. A change with other signals names their tests here too, for example the test of a changed metric or log line of a compaction change. Or "does not apply, because" with the reason.}

### Formats and configurations

{`yes` when the import reads a setting the test configurations set differently, for example when it touches compaction, an on-disk format or the memtable, so the tests also run with both sstable formats and in every test configuration [testing.md](../testing.md#test-levels) asks for. Otherwise `no`.}

## 6. Apache Cassandra behaviour confirmed

{The parity suite result with every fork feature off, or until the parity suite exists the result of the stock suites with every fork feature off. See [upstream.md](../upstream.md#the-import-record).}

## 7. Security

{Apache security fixes in this import, by Apache JIRA once public, and the VEX updates they need.}

## 8. Configuration changes

{Every setting that changed over the imported range in Apache's `conf/cassandra.yaml` or `conf/cassandra_latest.yaml`: added, removed, or changed in value or comment. Then every default that changed over the same range: a default in `Config.java`, a nested option named with dots such as `sstable.selected_format`, or a default the node computes at startup in `DatabaseDescriptor.java`. A new option block is one row. One row each, mapped to ChronitonDB's own `conf/cassandra_chronitondb.yaml`. Write "None." in place of the table when neither file and no default changed. See [upstream.md](../upstream.md#configuration-changes).}

| Setting | Changed in | Apache change | Our file |
|---|---|---|---|
| {setting name} | {`cassandra.yaml`, `cassandra_latest.yaml`, `Config.java` or `DatabaseDescriptor.java`} | {added, removed, the old and new value, `effective` with the old and new value of a default only startup changes, or the comment change} | {`taken`, `taken with a different value` and the value with the reason, or `not taken` with the reason} |
