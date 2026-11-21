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

# DEC-JVMEM-0011. A read of the view is no request path in the feature's class

| Field | Value |
|---|---|
| Document type | Record (ISO/IEC/IEEE 15289), MADR |
| Status | Accepted |
| Date | 2026-11-21 |
| Deciders | The maintainers |
| References | Issue #161, the [feature spec](../feature-spec.md), [classification.md](../../../process/classification.md#the-sections-of-a-feature-spec), [PRINCIPLE-050](../../../process/principles.md#principle-050), [PRINCIPLE-054](../../../process/principles.md#principle-054) |
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

The Touches row of a feature spec names what the feature touches. [classification.md](../../../process/classification.md#the-sections-of-a-feature-spec) lists a request path among the things it can name, and calls a path a request path when its cost grows with data or traffic. A Touches row that names a request path adds the performance checklist to the review of the code, and [PRINCIPLE-050](../../../process/principles.md#principle-050) then asks for benchmarks of the path.

One read of the view costs one call to the JVM for the list of memory pools and a fixed number of calls for each pool. The number of pools is the JVM's.

A statement can take more than one read. A statement that names pools with `IN` makes one read command for each name its client lists: `SelectStatement.getSliceCommands`, `src/java/org/apache/cassandra/cql3/statements/SelectStatement.java:713`, builds the group of commands at line 737. Apache Cassandra checks the number of those names against its guardrail on the partition keys of one `SELECT` at line 722 of the same method: `Guardrails.partitionKeysInSelect`, `src/java/org/apache/cassandra/db/guardrails/Guardrails.java:251`. Both thresholds of that guardrail are -1, which is off, unless an operator sets them: `Config.partition_keys_in_select_warn_threshold` and `Config.partition_keys_in_select_fail_threshold`, `src/java/org/apache/cassandra/config/Config.java:880` and line 881. A guardrail is applied to an ordinary user only: `Guardrail.enabled`, `src/java/org/apache/cassandra/db/guardrails/Guardrail.java:93`. All four are ChronitonDB chronitondb-sandbox at `ffa1bc742d`, in files that the line does not change against its base, Apache Cassandra cassandra-5.0 at `76550e9314`. They were not read in Apache Cassandra as it is now.

So the cost of a statement with `IN` grows with the names that the statement lists. The question was whether that makes a read of the view a request path in the feature's class.

## Considered options

1. No request path. The Touches row names a public interface and a new feature, and nothing else.
2. A request path. The Touches row names one too, the feature spec plans a benchmark of the read, and the review of the code runs the performance checklist.

## Decision outcome

Chosen option: "No request path", because the cost of a read grows neither with the data a node holds nor with the traffic it serves. A read asks the JVM about its own memory pools and touches no table, file or cache of Apache Cassandra. What makes a statement with `IN` cost more is the list of names that its client wrote into that one statement, and each read of it costs the same fixed amount. A benchmark and a performance review of a read of a handful of pools are more than the need asks for ([PRINCIPLE-054](../../../process/principles.md#principle-054)).

1. The Touches row of the feature spec MUST name no request path for the view.
2. The feature spec plans no benchmark of a read of the view.
3. This record decides for this view only. It changes no rule of classification.md, and whether other work touches a request path is decided by its own facts.

### Consequences

- Good: the checks and the review fit a read whose cost is fixed.
- Bad: the review of the code runs no performance checklist, so nothing but the tests and the ordinary checklists looks at the cost of the view class.
- Bad: nothing of the feature bounds the names of one statement with `IN`. A superuser is not bound by the guardrail, and an ordinary user is bound only where an operator sets a threshold.

## More information

- The [feature spec](../feature-spec.md), its Touches row, and items 1 and 2 of section 2.5 for the cost of a read and for benchmarks.
- [classification.md](../../../process/classification.md#checks-and-review): which review checklists the Touches row selects.
