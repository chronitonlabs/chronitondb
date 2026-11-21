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

# DEC-JVMEM-0004. The view is named jvm_memory_pools and its size columns end in _bytes

| Field | Value |
|---|---|
| Document type | Record (ISO/IEC/IEEE 15289), MADR |
| Status | Accepted |
| Date | 2026-11-20 |
| Deciders | The maintainers |
| References | Issue #161, the [feature spec](../feature-spec.md), [PRINCIPLE-057](../../../process/principles.md#principle-057), [PRINCIPLE-079](../../../process/principles.md#principle-079), [PRINCIPLE-082](../../../process/principles.md#principle-082) |
| Areas | observability |
| Supersedes | None |

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in BCP 14 (RFC 2119, RFC 8174) when, and only when, they appear in all capitals, as shown here.

## Contents

- [Context and problem statement](#context-and-problem-statement)
- [Considered options](#considered-options)
- [Decision outcome](#decision-outcome)
  - [Consequences](#consequences)
- [More information](#more-information)

## Context and problem statement

The feature adds one virtual table to `system_views`, with a column for the name of a memory pool of the JVM, one for its type and three for its sizes. An operator writes the name of the table and of each column in every statement that reads the view. A name of the project's own that a release has shipped is not renamed or removed within a line, and a column of a result cannot carry two names ([PRINCIPLE-082](../../../process/principles.md#principle-082)). So the names had to be settled before the view is built.

## Considered options

1. `system_views.jvm_memory_pools`, with the columns `name`, `type`, `used_bytes`, `committed_bytes` and `max_bytes`.
2. `system_views.memory_pools`, with the same five columns.

## Decision outcome

Chosen option: "`system_views.jvm_memory_pools`", because the name says whose pools the view shows, as [PRINCIPLE-079](../../../process/principles.md#principle-079) asks of a name. A node has other pools, such as its thread pools, which `system_views.thread_pools` shows, and its buffer pools. With `jvm` in the name an operator does not take the view for one of those.

1. The table MUST be named `jvm_memory_pools` and MUST stand in the keyspace `system_views`.
2. Its columns MUST be named `name`, `type`, `used_bytes`, `committed_bytes` and `max_bytes`.
3. The three size columns hold bytes and say so in their names.

The column names follow the tables `system_views` already has, which is evidence for the choice and not its reason. The key column of `system_views.thread_pools` is `name`: `ThreadPoolsTable.ThreadPoolsTable`, `src/java/org/apache/cassandra/db/virtual/ThreadPoolsTable.java:40`, which sets the key column at line 45, ChronitonDB chronitondb-sandbox at `ffa1bc742d`. The size columns of `system_views.caches` are `capacity_bytes` and `size_bytes`: `CachesTable.CAPACITY_BYTES` and `CachesTable.SIZE_BYTES`, `src/java/org/apache/cassandra/db/virtual/CachesTable.java:30` and line 31, the same tree. Both stand at the same lines in Apache Cassandra cassandra-5.0 at `76550e9314`, the base of the line, and at `47227d98bf`. In Apache Cassandra cassandra-6.0 at `a02931dea8` and trunk at `45c325a01b` the two names of `CachesTable` stand at lines 33 and 34, and the class `ThreadPoolsTable` is gone, so the key column of `thread_pools` is not verified there. The reason for the unit in the name is that an operator who reads one row knows what the number counts without the documentation.

### Consequences

- Good: an operator sees from the name that the view shows the JVM's memory pools, and from each size column that it holds bytes.
- Good: the names read like those of the tables beside the view.
- Bad: the name is longer to type than `memory_pools`.
- Bad: the names are kept for the whole line once a release ships them. A better name found later can only be added beside the table name, and a column keeps its name.

## More information

- The [feature spec](../feature-spec.md), section 2.2 for the table and its columns.
- [DEC-JVMEM-0005](DEC-JVMEM-0005-type-column-shows-heap-and-non-heap-as-jmx-does.md) for the values of the `type` column.
