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

# 0010. No test of what the startup checks log in the startup checks view item

| Field | Value |
|---|---|
| Document type | Record (ISO/IEC/IEEE 15289), MADR |
| Status | Accepted |
| Date | 2026-11-15 |
| Deciders | The maintainers |
| References | Issue #117, the design record in `docs/design/SCV-startup-checks-view/`, decision record [0003](0003-release-version-tests-before-a-package-exists.md) |

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in BCP 14 (RFC 2119, RFC 8174) when, and only when, they appear in all capitals, as shown here.

## Contents

- [Context and problem statement](#context-and-problem-statement)
- [Considered options](#considered-options)
- [Decision outcome](#decision-outcome)
  - [Consequences](#consequences)
- [More information](#more-information)

## Context and problem statement

One acceptance criterion of the startup checks view says that which checks run at node start, and what they log, stay as in Apache Cassandra. The design record tests the first half: which checks the daemon registers, and that the list of checks and their options are the same with the view on as with it off. It has no test for the second half. No test on this line can run an Apache Cassandra binary and compare the lines its checks log. The design had to know whether that half needs a test of its own.

## Considered options

1. No test of what the checks log. The coverage file shows that half of the criterion as not tested.
2. The in-JVM distributed test also compares the lines the checks log on a node with the view on and on a node with it off.

## Decision outcome

Chosen option: "No test of what the checks log", because the comparison of option 2 is between two nodes of one build, so it cannot show a difference from Apache Cassandra, and it would depend on the exact text of lines that carry values of the node, such as a directory or a port.

The requirement that the feature does not change what a startup check logs, REQ-SCV-036 of the design record, has no test. Its row in the coverage file MUST read Excluded and name this record.

### Consequences

- Good: no test of the item depends on the text of a log line of a stock check.
- Bad: a change to what a startup check logs passes every test of the item. The Planned file list of the design record holds no file with the code of a check, so the item itself has no place to make such a change.

## More information

The design record in `docs/design/SCV-startup-checks-view/` applies this decision in REQ-SCV-036, in section 14, Testing, and in the coverage file next to it. Decision record 0003 took the same course for the release version: the tests prove what a test on the line can reach.
