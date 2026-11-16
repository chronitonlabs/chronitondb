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

# 0012. The build details view follows the Apache Cassandra permission rule where authorization is off

| Field | Value |
|---|---|
| Document type | Record (ISO/IEC/IEEE 15289), MADR |
| Status | Accepted |
| Date | 2026-11-16 |
| Deciders | The maintainers |
| References | Issue #141, the feature spec in `docs/design/BUILD-build-details-view/` |

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in BCP 14 (RFC 2119, RFC 8174) when, and only when, they appear in all capitals, as shown here.

## Contents

- [Context and problem statement](#context-and-problem-statement)
- [Considered options](#considered-options)
- [Decision outcome](#decision-outcome)
  - [Consequences](#consequences)
- [More information](#more-information)

## Context and problem statement

The build details view is read by the permission rule Apache Cassandra has for the tables of `system_views`: a superuser, or a role granted `SELECT` on the table or its keyspace. That rule applies only on a node whose authorizer requires authorization. On a node whose authorizer requires none, the permission check returns at once and every client passes (`ClientState.ensurePermission`, `src/java/org/apache/cassandra/service/ClientState.java:477`, ChronitonDB chronitondb-sandbox at `17e0b84a36`, the same line in Apache Cassandra cassandra-5.0 at `531e98928d`, and `ClientState.java:512` in Apache Cassandra cassandra-6.0 at `383ed3c5ad` and trunk at `30b73cadf3`). The `cassandra.yaml` that Apache Cassandra ships sets such an authorizer (the setting `authorizer`, `conf/cassandra.yaml:217`, ChronitonDB chronitondb-sandbox at `17e0b84a36`). The requirement that only superusers and granted roles read the view, as for Apache Cassandra's own node views, reads two ways on such a node. The feature had to know which one holds.

## Considered options

1. The view follows the Apache Cassandra rule in full. On a node whose authorizer requires no authorization, every client reads the view once it is shown.
2. The view stays hidden on a node whose authorizer requires no authorization, whatever its switch says.

## Decision outcome

Chosen option: "The view follows the Apache Cassandra rule in full", because the view then works on clusters that run without authorization, and it is read exactly as Apache Cassandra's own tables of `system_views` are.

The view MUST add no condition of its own on the node's authorizer. On a node whose authorizer requires no authorization, every client MAY read the view while it is shown. The reference page of the feature MUST warn about this case.

### Consequences

- Good: one rule decides who reads the view, the rule Apache Cassandra already has, and the feature adds no code that looks at the authorizer.
- Good: operators of clusters without authorization can use the view.
- Bad: on such a node, every client that can connect reads the node's release version, Apache Cassandra version and git SHA once the switch is on. Such a node already lets every client read and change every table.

## More information

The feature spec in `docs/design/BUILD-build-details-view/feature-spec.md` applies this decision in FREQ-BUILD-008 and FREQ-BUILD-023, in its section 2.2 and in the second row of its section 6.
