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

# system_views.jvm_memory_pools

The virtual table `system_views.jvm_memory_pools` shows the memory pools of the JVM of the node that answers the read. It has one row for each memory pool that the JVM lists, such as the old generation, the metaspace and the code cache. It is read only, and it is present on every node of a release that has it, whatever the node's configuration. It has no setting.

The table holds the values of the moment of the read. They are the values that the JVM's own MBeans `java.lang:type=MemoryPool,name=<pool>` show over JMX. A node reports its own JVM only, and sends no message to another node to answer.

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
| `name` | `text` | partition key | The name of the memory pool as the JVM reports it, unchanged. For example `G1 Old Gen`, `Metaspace` or `CodeHeap 'non-nmethods'`. |
| `type` | `text` | regular | `HEAP` for a pool of heap memory, `NON_HEAP` for any other pool. These are the two values of the column, and the text JMX shows for the pool's `Type` attribute. |
| `used_bytes` | `bigint` | regular | The memory the pool uses at the read, in bytes. |
| `committed_bytes` | `bigint` | regular | The memory that is guaranteed to be available to the JVM for the pool, in bytes. It is never less than the used size, and it can grow or shrink over time. |
| `max_bytes` | `bigint` | regular | The most memory the JVM can use for the pool, in bytes. Where it is defined it can change over time. It is no promise that the memory can be had: the JVM can fail to get memory above the committed size while the used size is still below the maximum. |

The meanings of the three sizes are those that the Java SE documentation of `java.lang.management.MemoryUsage` gives for used, committed and max. The three sizes of one row come from one reading of the pool, so they belong to one moment.

Two values of the size columns have a meaning of their own:

1. **-1 in `max_bytes`.** The JVM reports a usage for the pool and defines no maximum for it.
2. **null in `used_bytes`, `committed_bytes` and `max_bytes`.** The JVM lists the pool and reports no usage for it, which the Java SE documentation calls a pool that is not valid. The row still holds the name and the type of the pool.

The rows come back in the byte order of the UTF-8 text of the name, as the rows of `system_views.thread_pools` do. In that order an upper case letter comes before every lower case letter.

