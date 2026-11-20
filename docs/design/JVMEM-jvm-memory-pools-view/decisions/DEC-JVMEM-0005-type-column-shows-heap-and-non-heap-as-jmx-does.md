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

# DEC-JVMEM-0005. The type column shows HEAP and NON_HEAP, as JMX does

| Field | Value |
|---|---|
| Document type | Record (ISO/IEC/IEEE 15289), MADR |
| Status | Accepted |
| Date | 2026-11-20 |
| Deciders | The maintainers |
| References | Issue #161, the [feature spec](../feature-spec.md), [DEC-JVMEM-0002](DEC-JVMEM-0002-a-pool-with-no-maximum-shows-minus-one.md), [PRINCIPLE-059](../../../process/principles.md#principle-059), [PRINCIPLE-082](../../../process/principles.md#principle-082) |
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

The view says for each memory pool whether it is a pool of heap memory or of other memory. The JVM holds this as `java.lang.management.MemoryType`, which has two values. The JVM and Apache Cassandra show those two values as text in more than one way, and an operator filters and joins on the text, so it had to be settled which text the view holds.

1. The names of the two values are `HEAP` and `NON_HEAP`. The JVM's own MBean of a pool, `java.lang:type=MemoryPool,name=<pool>`, shows this text in its `Type` attribute over JMX. That was read on OpenJDK 11.0.33.1 and 17.0.21.1 with the G1 collector.
2. The display text of the two values, which `MemoryType.toString` returns, is `Heap memory` and `Non-heap memory`. Apache Cassandra logs this text once for each pool at startup: `CassandraDaemon.logSystemInfo`, `src/java/org/apache/cassandra/service/CassandraDaemon.java:596`, the loop at line 614, ChronitonDB chronitondb-sandbox at `ffa1bc742d`. The same code stands at the same lines in Apache Cassandra cassandra-5.0 at `76550e9314`, the base of the line, and at `47227d98bf`, and at lines 706 and 724 in Apache Cassandra cassandra-6.0 at `a02931dea8` and trunk at `45c325a01b`.
3. Plain lower case words, `heap` and `non-heap`, are shown by no surface of the JVM.

## Considered options

1. `HEAP` and `NON_HEAP`, the names of the two values.
2. `heap` and `non-heap`.
3. `Heap memory` and `Non-heap memory`, the display text.

## Decision outcome

Chosen option: "`HEAP` and `NON_HEAP`", because the view then holds the text an operator reads for the same pool over JMX. One value has one meaning and one text on both surfaces, as [PRINCIPLE-059](../../../process/principles.md#principle-059) asks, and it is the reason [DEC-JVMEM-0002](DEC-JVMEM-0002-a-pool-with-no-maximum-shows-minus-one.md) gave for showing -1 as JMX does.

1. The `type` column MUST hold `HEAP` for a memory pool of heap memory and `NON_HEAP` for every other memory pool.
2. The documentation of the view MUST name both values.

### Consequences

- Good: an operator who compares the view with JMX sees the same text, and a script joins the two without a mapping.
- Good: each value is one word with no space, which is simple to filter on.
- Bad: the text is upper case, unlike most text values in the tables of `system_views`.
- Bad: the text differs from the line Apache Cassandra logs at startup for the same pool, which shows the display text.
- Bad: the two values are kept for the whole line once a release ships them ([PRINCIPLE-082](../../../process/principles.md#principle-082)).

## More information

- The [feature spec](../feature-spec.md), section 2.2 for the column and section 3 for the requirement.
- Java SE documentation, `java.lang.management.MemoryType`: the two values `HEAP` and `NON_HEAP`.
