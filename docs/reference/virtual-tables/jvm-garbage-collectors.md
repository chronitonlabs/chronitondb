---
title: JVM garbage collectors view
description: The virtual table system_views.jvm_garbage_collectors, its columns, who may read it, what a failed read answers, and the step before moving back.
---
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

# system_views.jvm_garbage_collectors

The virtual table `system_views.jvm_garbage_collectors` shows the garbage collectors of the JVM of the node that answers the read. It has one row for each garbage collector that the JVM lists, such as `G1 Young Generation` and `G1 Old Generation` on a node that runs the G1 collector. It is read only, and it is present on every node of a release that has it, whatever the node's configuration. It has no setting.

The table holds the values of the moment of the read. They are the values that the JVM's own MBeans `java.lang:type=GarbageCollector,name=<collector>` show over JMX as `CollectionCount` and `CollectionTime`. A node reports its own JVM only, and sends no message to another node to answer.

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in BCP 14 (RFC 2119, RFC 8174) when, and only when, they appear in all capitals, as shown here.

## Contents

- [Columns](#columns)
- [Example](#example)
- [One statement and its reads](#one-statement-and-its-reads)
- [Who may read the table](#who-may-read-the-table)
- [When a read fails](#when-a-read-fails)
- [Nodes without the table](#nodes-without-the-table)
- [Moving back](#moving-back)

## Columns

| Column | Type | Kind | Meaning |
|---|---|---|---|
| `name` | `text` | partition key | The name of the garbage collector as the JVM reports it, unchanged. For example `G1 Young Generation`, `ZGC Cycles` or `Shenandoah Pauses`. |
| `collection_count` | `bigint` | regular | The number of collections the collector has run since the JVM started. |
| `collection_time_millis` | `bigint` | regular | The approximate total time of those collections since the JVM started, in milliseconds. |

The meanings of the two values are those that the Java SE documentation of `java.lang.management.GarbageCollectorMXBean` gives for `getCollectionCount` and `getCollectionTime`. Both values only grow while the JVM runs. The time can stay the same while the count grows, when a collection is very short. What the JVM counts as a collection and as its time depends on the collector: for a collector that works beside the threads of the node, the time need not be a time in which those threads were stopped.

One value has a meaning of its own:

1. **-1 in `collection_count` or `collection_time_millis`.** The JVM leaves that value undefined for the collector. The column shows -1 as the JVM's bean returns it.

The rows come back in the byte order of the UTF-8 text of the name, as the rows of `system_views.thread_pools` do. In that order an upper case letter comes before every lower case letter.

Which collectors a node has depends on its JDK and the collector it runs. The table shows whatever the JVM reports. If the JVM lists more than one garbage collector under one name, every read of the table fails, as [When a read fails](#when-a-read-fails) says.

## Example

A sample of a read on a node with OpenJDK 17 and the G1 collector. The collectors and their values differ from node to node and from read to read:

```
cqlsh> SELECT * FROM system_views.jvm_garbage_collectors;

 name                | collection_count | collection_time_millis
---------------------+------------------+------------------------
 G1 Old Generation   |                0 |                      0
 G1 Young Generation |              412 |                   3180
```

A read of one collector names it:

```
SELECT collection_count, collection_time_millis FROM system_views.jvm_garbage_collectors WHERE name = 'G1 Young Generation';
```

A tool that wants the time spent in collections over a period reads the table twice and takes the difference of each row.

## One statement and its reads

A read is one run of the code that builds the rows of the table. Every read builds the row of every garbage collector that the JVM lists then, also a read of one collector by its name. The node then takes from those rows the ones the statement asks for. The table is read afresh at every read and keeps nothing from one read to the next.

One statement can be answered from more than one read, for example a statement whose rows a client fetches over more than one page, or one that names more than one collector with `IN`. The rows of such a statement can hold values of different moments, and a collector can be missing if the JVM changes its list between two reads. The [page of the memory pools view](jvm-memory-pools.md#one-statement-and-its-reads) lists the cases, which hold for this table too, since both tables are built the same way.

A tool that needs the values of one moment SHOULD send `SELECT * FROM system_views.jvm_garbage_collectors` with no page size, or with a page size above the number of collectors.

## Who may read the table

The table follows the permission check that every table of `system_views` has. A superuser may read it. Another role needs `SELECT` on the table or on the keyspace `system_views`. A grant of `SELECT` on all keyspaces does not let a role read it, since such a grant reaches no table of a system keyspace, and nor does a grant on another table of `system_views`. A statement that writes to the table is refused with `Modification is not supported by table system_views.jvm_garbage_collectors`, and `TRUNCATE` with `Truncation is not supported by table system_views.jvm_garbage_collectors`.

The rows hold counts and times of the node's JVM and no user data.

## When a read fails

The table catches nothing that a call to the JVM throws while a read builds its rows. That holds for the call for the list of collectors and for each call to the bean of one collector, and for an exception as for an error of the JVM. What was thrown goes to the node's own handling of a failed request, which this table does not change.

An exception, or an error of the JVM that is no out of memory error, that the JVM raises for one garbage collector fails every read of the table while it lasts, a read of another collector by its name included. The reason is that every read builds the row of every collector. A JVM that lists more than one garbage collector under one name fails every read too, so that no collector is hidden behind another of the same name. The client then gets the server error `java.lang.IllegalStateException: the JVM lists more than one garbage collector named <name>`.

A failed read of this table reaches the client and the log as a failed read of `system_views.jvm_memory_pools` does, since both go to the same handling of a failed request. The [page of the memory pools view](jvm-memory-pools.md#when-a-read-fails) gives what the client gets and what the node logs for each kind of failure, and the code it was read in. A tool that polls the table while a read fails adds ERROR entries to the log while the fault lasts. The entries hold what was thrown and no user data.

## Nodes without the table

A node of a release without the table, such as a node of an earlier release or of Apache Cassandra®, refuses a read of it with `table jvm_garbage_collectors does not exist`, as it refuses a read of any table it does not have. During a rolling upgrade a client sees the rows or the refusal by the node its driver sends the statement to. Until every node has the table, a client that needs it sends the read to a node that has it.

A node without the table also refuses a `GRANT` or a `REVOKE` that names it, with `Resource <table system_views.jvm_garbage_collectors> doesn't exist`.

## Moving back

Moving back to an earlier release or to Apache Cassandra needs one step for this table, and only where a grant names it. The table leaves no file, no schema row and no setting behind.

**The step.** Before the last node that has the table moves back, an operator lists the grants that name the table and revokes every permission of each. The operator MUST send both statements as a superuser, to a node that has the table:

1. List the grants of every role on the table:

   ```
   LIST ALL PERMISSIONS ON system_views.jvm_garbage_collectors NORECURSIVE;
   ```

2. For each role the listing shows, revoke every permission:

   ```
   REVOKE ALL PERMISSIONS ON system_views.jvm_garbage_collectors FROM <role>;
   ```

Once no node has the table, no node accepts a `REVOKE` that names it. A grant on the keyspace `system_views` or on all keyspaces names no table of this feature and needs no step.

**A grant left behind.** A grant that the operator did not revoke stays as a row of the auth tables. What such a row does on a node without the table is what the [page of the memory pools view](jvm-memory-pools.md#moving-back) says of a grant left behind on that table, for the code that page names. It is removed by `DROP ROLE` of its role, or by a `REVOKE` on a node that has the table.
