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

# 0005. The commit log disk check is switched under startup_checks

| Field | Value |
|---|---|
| Document type | Record (ISO/IEC/IEEE 15289), MADR |
| Status | Accepted |
| Date | 2026-11-15 |
| Deciders | The maintainers |
| References | Issue #112, the design record in `docs/design/CLD-commitlog-disk-check/`, [branching-and-review.md, Feature switches and defaults](../process/branching-and-review.md#feature-switches-and-defaults) |

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in BCP 14 (RFC 2119, RFC 8174) when, and only when, they appear in all capitals, as shown here.

## Contents

- [Context and problem statement](#context-and-problem-statement)
- [Considered options](#considered-options)
- [Decision outcome](#decision-outcome)
  - [Consequences](#consequences)
- [More information](#more-information)

## Context and problem statement

Every fork feature sits behind a switch, and the switch rules ask for a yaml setting and a nodetool toggle. Apache Cassandra switches its own configurable startup checks under the `startup_checks` block of `cassandra.yaml`, each by its name with the key `enabled`, and none of them has a nodetool command. Apache Cassandra 6.0 loads custom startup checks by name under the same block. A startup check has run before nodetool can reach the node. The design had to know which form the switch of the commit log disk check takes.

## Considered options

1. An entry under the stock `startup_checks` block, named `check_commitlog_shared_disk`, with the key `enabled`, read at start only. No nodetool command. It needs one constant in the stock enum of startup check names and one line in the daemon that registers the check.
2. A top level yaml key of its own, with a pair of nodetool commands that enable and disable the check, where enabling at runtime runs the check once. It needs a field in the stock configuration class and two entries in the stock command list, and a settings row, two commands and an MBean exist on every node, switch on or off.

## Decision outcome

Chosen option: "An entry under the stock `startup_checks` block", because it is how Apache Cassandra switches every startup check, it ports to the 6.0 line with the same yaml and no stock edit, and a nodetool toggle cannot change a check that has already run.

The switch of the commit log disk check MUST be the key `enabled` of the entry `check_commitlog_shared_disk` under `startup_checks` in `cassandra.yaml`. The feature MUST NOT add a top level yaml key. The feature MUST NOT add a nodetool command. The nodetool toggle that the switch rules ask of every fork feature does not apply to this feature.

### Consequences

- Good: one new name under a stock block, and no settings row, command or MBean on a node that does not use the feature.
- Bad: the check cannot be switched or run again without a restart, and this feature departs from the rule that every fork feature has a nodetool toggle.

## More information

The design record in `docs/design/CLD-commitlog-disk-check/` applies this decision in section 3, Stock behaviour preservation, in REQ-CLD-005 and in waiver 3. Whether the switch rules should name startup checks as a standing exception is a follow-up in section 15 of that record.
