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

# 0013. enableuptimeview is refused on a node that is between on and off

| Field | Value |
|---|---|
| Document type | Record (ISO/IEC/IEEE 15289), MADR |
| Status | Accepted |
| Date | 2026-11-17 |
| Deciders | The maintainers |
| References | Issue #144, the feature spec in `docs/design/UPTIM-node-uptime-view/`, decision record 0011 |

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in BCP 14 (RFC 2119, RFC 8174) when, and only when, they appear in all capitals, as shown here.

## Contents

- [Context and problem statement](#context-and-problem-statement)
- [Considered options](#considered-options)
- [Decision outcome](#decision-outcome)
  - [Consequences](#consequences)
- [More information](#more-information)

## Context and problem statement

A command of the node uptime view that a step ends part way leaves the node between on and off, and the feature does not undo the steps already done (decision record 0011). Such a node refuses every read of the view. `nodetool disableuptimeview` brings it to the off state. The feature spec had to know what `nodetool enableuptimeview` does on such a node: refuse, or finish turning the view on.

## Considered options

1. `enableuptimeview` is refused on a node that is between on and off, with a text that names `disableuptimeview`.
2. `enableuptimeview` runs the steps that turn the view off, then the steps that turn it on.

## Decision outcome

Chosen option: "`enableuptimeview` is refused", because the feature then keeps one way back from a failed command, the one decision record 0011 chose, and has no second way to prove.

If `nodetool enableuptimeview` runs against a node that is between on and off, the node MUST refuse the call with the text `The node uptime view is between on and off on this node. Run nodetool disableuptimeview first.` and MUST leave the node as it is.

While a node is between on and off, it MUST refuse every read of the view. A statement on the view that is no read follows the table listing of the node. Where the node still lists the view, the statement gets the answer of a node whose view is on: a `GRANT` on the view works, and a write is refused as a write to a read-only table. Where the node does not list the view, the statement gets the answer of a node whose view is off.

### Consequences

- Good: a switch change to on always starts from a node whose view is off, which holds no read counter. So each one creates a new counter at 0.
- Good: every command that changes a node logs its INFO line, since the refusal changes nothing.
- Bad: the operator runs two commands to turn the view on after a failed command, `disableuptimeview` and then `enableuptimeview`.
- Bad: while a node is between on and off, a statement that is no read can get the answer of a view that is on, while every read is refused.

## More information

The feature spec applies this decision in the command table of section 2.2 and in FREQ-UPTIM-038, FREQ-UPTIM-041 and FREQ-UPTIM-043. Problem 6 of its section 4 names the tests.
