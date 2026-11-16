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

# 0021. The build details view stays shown when the MBean of its read counter cannot be registered

| Field | Value |
|---|---|
| Document type | Record (ISO/IEC/IEEE 15289), MADR |
| Status | Accepted |
| Date | 2026-11-16 |
| Deciders | The maintainers |
| References | Issue #141, the feature spec in `docs/design/BUILD-build-details-view/`, decision records 0014 and 0016 |

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in BCP 14 (RFC 2119, RFC 8174) when, and only when, they appear in all capitals, as shown here.

## Contents

- [Context and problem statement](#context-and-problem-statement)
- [Considered options](#considered-options)
- [Decision outcome](#decision-outcome)
  - [Consequences](#consequences)
- [More information](#more-information)

## Context and problem statement

A node that shows the build details view holds one read counter (decision record 0014). Apache Cassandra registers an MBean for each metric it creates and does not tell the caller whether that worked. It skips a name that is already registered. It logs a failed registration in an ERROR line of its own and goes on. So the start step of the view can create the counter and find it in the metrics registry while no MBean of it exists. The feature had to know whether the view stays shown on such a node.

## Considered options

1. The view stays shown. Its counter counts in the metrics registry and in metrics reporters.
2. The start step looks for the MBean after it created the counter, and the node hides the view when the MBean is missing.

## Decision outcome

Chosen option: "The view stays shown. Its counter counts in the metrics registry and in metrics reporters", because the read counter then behaves as every metric of Apache Cassandra does, and a fault of the JMX server does not take the view away.

The start step of the view MUST NOT hide the view because the MBean of the read counter is missing. The feature adds no check for that MBean and no log line of its own for a failed registration. The ERROR line for it is the one Apache Cassandra writes.

### Consequences

- Good: the feature adds no failure handling of its own for the MBean.
- Good: a JMX fault never hides the view.
- Bad: on such a node JMX shows no read counter until the next start, while the view is shown and its reads are counted in the metrics registry.
- Bad: a monitoring tool that reads the counter over JMX cannot tell such a node from a node that hides the view.

## More information

The feature spec in `docs/design/BUILD-build-details-view/feature-spec.md` carries this decision in its section 2.2, The read counter, and in problem 6 of its section 4.
