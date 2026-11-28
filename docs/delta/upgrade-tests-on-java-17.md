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

# Delta: Upgrade tests run on Java 17

| Field | Value |
|---|---|
| Title | Upgrade tests run on Java 17 |
| Document type | Record (ISO/IEC/IEEE 15289) |
| Status | Current |
| Version | 1 |
| Author | The maintainers |
| Approver | The maintainer who merges the pull request |
| References | The Origin, Bug, Bug-ChronitonDB and Pull requests fields below. |

Revision history, one row for each version:

| Version | Date | Change | Decision record |
|---|---|---|---|
| 1 | 2026-11-28 | First version | None |

Full history in git: [commits of this file](https://github.com/chronitonlabs/chronitondb/commits/chronitondb-sandbox/docs/delta/upgrade-tests-on-java-17.md)

Location: `docs/delta/`. Process: [the delta register](README.md).

## Contents

- [Header](#header)
- [What](#what)
- [Why](#why)
- [Area](#area)
- [Lines](#lines)

## Header

The fields follow Debian's [DEP-3 patch header convention](https://dep-team.pages.debian.net/deps/dep3/), adapted to a change ChronitonDB carries on top of Apache Cassandra. Author is in the table above. Added, Pull requests, Status, Area and Lines are the register's own. DEP-3 has no such fields. Dates are written YYYY-MM-DD, as DEP-3 writes them.

| Field | Value |
|---|---|
| Description | `.build/run-tests.sh` runs the in-JVM upgrade tests on Java 17 and builds the jar of Apache Cassandra 5.0.9 for them. |
| Origin | ChronitonDB. |
| Bug | none |
| Bug-ChronitonDB | none |
| Forwarded | Not needed. Apache Cassandra's own upgrade paths start at 4.0 and 4.1, which do not run on Java 17, and the line's path starts at a 5.0 release. |
| Added | 2026-11-28 |
| Last-Update | 2026-11-28 |
| Pull requests | `chronitondb-sandbox`: not opened yet. |

## What

Two changes to `.build/run-tests.sh`.

1. `_main` no longer refuses Java 17 for the target `jvm-dtest-upgrade`. In its place, `_build_all_dtest_jars` reads `java.supported` from the `build.xml` of each older version and builds the jar of that version only when the Java in use is in the list. A `build.xml` with no `java.supported` is older than 5.0 and is taken as Java 8 and 11. So on Java 17 the jars of 4.0 and 4.1 are not built, and the script says so for each.
2. `_build_all_dtest_jars` also builds the jar of the tag `cassandra-5.0.9`, the latest Apache Cassandra 5.0 release, where the line's upgrade path starts. The jar keeps the name the stock runner reads, `dtest-5.0.9.jar`.

The CI of the line does not run through this script. It builds the jar of the release in `.github/workflows/chronitondb-apache-dtest-jar.yml` and runs each upgrade test class with `ant test-jvm-dtest-some`.

## Why

The same Java runs every version on an upgrade path. The line supports Java 17 only, and every Apache Cassandra 5.0 release supports it, so the line's path from 5.0.9 runs on Java 17. The stock refusal stopped every upgrade test on Java 17, which on the line means every upgrade test, because the stock upgrade paths from 4.0 and 4.1 need Java 11. The line's upgrade and rollback tests, as [testing.md](../process/testing.md#upgrade-and-rollback-tests) asks for them, need it to run.

## Area

Build scripts: `.build/run-tests.sh`, the functions `_main` and `_build_all_dtest_jars`. A stock upgrade test from 4.0 or 4.1 run through the script on Java 17 now fails on the missing jar of its older version, where the script refused the whole run before.

## Lines

`chronitondb-sandbox`.
