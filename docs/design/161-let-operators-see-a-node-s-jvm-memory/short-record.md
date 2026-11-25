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

# Short record: #161 Let operators see a node's JVM memory pools from CQL

| Field | Value |
|---|---|
| Title | Let operators see a node's JVM memory pools from CQL |
| Document type | Record (ISO/IEC/IEEE 15289) |
| Status | Draft |
| Version | 1 |
| Author | chronitondb-agent |
| Approver | The maintainer who merges the pull request |
| References | Issue #161. The [feature spec](../JVMEM-jvm-memory-pools-view/feature-spec.md), item 1 of the [plan](../JVMEM-jvm-memory-pools-view/plan.md) and the [delivery plan](../JVMEM-jvm-memory-pools-view/delivery-plan.md). Decision records [DEC-JVMEM-0001](../JVMEM-jvm-memory-pools-view/decisions/DEC-JVMEM-0001-jvm-memory-pools-view-has-no-switch.md) to [DEC-JVMEM-0013](../JVMEM-jvm-memory-pools-view/decisions/DEC-JVMEM-0013-the-view-stays-at-normal-risk-and-the-runs-of-its-two-tests-are-named.md). The delta entry [jvm-memory-pools-view.md](../../delta/jvm-memory-pools-view.md). The reference page [jvm-memory-pools.md](../../reference/virtual-tables/jvm-memory-pools.md). |
| Areas | observability |
| Tier | Short: no file the change touches is on the paths of the Critical floor |

Revision history, one row for each version:

| Version | Date | Change | Decision record |
|---|---|---|---|
| 1 | 2026-11-25 | First version | None |

