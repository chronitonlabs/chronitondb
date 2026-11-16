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

# 0008. The build details view obeys Apache compatibility mode through an internal check

| Field | Value |
|---|---|
| Document type | Record (ISO/IEC/IEEE 15289), MADR |
| Status | Accepted |
| Date | 2026-11-16 |
| Deciders | The maintainers |
| References | Issue #141, the feature spec in `docs/design/BUILD-build-details-view/`, [release.md, The version a running node reports](../process/release.md#the-version-a-running-node-reports) |

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in BCP 14 (RFC 2119, RFC 8174) when, and only when, they appear in all capitals, as shown here.

## Contents

- [Context and problem statement](#context-and-problem-statement)
- [Considered options](#considered-options)
- [Decision outcome](#decision-outcome)
  - [Consequences](#consequences)
- [More information](#more-information)

## Context and problem statement

A node in Apache compatibility mode reports as plain Apache Cassandra, so it must not show the build details view, whatever the view's own switch says. Apache compatibility mode is named in the release rules only. No code, no setting and no planned work exist for it. The view had to obey a mode that is not built.

## Considered options

1. One internal check. The view asks one fork class whether Apache compatibility mode is on. The class answers off until the work that builds the mode fills it. No setting and no command exist for it.
2. The view's last milestone waits for the mode, and the view's switch refuses to turn on until the mode ships.
3. The view's work adds the yaml setting `apache_compatibility_mode`, off by default, which for now hides only this view.

## Decision outcome

Chosen option: "One internal check", because the rule that the mode hides the view is built and tested now, nothing new becomes visible to operators, and building the mode stays out of this feature.

The view MUST ask one internal check whether Apache compatibility mode is on, and MUST be hidden while the check answers on, whatever the view's switch says. The check MUST answer off on every node until the work that builds Apache compatibility mode changes it. This feature MUST NOT add a yaml setting, a system property, a nodetool command or an MBean attribute that changes the check's answer. Tests MUST prove that the view is hidden while the check answers on, through a test-only way to set the answer.

### Consequences

- Good: the work that builds Apache compatibility mode has one place to fill, and the view obeys the mode from that day with no change of its own.
- Bad: until that work, the proof rests on tests that set the check's answer. No operator can put a node in the mode, so the rule is not proven on a real mode.

## More information

The feature spec in `docs/design/BUILD-build-details-view/feature-spec.md` applies this decision in FREQ-BUILD-014 and FREQ-BUILD-019 and in its section 2.2.
