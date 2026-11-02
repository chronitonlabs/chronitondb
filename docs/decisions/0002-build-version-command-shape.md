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

# 0002. The shape of the build version command

| Field | Value |
|---|---|
| Document type | Record (ISO/IEC/IEEE 15289), MADR |
| Status | Accepted |
| Date | 2026-11-02 |
| Deciders | The maintainers |
| References | [Feature spec: Build version command](../design/BVER-build-version-command/feature-spec.md), [release.md](../process/release.md#version-numbers), [conventions.md](../process/conventions.md#names), [branching-and-review.md](../process/branching-and-review.md#feature-switches-and-defaults) |

## Context and problem statement

ChronitonDB needs a nodetool command that prints the ChronitonDB build version. Stock `nodetool version` asks the node over JMX for Apache's release version and prints `ReleaseVersion: ` followed by it (`src/java/org/apache/cassandra/tools/nodetool/Version.java:36` on `chronitondb-sandbox`), and neither the build nor the node knows a ChronitonDB version today. The question was the shape of the command: what it prints and where the version comes from.

## Considered options

1. One line from the node. The command connects to the node over JMX, reads the ChronitonDB build version from a new MBean in the `org.chronitondb` domain and prints `ChronitonDBVersion: ` followed by the version.
2. Three lines from the node. As option 1, and the command also prints the Apache base version and the git SHA.
3. One line from the nodetool jar. The command prints the version of the nodetool installation it runs from, without connecting to a node.

## Decision outcome

Chosen option: "One line from the node", because it answers the question an operator asks during a rolling upgrade, which ChronitonDB release a given node runs, it keeps the shape of stock `nodetool version`, and it keeps the feature's switch on the node, where every feature switch lives.

1. The build MUST write a `ChronitonDBVersion` entry into `version.properties`, next to Apache's `CassandraVersion`, in the form `<Apache version>-chronitondb<n>` of [release.md](../process/release.md#version-numbers), with `n` the ChronitonDB release number the build is given and `0` for a build given none.
2. `nodetool chronitondbversion` MUST connect to the node like every other nodetool command, read the version from the node's MBean in the `org.chronitondb` JMX domain and print the one line `ChronitonDBVersion: ` followed by the version.
3. The command MUST NOT print the Apache base version or the git SHA. Stock `nodetool version` keeps printing those.
4. With the feature's switch off, the node MUST refuse the read with an error that names the switch.

### Consequences

- Good: the operator sees the version of the node asked, in one line, the same way `nodetool version` works. One MBean and one command, and no change to any stock output.
- Bad: the node side needs a startup hook and a `Config` field, two stock edits with delta entries. An operator who wants the Apache version too runs `nodetool version` as well.

## More information

The feature spec, [Build version command](../design/BVER-build-version-command/feature-spec.md), carries the architecture and the feature requirements that follow from this decision. Option 2 was rejected because its base version line repeats what `nodetool version` prints. Option 3 was rejected because it prints the version of the operator's own installation, which differs from the node's during a rolling upgrade, and because nodetool loads no yaml settings, so the switch could not live on the node.
