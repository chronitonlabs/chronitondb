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

# 0016. The node uptime view leaves its entry in ChronitonDB's configuration file to the item that creates the file

| Field | Value |
|---|---|
| Document type | Record (ISO/IEC/IEEE 15289), MADR |
| Status | Accepted |
| Date | 2026-11-17 |
| Deciders | The maintainers |
| References | Issue #144, the feature spec in `docs/design/UPTIM-node-uptime-view/`, [release.md, The configuration file](../process/release.md#the-configuration-file) |

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in BCP 14 (RFC 2119, RFC 8174) when, and only when, they appear in all capitals, as shown here.

## Contents

- [Context and problem statement](#context-and-problem-statement)
- [Considered options](#considered-options)
- [Decision outcome](#decision-outcome)
  - [Consequences](#consequences)
- [More information](#more-information)

## Context and problem statement

[release.md](../process/release.md#the-configuration-file) gives ChronitonDB a configuration file of its own, `conf/cassandra_chronitondb.yaml`, which carries ChronitonDB's own settings. Apache Cassandra's `conf/cassandra.yaml` and `conf/cassandra_latest.yaml` stay untouched. The node uptime view has one setting, `uptime_view_enabled`. The file does not exist on the line `chronitondb-sandbox` yet, and no item of this feature creates it. The feature spec had to know who adds the setting to the file.

## Considered options

1. The item that creates the file adds the setting.
2. The last item of this feature adds the setting, where the file exists when that item's pull request is opened.

## Decision outcome

Chosen option: "The item that creates the file adds the setting", because the design records of the release version and of the commit log disk check on this line already leave their settings to that item, and because the feature then has no requirement that depends on whether another item has landed.

The node uptime view MUST NOT change a file under `conf/`.

The item that creates `conf/cassandra_chronitondb.yaml` adds `uptime_view_enabled` to it, commented out with its default `false`. Adding it is a candidate issue for a maintainer to open. No item of this feature depends on it.

### Consequences

- Good: the feature follows the two design records already merged on the line.
- Good: no pull request of this feature touches a configuration file.
- Bad: until that item lands, no shipped yaml file names `uptime_view_enabled`, and an operator finds it on the reference page of the feature only.
- Bad: the entry rests on a candidate issue that a maintainer has to open.

## More information

The feature spec applies this decision in section 2.7 and in FREQ-UPTIM-040. Problem 7 of its section 4 names the check of the changed files of each pull request.