Full history in git: [commits of this file](https://github.com/chronitonlabs/chronitondb/commits/chronitondb-sandbox/docs/design/161-let-operators-see-a-node-s-jvm-memory/short-record.md)

Location: `docs/design/161-let-operators-see-a-node-s-jvm-memory/short-record.md`. Process: [the short path](../../process/branching-and-review.md#the-short-path). The pull request that carries this record also carries the code and the tests.

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in BCP 14 (RFC 2119, RFC 8174) when, and only when, they appear in all capitals, as shown here.

The Tier row records the tier the change took and why. It is the first line that `tools/chronitondb/doclint.py tier --repo . --base origin/<line>` prints for the change, copied as printed. The process document check works it out again and refuses a row that differs.

## Contents

- [1. Impact](#1-impact)
- [2. What changes](#2-what-changes)
- [3. Decisions by the maintainers](#3-decisions-by-the-maintainers)
- [4. Test plan](#4-test-plan)
- [5. Where problems could occur](#5-where-problems-could-occur)

## 1. Impact

An operator sees the memory pools of a node's JVM over JMX today, and nowhere in CQL. An operator who checks a node with `cqlsh` or a driver and has no JMX access cannot see how full the old generation, the metaspace or the code cache is. This change is item 1 of the plan of the feature: the table `system_views.jvm_memory_pools`, its one hook in Apache Cassandra's code, its tests and its reference page, in one pull request, so the line never holds the table without them ([PRINCIPLE-020](../../process/principles.md#principle-020)).

The class stays Normal risk with two faults named, a wrong value in the table and a node that does not start because of it, as [DEC-JVMEM-0013](../JVMEM-jvm-memory-pools-view/decisions/DEC-JVMEM-0013-the-view-stays-at-normal-risk-and-the-runs-of-its-two-tests-are-named.md) decides. That record replaces DEC-JVMEM-0003, which the feature spec still cites. This record follows DEC-JVMEM-0013.

The table has no switch and is not held back until every node has it. That is an exception to [PRINCIPLE-003](../../process/principles.md#principle-003) and to the edge of [PRINCIPLE-089](../../process/principles.md#principle-089), for this table only, which [DEC-JVMEM-0001](../JVMEM-jvm-memory-pools-view/decisions/DEC-JVMEM-0001-jvm-memory-pools-view-has-no-switch.md) states with its reason: the table does no work until it is read, keeps no memory, and nodes share nothing of it.

The change adds no runtime behaviour beyond a read of the table, so it adds no metric, trace line or log line of its own ([PRINCIPLE-033](../../process/principles.md#principle-033)). An operator sees it work by reading it, and sees it fail by the error of the read and the log lines Apache Cassandra writes for a failed request.

## 2. What changes

The table is built by `JvmMemoryPoolsTable` in `src/java/org/chronitondb/virtual/` and added to `system_views` by one line in the constructor of `SystemViewsKeyspace`. Each REQ below is the requirement of the feature spec that it names, with the same words where it is not shortened.

- REQ-1: The node MUST hold the table `system_views.jvm_memory_pools`, with the partition key `name` of type `text` and the regular columns `type` of type `text` and `used_bytes`, `committed_bytes` and `max_bytes` of type `bigint`, from its startup and whatever its configuration. Source: FREQ-JVMEM-001.
- REQ-2: When a read runs, the table MUST hold for that read exactly one row for each memory pool that its JVM lists during the read, whichever rows the statement asks for, unless a call to the JVM throws during the read. Source: FREQ-JVMEM-002.
- REQ-3: The `name` column MUST hold the name of the memory pool as `MemoryPoolMXBean.getName` returns it, unchanged. Source: FREQ-JVMEM-003.
- REQ-4: The `type` column MUST hold `HEAP` for a memory pool of heap memory and `NON_HEAP` for every other memory pool. Source: FREQ-JVMEM-004.
- REQ-5: When `MemoryPoolMXBean.getUsage` returns a `MemoryUsage` object for a memory pool during the read, the three size columns of its row MUST hold the used, the committed and the maximum size in bytes of that one object. Source: FREQ-JVMEM-005.
- REQ-6: If that `MemoryUsage` object defines no maximum, then `max_bytes` MUST hold -1. Source: FREQ-JVMEM-006.
- REQ-7: The node MUST take the values of every row from its own running JVM during the read, with no message to another node and no value kept from an earlier read. Source: FREQ-JVMEM-007.
- REQ-8: While no statement reads the table, the feature MUST run no thread and no scheduled task and keep no value of a memory pool. Source: FREQ-JVMEM-008.
- REQ-9: The node MUST apply to a statement on the table the permission check of a table of `system_views`, with no check of the feature's own. Source: FREQ-JVMEM-009.
- REQ-10: When a statement writes to the table or truncates it, the node MUST refuse it with the error Apache Cassandra returns for a read only virtual table. Source: FREQ-JVMEM-010.
- REQ-11: The feature MUST NOT change the definition or the rows of another table, a JMX MBean, a metric or the output of a nodetool command, apart from the surfaces that list what the node holds. Source: FREQ-JVMEM-011.
- REQ-12: The reference page MUST name the table and each column, with its type and meaning, the two values of `type`, and the meanings of -1 in `max_bytes` and of null in the three size columns. Source: FREQ-JVMEM-012.
- REQ-13: The reference page MUST say what a read of the table answers on a node that does not have it, and name the step for moving back. Source: FREQ-JVMEM-013.
- REQ-14: If `MemoryPoolMXBean.getUsage` returns null for a memory pool during the read, then its row MUST hold null in the three size columns. Source: FREQ-JVMEM-014.
- REQ-15: The reference page MUST say that one statement can be answered from more than one read, with the three cases that were read, the one statement of exactly one read and the two consequences. Source: FREQ-JVMEM-015.
- REQ-16: The reference page MUST say how an operator lists and revokes the grants that name the table, as which role, what a grant left behind does, the three commits for whose code it says that, that it says so for no other code, and how such a grant is removed. Source: FREQ-JVMEM-016.
- REQ-17: When a statement grants or revokes a permission on the table by name, the node MUST handle it as Apache Cassandra handles it on a table of `system_views`. Source: FREQ-JVMEM-017.
- REQ-18: If a call that the table makes to the JVM throws while a read builds its rows, then the table MUST NOT catch what was thrown, whichever rows the statement asks for. Source: FREQ-JVMEM-018.
- REQ-19: The reference page MUST say that an exception, or an error of the JVM that is no out of memory error, for one memory pool fails every read of the table while it lasts. Source: FREQ-JVMEM-019.
- REQ-20: The reference page MUST say that the table passes on what a call to the JVM throws, what the node then answers and logs, the three commits for whose code it says that, that it says so for no other code, and of an out of memory error only that it goes to the node's own handling. Source: FREQ-JVMEM-020.
- REQ-21: If the JVM lists more than one memory pool under one name during a read, then the read MUST fail with `IllegalStateException` and the message `the JVM lists more than one memory pool named <name>`, whichever rows the statement asks for. Source: decision 2 of section 3.
- REQ-22: The reference page MUST be `docs/reference/virtual-tables/jvm-memory-pools.md`. Source: decision 3 of section 3.

How the change answers what section 11 of the feature spec leaves to the design of the item:

1. **Tests by item.** Every test of this record is in this item. Item 2 adds the end to end tests on a cluster.
2. **An import that brings a table of the same name.** The constructor of a virtual keyspace builds its tables with `Tables.of`: `VirtualKeyspace.VirtualKeyspace`, `src/java/org/apache/cassandra/db/virtual/VirtualKeyspace.java:41`, ChronitonDB chronitondb-sandbox at `45f7afc7ce`. That builder holds the tables by name in an `ImmutableMap.Builder`, whose build refuses a second entry for one name: `Tables.Builder.build`, `src/java/org/apache/cassandra/schema/Tables.java:221`, the same tree. The node then fails at startup, and every test that starts a node catches it, the test of TEST-1 among them.
3. **Two pools under one name.** REQ-21.
4. **The runs of the two tests of DEC-JVMEM-0013.** `JvmMemoryPoolsTableTest.testNodeHoldsTheViewAndAnswersARead` and `JvmMemoryPoolsTableTest.testViewShowsThePoolsOfTheSameJvm`. Both pass in the test log of each commit of this pull request, from the commit that adds the hook, which is the first commit.
5. **A statement answered from more than one read when one read fails.** Each read builds every row, so the read that fails throws, and the statement fails with it. This change does not change how Apache Cassandra ends such a statement, and no test of it covers that.
6. **Exceptions.** PRINCIPLE-003 and PRINCIPLE-089, as section 1 says.

The one place a test supplies pools of its own is the public constructor `JvmMemoryPoolsTable(String, Supplier)`. No setting, system property, MBean, statement or command reaches it. The constructor and the static initialiser make no call to `java.lang.management`, the class reads no setting, and the code that builds the rows holds no catch. No pre-existing test file of Apache Cassandra changes: no stock test pins the complete list of the tables of `system_views`.

## 3. Decisions by the maintainers

The name of the table, its columns, their types and their values were decided before this item, in DEC-JVMEM-0001 to DEC-JVMEM-0013. The maintainers answered the three points that those records left open on 2026-11-25:

1. **The build starts before the feature spec cites DEC-JVMEM-0013.** This record cites that decision record directly. Answered on 2026-11-25.
2. **A JVM that lists two pools under one name fails every read, naming the pool.** No pool is hidden behind another of the same name. The error is `java.lang.IllegalStateException: the JVM lists more than one memory pool named <name>`. Answered on 2026-11-25.
3. **The reference page goes in a folder of reference pages for virtual tables**, at `docs/reference/virtual-tables/jvm-memory-pools.md`. Answered on 2026-11-25.

Details of form that follow Apache Cassandra's convention or an existing file, which the merge confirms:

1. The class name `JvmMemoryPoolsTable`, after the stock virtual table classes such as `ThreadPoolsTable`.
2. The new `NEWS-chronitondb.txt` follows the form of Apache Cassandra's `NEWS.txt`, with sections for new features, upgrading and moving back.
3. The example on the reference page shows the columns in the order `cqlsh` prints them, the partition key first and then the other columns by name.

## 4. Test plan

Every unit test class of the project runs on the options of `test-latest`, and the in-JVM distributed test on the latest configuration, on Java 17, the one JDK of the line.

- TEST-1: `org.chronitondb.virtual.JvmMemoryPoolsTableTest.testNodeHoldsTheViewAndAnswersARead` proves REQ-1.
- TEST-2: `org.chronitondb.virtual.JvmMemoryPoolsTableTest.testViewShowsThePoolsOfTheSameJvm` proves REQ-2, REQ-3, REQ-4 and REQ-6.
- TEST-3: `org.chronitondb.virtual.JvmMemoryPoolsTableTest.testPagedReadGivesEveryPoolOnce` proves REQ-2 and REQ-7.
- TEST-4: `org.chronitondb.virtual.JvmMemoryPoolsTableTest.testRowHoldsTheSizesOfTheUsage` proves REQ-4, REQ-5 and REQ-6.
- TEST-5: `org.chronitondb.virtual.JvmMemoryPoolsTableTest.testPoolWithNoUsageShowsNullSizes` proves REQ-14.
- TEST-6: `org.chronitondb.virtual.JvmMemoryPoolsTableTest.testThreeSizesOfARowComeFromOneCall` proves REQ-5.
- TEST-7: `org.chronitondb.virtual.JvmMemoryPoolsTableTest.testSecondReadTakesTheValuesOfTheSecondRead` proves REQ-7.
- TEST-8: `org.chronitondb.virtual.JvmMemoryPoolsTableTest.testWritesAndTruncationAreRefused` proves REQ-10.
- TEST-9: `org.chronitondb.virtual.JvmMemoryPoolsTableTest.testSystemViewsListsEveryStockTableAndTheView` proves REQ-11. Its list of the stock tables is written in the test, from the line before this change, and two stock tables that a test node with no CIDR authorizer cannot read are not read.
- TEST-10: `org.chronitondb.virtual.JvmMemoryPoolsTableTest.testFailureForOnePoolFailsAReadOfAnotherPool` proves REQ-2 and REQ-18, for an exception and for an error of the JVM.
- TEST-11: `org.chronitondb.virtual.JvmMemoryPoolsTableTest.testFailureFromTheListOfPoolsFailsAReadOfOnePool` proves REQ-18, for an exception and for an error of the JVM.
- TEST-12: `org.chronitondb.virtual.JvmMemoryPoolsTableTest.testDirectReadPassesOnTheObjectThatWasThrown` proves REQ-18.
- TEST-13: `org.chronitondb.virtual.JvmMemoryPoolsTableTest.testBuildingTheViewMakesNoCallForThePools` proves REQ-1.
- TEST-14: `org.chronitondb.virtual.JvmMemoryPoolsTableTest.testNoThreadNoTaskAndNoKeptValue` proves REQ-8: after reads no thread of the JVM runs code of the feature, no thread is left in the thread group of the thread that read, the view class names no class that starts a thread or schedules a task, and no field of the view changes.
- TEST-15: `org.chronitondb.virtual.JvmMemoryPoolsTableTest.testRepeatedPoolNameFailsTheRead` proves REQ-21.
- TEST-16: `org.chronitondb.virtual.JvmMemoryPoolsPermissionsTest.testReadNeedsTheGrantsOfATableOfSystemViews` proves REQ-9: a grant on the table or on `system_views` lets a role read it, and a grant on all keyspaces does not.
- TEST-17: `org.chronitondb.virtual.JvmMemoryPoolsPermissionsTest.testGrantAndRevokeOnTheViewByName` proves REQ-17.
- TEST-18: `org.chronitondb.virtual.JvmMemoryPoolsPermissionsTest.testGrantRowForATableTheNodeDoesNotHave` proves REQ-16, for the four places where a grant row is read.
- TEST-19: `org.chronitondb.virtual.JvmMemoryPoolsPageTest.testPageNamesEveryColumnWithItsTypeAndKind` and `testPageGivesTheValuesOfTypeAndTheMeaningOfMinusOneAndNull` prove REQ-12 and REQ-22.
- TEST-20: `org.chronitondb.virtual.JvmMemoryPoolsPageTest.testPageSaysWhatANodeWithoutTheViewAnswersAndNamesTheStep` proves REQ-13.
- TEST-21: `org.chronitondb.virtual.JvmMemoryPoolsPageTest.testPageSaysOneStatementCanTakeMoreThanOneRead` proves REQ-15.
- TEST-22: `org.chronitondb.virtual.JvmMemoryPoolsPageTest.testPageSaysHowToRemoveTheGrantsAndWhatOneLeftBehindDoes` proves REQ-16.
- TEST-23: `org.chronitondb.virtual.JvmMemoryPoolsPageTest.testPageSaysAFailureForOnePoolFailsEveryRead` proves REQ-19.
- TEST-24: `org.chronitondb.virtual.JvmMemoryPoolsPageTest.testPageSaysWhatTheNodeAnswersAndLogsForAFailedRead` proves REQ-20.
- TEST-25: `org.chronitondb.virtual.test.JvmMemoryPoolsNodesTest.testPoolGivenToOneNodeShowsOnThatNodeOnly` proves REQ-7 on a cluster of two nodes.
- TEST-26: `org.chronitondb.virtual.JvmMemoryPoolsTableTest.testNoPoolGivesNoRow` proves REQ-2 for a JVM that lists no pool and for a name that no pool has.
- TEST-27: `org.chronitondb.virtual.JvmMemoryPoolsPageTest.testExampleStatementsRunAndTheSampleShowsTheColumnsInTheirOrder` proves REQ-12 for the example: its statements run, and its sample shows the columns in the order a node returns them.

What no test shows, and the review of the code reads instead: that the code which builds the rows holds no catch (REQ-18), that the static initialiser and the constructor make no call to `java.lang.management` (REQ-1), that no static field and no other object of the package keeps a value of a memory pool, and that the code starts no thread in a thread group other than that of the thread that reads (REQ-8), that the class reads no setting (REQ-1), and that only the code of a test reaches the constructor that takes pools (REQ-7). That the meanings on the page are those of the feature spec is read at the gate of the milestone.

The tests of Apache Cassandra that exit criterion 5 of the delivery plan names run unchanged at the gate of the milestone.

## 5. Where problems could occur

Worst case first.

1. **A node does not start.** Every node of a release with the table exits during its start if the constructor or the static initialiser of `JvmMemoryPoolsTable` throws, since the node builds the tables of `system_views` once at startup. An import from Apache Cassandra that adds a table of the same name stops the start the same way.
2. **The table shows a wrong value.** An operator reads a size that is not what the JVM reports: a wrong unit, two columns swapped, sizes of two readings in one row, a wrong type, or a pool missing or shown twice. The operator may then resize a heap that needs no change, or miss a pool that is full. It would come from `JvmMemoryPoolsTable.data`.
3. **A read of the table fails.** An operator sees a server error in place of the rows, and the node logs it at ERROR for each failing request, so a tool that polls the table adds ERROR lines while the fault lasts. It comes from a fault of the table class, from the JVM throwing for one pool or for the list, or from a JVM that lists two pools under one name, which REQ-21 turns into a failed read.
4. **Another table of `system_views` is missing or fails.** A monitoring tool sees a table such as `system_views.settings` missing. It would come from a wrong edit of the list in `SystemViewsKeyspace`.
5. **The values reach a role that should not see them, or a client changes the table.** It would come from a table class that is not built on Apache Cassandra's read only virtual table.
6. **A read is refused during a rolling upgrade.** A tool whose driver sends the read to a node without the table sees `table jvm_memory_pools does not exist` until every node has it.
7. **A grant on the table cannot be revoked after moving back.** A node without the table refuses a `REVOKE` that names it, so a grant not revoked before moving back stays in the auth tables.
8. **The reference page names the table or a column wrongly.** An operator copies a statement from the page and it fails.
9. **The table does work when nobody reads it.** An operator sees a thread, a task or memory of the feature on a node where nobody reads it.
10. **An operator takes a paged or summed read for one moment.** A sum over rows of more than one read mixes moments, and a pool can be missing if the JVM changes its list between reads, as the page says.
