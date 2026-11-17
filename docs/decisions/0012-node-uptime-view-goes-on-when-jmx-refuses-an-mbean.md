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

# 0012. A node goes on when JMX refuses an MBean of the node uptime view

| Field | Value |
|---|---|
| Document type | Record (ISO/IEC/IEEE 15289), MADR |
| Status | Accepted |
| Date | 2026-11-17 |
| Deciders | The maintainers |
| References | Issue #144, the feature spec in `docs/design/UPTIM-node-uptime-view/`, decision records 0007 and 0009 |

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in BCP 14 (RFC 2119, RFC 8174) when, and only when, they appear in all capitals, as shown here.

## Contents

- [Context and problem statement](#context-and-problem-statement)
- [Considered options](#considered-options)
- [Decision outcome](#decision-outcome)
  - [Consequences](#consequences)
- [More information](#more-information)

## Context and problem statement

The node uptime view registers two MBeans. The switch MBean is registered at the start of every node, so that the two nodetool commands can reach the node. The MBean of the read counter is registered each time the view is turned on. JMX can refuse a registration, for example when another MBean already holds the name. The feature spec had to know what a node does then: go on without the MBean, or fail the start or the command that asked for it.

Apache Cassandra registers the MBeans of its own metrics in a mode that logs a refused registration in one ERROR line and goes on: `CassandraMetricsRegistry.registerMBean`, `src/java/org/apache/cassandra/metrics/CassandraMetricsRegistry.java:234`, with the mode in `MBeanWrapper.OnException` at `src/java/org/apache/cassandra/utils/MBeanWrapper.java:363`, ChronitonDB chronitondb-sandbox at `17e0b84a36`.

[quality-requirements.md](../process/quality-requirements.md#automatic-fallbacks-are-opt-in-and-counted) asks that an automatic fallback is off by default and has a setting, a toggle and a metric of its own. A node that goes on without an MBean could be read as such a fallback.

## Considered options

1. The node goes on. Apache Cassandra logs one ERROR line for the refused registration.
2. Where the view is asked on, the start fails for the switch MBean, and `enableuptimeview` fails for the MBean of the read counter.

## Decision outcome

Chosen option: "The node goes on", because Apache Cassandra treats its own MBeans this way, and because a fault in JMX then never keeps a node down for a view. Decision record 0007 made the same choice for a setting that turns the view on before the final gate.

If JMX refuses the switch MBean at the start of a node, the node MUST go on with its start, with the view on or off as its setting and the final gate say.

If JMX refuses the MBean of the read counter when the view is turned on, the switch change MUST succeed. The counter then counts in the metrics registry and is not shown over JMX.

A refused MBean is no automatic fallback in the sense of quality-requirements.md. The view answers as its switch says. What the node lacks is one way to manage or to watch the view, and the ERROR line of Apache Cassandra reports it. So it needs no setting, no toggle and no metric of its own.

### Consequences

- Good: a fault in JMX never stops a node or a switch change because of this feature.
- Good: the feature adds no failure handling of its own round the registration. It uses the mode Apache Cassandra has.
- Bad: a node without the switch MBean has no toggle until its next start. Where its setting turned the view on, the view stays on until then.
- Bad: a node without the MBean of the read counter shows no counter over JMX until the view is turned off and on again.
- Bad: the operator learns of it from one ERROR line in the log, or from the refusal the two commands print for a node that has no switch MBean.

## More information

The feature spec applies this decision in section 2.2 and in FREQ-UPTIM-033, FREQ-UPTIM-039 and FREQ-UPTIM-042. Problems 1 and 6 of its section 4 name the tests. An error of the JVM, such as a class that does not load or memory that runs out, still ends the start of a node, as it ends the start of an Apache Cassandra node.
