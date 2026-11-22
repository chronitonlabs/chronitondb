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

# Plan: JVM memory pools view in CQL

| Field | Value |
|---|---|
| Title | Plan for JVM memory pools view in CQL |
| Document type | Plan (ISO/IEC/IEEE 15289) |
| Status | Draft |
| Version | 1 |
| Author | Architect: chronitondb-agent |
| Approver | The maintainer who merges the pull request |
| References | The [feature spec](feature-spec.md) and the [delivery plan](delivery-plan.md). Decision records [DEC-JVMEM-0001](decisions/DEC-JVMEM-0001-jvm-memory-pools-view-has-no-switch.md), [DEC-JVMEM-0003](decisions/DEC-JVMEM-0003-jvm-memory-pools-view-stays-at-normal-risk.md), [DEC-JVMEM-0006](decisions/DEC-JVMEM-0006-a-grant-left-on-the-view-is-documented.md), [DEC-JVMEM-0009](decisions/DEC-JVMEM-0009-an-error-for-one-pool-fails-every-read.md) and [DEC-JVMEM-0010](decisions/DEC-JVMEM-0010-the-view-catches-nothing-a-call-to-the-jvm-throws.md). Line `chronitondb-sandbox`. |
| Areas | observability |
| Risk | Normal: the worst Bug Category is Availability, a read of the view that fails. The feature adds a virtual table, a public interface, so it is Normal risk at least. Decision record [DEC-JVMEM-0003](decisions/DEC-JVMEM-0003-jvm-memory-pools-view-stays-at-normal-risk.md) keeps it at Normal risk with two faults named: a wrong value in the view, and a node that does not start because of the view. |
| Size | Normal: one view class, one hook in a file of Apache Cassandra, names that are kept for the line once shipped, and a value the JVM leaves undefined. |
| Reach | One area: virtual tables. Both items work in the package `org.chronitondb.virtual`, its tests and its reference page, with one hook in `org.apache.cassandra.db.virtual`. |

Revision history, one row for each version:

| Version | Date | Change | Decision record |
|---|---|---|---|
| 1 | 2026-11-21 | First version | None |

