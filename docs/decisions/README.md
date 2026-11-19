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

ChronitonDB keeps its decisions as decision records, in MADR format (Markdown Architectural Decision Records). This folder holds the rules, the template and the records of the whole project. The records of one feature live with that feature. See rule 1.

## When a record is written

A decision record is written for every answered question that changes or settles behaviour, scope or process. A choice with no effect a user or an operator sees needs no record. Nor does a detail of form where Apache Cassandra's convention for that kind of thing leaves little choice: the contributor lists it in the Idiom and consistency section of the design record, or in the pull request description where the work has no design record, and the maintainers' merge confirms it. Whether there is a row, an error, a refusal, a default, a limit or an output, and what it means, is always a decision of the maintainers: [PRINCIPLE-057](../process/principles.md#principle-057). An exception to a principle is stated in the design record or fix record of the work that needs it and marked in its `Exceptions` row, with no decision record of its own. For example:

1. A behaviour a user or operator sees: which rows a query returns, an error, a refusal, a default, the output of a nodetool command, the name of a metric.
2. A change to an approved feature spec, plan or delivery plan.
3. A point of scope: what a feature includes or leaves out.
4. A rule of the development process.
5. A grant, lapse, restoration or removal of commit rights. See [governance.md](../process/governance.md).

The role that asked the question writes the record, in the pull request that follows the answer: the designer in the design record's pull request, the developer in the code pull request, the architect in the pull request that updates the feature spec, plan or delivery plan, the integrator in the import pull request. A question from the security engineer or the release engineer that settles behaviour, scope or process gets its record from a maintainer. The maintainers approve each record by merging, after the reviewer's review.

## Rules

1. Each record is one file named by its id: `DEC-<KEY>-nnnn-<slug>.md`. The id is `DEC`, a key and a number of four digits or more, counted from `0001` under that key. The slug is lower case words joined by single hyphens.
   1. A decision of one feature lives with the feature, in `docs/design/<KEY>-<slug>/decisions/`, under the [feature's key](../process/additive.md#feature-keys-and-requirement-ids). For example `docs/design/VER-release-version/decisions/DEC-VER-0001-<slug>.md`. Every item of the feature writes its records there.
   2. A decision of work that has no feature key, such as a fix, lives in that work's design directory under its issue number: `docs/design/<issue>-<slug>/decisions/DEC-<issue>-nnnn-<slug>.md`.
   3. A decision of the whole project, such as a rule of the development process or a change of commit rights, lives in this folder under the key `GOV`, which no feature may take: `docs/decisions/DEC-GOV-nnnn-<slug>.md`.
   4. A new record takes the next number of its key after the highest one merged on the line, in order with no gap. No two records share an id.
   5. The records of this folder named by a number alone, `NNNN-<slug>.md`, were merged before records had ids. They stay as they were merged, under rule 2, and are cited by their number.
2. Records are never edited after they are merged, except to change their status. A later decision that replaces an earlier one is a new record that names the one it supersedes in its `Supersedes` row. In the same pull request the earlier record's status becomes "Superseded by" and the id of the later one, for example "Superseded by DEC-VER-0007".
3. A record states the decision cleanly with its reason. It does not quote the discussion that led to it, and it points to no private material.
4. The decision outcome uses BCP 14 key words where it is normative.
5. Each new file carries the ChronitonDB licence header. See [conventions.md](../process/conventions.md#licence-headers).
6. A record has no version and no revision history. It is never edited, so the record that supersedes it is its history. The documents that do change, such as a feature spec or a design record, carry a version and a revision history that names the record behind each version. See [conventions.md](../process/conventions.md#versions-and-revision-history).
7. The two links are checked both ways: a record named in a `Supersedes` row says "Superseded by" that record in its status, and a record whose status says "Superseded by" another is named in that one's `Supersedes` row. A record merged before the template had the `Supersedes` or the `Areas` row keeps none.
8. Each record names its [areas](../process/areas.md) in its `Areas` row.
9. Each new record keeps the template's Contents index, regenerated with `tools/chronitondb/doclint.py index --write <file>`. A record merged before the template had one stays as it was merged, under rule 2. See [conventions.md](../process/conventions.md#contents-index-of-process-documents).

## Template

```markdown
# DEC-<KEY>-nnnn. <Short title of the decision>

| Field | Value |
|---|---|
| Document type | Record (ISO/IEC/IEEE 15289), MADR |
| Status | Proposed, Accepted, or Superseded by DEC-<KEY>-nnnn |
| Date | <RFC 3339 date> |
| Deciders | The maintainers |
| References | <issue, pull request, feature spec, earlier records> |
| Areas | <one or more areas of docs/process/areas.md, joined by commas> |
| Supersedes | <the id of each record this one replaces, joined by commas, or None> |

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

Every record, of the project and of each feature, is listed in the generated index [docs/index/decisions.md](../index/decisions.md), with its status, areas and what it supersedes. Each feature directory lists its own in its `INDEX.md`. See [conventions.md](../process/conventions.md#generated-indexes).
