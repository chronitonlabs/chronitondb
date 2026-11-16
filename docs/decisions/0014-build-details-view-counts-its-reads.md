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

# 0014. A node that shows the build details view counts its reads

| Field | Value |
|---|---|
| Document type | Record (ISO/IEC/IEEE 15289), MADR |
| Status | Accepted |
| Date | 2026-11-16 |
| Deciders | The maintainers |
| References | Issue #141, the feature spec in `docs/design/BUILD-build-details-view/`, [quality-requirements.md, Observability](../process/quality-requirements.md#observability), [conventions.md, Names](../process/conventions.md#names), decision record 0011 |

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in BCP 14 (RFC 2119, RFC 8174) when, and only when, they appear in all capitals, as shown here.

## Contents

- [Context and problem statement](#context-and-problem-statement)
- [Considered options](#considered-options)
- [Decision outcome](#decision-outcome)
  - [Consequences](#consequences)
- [More information](#more-information)

## Context and problem statement

The quality rules ask that every feature is measured and that every outcome has a counter. Decision record 0011 gives the build details view no MBean for its switch. Apache Cassandra registers every metric of its registry as an MBean (`CassandraMetricsRegistry.counter`, `src/java/org/apache/cassandra/metrics/CassandraMetricsRegistry.java:55`, ChronitonDB chronitondb-sandbox at `17e0b84a36`, the same file in Apache Cassandra cassandra-5.0 at `531e98928d`). So a counter of the view's reads is an MBean on the node that holds it. The feature had to know whether it has a metric at all, and on which nodes.

## Considered options

1. One counter of the reads of the view, created only on a node that shows the view.
2. No metric. The start log is the only trace of the view.

## Decision outcome

Chosen option: "One counter of the reads of the view, created only on a node that shows the view", because the feature is then measured as every feature is, and a node that hides the view still holds nothing of it in JMX.

A node that shows the view MUST hold one counter of the reads of the view, `org.chronitondb.metrics:type=BuildView,name=Reads`. The view MUST raise it by one at each read. A node that hides the view MUST NOT hold a metric or an MBean of the feature. The MBean Apache Cassandra creates for this counter is the one MBean of the feature. The reference page MUST name the counter.

The name follows conventions.md, Names, items 3 and 4: the feature's own metric type in the `org.chronitondb` domain, in the form the counters of the commit log disk check have.

### Consequences

- Good: an operator can see whether and how often the view is read, on each node that shows it.
- Good: a node with the switch off, and a node in Apache compatibility mode, hold no metric and no MBean of the feature.
- Bad: on a node that shows the view, whoever reads its MBeans sees the name of the counter and learns that the node runs ChronitonDB.
- Bad: a monitoring tool finds the counter on some nodes of a cluster and not on others, by each node's switch.
- Bad: Apache Cassandra 6.0 refuses a metric whose type is not in its fixed set of metric groups (`CassandraMetricsRegistry.verifyUnknownMetric`, `CassandraMetricsRegistry.java:272`, Apache Cassandra cassandra-6.0 at `383ed3c5ad` and trunk at `30b73cadf3`). A port of the view to a line based on it has to design how the counter is registered there.

## More information

The feature spec in `docs/design/BUILD-build-details-view/feature-spec.md` applies this decision in FREQ-BUILD-025, FREQ-BUILD-029 to FREQ-BUILD-031 and FREQ-BUILD-034, and in its sections 2.2 and 2.8.
