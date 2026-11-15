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

# 0004. The commit log disk check is off by default

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

The commit log disk check warns at startup when the commit log directory is on the same file system as a data directory. A node that sets neither directory keeps both under one storage directory, so the default layout shares a file system. A new warning in the start log changes what a stock node logs, and the switch rules make such a feature off by default, with `nodetool version` the one exception. The design had to know whether this check follows the rule or becomes a second exception.

## Considered options

1. Off by default. An operator switches the check on in `cassandra.yaml`. A node that does not name the check logs what a stock node logs.
2. On by default, as a second exception to the off by default rule. Every node on the default layout logs the warning at each start, development and test nodes included.

## Decision outcome

Chosen option: "Off by default", because stock behaviour stays unchanged for everyone who does not use the feature, and a check that is on by default would warn on every default install.

The commit log disk check MUST be off on a node whose configuration does not switch it on. While it is off, the check MUST NOT log a line or register a metric.

### Consequences

- Good: the start log of a node that does not use the feature is the stock one, and the off by default rule keeps its single exception.
- Bad: an operator who does not know the check never sees the warning. The reference page and the release notes are how operators learn of it.

## More information

The design record in `docs/design/CLD-commitlog-disk-check/` applies this decision in section 3, Stock behaviour preservation, and in REQ-CLD-004 and REQ-CLD-005.
