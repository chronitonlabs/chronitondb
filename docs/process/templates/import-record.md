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

# Import: {Apache release or CASSANDRA-n} into {line}

| Field | Value |
|---|---|
| Title | Import of {Apache release or CASSANDRA-n} into {line} |
| Document type | Record (ISO/IEC/IEEE 15289) |
| Status | Draft, Approved or Superseded |
| Version | {n} |
| Author | Integrator: {GitHub username} |
| Approver | The maintainer who merges the import pull request |
| References | Issue #{issue}. Apache release tag or commit hash. Import pull request. |

Change history: the git history of this file.

Location: `docs/imports/<apache-version-or-range>.md`, added in the import pull request. Process: [upstream.md](../upstream.md).

## 1. What came in

{Whole release: the Apache release tag and the commit range since the last import. Before Apache's first release of the major version: the Apache branch commit range merged this week. Single fix: the Apache JIRA, the Apache commit hash and the reason it is taken early (security, a dependency of our work, or a fault our users hit).}

## 2. Assessment

{The code checks and review checklists run on the imported diff. Findings, and the maintainers' decision on each.}

## 3. Conflicts with ChronitonDB changes

{Each conflict: the files, our change involved, and how it was resolved.}

## 4. Delta entries dropped

{Entries in the delta register that this import makes obsolete, because Apache now has the change.}

## 5. Tests run

{The suites and results: the stock suites with every fork feature off, the suites around the changed areas, and the regression tests of imported fixes.}

## 6. Stock behaviour confirmed

{The parity suite result with every fork feature off.}

## 7. Security

{Apache security fixes in this import, by Apache JIRA once public, and the VEX updates they need.}
