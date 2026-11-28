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

# Short record: #172 Let operators see a node's JVM garbage collectors from CQL

| Field | Value |
|---|---|
| Title | Let operators see a node's JVM garbage collectors from CQL |
| Document type | Record (ISO/IEC/IEEE 15289) |
| Status | Draft |
| Version | 1 |
| Author | chronitondb-agent |
| Approver | The maintainer who merges the pull request |
| References | Issue #172. The delta entry [jvm-garbage-collectors-view.md](../../delta/jvm-garbage-collectors-view.md). The reference page [jvm-garbage-collectors.md](../../reference/virtual-tables/jvm-garbage-collectors.md). The [short record of the memory pools view](../161-let-operators-see-a-node-s-jvm-memory/short-record.md), which this view follows. |
| Areas | observability |
| Tier | Short: no file the change touches is on the paths of the Critical floor |
| Exceptions | PRINCIPLE-003, PRINCIPLE-089 |

Revision history, one row for each version:

| Version | Date | Change | Decision record |
|---|---|---|---|
| 1 | 2026-11-27 | First version | None |

Full history in git: [commits of this file](https://github.com/chronitonlabs/chronitondb/commits/chronitondb-sandbox/docs/design/172-let-operators-see-a-node-s-jvm-garbage/short-record.md)

Location: `docs/design/172-let-operators-see-a-node-s-jvm-garbage/short-record.md`. Process: [the short path](../../process/branching-and-review.md#the-short-path). The pull request that carries this record also carries the code and the tests.

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in BCP 14 (RFC 2119, RFC 8174) when, and only when, they appear in all capitals, as shown here.

The Tier row records the tier the change took and why. It is the first line that `tools/chronitondb/doclint.py tier --repo . --base origin/<line>` prints for the change, copied as printed. The process document check works it out again and refuses a row that differs.

## Contents

- [1. Impact](#1-impact)
- [2. What changes](#2-what-changes)
- [3. Decisions by the maintainers](#3-decisions-by-the-maintainers)
- [4. Test plan](#4-test-plan)
- [5. Where problems could occur](#5-where-problems-could-occur)

## 1. Impact

An operator sees how often each garbage collector of a node's JVM has run, and for how long, over JMX today, and nowhere in CQL. An operator who checks a node with `cqlsh` or a driver and has no JMX access cannot see whether the node spends its time in collections. This change adds the table `system_views.jvm_garbage_collectors`, its one hook in Apache Cassandra's code, its tests and its reference page, in one pull request, so the line never holds the table without them ([PRINCIPLE-020](../../process/principles.md#principle-020)).

The table has no switch and is not held back until every node has it. That is an exception to [PRINCIPLE-003](../../process/principles.md#principle-003) and to the edge of [PRINCIPLE-089](../../process/principles.md#principle-089), for this table only, which decision 1 of section 3 takes. The reason is the one the memory pools view took the same exception for: the table does no work until it is read, keeps no memory, and nodes share nothing of it. The maintainers decide the exception by merging this record.

The change adds no runtime behaviour beyond a read of the table, so it adds no metric, trace line or log line of its own ([PRINCIPLE-033](../../process/principles.md#principle-033)). An operator sees it work by reading it, and sees it fail by the error of the read and the log lines Apache Cassandra writes for a failed request.

## 2. What changes

The table is built by `JvmGarbageCollectorsTable` in `src/java/org/chronitondb/virtual/` and added to `system_views` by one line in the constructor of `SystemViewsKeyspace`, after the line of the memory pools view.

- REQ-1: The node MUST hold the table `system_views.jvm_garbage_collectors`, with the partition key `name` of type `text` and the regular columns `collection_count` and `collection_time_millis` of type `bigint`, from its startup and whatever its configuration. Source: issue #172 and decisions 1 and 2 of section 3.
- REQ-2: When a read runs, the table MUST hold for that read exactly one row for each garbage collector that its JVM lists during the read, whichever rows the statement asks for, unless a call to the JVM throws during the read. Source: issue #172.
- REQ-3: The `name` column MUST hold the name of the collector as `GarbageCollectorMXBean.getName` returns it, unchanged. Source: decision 2 of section 3.
- REQ-4: The `collection_count` column MUST hold the value that `GarbageCollectorMXBean.getCollectionCount` returns for the collector during the read, and the `collection_time_millis` column the value that `GarbageCollectorMXBean.getCollectionTime` returns, -1 included. Source: decisions 2 and 3 of section 3.
- REQ-5: The node MUST take the values of every row from its own running JVM during the read, with no message to another node and no value kept from an earlier read. Source: issue #172.
- REQ-6: While no statement reads the table, the table MUST run no thread and no scheduled task and keep no value of a collector. Source: decision 1 of section 3.
- REQ-7: The node MUST apply to a statement on the table the permission check of a table of `system_views`, with no check of the table's own. Source: issue #172.
- REQ-8: When a statement writes to the table or truncates it, the node MUST refuse it with the error Apache Cassandra returns for a read only virtual table. Source: issue #172.
- REQ-9: The change MUST NOT change the definition or the rows of another table, a JMX MBean, a metric or the output of a nodetool command, apart from the surfaces that list what the node holds. Source: issue #172.
- REQ-10: If a call that the table makes to the JVM throws while a read builds its rows, then the table MUST NOT catch what was thrown, whichever rows the statement asks for. Source: decision 3 of section 3.
- REQ-11: If the JVM lists more than one garbage collector under one name during a read, then the read MUST fail with `IllegalStateException` and the message `the JVM lists more than one garbage collector named <name>`, whichever rows the statement asks for, unless a call to the JVM throws during the read before the table takes the name of the second collector of that name. Source: decision 3 of section 3.
- REQ-12: The reference page `docs/reference/virtual-tables/jvm-garbage-collectors.md` MUST name the table and each column, with its type and meaning, and the meaning of -1. Source: issue #172.
- REQ-13: The reference page MUST say what a read of the table answers on a node that does not have it, and name the step for moving back. Source: issue #172.
- REQ-14: The reference page MUST say that a failure for one collector fails every read of the table, and give the error of a repeated name. Source: decision 3 of section 3.
- REQ-15: The reference page MUST say that one statement can be answered from more than one read, with values of different moments. Source: issue #172.

Points of the build:

1. **An import that brings a table of the same name.** The constructor of a virtual keyspace builds its tables with `Tables.of`: `VirtualKeyspace.VirtualKeyspace`, `src/java/org/apache/cassandra/db/virtual/VirtualKeyspace.java:41`, ChronitonDB chronitondb-sandbox at `ad5850b528`. `Tables.Builder.build`, `src/java/org/apache/cassandra/schema/Tables.java:221`, ChronitonDB chronitondb-sandbox at `ad5850b528`, calls the constructor `Tables.Tables`, which builds an `ImmutableMap` of the tables by name at `src/java/org/apache/cassandra/schema/Tables.java:52`, ChronitonDB chronitondb-sandbox at `ad5850b528`, and that build refuses a second entry for one name. The node then fails at startup, and every test that starts a node catches it, the test of TEST-1 among them.
2. **Two collectors under one name.** REQ-11. Over JMX each collector has the name `java.lang:type=GarbageCollector,name=<collector>`, which the Java SE documentation of `GarbageCollectorMXBean` gives, and an MBean server holds one bean for one name, so no known JVM lists two. The exception reaches the node's handling of a failed request as an exception of a call to the JVM does. [PRINCIPLE-036](../../process/principles.md#principle-036) lets a node log an unexpected server error at ERROR for each failing request, and asks for this assessment:
   1. **Why it is unexpected.** A JVM that lists two collectors under one name is at fault, and no statement of a client causes it. The table has no expected failure that takes this path.
   2. **What bounds how often it fires.** Each entry is logged for a read of a client that fails, so the rate is the rate at which clients read the table while the fault lasts. The table adds no other bound, as the memory pools view adds none.
   3. **What the log holds if it fires on every request.** The class name, the message, which names the collector, and the stack trace. The name of a collector is the JVM's, and the entries hold no user data ([PRINCIPLE-035](../../process/principles.md#principle-035)).
3. **Exceptions.** The Exceptions row names PRINCIPLE-003 and PRINCIPLE-089. In their place the table is present on every node of a release that has it, from startup, with no switch and no hold back, for this table only, for the reason of section 1.
4. **A merged test of the project that changes.** `JvmMemoryPoolsTableTest.testSystemViewsListsEveryStockTableAndTheView` pins the complete list of the tables of `system_views`. Its expected list changes from the stock tables and `jvm_memory_pools` to the stock tables, `jvm_memory_pools` and `jvm_garbage_collectors`, by one added line, `expected.add(JvmGarbageCollectorsTable.TABLE_NAME)`. The old expectation is no longer right because the node now holds the new table, and the test fails on any list that differs ([PRINCIPLE-065](../../process/principles.md#principle-065)). No other assertion of a merged test changes.

The one place a test supplies collectors of its own is the public constructor `JvmGarbageCollectorsTable(String, Supplier)`. No setting, system property, MBean, statement or command reaches it. The constructor and the static initialiser make no call to `java.lang.management`, the class reads no setting, and the code that builds the rows holds no catch. No pre-existing test file of Apache Cassandra changes: no stock test pins the complete list of the tables of `system_views`.

## 3. Decisions by the maintainers

The maintainers answered the three visible choices of the change on 2026-11-27:

1. **The table ships with no switch, as the memory pools view does.** It is present on every node of a release that has it, from startup, an exception to PRINCIPLE-003 and PRINCIPLE-089 for this table. Answered on 2026-11-27.
2. **The name and the columns.** The table is `system_views.jvm_garbage_collectors`, with the partition key `name` of type `text` and the columns `collection_count` and `collection_time_millis` of type `bigint`. Stock tables name a plain time column with `millis`, such as `duration_millis` of `StreamingVirtualTable.updateDataSet`, `src/java/org/apache/cassandra/db/virtual/StreamingVirtualTable.java:96`, ChronitonDB chronitondb-sandbox at `ad5850b528`. Answered on 2026-11-27.
3. **Edge values.** A value the JVM leaves undefined shows -1, as the bean returns it. A JVM that lists two collectors under one name fails every read with an error that names the collector, so no collector is hidden. Answered on 2026-11-27.

Details of form that follow Apache Cassandra's convention or an existing file, which the merge confirms:

1. The class name `JvmGarbageCollectorsTable`, after the memory pools view `JvmMemoryPoolsTable` and the stock virtual table classes such as `ThreadPoolsTable`.
2. The entries in `NEWS-chronitondb.txt` follow those of the memory pools view, in the sections for new features, upgrading and moving back.
3. The example on the reference page shows the columns in the order `cqlsh` prints them, the partition key first and then the other columns by name.
4. The reference page points to the page of the memory pools view for what holds for both tables alike: the cases of one statement answered from more than one read, what the node answers and logs for a failed read, and what a grant left behind does.

## 4. Test plan

Every unit test class runs on the options of `test-latest`, and the in-JVM distributed test on the latest configuration, on Java 17, the one JDK of the line.

- TEST-1: `org.chronitondb.virtual.JvmGarbageCollectorsTableTest.testNodeHoldsTheViewAndAnswersARead` proves REQ-1.
- TEST-2: `org.chronitondb.virtual.JvmGarbageCollectorsTableTest.testViewShowsTheCollectorsOfTheSameJvm` proves REQ-2, REQ-3 and REQ-4 against the collectors of the test node's own JVM: each row lies between two readings of its bean, and a name read by itself or with `IN` gives its row.
- TEST-3: `org.chronitondb.virtual.JvmGarbageCollectorsTableTest.testPagedReadGivesEveryCollectorOnce` proves REQ-2 for a read in pages of one row.
- TEST-4: `org.chronitondb.virtual.JvmGarbageCollectorsTableTest.testWritesAndTruncationAreRefused` proves REQ-8.
- TEST-5: `org.chronitondb.virtual.JvmGarbageCollectorsTableTest.testSystemViewsListsEveryEarlierTableAndTheView` proves REQ-9 for `system_views`. Its list of the earlier tables is written in the test, from the line before this change, and two stock tables that a test node with no CIDR authorizer cannot read are not read.
- TEST-6: `org.chronitondb.virtual.JvmGarbageCollectorsRowsTest.testRowHoldsTheCountAndTheTimeOfTheCollector` proves REQ-4 for given values, zero and the largest `bigint`.
- TEST-7: `org.chronitondb.virtual.JvmGarbageCollectorsRowsTest.testUndefinedValueShowsMinusOne` proves REQ-4 for -1 in either column and in both.
- TEST-8: `org.chronitondb.virtual.JvmGarbageCollectorsRowsTest.testSecondReadTakesTheValuesOfTheSecondRead` proves REQ-5.
- TEST-9: `org.chronitondb.virtual.JvmGarbageCollectorsRowsTest.testNoCollectorGivesNoRow` proves REQ-2 for a JVM that lists no collector and for a name that no collector has.
- TEST-10: `org.chronitondb.virtual.JvmGarbageCollectorsRowsTest.testRepeatedCollectorNameFailsTheRead` proves REQ-11.
- TEST-11: `org.chronitondb.virtual.JvmGarbageCollectorsRowsTest.testFailureForOneCollectorFailsAReadOfAnotherCollector` proves REQ-2 and REQ-10, for the count and for the time, for an exception and for an error of the JVM.
- TEST-12: `org.chronitondb.virtual.JvmGarbageCollectorsRowsTest.testFailureFromTheListOfCollectorsFailsAReadOfOneCollector` proves REQ-10, for an exception and for an error of the JVM.
- TEST-13: `org.chronitondb.virtual.JvmGarbageCollectorsRowsTest.testDirectReadPassesOnTheObjectThatWasThrown` proves REQ-10.
- TEST-14: `org.chronitondb.virtual.JvmGarbageCollectorsRowsTest.testBuildingTheViewMakesNoCallForTheCollectors` proves REQ-1.
- TEST-15: `org.chronitondb.virtual.JvmGarbageCollectorsRowsTest.testNoThreadNoTaskAndNoKeptValue` proves REQ-6: after reads no other thread runs code of the table class, no thread is left in the thread group of the thread that read, the class names no class that starts a thread or schedules a task, and no field of the table changes.
- TEST-16: `org.chronitondb.virtual.JvmGarbageCollectorsPermissionsTest.testReadNeedsTheGrantsOfATableOfSystemViews` proves REQ-7: a grant on the table or on `system_views` lets a role read it, and a grant on all keyspaces or on the memory pools view does not.
- TEST-17: `org.chronitondb.virtual.JvmGarbageCollectorsPermissionsTest.testGrantAndRevokeOnTheViewByName` proves REQ-7 and REQ-13 for the statements of the step for moving back.
- TEST-18: `org.chronitondb.virtual.JvmGarbageCollectorsPageTest.testPageNamesEveryColumnWithItsTypeAndKind`, `testExampleStatementsRunAndTheSampleShowsTheColumnsInTheirOrder` and `testPageGivesTheMeaningOfMinusOne` prove REQ-12.
- TEST-19: `org.chronitondb.virtual.JvmGarbageCollectorsPageTest.testPageSaysWhatANodeWithoutTheViewAnswersAndNamesTheStep` proves REQ-13.
- TEST-20: `org.chronitondb.virtual.JvmGarbageCollectorsPageTest.testPageSaysAFailureForOneCollectorFailsEveryReadAndNamesTheError` proves REQ-14.
- TEST-21: `org.chronitondb.virtual.JvmGarbageCollectorsPageTest.testPageSaysOneStatementCanTakeMoreThanOneRead` proves REQ-15.
- TEST-22: `org.chronitondb.virtual.test.JvmGarbageCollectorsNodesTest.testCollectorGivenToOneNodeShowsOnThatNodeOnly` proves REQ-5 on a cluster of two nodes.
- TEST-23: `org.chronitondb.virtual.JvmMemoryPoolsTableTest.testSystemViewsListsEveryStockTableAndTheView`, with the one line of section 2, point 4, proves REQ-9 for the memory pools view, whose definition and rows the merged tests of that view read unchanged.

No tracing test applies, because a read of the table takes no decision and no fallback and adds no step of its own to a request: it builds its rows by calls to the JVM, and Apache Cassandra's tracing of the read is unchanged. So the change adds no trace event ([PRINCIPLE-033](../../process/principles.md#principle-033)).

What no test shows, and the review of the code reads instead: that the code which builds the rows holds no catch (REQ-10), that the static initialiser and the constructor make no call to `java.lang.management` (REQ-1), that no static field and no other object of the package keeps a value of a collector (REQ-6), that the class reads no setting (REQ-1), and that only the code of a test reaches the constructor that takes collectors (REQ-5).

## 5. Where problems could occur

Worst case first.

1. **A node does not start.** Every node of a release with the table exits during its start if the constructor or the static initialiser of `JvmGarbageCollectorsTable` throws, since the node builds the tables of `system_views` once at startup. An import from Apache Cassandra that adds a table of the same name stops the start the same way.
2. **The table shows a wrong value.** An operator reads a count or a time that is not what the JVM reports: the two columns swapped, a wrong unit, a collector missing or shown twice, or 0 where the JVM leaves a value undefined. The operator may then tune a collector that needs no change, or miss a node that spends its time in collections. It would come from `JvmGarbageCollectorsTable.data`.
3. **A read of the table fails.** An operator sees a server error in place of the rows, and the node logs it at ERROR for each failing request, so a tool that polls the table adds ERROR lines while the fault lasts. It comes from a fault of the table class, from the JVM throwing for one collector or for the list, or from a JVM that lists two collectors under one name, which REQ-11 turns into a failed read.
4. **Another table of `system_views` is missing or fails.** A monitoring tool sees a table such as `system_views.settings` or `system_views.jvm_memory_pools` missing. It would come from a wrong edit of the list in `SystemViewsKeyspace`.
5. **The values reach a role that should not see them, or a client changes the table.** It would come from a table class that is not built on Apache Cassandra's read only virtual table.
6. **A read is refused during a rolling upgrade.** A tool whose driver sends the read to a node without the table sees `table jvm_garbage_collectors does not exist` until every node has it.
7. **A grant on the table cannot be revoked after moving back.** A node without the table refuses a `REVOKE` that names it, so a grant not revoked before moving back stays in the auth tables.
8. **An operator takes the time for a pause time.** For a collector that works beside the threads of the node, the time need not be time in which those threads were stopped, as the page says.
9. **The reference page names the table or a column wrongly.** An operator copies a statement from the page and it fails.
10. **The table does work when nobody reads it.** An operator sees a thread, a task or memory of the table on a node where nobody reads it.
