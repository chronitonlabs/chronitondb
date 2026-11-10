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

# 0002. What nodetool version prints on a ChronitonDB node

| Field | Value |
|---|---|
| Document type | Record (ISO/IEC/IEEE 15289), MADR |
| Status | Proposed |
| Date | 2026-11-10 |
| Deciders | The maintainers |
| References | Issue #67, the design record in `docs/design/67-let-operators-see-a-node-s/`, [release.md, What nodetool version shows](../process/release.md#what-nodetool-version-shows) |

## Contents

- [Context and problem statement](#context-and-problem-statement)
- [Considered options](#considered-options)
- [Decision outcome](#decision-outcome)
  - [Consequences](#consequences)
- [More information](#more-information)

## Context and problem statement

The release process page settles that `nodetool version` on a ChronitonDB node shows the release version, for example `5.0-chronitondb3`, and the git SHA of the build, with no Apache release line. It does not settle the label of the first line, or whether the git SHA line needs the `--verbose` flag that stock Apache Cassandra requires for it. Operators and their scripts read this output on every node during a rolling upgrade, so the label and the line count decide what keeps working.

## Considered options

1. Keep the stock labels. The first line is `ReleaseVersion: ` followed by the release version. The `GitSHA: ` line appears only with `--verbose`, as in stock.
2. Print both lines always, `ReleaseVersion: ` and `GitSHA: `, with or without `--verbose`. This changes the line count and makes a stock test assertion fail, so that test would have to change.
3. A new label, `ChronitonDB: ` followed by the release version, in place of the `ReleaseVersion: ` line. The `GitSHA: ` line as in option 1.

## Decision outcome

Chosen option: "Keep the stock labels", because scripts that read `ReleaseVersion:` keep working, the git SHA stays a detail shown on request as stock Apache Cassandra shows it, and no stock test changes.

On a ChronitonDB node with the feature on, `nodetool version` MUST print one line, `ReleaseVersion: ` followed by the node's ChronitonDB release version, for example `ReleaseVersion: 5.0-chronitondb3`. With `--verbose` it MUST print a second line, `GitSHA: ` followed by the git SHA of the build. Without `--verbose` it MUST NOT print the git SHA. No stock test changes for this feature.

### Consequences

- Good: a script that reads the `ReleaseVersion:` label finds a value on Apache Cassandra and ChronitonDB nodes alike, and the stock distributed test of `nodetool version` passes unchanged.
- Bad: a script that expects an Apache Cassandra version number after that label reads a ChronitonDB release version on a ChronitonDB node. The feature switch restores the Apache value for an operator who needs it.

## More information

The design record in `docs/design/67-let-operators-see-a-node-s/` implements this decision in its requirements REQ-1 and REQ-2 and in its Stock behaviour preservation section.
