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

# Research report: #{issue} {title}

| Field | Value |
|---|---|
| Title | {title} |
| Document type | Report (ISO/IEC/IEEE 15289), technical report |
| Status | Draft, Approved or Superseded |
| Version | {n} |
| Author | Architect: {GitHub username} |
| Approver | The maintainer who merges the pull request |
| References | Issue #{issue}, labelled `spike`. Its parent issue, if any. |

Revision history, one row for each version:

| Version | Date | Change | Decision record |
|---|---|---|---|
| 1 | {RFC 3339 date} | First version | {the id of the decision record behind this version, or None} |

Full history in git: [commits of this file]({the address `tools/chronitondb/doclint.py history --write` puts here})

Location: `docs/research/<issue>-<slug>.md`. Process: [additive.md](../additive.md#work-intake). The merge approves the report as the record of what was found. It approves no work: the maintainers decide that in a decision record.

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in BCP 14 (RFC 2119, RFC 8174) when, and only when, they appear in all capitals, as shown here.

## Contents

- [1. Question](#1-question)
- [2. Sources](#2-sources)
- [3. Prior art](#3-prior-art)
- [4. Feasibility](#4-feasibility)
- [5. Effort](#5-effort)
- [6. Risks](#6-risks)
- [7. Options](#7-options)
- [8. Recommendation](#8-recommendation)

## 1. Question

{The question the spike answers, as the issue asks it: how to do something, or whether it can be done. One or two sentences. Then what the question leaves out.}

## 2. Sources

{Every piece of code read, cited as [conventions.md](../conventions.md#claims-about-code) says: the project, the branch and the commit, then the symbol and the file and line. The three sources stay apart, one row each. A source not read says "Not read" with the reason. Below the table: the Apache JIRA tickets read with their comments, mailing list threads and documentation.}

| Source | Project, branch and commit | What was read |
|---|---|---|
| Our line | `ChronitonDB chronitondb-5.0 at <hash>` | {symbols, files and lines} |
| The Apache Cassandra release our line is based on | `Apache Cassandra cassandra-5.0 at <hash>` | {symbols, files and lines} |
| Apache Cassandra upstream now | `Apache Cassandra cassandra-5.0 at <hash>` for the head of the same branch, the next major version's branch at its hash, `Apache Cassandra trunk at <hash>` | {symbols, files and lines} |

## 3. Prior art

{How other systems and projects solved this problem, and what each got right and wrong. Cite each source.}

These rules apply to every source:

1. Describe and cite behaviour, published designs, papers, public documentation and code under licences compatible with the Apache License 2.0.
2. Code or text under an incompatible licence, for example the Elastic License, SSPL, BUSL or a proprietary licence, MUST NOT be copied. The behaviour of such a system is taken only from its public documentation. Code under a compatible licence MAY be used only with credit. See [conventions.md](../conventions.md#code-from-elsewhere).
3. Contributors working on the project's behalf MUST NOT search for or read patents for design work. Any patent concern goes to the maintainers.

## 4. Feasibility

{Whether it can be done, and on which lines. The mechanism it would use, cited. What stands in the way. Each finding says which of the three sources it holds for.}

## 5. Effort

{A rough size in the terms of [classification.md](../classification.md#size): the complexity, the reach and how many items the work would take. A range, with what would move it.}

## 6. Risks

| Id | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|

{What could go wrong if the work were done, worst first. A public interface or stock behaviour the work would touch is named here, as [classification.md](../classification.md#the-floor) names it.}

## 7. Options

{Each option: what it is, what it changes for users and operators, its effort and its risks. Not doing the work is always one option.}

## 8. Recommendation

{The option the architect recommends, and why. The questions the report could not answer. The maintainers decide, and a decision record holds their answer.}
