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

# Delta: {short name}

| Field | Value |
|---|---|
| Title | {short name} |
| Document type | Record (ISO/IEC/IEEE 15289) |
| Status | Current or Dropped |
| Version | {n} |
| Author | {role: GitHub username}, or The maintainers. Who wrote this entry, and the change when its Origin is ChronitonDB. This is the DEP-3 Author field. |
| Approver | The maintainer who merges the pull request |
| References | The Origin, Bug, Bug-ChronitonDB and Pull requests fields below. |

Change history: the git history of this file.

Location: `docs/delta/`. Process: [the delta register](../../delta/README.md).

## Header

The fields follow Debian's [DEP-3 patch header convention](https://dep-team.pages.debian.net/deps/dep3/), adapted to a change ChronitonDB carries on top of Apache Cassandra. Author is in the table above. Added, Pull requests, Status, Area and Lines are the register's own. DEP-3 has no such fields. Dates are written YYYY-MM-DD, as DEP-3 writes them.

| Field | Value |
|---|---|
| Description | {One line: what ChronitonDB carries. The What and Why sections below are the long description.} |
| Origin | {Where the change came from. One of: ChronitonDB. Apache commit `<hash>`, taken whole, with its link. Backport of Apache commit `<hash>`, when only part of it is taken or it is changed, with its link. Another fork, with its name and a link to the commit.} |
| Bug | {The Apache JIRA as a link, `https://issues.apache.org/jira/browse/CASSANDRA-<n>`, or none.} |
| Bug-ChronitonDB | {Our GitHub issue in `chronitonlabs/chronitondb` as a link, or none.} |
| Forwarded | {Whether the change has gone to Apache Cassandra. One of: Offered, with the Apache JIRA. Declined, with the Apache JIRA and a one line reason. Not needed, with the reason.} |
| Added | {The date ChronitonDB first carried the change on a line.} |
| Last-Update | {The date of the last change to this entry.} |
| Pull requests | {The pull requests that carry the change, per line, each with its commit on the line.} |

## What

{What ChronitonDB carries on top of Apache Cassandra, in plain words.}

## Why

{Why we carry it.}

## Area

{The part of the tree and the behaviour it touches: feature, stock fix, build or packaging. Files or packages where useful.}

## Lines

{The lines that carry it.}
