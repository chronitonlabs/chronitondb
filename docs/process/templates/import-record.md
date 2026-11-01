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

# Import: {Apache release or CASSANDRA-n} into {line}

| Field | Value |
|---|---|
| Title | Import of {Apache release or CASSANDRA-n} into {line} |
| Document type | Record (ISO/IEC/IEEE 15289) |
| Status | Draft, Approved or Superseded |
| Version | {n} |
| Author | Integrator: {GitHub username} |
| Approver | The maintainer who merges the import pull request |
| References | Issue #{issue}. Apache release tag or commit hash. Import pull request. |

Change history: the git history of this file.

Location: `docs/imports/<apache-version-or-range>.md`, added in the import pull request. Process: [upstream.md](../upstream.md).

## 1. What came in

{Whole release: the Apache release tag and the commit range since the last import. Before Apache's first release of the major version: the Apache branch commit range merged this week. Single fix: the Apache JIRA, the Apache commit hash and the reason it is taken early (security, a dependency of our work, or a fault our users hit).}

## 2. Assessment

{The code checks and review checklists run on the imported diff. Findings, and the maintainers' decision on each.}

## 3. Conflicts with ChronitonDB changes

{Each conflict: the files, our change involved, and how it was resolved.}

## 4. Delta entries dropped

{Entries in the delta register that this import makes obsolete, because Apache now has the change.}

## 5. Tests run

{The tests this import runs, in the five lists of the design record's Testing section, with the same headings and format. Tooling reads them, so keep the headings. One fully qualified test class per line. Write `none` under a heading that has no entry, except Tests for this change, which takes a written reason. The results go in the evidence of the import pull request, not in this record. See [design-record.md](design-record.md#14-testing).}

### Tests for this change

{The regression tests of the imported fixes. When there are none, one line `none, because` with the reason, for example `none, because this range changes only build files and documentation`, or `none, because CASSANDRA-n merged without a test and the suites at risk cover the changed code`. A bare `none` is refused. The suites at risk and the stock suites still run, and the reviewer checks the reason.}

### Existing suites at risk

{Unit test suites and in-JVM distributed test suites around the changed areas.}

### Stock suites run unchanged

{Apache Cassandra's own suites, which run with every fork feature off and pass without modification.}

### Tracing test

{The test that shows the imported change in query tracing, or "does not apply, because" with the reason.}

### Formats and configurations

{`yes` when the import touches compaction or an on-disk format, so the tests also run with both sstable formats and both unit test configurations. Otherwise `no`.}

## 6. Stock behaviour confirmed

{The parity suite result with every fork feature off.}

## 7. Security

{Apache security fixes in this import, by Apache JIRA once public, and the VEX updates they need.}

## 8. Configuration changes

{Every setting that changed over the imported range in Apache's `conf/cassandra.yaml` or `conf/cassandra_latest.yaml`: added, removed, or changed in value or comment. Then every default in Apache's `Config.java` that changed over the same range. One row each, mapped to ChronitonDB's own `conf/cassandra_chronitondb.yaml`. Write "None." in place of the table when neither file and no default changed. See [upstream.md](../upstream.md#configuration-changes).}

| Setting | Changed in | Apache change | Our file |
|---|---|---|---|
| {setting name} | {`cassandra.yaml`, `cassandra_latest.yaml` or `Config.java`} | {added, removed, the old and new value, or the comment change} | {`taken`, `taken with a different value` and the value with the reason, or `not taken` with the reason} |
