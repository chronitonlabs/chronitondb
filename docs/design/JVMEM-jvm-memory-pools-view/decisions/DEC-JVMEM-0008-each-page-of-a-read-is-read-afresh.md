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

# DEC-JVMEM-0008. Each page of a read of the view holds the values of its own moment

| Field | Value |
|---|---|
| Document type | Record (ISO/IEC/IEEE 15289), MADR |
| Status | Accepted |
| Date | 2026-11-20 |
| Deciders | The maintainers |
| References | Issue #161, the [feature spec](../feature-spec.md), [DEC-JVMEM-0001](DEC-JVMEM-0001-jvm-memory-pools-view-has-no-switch.md), [PRINCIPLE-054](../../../process/principles.md#principle-054) |
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

A client can fetch the rows of a statement in pages. For the view that happens when the page size is below the number of memory pools, for example with `PAGING 3` in `cqlsh` on a node with 8 pools.

Apache Cassandra runs the read once for each page, and a virtual table builds its rows again each time the read runs. `AbstractQueryPager.fetchPage`, `src/java/org/apache/cassandra/service/pager/AbstractQueryPager.java:63`, runs the read of the next page at line 76. `AbstractVirtualTable.select`, `src/java/org/apache/cassandra/db/virtual/AbstractVirtualTable.java:91`, asks the table for its rows at line 93. Both are ChronitonDB chronitondb-sandbox at `ffa1bc742d`, unchanged against the base of the line, Apache Cassandra cassandra-5.0 at `76550e9314`. Section 12 of the feature spec has the lines in Apache Cassandra cassandra-5.0 at `47227d98bf`, cassandra-6.0 at `a02931dea8` and trunk at `45c325a01b`, where the code does the same.

So the rows of two pages of one statement hold values of two moments, which can be seconds apart when the client waits between the pages. It had to be settled whether the view keeps to that or holds one moment for the whole statement.

## Considered options

1. Each page is its own read, with the values of its own moment. The documentation of the view says so.
2. One moment for the whole statement. The node keeps the rows of the first page until the client has fetched the last one.

## Decision outcome

Chosen option: "Each page is its own read", because it is what every virtual table of Apache Cassandra does, it needs no code and it keeps no memory between two reads. Option 2 needs memory that the node holds between the pages of a statement, with a rule for when to free it. The view gets no sign from Apache Cassandra of which pages belong to one statement, so its paging code would have to change. That is more than the need asks for ([PRINCIPLE-054](../../../process/principles.md#principle-054)), and it goes against [DEC-JVMEM-0001](DEC-JVMEM-0001-jvm-memory-pools-view-has-no-switch.md), which rests on a view that keeps no memory.

1. The node MUST take the values of the rows of each page from its JVM when it reads that page.
2. The documentation of the view MUST say that the pages of one statement can hold values of different moments.

### Consequences

- Good: the view behaves as every table of `system_views` does, and the paging code stays as Apache Cassandra has it.
- Good: nothing is kept between two pages, so a client that never fetches the next page costs the node nothing.
- Bad: the sizes of two pages of one statement do not belong to one moment, so sums across pages can be off.
- Bad: if the JVM changes its list of pools between two pages, a pool can be missing from the statement's rows.
- Neutral: a statement whose rows fit in one page is one read. The default page size of `cqlsh` and of the drivers is far above the number of pools a JVM has.

## More information

- The [feature spec](../feature-spec.md), section 2.2 for what one read is and section 3 for the requirements.
