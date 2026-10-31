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
2. Each entry says what the change is, why we carry it, the area it touches, the lines that carry it, its upstream status and the date of its last change.
3. The upstream status is one of: offered (with the Apache JIRA), declined upstream, or ours only.

## Keeping it current

1. Every pull request that changes stock code or stock behaviour adds or updates its entry. The reviewer checks this.
2. Every fix to stock code gets an Apache JIRA, filed by the maintainers, and its entry records it.
3. Features are offered to Apache Cassandra only when the maintainers decide, case by case.
4. The integrator keeps the register current. Its upstream radar flags entries that Apache Cassandra has since fixed. Those entries are dropped at the next import, and its import record in `docs/imports/` lists them.

See [upstream.md](../process/upstream.md) for how imports and upstreaming work.

## Index

| Entry | Area | Lines | Upstream status |
|---|---|---|---|
| [One Java version per line](java-version-per-line.md) | Build and packaging | 5.0, 6.0 | Ours only |
| [Apache GitHub checks run on pull requests to the lines](github-checks-on-pull-requests.md) | Continuous integration | 5.0, 6.0 | Ours only |
| [Apache workflow actions pinned to commits](github-actions-pinned.md) | Continuous integration | 5.0, 6.0 | Ours only |
| [run-ci accepts this repository](run-ci-accepts-chronitondb.md) | Build scripts | 5.0, 6.0 | Ours only |
| [Import order check suppressed for ChronitonDB code](checkstyle-import-order-suppression.md) | Build | 6.0 | Ours only |
| [run-ci routes 6.0 versions on the 5.0 line](run-ci-6.0-version-routing.md) | Build scripts | 5.0 | Ours only, until an Apache 5.0 release brings it |
