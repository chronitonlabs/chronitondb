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
| Risk | {Critical, Normal or Low}: {the worst Bug Category the change could cause if wrong, and the floor if one applied} |
| Size | {Low Hanging Fruit, Normal, Challenging or Byzantine}: {why} |
| Reach | {One area or Cross-cutting}: {why, naming the packages touched} |
| Touches | {public interface (name which), stock behaviour, new input or privilege, new dependency, shared state (threads, pools or shared state), request path (a read, write or query path), new feature or switch, or none} |

Change history: the git history of this file.

Location: `docs/design/<issue>-<slug>/`, with the coverage file `ac-coverage.md` next to it. Process: [maintenance.md](../maintenance.md). A security fix stays in its private advisory until disclosure, see [security.md](../security.md).

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in BCP 14 (RFC 2119, RFC 8174) when, and only when, they appear in all capitals, as shown here.

The Risk, Size and Reach rows are the item's class, as [classification.md](../classification.md) defines it, and match the issue's `risk:`, `size:` and `reach:` labels. Each value is the level, a colon and the reason. Touches lists what the change touches, from the four phrases in the row, or says none. A public interface or stock behaviour in Touches means the risk is Normal or Critical.

## Contents

- [1. Symptom](#1-symptom)
- [2. Root cause](#2-root-cause)
- [3. Affected lines and releases](#3-affected-lines-and-releases)
- [4. Fix](#4-fix)
- [5. Requirements](#5-requirements)
- [6. The reproducing test](#6-the-reproducing-test)
- [7. Compatibility impact](#7-compatibility-impact)
- [8. Upstream](#8-upstream)
- [9. Order of pull requests](#9-order-of-pull-requests)
- [10. Tests the change runs](#10-tests-the-change-runs)
  - [Tests for this change](#tests-for-this-change)
  - [Existing suites at risk](#existing-suites-at-risk)
  - [Stock suites run unchanged](#stock-suites-run-unchanged)
  - [Tracing test](#tracing-test)
  - [Formats and configurations](#formats-and-configurations)
- [Where problems could occur](#where-problems-could-occur)
  - [Test plan](#test-plan)
- [Planned file list](#planned-file-list)
  - [Shared with open items](#shared-with-open-items)

## 1. Symptom

{What a user or operator sees, with the version, line and steps to reproduce.}

## 2. Root cause

{Why it happens, with file and line on each affected line.}

## 3. Affected lines and releases

{Each line and release that carries the fault, and whether stock Apache Cassandra carries it too.}

## 4. Fix

{What changes, in plain words, and why this fix over the alternatives.}

{A fix that changes how nodes coordinate names its checked model here: the model files in the item's design directory and the model checker's result. See [quality-requirements.md](../quality-requirements.md#coordination-between-nodes-is-model-checked).}

## 5. Requirements

{The corrected behaviour as EARS requirements, `REQ-n`, one BCP 14 key word each, each with its source. Usually the unwanted behaviour shape: "If {condition}, then {the system} MUST {response}". A fix to a fork feature also lists here every feature requirement the fault breaks, by its id `REQ-<KEY>-nnn` at the start of a line. Its text stays in the design record that defines it, so the line cites the id with a few words of what it covers, no key word and no source. Each listed requirement is reproduced by a scenario tagged with it and with `@fix-<issue>`. See [testing.md](../testing.md#scenarios), rule 11.}

## 6. The reproducing test

{The test the designer wrote on the item's code branch: its class and method, and its failing result on each affected line before the fix. The developer fixes against it on the same branch, and the code pull request shows it passing.}

{A fix to a fork feature MAY use scenarios as its reproducing test: new scenarios, or the feature's existing scenarios updated with only the two tags and new Examples rows. Each carries the tag of at least one requirement listed in section 5 and the tag `@fix-<issue>`, with the issue number of this record, for example `@fix-142`, and no `@wip`. Name each feature file and scenario. Each MUST fail before the fix and pass after it. A fix to stock Apache Cassandra code uses a plain JUnit test. See [testing.md](../testing.md#scenarios).}

## 7. Compatibility impact

{On-disk, wire, schema, settings, client visible behaviour. Mixed-version behaviour during a rolling upgrade. Or "does not apply, because".}

## 8. Upstream

{For a stock fault: the Apache JIRA and the delta entry that records it in its Bug and Forwarded fields. Otherwise "ChronitonDB code only".}

## 9. Order of pull requests

{One pull request per affected line, oldest line first. The item is done when all are merged.}

## 10. Tests the change runs

Scenario runner: {the command that runs the scenarios, with {tags} once}

Scenario tags: {the requirement tags section 5 lists and this record's fix tag, joined with `and`, for example `@REQ-LUC-012 and @fix-142`, or `(@REQ-LUC-012 or @REQ-LUC-013) and @fix-142`}

{The two scenario lines and their rules are those of the design record's Testing section. A fix with no scenarios leaves out both lines. A fix whose reproducing test is a scenario keeps them. Its tags line MUST require `@fix-<issue>` with the issue number of this record, joined with `and` to the requirement tags section 5 lists, never with `or`. So only the scenarios that carry both tags run before the fix and after it, as long as none carries `@wip` or `@stock`, which the run leaves out. After the fix the feature's other scenarios run too, and each MUST still pass.}

{Then the five lists of the design record's Testing section, with the same headings and format. Tooling reads them, so keep the headings. One fully qualified test class per line. Write `none` under a heading that has no entry. See [design-record.md](design-record.md#14-testing).}

### Tests for this change

{The reproducing test first, when it is a JUnit test, then the other new and changed tests.}

### Existing suites at risk

{Unit test suites and in-JVM distributed test suites this fix could break.}

### Stock suites run unchanged

{Apache Cassandra's own suites that MUST pass without modification.}

### Tracing test

{The test that shows the fix in query tracing, or "does not apply, because" with the reason.}

### Formats and configurations

{`yes` when the fix touches compaction or an on-disk format, so the tests also run with both sstable formats and both unit test configurations. Otherwise `no`.}

## Where problems could occur

{Never Not applicable. Where the fix could go wrong if it is wrong, worst case first: what a user or an operator would see (a wrong result, an error, a crash, a slow request, a changed file on disk), on which request path, and from which part of the change. Never "None" or "Low", and never an argument that the fix is safe. After the "Where problems could occur" section of Ubuntu's stable release update template. See [classification.md](../classification.md).}

### Test plan

{Never Not applicable. For each problem above, the test that would catch it and what it checks. A problem no test covers says why, and how it is watched instead.}

## Planned file list

{The same format as the design record's planned file list: one file per line, the exact path from the repository root, a space, then `new`, `edit`, `test` or `stock`, all in one fenced block. No wildcards. The reproducing test is listed as `test`. Tooling enforces the list as written here. See [design-record.md](design-record.md#planned-file-list).}

```
src/java/org/apache/cassandra/example/Example.java stock
test/unit/org/apache/cassandra/example/ExampleTest.java test
```

### Shared with open items

{The same table as the design record's: one row per open item whose pull request changes a planned file, with the kind `soft` or `hard`. Write "None." in place of the table when no open item shares a file. A hard overlap stops the work, and the maintainers decide which item goes first. Tooling reads this table, so keep its columns. See [design-record.md](design-record.md#shared-with-open-items).}

| Item | Shared file | Kind |
|---|---|---|
| {#issue of the open item} | {path} | {soft or hard} |
