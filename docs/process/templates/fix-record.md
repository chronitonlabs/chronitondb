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

# Fix: #{issue} {title}

| Field | Value |
|---|---|
| Title | {title} |
| Document type | Record (ISO/IEC/IEEE 15289) |
| Status | Draft, Approved or Superseded |
| Version | {n} |
| Author | Designer: {GitHub username} |
| Approver | The maintainer who merges the pull request |
| References | Issue #{issue}. Apache JIRA `CASSANDRA-<n>` if stock is affected. Delta entry. |

Change history: the git history of this file.

Location: `docs/design/<issue>-<slug>/`, with the coverage file `ac-coverage.md` next to it. Process: [maintenance.md](../maintenance.md). A security fix stays in its private advisory until disclosure, see [security.md](../security.md).

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in BCP 14 (RFC 2119, RFC 8174) when, and only when, they appear in all capitals, as shown here.

## 1. Symptom

{What a user or operator sees, with the version, line and steps to reproduce.}

## 2. Root cause

{Why it happens, with file and line on each affected line.}

## 3. Affected lines and releases

{Each line and release that carries the fault, and whether stock Apache Cassandra carries it too.}

## 4. Fix

{What changes, in plain words, and why this fix over the alternatives.}

## 5. Requirements

{The corrected behaviour as EARS requirements, `REQ-n`, one BCP 14 key word each, each with its source. Usually the unwanted behaviour shape: "If {condition}, then {the system} MUST {response}".}

## 6. The reproducing test

{The test the designer wrote on the item's code branch: its class and method, and its failing result on each affected line before the fix. The developer fixes against it on the same branch, and the code pull request shows it passing.}

## 7. Compatibility impact

{On-disk, wire, schema, settings, client visible behaviour. Mixed-version behaviour during a rolling upgrade. Or "does not apply, because".}

## 8. Upstream

{For a stock fault: the Apache JIRA and the delta entry with its upstream status. Otherwise "ChronitonDB code only".}

## 9. Order of pull requests

{One pull request per affected line, oldest line first. The item is done when all are merged.}

## 10. Tests the change runs

{The five lists of the design record's Testing section, with the same headings and format: Tests for this change (the reproducing test first), Existing suites at risk, Stock suites run unchanged, Tracing test, Formats and configurations. See [design-record.md](design-record.md#14-testing).}

## Planned file list

{The same format as the design record's planned file list: one file per line, the exact path, a space, then `new`, `edit`, `test` or `stock`. The reproducing test is listed as `test`. See [design-record.md](design-record.md#planned-file-list).}
