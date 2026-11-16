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

# 0015. A grant on the build details view that outlives the view is documented

| Field | Value |
|---|---|
| Document type | Record (ISO/IEC/IEEE 15289), MADR |
| Status | Accepted |
| Date | 2026-11-16 |
| Deciders | The maintainers |
| References | Issue #141, the feature spec in `docs/design/BUILD-build-details-view/`, decision records 0009 and 0012 |

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in BCP 14 (RFC 2119, RFC 8174) when, and only when, they appear in all capitals, as shown here.

## Contents

- [Context and problem statement](#context-and-problem-statement)
- [Considered options](#considered-options)
- [Decision outcome](#decision-outcome)
  - [Consequences](#consequences)
- [More information](#more-information)

## Context and problem statement

A role reads the build details view through a grant, and grants are stored for the whole cluster. The view exists only on the nodes that show it. Apache Cassandra refuses a `REVOKE` on a table that the node does not find (`PermissionsManagementStatement.validate`, `src/java/org/apache/cassandra/cql3/statements/PermissionsManagementStatement.java:57`, ChronitonDB chronitondb-sandbox at `17e0b84a36`, the same line in Apache Cassandra cassandra-5.0 at `531e98928d`, and `PermissionsManagementStatement.java:60` in Apache Cassandra cassandra-6.0 at `383ed3c5ad` and trunk at `30b73cadf3`). So once no node shows the view, a grant on it can no longer be revoked, and it counts again when a node shows the view later. The feature had to know what operators are told to do about such a grant.

## Considered options

1. Document it: the reference page says when to revoke and what a grant left behind does.
2. The reference page recommends a grant on the keyspace `system_views` in place of a grant on the view. A keyspace grant can be revoked on any node. Its role reads every table of `system_views`.

## Decision outcome

Chosen option: "Document it", because the feature then changes no permission code, and a role that should read only the view is not given every other table of `system_views`.

A grant on the view that is left behind when no node shows the view is accepted. The feature MUST NOT add code that removes, hides or changes a grant. The reference page MUST give the grant on the view as the way to let a role read it. It MUST state the rule for the cluster: revoke a grant on the view over a connection to a node that shows the view, before the last node that shows the view is restarted with the view hidden. It MUST state what a grant left behind does:

1. It gives no access while no node shows the view.
2. It gives its role the read again on every node that shows the view later.
3. It can be revoked on any node that shows the view, whenever one does.
4. It goes when its role is dropped, on any node.

### Consequences

- Good: no file of Apache Cassandra's permission code changes, so the feature stays clear of the areas that are always Critical risk.
- Good: the grant on the view stays the recommended grant, the narrowest one Apache Cassandra offers.
- Bad: a grant that an operator forgot gives its role the read again when a node shows the view later, with no new `GRANT`.
- Bad: an operator who wants such a grant gone while no node shows the view has to show the view on one node first, or drop the role.

## More information

The feature spec in `docs/design/BUILD-build-details-view/feature-spec.md` applies this decision in FREQ-BUILD-009 and FREQ-BUILD-035, in its section 2.2, Access, in problem 8 of its section 4 and in its section 7.4. Dropping a role removes its grants in `DropRoleStatement.execute`, `src/java/org/apache/cassandra/cql3/statements/DropRoleStatement.java:67`, ChronitonDB chronitondb-sandbox at `17e0b84a36`.
