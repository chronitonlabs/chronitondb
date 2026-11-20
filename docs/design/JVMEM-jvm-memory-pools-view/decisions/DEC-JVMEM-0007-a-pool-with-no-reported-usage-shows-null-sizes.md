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

# DEC-JVMEM-0007. A memory pool whose usage the JVM does not report shows null in its three sizes

| Field | Value |
|---|---|
| Document type | Record (ISO/IEC/IEEE 15289), MADR |
| Status | Accepted |
| Date | 2026-11-20 |
| Deciders | The maintainers |
| References | Issue #161, the [feature spec](../feature-spec.md), [DEC-JVMEM-0002](DEC-JVMEM-0002-a-pool-with-no-maximum-shows-minus-one.md), [PRINCIPLE-056](../../../process/principles.md#principle-056), [PRINCIPLE-082](../../../process/principles.md#principle-082) |
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

The view takes the three sizes of a row from the `java.lang.management.MemoryUsage` object that `MemoryPoolMXBean.getUsage` returns for the memory pool. The Java SE documentation of that method says it returns null for a memory pool that is not valid, and `MemoryPoolMXBean.isValid` says a pool becomes invalid once the JVM removes it from the memory system. The JVM can still list such a pool, and its name and its type can still be read. It had to be settled what the view shows for it.

No way was found for an operator or a client to make a JVM invalidate a pool on a running node. The case is one the Java interface allows, so the view needs a stated answer for it.

## Considered options

1. A row with the name and the type of the pool, and null in `used_bytes`, `committed_bytes` and `max_bytes`.
2. No row for that pool.
3. No handling. The read then ends in a server error, for every read of the view while the JVM lists such a pool.

## Decision outcome

Chosen option: "A row with null in the three sizes", because the pool stays visible and no read fails. The view still holds one row for each memory pool the JVM lists. It is the simplest control that leaves every read working ([PRINCIPLE-056](../../../process/principles.md#principle-056)). Option 2 hides a pool the JVM lists. Option 3 turns a state the JVM reports in good order into an error on every read of the view, also on a read of another pool by its name.

1. If `MemoryPoolMXBean.getUsage` returns null for a memory pool, then the row of that pool MUST hold the name and the type of the pool and null in `used_bytes`, `committed_bytes` and `max_bytes`.
2. The documentation of the view MUST give the meaning of null in the three size columns.

### Consequences

- Good: a read of the view does not fail because of such a pool.
- Good: null says that the value is absent, as it does in the tables of `system_views` that Apache Cassandra has. For example `system_views.clients` holds null as the user name of a client that has none: `ClientsTable.data`, `src/java/org/apache/cassandra/db/virtual/ClientsTable.java:79`, ChronitonDB chronitondb-sandbox at `ffa1bc742d`, unchanged against its base, Apache Cassandra cassandra-5.0 at `76550e9314`.
- Good: null in `max_bytes` differs from -1, which [DEC-JVMEM-0002](DEC-JVMEM-0002-a-pool-with-no-maximum-shows-minus-one.md) keeps for a pool whose usage the JVM reports with no maximum defined.
- Bad: a script that computes with a size has to pass over a row whose size is null.
- Bad: the three size columns are kept able to hold null for the whole line once a release ships them ([PRINCIPLE-082](../../../process/principles.md#principle-082)).

## More information

- The [feature spec](../feature-spec.md), section 2.2 for the columns and section 3 for the requirement.
- Java SE documentation, `java.lang.management.MemoryPoolMXBean`: `getUsage` and `isValid`.
