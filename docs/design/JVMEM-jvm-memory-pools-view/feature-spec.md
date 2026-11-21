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
| References | Issue #161. Line `chronitondb-sandbox`. Apache base commit `76550e931481e965ae3283d8cf4a59c320d74c55` (Apache Cassandra `cassandra-5.0`). Decision records [DEC-JVMEM-0001](decisions/DEC-JVMEM-0001-jvm-memory-pools-view-has-no-switch.md), [DEC-JVMEM-0002](decisions/DEC-JVMEM-0002-a-pool-with-no-maximum-shows-minus-one.md), [DEC-JVMEM-0003](decisions/DEC-JVMEM-0003-jvm-memory-pools-view-stays-at-normal-risk.md), [DEC-JVMEM-0004](decisions/DEC-JVMEM-0004-view-is-named-jvm-memory-pools.md), [DEC-JVMEM-0005](decisions/DEC-JVMEM-0005-type-column-shows-heap-and-non-heap-as-jmx-does.md), [DEC-JVMEM-0006](decisions/DEC-JVMEM-0006-a-grant-left-on-the-view-is-documented.md), [DEC-JVMEM-0007](decisions/DEC-JVMEM-0007-a-pool-with-no-reported-usage-shows-null-sizes.md), [DEC-JVMEM-0008](decisions/DEC-JVMEM-0008-each-page-of-a-read-is-read-afresh.md), [DEC-JVMEM-0009](decisions/DEC-JVMEM-0009-an-error-for-one-pool-fails-every-read.md), [DEC-JVMEM-0010](decisions/DEC-JVMEM-0010-the-view-catches-nothing-a-call-to-the-jvm-throws.md) and [DEC-JVMEM-0011](decisions/DEC-JVMEM-0011-a-read-of-the-view-is-no-request-path.md). |
| Areas | observability |
| Risk | Normal: by the label the worst Bug Category is Availability, a response crash, which is a read of the view that fails. The floor of [classification.md](../../process/classification.md#the-floor), which keeps a change to a public interface at Normal risk at least, applies, because the feature adds a virtual table. The class table of that page rates two faults of this feature Critical: a wrong value in the view, and a node that does not start because of the view. Problems 1 and 2 of section 4 name them with their tests. Decision record [DEC-JVMEM-0003](decisions/DEC-JVMEM-0003-jvm-memory-pools-view-stays-at-normal-risk.md) keeps the feature at Normal risk with both faults named. |
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

A code fact is cited by its number, as fact 1 to fact 23. Section 12 holds each one with its symbol, file, line and the tree it was read in.

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
3. **Apache Cassandra.** The view is a virtual table like the other tables of `system_views`. Apache Cassandra's own code parses the statement, checks the permission (fact 9), filters, limits and pages the rows and lists the view in `system_virtual_schema`. The feature changes none of that code.
4. **Not touched.** The schema tables, the data files, the commit log, gossip, the messages between nodes, the settings, the permission code, nodetool and JMX.

### 2.2 Building blocks

**The view class.** A class of the project in `src/java/org/chronitondb/virtual/`. It extends `AbstractVirtualTable` of Apache Cassandra, whose constructor a class of another package can call (fact 2), and fills a `SimpleDataSet` at each read (fact 3). It defines this table:

| Column | CQL type | Kind | What it holds |
|---|---|---|---|
| `name` | `text` | partition key | The name of the pool as the JVM reports it, unchanged. For example `G1 Old Gen`, `Metaspace` or `CodeHeap 'non-nmethods'`. |
| `type` | `text` | regular | `HEAP` for a pool of heap memory, `NON_HEAP` for any other pool. These are the names of the two values of `java.lang.management.MemoryType`, and the text JMX shows for the pool's `Type` attribute ([DEC-JVMEM-0005](decisions/DEC-JVMEM-0005-type-column-shows-heap-and-non-heap-as-jmx-does.md)). |
| `used_bytes` | `bigint` | regular | The memory the pool uses at the read, in bytes. |
| `committed_bytes` | `bigint` | regular | The memory that is guaranteed to be available to the JVM for the pool, in bytes. It is never less than the used size, and it can grow or shrink over time. |
| `max_bytes` | `bigint` | regular | The most memory the JVM can use for the pool, in bytes, or -1 where the JVM defines no maximum ([DEC-JVMEM-0002](decisions/DEC-JVMEM-0002-a-pool-with-no-maximum-shows-minus-one.md)). Where it is defined it can change over time. It is no promise that the memory can be had: the JVM can fail to get memory above the committed size while the used size is still below the maximum. |

The meanings of the three sizes are those the Java SE documentation of `java.lang.management.MemoryUsage` gives for used, committed and max, and the documentation of the view states them so.

The table is `system_views.jvm_memory_pools`, and its name and the names of its columns are those of [DEC-JVMEM-0004](decisions/DEC-JVMEM-0004-view-is-named-jvm-memory-pools.md). The size columns end in `_bytes` as the size columns of `system_views.caches` do (fact 5). The table is keyed by the name of the pool under the partitioner `system_views.thread_pools` has (fact 4). So its rows come back in the byte order of the UTF-8 text of the name, as the rows of that table do. In that order an upper case letter comes before every lower case letter.

For one row the view calls `MemoryPoolMXBean.getUsage` once and takes the three sizes from the one `MemoryUsage` object it returns. So the three sizes of a row belong to one moment. The rows of one read are taken one after the other, so two rows of one read can be a few instructions apart.

The JVM can list a memory pool whose usage it does not report. `MemoryPoolMXBean.getUsage` then returns null, and the Java SE documentation calls such a pool not valid. Its row holds the name and the type of the pool and null in the three sizes ([DEC-JVMEM-0007](decisions/DEC-JVMEM-0007-a-pool-with-no-reported-usage-shows-null-sizes.md)). So null in `max_bytes` means that the JVM reports no usage for the pool, and -1 means that it reports a usage with no maximum defined.

One read is one run of the code that builds the rows of the view. Every read builds the row of every memory pool that the JVM lists then, also a read of one pool by its name, and Apache Cassandra's code takes from those rows the ones the statement asks for (fact 20, [DEC-JVMEM-0009](decisions/DEC-JVMEM-0009-an-error-for-one-pool-fails-every-read.md)). Apache Cassandra answers one statement from one read or from more, and the view is read afresh at every read, whatever makes a statement take more than one ([DEC-JVMEM-0008](decisions/DEC-JVMEM-0008-each-page-of-a-read-is-read-afresh.md)). Three cases of more than one read were read in the code. They are the cases that were read, and this spec does not give them as the whole list:

1. A statement whose rows a client fetches over more than one page is at least one read for each page. Each page starts after the last name that the page before returned (fact 15).
2. A statement that aggregates, such as `SELECT sum(used_bytes)`, and that the client sends with a page size is fetched in pages of that size inside the node. Each of those pages is at least one read, and the client gets the value that the node computed over all of them (fact 17). A page that comes back full does not end a statement, so such a statement is more than one read where the page size is not above the number of pools (fact 18).
3. A statement that names more than one pool, such as one with `WHERE name IN ('G1 Eden Space', 'G1 Old Gen')`, is at least one read for each name (fact 20). Where such a statement is also fetched in pages or aggregates, cases 1 and 2 hold for it too, and Apache Cassandra fills one page from the reads of one name after the other, so one page of it can hold rows of more than one read (fact 20).

For a statement that is answered from more than one read:

1. Its rows can hold values of different moments, as far apart as its reads are. A sum over them mixes those moments, whether a client or the node adds them up.
2. While the JVM does not change its list of pools, the reads of a statement of case 1 or case 2 together give every pool that the statement asks for once. If the JVM changes its list between two reads, a pool can be missing from the rows of the statement, or from the value the node computes over them.

One statement was read in the code as exactly one read: `SELECT * FROM system_views.jvm_memory_pools`, sent with no page size or with a page size above the number of pools (fact 7, fact 18, fact 22). For a statement that is neither that one nor one of the three cases, this spec does not say how many reads answer it.

The view keeps nothing from one read to the next.

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

1. **Isolation.** The feature adds no work to a path that Apache Cassandra already has, so it needs no pool, limit or budget of its own ([PRINCIPLE-051](../../process/principles.md#principle-051)). A statement on the view is a new kind of statement. Each read costs one call to the JVM for the list of pools and a fixed number of calls for each pool. The number of pools is the JVM's, 8 in the example of section 2.2, and does not grow with data or traffic. A statement costs that once for each of its reads (section 2.2). The reads of a statement that names pools with `IN` grow with the number of names the client lists. Apache Cassandra bounds that number for an ordinary role by its guardrail on the partition keys of one `SELECT`, where an operator sets it, and the feature adds no bound of its own (fact 21). A read runs where a read of every table of `system_views` runs.
2. **Performance.** The feature touches no request path of Apache Cassandra and no background path that competes with requests, so no benchmark is planned ([PRINCIPLE-050](../../process/principles.md#principle-050)). A read of the view is no request path in the feature's class either, so the Touches row names none: the cost of a read grows neither with data nor with traffic, as item 1 says, and the reads of a statement with `IN` grow only with the names that the statement lists ([DEC-JVMEM-0011](decisions/DEC-JVMEM-0011-a-read-of-the-view-is-no-request-path.md)).
3. **Observability.** The feature adds no setting, no pool, no limit, no background work and no fallback, so it adds no metric, no trace line and no log line of its own ([PRINCIPLE-033](../../process/principles.md#principle-033)). An operator sees the view work by reading it, and sees it fail by the error of the read and, where a call to the JVM throws, by what the node logs, as item 4 says.
4. **Errors.** A memory pool whose usage the JVM does not report is no error: its row holds null sizes, as section 2.2 says. The view catches nothing that a call it makes to the JVM throws while a read builds its rows, whether the call is the one for the list of pools or a call to the bean of one pool, and whether an exception or an error of the JVM is thrown ([DEC-JVMEM-0010](decisions/DEC-JVMEM-0010-the-view-catches-nothing-a-call-to-the-jvm-throws.md), FREQ-JVMEM-018). So such a read fails, whichever pools the statement names, because every read builds the row of every pool ([DEC-JVMEM-0009](decisions/DEC-JVMEM-0009-an-error-for-one-pool-fails-every-read.md)). What was thrown goes to Apache Cassandra's own handling, which the feature does not change. The view keeps nothing from a failed read, since it keeps no state. What that handling answers and logs was read in the code for a statement that a client sends (fact 23), and the three parts below state it.
   - **Answered.** An exception is answered with a server error whose message is the class name and the message of the exception as Apache Cassandra's handler got it, in the form that Java's `toString` gives. An error of the JVM that is no out of memory error is answered with a server error of the same form. An out of memory error is not answered by that handling. Apache Cassandra throws an error on for the JVM to handle, as on any other request, and what the JVM then does was not read. Where the message of the out of memory error is `Java heap space` or `GC Overhead limit exceeded`, the error thrown on is that error. For any other message Apache Cassandra fills the heap until an allocation of its own throws an out of memory error, and that new error is thrown on in its place. One case differs. Where the system property `cassandra.printHeapHistogramOnOutOfMemoryError` is on, an error is thrown on only for the first out of memory error that Apache Cassandra's handling meets on the node. A later one is answered with a server error, as another error of the JVM is.
   - **Logged.** The node logs an exception at ERROR, each time with its stack trace: in two log entries for a statement that the client sends as text, as `cqlsh` does, and in one for a prepared statement. It logs an error of the JVM that is no out of memory error once with its stack trace, at ERROR, or at DEBUG where the address of the client lies in a subnet that the setting `client_error_reporting_exclusions` lists. It logs an out of memory error at ERROR, with its stack trace, before it throws an error on. Where the message of the out of memory error is neither of the two texts that the Answered part names, it logs that error in a second ERROR entry, with its stack trace, before it fills the heap. Where the system property `cassandra.printHeapHistogramOnOutOfMemoryError` is on, Apache Cassandra first logs a heap histogram for the first out of memory error that its handling meets on the node: an INFO line, then the output of the `jcmd` command `GC.class_histogram` in one INFO entry. Where it cannot find its process id, or the attempt throws, it logs an ERROR entry. A later out of memory error gets none of the entries of an out of memory error. It is logged as another error of the JVM is. The ERROR entries are those of an unexpected error of the server, which [PRINCIPLE-036](../../process/principles.md#principle-036) lets a node log for each failing request. An exception is unexpected because no case is known in which a JVM makes a call of the view throw one, and none was looked for. An out of memory error is unexpected for another reason: any call that needs memory can throw one while the heap is full, and that is a fault of the node and none of the failures a request is expected to end in, such as a bad statement, a timeout or a refused permission. Apache Cassandra writes the entries of such an error at ERROR, and the feature writes none. What bounds the entries is the same for an exception and for an error of the JVM: each is logged for a request of a client that fails, so their rate is the rate at which clients send such requests while the fault lasts, and the feature adds no other bound. With the system property `cassandra.printHeapHistogramOnOutOfMemoryError` on, that holds for the ERROR entry of each later out of memory error too, and the heap histogram is logged once on a node. Each ERROR entry holds what was thrown, with its stack trace, and no user data.
   - **Not covered.** What Apache Cassandra answers and logs was read in three trees, which this item and the documentation name by commit: ChronitonDB chronitondb-sandbox at `ffa1bc742d`, its base, which is Apache Cassandra cassandra-5.0 at `76550e9314`, and Apache Cassandra cassandra-5.0 at `47227d98bf` (fact 23). None of the three commits is a release, and no test of the feature covers that code (section 4.1). So this item says what Apache Cassandra answers and logs for the code of those three commits, and for no other code ([DEC-JVMEM-0010](decisions/DEC-JVMEM-0010-the-view-catches-nothing-a-call-to-the-jvm-throws.md)). A release of the line is other code, since it is cut from another commit, and so is another release of Apache Cassandra. An import from Apache Cassandra can change that code, and this item and the documentation then still say only what was read. Fact 23 also gives the lines of the same code in `cassandra-6.0` and trunk, which are a later major version than the line's, and this item makes no statement for them. What a statement answered from more than one read returns when one of its reads fails was not read in the code (section 11).
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

The feature is not held back either, and that is an exception to two principles. [PRINCIPLE-003](../../process/principles.md#principle-003) and the edge of [PRINCIPLE-089](../../process/principles.md#principle-089) let only a feature that is held back until every node has it add a definition to a keyspace that Apache Cassandra defines in code, and `system_views` is such a keyspace. Decision record DEC-JVMEM-0001 states the exception for this view only, with its reason. The design record of the item names both principles in its `Exceptions` row, where [principles.md](../../process/principles.md#how-to-read-and-cite-a-principle) has an exception recorded.

1. **Default on each line.** The view is present on every node of the line `chronitondb-sandbox` that runs a release with the feature. The delivery plan proposes the line, and this spec names no other.
2. **A feature finished after its line's first release.** The view is present on that line too. It does no work without being asked and adds nothing nodes share, so the edge of [PRINCIPLE-018](../../process/principles.md#principle-018) does not turn it off.
3. **Built in one milestone.** A feature with no switch merges no item that makes unfinished work reachable ([PRINCIPLE-020](../../process/principles.md#principle-020)). So the item that adds the hook delivers the view whole, with its tests and its documentation. Section 11 has one milestone.

## 3. Feature requirements

"The node" is the node that executes the statement. "The view" is the table `system_views.jvm_memory_pools`. "A memory pool" is one element of the list that `ManagementFactory.getMemoryPoolMXBeans` returns in the node's JVM. "A read" is one run of the code that builds the rows of the view. Apache Cassandra answers one statement from one read or from more, as section 2.2 says.

FREQ-JVMEM-001 (ubiquitous): The node MUST hold the view, with the columns and types of section 2.2, from its startup and whatever its configuration. Source: stakeholder need, decision records [DEC-JVMEM-0001](decisions/DEC-JVMEM-0001-jvm-memory-pools-view-has-no-switch.md) and [DEC-JVMEM-0004](decisions/DEC-JVMEM-0004-view-is-named-jvm-memory-pools.md).

FREQ-JVMEM-002 (event driven): When a read runs, the view MUST hold for that read exactly one row for each memory pool that its JVM lists during the read, whichever rows the statement asks for, unless a call to the JVM throws during the read (FREQ-JVMEM-018). Source: stakeholder need, decision record [DEC-JVMEM-0009](decisions/DEC-JVMEM-0009-an-error-for-one-pool-fails-every-read.md).

FREQ-JVMEM-003 (ubiquitous): The `name` column MUST hold the name of the memory pool as `MemoryPoolMXBean.getName` returns it, unchanged. Source: stakeholder need.

FREQ-JVMEM-004 (ubiquitous): The `type` column MUST hold `HEAP` for a memory pool whose `MemoryPoolMXBean.getType` is heap memory, and `NON_HEAP` for every other memory pool. Source: stakeholder need, decision record [DEC-JVMEM-0005](decisions/DEC-JVMEM-0005-type-column-shows-heap-and-non-heap-as-jmx-does.md).

FREQ-JVMEM-005 (event driven): When `MemoryPoolMXBean.getUsage` returns a `MemoryUsage` object for a memory pool during the read, the `used_bytes`, `committed_bytes` and `max_bytes` columns of the row of that memory pool MUST hold the used, the committed and the maximum size in bytes of that one object. Source: stakeholder need.

FREQ-JVMEM-006 (unwanted behaviour): If the `MemoryUsage` object that `MemoryPoolMXBean.getUsage` returns for a memory pool defines no maximum, then the `max_bytes` column of the row of that memory pool MUST hold -1. Source: decision record [DEC-JVMEM-0002](decisions/DEC-JVMEM-0002-a-pool-with-no-maximum-shows-minus-one.md).

FREQ-JVMEM-007 (ubiquitous): The node MUST take the values of every row from its own running JVM during the read, with no message to another node and no value kept from an earlier read. Source: stakeholder need, decision record [DEC-JVMEM-0008](decisions/DEC-JVMEM-0008-each-page-of-a-read-is-read-afresh.md).

FREQ-JVMEM-008 (state driven): While no statement reads the view, the feature MUST do no work, which means that it runs no thread and no scheduled task and keeps no value of a memory pool. Source: stakeholder need.

FREQ-JVMEM-009 (ubiquitous): The node MUST apply to a statement on the view the permission check that Apache Cassandra applies to a statement on a table of `system_views` (fact 9), with no check of the feature's own. Source: stakeholder need, [PRINCIPLE-045](../../process/principles.md#principle-045).

FREQ-JVMEM-010 (event driven): When a statement writes to the view or truncates it, the node MUST refuse the statement with the error Apache Cassandra returns for that kind of statement on a read only virtual table (fact 8). Source: stakeholder need.

FREQ-JVMEM-011 (ubiquitous): The feature MUST NOT change the definition or the rows of another table, a JMX MBean, a metric or the output of a nodetool command, apart from a surface of Apache Cassandra that lists what the node holds, such as the tables of `system_virtual_schema` and the `DESCRIBE` statements, which show the view as they show every virtual table. Source: stakeholder need, [PRINCIPLE-001](../../process/principles.md#principle-001), [PRINCIPLE-002](../../process/principles.md#principle-002).

FREQ-JVMEM-012 (ubiquitous): The documentation MUST name the view and each of its columns, and give for each column its type and its meaning, the two values of `type`, the meaning of -1 in `max_bytes` and the meaning of null in the three size columns. Source: stakeholder need, [PRINCIPLE-077](../../process/principles.md#principle-077), decision record [DEC-JVMEM-0007](decisions/DEC-JVMEM-0007-a-pool-with-no-reported-usage-shows-null-sizes.md).

FREQ-JVMEM-013 (ubiquitous): The documentation MUST say what a read of the view answers on a node that does not have the view, and name the step of section 7.4 for moving back. Source: [PRINCIPLE-062](../../process/principles.md#principle-062), [PRINCIPLE-003](../../process/principles.md#principle-003).

FREQ-JVMEM-014 (unwanted behaviour): If `MemoryPoolMXBean.getUsage` returns null for a memory pool during the read, then the row of that memory pool MUST hold null in `used_bytes`, `committed_bytes` and `max_bytes`. Source: decision record [DEC-JVMEM-0007](decisions/DEC-JVMEM-0007-a-pool-with-no-reported-usage-shows-null-sizes.md).

FREQ-JVMEM-015 (ubiquitous): The documentation MUST say that one statement can be answered from more than one read, with the three cases of section 2.2 given as the cases that were read and not as the whole list, the one statement that section gives as exactly one read, and the two consequences that section gives for a statement answered from more than one read. Source: decision record [DEC-JVMEM-0008](decisions/DEC-JVMEM-0008-each-page-of-a-read-is-read-afresh.md).

FREQ-JVMEM-016 (ubiquitous): The documentation MUST say how an operator lists the grants that name the view, that the operator revokes every permission of each, as which role the operator does both, what a grant left behind after moving back does, the three commits for whose code section 7.4 says that, that it says so for no other code, and how it is removed. Source: decision record [DEC-JVMEM-0006](decisions/DEC-JVMEM-0006-a-grant-left-on-the-view-is-documented.md), [PRINCIPLE-003](../../process/principles.md#principle-003).

FREQ-JVMEM-017 (event driven): When a statement grants or revokes a permission on the view by name, the node MUST handle it as Apache Cassandra handles that statement on a table of `system_views` (fact 10), with no check of the feature's own. Source: decision record [DEC-JVMEM-0006](decisions/DEC-JVMEM-0006-a-grant-left-on-the-view-is-documented.md).

FREQ-JVMEM-018 (unwanted behaviour): If a call that the view makes to the JVM throws while a read builds its rows, whether the call for the list of memory pools or a call to the bean of one memory pool, then the view MUST NOT catch what was thrown, whichever rows the statement asks for. Source: decision records [DEC-JVMEM-0009](decisions/DEC-JVMEM-0009-an-error-for-one-pool-fails-every-read.md) and [DEC-JVMEM-0010](decisions/DEC-JVMEM-0010-the-view-catches-nothing-a-call-to-the-jvm-throws.md).

FREQ-JVMEM-019 (ubiquitous): The documentation MUST say that an error the JVM raises for one memory pool fails every read of the view while it lasts, a read of another pool by its name included. Source: decision record [DEC-JVMEM-0009](decisions/DEC-JVMEM-0009-an-error-for-one-pool-fails-every-read.md), [PRINCIPLE-077](../../process/principles.md#principle-077).

FREQ-JVMEM-020 (ubiquitous): The documentation MUST say that the view passes on what a call to the JVM throws, what Apache Cassandra then answers and logs, as item 4 of section 2.5 states it, the three commits for whose code that item says so, and that it says so for no other code. Source: decision record [DEC-JVMEM-0010](decisions/DEC-JVMEM-0010-the-view-catches-nothing-a-call-to-the-jvm-throws.md), [PRINCIPLE-077](../../process/principles.md#principle-077).

## 4. Where problems could occur

Worst case first.

1. **A node does not start.** An operator sees a node that exits during its start. It is every node that runs the release. It comes from the hook: Apache Cassandra builds the tables of `system_views` once, during the start of the node (fact 1), and a view class whose constructor or static initialiser throws stops that step.
2. **The view shows a wrong value.** An operator reads a size that is not what the JVM reports: a wrong unit, two columns swapped, the three sizes of a row taken from two readings, a maximum shown as a size where the JVM defines none, a wrong type, a pool missing or a pool shown twice. The operator may then resize a heap that needs no change, or miss a pool that is full. It comes from the view class. A pool that is missing from the rows of a statement answered from more than one read, because the JVM changed its list of pools between two reads, is no such fault. It is the decided behaviour of problem 10.
3. **A read of the view fails.** An operator sees an error in place of the rows. It comes from a fault of the view class, for example a pool whose usage the JVM does not report and that the view does not show as FREQ-JVMEM-014 says. Other statements are not affected. A read that fails because the JVM raises an error for a pool is no such fault. It is the decided behaviour of FREQ-JVMEM-018: while the JVM raises the error, every read of the view fails, a read of another pool by its name too. For an exception the client gets a server error and the node logs the exception at ERROR for each such request, as item 4 of section 2.5 says for a statement that a client sends and for the code of the three commits it names, so a tool that polls the view adds ERROR lines to the log while the fault lasts.
4. **Another table of `system_views` is missing or fails.** An operator or a monitoring tool sees a table such as `system_views.settings` missing, or a read of it failing. It comes from a wrong edit of the list in `SystemViewsKeyspace`, or from a later import in which Apache Cassandra adds a table of the same name.
5. **The values reach a role that should not see them, or a client changes the view.** A role with no grant reads the rows, or a write to the view is accepted. It comes from a view class that is not built on Apache Cassandra's read only virtual table, or that is added to a keyspace every role may read.
6. **A read is refused during a rolling upgrade.** A monitoring tool whose driver sends the read to a node that does not have the view yet sees `table jvm_memory_pools does not exist` (fact 8). The refusal is Apache Cassandra's own, for any table a node does not have. It ends when every node runs a release with the view.
7. **A grant on the view cannot be revoked after moving back.** An operator gave a role a permission on the view by name, then moved the cluster back. A node without the view refuses a `REVOKE` that names it (fact 10), so the row stays in the auth tables. Section 7.4 says what the row does, for the code of the three commits it names. For every other tree, an earlier release of the line and another release of Apache Cassandra included, an operator has the step and no statement on a row left behind. If Apache Cassandra did not handle the row as that section says, a listing of permissions or the start of a node could fail after moving back.
8. **The documentation names the view or a column wrongly.** An operator copies a statement from the page and it fails.
9. **The view does work when nobody reads it, or a read costs more than section 2.5 says.** An operator sees a thread, a task or memory of the feature on a node where nobody reads the view, or request threads busy with reads of the view.
10. **An operator takes a statement answered from more than one read for one moment.** An operator or a script fetches the view in pages, asks the node for a sum with a page size that is not above the number of pools, or names several pools with `IN`, and so adds up sizes of rows from more than one read, which belong to different moments ([DEC-JVMEM-0008](decisions/DEC-JVMEM-0008-each-page-of-a-read-is-read-afresh.md)). The sum is off by what the JVM did between the reads. If the JVM changed its list of pools meanwhile, a pool can be missing from the rows.

### 4.1 Test plan

No scenario module exists on this line. Each requirement is proven by a unit test or an in-JVM distributed test, and each item's design record names them and says how each detects a breach.

1. Problem 1: every test that starts a node fails when the view stops the start. A unit test of the feature starts a test node with the default configuration and reads the view (FREQ-JVMEM-001), and the validation item starts a cluster in an in-JVM distributed test.
2. Problem 2: a unit test reads the view through CQL and compares it with the memory pools the test reads from the JVM in the same process. The set of names and the type and maximum of each pool do not move while the test runs, so they are compared exactly (FREQ-JVMEM-002, FREQ-JVMEM-003, FREQ-JVMEM-004, FREQ-JVMEM-006). A unit test builds a row from a `MemoryUsage` object of its own and expects its three sizes in the three columns, and -1 for an undefined maximum (FREQ-JVMEM-005, FREQ-JVMEM-006). A unit test builds the row of a memory pool whose usage is null and expects the name, the type and null in the three sizes (FREQ-JVMEM-014). A test reads the view with a page size below the number of pools, on a JVM whose list of pools does not change during the test, and expects every pool once over the pages (FREQ-JVMEM-002, FREQ-JVMEM-007). The tests run on each JDK the line's build supports, since the pools differ from one JDK to another.
3. Problem 3: the unit tests of problem 2 read every row, each row by its name, and two rows by their names with `IN`, and expect no error. A unit test gives the view a memory pool whose `getUsage` throws an exception, reads another pool by its name and expects the read to fail with that exception, which the view did not catch. A unit test makes the call for the list of pools throw an exception, reads one pool by its name and expects the read to fail with that exception (FREQ-JVMEM-018). What Apache Cassandra answers and logs for that exception is its own code, which the feature does not touch, so no test of the feature covers it. The documentation test of problem 6 checks that the page says that such an error fails every read of the view (FREQ-JVMEM-019), and that the view passes on what a call throws, with what Apache Cassandra then answers and logs, the three commits for whose code it says that, and that it says so for no other code (FREQ-JVMEM-020). A test reads the view twice and expects the second answer to hold values taken at the second read (FREQ-JVMEM-007).
4. Problem 4: a test reads the names of the tables of `system_views` from `system_virtual_schema.tables` and expects every table of Apache Cassandra and the view, each once, and reads each table of Apache Cassandra that it can read on a test node (FREQ-JVMEM-011). An import that brings a table of the same name conflicts in the hook file, and the maintainers decide it before the import merges.
5. Problem 5: a test with authentication and authorization on reads the view as a superuser, as a role granted `SELECT` on the view, as a role granted `SELECT` on the keyspace `system_views`, and as a role with no grant, and expects the last to be refused (FREQ-JVMEM-009). A test sends an `INSERT`, an `UPDATE`, a `DELETE` and a `TRUNCATE` on the view and expects Apache Cassandra's refusal (FREQ-JVMEM-010).
6. Problem 6: no test of the feature covers it, because the answer of a node without the view is code of Apache Cassandra that the feature does not touch, and no test on this line starts a node of an earlier release. It is watched by the documentation, which states it (FREQ-JVMEM-013), and a documentation test checks that the page holds the statement.
7. Problem 7: on a node that has the view, a test grants `SELECT` and `AUTHORIZE` on the view by name to a role, lists them with the statement of section 7.4, revokes them with `REVOKE ALL PERMISSIONS` and expects the listing to hold no row of the role afterwards (FREQ-JVMEM-017). The refusal on a node without the view is not tested, for the reason of problem 6. A test writes into the auth tables of a test node a grant row that names a table of `system_views` the node does not have, and runs with the warm-up of the auth caches turned on. It expects each of the four places of section 7.4 to do what that section says: a statement of the role on another table passes its permission check, `LIST ALL PERMISSIONS` and `LIST ALL PERMISSIONS OF <role>` list the row, the warm-up of the permissions cache passes, and `DROP ROLE` removes the row ([DEC-JVMEM-0006](decisions/DEC-JVMEM-0006-a-grant-left-on-the-view-is-documented.md)). The documentation test of problem 6 checks that the page names the step and says how to list the grants, that every permission is revoked, as which role the operator does both, what a grant left behind does, the three commits for whose code it says that, that it says so for no other code, and how it is removed (FREQ-JVMEM-013, FREQ-JVMEM-016).
8. Problem 8: a documentation test reads the name of the view and of each column from the page and expects each in `system_virtual_schema.columns` of a test node, and the other way round (FREQ-JVMEM-012).
9. Problem 9: a test starts a test node, reads no row of the view and expects no thread and no scheduled task of the feature. After a read it expects that the feature holds no value of a memory pool (FREQ-JVMEM-008). The cost of a read is not benchmarked, for the reason of section 2.5. It is watched by the review of the view class against that section.
10. Problem 10: the paged test of problem 2 shows that a paged read works. That two reads hold two moments, and that a pool can be missing when the JVM changes its list between them, is the decided behaviour, so no test forbids it. It is watched by the documentation, which states both (FREQ-JVMEM-015), and the documentation test of problem 6 checks that the page holds the statements, gives the three cases as the cases that were read, and names the one statement of exactly one read.

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

1. Before the last node that has the view moves back, an operator lists the grants that name the view and revokes every permission of each. The operator sends both statements as a superuser, to a node that has the view. A node without it refuses the listing (the second of the four places below) and the `REVOKE` (fact 10). `LIST ALL PERMISSIONS ON system_views.jvm_memory_pools NORECURSIVE` lists the grants of every role, and Apache Cassandra accepts it only from a superuser or from a role that has `DESCRIBE` on all roles (fact 16). A grant on the view can hold any permission of a table, such as `SELECT` or `AUTHORIZE`, so the operator sends `REVOKE ALL PERMISSIONS ON system_views.jvm_memory_pools FROM <role>` for each role listed. Apache Cassandra accepts a `REVOKE` only from a role that has `AUTHORIZE` and every permission the statement revokes, and a superuser has them all (fact 19). Once no node has the view, no node accepts a `REVOKE` that names it (fact 10). A grant on the keyspace `system_views` or on all keyspaces names no table of the feature and needs no step.
2. Nothing else is removed: the feature leaves no file, no schema row and no setting.

The feature changes no permission code, so nothing refuses a grant on the view and nothing removes one ([DEC-JVMEM-0006](decisions/DEC-JVMEM-0006-a-grant-left-on-the-view-is-documented.md)). A grant that the operator did not revoke is left behind, and so is one given on a node that still has the view after the operator revoked the others.

A grant row that is left behind names a table the node does not have. Four places where Apache Cassandra reads grant rows were read in the code, and none of them looks up the table that a row names (fact 14):

1. A permission check reads the row of the role for the resource the statement names. No statement on a node without the view can name the view, so the row is never read there.
2. `LIST ALL PERMISSIONS` and `LIST ALL PERMISSIONS OF <role>` list the row. A `LIST ALL PERMISSIONS ON system_views.jvm_memory_pools` is refused on a node without the view. The role may not list the permissions of every role (fact 16), or the statement names a table the node does not have (fact 14).
3. The warm-up of the permissions cache at the start of a node, which runs only where the setting `auth_cache_warming_enabled` is on, parses the name of the row and goes on.
4. `DROP ROLE` removes every grant row of the role, this one with them.

So a row left behind gives its role nothing on a node without the view, where `LIST ALL PERMISSIONS` still shows it. It gives its role its permissions on the view again when a node gets the view back. It is removed by `DROP ROLE` of its role, or by a `REVOKE` on a node that has the view.

The four places were read in three trees, which this section and the documentation name by commit: ChronitonDB chronitondb-sandbox at `ffa1bc742d`, its base, which is Apache Cassandra cassandra-5.0 at `76550e9314`, and Apache Cassandra cassandra-5.0 at `47227d98bf` (fact 14). None of the three commits is a release. The line changes none of the files of fact 14 against its base, and the test of problem 7 runs on the line. So this section says what a row left behind does for the code of those three commits, and for no other code ([DEC-JVMEM-0006](decisions/DEC-JVMEM-0006-a-grant-left-on-the-view-is-documented.md)). An earlier release of the line is other code, since it is cut from another commit, and so is another release of Apache Cassandra. An operator who moves back to either has the step of item 1 and no statement on a row left behind. Fact 14 also gives the lines of the same code in `cassandra-6.0` and trunk. Those are a later major version than the line's, no cluster of the line moves back to them, and this section makes no statement for them. The step of item 1 is done on nodes that have the view, so it does not depend on the release the cluster moves back to. Each release of the line states which Apache Cassandra releases a cluster on it can move back to ([PRINCIPLE-003](../../process/principles.md#principle-003)).

No schema object uses the feature, so nothing is removed when an object stops using it.

### 7.5 Runbook entries

The line has no runbook pages yet. The reference page of the view carries the entries: what a read answers on a node without the view and the step of section 7.4 (FREQ-JVMEM-013), and every statement on grants that FREQ-JVMEM-016 names. The same page carries the statements on failed reads that FREQ-JVMEM-019 and FREQ-JVMEM-020 name.

## 8. Dependencies

No new dependency. The feature uses `java.lang.management` of the JDK and classes Apache Cassandra already has.

## 9. Risks

| Id | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| R1 | Apache Cassandra later adds a table of the same name to `system_views`. | Unlikely: no Apache Cassandra branch read for this spec has a view of JVM memory (fact 1). | The import conflicts in the hook file, and one of the two names has to give way. | The maintainers decide the conflict before the import merges ([PRINCIPLE-074](../../process/principles.md#principle-074), [PRINCIPLE-082](../../process/principles.md#principle-082)). |
| R2 | A JDK or a collector the line supports reports its pools in a way the view was not tested with. | Possible: the pools differ by JDK and collector. | A read fails or shows an unexpected row on such a node. | The view takes names and values as the JVM reports them and depends on no pool by name. The tests run on each JDK the line's build supports. |

## 10. Decisions

1. [DEC-JVMEM-0001. The JVM memory pools view has no switch and is not held back](decisions/DEC-JVMEM-0001-jvm-memory-pools-view-has-no-switch.md): the view is on every node from startup, because nodes share nothing of it, as an exception to PRINCIPLE-003 and the edge of PRINCIPLE-089 for this view only.
2. [DEC-JVMEM-0002. A memory pool with no maximum shows -1 as its maximum](decisions/DEC-JVMEM-0002-a-pool-with-no-maximum-shows-minus-one.md): the number JMX shows, not null.
3. [DEC-JVMEM-0003. The JVM memory pools view stays at Normal risk with two faults named](decisions/DEC-JVMEM-0003-jvm-memory-pools-view-stays-at-normal-risk.md): a wrong value and a node that does not start are named with their tests, and the class stays Normal.
4. [DEC-JVMEM-0004. The view is named jvm_memory_pools and its size columns end in _bytes](decisions/DEC-JVMEM-0004-view-is-named-jvm-memory-pools.md): the name says whose pools the view shows, and each size column says that it holds bytes.
5. [DEC-JVMEM-0005. The type column shows HEAP and NON_HEAP, as JMX does](decisions/DEC-JVMEM-0005-type-column-shows-heap-and-non-heap-as-jmx-does.md): the text JMX shows for the same pool, not lower case words and not the display text.
6. [DEC-JVMEM-0006. A grant left on the view after moving back is documented, and permission code is unchanged](decisions/DEC-JVMEM-0006-a-grant-left-on-the-view-is-documented.md): the documentation states the step and what a row left behind does for the code of the three commits that were read, and no grant on the view is refused.
7. [DEC-JVMEM-0007. A memory pool whose usage the JVM does not report shows null in its three sizes](decisions/DEC-JVMEM-0007-a-pool-with-no-reported-usage-shows-null-sizes.md): the pool keeps its row and no read fails.
8. [DEC-JVMEM-0008. The view is read afresh at every read of a statement](decisions/DEC-JVMEM-0008-each-page-of-a-read-is-read-afresh.md): a statement takes more than one read for pages a client fetches, for pages the node fetches for a sum, or for several names, which are the cases that were read and not the whole list, and nothing is kept between reads.
9. [DEC-JVMEM-0009. Every read builds the row of every pool, and a JVM error for one pool fails every read](decisions/DEC-JVMEM-0009-an-error-for-one-pool-fails-every-read.md): a read of one pool by its name fails too while the JVM raises an error for another pool.
10. [DEC-JVMEM-0010. The view catches nothing that a call to the JVM throws](decisions/DEC-JVMEM-0010-the-view-catches-nothing-a-call-to-the-jvm-throws.md): what a call throws goes to Apache Cassandra's own handling, which answers an exception with a server error and logs it at ERROR, and the documentation states that for the code of the three commits that were read.
11. [DEC-JVMEM-0011. A read of the view is no request path in the feature's class](decisions/DEC-JVMEM-0011-a-read-of-the-view-is-no-request-path.md): the cost of a read grows neither with data nor with traffic, so the Touches row names no request path and no benchmark is planned.

## 11. Milestones outline

1. **Milestone 1: the view.** The view class, the hook with its delta entry, the unit tests and the documentation, in one build item, and one validation item with the end to end tests. It makes every requirement of section 3 testable. The feature has no second milestone, for the reason of section 2.8.

- For the design record: which item holds which test of section 4.1, so that the item that adds the hook leaves no unfinished work reachable.
- For the design record: how an import from Apache Cassandra that brings a table of the same name is caught when it gives no text conflict in the hook file.
- For the design record: what the view does if a JVM reports two memory pools under one name.
- For the design record: which test runs hold the two tests that decision record DEC-JVMEM-0003 wants run on every build.
- For the design record: what Apache Cassandra does with a statement answered from more than one read when one of its reads fails, which the feature does not change.
- For the design record: its `Exceptions` row names PRINCIPLE-003 and PRINCIPLE-089, and it states the exception of decision record DEC-JVMEM-0001 with its reason.

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
| 1 | The tables of `system_views` are one fixed list built in a constructor. No table of it is about JVM memory. The file imports `StorageAttachedIndexTables` from another package. The node registers the keyspace, and so builds the list, when it starts. | `SystemViewsKeyspace.SystemViewsKeyspace`, `src/java/org/apache/cassandra/db/virtual/SystemViewsKeyspace.java:30`, import at line 22. `CassandraDaemon.setupVirtualKeyspaces`, `src/java/org/apache/cassandra/service/CassandraDaemon.java:534`, the registration at line 537. Both ChronitonDB chronitondb-sandbox at `ffa1bc742d` | The first at line 30 in cassandra-5.0 at `47227d98bf`, and at line 33 with the import at line 24 in cassandra-6.0 at `a02931dea8` and trunk at `45c325a01b`. The second at lines 534 and 537 in cassandra-5.0 at `47227d98bf`, and at lines 641 and 644 in cassandra-6.0 at `a02931dea8` and trunk at `45c325a01b` |
| 2 | `AbstractVirtualTable` is a public class with a protected constructor. | `AbstractVirtualTable.AbstractVirtualTable`, `src/java/org/apache/cassandra/db/virtual/AbstractVirtualTable.java:50`, ChronitonDB chronitondb-sandbox at `ffa1bc742d` | The same at line 50 in cassandra-5.0 at `47227d98bf`, and at line 52 in cassandra-6.0 at `a02931dea8` and trunk at `45c325a01b` |
| 3 | `SimpleDataSet` is a public class with a public constructor. | `SimpleDataSet.SimpleDataSet`, `src/java/org/apache/cassandra/db/virtual/SimpleDataSet.java:64`, ChronitonDB chronitondb-sandbox at `ffa1bc742d` | The same at line 64 in cassandra-5.0 at `47227d98bf`, cassandra-6.0 at `a02931dea8` and trunk at `45c325a01b` |
| 4 | `system_views.thread_pools` is keyed by a `name` column of type text, under a `LocalPartitioner` over `UTF8Type`, which orders rows by the bytes of the UTF-8 text of the name. | `ThreadPoolsTable.ThreadPoolsTable`, `src/java/org/apache/cassandra/db/virtual/ThreadPoolsTable.java:40`, the partitioner at line 44 and the key column at line 45, ChronitonDB chronitondb-sandbox at `ffa1bc742d` | The same at lines 40, 44 and 45 in cassandra-5.0 at `47227d98bf`. In cassandra-6.0 at `a02931dea8` and trunk at `45c325a01b` the class is gone and the table is built in `SystemViewsKeyspace.SystemViewsKeyspace`, line 44. Its key there is not verified |
| 5 | `system_views.caches` names its size columns `capacity_bytes` and `size_bytes`, of type bigint. | `CachesTable.CAPACITY_BYTES` and `CachesTable.SIZE_BYTES`, `src/java/org/apache/cassandra/db/virtual/CachesTable.java:30` and line 31, with their type in `CachesTable.CachesTable`, line 39, ChronitonDB chronitondb-sandbox at `ffa1bc742d` | The same lines in cassandra-5.0 at `47227d98bf`. In cassandra-6.0 at `a02931dea8` and trunk at `45c325a01b` the names stand at lines 33 and 34 |
| 6 | A virtual keyspace is kept in two maps of the node's own registry. | `VirtualKeyspaceRegistry.register`, `src/java/org/apache/cassandra/db/virtual/VirtualKeyspaceRegistry.java:41`, ChronitonDB chronitondb-sandbox at `ffa1bc742d` | The same at line 41 in cassandra-5.0 at `47227d98bf`, and at line 42 in cassandra-6.0 at `a02931dea8` and trunk at `45c325a01b` |
| 7 | A read of all rows of a virtual table is executed on the node that receives it, in the calling thread, with no message to another node. | `PartitionRangeReadCommand.VirtualTablePartitionRangeReadCommand.execute`, `src/java/org/apache/cassandra/db/PartitionRangeReadCommand.java:547`, ChronitonDB chronitondb-sandbox at `ffa1bc742d`. A read of one row: `SinglePartitionReadCommand.VirtualTableSinglePartitionReadCommand.execute`, `src/java/org/apache/cassandra/db/SinglePartitionReadCommand.java:1407`, the same tree | The first at line 547 in cassandra-5.0 at `47227d98bf`, and at line 646 in cassandra-6.0 at `a02931dea8` and trunk at `45c325a01b`. The second was not read there |
| 8 | A statement that names a table the node does not have is refused with `table %s does not exist`. A write to a read only virtual table is refused with `Modification is not supported by table`, and a truncation with `Truncation is not supported by table`. | `Schema.validateTable`, `src/java/org/apache/cassandra/schema/Schema.java:429`, the text at line 440. `AbstractVirtualTable.apply`, `src/java/org/apache/cassandra/db/virtual/AbstractVirtualTable.java:126`, and `AbstractVirtualTable.truncate`, line 132. All ChronitonDB chronitondb-sandbox at `ffa1bc742d` | `Schema.validateTable` is the same at line 429 in cassandra-5.0 at `47227d98bf`. In cassandra-6.0 at `a02931dea8` and trunk at `45c325a01b` the text is not in `Schema.java`, and where it stands is not verified. The two refusals of `AbstractVirtualTable` were not read there |
| 9 | A read needs no grant only on the resources of `READABLE_SYSTEM_RESOURCES`, which holds the tables of `system_virtual_schema` and no table of `system_views`. | `ClientState.ensurePermission`, `src/java/org/apache/cassandra/service/ClientState.java:451`, the check at line 463. `ClientState.READABLE_SYSTEM_RESOURCES`, built at lines 74 to 93. ChronitonDB chronitondb-sandbox at `ffa1bc742d` | The same lines in cassandra-5.0 at `47227d98bf`. In cassandra-6.0 at `a02931dea8` and trunk at `45c325a01b` the check stands at line 498 and the set is built up to line 100 |
| 10 | A `GRANT` or a `REVOKE` on a resource that does not exist is refused with `Resource %s doesn't exist`. A table resource exists when the schema has the table. A resource name is parsed without looking the table up. | `PermissionsManagementStatement.validate`, `src/java/org/apache/cassandra/cql3/statements/PermissionsManagementStatement.java:57`. `DataResource.exists`, `src/java/org/apache/cassandra/auth/DataResource.java:245`. `DataResource.fromName`, line 140. All ChronitonDB chronitondb-sandbox at `ffa1bc742d` | The same lines in cassandra-5.0 at `47227d98bf`. In cassandra-6.0 at `a02931dea8` and trunk at `45c325a01b` at lines 60, 246 and 141 |
| 11 | At startup the node logs, for each memory pool of the JVM, its name, its type and its peak usage. | `CassandraDaemon.logSystemInfo`, `src/java/org/apache/cassandra/service/CassandraDaemon.java:596`, the loop at line 614, ChronitonDB chronitondb-sandbox at `ffa1bc742d` | The same lines in cassandra-5.0 at `47227d98bf`. In cassandra-6.0 at `a02931dea8` and trunk at `45c325a01b` the method stands at line 706 and the loop at line 724 |
| 12 | `nodetool info` prints one line `Heap Memory (MB)` with the used and the maximum heap, and no line for a pool. | `Info.execute`, `src/java/org/apache/cassandra/tools/nodetool/Info.java:48`, the line at 72, ChronitonDB chronitondb-sandbox at `ffa1bc742d` | The line stands at 72 in cassandra-5.0 at `47227d98bf`, and at 68 in cassandra-6.0 at `a02931dea8` and trunk at `45c325a01b` |
| 13 | The metric tables of trunk are built from a list of metric groups, and the list names no group of JVM memory. | Our line and its base have no such keyspace | `CassandraMetricsRegistry.createMetricsKeyspaceTables`, `src/java/org/apache/cassandra/metrics/CassandraMetricsRegistry.java:210`, the list at line 116, Apache Cassandra trunk at `45c325a01b`, and the same in cassandra-6.0 at `a02931dea8` |
| 14 | Four places that read a grant row were read, and none looks the table up: a permission check reads the row of one role for the resource the statement names, `LIST PERMISSIONS` and the warm-up of the permissions cache parse the resource name of each row with `Resources.fromName`, and `DROP ROLE` deletes the rows of the role by their text. `LIST PERMISSIONS ON` a resource that does not exist is refused with `%s doesn't exist`, once the authorizer has let the role list (fact 16). The warm-up runs at the start of a node only where the setting `auth_cache_warming_enabled` is on, and it is off by default. | `CassandraAuthorizer.addPermissionsForRole`, `src/java/org/apache/cassandra/auth/CassandraAuthorizer.java:255`. `CassandraAuthorizer.listPermissionsForRole`, line 340, the parse at line 355. `CassandraAuthorizer.bulkLoader`, line 458, the parse at line 477. `CassandraAuthorizer.revokeAllFrom`, line 135, called by `DropRoleStatement.execute`, `src/java/org/apache/cassandra/cql3/statements/DropRoleStatement.java:67`, at line 75. `ListPermissionsStatement.execute`, `src/java/org/apache/cassandra/cql3/statements/ListPermissionsStatement.java:86`, the check at line 100. `Config.auth_cache_warming_enabled`, `src/java/org/apache/cassandra/config/Config.java:754`, read in `CassandraDaemon.setup`, `src/java/org/apache/cassandra/service/CassandraDaemon.java:229`, at line 447. All ChronitonDB chronitondb-sandbox at `ffa1bc742d` | The same lines in cassandra-5.0 at `47227d98bf`. In cassandra-6.0 at `a02931dea8` the five methods of `CassandraAuthorizer` and `DropRoleStatement` stand at lines 271, 356 with the parse at 371, 474 with the parse at 493, 151, and 74 with the call at 82, and the check of `ListPermissionsStatement` at line 111. In trunk at `45c325a01b` at lines 273, 358 with the parse at 373, 470 with the parse at 489, 153, and 74 with the call at 82, and the check at line 111. `Config.auth_cache_warming_enabled` stands at `Config.java:876` in cassandra-6.0 and at line 878 in trunk, read in `CassandraDaemon.setup`, line 244, at line 451 in both |
| 15 | A statement fetched in pages runs its read once for each page, from the key after the last one returned. A virtual table builds its rows again each time the read runs. | `AbstractQueryPager.fetchPage`, `src/java/org/apache/cassandra/service/pager/AbstractQueryPager.java:63`, the run of the read at line 76. `PartitionRangeQueryPager.nextPageReadQuery`, `src/java/org/apache/cassandra/service/pager/PartitionRangeQueryPager.java:77`. `AbstractVirtualTable.select`, `src/java/org/apache/cassandra/db/virtual/AbstractVirtualTable.java:91`, the call for the rows at line 93. All ChronitonDB chronitondb-sandbox at `ffa1bc742d` | The same lines in cassandra-5.0 at `47227d98bf`. In cassandra-6.0 at `a02931dea8` and trunk at `45c325a01b` `AbstractQueryPager.fetchPage` stands at line 123 with the run of the read at line 131, `PartitionRangeQueryPager.nextPageReadQuery` at line 89, and `AbstractVirtualTable.select` at line 93 with the call at line 95 |
| 16 | `LIST ALL PERMISSIONS ON <resource>` with `NORECURSIVE` lists the grant rows of that resource alone, for every role when the statement names none. Without `NORECURSIVE` it also lists the rows of the resources above it. A listing that names no role is refused with `You are not authorized to view everyone's permissions` unless a superuser or a role with `DESCRIBE` on all roles sends it. | `ListPermissionsStatement.execute`, `src/java/org/apache/cassandra/cql3/statements/ListPermissionsStatement.java:86`, the choice at line 90. `CassandraAuthorizer.buildListQuery`, `src/java/org/apache/cassandra/auth/CassandraAuthorizer.java:363`. `CassandraAuthorizer.list`, the same file, line 315, the refusal at line 321. All ChronitonDB chronitondb-sandbox at `ffa1bc742d` | The same lines in cassandra-5.0 at `47227d98bf`. In cassandra-6.0 at `a02931dea8` at lines 97 with the choice at 101, 379 and 331. In trunk at `45c325a01b` at lines 97 with the choice at 101, 381 and 333 |
| 17 | A statement that aggregates is fetched through a pager inside the node. Where the statement has a page size, the pager fetches pages of that size, and each of them runs the read again. Where it has none, the pager fetches a statement with no `GROUP BY` with no row limit. `DEFAULT_PAGE_SIZE`, which is 10000, is used only in the limits of a statement with `GROUP BY`. | `SelectStatement.getPager`, `src/java/org/apache/cassandra/cql3/statements/SelectStatement.java:625`, the pager at line 632. `SelectStatement.getDataLimits`, the same file, line 881, the default at line 902 and its one use, in the limits of a statement with `GROUP BY`, at line 911. `SelectStatement.DEFAULT_PAGE_SIZE`, line 114. `AggregationQueryPager.GroupByPartitionIterator.handlePagingOff`, `src/java/org/apache/cassandra/service/pager/AggregationQueryPager.java:193`, and `AggregationQueryPager.GroupByPartitionIterator.fetchSubPage`, line 295. All ChronitonDB chronitondb-sandbox at `ffa1bc742d` | The same lines in cassandra-5.0 at `47227d98bf`. In cassandra-6.0 at `a02931dea8` `SelectStatement.getPager` stands at `SelectStatement.java:755` with the pager at line 773, and `fetchSubPage` at line 337. In trunk at `45c325a01b` at lines 761, 779 and 337. How a statement with no page size is fetched was not read there |
| 18 | A page ends a statement only when it holds fewer rows than the page size. So a page that comes back full is followed by one more read. | `DataLimits.isExhausted`, `src/java/org/apache/cassandra/db/filter/DataLimits.java:139`, the comparison at line 141. `AbstractQueryPager.Pager.onClose`, `src/java/org/apache/cassandra/service/pager/AbstractQueryPager.java:179`, the call at line 200. Both ChronitonDB chronitondb-sandbox at `ffa1bc742d` | The call stands at line 200 in cassandra-5.0 at `47227d98bf`. `DataLimits.java` was not read there. Neither was read in cassandra-6.0 and trunk |
| 19 | A `GRANT` or a `REVOKE` is accepted only from a role that has `AUTHORIZE` on the resource or on one above it, and each permission the statement names. `ALL PERMISSIONS` stands for the permissions that apply to the resource. A superuser has every permission that applies to a resource. | `PermissionsManagementStatement.authorize`, `src/java/org/apache/cassandra/cql3/statements/PermissionsManagementStatement.java:61`, the two checks at lines 67 and 71. The rule `revokePermissionsStatement`, `src/antlr/Parser.g:1092`, the filter at line 1099. `CassandraAuthorizer.authorize`, `src/java/org/apache/cassandra/auth/CassandraAuthorizer.java:75`, the superuser at line 79. All ChronitonDB chronitondb-sandbox at `ffa1bc742d` | `PermissionsManagementStatement.authorize` at the same lines in cassandra-5.0 at `47227d98bf`, and at line 64 with the checks at lines 70 and 74 in cassandra-6.0 at `a02931dea8` and trunk at `45c325a01b`. The other two were not read there |
| 20 | A statement that names more than one partition key makes one read command for each key, and a group of read commands on a virtual table runs each of them. A read of one key asks the virtual table for its rows for that key, and `AbstractVirtualTable` builds all its rows for it unless the table overrides that method. A page of a statement with more than one key is filled from the pager of one key after the other. | `SelectStatement.getSliceCommands`, `src/java/org/apache/cassandra/cql3/statements/SelectStatement.java:713`, the group at line 737. `SinglePartitionReadCommand.VirtualTableGroup.execute`, `src/java/org/apache/cassandra/db/SinglePartitionReadCommand.java:1326`, the run of each command at line 1331. `AbstractVirtualTable.select`, `src/java/org/apache/cassandra/db/virtual/AbstractVirtualTable.java:78`, the call at line 80, and `AbstractVirtualTable.data` with a key, line 72. `MultiPartitionPager.PagersIterator.computeNext`, `src/java/org/apache/cassandra/service/pager/MultiPartitionPager.java:191`, the fetch from the pager of the current key at lines 216 and 217. All ChronitonDB chronitondb-sandbox at `ffa1bc742d` | The same lines in cassandra-5.0 at `47227d98bf`, where `MultiPartitionPager.java` was not read. In cassandra-6.0 at `a02931dea8` `SelectStatement.getSliceCommands` stands at line 871 with the group at line 905, `VirtualTableGroup.execute` at line 1454 with the run at line 1459, `AbstractVirtualTable.select` at line 80 with the call at line 82, and `AbstractVirtualTable.data` with a key at line 74. In trunk at `45c325a01b` `SelectStatement.getSliceCommands` stands at line 877 with the group at line 911, and the others at the lines of cassandra-6.0. `MultiPartitionPager.java` was not read in cassandra-6.0 and trunk |
| 21 | A statement whose `IN` lists partition keys passes the guardrail on the partition keys of one `SELECT`. Its warn and fail thresholds are -1, which is off, by default, and a guardrail is not applied to a superuser. | `SelectStatement.getSliceCommands`, `src/java/org/apache/cassandra/cql3/statements/SelectStatement.java:713`, the check at line 722. `Guardrails.partitionKeysInSelect`, `src/java/org/apache/cassandra/db/guardrails/Guardrails.java:251`. `Config.partition_keys_in_select_warn_threshold` and `Config.partition_keys_in_select_fail_threshold`, `src/java/org/apache/cassandra/config/Config.java:880` and line 881. `Guardrail.enabled`, `src/java/org/apache/cassandra/db/guardrails/Guardrail.java:93`. All ChronitonDB chronitondb-sandbox at `ffa1bc742d` | Not read in cassandra-5.0 at `47227d98bf`, cassandra-6.0 at `a02931dea8` and trunk at `45c325a01b` |
| 22 | A `SELECT` that does not aggregate and has no page size, or whose limit is not above its page size, runs its read once, with no pager. | `SelectStatement.execute`, `src/java/org/apache/cassandra/cql3/statements/SelectStatement.java:280`, the choice at line 338 and the read at line 427, ChronitonDB chronitondb-sandbox at `ffa1bc742d` | The same lines in cassandra-5.0 at `47227d98bf`. In cassandra-6.0 at `a02931dea8` the method stands at line 376 with the choice at line 447, and in trunk at `45c325a01b` at line 382 with the choice at line 453. The choice there calls `canSkipPaging`, which was not read |
| 23 | An exception that escapes a statement a client sends is caught by the message that carries the statement. Unless it is one of the request errors that Apache Cassandra returns to the client as they are, it is answered with a server error, whose message is the `toString` of the exception, and it is logged at ERROR with its stack trace where that error is made. The message of a statement sent as text logs it at ERROR once more before that, and the message of a prepared statement has no log line of its own. An error of the JVM passes that catch and is caught where the request is dispatched. An out of memory error is logged there at ERROR with its stack trace. Where its message is one of the two texts `Java heap space` and `GC Overhead limit exceeded`, it is then thrown on for the JVM to handle. For any other message it is logged in a second ERROR entry with its stack trace, and arrays are allocated in a loop until an allocation throws, so the error of that allocation goes on in its place. With the system property `cassandra.printHeapHistogramOnOutOfMemoryError` on, a flag is set at the first such error and never cleared. At that first error a heap histogram is logged before the first ERROR entry: an INFO line, then the output of `jcmd` with `GC.class_histogram` in one INFO entry, or an ERROR entry where the process id cannot be found or the attempt throws. For a later one the flag makes that step return with no log line and no throw. Another error, and an out of memory error for which that step returned, is answered with the same server error and logged once, by the handler of the client's channel: at DEBUG for a client address inside a subnet that `client_error_reporting_exclusions` lists, and otherwise at ERROR, with its stack trace, in an entry that names the channel. | `QueryMessage.execute`, `src/java/org/apache/cassandra/transport/messages/QueryMessage.java:102`, the catch at line 125 and a log line at 130. `ExecuteMessage.execute`, `src/java/org/apache/cassandra/transport/messages/ExecuteMessage.java:131`, the catch at line 205, which ends at line 209 with no log line. `ErrorMessage.fromException`, `src/java/org/apache/cassandra/transport/messages/ErrorMessage.java:437`, the log line at 473 and the server error at 475. `ServerError.ServerError`, `src/java/org/apache/cassandra/transport/ServerError.java:28`, the `toString` at line 30. `Dispatcher.processRequest`, `src/java/org/apache/cassandra/transport/Dispatcher.java:429`, the catch at line 436, the handler at 443 and the server error at 444. `ExceptionHandlers.getUnexpectedExceptionHandler`, `src/java/org/apache/cassandra/transport/ExceptionHandlers.java:185`, the check of the address at line 188 and the DEBUG line at 191. `SubnetGroups.contains`, `src/java/org/apache/cassandra/config/SubnetGroups.java:57`, the match against each subnet at line 64. `ExceptionHandlers.UnexpectedChannelExceptionHandler.apply`, `src/java/org/apache/cassandra/transport/ExceptionHandlers.java:227`, the ERROR line at 271. `JVMStabilityInspector.inspectThrowable`, `src/java/org/apache/cassandra/utils/JVMStabilityInspector.java:105`, the check of the property at line 110, the early return at line 117, the call for the histogram at 120, the log line at 123, the call that may force a heap space error at 127 and the throw at line 131. `JVMStabilityInspector.forceHeapSpaceOomMaybe`, `src/java/org/apache/cassandra/utils/JVMStabilityInspector.java:193`, the two texts at line 184, the check of the message at 195, the ERROR line at 197 and the loop at 200. `HeapUtils.logHeapHistogram`, `src/java/org/apache/cassandra/utils/HeapUtils.java:57`, the INFO line at 61, the ERROR lines at 66 and 83 and the command at 79. `HeapUtils.logProcessOutput`, `src/java/org/apache/cassandra/utils/HeapUtils.java:171`, the INFO entry at 181. `CassandraRelevantProperties.PRINT_HEAP_HISTOGRAM_ON_OUT_OF_MEMORY_ERROR`, `src/java/org/apache/cassandra/config/CassandraRelevantProperties.java:406`. All ChronitonDB chronitondb-sandbox at `ffa1bc742d` | The same lines in cassandra-5.0 at `47227d98bf`. In cassandra-6.0 at `a02931dea8` and trunk at `45c325a01b`: `QueryMessage.execute` at line 103 with the catch at 126 and the log line at 131, `ExecuteMessage.execute` at line 132 with the catch at 206, which ends at line 210 with no log line, `ErrorMessage.fromException` at line 466 with the log line at 502 and the server error at 504, `ServerError.ServerError` at line 28 with the `toString` at 30, `Dispatcher.processRequest` at line 447 with the catch at 454, the handler at 464 and the server error at 465, `ExceptionHandlers.getUnexpectedExceptionHandler` at line 192 with the DEBUG line at 198, `ExceptionHandlers.UnexpectedChannelExceptionHandler.apply` at line 234 with the ERROR line at 278, `SubnetGroups.contains` at line 56 with the match at line 63, `JVMStabilityInspector.inspectThrowable` at line 109 with the check of the property at 114, the early return at 121, the call for the histogram at 124, the log line at 127, the call that may force a heap space error at 131 and the throw at 135, `HeapUtils.logHeapHistogram` at line 59 with the INFO line at 63, the ERROR lines at 68 and 85 and the command at 81, `HeapUtils.logProcessOutput` at line 173 with the INFO entry at 183, and `CassandraRelevantProperties.PRINT_HEAP_HISTOGRAM_ON_OUT_OF_MEMORY_ERROR` at line 481. `JVMStabilityInspector.forceHeapSpaceOomMaybe` stands in cassandra-6.0 at `a02931dea8` at line 200, with the two texts at 191, the check of the message at 202, the ERROR line at 204 and the loop at 207. In trunk at `45c325a01b` it stands at line 201 and differs: the second of the two texts, at line 191, reads `GC overhead limit exceeded`, the check of the message is at 204, the ERROR line is one of two, at lines 207 and 209, and the loop is at 212 |

These rules apply to every source:

1. Describe and cite behaviour, published designs, papers, public documentation and code under licences compatible with the Apache License 2.0.
2. Code or text under an incompatible licence, for example the Elastic License, SSPL, BUSL or a proprietary licence, MUST NOT be copied. The behaviour of such a system is taken only from its public documentation. Code under a compatible licence MAY be used only with credit. See [conventions.md](../../process/conventions.md#code-from-elsewhere).
3. Contributors working on the project's behalf MUST NOT search for or read patents for design work. Any patent concern goes to the maintainers.

## Glossary

Not applicable: the glossary is required from Challenging size, and this feature is Normal size. Section 3 defines the terms the requirements use.
