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

# Decision records

This folder holds the decision records of ChronitonDB, in MADR format (Markdown Architectural Decision Records).

## When a record is written

A decision record is written for every answered question that changes or settles behaviour, scope or process. For example:

1. A user visible behaviour: which rows a query returns, an error, a refusal, a default.
2. A change to an approved feature spec, plan or delivery plan.
3. A point of scope: what a feature includes or leaves out.
4. A rule of the development process.
5. A grant, lapse, restoration or removal of commit rights. See [governance.md](../process/governance.md).

The role that asked the question writes the record, in the pull request that follows the answer: the designer in the design record's pull request, the developer in the code pull request, the architect in the pull request that updates the feature spec, plan or delivery plan, the integrator in the import pull request. A question from the security engineer or the release engineer that settles behaviour, scope or process gets its record from a maintainer. The maintainers approve each record by merging, after the reviewer's review.

## Rules

1. Each record is one file named `NNNN-<slug>.md`, numbered in order from `0001`.
2. Records are never edited after they are merged, except to change their status. A later decision that replaces an earlier one is a new record that names the one it supersedes. The earlier record's status becomes "Superseded by NNNN".
3. A record states the decision cleanly with its reason. It does not quote the discussion that led to it, and it points to no private material.
4. The decision outcome uses BCP 14 key words where it is normative.
5. Each new file carries the ChronitonDB licence header. See [conventions.md](../process/conventions.md#licence-headers).
6. Each new record keeps the template's Contents index, regenerated with `tools/chronitondb/doclint.py index --write <file>`. A record merged before the template had one stays as it was merged, under rule 2. See [conventions.md](../process/conventions.md#contents-index-of-process-documents).

## Template

```markdown
# NNNN. <Short title of the decision>

| Field | Value |
|---|---|
| Document type | Record (ISO/IEC/IEEE 15289), MADR |
| Status | Proposed, Accepted, or Superseded by NNNN |
| Date | <RFC 3339 date> |
| Deciders | The maintainers |
| References | <issue, pull request, feature spec, earlier records> |

## Contents

- [Context and problem statement](#context-and-problem-statement)
- [Considered options](#considered-options)
- [Decision outcome](#decision-outcome)
  - [Consequences](#consequences)
- [More information](#more-information)

## Context and problem statement

<The question in two or three sentences, and why it needed an answer.>

## Considered options

1. <Option one>
2. <Option two>

## Decision outcome

Chosen option: "<option>", because <reason>.

<The decision as normative statements with BCP 14 key words, where it binds behaviour.>

### Consequences

- Good: <what gets better>
- Bad: <what it costs, or what it rules out>

## More information

<Links to the design record, the feature spec section or the code it affects.>
```

## Index

1. [0001. The first maintainers](0001-initial-maintainers.md), 2026-11-01, Accepted.
2. [0002. What nodetool version prints on a ChronitonDB node](0002-nodetool-version-output-on-a-chronitondb-node.md), 2026-11-10, Accepted.
3. [0003. Where the tests prove the release version before a package exists](0003-release-version-tests-before-a-package-exists.md), 2026-11-11, Accepted.
4. [0004. The commit log disk check is off by default](0004-commit-log-disk-check-off-by-default.md), 2026-11-15, Accepted.
5. [0005. The commit log disk check is switched under startup_checks](0005-commit-log-disk-check-switched-under-startup-checks.md), 2026-11-15, Accepted.
6. [0006. The commit log disk check compares file systems](0006-commit-log-disk-check-compares-file-systems.md), 2026-11-15, Accepted.
7. [0007. The build details view builds the release version key and its reader](0007-build-details-view-builds-the-release-version-reader.md), 2026-11-16, Accepted.
8. [0008. The build details view obeys Apache compatibility mode through an internal check](0008-build-details-view-obeys-apache-compatibility-mode.md), 2026-11-16, Accepted.
9. [0009. A hidden build details view answers as a table that does not exist](0009-hidden-build-details-view-answers-as-a-missing-table.md), 2026-11-16, Accepted.
10. [0010. The build details view stays at Normal risk](0010-build-details-view-stays-at-normal-risk.md), 2026-11-16, Accepted.
11. [0011. The build details view is switched by its yaml setting only](0011-build-details-view-switched-by-yaml-setting-only.md), 2026-11-16, Accepted.
12. [0012. The build details view follows the Apache Cassandra permission rule where authorization is off](0012-build-details-view-readable-where-authorization-is-off.md), 2026-11-16, Accepted.
13. [0013. A node starts with the build details view hidden when its configuration turns the view on before the final gate](0013-build-details-view-hidden-before-the-final-gate.md), 2026-11-16, Accepted.
14. [0014. A node that shows the build details view counts its reads](0014-build-details-view-counts-its-reads.md), 2026-11-16, Accepted.
15. [0015. A grant on the build details view that outlives the view is documented](0015-grant-on-the-build-details-view-that-outlives-the-view.md), 2026-11-16, Accepted.
