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

# DEC-JVMEM-0009. Every read builds the row of every pool, and a JVM error for one pool fails every read

| Field | Value |
|---|---|
| Document type | Record (ISO/IEC/IEEE 15289), MADR |
| Status | Accepted |
| Date | 2026-11-20 |
| Deciders | The maintainers |
| References | Issue #161, the [feature spec](../feature-spec.md), [DEC-JVMEM-0007](DEC-JVMEM-0007-a-pool-with-no-reported-usage-shows-null-sizes.md), [PRINCIPLE-054](../../../process/principles.md#principle-054), [PRINCIPLE-056](../../../process/principles.md#principle-056) |
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

The view builds its rows by calling the JVM's memory pool beans. A call to a bean can throw. No case is known in which a JVM makes such a call throw an exception, and none was looked for. An out of memory error is another matter: any call that needs memory can throw one while the heap is full, and [DEC-JVMEM-0010](DEC-JVMEM-0010-the-view-catches-nothing-a-call-to-the-jvm-throws.md) says where it goes.

When a statement names one pool, Apache Cassandra asks the virtual table for its rows for that key. `AbstractVirtualTable` then builds all its rows, unless the table overrides the method that is asked: `AbstractVirtualTable.select`, `src/java/org/apache/cassandra/db/virtual/AbstractVirtualTable.java:78`, calls `AbstractVirtualTable.data` with the key at line 80, and that method, line 72, returns all rows. Both are ChronitonDB chronitondb-sandbox at `ffa1bc742d`, unchanged against the base of the line, Apache Cassandra cassandra-5.0 at `76550e9314`. Section 12 of the feature spec has the lines in Apache Cassandra now, where the code does the same.

So it had to be settled whether a read of one pool by its name builds the row of every pool or the named row alone. That decides whether an error the JVM raises for one pool also fails a read of another pool by name.

## Considered options

1. Every read builds the row of every pool. An error that the JVM raises for any pool then fails every read, also a read of another pool by its name.
2. A read by name builds the named row alone, through the method Apache Cassandra lets a table override. A read of the whole view still fails on such an error.

## Decision outcome

Chosen option: "Every read builds the row of every pool", because the view then has one way to build its rows, so a read by name and a read of the whole view take their values in the same way and are proven by the same tests. Option 2 adds a second way to build a row, with tests of its own, for an exception that no JVM is known to make such a call throw. That is more to build, test and review than the need asks for ([PRINCIPLE-054](../../../process/principles.md#principle-054)). The cost of option 1 is stated as what happens on a node ([PRINCIPLE-056](../../../process/principles.md#principle-056)): while the JVM raises an error for one pool, no pool can be read through the view.

1. Every read of the view MUST build the row of every memory pool that the JVM lists, whichever rows the statement asks for.
2. If a call to the JVM's memory pool beans throws while a read builds its rows, then the read MUST fail, also where the statement names another pool.
3. A memory pool whose usage the JVM does not report MUST stay a row with null sizes, as [DEC-JVMEM-0007](DEC-JVMEM-0007-a-pool-with-no-reported-usage-shows-null-sizes.md) says. It is no error.
4. The documentation of the view MUST say that an error the JVM raises for one memory pool fails every read of the view while it lasts.

### Consequences

- Good: the view has one code path for every read, so a read by name cannot show another value than a read of the whole view would.
- Good: the view passes over no error of the JVM, so an operator sees it as a failed read.
- Bad: while the JVM raises an error for one pool, every read of the view fails, a read of another pool by its name too.
- Neutral: a read by name makes the calls to the JVM that a read of the whole view makes. The number of pools is the JVM's, 8 in the example of the feature spec.

## More information

- The [feature spec](../feature-spec.md), section 2.2 for what one read is, section 2.5 for errors and section 3 for the requirements.
- [DEC-JVMEM-0010](DEC-JVMEM-0010-the-view-catches-nothing-a-call-to-the-jvm-throws.md) for what the view does with what a call to the JVM throws.
