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

# 0003. Where the tests prove the release version before a package exists

| Field | Value |
|---|---|
| Document type | Record (ISO/IEC/IEEE 15289), MADR |
| Status | Accepted |
| Date | 2026-11-11 |
| Deciders | The maintainers |
| References | Issue #67, the design record in `docs/design/67-let-operators-see-a-node-s/`, [release.md, What nodetool version shows](../process/release.md#what-nodetool-version-shows), [release.md, Packaging](../process/release.md#packaging), decision record 0002 |

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in BCP 14 (RFC 2119, RFC 8174) when, and only when, they appear in all capitals, as shown here.

## Contents

- [Context and problem statement](#context-and-problem-statement)
- [Considered options](#considered-options)
- [Decision outcome](#decision-outcome)
  - [Consequences](#consequences)
- [More information](#more-information)

## Context and problem statement

The release process page says that the tests of the feature that shows the release version in `nodetool version` prove the version and the git SHA on a built package. No package exists on the `chronitondb-sandbox` line yet, because the packaging item has not created `packaging/`. The item that builds the feature had to know where its tests prove both until a package exists.

## Considered options

1. On the built jar now. The item's tests read the release version from the jar the build made and run nodetool against a node started from it. The package test comes with the packaging item, when a package exists.
2. Wait for the packaging item, then prove both on the package in this item. The item merges only after a package exists.
3. On the binary tarball the build makes today, as an interim package. A test unpacks the tarball and runs `bin/nodetool version` against a node started from it. The packaging item still owes the package test, because the tarball is not what the release process page calls a package.

## Decision outcome

Chosen option: "On the built jar now", because the item ships without waiting for packaging, the jar is what a package wraps, and the packaging item adds the package test once there is a package to test.

The tests of the item MUST prove the release version and the git SHA on the built jar. The packaging item MUST add a test that installs the package and runs `nodetool version` against a node started from it. The item MUST NOT wait for the packaging item.

### Consequences

- Good: the item merges now, and its test list and Planned file list stay as they are.
- Bad: the release process page is met in two steps, and until the packaging item adds its test the release engineer checks `nodetool version` on the installed candidate by hand.

## More information

The design record in `docs/design/67-let-operators-see-a-node-s/` applies this decision in section 14, Testing, item 1, and in section 15, Not covered and follow-ups, item 4.
