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

# 0011. A switch change of the node uptime view that fails is not undone

| Field | Value |
|---|---|
| Document type | Record (ISO/IEC/IEEE 15289), MADR |
| Status | Accepted |
| Date | 2026-11-17 |
| Deciders | The maintainers |
| References | Issue #144, the feature spec in `docs/design/UPTIM-node-uptime-view/`, decision record 0009 |

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in BCP 14 (RFC 2119, RFC 8174) when, and only when, they appear in all capitals, as shown here.

## Contents

- [Context and problem statement](#context-and-problem-statement)
- [Considered options](#considered-options)
- [Decision outcome](#decision-outcome)
  - [Consequences](#consequences)
- [More information](#more-information)

## Context and problem statement

A nodetool command of the node uptime view changes a running node in several steps. It first turns the view on or off, which is three steps: the read counter, the registered tables of `system_views` and the view flag that the view reads at each read. Then it sets the running value of the setting and logs the change. A step can throw. The table listings, the read counter, the view flag and the running value can then disagree. The feature spec had to know what the node does after such a step.

## Considered options

1. The command stops at the step that threw and reports the error. The steps already done stay.
2. The command reverses the steps already done, then reports the error.

## Decision outcome

Chosen option: "The command stops at the step that threw and reports the error", because the feature then has no undo code, which could fail too and leave the same state behind more code.

If a step of a command of the feature throws, the command MUST stop there, print the error and exit with a status other than 0. The feature MUST NOT undo the steps already done.

`nodetool disableuptimeview` is the way back. It MUST run every step that turns the view off, whatever the running value says, so that it brings such a node to the off state: the view off, no metric of the feature and the running value `false`.

The view flag MUST be the last step of turning the view on and the first step of turning it off. So a node on which turning the view on or off ended part way has its view flag off, and refuses every read of the view with the error that names the switch.

### Consequences

- Good: one failure rule, with no code that handles a failure of the failure handling.
- Good: one command always reaches the off state.
- Bad: after a step that threw, a node can list the view or hold the read counter while it refuses reads of the view, and its settings row can show a value that does not match. It stays so until a command of the feature succeeds on that node.
- Bad: the operator has to read the error of the command and run `disableuptimeview`.

## More information

The feature spec applies this decision in section 2.2 and in FREQ-UPTIM-029 and FREQ-UPTIM-036. Problem 6 of its section 4 names the tests.
