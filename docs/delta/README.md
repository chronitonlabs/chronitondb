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

# The delta register

This register lists every change ChronitonDB carries on top of Apache Cassandra on its lines: features, fixes to stock code, and build and packaging changes. It works the way Ubuntu tracks its changes against Debian. Anyone can read here what ChronitonDB changes, why, and whether the change has been offered to Apache Cassandra.

## Entries

1. Each entry is one Markdown file in this folder, written from [the delta entry template](../process/templates/delta-entry.md).
2. The file name is a short descriptive name. It is the entry's id and does not change. Entries are not numbered.
3. Each entry has a header that follows Debian's [DEP-3 patch header convention](https://dep-team.pages.debian.net/deps/dep3/), adapted to a change ChronitonDB carries on top of Apache Cassandra. Most fields keep their DEP-3 names. Added, Pull requests, Status, Area and Lines are the register's own.

### Fields

1. **Description**: one line saying what we carry. The What and Why sections of the entry are the long description.
2. **Origin**: where the change came from. ChronitonDB, an Apache commit taken whole, a backport of part of an Apache commit, or another fork, with a link to the commit.
3. **Bug**: the Apache JIRA, `CASSANDRA-<n>`, as a link, or none.
4. **Bug-ChronitonDB**: our GitHub issue in this repository, or none. This is the Bug-Vendor field of DEP-3.
5. **Forwarded**: whether the change has gone to Apache Cassandra. Offered, with the Apache JIRA. Declined, with the Apache JIRA and a one line reason. Not needed, with the reason. Offered and Declined both mean DEP-3's forwarded. Not needed is DEP-3's `not-needed`.
6. **Author**: who wrote the entry, and the change when its Origin is ChronitonDB. A change from Apache or another fork keeps its author in its Origin commit. Author sits in the document control table.
7. **Last-Update**: the date of the last change to the entry, written YYYY-MM-DD.
8. **Added**: the date ChronitonDB first carried the change on a line, written YYYY-MM-DD. Ours, not in DEP-3.
9. **Pull requests**: the pull requests that carry the change on each line, with their commits. Ours, not in DEP-3.
10. **Status**: Current or Dropped. It sits in the document control table. Ours, not in DEP-3.
11. **Area**: the part of the tree and the behaviour the change touches. Ours, not in DEP-3.
12. **Lines**: the lines that carry the change. Ours, not in DEP-3.

## Keeping it current

1. Every pull request that changes stock code or stock behaviour adds or updates its entry, with a new Last-Update and its row in the index below. A pull request check enforces it once it exists, and the reviewer reads the entry.
2. Every fix to stock code gets an Apache JIRA, filed by the maintainers. Its entry records it in Bug and Forwarded.
3. Features are offered to Apache Cassandra only when the maintainers decide, case by case.
4. The integrator keeps the register current. Its upstream radar flags entries that Apache Cassandra has since fixed. Those entries are dropped at the next import, and its import record in `docs/imports/` lists them.

See [upstream.md](../process/upstream.md) for how imports and upstreaming work.

## Index

Ordered by area, then by name.

| Entry | Area | Lines | Forwarded | Added | Last update | Issue |
|---|---|---|---|---|---|---|
| [Import order check suppressed for ChronitonDB code](checkstyle-import-order-suppression.md) | Build | 6.0 | Not needed | 2026-10-30 | 2026-11-01 | none |
| [One Java version per line](java-version-per-line.md) | Build and packaging | 5.0, 6.0 | Not needed | 2026-10-30 | 2026-11-01 | none |
| [run-ci accepts this repository](run-ci-accepts-chronitondb.md) | Build scripts | 5.0, 6.0 | Not needed | 2026-10-30 | 2026-11-01 | none |
| [run-ci routes 6.0 versions on the 5.0 line](run-ci-6.0-version-routing.md) | Build scripts | 5.0 | Not needed, Apache has it on 6.0 | 2026-10-30 | 2026-11-01 | none |
| [Apache GitHub checks run on pull requests to the lines](github-checks-on-pull-requests.md) | Continuous integration | 5.0, 6.0 | Not needed | 2026-10-31 | 2026-11-01 | none |
| [Apache workflow actions pinned to commits](github-actions-pinned.md) | Continuous integration | 5.0, 6.0 | Not needed | 2026-10-30 | 2026-11-01 | none |
