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

# 0014. The node uptime view logs one ERROR line when JMX already holds the name of its read counter

| Field | Value |
|---|---|
| Document type | Record (ISO/IEC/IEEE 15289), MADR |
| Status | Accepted |
| Date | 2026-11-17 |
| Deciders | The maintainers |
| References | Issue #144, the feature spec in `docs/design/UPTIM-node-uptime-view/`, decision record 0012 |

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in BCP 14 (RFC 2119, RFC 8174) when, and only when, they appear in all capitals, as shown here.

## Contents

- [Context and problem statement](#context-and-problem-statement)
- [Considered options](#considered-options)
- [Decision outcome](#decision-outcome)
  - [Consequences](#consequences)
- [More information](#more-information)

## Context and problem statement

Each time the node uptime view is turned on, the feature creates its read counter through Apache Cassandra's metrics registry, which registers the MBean of the counter. Decision record 0012 says that the node goes on when JMX does not take that MBean, and that one ERROR line reports it.

For one case Apache Cassandra writes no such line. When JMX already holds an MBean under the name of the counter, the registry attempts no registration and logs nothing: `CassandraMetricsRegistry.registerMBean`, `src/java/org/apache/cassandra/metrics/CassandraMetricsRegistry.java:234`, the check at line 262, ChronitonDB chronitondb-sandbox at `17e0b84a36`. The view is then on, the counter counts in the metrics registry, and JMX goes on showing the other MBean under the name of the counter. Nothing in the log tells the operator. The feature spec had to know whether the feature writes a line of its own for this case.

## Considered options

1. The feature asks JMX for the name before it creates the counter, and logs one ERROR line of its own when JMX holds it.
2. The feature adds no line, as Apache Cassandra adds none for its own metrics.

## Decision outcome

Chosen option: "The feature asks JMX for the name and logs one ERROR line of its own", because the operator then has a sign in the log in every case in which JMX does not show the read counter of the view, as decision record 0012 says.

If JMX holds an MBean under the MBean name of the read counter when a switch change to on is about to create the counter, the node MUST log one ERROR line that holds that MBean name.

The switch change MUST go on after that line, as decision record 0012 says: the view is on and the counter counts in the metrics registry.

The feature asks with the question Apache Cassandra's metrics registry asks, `MBeanWrapper.isRegistered`, `src/java/org/apache/cassandra/utils/MBeanWrapper.java:104`, in the same tree. It asks at every switch change to on, at the start of a node and for `nodetool enableuptimeview`.

### Consequences

- Good: an operator who reads the log learns that the value JMX shows under the name of the counter is no count of the reads of the view.
- Good: what decision record 0012 says of the ERROR line holds for every case.
- Bad: the feature makes one check of its own before it creates the counter, with one more log line to test.
- Bad: JMX goes on showing the other MBean until the view is turned off. Apache Cassandra's registry then unregisters whatever MBean holds the name, as it does for every metric it removes: `CassandraMetricsRegistry.remove`, `src/java/org/apache/cassandra/metrics/CassandraMetricsRegistry.java:208`, in the same tree.

## More information

The feature spec applies this decision in section 2.2 and in FREQ-UPTIM-045. Problem 6 of its section 4 names the test. Apache Cassandra upstream was not read for this record.