Full history in git: [commits of this file](https://github.com/chronitonlabs/chronitondb/commits/chronitondb-sandbox/docs/design/JVMEM-jvm-memory-pools-view/plan.md)

Location: `docs/design/JVMEM-jvm-memory-pools-view/plan.md` on the line `chronitondb-sandbox`. Process: [additive.md](../../process/additive.md).

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in BCP 14 (RFC 2119, RFC 8174) when, and only when, they appear in all capitals, as shown here.

The Risk, Size and Reach rows repeat the feature spec's class, the level words the same, as [classification.md](../../process/classification.md) defines it.

This plan cites the feature spec and does not restate it. "Section" with a number is a section of the feature spec, "problem" with a number is a problem of its section 4, and "fact" with a number is a code fact of its section 12. "The view" is the table `system_views.jvm_memory_pools`. "The reference page" is the page of the view that section 2.2 names.

## Contents

- [1. Items](#1-items)
  - [Item 1: The view, its hook, its tests and its reference page](#item-1-the-view-its-hook-its-tests-and-its-reference-page)
  - [Item 2: End to end tests of the view on a cluster](#item-2-end-to-end-tests-of-the-view-on-a-cluster)
- [2. Validation items](#2-validation-items)
- [3. Traceability](#3-traceability)

## 1. Items

The feature has two items: one build item and one validation item. The feature has no switch, so no merged item may make unfinished work reachable ([PRINCIPLE-020](../../process/principles.md#principle-020)). The hook is what makes the view reachable. So the item that adds the hook delivers the view whole, with its tests and its reference page, as section 2.8 and section 11 say. The validation item is split off because its tests are written from the feature requirements and not from the build item's design, and because it has a real prerequisite: it needs the merged view.

### Item 1: The view, its hook, its tests and its reference page

- **Delivers:** FREQ-JVMEM-001, FREQ-JVMEM-002, FREQ-JVMEM-003, FREQ-JVMEM-004, FREQ-JVMEM-005, FREQ-JVMEM-006, FREQ-JVMEM-007, FREQ-JVMEM-008, FREQ-JVMEM-009, FREQ-JVMEM-010, FREQ-JVMEM-011, FREQ-JVMEM-012, FREQ-JVMEM-013, FREQ-JVMEM-014, FREQ-JVMEM-015, FREQ-JVMEM-016, FREQ-JVMEM-017, FREQ-JVMEM-018, FREQ-JVMEM-019, FREQ-JVMEM-020
- **Acceptance criteria:**
  1. The item MUST add the view class to the package `org.chronitondb.virtual`, with the table, the columns and the types of section 2.2, and with no import that section 2.7 does not allow (FREQ-JVMEM-001).
  2. The item MUST add the view to the tables of `system_views` by the one hook of section 2.7, with the delta entry of that change in the same pull request (FREQ-JVMEM-001, FREQ-JVMEM-011).
  3. When a test node starts with the default configuration and a statement reads the view, the node MUST answer with the rows of the view, as the first test of problem 1 in section 4.1 checks (FREQ-JVMEM-001).
  4. When a read runs, the view MUST hold the rows that FREQ-JVMEM-002 to FREQ-JVMEM-007 and FREQ-JVMEM-014 require, and each test that problem 2 in section 4.1 names proves it.
  5. When a statement reads every row of the view, one row by its name, or two rows by their names with `IN` on a test node, the node MUST answer with no error, which are the reads that problem 3 in section 4.1 adds to the unit tests of problem 2 (FREQ-JVMEM-002).
  6. When a test reads the view twice and changes between the two reads the usage of a memory pool that it supplies, the second answer MUST hold the changed sizes, which is the last test of problem 3 in section 4.1 with a pool of the test's own (FREQ-JVMEM-007).
  7. If a call that the view makes to the JVM throws an exception, or an error of the JVM that is no out of memory error, while a read builds its rows, whether the call for the list of memory pools or a call to the bean of one memory pool, then the read MUST fail with what was thrown, uncaught by the view, whichever rows the statement asks for (FREQ-JVMEM-018).
  8. While no statement reads the view, both before the first read of the view and after a read has ended, the feature MUST run no thread and no scheduled task and keep no value of a memory pool, as the test of problem 9 in section 4.1 checks, which the item extends to look for a thread and a scheduled task after a read too (FREQ-JVMEM-008).
  9. The node MUST apply to a statement on the view the permission check of FREQ-JVMEM-009, with no check of the feature's own, as the first test of problem 5 in section 4.1 checks (FREQ-JVMEM-009).
  10. The item MUST add the test of a grant row left behind that problem 7 in section 4.1 names, with its four places, in which the warm-up of the permissions cache runs after the row is in the auth tables (FREQ-JVMEM-016, [DEC-JVMEM-0006](decisions/DEC-JVMEM-0006-a-grant-left-on-the-view-is-documented.md)).
  11. The item MUST leave every other table of `system_views` and every other surface that FREQ-JVMEM-011 names as they were, as the test of problem 4 in section 4.1 and the unchanged suites of Apache Cassandra that exit criterion 5 of the [delivery plan](delivery-plan.md#milestone-1-the-view) names check. The test of problem 4 expects each name of a list that is written in the test, which holds every table of `system_views` on a node of the line at the commit before this item is merged, and it takes no expected name from the running node.
  12. The item MUST add the reference page of the view under `docs/`, with every statement that FREQ-JVMEM-012, FREQ-JVMEM-013, FREQ-JVMEM-015, FREQ-JVMEM-016, FREQ-JVMEM-019 and FREQ-JVMEM-020 require, in the same pull request as the view class and the hook ([PRINCIPLE-077](../../process/principles.md#principle-077)).
  13. The documentation tests that problems 3, 6, 7, 8 and 10 in section 4.1 name MUST pass on the reference page as the item merges it (FREQ-JVMEM-012, FREQ-JVMEM-013, FREQ-JVMEM-015, FREQ-JVMEM-016, FREQ-JVMEM-019, FREQ-JVMEM-020).
  14. The documentation tests MUST also check that the reference page gives the type of each column as `system_virtual_schema.columns` of a test node has it, gives a meaning for each column, names `HEAP` and `NON_HEAP` as the two values of `type`, and states the meaning of -1 in `max_bytes` and the meaning of null in the three size columns (FREQ-JVMEM-012).
  15. The view class MUST take the memory pools of a read through one place that a test of the project can replace with pools of its own, in a unit test and on one node of the cluster of an in-JVM distributed test, so that the tests of FREQ-JVMEM-005, FREQ-JVMEM-006, FREQ-JVMEM-007, FREQ-JVMEM-014 and FREQ-JVMEM-018 in both items can run.
  16. The item MUST merge the view class, the hook, its tests and the reference page in one pull request, so that the line never holds the view without them ([PRINCIPLE-020](../../process/principles.md#principle-020)).
  17. The code of the view class that builds the rows of a read MUST NOT catch what a call that it makes to the JVM throws, of whatever kind, an out of memory error included (FREQ-JVMEM-018).
  18. The view class MUST make none of the calls to the JVM that a read makes while the class is loaded or while an object of it is built, in its static initialiser or in its constructor, which a unit test checks for a call that the constructor makes through the place of criterion 15, by building an object of the view class while that place throws at every call and expecting no throw, and which the review of the view class against this criterion shows for the rest (FREQ-JVMEM-001).
  19. The item MUST add one in-JVM distributed test that supplies a memory pool through the place of criterion 15 on one node of a cluster of 2 nodes, reads the view through CQL on both nodes, and expects the row of that pool on that node and no row of it on the other node (FREQ-JVMEM-007).
  20. When a read builds the row of a memory pool that the test supplies and whose `getUsage` returns a `MemoryUsage` object of other sizes at each call, the three sizes of that row MUST be the used, the committed and the maximum size of one of those objects (FREQ-JVMEM-005).
  21. The node MUST offer no setting, no system property, no MBean, no statement and no command through which the memory pools of a read are replaced, so that only the code of a test reaches the place of criterion 15 (FREQ-JVMEM-007, FREQ-JVMEM-011).
  22. If a call that the view makes to the JVM throws while a unit test calls directly the code of the view class that builds the rows of a read, then what reaches the test MUST be the object that the call threw, and no other throwable that holds that object as its cause (FREQ-JVMEM-018).
  23. When a statement writes to the view or truncates it, the node MUST refuse the statement with the error of Apache Cassandra that FREQ-JVMEM-010 names, as the second test of problem 5 in section 4.1 checks (FREQ-JVMEM-010).
  24. When a statement grants or revokes a permission on the view by name, the node MUST handle it as FREQ-JVMEM-017 says, with no check of the feature's own, as the first test of problem 7 in section 4.1 checks (FREQ-JVMEM-017).
  25. The view class MUST read no setting of the node, which the review of the view class against this criterion shows (FREQ-JVMEM-001).
- **Depends on:** none
- **Line:** chronitondb-sandbox
- **Milestone:** 1
- **Parallel:** No. It is the first item, and item 2 waits for it.
- **Item type:** build item

The design record of this item also answers the six lines that section 11 leaves to it. Among them, its `Exceptions` row names PRINCIPLE-003 and PRINCIPLE-089, as item 4 of the outcome of [DEC-JVMEM-0001](decisions/DEC-JVMEM-0001-jvm-memory-pools-view-has-no-switch.md) requires, and it names the test runs that hold the two tests of item 3 of the outcome of [DEC-JVMEM-0003](decisions/DEC-JVMEM-0003-jvm-memory-pools-view-stays-at-normal-risk.md). It also names each test file or test data file of Apache Cassandra that pins a complete listing to which the view adds a line, with the lines that the item adds to it, as [PRINCIPLE-013](../../process/principles.md#principle-013) has it. Exit criterion 5 of the [delivery plan](delivery-plan.md#milestone-1-the-view) takes those added lines as the one change to a test of Apache Cassandra.

The criteria below ask for a test, or for a property of the view class, that section 4.1 does not name in these words. Each is needed by a feature requirement, which has a test that proves it ([PRINCIPLE-063](../../process/principles.md#principle-063)). Where no test can show a part of a criterion, its entry says what shows that part:

1. **Criterion 6.** Section 4.1 has a test read the view twice. Real pools often show the same sizes at two reads, so the test changes the usage of a pool of its own between the reads. A view that kept the values of the first read then fails.
2. **Criterion 7.** Problem 3 in section 4.1 names the two tests of FREQ-JVMEM-018 with an exception. The item adds the same two tests with an error of the JVM that is no out of memory error, because FREQ-JVMEM-018 and item 4 of section 2.5 cover both. No test of the feature throws an out of memory error: of that error the feature spec says only that it goes to Apache Cassandra's own handling.
3. **Criterion 8.** The test of problem 9 in section 4.1 looks for a thread and a scheduled task before any read, and for a kept value after a read. FREQ-JVMEM-008 holds whenever no statement reads the view, so the item looks for a thread and a scheduled task after a read too. A view that starts a thread at its first read then fails.
4. **Criterion 14.** The documentation test of problem 8 in section 4.1 compares names. FREQ-JVMEM-012 also names the type and the meaning of each column, the two values of `type` and the meanings of -1 and null, so the documentation tests check that the page holds each. A test can check that the page gives a meaning for a column. Whether it is the meaning that section 2.2 gives is read at the gate, exit criterion 8 of the [delivery plan](delivery-plan.md#milestone-1-the-view).
5. **Criterion 17.** FREQ-JVMEM-018 has the view catch nothing, of any kind. The tests of criterion 7 show it for an exception and for an error of the JVM that is no out of memory error. The test of criterion 22 shows for both that the view does not wrap what it passes on. No test of the feature throws an out of memory error, so for that error the review of the view class against this criterion shows it.
6. **Criterion 18.** A view class that makes no call to the JVM while it is loaded and built does not depend, at the start of a node, on what a JDK or a collector reports for its memory pools (problem 1, [DEC-JVMEM-0003](decisions/DEC-JVMEM-0003-jvm-memory-pools-view-stays-at-normal-risk.md)). The unit test shows one part of that: the constructor makes no call through the place of criterion 15. It does not show two parts. Where that place is on the view class or is set through it, the class is loaded, and its static initialiser has run, before the test can make the place throw. And the test does not see a call that goes to `java.lang.management` past that place. Both parts are shown by the review of the view class against this criterion, which reads that its static initialiser and its constructor hold no call to `java.lang.management`. A view class that throws while a node builds it also fails every test that starts a node (problem 1 in section 4.1).
7. **Criterion 19.** Criterion 15 says that a test can replace the pools on one node of an in-JVM cluster, and item 2 rests on that. Every node of such a cluster runs in the JVM of the test, with a class loader of its own for the classes that the nodes do not share (fact F of the [delivery plan](delivery-plan.md#6-test-plan)). The nodes share a class that carries the annotation `Shared` in the package `org.apache.cassandra` or below it, a class that the test names when it builds its cluster, and a class that one filter of a library takes. The view class lies in `org.chronitondb.virtual`, which that scan does not reach, so each node loads the view class for itself unless that filter takes it. The filter is in a library that the checkout of the line does not hold, and it was not read. The test of criterion 19 shows that a pool given to one node is not seen on the other node, in the item that builds the place, before item 2 starts.
8. **Criterion 20.** Problem 2 names the three sizes of a row taken from two readings as a wrong value. The unit test of problem 2 in section 4.1 builds a row from one `MemoryUsage` object, and a view that asks the pool for its usage once for each column passes it. A pool that returns an object of other sizes at each call fails such a view.
9. **Criterion 21.** The place of criterion 15 is there for tests alone. A node on which an operator or a client could replace the pools would show sizes that are not its JVM's, against FREQ-JVMEM-007. It is shown by the review of the view class against this criterion and by exit criterion 7 of the delivery plan, which looks in the merged code for behaviour that no requirement asks for.
10. **Criterion 11.** Section 4.1 has the test of problem 4 expect every table of Apache Cassandra. A test that took those names from the running node would pass when the hook dropped a table from the list of `system_views`, which is problem 4. So the names are written in the test, from the line at the commit before this item is merged. A table that a later import adds is not on the written list and does not fail the test.
11. **Criterion 22.** The tests of criterion 7 read the view through CQL. There a test sees a throwable that holds what the call threw, in itself or among its causes, and that is the same for a view that passes on what was thrown and for a view that catches it and throws a throwable of its own with what it caught as the cause. FREQ-JVMEM-018 forbids the second view. A unit test that calls the code of the view class directly gets what that code threw, so it expects the object itself.
12. **Criterion 25.** FREQ-JVMEM-001 has the node hold the view whatever its configuration, and the tests start a node with the default configuration only. A view class that reads no setting is built the same way under every configuration. No test shows that a class reads no setting, so the review of the view class against this criterion shows it.

Criterion 15 is the one interface between the two items. Needed by the tests of both items: no JVM gives a pool a usage of the test's choosing, lists a pool with no usage, or throws from a call of the view, when a test asks for it. So those tests need pools of their own. How the view class offers that place is the design record's choice.

### Item 2: End to end tests of the view on a cluster

- **Delivers:** the proof on a started cluster of FREQ-JVMEM-001, FREQ-JVMEM-002, FREQ-JVMEM-003, FREQ-JVMEM-004, FREQ-JVMEM-005, FREQ-JVMEM-006, FREQ-JVMEM-007, FREQ-JVMEM-008, FREQ-JVMEM-009, FREQ-JVMEM-010, FREQ-JVMEM-011, FREQ-JVMEM-012, FREQ-JVMEM-013, FREQ-JVMEM-014, FREQ-JVMEM-015, FREQ-JVMEM-016, FREQ-JVMEM-017, FREQ-JVMEM-018, FREQ-JVMEM-019, FREQ-JVMEM-020. It builds no part of the view and no part of the reference page: item 1 builds both.
- **Acceptance criteria:**
  1. When a cluster of 2 nodes starts in an in-JVM distributed test, each node MUST list the view in `system_virtual_schema` with the columns and the types of section 2.2 (FREQ-JVMEM-001).
  2. When a statement reads the whole view on a node of the cluster, the rows MUST be exactly one for each memory pool that the test reads from the same JVM, with the name, the type and the maximum of that pool (FREQ-JVMEM-002, FREQ-JVMEM-003, FREQ-JVMEM-004).
  3. When a node of the cluster has a memory pool that the test supplies, whose `getUsage` returns at each call a `MemoryUsage` object of 3 different sizes that no other call returns, a read of the view through CQL on that node MUST return the used, the committed and the maximum size of one of those objects, each in its own column and in bytes (FREQ-JVMEM-005).
  4. If a memory pool that the test supplies on a node of the cluster has a `MemoryUsage` object that defines no maximum, then a read of the view through CQL on that node MUST return -1 in `max_bytes` for that pool (FREQ-JVMEM-006).
  5. While a node of the cluster can exchange no message with the other node, that node MUST answer a read of the view with its rows (FREQ-JVMEM-007).
  6. When the test changes the usage of a memory pool that it supplies on a node of the cluster between two reads of the view, the second answer MUST hold the changed sizes, so that no value of the first read is kept (FREQ-JVMEM-007, FREQ-JVMEM-008).
  7. While no statement reads the view on the started cluster, both before the first read of the view and after a read has ended, each node MUST run no thread and no scheduled task of the feature (FREQ-JVMEM-008).
  8. When a role with no grant reads the view on a cluster with authentication and authorization on, the node MUST refuse the read (FREQ-JVMEM-009).
  9. When a superuser, a role granted `SELECT` on the view or a role granted `SELECT` on the keyspace `system_views` reads the view on that cluster, the node MUST answer with the rows of the view (FREQ-JVMEM-009).
  10. When an `INSERT`, an `UPDATE`, a `DELETE` or a `TRUNCATE` names the view on a node of the cluster, the node MUST refuse it with the error of Apache Cassandra that fact 8 gives, and the test sends each of the four (FREQ-JVMEM-010).
  11. When a node of the cluster lists the tables of `system_views`, the list MUST hold the view and each name of a list that is written in the test, each once, where the written list holds every table of `system_views` on a node of the line at the commit before item 1 is merged and takes no name from the running node (FREQ-JVMEM-011).
  12. When a statement reads a table of Apache Cassandra in `system_views` on a node of the cluster, the node MUST answer with no error, for each such table but those that the design record of the item names, each with the error that a read of it gives on a node of the line at the commit before item 1 is merged (FREQ-JVMEM-011).
  13. When a superuser grants `SELECT` and `AUTHORIZE` on the view by name to a role on a cluster with authentication and authorization on, lists the grants with `LIST ALL PERMISSIONS ON system_views.jvm_memory_pools NORECURSIVE` and sends `REVOKE ALL PERMISSIONS ON system_views.jvm_memory_pools` for that role, the listing MUST show both grants before the `REVOKE` and no row of the role after it (FREQ-JVMEM-016, FREQ-JVMEM-017).
  14. If a node of the cluster has a memory pool whose usage is null, which the test supplies through the place of criterion 15 of item 1, then a read of the view through CQL on that node MUST return the row of that pool with its name, its type and null in the three sizes (FREQ-JVMEM-014).
  15. If the call for the list of memory pools, or a call to the bean of a memory pool that the test supplies, throws an exception or an error of the JVM that is no out of memory error on a node of the cluster, then a read of the whole view and a read of another pool by its name, each run inside that node with no connection of a client, MUST each fail with a throwable that holds the class and the message of what was thrown, in itself or among its causes (FREQ-JVMEM-018, FREQ-JVMEM-019).
  16. When a client reads the whole view on a node of the cluster with a page size below the number of memory pools, while the JVM does not change its list of pools, the pages together MUST hold every memory pool exactly once (FREQ-JVMEM-002, FREQ-JVMEM-015).
  17. When a statement names 2 memory pools with `IN` on a node of the cluster, the node MUST return the row of each of the 2 pools (FREQ-JVMEM-002, FREQ-JVMEM-015).
  18. The validation tests MUST read the reference page as item 1 merged it and check it against a node of the cluster: the name of the view, each column name and each column type against `system_virtual_schema`, each value of `type` that a read returns against the two values the page names, and each CQL statement that the page gives for a node that has the view against the result the page states for such a node (FREQ-JVMEM-012, FREQ-JVMEM-013, FREQ-JVMEM-016, FREQ-JVMEM-020).
  19. When a node of the cluster has a memory pool that the test supplies and the other node has none, a read of the view through CQL on the other node MUST return no row of that pool (FREQ-JVMEM-007).
  20. The validation tests MUST check that the reference page as item 1 merged it holds each statement that FREQ-JVMEM-012, FREQ-JVMEM-013, FREQ-JVMEM-015, FREQ-JVMEM-016, FREQ-JVMEM-019 and FREQ-JVMEM-020 require of the documentation, in tests that are written from those requirements and not from the documentation tests of item 1.
  21. When a client sends `SELECT count(*)` on the view to a node of the cluster with a page size below the number of memory pools, while the JVM does not change its list of pools, the node MUST return the number of memory pools (FREQ-JVMEM-002, FREQ-JVMEM-015).
  22. When a test writes into the auth tables of a cluster, with authentication, authorization and the warm-up of the auth caches on, a grant row that names a table of `system_views` that no node has, and then starts a node of the cluster again, the cluster MUST show the four outcomes that problem 7 in section 4.1 gives for the four places of section 7.4: a statement of the role on another table passes its permission check, `LIST ALL PERMISSIONS` and `LIST ALL PERMISSIONS OF <role>` each list the row, the node starts again with the warm-up of the permissions cache passed, and `DROP ROLE` of the role removes the row (FREQ-JVMEM-016).
  23. When a role that is no superuser, to which a superuser granted `SELECT` and `AUTHORIZE` on the view by name, sends `GRANT SELECT ON system_views.jvm_memory_pools` to another role and then the `REVOKE` of that grant, on a cluster with authentication and authorization on, the node MUST accept both statements, so that the listing of section 7.4 shows the grant after the first and no row of the other role after the second (FREQ-JVMEM-017).
  24. If a role that is no superuser, which has `SELECT` on the view by name and no `AUTHORIZE` on the view or on a resource above it, sends a `GRANT` or a `REVOKE` of `SELECT` on the view on that cluster, then the node MUST refuse the statement with the error that it gives that role for the same statement on a table of Apache Cassandra in `system_views` on which the role has the same grants (FREQ-JVMEM-017).
- **Depends on:** 1
- **Line:** chronitondb-sandbox
- **Milestone:** 1
- **Parallel:** No. It starts when item 1 is merged.
- **Item type:** validation item

The tests of this item send their statements to a node of a started cluster. The tests of criterion 15 run their statements inside the node, as the coordinator of an in-JVM cluster does, with no connection of a client (fact G of the [delivery plan](delivery-plan.md#6-test-plan)). So they see what the read threw, and they assert nothing of what Apache Cassandra answers and logs on a client's connection for a failed read: item 4 of section 2.5 and section 4.1 say that no test of the feature covers that code. Criterion 15 does not tell a view that passes on what was thrown from a view that catches it and throws something of its own with what it caught as the cause. Criterion 17 of item 1 forbids the second, and the unit test of criterion 22 of item 1 catches it. No test of this item throws an out of memory error. Criteria 23 and 24 send a `GRANT` and a `REVOKE` as a role that is no superuser, with `AUTHORIZE` and without it (fact 19). A check of the feature's own on such a role would pass every test that sends them as a superuser, so criterion 13 alone does not show that the feature adds none.

## 2. Validation items

Milestone 1 has one validation item, item 2. Its tests are in-JVM distributed tests under `test/distributed/org/chronitondb/virtual/test/`, written from the feature requirements. No Python distributed test is planned: every criterion of item 2 is reached by a statement on a node of an in-JVM cluster, and none needs a node process or a tool of its own.

Every feature requirement has a validation test, which the gate of a milestone needs ([testing.md](../../process/testing.md#exit-criteria)). The limits of what a validation test on this line can show follow, each with what proves the rest:

1. **A node without the view.** No test on this line starts a node of an earlier release (problems 6 and 7 in section 4.1). So no validation test shows what a read, a listing or a `REVOKE` answers on such a node, and criterion 18 of item 2 runs no statement whose result the page gives for such a node. What a grant row left behind does needs no node of an earlier release: criterion 22 of item 2 tests the four places of section 7.4 on a cluster whose nodes do not have the table that the row names. Criterion 13 of item 2 runs the step of section 7.4 on a node that has the view. That the page states the answer of a node without the view is checked by criterion 20 of item 2 and by the documentation tests of item 1 (criterion 13 of item 1).
2. **What Apache Cassandra answers and logs for a failed read.** No test of the feature covers it (problem 3 in section 4.1). Criterion 15 of item 2 shows that the read fails with what was thrown, for both calls and for an exception and an error of the JVM. It takes what was thrown in the throwable that reaches the test or among its causes, so it does not tell a view that passes on what was thrown from a view that wraps it in a throwable of its own. That part of FREQ-JVMEM-018 is proven in item 1, by the unit test of criterion 22 of item 1, which expects the object itself. That the page states the answer, the log entries, the three commits and the one statement on an out of memory error is checked by criterion 20 of item 2 and by the documentation tests of item 1. No test of either item throws an out of memory error. That the view catches none is criterion 17 of item 1, which the review of the view class holds.
3. **More than one read.** That two reads hold two moments, and that a pool can be missing when the JVM changes its list between them, is the decided behaviour, and no test forbids it (problem 10 in section 4.1). Criteria 16, 17 and 21 of item 2 show that a paged statement, a statement with `IN` and a statement that aggregates with a page size take in every pool they ask for. They do not rest on the page giving a statement to run. That the page states the three cases, the one statement of exactly one read and the two consequences is checked by criterion 20 of item 2 and by the documentation tests of item 1.
4. **Another surface of the node.** A validation test runs on one build, so it cannot compare a table, an MBean, a metric or the output of a nodetool command with what Apache Cassandra shows. Criteria 11 and 12 of item 2 show that every table that `system_views` had at the commit before item 1 is merged is listed once and answers a read. The rest of FREQ-JVMEM-011 is proven by the tests of Apache Cassandra that run unchanged, which exit criterion 5 of the [delivery plan](delivery-plan.md#milestone-1-the-view) names: its unit tests of the virtual tables, its test that compares the MBeans of a node, the metrics among them, with those of four earlier releases, its unit tests of the nodetool commands, its unit tests of grants and its two in-JVM distributed tests that read tables of `system_views` on a cluster (facts D, E and H of the delivery plan). It is also proven by the hook being the one line of Apache Cassandra that the feature changes (section 2.7), which the required check of the delta register holds on each pull request.
5. **The meanings on the page.** Criterion 18 of item 2 compares names, types and the values of `type` with the cluster. Criterion 20 of item 2 and criterion 14 of item 1 check that the page gives a meaning for each column and states the meaning of -1 and of null. No test tells whether a meaning on the page is the one that section 2.2 gives. That is read at the gate, exit criterion 8 of the delivery plan.
6. **One JVM for both nodes.** Both nodes of an in-JVM cluster run in the JVM of the test (fact F of the delivery plan), so both have the same memory pools of the JVM. No validation test shows two nodes whose JVMs report different pools. Criterion 19 of item 2 shows that a node does not answer with a pool that only the other node was given, and criterion 5 that a node answers while it can exchange no message. The rest of FREQ-JVMEM-007 is shown by the review of the view class against that requirement, which reads that its values come from `java.lang.management` in its own process and from nowhere else.
7. **What the feature keeps in memory.** Criterion 6 of item 2 shows that a second read does not answer from the values of the first. It does not catch a view that keeps the values of each read and writes over them at the next read. A test of item 2 could look inside a node, as the tests of criteria 7 and 15 of item 2 do, so what a test can reach is not the reason that item 2 has no such check. The reason is that the check looks at what the object of the view class holds after a read, and a node of a cluster holds an object of the same class as a test node does. A check on the cluster would repeat the test of problem 9 in section 4.1, which is in item 1 (criterion 8 of item 1), and show nothing more. So that the feature holds no value of a memory pool after a read is proven by that test of item 1 alone.
8. **One configuration.** The validation tests start their cluster with the configuration that the in-JVM distributed tests set. So criterion 1 of item 2 shows that a node holds the view under that configuration. That a node holds it whatever its configuration rests on criterion 25 of item 1: a view class that reads no setting is built the same way under every configuration.

## 3. Traceability

| FREQ | Items | Validation item |
|---|---|---|
| FREQ-JVMEM-001 | Item 1, criteria 1, 2, 3, 18 and 25 | Item 2, criterion 1, within limit 8 of section 2 of this plan |
| FREQ-JVMEM-002 | Item 1, criteria 4 and 5 | Item 2, criteria 2, 16, 17 and 21 |
| FREQ-JVMEM-003 | Item 1, criterion 4 | Item 2, criterion 2 |
| FREQ-JVMEM-004 | Item 1, criterion 4 | Item 2, criterion 2 |
| FREQ-JVMEM-005 | Item 1, criteria 4, 15 and 20 | Item 2, criterion 3 |
| FREQ-JVMEM-006 | Item 1, criteria 4 and 15 | Item 2, criterion 4 |
| FREQ-JVMEM-007 | Item 1, criteria 4, 6, 15, 19 and 21 | Item 2, criteria 5, 6 and 19, within limit 6 of section 2 of this plan |
| FREQ-JVMEM-008 | Item 1, criterion 8 | Item 2, criteria 6 and 7, within limit 7 of section 2 of this plan |
| FREQ-JVMEM-009 | Item 1, criterion 9 | Item 2, criteria 8 and 9 |
| FREQ-JVMEM-010 | Item 1, criterion 23 | Item 2, criterion 10 |
| FREQ-JVMEM-011 | Item 1, criteria 2, 11 and 21 | Item 2, criteria 11 and 12, within limit 4 of section 2 of this plan |
| FREQ-JVMEM-012 | Item 1, criteria 12, 13 and 14 | Item 2, criteria 18 and 20, within limit 5 of section 2 of this plan |
| FREQ-JVMEM-013 | Item 1, criteria 12 and 13 | Item 2, criteria 18 and 20, within limit 1 of section 2 of this plan |
| FREQ-JVMEM-014 | Item 1, criteria 4 and 15 | Item 2, criterion 14 |
| FREQ-JVMEM-015 | Item 1, criteria 12 and 13 | Item 2, criteria 16, 17, 20 and 21, within limit 3 of section 2 of this plan |
| FREQ-JVMEM-016 | Item 1, criteria 10, 12 and 13 | Item 2, criteria 13, 18, 20 and 22, within limit 1 of section 2 of this plan |
| FREQ-JVMEM-017 | Item 1, criterion 24 | Item 2, criteria 13, 23 and 24 |
| FREQ-JVMEM-018 | Item 1, criteria 7, 15, 17 and 22 | Item 2, criterion 15, within limit 2 of section 2 of this plan |
| FREQ-JVMEM-019 | Item 1, criteria 12 and 13 | Item 2, criteria 15 and 20, within limit 2 of section 2 of this plan |
| FREQ-JVMEM-020 | Item 1, criteria 12 and 13 | Item 2, criteria 18 and 20, within limit 2 of section 2 of this plan |
