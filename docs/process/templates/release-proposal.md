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

# Release: {version}

| Field | Value |
|---|---|
| Title | ChronitonDB {version} |
| Document type | Plan (ISO/IEC/IEEE 15289), release plan, with the verification report the promotion adds |
| Status | Draft, Approved or Superseded |
| Version | {n} |
| Author | Release engineer: {GitHub username} |
| Approver | The maintainer who merges the pull request, once for the proposal and once for the promotion |
| References | {line, the previous release, milestone reports, security advisories} |

Change history: the git history of this file.

Location: `docs/releases/<version>.md`. Process: [release.md](../release.md).

## 1. Version

{The version, in the form of [release.md](../release.md#version-numbers), and the line it ships on.}

## 2. Commit

{The full hash of the commit on the line the candidate is built from. The release candidate tag is signed at this commit, so anything merged later stays out.}

## 3. What goes in

{From the commits on the line since the previous release, grouped as features, fixes, performance, security and imports. One line each, with its pull request.}

## 4. Milestone gates passed

{The features whose final milestone gate passed and become switchable in this release, each with its milestone report. Or "None".}

## 5. Security fixes due

{The security fixes this release ships, each with its advisory and the date the maintainers set. Or "None".}

## 6. Verification results

Not verified yet. After the soak the promotion pull request replaces this line with the results: signatures, installs, upgrade and rollback from the previous ChronitonDB release and from Apache Cassandra, and the parity suite, each with its result and evidence in the table, and the problems reported during the soak with what was done about each.

| Check | Result | Evidence |
|---|---|---|
