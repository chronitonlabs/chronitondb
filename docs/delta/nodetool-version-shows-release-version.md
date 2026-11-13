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

# Delta: nodetool version shows the ChronitonDB release version

| Field | Value |
|---|---|
| Title | nodetool version shows the ChronitonDB release version |
| Document type | Record (ISO/IEC/IEEE 15289) |
| Status | Current |
| Version | 1 |
| Author | developer: chronitondb-agent |
| Approver | The maintainer who merges the pull request |
| References | The Origin, Bug, Bug-ChronitonDB and Pull requests fields below. |

Change history: the git history of this file.

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
| Description | `nodetool version` prints the node's ChronitonDB release version on its `ReleaseVersion:` line, behind a switch that is on by default. |
| Origin | ChronitonDB. |
| Bug | none |
| Bug-ChronitonDB | [#67](https://github.com/chronitonlabs/chronitondb/issues/67) |
| Forwarded | Not needed. The release version of a ChronitonDB build means nothing to Apache Cassandra. |
| Added | 2026-11-13 |
| Last-Update | 2026-11-13 |
| Pull requests | `chronitondb-sandbox`: the code pull request of #67, not merged yet. |

## What

On a ChronitonDB node with the switch `nodetool_release_version_enabled` on, the default, `nodetool version` prints the node's ChronitonDB release version, for example `5.0-chronitondb3`, on the stock `ReleaseVersion:` line. The `GitSHA:` line keeps its label and its `--verbose` flag. With the switch off, against a node without the fork MBean, or for a JMX role without a grant on it, nodetool prints the stock lines.

The stock edits are hook lines only. `build.xml` gains the property `chronitondb.version` and writes it as one more key, `ReleaseVersion`, at the end of the stock `version.properties`. `Config` gains the field `nodetool_release_version_enabled`. `StorageService.initServer` registers the MBean `org.chronitondb:type=ReleaseVersion` after the stock MBeans. The stock `version` command calls the fork class `VersionOutput` first. `NodeTool` lists the two new commands `enablereleaseversion` and `disablereleaseversion`.

On every node, with the switch on or off, the change also adds one row to `system_views.settings` and the `Node configuration:` log line, two commands to `nodetool help`, the start log line `ChronitonDB release version:`, one MBean, the counter `org.chronitondb.metrics:type=ReleaseVersion,name=Reported`, and the key in the properties file. The design record lists each with its reason in its section 3.

Nothing else changes. Apache Cassandra's version string stays in gossip, `system.local`, drivers, `bin/cassandra -v`, the cqlsh banner and the start log line `Cassandra version:`.

## Why

During a rolling upgrade an operator needs to ask each node which ChronitonDB release it runs. The stock command only names the Apache Cassandra version the line is built on, which stays the same across ChronitonDB releases. The maintainers settled the output in decision record 0002 and in [release.md](../process/release.md#what-nodetool-version-shows).

## Area

Tools and build: `build.xml`, `src/java/org/apache/cassandra/config/Config.java`, `src/java/org/apache/cassandra/service/StorageService.java`, `src/java/org/apache/cassandra/tools/NodeTool.java` and `src/java/org/apache/cassandra/tools/nodetool/Version.java`, with the fork code in `org.chronitondb.version` and `org.chronitondb.tools.nodetool`. The design record is [VER-release-version](../design/VER-release-version/design-record.md).

## Lines

`chronitondb-sandbox`.
