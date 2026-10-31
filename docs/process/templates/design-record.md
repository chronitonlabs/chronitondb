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

Change history: the git history of this file.

Location: `docs/design/<issue>-<slug>/`, with the coverage file `ac-coverage.md` next to it. Every section is filled, or carries a waiver with its reason. An empty section blocks approval.

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in BCP 14 (RFC 2119, RFC 8174) when, and only when, they appear in all capitals, as shown here.

## 1. Problem, acceptance criteria and requirements

{The problem in plain words. The acceptance criteria quoted from the issue or the plan item. Context and rationale stay in prose.}

### Requirements

{One requirement per entry: an id `REQ-n`, one EARS shape, one BCP 14 key word, and its source. For an item of a feature, the source is an acceptance criterion in the plan, and through it a FREQ. Otherwise it is an acceptance criterion in the issue, a risk this record names, or a decision record. Each id has exactly one row and one test in `ac-coverage.md`.}

The five EARS shapes, one example each:

REQ-1 (ubiquitous): The index MUST return the same rows for a query in the memtable, after flush and after compaction. Source: {...}.

REQ-2 (event driven): When the toggle is changed with nodetool, the node MUST log the old and the new value at INFO. Source: {...}.

REQ-3 (state driven): While the feature switch is off, the node MUST refuse every statement that uses the feature's syntax. Source: {...}.

REQ-4 (optional feature): Where the timeout option is set to partial, the coordinator MUST mark the result as partial. Source: {...}.

REQ-5 (unwanted behaviour): If a node reads a file with an unknown version marker, then the node MUST refuse to open it and log the file name. Source: {...}.

## 2. Decisions implemented

{Each decision record by number, with a one line reminder and its date. A statement that no newer record exists on the same subject as of the date of this record.}

## 3. Stock behaviour preservation

{One row per departure from stock, in this table. Write "No departures from stock." in place of the table when there are none. Code defaults in stock classes unchanged. Tooling reads this table, so keep its columns.}

| Stock behaviour today (file and line) | This change | Switch that controls it | Error text naming the switch |
|---|---|---|---|
| {stock behaviour} | {change} | {switch} | {error text} |

## 4. Prior art reviewed

{Stock code on each line with file and line. Other projects by behaviour. Apache JIRA tickets read with their comments. What each got right or wrong for this problem.}

## 5. Idiom and consistency

{For each user visible choice: whether it matches stock, earlier decisions and the idiom it follows, and the reason for any deliberate difference.}

## 6. Quality requirements

{For a one-item change, the checklist table from [quality-requirements.md](../quality-requirements.md), each line answered with REQ ids or a reason it does not apply. For an item of a feature, cite the feature spec lines this item delivers.}

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

{Each new library or version change with version, ASF category, NOTICE and credit lines, known vulnerabilities and why it is needed. Or "No new dependency".}

## 12. Compliance impact

{Copies of data and what deletes each, erasure, minimisation, masking, access control, audit, logging, cryptography, data residency, backups and snapshots, supply chain, secure defaults, retention, isolation levers, and one paragraph for operators naming the settings.}

## 13. Documentation

{The pages this change adds or edits. Every new yaml key, option, metric, virtual table, nodetool command and error string by exact name. Failure behaviour on timeout, coordinator failure, missing replica, limit hit and index not built. Known limitations.}

## 14. Testing

{The test levels required. RF 1 and RF 3 for anything multi node. Both sstable formats and both unit test configurations for anything touching compaction or formats. What the parity suite will check. See [testing.md](../testing.md).}

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

## Planned file list

{One file per line: the exact path from the repository root, a space, then one word: `new`, `edit`, `test` or `stock`. No wildcards. The developer edits only these files, and tooling enforces the list as written here.}

```
src/java/org/apache/cassandra/example/Example.java stock
test/unit/org/apache/cassandra/example/ExampleTest.java test
```

### Waivers

{Any waiver of a shape limit, with the method, the rule and the reason. Write "None." when there are none.}

## Requirement quality checklist (ISO/IEC/IEEE 29148)

Check every requirement against these seven qualities before asking for approval. The reviewer judges against the same list.

1. **Necessary:** it traces to an acceptance criterion, a named risk or a decision record. Removing it would lose something the issue asks for.
2. **Unambiguous:** it has one reading. No "fast", "large", "quickly" or "efficient" without a number and a unit.
3. **Singular:** one requirement, one BCP 14 key word, one EARS shape. Two requirements joined by "and" are split into two ids.
4. **Verifiable:** one test or benchmark can prove it, and `ac-coverage.md` names it.
5. **Feasible:** the mechanism exists in the tree or in this design, cited with file and line.
6. **Consistent:** it contradicts no other requirement, no decision record and no stock behaviour rule.
7. **Traceable:** it has an id, a source and exactly one coverage row.

A requirement that fits none of the five EARS shapes is rewritten until it fits one.