Which pools a node has depends on its JDK and its garbage collector. The table shows whatever the JVM reports. If the JVM lists more than one memory pool under one name, every read of the table fails, as [When a read fails](#when-a-read-fails) says.

## Example

A read on a node with OpenJDK 17, the G1 collector and a 512 MiB heap:

```
cqlsh> SELECT * FROM system_views.jvm_memory_pools;

 name                               | committed_bytes | max_bytes  | type     | used_bytes
------------------------------------+-----------------+------------+----------+------------
 CodeHeap 'non-nmethods'            |         2555904 |    5840896 | NON_HEAP |    1177984
 CodeHeap 'non-profiled nmethods'   |         2555904 |  122908672 | NON_HEAP |     482432
 CodeHeap 'profiled nmethods'       |         2555904 |  122908672 | NON_HEAP |    2332800
 Compressed Class Space             |         1245184 | 1073741824 | NON_HEAP |    1173816
 G1 Eden Space                      |        28311552 |         -1 | HEAP     |   22020096
 G1 Old Gen                         |       508559360 |  536870912 | HEAP     |     970752
 G1 Survivor Space                  |               0 |         -1 | HEAP     |          0
 Metaspace                          |        10027008 |         -1 | NON_HEAP |    9829624
```

A read of one pool names it:

```
SELECT used_bytes, max_bytes FROM system_views.jvm_memory_pools WHERE name = 'G1 Old Gen';
```

## One statement and its reads

A read is one run of the code that builds the rows of the table. Every read builds the row of every memory pool that the JVM lists then, also a read of one pool by its name. The node then takes from those rows the ones the statement asks for. The table is read afresh at every read and keeps nothing from one read to the next.

One statement can be answered from more than one read. These are the cases that were read in the code. They are not the whole list:

1. **Pages a client fetches.** A statement whose rows a client fetches over more than one page is at least one read for each page. Each page starts after the last name that the page before returned.
2. **Pages the node fetches for an aggregate.** A statement that aggregates, such as `SELECT sum(used_bytes) FROM system_views.jvm_memory_pools`, and that the client sends with a page size, is fetched in pages of that size inside the node. Each of those pages is at least one read. A page that comes back full does not end the statement, so such a statement is more than one read where the page size is not above the number of pools.
3. **Several names.** A statement that names more than one pool, such as one with `WHERE name IN ('G1 Eden Space', 'G1 Old Gen')`, is at least one read for each name. Where such a statement is also fetched in pages or aggregates, cases 1 and 2 hold for it too, and one page of it can hold rows of more than one read.

One statement was read in the code as exactly one read: `SELECT * FROM system_views.jvm_memory_pools`, sent with no page size or with a page size above the number of pools. For a statement that is neither that one nor one of the three cases, this page does not say how many reads answer it.

For a statement that is answered from more than one read:

1. **Different moments.** Its rows can hold values of different moments, as far apart as its reads are. A sum over them mixes those moments, whether a client or the node adds them up.
2. **A pool can be missing.** While the JVM does not change its list of pools, the reads of a statement of case 1 or case 2 together give every pool that the statement asks for once. If the JVM changes its list between two reads, a pool can be missing from the rows of the statement, or from the value the node computes over them.

A tool that needs the sizes of one moment SHOULD send `SELECT * FROM system_views.jvm_memory_pools` with no page size, or with a page size above the number of pools.

## Who may read the table

The table follows the permission check that every table of `system_views` has. A superuser may read it. Another role needs `SELECT` on the table, on the keyspace `system_views` or on all keyspaces. A statement that writes to the table is refused with `Modification is not supported by table system_views.jvm_memory_pools`, and `TRUNCATE` with `Truncation is not supported by table system_views.jvm_memory_pools`.

The rows hold sizes of the node's JVM and no user data.

## When a read fails

The table catches nothing that a call to the JVM throws while a read builds its rows. That holds for the call for the list of pools and for each call to the bean of one pool, and for an exception as for an error of the JVM. What was thrown goes to the node's own handling of a failed request, which this table does not change.

An exception, or an error of the JVM that is no out of memory error, that the JVM raises for one memory pool fails every read of the table while it lasts, a read of another pool by its name included. The reason is that every read builds the row of every pool. A JVM that lists more than one memory pool under one name fails every read too, with the server error `java.lang.IllegalStateException: the JVM lists more than one memory pool named <name>`, so that no pool is hidden behind another of the same name.

For a statement that a client sends, where no cause of what was thrown is an out of memory error, the node answers and logs as follows:

1. **Answered.** An exception is answered with a server error whose message is the class name and the message of the exception, in the form that Java's `toString` gives. An error of the JVM that is no out of memory error is answered with a server error of the same form.
2. **Logged.** The node logs an exception at ERROR, each time with its stack trace: in two log entries for a statement that the client sends as text, as `cqlsh` does, and in one for a prepared statement. It logs an error of the JVM that is no out of memory error once with its stack trace, at ERROR, or at DEBUG where the address of the client lies in a subnet that the setting `client_error_reporting_exclusions` lists. Each entry is logged for a request of a client that fails, so a tool that polls the table adds ERROR entries to the log while the fault lasts. The entries hold what was thrown and no user data.

An out of memory error during a read of the table goes to the node's own handling of an out of memory error, as on any request.

What the node answers and logs was read in the code of three commits: ChronitonDB `chronitondb-sandbox` at `ffa1bc742d`, its base, Apache Cassandra `cassandra-5.0` at `76550e9314`, and Apache Cassandra `cassandra-5.0` at `47227d98bf`. None of the three commits is a release. This page says what the node answers and logs for the code of those three commits, and for no other code. A release is cut from another commit, so it is other code, and so is another release of Apache Cassandra.

## Nodes without the table

A node of a release without the table, such as a node of an earlier release or of Apache Cassandra, refuses a read of it with `table jvm_memory_pools does not exist`, as it refuses a read of any table it does not have. During a rolling upgrade a client sees the rows or the refusal by the node its driver sends the statement to. Until every node has the table, a client that needs it sends the read to a node that has it.

A node without the table also refuses a `GRANT` or a `REVOKE` that names it, with `Resource <table system_views.jvm_memory_pools> doesn't exist`.

## Moving back

Moving back to an earlier release or to Apache Cassandra needs one step for this table, and only where a grant names it. The table leaves no file, no schema row and no setting behind.

**The step.** Before the last node that has the table moves back, an operator lists the grants that name the table and revokes every permission of each. The operator MUST send both statements as a superuser, to a node that has the table:

1. List the grants of every role on the table:

   ```
   LIST ALL PERMISSIONS ON system_views.jvm_memory_pools NORECURSIVE;
   ```

   The node accepts this listing only from a superuser or from a role that has `DESCRIBE` on all roles.

2. For each role the listing shows, revoke every permission:

   ```
   REVOKE ALL PERMISSIONS ON system_views.jvm_memory_pools FROM <role>;
   ```

   A grant on the table can hold any permission of a table, such as `SELECT` or `AUTHORIZE`, so `ALL PERMISSIONS` revokes each. The node accepts a `REVOKE` only from a role that has `AUTHORIZE` and every permission the statement revokes, and a superuser has them all.

Once no node has the table, no node accepts a `REVOKE` that names it, and a node without it refuses the listing too. A grant on the keyspace `system_views` or on all keyspaces names no table of this feature and needs no step.

**A grant left behind.** A grant that the operator did not revoke stays as a row of the auth tables, and so does one given on a node that still had the table after the operator revoked the others. Nothing refuses a grant on the table and nothing removes one by itself. For the code of the three commits named below, such a row does this on a node without the table:

1. It gives its role nothing. A permission check reads only the row of the resource a statement names, and no statement on such a node can name the table.
2. `LIST ALL PERMISSIONS` and `LIST ALL PERMISSIONS OF <role>` still list it.
3. The warm-up of the permissions cache at the start of a node, which runs only where the setting `auth_cache_warming_enabled` is on, reads it and goes on.
4. It gives its role its permissions on the table again when a node gets the table back.

It is removed by `DROP ROLE` of its role, which removes every grant row of the role, or by a `REVOKE` on a node that has the table.

What a row left behind does was read in the code of three commits: ChronitonDB `chronitondb-sandbox` at `ffa1bc742d`, its base, Apache Cassandra `cassandra-5.0` at `76550e9314`, and Apache Cassandra `cassandra-5.0` at `47227d98bf`. None of the three commits is a release. This page says what a row left behind does for the code of those three commits, and for no other code. An earlier release of the line is other code, since it is cut from another commit, and so is another release of Apache Cassandra. An operator who moves back to either has the step above and no statement on a row left behind.
