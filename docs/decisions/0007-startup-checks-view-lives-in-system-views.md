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

# 0007. The startup checks view lives in system_views

| Field | Value |
|---|---|
| Document type | Record (ISO/IEC/IEEE 15289), MADR |
| Status | Accepted |
| Date | 2026-11-15 |
| Deciders | The maintainers |
| References | Issue #117, the design record in `docs/design/SCV-startup-checks-view/`, [classification.md, The floor](../process/classification.md#the-floor) |

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in BCP 14 (RFC 2119, RFC 8174) when, and only when, they appear in all capitals, as shown here.

## Contents

- [Context and problem statement](#context-and-problem-statement)
- [Considered options](#considered-options)
- [Decision outcome](#decision-outcome)
  - [Consequences](#consequences)
- [More information](#more-information)

## Context and problem statement

The startup checks view is a virtual table that shows which startup checks a node runs, whether each is on, and where that value came from. The design had to know which keyspace holds the table, because the keyspace decides the table's full name and the permission a role needs to read it. Apache Cassandra keeps its own tables of node settings, `settings` and `system_properties`, in the virtual keyspace `system_views`. An ordinary role reads a table of that keyspace only with `SELECT` granted on the table or on the keyspace. The tables of `system_virtual_schema` are readable by every role with no grant, through a list in the stock access code.

## Considered options

1. In `system_views`, as the table `startup_checks`, under the stock access rule of that keyspace. No stock file is edited for it.
2. In a new virtual keyspace of ChronitonDB's own. A role with `SELECT` on all keyspaces could read it. It needs a stock edit so that the keyspace goes away when the view is switched off.
3. In `system_views`, and added to the stock list of tables that every role reads with no grant. That edits a file of authorisation, which makes the work Critical risk.

## Decision outcome

Chosen option: "In `system_views`, as the table `startup_checks`", because it is where operators already read a node's settings, it needs a grant as those tables do, and it edits no file of authentication or authorisation.

The view MUST be the table `system_views.startup_checks`. The feature MUST NOT change which roles may read a table. A read of the view by a role without the `SELECT` permission that the stock rule of `system_views` asks for MUST be refused as unauthorised.

### Consequences

- Good: the view sits beside `settings` and `system_properties`, and a role that may not read those may not read the view.
- Good: no file of authentication or authorisation changes.
- Bad: a table that Apache Cassandra later adds to `system_views` under the same name clashes at an import. The tests of the feature then fail on the import, and the name is decided again.
- Bad: a role needs a grant before it can read the view on a node with authorisation on.

## More information

The design record in `docs/design/SCV-startup-checks-view/` applies this decision in section 3, Stock behaviour preservation, in REQ-SCV-015 and in section 10, Threat model and security.
