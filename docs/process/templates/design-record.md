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

# Design: #{issue} {title}

| Field | Value |
|---|---|
| Title | {title} |
| Document type | Specification and description at item level (ISO/IEC/IEEE 15289) |
| Status | Draft, Approved or Superseded |
| Version | {n} |
| Author | Designer: {GitHub username} |
| Approver | The maintainer who merges the pull request |
| References | Issue #{issue}. Line `chronitondb-<line>`. Apache base commit `<hash>`. Feature spec and plan item, if any. Decision records. |
| Risk | {Critical, Normal or Low}: {the worst Bug Category the change could cause if wrong, and the floor if one applied} |
| Size | {Low Hanging Fruit, Normal, Challenging or Byzantine}: {why} |
| Reach | {One area or Cross-cutting}: {why, naming the packages touched} |
| Touches | {public interface (its compatibility area), stock behaviour, new input or privilege, new dependency, shared state (threads, pools or shared state), request path (a read, write or query path), new feature or switch, or none} |

Change history: the git history of this file.

Location: `docs/design/<issue>-<slug>/`, or `docs/design/<KEY>-<slug>/` for a fork feature that fits one item (see [feature keys](../additive.md#feature-keys-and-requirement-ids)), with the coverage file `ac-coverage.md` next to it. For a fork feature that fits one item, the designer proposes a free key in this record's pull request, and the key is reserved when a maintainer merges it. Every section is filled, or carries a waiver with its reason. An empty section blocks approval.

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in BCP 14 (RFC 2119, RFC 8174) when, and only when, they appear in all capitals, as shown here.

The Risk, Size and Reach rows are the item's class, as [classification.md](../classification.md) defines it, and match the issue's `risk:`, `size:` and `reach:` labels. Each value is the level, a colon and the reason. Touches lists what the change touches, from the phrases in the row, or says none. A public interface names its area in brackets, one of the compatibility areas in [classification.md](../classification.md#the-floor), such as public interface (configuration). A public interface or stock behaviour in Touches means the risk is Normal or Critical.

## Contents

- [1. Problem, acceptance criteria and requirements](#1-problem-acceptance-criteria-and-requirements)
  - [Requirements](#requirements)
- [2. Decisions implemented](#2-decisions-implemented)
- [3. Stock behaviour preservation](#3-stock-behaviour-preservation)
  - [Stock hook points](#stock-hook-points)
- [4. Prior art reviewed](#4-prior-art-reviewed)
- [5. Idiom and consistency](#5-idiom-and-consistency)
- [6. Quality requirements](#6-quality-requirements)
- [7. Performance](#7-performance)
  - [Hot path statement](#hot-path-statement)
  - [Expected cost](#expected-cost)
  - [Isolation levers](#isolation-levers)
  - [Benchmarks that prove it](#benchmarks-that-prove-it)
  - [Regression threshold and gate](#regression-threshold-and-gate)
  - [Stock guard](#stock-guard)
  - [What was not measured](#what-was-not-measured)
- [8. Observability](#8-observability)
- [9. Compatibility](#9-compatibility)
- [10. Threat model and security](#10-threat-model-and-security)
- [11. Dependencies](#11-dependencies)
- [12. Compliance impact](#12-compliance-impact)
- [13. Documentation](#13-documentation)
- [14. Testing](#14-testing)
  - [Tests for this change](#tests-for-this-change)
  - [Existing suites at risk](#existing-suites-at-risk)
  - [Stock suites run unchanged](#stock-suites-run-unchanged)
  - [Tracing test](#tracing-test)
  - [Formats and configurations](#formats-and-configurations)
- [15. Not covered and follow-ups](#15-not-covered-and-follow-ups)
- [New terms](#new-terms)
- [Where problems could occur](#where-problems-could-occur)
  - [Test plan](#test-plan)
- [Planned file list](#planned-file-list)
  - [Shared with open items](#shared-with-open-items)
  - [Waivers](#waivers)
- [Requirement quality checklist (ISO/IEC/IEEE 29148)](#requirement-quality-checklist-isoiecieee-29148)

## 1. Problem, acceptance criteria and requirements

{The problem in plain words. The acceptance criteria quoted from the issue or the plan item. Context and rationale stay in prose.}

### Requirements

{One requirement per entry, on one line: an id, one EARS shape, one BCP 14 key word, and its source. The id is `REQ-<KEY>-nnn` for feature work, with the feature key and three digits numbered across the whole feature, and `REQ-n` for any other item. For an item of a feature, the source is an acceptance criterion in the plan, and through it a FREQ. Otherwise it is an acceptance criterion in the issue, a risk this record names, or a decision record. Each id is proven by a scenario that carries it as a tag, or has exactly one row in `ac-coverage.md` naming its test or the reason it is deliberately not tested.}

The five EARS shapes, one example each:

REQ-1 (ubiquitous): The index MUST return the same rows for a query in the memtable, after flush and after compaction. Source: {...}.

REQ-2 (event driven): When the toggle is changed with nodetool, the node MUST log the old and the new value at INFO. Source: {...}.

REQ-3 (state driven): While the feature switch is off, the node MUST refuse every statement that uses the feature's syntax. Source: {...}.

REQ-4 (optional feature): Where the timeout option is set to partial, the coordinator MUST mark the result as partial. Source: {...}.

REQ-5 (unwanted behaviour): If a node reads a file with an unknown version marker, then the node MUST refuse to open it and log the file name. Source: {...}.

## 2. Decisions implemented

{Each decision record by number, with a one line reminder and its date. A statement that no newer record exists on the same subject as of the date of this record.}

## 3. Stock behaviour preservation

{One row per departure from stock, in this table. Write "No departures from stock." in place of the table when there are none. Code defaults in stock classes unchanged. In the switch column, link each departure to its switch's row in the feature spec's section 2.8. A fork feature that fits one item has no feature spec: state its class and the class of each switch above the table, in the form of [section 2.8 of the feature spec](feature-spec.md#28-feature-class-and-switches), and link to that. Tooling reads this table, so keep its columns.}

| Stock behaviour today (file and line) | This change | Switch that controls it | Error text naming the switch |
|---|---|---|---|
| {stock behaviour} | {change} | {switch} | {error text} |

### Stock hook points

{Each stock Apache Cassandra file this item makes import ChronitonDB code, with its hook point in the feature spec (section 2.7) and its delta entry. Write "None." when there are none. A hook point not in the spec needs the spec changed first.}

## 4. Prior art reviewed

{Stock code on each line with file and line. Other projects by behaviour. Apache JIRA tickets read with their comments. What each got right or wrong for this problem.}

These rules apply to every source:

1. Describe and cite behaviour, published designs, papers, public documentation and code under licences compatible with the Apache License 2.0.
2. Code or text under an incompatible licence, for example the Elastic License, SSPL, BUSL or a proprietary licence, MUST NOT be copied. The behaviour of such a system is taken only from its public documentation. Code under a compatible licence MAY be used only with credit. See [conventions.md](../conventions.md#code-from-elsewhere).
3. Contributors working on the project's behalf MUST NOT search for or read patents for design work. Any patent concern goes to the maintainers.

## 5. Idiom and consistency

{For each user visible choice: whether it matches stock, earlier decisions and the idiom it follows, and the reason for any deliberate difference.}

## 6. Quality requirements

{For a one-item change, the checklist table from [quality-requirements.md](../quality-requirements.md), each line answered with REQ ids or a reason it does not apply. For an item of a feature, cite the feature spec lines this item delivers.}

{A design that changes how nodes coordinate names its checked model here: the model files in the item's design directory and the model checker's result. See [quality-requirements.md](../quality-requirements.md#coordination-between-nodes-is-model-checked).}

## 7. Performance

### Hot path statement

{Which request types touch the new code, and where: coordinator, replica read, memtable write, flush, compaction, streaming, repair. One line each.}

### Expected cost

| Path | Metric | Stock today | Expected with the change | Why (mechanism) |
|---|---|---|---|---|

{Mechanism means the data structure and the count of operations.}

### Isolation levers

{Yaml settings and nodetool toggles, thread pool, memory limit, kill switch, and stock behaviour when each lever is off.}

### Benchmarks that prove it

| Claim | Benchmark | Command | Pairs | Threshold |
|---|---|---|---|---|

### Regression threshold and gate

{Which benchmarks gate the pull request. Pull request gates block only on counted values and on benchmarks that fail to run, never on timing.}

### Stock guard

{The stock runs that must not move, and the run with the switch off that must match stock.}

### What was not measured

{With the reason and the follow-up issue.}

## 8. Observability

{Counted, timed, logged, traced, exposed, toggled, audited, released on drop, documented, tested. Every outcome has a counter. Every limit has limit, used and tripped. Every runtime change logs old and new at INFO. No line above TRACE carries a key, term, literal or secret.}

## 9. Compatibility

{For a one-item change, the feature spec's Compatibility headings in small form: on-disk format changes with version markers, mixed-version behaviour, upgrade path and prerequisites, rollback path, runbook entries. Also: surfaces touched, the version bump per surface or the Apache test that passes unchanged, what the switch writes to shared state when off and when on, and the impact on the other line. Or "does not apply, because".}

## 10. Threat model and security

{For a one-item change, every new entry point checked with STRIDE, each mitigation a REQ, or "no new entry point" with the reason. For any change: the input it parses, the bound on each input, the permissions it needs with a negative test per permission, the audit entries, the limits with warn and fail thresholds, and how errors map to client errors.}

## 11. Dependencies

{Each new library or version change with version, ASF category, NOTICE and credit lines, known vulnerabilities and why it is needed, one library per line or table row. Name a library by its Maven `group:artifact` or artifact, its pip name, its file name under `lib/` without the version, or `accord` for the Accord submodule, and give the exact version, or the commit for Accord. A check reads the library and the version from the same line. Or "No new dependency".}

## 12. Compliance impact

{Copies of data and what deletes each, erasure, minimisation, masking, access control, audit, logging, cryptography, data residency, backups and snapshots, supply chain, secure defaults, retention, isolation levers, and one paragraph for operators naming the settings.}

## 13. Documentation

{The pages this change adds or edits. Every new yaml key, option, metric, virtual table, nodetool command and error string by exact name. Failure behaviour on timeout, coordinator failure, missing replica, limit hit and index not built. Known limitations.}

## 14. Testing

{The test levels required. RF 1 and RF 3 for anything multi node. Both sstable formats and both unit test configurations for anything touching compaction or formats. What the parity suite will check. See [testing.md](../testing.md).}

{For an item of a fork feature: the scenarios this pull request adds under `test/bdd/`, tagged `@wip` and with their requirement tags. See [testing.md](../testing.md#scenarios).}

Scenario runner: {the command that runs the scenarios, with {tags} once}

Scenario tags: {the tag expression for this item's scenarios}

{Tooling reads these two lines, so keep their names and write each on one line. The runner is `ant` or a script under `tools/chronitondb/`, and it runs as plain words, never through a shell. Without the tags line, the item's scenarios are those tagged with the requirement ids this record defines. An item with no scenarios leaves out both lines.}

{Then these five lists. Tooling reads them, so keep the headings. One fully qualified test class per line. Write `none` under a heading that has no entry.}

### Tests for this change

{The new and changed tests that prove each requirement.}

### Existing suites at risk

{Unit test suites and in-JVM distributed test suites this change could break.}

### Stock suites run unchanged

{Apache Cassandra's own suites that MUST pass without modification.}

### Tracing test

{The test that shows the change in query tracing, or "does not apply, because" with the reason.}

### Formats and configurations

{`yes` when the change touches compaction or an on-disk format, so the tests also run with both sstable formats and both unit test configurations. Otherwise `no`.}

## 15. Not covered and follow-ups

{What stays out, each with the decision that put it out, stated cleanly. Candidate issues for anything found on the way.}

## New terms

{Terms this item needs that are not in the feature spec's glossary, each with a one line definition and its name in code, CQL and docs. The architect adds them to the glossary. Write "None." when there are none.}

## Where problems could occur

{Where the change could go wrong if it is wrong, worst case first: what a user or an operator would see (a wrong result, an error, a crash, a slow request, a changed file on disk), on which request path, and from which part of the change. Never "None" or "Low", and never an argument that the change is safe. After the "Where problems could occur" section of Ubuntu's stable release update template. An item of a feature whose feature spec the References row links, as a Markdown link to its `feature-spec.md`, MAY write the one line `Not applicable: <reason>` here, the reason naming the spec's section 4 that covers it. Every other design record fills it. See [classification.md](../classification.md).}

### Test plan

{For each problem above, the test that would catch it and what it checks. A problem no test covers says why, and how it is watched instead. Left out when the section above says Not applicable.}

## Planned file list

{One file per line: the exact path from the repository root, a space, then one word: `new`, `edit`, `test` or `stock`. No wildcards. The developer edits only these files, and tooling enforces the list as written here.}

The four words:

1. `new`: a file the line does not have yet.
2. `edit`: an existing ChronitonDB file.
3. `stock`: an existing Apache Cassandra file that is not a test.
4. `test`: any test file, new or existing. A stock test stays add only: its existing tests are not changed.

```
src/java/org/apache/cassandra/example/Example.java stock
test/unit/org/apache/cassandra/example/ExampleTest.java test
```

### Shared with open items

{One row per open item whose pull request changes a file in the list above. The designer checks the open pull requests for changes to the planned files. The kind is `soft` when the open item changes other lines of the same file, and `hard` when it changes the same lines. A hard overlap stops the work, and the maintainers decide which item goes first. Write "None." in place of the table when no open item shares a file. Tooling reads this table, so keep its columns.}

| Item | Shared file | Kind |
|---|---|---|
| {#issue of the open item} | {path} | {soft or hard} |

### Waivers

{Any waiver of a shape limit, with the method, the rule and the reason. Write "None." when there are none.}

## Requirement quality checklist (ISO/IEC/IEEE 29148)

Check every requirement against these seven qualities before asking for approval. The reviewer judges against the same list.

1. **Necessary:** it traces to an acceptance criterion, a named risk or a decision record. Removing it would lose something the issue asks for.
2. **Unambiguous:** it has one reading. No "fast", "large", "quickly" or "efficient" without a number and a unit.
3. **Singular:** one requirement, one BCP 14 key word, one EARS shape. Two requirements joined by "and" are split into two ids.
4. **Verifiable:** one scenario, test or benchmark can prove it, and a scenario tag or `ac-coverage.md` names it.
5. **Feasible:** the mechanism exists in the tree or in this design, cited with file and line.
6. **Consistent:** it contradicts no other requirement, no decision record and no stock behaviour rule.
7. **Traceable:** it has an id, a source, and a scenario tag or exactly one coverage row.

A requirement that fits none of the five EARS shapes is rewritten until it fits one.
