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

# 0007. The build details view builds the release version key and its reader

| Field | Value |
|---|---|
| Document type | Record (ISO/IEC/IEEE 15289), MADR |
| Status | Accepted |
| Date | 2026-11-16 |
| Deciders | The maintainers |
| References | Issue #141, the feature spec in `docs/design/BUILD-build-details-view/`, the design record in `docs/design/VER-release-version/`, decision record 0002 |

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in BCP 14 (RFC 2119, RFC 8174) when, and only when, they appear in all capitals, as shown here.

## Contents

- [Context and problem statement](#context-and-problem-statement)
- [Considered options](#considered-options)
- [Decision outcome](#decision-outcome)
  - [Consequences](#consequences)
- [More information](#more-information)

## Context and problem statement

The build details view shows a node's ChronitonDB release version from CQL. That value comes from a key the build writes and from a reader class. The design record of `nodetool version` in `docs/design/VER-release-version/` defines both, in its requirements REQ-VER-006, REQ-VER-007, REQ-VER-025 and REQ-VER-033. Neither is on the line yet, and no work on that record's code is planned. The view had to know where its release version comes from.

## Considered options

1. The view waits. Its first milestone starts only once the code of the `nodetool version` design record is on the line, and the view calls that reader.
2. The view's own work adds the build key and the reader, as the `nodetool version` design record defines them. The `nodetool version` work then finds them on the line and reuses them.

## Decision outcome

Chosen option: "The view's own work adds the build key and the reader", because the view can then be built now, and one key and one reader still serve both the view and `nodetool version`.

The work on the build details view MUST add the build key `ReleaseVersion` and the reader class as REQ-VER-006, REQ-VER-007, REQ-VER-025 and REQ-VER-033 of the `nodetool version` design record define them, with no change to their behaviour. The view and `nodetool version` MUST read the release version through that one reader. The `nodetool version` design record MUST be updated through change control before its code starts, so that it reuses the key, the reader and the reader's test in place of adding them.

### Consequences

- Good: the view does not wait for other work, and both outputs show the same release version because they share the reader.
- Bad: the build file changes in the view's work, and an approved design record needs a change control update to its planned file list and to the delta entry it names for the build file.

## More information

The feature spec in `docs/design/BUILD-build-details-view/feature-spec.md` applies this decision in FREQ-BUILD-006 and FREQ-BUILD-007 and in its section 2.7. The design record in `docs/design/VER-release-version/` holds the four requirements this record names.
