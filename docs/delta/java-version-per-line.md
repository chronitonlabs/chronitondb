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

# Delta: One Java version per line

| Field | Value |
|---|---|
| Title | One Java version per line |
| Document type | Record (ISO/IEC/IEEE 15289) |
| Status | Current |
| Version | 1 |
| Author | The maintainers |
| Approver | The maintainer who merges the pull request |
| References | Pull requests #46 (`chronitondb-5.0`, commit `af8deb8da7`) and #49 (`chronitondb-6.0`, commit `2cffdd4d91`). |

Change history: the git history of this file.

## What

Each line builds, packages and installs on one Java version: Java 17 on `chronitondb-5.0`, Java 21 on `chronitondb-6.0`. `java.default` and `java.supported` in `build.xml` name that version only, so ant refuses any other JDK. The Debian and Red Hat package files depend on that version. The Ant Check workflow runs one job, on that version. On the 6.0 line the build script test cases under `.build/sh/test/` pass 21 as the supported version.

## Why

ChronitonDB code on each line uses one Java language level. Apache Cassandra 5.0 also supports Java 11, and Apache Cassandra 6.0 also supports Java 11 and 17. The JDK is per node, so in a rolling upgrade each node moves to the line's Java version when it restarts on ChronitonDB.

## Area

Build and packaging: `build.xml`, `debian/control`, `redhat/cassandra.spec`, `redhat/noboolean/cassandra.spec` (5.0 line), `.github/workflows/code-check.yaml`, and on the 6.0 line `.build/sh/test/stub-ant-cases.sh` and `.build/sh/test/stub-docker-cases.sh`. The package changes move into ChronitonDB's own packaging under `packaging/` once it exists. The `java.supported` change in `build.xml` stays, since it gates the build itself.

## Lines

`chronitondb-5.0` (Java 17) and `chronitondb-6.0` (Java 21).

## Upstream status

Ours only. The Java versions Apache Cassandra supports are Apache's choice for its own users.

## Date

2026-10-31
