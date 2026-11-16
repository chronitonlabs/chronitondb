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

# 0016. A node starts without the build details view when the start step of the view fails

| Field | Value |
|---|---|
| Document type | Record (ISO/IEC/IEEE 15289), MADR |
| Status | Accepted |
| Date | 2026-11-16 |
| Deciders | The maintainers |
| References | Issue #141, the feature spec in `docs/design/BUILD-build-details-view/`, [quality-requirements.md, Automatic fallbacks are opt-in and counted](../process/quality-requirements.md#automatic-fallbacks-are-opt-in-and-counted), decision records 0013, 0014 and 0019 |

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in BCP 14 (RFC 2119, RFC 8174) when, and only when, they appear in all capitals, as shown here.

## Contents

- [Context and problem statement](#context-and-problem-statement)
- [Considered options](#considered-options)
- [Decision outcome](#decision-outcome)
  - [Consequences](#consequences)
- [More information](#more-information)

## Context and problem statement

A node whose configuration turns the build details view on runs the start step of the view at start. That step builds the view, creates the read counter and registers the keyspace `system_views` with the view added. Any of these can fail. The feature had to know what the node does then: go on with its start, or stop. The quality rules ask that an automatic fallback is off by default and has a yaml setting, a nodetool toggle, a metric that counts each use and a rate-limited log line. A node that hides the view holds no metric of the feature (decision record 0014), so the feature also had to know whether a failed start step is counted.

## Considered options

1. The node goes on with its start. The view stays hidden, and the log holds one error that names the view.
2. The node refuses to start when its switch is on and the view cannot be shown.

## Decision outcome

Chosen option: "The node goes on with its start. The view stays hidden, and the log holds one error that names the view", because a fault of one read-only table that no other part of the node depends on then never keeps a node down, as decision record 0013 chose for a view turned on before the final gate.

When a throwable is thrown in the start step of the view after the step read the setting as `true`, the start step MUST return normally and the node MUST go on with its start. The node MUST keep the view hidden until its next start. It MUST log one ERROR line that names the view. The node MUST NOT refuse to start because the start step of the view failed. Decision record 0019 narrows this to a throwable that Apache Cassandra's JVM stability check returns from.

The feature counts no failed start step. The node holds no metric and no MBean of the feature after the failure, as on every node that hides the view. The failure has no yaml setting and no nodetool toggle of its own. This is a departure from the rule on automatic fallbacks in quality-requirements.md, made for this feature only. The ERROR line is written once at a start, so it needs no rate limit.

### Consequences

- Good: no fault in the code that shows the view stops a node.
- Good: the failure is visible where an operator looks first after a start, in the log, with the name of the view.
- Bad: the failure shows in the log only. An operator who does not read the start log learns it from the answer for a table that does not exist.
- Bad: no metric counts the failure, so a monitoring tool that reads metrics alone does not see it.
- Bad: `system_views.settings` shows `true` on a node that hides the view after a failure, as it does before the final gate.

## More information

The feature spec in `docs/design/BUILD-build-details-view/feature-spec.md` applies this decision in FREQ-BUILD-027, FREQ-BUILD-028 and FREQ-BUILD-036, in its sections 2.2 and 2.8 and in problem 1 of its section 4.
