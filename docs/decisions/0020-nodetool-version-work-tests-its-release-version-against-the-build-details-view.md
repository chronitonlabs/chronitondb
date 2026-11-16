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

# 0020. The nodetool version work adds the test that compares its release version with the build details view

| Field | Value |
|---|---|
| Document type | Record (ISO/IEC/IEEE 15289), MADR |
| Status | Accepted |
| Date | 2026-11-16 |
| Deciders | The maintainers |
| References | Issue #141, the feature spec in `docs/design/BUILD-build-details-view/`, the design record in `docs/design/VER-release-version/`, decision records 0002 and 0007 |

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in BCP 14 (RFC 2119, RFC 8174) when, and only when, they appear in all capitals, as shown here.

## Contents

- [Context and problem statement](#context-and-problem-statement)
- [Considered options](#considered-options)
- [Decision outcome](#decision-outcome)
  - [Consequences](#consequences)
- [More information](#more-information)

## Context and problem statement

The `release_version` column of the build details view and the `ReleaseVersion:` line that decision record 0002 defines for `nodetool version` are meant to show one value. Decision record 0007 has both read it through one reader class. On this line `nodetool version` prints the Apache Cassandra version until the code of its design record is built, so no test can compare the two values yet. The feature had to know which work adds that test, and whether the view waits for it.

## Considered options

1. The `nodetool version` work adds the requirement and the test, in the change control update of its design record.
2. The build details view adds the test, and its final milestone starts only once the `nodetool version` code is on the line.
3. No test compares the two values. The shared reader, with its own tests, is the proof.

## Decision outcome

Chosen option: "The `nodetool version` work adds the requirement and the test, in the change control update of its design record", because the view is then not held up by the code of another feature, and the two values are still compared by a test as soon as one can be written.

The change control update of the design record of `nodetool version`, which decision record 0007 requires before that code starts, MUST add a requirement that the `ReleaseVersion:` line of `nodetool version` equals the `release_version` column of the build details view on the same node. It MUST add a test that proves that requirement on a node that shows the view.

The final gate of the build details view MUST NOT wait for that test. Until the `nodetool version` code is on the line, the tests of the reader and of the `release_version` column are the proof for the value the view shows.

### Consequences

- Good: operators get the view without a wait for the `nodetool version` code.
- Good: once that code is built, a change that gives `nodetool version` its own way to the release version fails a test.
- Bad: until that code is built, no test compares the two values, and the shared reader is the only proof that they are one.
- Bad: the requirement and the test live in the design record of another feature, so the update of that record has to carry them.

## More information

The feature spec in `docs/design/BUILD-build-details-view/feature-spec.md` carries this decision in its section 2.7, in test 3 of its section 4.1 and in risk R5 of its section 9.
