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

# 0009. A startup check named in cassandra.yaml shows the source yaml

| Field | Value |
|---|---|
| Document type | Record (ISO/IEC/IEEE 15289), MADR |
| Status | Accepted |
| Date | 2026-11-15 |
| Deciders | The maintainers |
| References | Issue #117, the design record in `docs/design/SCV-startup-checks-view/`, [branching-and-review.md, Feature switches and defaults](../process/branching-and-review.md#feature-switches-and-defaults) |

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in BCP 14 (RFC 2119, RFC 8174) when, and only when, they appear in all capitals, as shown here.

## Contents

- [Context and problem statement](#context-and-problem-statement)
- [Considered options](#considered-options)
- [Decision outcome](#decision-outcome)
  - [Consequences](#consequences)
- [More information](#more-information)

## Context and problem statement

Each row of the startup checks view has a column `source` that says where the on or off value of the check came from. `cassandra.yaml` can name a check under `startup_checks` without the key `enabled`, for example to give the ownership check its token. Apache Cassandra writes the key into such an entry with the default of the check while it loads the configuration. After that, the entry looks the same as one that wrote the key. The design had to know what `source` shows for such an entry.

## Considered options

1. Show `yaml` for every check that `cassandra.yaml` names under `startup_checks`, with or without the key `enabled`. The view reads what Apache Cassandra holds in memory.
2. Tell the two apart, and show `default` for an entry without the key. That needs new code in the stock loading of the configuration, which then runs at every node start, with the view on or off.

## Decision outcome

Chosen option: "Show `yaml` for every check that `cassandra.yaml` names", because the on or off value is right in both cases and no code is added to the loading of the configuration.

The row of a switchable check that `cassandra.yaml` names under `startup_checks`, and whose start option is not set, MUST show `source` as `yaml`. The feature MUST NOT add code to the loading of the configuration that notes which entries wrote the key `enabled`.

### Consequences

- Good: a node loads its `startup_checks` block exactly as Apache Cassandra does, with the view on or off.
- Bad: for an entry without the key `enabled`, the view shows `yaml` although the value is the default of the check. The reference page states this as a known limitation.

## More information

The design record in `docs/design/SCV-startup-checks-view/` applies this decision in section 1, in REQ-SCV-012 and in section 13, Documentation.
