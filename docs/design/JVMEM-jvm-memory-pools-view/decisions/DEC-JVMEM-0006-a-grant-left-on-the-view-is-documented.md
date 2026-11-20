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

# DEC-JVMEM-0006. A grant left on the view after moving back is documented, and permission code is unchanged

| Field | Value |
|---|---|
| Document type | Record (ISO/IEC/IEEE 15289), MADR |
| Status | Accepted |
| Date | 2026-11-20 |
| Deciders | The maintainers |
| References | Issue #161, the [feature spec](../feature-spec.md), [PRINCIPLE-003](../../../process/principles.md#principle-003), [PRINCIPLE-054](../../../process/principles.md#principle-054) |
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

A role gets the read of the view by a grant on all keyspaces, on the keyspace `system_views` or on the view by name. A grant on the view by name is a row of the auth tables, which every node of the cluster holds. It can hold any permission of a table, such as `SELECT` or `AUTHORIZE`.

A cluster can move back to a release of the line without the view, or to Apache Cassandra. After the last node that has the view has moved back, no node accepts a `REVOKE` that names the view, because Apache Cassandra refuses a `GRANT` or a `REVOKE` on a table the node does not have: `PermissionsManagementStatement.validate`, `src/java/org/apache/cassandra/cql3/statements/PermissionsManagementStatement.java:57`, ChronitonDB chronitondb-sandbox at `ffa1bc742d`. A grant that was not revoked before that stays in the auth tables. It had to be settled what the feature does about such a row.

What Apache Cassandra does with a grant row that names a table the node does not have was read in the code. The row is read in four places, and none of them looks the table up. All are ChronitonDB chronitondb-sandbox at `ffa1bc742d`.

1. A permission check reads the row of one role for the resource the statement names: `CassandraAuthorizer.addPermissionsForRole`, `src/java/org/apache/cassandra/auth/CassandraAuthorizer.java:255`. No statement on a node without the view can name the view, so the row is not read there.
2. `LIST ALL PERMISSIONS` lists the row: `CassandraAuthorizer.listPermissionsForRole`, the same file, line 340.
3. The warm-up of the permissions cache at the start of a node parses the name of the row and goes on: `CassandraAuthorizer.bulkLoader`, the same file, line 458. The warm-up runs only where the setting `auth_cache_warming_enabled` is on: `CassandraDaemon.setup`, `src/java/org/apache/cassandra/service/CassandraDaemon.java:229`, at line 447.
4. `DROP ROLE` removes every grant row of the role: `CassandraAuthorizer.revokeAllFrom`, the same file, line 135.

The line changes none of these files against its base, Apache Cassandra cassandra-5.0 at `76550e9314`. Section 12 of the feature spec has the lines in Apache Cassandra cassandra-5.0 at `47227d98bf`, cassandra-6.0 at `a02931dea8` and trunk at `45c325a01b`, where the code does the same. `CassandraAuthorizer.java` and `DropRoleStatement.java` are unchanged from the tag `cassandra-5.0.0` at `186272edca` to that base, so the four places do the same in every Apache Cassandra 5.0 release up to the base.

## Considered options

1. Document the row. The documentation of the view says how to list the grants that name the view, to revoke every permission of each before the last node that has the view moves back, what a row left behind does and how it is removed. Permission code stays as Apache Cassandra has it.
2. Refuse a `GRANT` that names the view. A role then gets the read only by a grant on the keyspace or on all keyspaces, so no row can name the view.

## Decision outcome

Chosen option: "Document the row", because a row left behind does no harm that the code shows, and the operator has a stated step for moving back, as [PRINCIPLE-003](../../../process/principles.md#principle-003) asks. Option 2 puts a check of the project into the permission code of Apache Cassandra. Authorisation is an area that [classification.md](../../../process/classification.md#the-critical-floor) keeps at Critical risk, and the view would be the only table of `system_views` that takes no grant by name. That is more to build, test and review than the row needs ([PRINCIPLE-054](../../../process/principles.md#principle-054)).

1. The feature MUST NOT change the permission code of Apache Cassandra. A `GRANT` and a `REVOKE` on the view by name work as they do on every table of `system_views`.
2. The documentation of the view MUST say how an operator lists the grants that name the view, that the operator revokes every permission of each before the last node that has the view moves back, and as which role the operator does both.
3. The documentation of the view MUST say what a grant left behind does and how it is removed.
4. A test MUST show that a node handles a grant row that names a table the node does not have as the context above says.

### Consequences

- Good: the permission code and every other table of `system_views` stay as Apache Cassandra has them.
- Good: the feature stays off the areas that are always Critical risk.
- Bad: an operator who skips the step leaves a row in the auth tables. `LIST ALL PERMISSIONS` shows it, and no statement that names the view can remove it while no node has the view.
- Bad: a grant given on a node that still has the view, after the operator revoked the others, is left behind in the same way. Nothing stops it.
- Neutral: a row left behind gives its role its permissions on the view again when a node gets the view back. It goes with `DROP ROLE` of its role, or with a `REVOKE` on a node that has the view.

## More information

- The [feature spec](../feature-spec.md), section 7.4 for the step and the row, section 4.1 for the test and section 3 for the requirements.
