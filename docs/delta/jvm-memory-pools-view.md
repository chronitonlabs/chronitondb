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

# Delta: JVM memory pools view in system_views

| Field | Value |
|---|---|
| Title | JVM memory pools view in system_views |
| Document type | Record (ISO/IEC/IEEE 15289) |
| Status | Current |
| Version | 1 |
| Author | developer: chronitondb-agent |
| Approver | The maintainer who merges the pull request |
| References | The Origin, Bug, Bug-ChronitonDB and Pull requests fields below. |

Revision history, one row for each version:

| Version | Date | Change | Decision record |
|---|---|---|---|
| 1 | 2026-11-25 | First version | None |

Full history in git: [commits of this file](https://github.com/chronitonlabs/chronitondb/commits/chronitondb-sandbox/docs/delta/jvm-memory-pools-view.md)

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
| Description | `SystemViewsKeyspace` adds the table `system_views.jvm_memory_pools` of ChronitonDB to the tables of `system_views`. |
| Origin | ChronitonDB. |
| Bug | none |
| Bug-ChronitonDB | [#161](https://github.com/chronitonlabs/chronitondb/issues/161) |
| Forwarded | Not needed. It is a feature of ChronitonDB, and features are offered to Apache Cassandra only when the maintainers decide. |
| Added | 2026-11-25 |
| Last-Update | 2026-11-25 |
| Pull requests | `chronitondb-sandbox`: the pull request that adds this entry, not merged yet. |

## What

The constructor of `SystemViewsKeyspace` in `src/java/org/apache/cassandra/db/virtual/SystemViewsKeyspace.java` builds the fixed list of the tables of `system_views`. ChronitonDB adds one line to that list, `.add(new JvmMemoryPoolsTable(VIRTUAL_VIEWS))`, after the tables of Apache Cassandra, and one import of `org.chronitondb.virtual.JvmMemoryPoolsTable`. Every table of Apache Cassandra stays in the list as it was.

The table shows the memory pools of the JVM of the node, one row for each pool. Its reference page is [jvm-memory-pools.md](../reference/virtual-tables/jvm-memory-pools.md).

## Why

A table is in `system_views` only when it is in that list, so the table of ChronitonDB needs this hook. The table itself lives in the package `org.chronitondb.virtual`. The rule for such a hook is [PRINCIPLE-010](../process/principles.md#principle-010).

## Area

Virtual tables: `src/java/org/apache/cassandra/db/virtual/SystemViewsKeyspace.java`. The list of the tables of `system_views`, which `system_virtual_schema.tables` and `DESCRIBE` show, holds one more table.

## Lines

`chronitondb-sandbox`.
