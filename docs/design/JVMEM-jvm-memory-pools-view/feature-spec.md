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

# Feature spec: JVM memory pools view in CQL

| Field | Value |
|---|---|
| Title | JVM memory pools view in CQL |
| Document type | Specification and description (ISO/IEC/IEEE 15289) |
| Status | Draft |
| Version | 1 |
| Author | Architect: chronitondb-agent |
| Approver | The maintainer who merges the pull request |
| References | Issue #161. Line `chronitondb-sandbox`. Apache base commit `76550e931481e965ae3283d8cf4a59c320d74c55` (Apache Cassandra `cassandra-5.0`). Decision records [DEC-JVMEM-0001](decisions/DEC-JVMEM-0001-jvm-memory-pools-view-has-no-switch.md) and [DEC-JVMEM-0002](decisions/DEC-JVMEM-0002-a-pool-with-no-maximum-shows-minus-one.md). |
| Areas | observability |
| Risk | Normal: by the label the worst Bug Category is Availability, a response crash, which is a read of the view that fails. The floor of [classification.md](../../process/classification.md#the-floor) applies, because the feature adds a virtual table. The class table of that page rates two faults of this feature Critical: a wrong value in the view, and a node that does not start because of the view. Problems 1 and 2 of section 4 name them with their tests. |
| Size | Normal: one view class, one hook in a file of Apache Cassandra, names that are kept for the line once shipped, and a value the JVM leaves undefined. |
| Reach | One area: virtual tables. Fork code in the new package `org.chronitondb.virtual`, with one hook in `org.apache.cassandra.db.virtual`. |
| Touches | public interface (virtual tables), new feature or switch |

Revision history, one row for each version:

| Version | Date | Change | Decision record |
|---|---|---|---|
| 1 | 2026-11-20 | First version | None |

Full history in git: [commits of this file](https://github.com/chronitonlabs/chronitondb/commits/chronitondb-sandbox/docs/design/JVMEM-jvm-memory-pools-view/feature-spec.md)

Location: `docs/design/JVMEM-jvm-memory-pools-view/feature-spec.md` on the line `chronitondb-sandbox`. The feature key is `JVMEM`, a new key. See [Feature keys and requirement ids](../../process/additive.md#feature-keys-and-requirement-ids). Process: [additive.md](../../process/additive.md).

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in BCP 14 (RFC 2119, RFC 8174) when, and only when, they appear in all capitals, as shown here.

A rule of the project is cited by its id from [principles.md](../../process/principles.md), as a link to its entry. This document cites nothing that a reader of the repository cannot open.

The Risk, Size and Reach rows are the feature's class, as [classification.md](../../process/classification.md) defines it, and match the issue's `risk:`, `size:` and `reach:` labels.

A code fact is cited by its number, as fact 1 to fact 13. Section 12 holds each one with its symbol, file, line and the tree it was read in.

## Contents

- [1. Purpose and scope](#1-purpose-and-scope)
  - [Non-goals](#non-goals)
- [2. Architecture](#2-architecture)
  - [2.1 Context and scope](#21-context-and-scope)
  - [2.2 Building blocks](#22-building-blocks)
  - [2.3 Runtime view](#23-runtime-view)
  - [2.4 Data and formats](#24-data-and-formats)
  - [2.5 Cross cutting concepts](#25-cross-cutting-concepts)
  - [2.6 Deployment](#26-deployment)
  - [2.7 Package dependencies and hook points](#27-package-dependencies-and-hook-points)
  - [2.8 Feature class and switches](#28-feature-class-and-switches)
- [3. Feature requirements](#3-feature-requirements)
- [4. Where problems could occur](#4-where-problems-could-occur)
  - [4.1 Test plan](#41-test-plan)
- [5. Quality requirements](#5-quality-requirements)
- [6. Threat model](#6-threat-model)
- [7. Compatibility](#7-compatibility)
  - [7.1 On-disk format changes](#71-on-disk-format-changes)
  - [7.2 Mixed-version cluster](#72-mixed-version-cluster)
  - [7.3 Upgrade path and prerequisites](#73-upgrade-path-and-prerequisites)
  - [7.4 Rollback path](#74-rollback-path)
  - [7.5 Runbook entries](#75-runbook-entries)
- [8. Dependencies](#8-dependencies)
- [9. Risks](#9-risks)
- [10. Decisions](#10-decisions)
- [11. Milestones outline](#11-milestones-outline)
- [12. Prior art](#12-prior-art)
- [Glossary](#glossary)

## 1. Purpose and scope

An operator sees the memory pools of a node's JVM over JMX today, and nowhere in CQL. This feature adds one read only virtual table to the `system_views` keyspace. A read of it returns one row for each memory pool of the JVM of the node that answers. Each row holds the name of the pool, whether it is heap or non-heap memory, and its used, committed and maximum size in bytes, as the JVM reports them at the read.

The view is for operators who check a node's memory with `cqlsh` or a driver and have no JMX access to the node. It lets them see how full each pool is, such as the old generation, the metaspace and the code cache.

In scope:

1. The view, with its five columns.
2. Its documentation, which names the view and each column.

### Non-goals

1. Direct and mapped buffer pools. They are not memory pools of the JVM and they stay on JMX.
2. Counts and pauses of the garbage collector. The need is memory.
3. One view that shows every node. Each node reports its own JVM, as every table of `system_views` reports its own node.
4. A nodetool command, a metric or an MBean. The need is CQL, and the JVM's own MBeans stay as they are.
5. The other values the JVM holds for a pool: its initial size, its peak usage, its usage after the last collection, its thresholds and a ratio of used to maximum. The view carries the five values named above.
6. A history of the values. The view holds the values of the moment of the read.
7. A switch for the view. Section 2.8 says why it needs none.

## 2. Architecture

The feature is one class of the project and one line in a file of Apache Cassandra. The class defines the table and builds its rows from the JVM's platform beans each time the view is read. The line adds the class to the list of tables of `system_views`. Nothing is stored, nothing is sent to another node and nothing runs between two reads.

### 2.1 Context and scope

1. **Clients.** An operator sends a `SELECT` on the view with `cqlsh` or a driver, to the node whose JVM is of interest. The node that receives the statement answers it by itself, with no message to another node (fact 7).
2. **The JVM.** The view reads the memory pools through `java.lang.management.ManagementFactory.getMemoryPoolMXBeans`, the JDK's own interface. The same beans stand behind the MBeans `java.lang:type=MemoryPool,name=<pool>` that JMX shows.
3. **Apache Cassandra.** The view is a virtual table like the other tables of `system_views`. Apache Cassandra's own code parses the statement, checks the permission (fact 9), filters and limits the rows and lists the view in `system_virtual_schema`. The feature changes none of that code.
4. **Not touched.** The schema tables, the data files, the commit log, gossip, the messages between nodes, the settings, nodetool and JMX.

### 2.2 Building blocks

**The view class.** A class of the project in `src/java/org/chronitondb/virtual/`. It extends `AbstractVirtualTable` of Apache Cassandra, whose constructor a class of another package can call (fact 2), and fills a `SimpleDataSet` at each read (fact 3). It defines this table:

| Column | CQL type | Kind | What it holds |
|---|---|---|---|
| `name` | `text` | partition key | The name of the pool as the JVM reports it, unchanged. For example `G1 Old Gen`, `Metaspace` or `CodeHeap 'non-nmethods'`. |
| `type` | `text` | regular | `HEAP` for a pool of heap memory, `NON_HEAP` for any other pool. These are the names of the two values of `java.lang.management.MemoryType`, and the text JMX shows for the pool's `Type` attribute. |
| `used_bytes` | `bigint` | regular | The memory in use in the pool, in bytes. |
| `committed_bytes` | `bigint` | regular | The memory the operating system has committed to the pool, in bytes. |
| `max_bytes` | `bigint` | regular | The largest size the pool can have, in bytes, or -1 where the JVM defines no maximum ([DEC-JVMEM-0002](decisions/DEC-JVMEM-0002-a-pool-with-no-maximum-shows-minus-one.md)). |

The table is `system_views.jvm_memory_pools`. The size columns end in `_bytes` as the size columns of `system_views.caches` do (fact 5). The table is keyed by the name of the pool, and its rows come back in the order of that name, as the rows of `system_views.thread_pools` do (fact 4).

For one row the view calls `MemoryPoolMXBean.getUsage` once and takes the three sizes from the one `MemoryUsage` object it returns. So the three sizes of a row belong to one moment. The rows of one read are taken one after the other, so two rows of one read can be a few instructions apart.

A read on a node of this line, on OpenJDK 17.0.21 with the G1 collector and a 512 MiB heap, would show:

```
 name                               | type     | used_bytes | committed_bytes | max_bytes
------------------------------------+----------+------------+-----------------+------------
 CodeHeap 'non-nmethods'            | NON_HEAP |    1177984 |         2555904 |    5840896
 CodeHeap 'non-profiled nmethods'   | NON_HEAP |     482432 |         2555904 |  122908672
 CodeHeap 'profiled nmethods'       | NON_HEAP |    2332800 |         2555904 |  122908672
 Compressed Class Space             | NON_HEAP |    1173816 |         1245184 | 1073741824
 G1 Eden Space                      | HEAP     |   22020096 |        28311552 |         -1
 G1 Old Gen                         | HEAP     |     970752 |       508559360 |  536870912
 G1 Survivor Space                  | HEAP     |          0 |               0 |         -1
 Metaspace                          | NON_HEAP |    9829624 |        10027008 |         -1
```

The values are those a small Java program printed from the same beans on that JVM. Which pools a node has depends on its JDK and its collector, and the view shows whatever the JVM reports.

**The hook.** One line in the constructor of `SystemViewsKeyspace` adds the view to the tables of `system_views`, beside the tables of Apache Cassandra (fact 1). Section 2.7 names the file.

**The documentation.** A reference page under `docs/` names the view and each column, as FREQ-JVMEM-012 and FREQ-JVMEM-013 say.

The interfaces between the blocks are those of Apache Cassandra: the hook passes the keyspace name to the constructor of the view class, and Apache Cassandra calls the view class through `AbstractVirtualTable` when a statement reads the view.

### 2.3 Runtime view

A `SELECT` on the view runs on the node that receives it, in the thread that runs the statement (fact 7). The view asks the JVM for its memory pools, reads the usage of each and returns the rows. No other request path, no write path and no background path is touched.

### 2.4 Data and formats

Not applicable: the feature stores nothing on disk, writes nothing to the schema tables and sends nothing between nodes.

### 2.5 Cross cutting concepts

1. **Isolation.** The feature adds no work to a path that Apache Cassandra already has, so it needs no pool, limit or budget of its own ([PRINCIPLE-051](../../process/principles.md#principle-051)). A read of the view is a new statement, and it costs one call to the JVM for the list of pools and one call for each pool. The number of pools is the JVM's, 8 in the example of section 2.2, and does not grow with data or traffic. The read runs where a read of every table of `system_views` runs.
2. **Performance.** The feature touches no request path of Apache Cassandra and no background path that competes with requests, so no benchmark is planned ([PRINCIPLE-050](../../process/principles.md#principle-050)).
3. **Observability.** The feature adds no setting, no pool, no limit, no background work and no fallback, so it adds no metric, no trace line and no log line of its own ([PRINCIPLE-033](../../process/principles.md#principle-033)). An operator sees the view work by reading it, and sees it fail by the error of the read.
4. **Errors.** The view catches no error. An error that the JVM raises while the view reads a pool fails that statement and no other, and leaves nothing behind, since the view keeps no state.
5. **Security.** Who may read the view is decided by Apache Cassandra's permission check for a table of `system_views` (fact 9). The view shows sizes of the node's JVM and no user data.

### 2.6 Deployment

Not applicable: the feature adds no setting, no command and no file on disk. An operator does nothing to have the view.

### 2.7 Package dependencies and hook points

| Package of the project | MAY import |
|---|---|
| `org.chronitondb.virtual` | The JDK, with `java.lang.management`. From Apache Cassandra: `org.apache.cassandra.db.virtual`, `org.apache.cassandra.db`, `org.apache.cassandra.db.marshal`, `org.apache.cassandra.dht` and `org.apache.cassandra.schema`. |

The package holds the view class and nothing else in this feature. It needs no package private access to a package of Apache Cassandra (fact 2, fact 3).

Hook points:

| File of Apache Cassandra | Why it must import code of the project | Delta entry |
|---|---|---|
| `src/java/org/apache/cassandra/db/virtual/SystemViewsKeyspace.java` | The tables of `system_views` are one fixed list, built in the constructor of this class (fact 1). A table is in `system_views` only when it is in that list. The file already imports a table class from another package, `StorageAttachedIndexTables` (fact 1). | A new entry in `docs/delta/`, written by the item that adds the hook. |

### 2.8 Feature class and switches

Feature class: purely additive, because the feature is reachable only through a virtual table that Apache Cassandra does not have.

The feature has no switch, because nothing needs it turned off: it does no work until the view is read, it keeps no memory, and nodes share nothing of it ([DEC-JVMEM-0001](decisions/DEC-JVMEM-0001-jvm-memory-pools-view-has-no-switch.md), [PRINCIPLE-016](../../process/principles.md#principle-016)).

1. **Default on each line.** The view is present on every node of the line `chronitondb-sandbox` that runs a release with the feature. The delivery plan proposes the line, and this spec names no other.
2. **A feature finished after its line's first release.** The view is present on that line too. It does no work without being asked and adds nothing nodes share, so the edge of [PRINCIPLE-018](../../process/principles.md#principle-018) does not turn it off.
3. **Built in one milestone.** A feature with no switch merges no item that makes unfinished work reachable ([PRINCIPLE-020](../../process/principles.md#principle-020)). So the item that adds the hook delivers the view whole, with its tests and its documentation. Section 11 has one milestone.

## 3. Feature requirements

"The node" is the node that executes the statement. "The view" is the table `system_views.jvm_memory_pools`. "A memory pool" is one element of the list that `ManagementFactory.getMemoryPoolMXBeans` returns in the node's JVM.

FREQ-JVMEM-001 (ubiquitous): The node MUST hold the view, with the columns and types of section 2.2, from its startup and whatever its configuration. Source: stakeholder need, decision record [DEC-JVMEM-0001](decisions/DEC-JVMEM-0001-jvm-memory-pools-view-has-no-switch.md).

FREQ-JVMEM-002 (event driven): When a statement reads the view, the node MUST answer it from exactly one row for each memory pool that its JVM reports at the read. Source: stakeholder need.

FREQ-JVMEM-003 (ubiquitous): The `name` column MUST hold the name of the memory pool as `MemoryPoolMXBean.getName` returns it, unchanged. Source: stakeholder need.

FREQ-JVMEM-004 (ubiquitous): The `type` column MUST hold `HEAP` for a memory pool whose `MemoryPoolMXBean.getType` is heap memory, and `NON_HEAP` for every other memory pool. Source: stakeholder need.

FREQ-JVMEM-005 (ubiquitous): The `used_bytes`, `committed_bytes` and `max_bytes` columns of a row MUST hold the used, the committed and the maximum size in bytes of one `MemoryUsage` object, which the node takes from `MemoryPoolMXBean.getUsage` of that memory pool during the read. Source: stakeholder need.

FREQ-JVMEM-006 (unwanted behaviour): If the JVM defines no maximum for a memory pool, then the `max_bytes` column of its row MUST hold -1. Source: decision record [DEC-JVMEM-0002](decisions/DEC-JVMEM-0002-a-pool-with-no-maximum-shows-minus-one.md).

FREQ-JVMEM-007 (ubiquitous): The node MUST take the values of every row from its own running JVM during the read, with no message to another node and no value kept from an earlier read. Source: stakeholder need.

FREQ-JVMEM-008 (state driven): While no statement reads the view, the feature MUST do no work, which means that it runs no thread and no scheduled task and keeps no value of a memory pool. Source: stakeholder need.

FREQ-JVMEM-009 (ubiquitous): The node MUST apply to a statement on the view the permission check that Apache Cassandra applies to a statement on a table of `system_views` (fact 9), with no check of the feature's own. Source: stakeholder need, [PRINCIPLE-045](../../process/principles.md#principle-045).

FREQ-JVMEM-010 (event driven): When a statement writes to the view or truncates it, the node MUST refuse the statement with the error Apache Cassandra returns for a read only virtual table (fact 8). Source: stakeholder need.

FREQ-JVMEM-011 (ubiquitous): The feature MUST NOT change the definition or the rows of another table, a JMX MBean, a metric or the output of a nodetool command, apart from a surface of Apache Cassandra that lists what the node holds, such as the tables of `system_virtual_schema` and the `DESCRIBE` statements, which show the view as they show every virtual table. Source: stakeholder need, [PRINCIPLE-001](../../process/principles.md#principle-001), [PRINCIPLE-002](../../process/principles.md#principle-002).

FREQ-JVMEM-012 (ubiquitous): The documentation MUST name the view and each of its columns, and give for each column its type and its meaning, the two values of `type` and the meaning of -1 in `max_bytes`. Source: stakeholder need, [PRINCIPLE-077](../../process/principles.md#principle-077).

FREQ-JVMEM-013 (ubiquitous): The documentation MUST say what a read of the view answers on a node that does not have the view, and name the step of section 7.4 for moving back. Source: [PRINCIPLE-062](../../process/principles.md#principle-062), [PRINCIPLE-003](../../process/principles.md#principle-003).

## 4. Where problems could occur

Worst case first.

1. **A node does not start.** An operator sees a node that exits during its start. It is every node that runs the release. It comes from the hook: Apache Cassandra builds the tables of `system_views` once, during the start of the node (fact 1), and a view class whose constructor or static initialiser throws stops that step.
2. **The view shows a wrong value.** An operator reads a size that is not what the JVM reports: a wrong unit, two columns swapped, the three sizes of a row taken from two readings, a maximum shown as a size where the JVM defines none, a wrong type, a pool missing or a pool shown twice. The operator may then resize a heap that needs no change, or miss a pool that is full. It comes from the view class.
3. **A read of the view fails.** An operator sees an error in place of the rows, on every read or on the reads that meet one pool. It comes from the view class, for example from a value that does not fit the type of its column, or from a pool for which the JVM returns no usage. Other statements are not affected.
4. **Another table of `system_views` is missing or fails.** An operator or a monitoring tool sees a table such as `system_views.settings` missing, or a read of it failing. It comes from a wrong edit of the list in `SystemViewsKeyspace`, or from a later import in which Apache Cassandra adds a table of the same name.
5. **The values reach a role that should not see them, or a client changes the view.** A role with no grant reads the rows, or a write to the view is accepted. It comes from a view class that is not built on Apache Cassandra's read only virtual table, or that is added to a keyspace every role may read.
6. **A read is refused during a rolling upgrade.** A monitoring tool whose driver sends the read to a node that does not have the view yet sees `table jvm_memory_pools does not exist` (fact 8). The refusal is Apache Cassandra's own, for any table a node does not have. It ends when every node runs a release with the view.
7. **A grant on the view cannot be revoked after moving back.** An operator gave a role `SELECT` on the view by name, then moved the cluster back. A node without the view refuses a `REVOKE` that names it (fact 10), so the row stays in the auth tables.
8. **The documentation names the view or a column wrongly.** An operator copies a statement from the page and it fails.
9. **The view does work when nobody reads it, or a read costs more than section 2.5 says.** An operator sees a thread, a task or memory of the feature on a node where nobody reads the view, or request threads busy with reads of the view.

### 4.1 Test plan

No scenario module exists on this line. Each requirement is proven by a unit test or an in-JVM distributed test, and each item's design record names them and says how each detects a breach.

1. Problem 1: every test that starts a node fails when the view stops the start. A unit test of the feature starts a test node with the default configuration and reads the view (FREQ-JVMEM-001), and the validation item starts a cluster in an in-JVM distributed test.
2. Problem 2: a unit test reads the view through CQL and compares it with the memory pools the test reads from the JVM in the same process. The set of names and the type and maximum of each pool do not move while the test runs, so they are compared exactly (FREQ-JVMEM-002, FREQ-JVMEM-003, FREQ-JVMEM-004, FREQ-JVMEM-006). A unit test builds a row from a `MemoryUsage` object of its own and expects its three sizes in the three columns, and -1 for an undefined maximum (FREQ-JVMEM-005, FREQ-JVMEM-006). The tests run on each JDK the line's build supports, since the pools differ from one JDK to another.
3. Problem 3: the unit tests of problem 2 read every row, and each row by its name, and expect no error. A test reads the view twice and expects the second answer to hold values taken at the second read (FREQ-JVMEM-007).
4. Problem 4: a test reads the names of the tables of `system_views` from `system_virtual_schema.tables` and expects every table of Apache Cassandra and the view, each once, and reads each table of Apache Cassandra that it can read on a test node (FREQ-JVMEM-011). An import that brings a table of the same name conflicts in the hook file, and the maintainers decide it before the import merges.
5. Problem 5: a test with authentication and authorization on reads the view as a superuser, as a role granted `SELECT` on the view, as a role granted `SELECT` on the keyspace `system_views`, and as a role with no grant, and expects the last to be refused (FREQ-JVMEM-009). A test sends an `INSERT`, an `UPDATE`, a `DELETE` and a `TRUNCATE` on the view and expects Apache Cassandra's refusal (FREQ-JVMEM-010).
6. Problem 6: no test of the feature covers it, because the answer of a node without the view is code of Apache Cassandra that the feature does not touch, and no test on this line starts a node of an earlier release. It is watched by the documentation, which states it (FREQ-JVMEM-013), and a documentation test checks that the page holds the statement.
7. Problem 7: a test grants `SELECT` on the view by name and revokes it on a node that has the view, and expects both to succeed. The refusal on a node without the view is not tested, for the reason of problem 6. The documentation test of problem 6 checks that the page names the step (FREQ-JVMEM-013).
8. Problem 8: a documentation test reads the name of the view and of each column from the page and expects each in `system_virtual_schema.columns` of a test node, and the other way round (FREQ-JVMEM-012).
9. Problem 9: a test starts a test node, reads no row of the view and expects no thread and no scheduled task of the feature. After a read it expects that the feature holds no value of a memory pool (FREQ-JVMEM-008). The cost of a read is not benchmarked, for the reason of section 2.5. It is watched by the review of the view class against that section.

## 5. Quality requirements

Not applicable: the checklist is required from Challenging size, and this feature is Normal size. The design record of its item answers the checklist in small form.

## 6. Threat model

This feature adds no new entry point. It adds no syntax, no setting, no command, no file and no network path. The view is read with the `SELECT` Apache Cassandra already has, and a value a client gives for `name` is compared with the names of the pools in memory and picks no code, file or other resource of the node. Who may read the view is FREQ-JVMEM-009, and that a client cannot change it is FREQ-JVMEM-010. The rows hold sizes of the node's JVM and no user data.

## 7. Compatibility

### 7.1 On-disk format changes

This feature changes no format, schema or protocol. The definition of the view is built in the memory of each node at startup (fact 6). It is not written to the schema tables, no file is written and no message between nodes carries it.

### 7.2 Mixed-version cluster

1. **A read on a node that has the view.** It answers with its rows, also while other nodes do not have the view.
2. **A read on a node that does not have the view.** It is refused with `table jvm_memory_pools does not exist`, as Apache Cassandra refuses a read of any table it does not have (fact 8). A client sees the rows or the refusal by the node its driver sends the statement to. Until every node has the view, a client that needs it sends the read to a node that has it.
3. **A grant on the view by name.** A node that has the view accepts it. A node that does not have the view refuses it with `Resource <table system_views.jvm_memory_pools> doesn't exist` (fact 10). Once given, the grant is a row of the auth tables on every node, in the form Apache Cassandra gives every grant.
4. **A value another release or node wrote.** There is none: the feature stores and sends nothing, so no reader of the feature can meet a value it does not recognise.
5. **A setting that differs between nodes.** There is none.
6. **State kept when a write is applied.** No state is kept. The feature takes no part in a write.

### 7.3 Upgrade path and prerequisites

The supported paths are those of the line: from Apache Cassandra of the same major version onto the line, and from one release of the line to a later one. The feature adds no prerequisite and no setting to the line's minimum setup. Each node has the view from its first start on a release with the feature.

### 7.4 Rollback path

Moving back to an earlier release of the line or to Apache Cassandra needs one step for this feature, and only where a grant names the view.

1. Before the last node that has the view moves back, an operator revokes every grant that was given on the view by name. After that no node accepts a `REVOKE` that names the view (fact 10). A grant on the keyspace `system_views` or on all keyspaces names no table of the feature and needs no step.
2. Nothing else is removed: the feature leaves no file, no schema row and no setting.

A grant row that is left behind names a table the node does not have. `DataResource.fromName` reads such a name without looking the table up (fact 10). What else Apache Cassandra does with such a row is not verified.

No schema object uses the feature, so nothing is removed when an object stops using it.

### 7.5 Runbook entries

The line has no runbook pages yet. The reference page of the view carries the two entries: what a read answers on a node without the view, and the step of section 7.4 (FREQ-JVMEM-013).

## 8. Dependencies

No new dependency. The feature uses `java.lang.management` of the JDK and classes Apache Cassandra already has.

## 9. Risks

| Id | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| R1 | Apache Cassandra later adds a table of the same name to `system_views`. | Unlikely: no Apache Cassandra branch read for this spec has a view of JVM memory (fact 1). | The import conflicts in the hook file, and one of the two names has to give way. | The maintainers decide the conflict before the import merges ([PRINCIPLE-074](../../process/principles.md#principle-074), [PRINCIPLE-082](../../process/principles.md#principle-082)). |
| R2 | A JDK or a collector the line supports reports its pools in a way the view was not tested with. | Possible: the pools differ by JDK and collector. | A read fails or shows an unexpected row on such a node. | The view takes names and values as the JVM reports them and depends on no pool by name. The tests run on each JDK the line's build supports. |

## 10. Decisions

1. [DEC-JVMEM-0001. The JVM memory pools view has no switch and is not held back](decisions/DEC-JVMEM-0001-jvm-memory-pools-view-has-no-switch.md): the view is on every node from startup, because nodes share nothing of it.
2. [DEC-JVMEM-0002. A memory pool with no maximum shows -1 as its maximum](decisions/DEC-JVMEM-0002-a-pool-with-no-maximum-shows-minus-one.md): the number JMX shows, not null.

## 11. Milestones outline

1. **Milestone 1: the view.** The view class, the hook with its delta entry, the unit tests and the documentation, in one build item, and one validation item with the end to end tests. It makes every requirement of section 3 testable. The feature has no second milestone, for the reason of section 2.8.

- For the design record: what the view shows for a memory pool whose usage the JVM does not report, which `MemoryPoolMXBean.getUsage` signals by returning null for a pool that is no longer valid.

## 12. Prior art

**Apache Cassandra.** Three sources are kept apart: our line, ChronitonDB chronitondb-sandbox at `ffa1bc742d`, its base, Apache Cassandra cassandra-5.0 at `76550e9314`, and Apache Cassandra now, which is cassandra-5.0 at `47227d98bf`, cassandra-6.0 at `a02931dea8` and trunk at `45c325a01b`. Our line changes none of the files cited below against its base, so each claim for our line holds for the base at the same line.

No source has a view of JVM memory in CQL (fact 1). What Apache Cassandra shows of the JVM's memory:

1. The JVM's own MBeans `java.lang:type=MemoryPool,name=<pool>` over JMX, which are the JDK's and not Apache Cassandra's code.
2. One log line for each pool at startup, with its name, type and peak usage (fact 11).
3. `nodetool info`, which prints the used and the maximum heap as one line and no pool (fact 12).
4. Apache Cassandra's documentation names a metric `jvm.memory.pools.<memory_pool>.<MetricName>` with the values Committed, Init, Max, Usage and Used: `doc/modules/cassandra/pages/managing/operating/metrics.adoc:1036`, ChronitonDB chronitondb-sandbox at `ffa1bc742d`. No class under `src/java` of our line registers a metric of that name. Where the metric comes from is not verified, and this spec does not rest on it.
5. Trunk has a keyspace of metric tables. Its list of metric groups names no group of JVM memory (fact 13).

What Apache Cassandra got right: the values are the JVM's own, under the JVM's own names, so every tool that knows the JVM reads them. What it lacks: an operator without JMX access sees no pool. This feature keeps the JVM's names and values and adds the CQL surface, on the model of the tables of `system_views` that Apache Cassandra already has (fact 4, fact 5).

**Other systems.** No other system's documentation was read for this version of the spec, so it names no comparable system.

**Code facts.**

| Fact | Claim | Our line and its base | Apache Cassandra now |
|---|---|---|---|
| 1 | The tables of `system_views` are one fixed list built in a constructor. No table of it is about JVM memory. The file imports `StorageAttachedIndexTables` from another package. | `SystemViewsKeyspace.SystemViewsKeyspace`, `src/java/org/apache/cassandra/db/virtual/SystemViewsKeyspace.java:30`, import at line 22, ChronitonDB chronitondb-sandbox at `ffa1bc742d` | The same at line 30 in cassandra-5.0 at `47227d98bf`, and at line 33 with the import at line 24 in cassandra-6.0 at `a02931dea8` and trunk at `45c325a01b` |
| 2 | `AbstractVirtualTable` is a public class with a protected constructor. | `AbstractVirtualTable.AbstractVirtualTable`, `src/java/org/apache/cassandra/db/virtual/AbstractVirtualTable.java:50`, ChronitonDB chronitondb-sandbox at `ffa1bc742d` | The same at line 50 in cassandra-5.0 at `47227d98bf`, and at line 52 in cassandra-6.0 at `a02931dea8` and trunk at `45c325a01b` |
| 3 | `SimpleDataSet` is a public class with a public constructor. | `SimpleDataSet.SimpleDataSet`, `src/java/org/apache/cassandra/db/virtual/SimpleDataSet.java:64`, ChronitonDB chronitondb-sandbox at `ffa1bc742d` | The same at line 64 in cassandra-5.0 at `47227d98bf`, cassandra-6.0 at `a02931dea8` and trunk at `45c325a01b` |
| 4 | `system_views.thread_pools` is keyed by a `name` column of type text, under a local partitioner that orders by that text. | `ThreadPoolsTable.ThreadPoolsTable`, `src/java/org/apache/cassandra/db/virtual/ThreadPoolsTable.java:40`, ChronitonDB chronitondb-sandbox at `ffa1bc742d` | The same at line 40 in cassandra-5.0 at `47227d98bf`. In cassandra-6.0 at `a02931dea8` and trunk at `45c325a01b` the class is gone and the table is built in `SystemViewsKeyspace.SystemViewsKeyspace`, line 44. Its key there is not verified |
| 5 | `system_views.caches` names its size columns `capacity_bytes` and `size_bytes`, of type bigint. | `CachesTable.CachesTable`, `src/java/org/apache/cassandra/db/virtual/CachesTable.java:39`, ChronitonDB chronitondb-sandbox at `ffa1bc742d` | The same in cassandra-5.0 at `47227d98bf`, and in cassandra-6.0 at `a02931dea8` and trunk at `45c325a01b`, where the names stand at lines 33 and 34 |
| 6 | A virtual keyspace is kept in two maps of the node's own registry. | `VirtualKeyspaceRegistry.register`, `src/java/org/apache/cassandra/db/virtual/VirtualKeyspaceRegistry.java:41`, ChronitonDB chronitondb-sandbox at `ffa1bc742d` | The same at line 41 in cassandra-5.0 at `47227d98bf`, and at line 42 in cassandra-6.0 at `a02931dea8` and trunk at `45c325a01b` |
| 7 | A read of all rows of a virtual table is executed on the node that receives it, in the calling thread, with no message to another node. | `PartitionRangeReadCommand.VirtualTablePartitionRangeReadCommand.execute`, `src/java/org/apache/cassandra/db/PartitionRangeReadCommand.java:547`, ChronitonDB chronitondb-sandbox at `ffa1bc742d`. A read of one row: `SinglePartitionReadCommand.VirtualTableSinglePartitionReadCommand.execute`, `src/java/org/apache/cassandra/db/SinglePartitionReadCommand.java:1407`, the same tree | The first at line 547 in cassandra-5.0 at `47227d98bf`, and at line 646 in cassandra-6.0 at `a02931dea8` and trunk at `45c325a01b`. The second was not read there |
| 8 | A statement that names a table the node does not have is refused with `table %s does not exist`. A write to a read only virtual table is refused with `Modification is not supported by table`, and a truncation with `Truncation is not supported by table`. | `Schema.validateTable`, `src/java/org/apache/cassandra/schema/Schema.java:429`, the text at line 440. `AbstractVirtualTable.apply`, `src/java/org/apache/cassandra/db/virtual/AbstractVirtualTable.java:126`, and `AbstractVirtualTable.truncate`, line 132. All ChronitonDB chronitondb-sandbox at `ffa1bc742d` | `Schema.validateTable` is the same at line 429 in cassandra-5.0 at `47227d98bf`. In cassandra-6.0 at `a02931dea8` and trunk at `45c325a01b` the text is not in `Schema.java`, and where it stands is not verified. The two refusals of `AbstractVirtualTable` were not read there |
| 9 | A read needs no grant only on the resources of `READABLE_SYSTEM_RESOURCES`, which holds the tables of `system_virtual_schema` and no table of `system_views`. | `ClientState.ensurePermission`, `src/java/org/apache/cassandra/service/ClientState.java:451`, the check at line 463. `ClientState.READABLE_SYSTEM_RESOURCES`, built at lines 74 to 93. ChronitonDB chronitondb-sandbox at `ffa1bc742d` | The same lines in cassandra-5.0 at `47227d98bf`. In cassandra-6.0 at `a02931dea8` and trunk at `45c325a01b` the check stands at line 498 and the set is built up to line 100 |
| 10 | A `GRANT` or a `REVOKE` on a resource that does not exist is refused with `Resource %s doesn't exist`. A table resource exists when the schema has the table. A resource name is parsed without looking the table up. | `PermissionsManagementStatement.validate`, `src/java/org/apache/cassandra/cql3/statements/PermissionsManagementStatement.java:57`. `DataResource.exists`, `src/java/org/apache/cassandra/auth/DataResource.java:245`. `DataResource.fromName`, line 140. All ChronitonDB chronitondb-sandbox at `ffa1bc742d` | The same lines in cassandra-5.0 at `47227d98bf`. In cassandra-6.0 at `a02931dea8` and trunk at `45c325a01b` at lines 60, 246 and 141 |
| 11 | At startup the node logs, for each memory pool of the JVM, its name, its type and its peak usage. | `CassandraDaemon.logSystemInfo`, `src/java/org/apache/cassandra/service/CassandraDaemon.java:596`, the loop at line 614, ChronitonDB chronitondb-sandbox at `ffa1bc742d` | The same lines in cassandra-5.0 at `47227d98bf`. In cassandra-6.0 at `a02931dea8` and trunk at `45c325a01b` the method stands at line 706 and the loop at line 724 |
| 12 | `nodetool info` prints one line `Heap Memory (MB)` with the used and the maximum heap, and no line for a pool. | `Info.execute`, `src/java/org/apache/cassandra/tools/nodetool/Info.java:48`, the line at 72, ChronitonDB chronitondb-sandbox at `ffa1bc742d` | The line stands at 72 in cassandra-5.0 at `47227d98bf`, and at 68 in cassandra-6.0 at `a02931dea8` and trunk at `45c325a01b` |
| 13 | The metric tables of trunk are built from a list of metric groups, and the list names no group of JVM memory. | Our line and its base have no such keyspace | `CassandraMetricsRegistry.createMetricsKeyspaceTables`, `src/java/org/apache/cassandra/metrics/CassandraMetricsRegistry.java:210`, the list at line 116, Apache Cassandra trunk at `45c325a01b`, and the same in cassandra-6.0 at `a02931dea8` |

These rules apply to every source:

1. Describe and cite behaviour, published designs, papers, public documentation and code under licences compatible with the Apache License 2.0.
2. Code or text under an incompatible licence, for example the Elastic License, SSPL, BUSL or a proprietary licence, MUST NOT be copied. The behaviour of such a system is taken only from its public documentation. Code under a compatible licence MAY be used only with credit. See [conventions.md](../../process/conventions.md#code-from-elsewhere).
3. Contributors working on the project's behalf MUST NOT search for or read patents for design work. Any patent concern goes to the maintainers.

## Glossary

Not applicable: the glossary is required from Challenging size, and this feature is Normal size. Section 3 defines the three terms the requirements use.
