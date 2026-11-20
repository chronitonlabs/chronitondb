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

# DEC-JVMEM-0002. A memory pool with no maximum shows -1 as its maximum

| Field | Value |
|---|---|
| Document type | Record (ISO/IEC/IEEE 15289), MADR |
| Status | Accepted |
| Date | 2026-11-20 |
| Deciders | The maintainers |
| References | Issue #161, the [feature spec](../feature-spec.md), [PRINCIPLE-059](../../../process/principles.md#principle-059) |
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

The view shows, for each memory pool of the JVM, the maximum size of the pool in bytes. The JVM defines no maximum for some pools. For such a pool `java.lang.management.MemoryUsage.getMax` returns -1, as the Java SE documentation of that class says. On OpenJDK 17.0.21 with the G1 collector and a 512 MiB heap, three of the eight pools had no maximum: `Metaspace`, `G1 Eden Space` and `G1 Survivor Space`.

Two idioms give two answers for what the view shows then.

1. The JVM's own MBean of the pool, `java.lang:type=MemoryPool,name=<pool>`, shows -1 over JMX. That was read on the same JVM.
2. A view of Apache Cassandra shows a value that is absent as null. For example `ClientsTable.data` writes null for a client with no user name: `src/java/org/apache/cassandra/db/virtual/ClientsTable.java:79`, ChronitonDB chronitondb-sandbox at `ffa1bc742d`. The same code stands at the same line in Apache Cassandra cassandra-5.0 at `76550e9314`, the base of the line, and at `47227d98bf`, and at line 92 in Apache Cassandra cassandra-6.0 at `a02931dea8` and trunk at `45c325a01b`.

## Considered options

1. -1, as the JVM reports it.
2. null, an empty value.

## Decision outcome

Chosen option: "-1, as the JVM reports it", because the view then holds the number an operator reads for the same pool over JMX. One value has one meaning on both surfaces, as [PRINCIPLE-059](../../../process/principles.md#principle-059) asks. The feature's requirement is that the view shows the values as the JVM reports them, and -1 is what the JVM reports.

1. Where the JVM reports a usage with no maximum defined for a memory pool, the maximum column of the view MUST hold -1 for that pool.
2. The documentation of the view MUST say that -1 in that column means the JVM defines no maximum for the pool.

### Consequences

- Good: an operator who compares the view with JMX sees the same number.
- Good: a query can pick out the pools with no maximum by the value -1.
- Bad: -1 is not a size. A script that divides the used size by the maximum has to pass over a row whose maximum is -1.
- Bad: the view differs here from the views of Apache Cassandra that show an absent value as null. The difference is deliberate, for the reason above.

## More information

- The [feature spec](../feature-spec.md), section 2.2 for the columns of the view and section 3 for the requirement.
- Java SE documentation, `java.lang.management.MemoryUsage`: the maximum is -1 if it is undefined.
