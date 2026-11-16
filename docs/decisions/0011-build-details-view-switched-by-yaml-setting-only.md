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

# 0011. The build details view is switched by its yaml setting only

| Field | Value |
|---|---|
| Document type | Record (ISO/IEC/IEEE 15289), MADR |
| Status | Accepted |
| Date | 2026-11-16 |
| Deciders | The maintainers |
| References | Issue #141, the feature spec in `docs/design/BUILD-build-details-view/`, [branching-and-review.md, Feature switches and defaults](../process/branching-and-review.md#feature-switches-and-defaults), [quality-requirements.md](../process/quality-requirements.md) |

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in BCP 14 (RFC 2119, RFC 8174) when, and only when, they appear in all capitals, as shown here.

## Contents

- [Context and problem statement](#context-and-problem-statement)
- [Considered options](#considered-options)
- [Decision outcome](#decision-outcome)
  - [Consequences](#consequences)
- [More information](#more-information)

## Context and problem statement

The switch rules ask for a yaml setting and a nodetool toggle for every feature. For the build details view that meant a field in the configuration, two nodetool commands and an MBean the commands write to. All of them would exist on every node, also on one whose switch is off: Apache Cassandra lists every configuration field in `system_views.settings` and in its start log, `nodetool help` lists every command, and the JMX server holds every MBean. The rule that a node with a feature off behaves exactly as Apache Cassandra allows none of the three. The feature had to know which of them a node with the switch off may show.

## Considered options

1. The yaml setting, the two nodetool commands and the MBean. Three things are present on every node. The switch changes while the node runs.
2. The yaml setting only. One thing is present on every node, the settings row with its line in the start log. A change of the switch needs a restart.
3. A JVM start flag in place of the yaml setting. Nothing is present on a node while the switch is off. The feature has no yaml setting and no toggle.

## Decision outcome

Chosen option: "The yaml setting only", because a node with the switch off then differs from Apache Cassandra by one settings row, and the switch is still set where operators set every other switch.

The switch of the build details view is the yaml setting `build_view_enabled` and nothing else. The node MUST read it at start, and a change MUST take a restart of the node to have effect. The feature MUST NOT add a nodetool command, or an MBean that reads or changes the switch. Whether the feature has a metric, which Apache Cassandra registers as an MBean, is decided in decision record 0014. The settings row and the line of the start log that prints the configuration are accepted on every node, whatever the switch says. This is a departure from the rule that every feature has a nodetool toggle, made for this view only.

### Consequences

- Good: with the switch off, a node shows one trace of the feature, the settings row with its line in the start log, where the first option shows three.
- Good: the state of the view is fixed from start to stop. The feature needs no lock, no step that hides the view under running statements, and no error for a refused toggle.
- Good: a rolling upgrade restarts every node anyway, so the setting can be put in place when a node gets its new binary, before it starts on it.
- Bad: an operator cannot show or hide the view on a running node. Each change costs a restart of that node.
- Bad: the rule that a runtime change of a setting is logged with its old and new value has no case here, since no runtime change exists. The start log shows the value the node started with.
- Bad: the view departs from the switch rules, so an operator who knows the toggles of other features finds none for this one. The reference page has to say so.

## More information

The feature spec in `docs/design/BUILD-build-details-view/feature-spec.md` applies this decision in FREQ-BUILD-011, FREQ-BUILD-012 and FREQ-BUILD-025 and in its sections 2.2 and 2.8.
