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
| Areas | {one or more areas of [areas.md](../areas.md), joined by commas} |
| Risk | {Critical, Normal or Low}: {the worst Bug Category the change could cause if wrong, and the floor if one applied} |
| Size | {Low Hanging Fruit, Normal, Challenging or Byzantine}: {why} |
| Reach | {One area or Cross-cutting}: {why, naming the packages touched} |
| Touches | {public interface (its compatibility area, an on-disk file by its area: sstable components, or commitlog, hint log and cache files), stock behaviour, new input or privilege, new dependency, shared state (threads, pools, caches or other state several requests share), request path (any path whose cost grows with data or traffic), new feature or switch, on-disk files, flush, compaction, streaming, repair, or none} |
| Exceptions | {None, or the id of each principle this record departs from, joined by commas, for example PRINCIPLE-016} |

Revision history, one row for each version:

| Version | Date | Change | Decision record |
|---|---|---|---|
| 1 | {RFC 3339 date} | First version | {the id of the decision record behind this version, or None} |

Full history in git: [commits of this file]({the address `tools/chronitondb/doclint.py history --write` puts here})

Location: `docs/design/<issue>-<slug>/`, or `docs/design/<KEY>-<slug>/` for a fork feature that fits one item (see [feature keys](../additive.md#feature-keys-and-requirement-ids)), with the coverage file `ac-coverage.md` next to it. For a fork feature that fits one item, the designer proposes a free key in this record's pull request, and the key is reserved when a maintainer merges it. Every section is filled, or says "does not apply, because" with the reason. The section Where problems could occur has its own rule, given there. An empty section blocks approval.

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in BCP 14 (RFC 2119, RFC 8174) when, and only when, they appear in all capitals, as shown here.

A rule of the project is cited by its id from [principles.md](../principles.md), as a link to its entry, for example `[PRINCIPLE-001](../principles.md#principle-001)`. This document cites nothing that a reader of the repository cannot open.

The Risk, Size and Reach rows are the item's class, as [classification.md](../classification.md) defines it, and match the issue's `risk:`, `size:` and `reach:` labels. Each value is the level, a colon and the reason. Touches lists what the change touches, from the phrases in the row, or says none. A public interface names its area in brackets, one of the compatibility areas in [classification.md](../classification.md#the-floor), such as public interface (configuration). A public interface or stock behaviour in Touches means the risk is Normal or Critical. On-disk files, flush, compaction, streaming and repair name what the code of the change does, in Apache Cassandra's files or in ChronitonDB's own, and any of them in Touches means the risk is Critical, unless the maintainers said for this change that it is not. A change whose code takes part in authentication, authorisation, encryption, audit logging or the decoding of bytes from the network is Critical too: its Risk row says so, since Touches has no phrase for it. See [classification.md](../classification.md#the-critical-floor).

The Exceptions row marks a record that departs from a principle in a way the principle does not itself allow, or by an exception the principle says is marked here. It names each such principle by its id, joined by commas, or says None. Section 2 states each exception: what this record does in place of the principle, and the reason. The maintainers decide the exception by merging this record, and the generated index lists every record that carries one. See [principles.md](../principles.md#how-to-read-and-cite-a-principle).

## Contents

- [1. Problem, acceptance criteria and requirements](#1-problem-acceptance-criteria-and-requirements)
  - [Requirements](#requirements)
- [2. Decisions implemented](#2-decisions-implemented)
- [3. Apache Cassandra behaviour preservation](#3-apache-cassandra-behaviour-preservation)
  - [Apache Cassandra hook points](#apache-cassandra-hook-points)
- [4. Prior art reviewed](#4-prior-art-reviewed)
- [5. Idiom and consistency](#5-idiom-and-consistency)
- [6. Quality requirements](#6-quality-requirements)
- [7. Performance](#7-performance)
  - [Hot path statement](#hot-path-statement)
  - [Expected cost](#expected-cost)
  - [Isolation levers](#isolation-levers)
  - [Benchmarks that prove it](#benchmarks-that-prove-it)
  - [Regression threshold and gate](#regression-threshold-and-gate)
  - [Apache Cassandra guard](#apache-cassandra-guard)
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
  - [Apache Cassandra suites run unchanged](#apache-cassandra-suites-run-unchanged)
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

{One requirement per entry, on one line: an id, one EARS shape, one BCP 14 key word, and its source. The id is `REQ-<KEY>-nnn` for feature work, with the feature key and three digits numbered across the whole feature, and `REQ-n` for any other item. For an item of a feature, the source is an acceptance criterion in the plan, and through it a FREQ. Otherwise it is an acceptance criterion in the issue, a risk this record names, a decision record, a principle by its id or a stakeholder need. Each id is proven by a scenario that carries it as a tag, or has exactly one row in `ac-coverage.md` naming its test or the reason it is deliberately not tested. A requirement that needs tests at two levels keeps one id and lists both tests. A requirement that states two behaviours is split into two ids.}

The five EARS shapes, one example each:

REQ-1 (ubiquitous): The compaction task MUST keep every live row of the sstables it reads. Source: {...}.

REQ-2 (event driven): When the toggle is changed with nodetool, the node MUST log the old and the new value at INFO. Source: {...}.

REQ-3 (state driven): While the feature switch is off, the node MUST refuse every statement that uses the feature's syntax. Source: {...}.

REQ-4 (optional feature): Where the table option sets a rate, the node MUST keep streaming for that table at or below the rate. Source: {...}.

REQ-5 (unwanted behaviour): If a node reads a file with an unknown version marker, then the node MUST refuse to open it and log the file name. Source: {...}.

## 2. Decisions implemented

{Each decision record by its id, with a one line reminder and its date. Then each principle the Exceptions row names, with what this record does in its place and the reason.}

## 3. Apache Cassandra behaviour preservation

{One row per departure from stock, in this table. Write "No departures from stock." in place of the table when there are none. Code defaults in stock classes unchanged. In the switch column, link each departure to its switch's row in the feature spec's section 2.8. A departure with no switch, such as a fix to a defect in stock, says so in that column with the reason. The last column says how a user or operator sees the departure in effect, for example the text of an error or a warning, a log line, a setting or a metric. A fork feature that fits one item has no feature spec: state its class and the class of each switch above the table, in the form of [section 2.8 of the feature spec](feature-spec.md#28-feature-class-and-switches), and link to that. Keep its columns exact, since a check may read the table. Cite each behaviour in the first column as [conventions.md](../conventions.md#claims-about-code) says: `Apache Cassandra <branch> at <hash>`, the symbol, and the file and line.}

| Apache Cassandra behaviour today (file and line) | This change | Switch that controls it | How a user or operator sees it in effect |
|---|---|---|---|
| {Apache Cassandra behaviour, cited} | {change} | {switch, or the reason there is none} | {an error, a warning, a log line, a setting or a metric, by its exact text or name} |

### Apache Cassandra hook points

{Each stock Apache Cassandra file this item makes import ChronitonDB code, with its hook point in the feature spec (section 2.7) and its delta entry. Write "None." when there are none. A hook point not in the spec needs the spec changed first.}

## 4. Prior art reviewed

{Apache Cassandra code and our own, each cited as [conventions.md](../conventions.md#claims-about-code) says, with our line, the Apache Cassandra release it is based on and Apache Cassandra upstream now kept apart. Other projects by behaviour. Apache JIRA tickets read with their comments. What each got right or wrong for this problem.}

These rules apply to every source:

1. Describe and cite behaviour, published designs, papers, public documentation and code under licences compatible with the Apache License 2.0.
2. Code or text under an incompatible licence, for example the Elastic License, SSPL, BUSL or a proprietary licence, MUST NOT be copied. The behaviour of such a system is taken only from its public documentation. Code under a compatible licence MAY be used only with credit. See [conventions.md](../conventions.md#code-from-elsewhere).
3. Contributors working on the project's behalf MUST NOT search for or read patents for design work. Any patent concern goes to the maintainers.

## 5. Idiom and consistency

{For each user visible choice: whether it matches Apache Cassandra, earlier decisions and the idiom it follows, and the reason for any deliberate difference.}

## 6. Quality requirements

{For a one-item change, the checklist table from [quality-requirements.md](../quality-requirements.md), each line answered with REQ ids or a reason it does not apply. For an item of a feature, cite the feature spec lines this item delivers.}

{A design whose correctness depends on ordering, concurrency or shared state, across nodes or within one node across a crash and restart, says here why a TLA+ model is believed to be needed, and gives the maintainers' answer. A model they asked for is named here: the model files in the item's design directory and the model checker's result. A design with no such dependence says in one line why it needs none. See [quality-requirements.md](../quality-requirements.md#a-tla-model-where-the-maintainers-ask-for-one).}

## 7. Performance

### Hot path statement

{Which request types touch the new code, and where: coordinator, replica read, memtable write, flush, compaction, streaming, repair. One line each.}

### Expected cost

| Path | Metric | Apache Cassandra today | Expected with the change | Why (mechanism) |
|---|---|---|---|---|

{Mechanism means the data structure and the count of operations.}

### Isolation levers

{For a change that adds work to a shared path: what bounds its threads, its memory and its work per operation, how it sheds load, how long it may run and how an operator turns it off, on every node role that does the work. For each bound, how an operator sets it, at which scope, and the metric that shows it. Why this level of isolation is what the change needs. A change that adds no work to a shared path says so in one line. See [PRINCIPLE-051](../principles.md#principle-051).}

### Benchmarks that prove it

| Claim | Benchmark | Command | Pairs | Threshold |
|---|---|---|---|---|

### Regression threshold and gate

{Which benchmarks gate the pull request. Pull request gates block only on counted values and on benchmarks that fail to run, never on timing.}

### Apache Cassandra guard

{The stock runs the change is compared against: with the feature off, and with it on but unused. A measured slowdown of operations that do not use the feature is reported here with its numbers and what causes it, for the maintainers to decide. See [PRINCIPLE-052](../principles.md#principle-052).}

### What was not measured

{With the reason and the follow-up issue.}

## 8. Observability

{Counted, timed, logged, traced, exposed, toggled, audited, released on drop, documented, tested. Every outcome has a counter. Every limit has limit, used and tripped. Every runtime change logs old and new at INFO. No log line the change adds carries user data or a secret, at any log level, and no trace line it adds carries user data. Nothing is logged once per request or per element, such as a row, a partition, a file or a message, and the start and end lines of a background task follow [PRINCIPLE-036](../principles.md#principle-036). The stock log lines the change's input reaches, in one line. The startup line of each switch and the WARN line of each degraded state. An ERROR line for each failing request is for an unexpected server error only, and is assessed here: why the error is unexpected, what bounds how often it can fire, and what the log holds if it fires on every request. See [quality-requirements.md](../quality-requirements.md#observability).}

## 9. Compatibility

{For a one-item change, the feature spec's Compatibility headings in small form: on-disk format changes with version markers, mixed-version behaviour, upgrade path and prerequisites, rollback path, runbook entries. Also: surfaces touched, the version bump per surface or the Apache test that passes unchanged, what the change writes to shared state, for a change with a switch when off and when on, and the impact on the other line. For each form the change stores or sends: the version it records and, for a sent form, how the receiver knows it. For each value a reader can meet that another release or node wrote: the reader's answer, passed over or refused, and the step that avoids a node that does not start. For each file a node reads back: what the node does when it is absent after a crash, and for an appended file how the reader finds the last complete record. For state kept when a write is applied: each route a write arrives by and data that arrives as files, or one line that no state is kept. What a client sees while nodes differ in a setting. How the feature is removed, and what is removed when an object stops using it. See [PRINCIPLE-084](../principles.md#principle-084) to [PRINCIPLE-088](../principles.md#principle-088), [PRINCIPLE-019](../principles.md#principle-019), [PRINCIPLE-024](../principles.md#principle-024) and [PRINCIPLE-089](../principles.md#principle-089). Or "does not apply, because".}

## 10. Threat model and security

{For a one-item change, every new entry point checked with STRIDE, each mitigation a REQ, or "no new entry point" with the reason. For any change: the input it parses, the bound on each input, any code it loads by a name a client supplies with the allow list entry that permits it, the permissions it needs with a negative test per permission, the audit entries, the limits and what happens as each is approached and reached, for example warn and fail thresholds, and how errors map to client errors.}

## 11. Dependencies

{Each new library or version change with version, ASF category, NOTICE and credit lines, known vulnerabilities and why it is needed, one library per line or table row. Name a library by its Maven `group:artifact` or artifact, its pip name, its file name under `lib/` without the version, or `accord` for the Accord submodule, and give the exact version, or the commit for Accord. A check reads the library and the version from the same line. Or "No new dependency".}

## 12. Compliance impact

{Copies of data and what deletes each, with the stock copies that also hold the value, erasure, minimisation, masking, access control, audit, logging, cryptography, data residency, backups and snapshots, supply chain, secure defaults, retention, and one paragraph for operators naming the settings.}

## 13. Documentation

{The pages this change adds or edits. Every new yaml key, option, metric, virtual table, nodetool command and error string by exact name. Failure behaviour for each way the change can fail, for example a timeout, a failed coordinator, a missing replica, a limit hit, a full disk or a node restart in the middle of the operation. Known limitations.}

## 14. Testing

{The test levels required. RF 1 and RF 3 on the same data for anything that runs across nodes, and two data centres where a data centre aware consistency level or replication strategy is involved. Both sstable formats, and every test configuration [testing.md](../testing.md#test-levels) asks for, for anything that reads a setting the test configurations set differently, for example anything touching compaction, an on-disk format or the memtable. What the parity suite will check. A changed assertion, expected value or error text of a merged test of the project's own is named here: which one, from what to what, and why the old expectation is no longer right, see [PRINCIPLE-065](../principles.md#principle-065). See [testing.md](../testing.md).}

{For an item of a fork feature: the scenarios this pull request adds under `test/bdd/`, tagged `@wip` and with their requirement tags. See [testing.md](../testing.md#scenarios).}

Scenario runner: {the command that runs the scenarios, with {tags} once}

Scenario tags: {the tag expression for this item's scenarios}

{Keep the names of these two lines and write each on one line, since a check may read them. The runner is `ant` or a script under `tools/chronitondb/`, and it runs as plain words, never through a shell. Without the tags line, the item's scenarios are those tagged with the requirement ids this record defines. An item with no scenarios leaves out both lines.}

{For each stock test file or stock test data file that pins a complete listing this item extends, such as the stored help text of a command, the options a DESCRIBE prints, a golden file or a class list: one line in this form, and under it in words the lines the change adds. The file also stands in the Planned file list as `test`. The change only adds lines to the file. No existing line is removed or altered. Keep the line's name and write the path alone on it, since a check may read the line. An item that extends no such listing leaves the line out. See [PRINCIPLE-013](../principles.md#principle-013).}

Pinned listing: {the file's path from the repository root}

{Then these five lists. Keep the headings exact, since a check may read the lists. One fully qualified test class per line. Write `none` under a heading that has no entry.}

### Tests for this change

{The new and changed tests that prove each requirement.}

### Existing suites at risk

{Unit test suites and in-JVM distributed test suites this change could break.}

### Apache Cassandra suites run unchanged

{Apache Cassandra's own suites that MUST pass without modification.}

### Tracing test

{The test that shows the change in query tracing, for a change on a traced request. A change with other signals names their tests here too, for example the test of a new metric or log line of a compaction change. Or "does not apply, because" with the reason.}

### Formats and configurations

{`yes` when the change reads a setting the test configurations set differently, for example when it touches compaction, an on-disk format or the memtable, so the tests also run with both sstable formats and in every test configuration [testing.md](../testing.md#test-levels) asks for. Otherwise `no`.}

## 15. Not covered and follow-ups

{What stays out, each with the decision that put it out, stated cleanly. Candidate issues for anything found on the way.}

## New terms

{Terms this item needs that are not in the feature spec's glossary, each with a one line definition and its name in code, CQL and docs. The architect adds them to the glossary. Write "None." when there are none.}

## Where problems could occur

{Where the change could go wrong if it is wrong, worst case first: what a user or an operator would see (a wrong result, an error, a crash, a slow request, a changed file on disk), on which request path, and from which part of the change. Never "None" or "Low", and never an argument that the change is safe. After the "Where problems could occur" section of Ubuntu's stable release update template. An item of a feature whose feature spec the References row links, as a Markdown link to its `feature-spec.md`, MAY write the one line `Not applicable: <reason>` here, the reason naming the spec's section 4 that covers it. Every other design record fills it. See [classification.md](../classification.md).}

### Test plan

{For each problem above, the test that would catch it and what it checks. A problem no test covers says why, and how it is watched instead. Left out when the section above says Not applicable.}

## Planned file list

{One file per line: the exact path from the repository root, a space, then one word: `new`, `edit`, `test` or `stock`. No wildcards. The developer edits only these files. The reviewer holds the developer to this list. Keep its form exact, since a check may read it.}

The four words:

1. `new`: a file the line does not have yet that is not a test.
2. `edit`: an existing ChronitonDB file.
3. `stock`: an existing Apache Cassandra file that is not a test.
4. `test`: any test file, new or existing. A pre-existing stock test file is listed only in three cases: a fix to stock the maintainers approved, a complete listing the file pins that this record names in a Pinned listing line with the lines added, or a decision record that names the file and the issue and explains in writing why the change to the test is needed. See [PRINCIPLE-013](../principles.md#principle-013).

```
src/java/org/apache/cassandra/example/Example.java stock
test/unit/org/chronitondb/example/ExampleTest.java test
```

### Shared with open items

{One row per open item whose pull request changes a file in the list above. The designer checks the open pull requests for changes to the planned files. The kind is `soft` when the open item changes other lines of the same file, and `hard` when it changes the same lines. A hard overlap stops the work, and the maintainers decide which item goes first. Write "None." in place of the table when no open item shares a file. Keep its columns exact, since a check may read the table.}

| Item | Shared file | Kind |
|---|---|---|
| {#issue of the open item} | {path} | {soft or hard} |

### Waivers

{Any waiver of a shape limit, with the method, the rule and the reason. Write "None." when there are none.}

## Requirement quality checklist (ISO/IEC/IEEE 29148)

Check every requirement against these seven qualities before asking for approval. The reviewer judges against the same list.

1. **Necessary:** it traces to an acceptance criterion, a named risk, a decision record or a principle by its id. Removing it would lose something the issue asks for.
2. **Unambiguous:** it has one reading. No "large" without a number and a unit, and no "fast", "quickly" or "efficient" without a number or the mechanism that makes it so.
3. **Singular:** one requirement, one BCP 14 key word, one EARS shape. Two requirements joined by "and" are split into two ids.
4. **Verifiable:** a scenario, test or benchmark can prove it, and a scenario tag or `ac-coverage.md` names it. A requirement that needs tests at two levels keeps one id and names both tests.
5. **Feasible:** the mechanism exists in the tree or in this design, cited with the project, branch and commit, the symbol, and the file and line.
6. **Consistent:** it contradicts no other requirement, no decision record and no principle.
7. **Traceable:** it has an id, a source, and a scenario tag or exactly one coverage row.

A requirement that fits none of the five EARS shapes is rewritten until it fits one.
