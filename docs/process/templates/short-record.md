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

# Short record: #{issue} {title}

| Field | Value |
|---|---|
| Title | {title} |
| Document type | Record (ISO/IEC/IEEE 15289) |
| Status | Draft, Approved or Superseded |
| Version | {n} |
| Author | {GitHub username} |
| Approver | The maintainer who merges the pull request |
| References | Issue #{issue}. |
| Areas | {one or more areas of [areas.md](../areas.md), joined by commas} |
| Tier | {the first line `tools/chronitondb/doclint.py tier` prints for the change} |

Revision history, one row for each version:

| Version | Date | Change | Decision record |
|---|---|---|---|
| 1 | {RFC 3339 date} | First version | {the id of the decision record behind this version, or None} |

Full history in git: [commits of this file]({the address `tools/chronitondb/doclint.py history --write` puts here})

Location: `docs/design/<issue>-<slug>/short-record.md`. Process: [the short path](../branching-and-review.md#the-short-path). The pull request that carries this record also carries the code and the tests.

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in BCP 14 (RFC 2119, RFC 8174) when, and only when, they appear in all capitals, as shown here.

The Tier row records the tier the change took and why. It is the first line that `tools/chronitondb/doclint.py tier --repo . --base origin/<line>` prints for the change, copied as printed. The process document check works it out again and refuses a row that differs.

## Contents

- [1. Impact](#1-impact)
- [2. What changes](#2-what-changes)
- [3. Decisions by the maintainers](#3-decisions-by-the-maintainers)
- [4. Test plan](#4-test-plan)
- [5. Where problems could occur](#5-where-problems-could-occur)

## 1. Impact

{The need, in a few lines: who needs the change and what they lack without it.}

## 2. What changes

{The precise interface the change adds or changes, one item per line: an id `REQ-n`, one EARS shape, one BCP 14 key word and its source. For example: REQ-1: The widget table MUST have the columns name of type text and size of type int. Source: issue #42.}

## 3. Decisions by the maintainers

{Each visible choice of the change, such as a name, a default or what an operator sees, with the answer the maintainers gave and its date. The author asks them all once, in one batch, before writing. A change with no visible choice says so in one line.}

## 4. Test plan

{One line per test: an id `TEST-n`, the test class and method, and each `REQ-n` of section 2 it proves. For example: TEST-1: WidgetTableTest.testColumns proves REQ-1. Every `REQ-n` of section 2 is named here.}

## 5. Where problems could occur

{Where the change could go wrong if a part of it is wrong, worst case first: what a user or an operator would see, on which request path, and from which part of the change. Never "None" or "Low", and never an argument that the change is safe. After the section of the same name in Ubuntu's stable release update template.}
