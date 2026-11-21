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

# Review record: feature spec of #161 Let operators see a node's JVM memory pools from CQL

| Field | Value |
|---|---|
| Title | Review record: feature spec of #161 Let operators see a node's JVM memory pools from CQL |
| Document type | Record (ISO/IEC/IEEE 15289) |
| Status | Open |
| Work product | Feature spec: `docs/design/JVMEM-jvm-memory-pools-view/feature-spec.md` |
| Pull request | #162 |
| Version reviewed | `3db6b0aad9` |
| Review type | Technical review (ISO/IEC 20246) |
| Reviewer | The project's review App |
| Author | Architect: chronitondb-agent |
| Decision maker | The maintainer who merges the pull request |
| References | Issue #161. The feature spec `docs/design/JVMEM-jvm-memory-pools-view/feature-spec.md` and its decision records `DEC-JVMEM-0001` to `DEC-JVMEM-0011` under `docs/design/JVMEM-jvm-memory-pools-view/decisions/`. |

A review record has no version. Its history is the commits of this file.

Location: `docs/reviews/<work>.md`, where `<work>` is the pull request's branch without its first part, `agent/` or a username, and without the line. An import branch keeps its first part, as `import-`. Process: [branching-and-review.md](../process/branching-and-review.md#the-review-record). Structure: the review record of ISO/IEC 20246 and the review report and anomaly list of IEEE 1028. The review record of a security fix is not committed to the branch that lands: it is kept in the private advisory and stays there after disclosure, see [security.md](../process/security.md#private-until-disclosure).

Only the project's own automation keeps this record: it is the committed record of the review of a pull request the automation wrote. An outside contributor writes none, and on such a pull request the verdict's own review comment for the round carries the findings, one row for each finding. The author keeps this record current and commits it with the change: when the pull request opens, after each review round and after the last one. It states in the third person what each round found, what was done about each finding and what the maintainers decided.

## Contents

- [1. Rounds](#1-rounds)
- [2. Anomaly list](#2-anomaly-list)
- [3. Decisions](#3-decisions)
  - [D1. Is the view with no hold back an exception to two principles, or do they not apply to it](#d1-is-the-view-with-no-hold-back-an-exception-to-two-principles-or-do-they-not-apply-to-it)
  - [D2. Does a read of the view make the Touches row name a request path](#d2-does-a-read-of-the-view-make-the-touches-row-name-a-request-path)
- [4. Limits](#4-limits)
- [5. Exit decision](#5-exit-decision)

## 1. Rounds

| Round | Date | Version reviewed | Scope | Verdict | Blockers | Majors | Minors | Nits |
|---|---|---|---|---|---|---|---|---|
| 1 | 2026-11-21 | `f83b59022b` | The whole change | Changes requested | 0 | 2 | 7 | 2 |
| 2 | 2026-11-21 | `3db6b0aad9` | The changes since `f83b59022b` | Changes requested | 0 | 1 | 6 | 2 |

## 2. Anomaly list

One row per finding, in the reviewer's order. The id is `R<round>-<number>`. A finding raised again in a later round gets a new id and names the earlier one. The source says which checklist raised the finding, or that the security engineer's review did. On Critical risk work the security engineer's findings reach the record only through the reviewer, and stand here as rows like any other.

| Id | Location | Description | Source | Classification | Disposition |
|---|---|---|---|---|---|
| R1-1 | Item 3 of `Decision outcome`, `docs/design/JVMEM-jvm-memory-pools-view/decisions/DEC-JVMEM-0001-jvm-memory-pools-view-has-no-switch.md:67` at `f83b59022b` | The record chooses no hold back and does not say whether that departs from PRINCIPLE-003 and the edge of PRINCIPLE-089. Section 11 leaves the point to a design record, which cannot settle it. | compatibility | Minor | Fixed in `ec285c4163` |
| R1-2 | Case 2 of `2.2 Building blocks`, `docs/design/JVMEM-jvm-memory-pools-view/feature-spec.md:139` at `f83b59022b` | A plain aggregate with no page size is one read with no limit. The 10000 rows hold for `GROUP BY` only. Fact 17 and DEC-JVMEM-0008 carry the same statement. | correctness | Major | Fixed in `9dc090163b` |
| R1-3 | Item 4 of `2.5 Cross cutting concepts`, `docs/design/JVMEM-jvm-memory-pools-view/feature-spec.md:187` at `f83b59022b` | Three behaviours are stated inexactly: the DEBUG line holds for subnets, the heap histogram property changes the handling of an out of memory error, and a JVM can make a call throw. DEC-JVMEM-0010 carries the same statements. | docs | Major | Fixed in `f48f3be590` |
| R1-4 | Item 4 of `2.5 Cross cutting concepts`, `docs/design/JVMEM-jvm-memory-pools-view/feature-spec.md:187` at `f83b59022b` | The text says one or two ERROR lines. Each log call is given the exception, so each entry carries a stack trace. | correctness | Minor | Fixed in `041f3e6b7b` |
| R1-5 | The Touches row of `Feature spec: JVM memory pools view in CQL`, `docs/design/JVMEM-jvm-memory-pools-view/feature-spec.md:33` at `f83b59022b` | Needs verification: the reads of a statement with `IN` grow with the names listed, which may be a request path under classification.md. | correctness | Minor | Accepted: decision D2 keeps the Touches row as it is. Decision record DEC-JVMEM-0011 states the decision, added in `95049e31a0`. |
| R1-6 | Item 1 of `7.4 Rollback path`, `docs/design/JVMEM-jvm-memory-pools-view/feature-spec.md:323` at `f83b59022b` | The pointer to item 2 of the list below reaches "Nothing else is removed". It means the second of the four places where a grant row is read. | correctness | Minor | Fixed in `6419c3d0d2` |
| R1-7 | Facts 14 and 17 of `12. Prior art`, `docs/design/JVMEM-jvm-memory-pools-view/feature-spec.md:413` at `f83b59022b`, and line 416 | `Config.java:876` and `SelectStatement.java:773` in the Apache Cassandra columns name no symbol. | correctness | Minor | Fixed in `c0d4940222` and `9dc090163b` |
| R1-8 | Item 3 of the context and one consequence, `Context and problem statement`, `docs/design/JVMEM-jvm-memory-pools-view/decisions/DEC-JVMEM-0005-type-column-shows-heap-and-non-heap-as-jmx-does.md:46` at `f83b59022b` | "Shown by no surface of the JVM" and "unlike most text values" name no code that was read. | docs | Minor | Fixed in `5371654e96` |
| R1-9 | The pull request body, Open points | Two lines tell how the work went and not what stands open. The open points are to be stated as facts. | docs | Minor | Fixed in the pull request body |
| R1-10 | Item 4 of `2.5 Cross cutting concepts`, `docs/design/JVMEM-jvm-memory-pools-view/feature-spec.md:187` at `f83b59022b` | One list item of about 3,200 characters. It reads better split into answered, logged and not covered. | docs | Nit | Fixed in `0d4cfe5243` |
| R1-11 | `ThreadPoolsTable.ThreadPoolsTable`, `docs/design/JVMEM-jvm-memory-pools-view/decisions/DEC-JVMEM-0004-view-is-named-jvm-memory-pools.md:57` at `f83b59022b` | The citation names line 40, the header of the constructor. The key column is set at line 45. | docs | Nit | Fixed in `7d0ebe2eff` |
| R2-1 | The Answered and Logged parts of item 4 of `2.5 Cross cutting concepts`, `docs/design/JVMEM-jvm-memory-pools-view/feature-spec.md:188` at `3db6b0aad9`, and line 189. Also fact 23, line 428, and item 3 of the context of DEC-JVMEM-0010 | Out of memory handling is stated inexactly. The Answered part has no condition for the heap histogram property. The histogram lines are left out. So are the second ERROR entry and the forced heap space error for some messages. | docs, correctness | Major | Fixed in `bbe80cc01c` and `44b41269db` |
| R2-2 | `Decision outcome`, `docs/design/JVMEM-jvm-memory-pools-view/decisions/DEC-JVMEM-0010-the-view-catches-nothing-a-call-to-the-jvm-throws.md:73` at `3db6b0aad9`, and the Logged part of item 4 of `2.5 Cross cutting concepts` | The assessment under PRINCIPLE-036 says why an exception is unexpected. It gives no reason, bound or level for the entries of an out of memory error. With the property on, each later failing request logs at ERROR. | correctness | Minor | Accepted: by item 6 of DEC-JVMEM-0010 the spec says of an out of memory error only that it goes to Apache Cassandra's own handling, so it assesses no log entry of one. `44b41269db` takes that assessment out. |
| R2-3 | `Context and problem statement`, `docs/design/JVMEM-jvm-memory-pools-view/decisions/DEC-JVMEM-0009-an-error-for-one-pool-fails-every-read.md:42` at `3db6b0aad9`, and line 55 | The record says no JVM is known to raise such an error and gives that as a reason. DEC-JVMEM-0010 and the spec say any call can throw an out of memory error. The kind of error is not named. | docs, correctness | Minor | Fixed in `6105f1f50b` |
| R2-4 | `2.3 Runtime view`, `docs/design/JVMEM-jvm-memory-pools-view/feature-spec.md:176` at `3db6b0aad9` | "No other request path" reads the read of the view as a request path, against item 2 of section 2.5 and DEC-JVMEM-0011. | docs, correctness | Minor | Fixed in `aaa9460a16` |
| R2-5 | `Consequences`, `docs/design/JVMEM-jvm-memory-pools-view/decisions/DEC-JVMEM-0005-type-column-shows-heap-and-non-heap-as-jmx-does.md:65` at `3db6b0aad9` | The record says that the other tables were not read. They were read: four write the text of an enum in lower case and one in upper case. The result belongs in the record, with its tree. | docs | Minor | Fixed in `9152440a09` |
| R2-6 | `7.1 On-disk format changes`, `docs/design/JVMEM-jvm-memory-pools-view/feature-spec.md:309` at `3db6b0aad9` | The section says that the feature changes no schema. DEC-JVMEM-0001 says that the view is schema state under the edge of PRINCIPLE-089. Section 7 does not point to the exception. | compatibility | Minor | Fixed in `448251f162` |
| R2-7 | The pull request body, Open points, the note on decision record 0001 | The note names the wrong merge. The merge of the item's design record decides the exception, as principles.md and item 4 of DEC-JVMEM-0001 say. | compatibility | Minor | Fixed in the pull request body |
| R2-8 | The pull request body, Open points, the first sentences | Two sentences tell how the work went and not what stands open. | docs | Nit | Fixed in the pull request body |
| R2-9 | Fact 23 of `12. Prior art`, `docs/design/JVMEM-jvm-memory-pools-view/feature-spec.md:428` at `3db6b0aad9` | `SubnetGroups.contains`: line 64 is the header of the other overload. The match is at line 68, and at line 67 in cassandra-6.0 and trunk. | correctness | Nit | Fixed in `77b0ef3d4b` |

1. **Fixed in `<hash>`**: the commit that fixes the finding, a commit of the pull request's branch. Several commits are joined with "and". A finding on the pull request's title or body is "Fixed in the pull request title" or "body".
2. **Accepted: `<reason>`**: the work product stays as it is, for the reason given. The reviewer judges the reason in the next round.
3. **Waived by `<the maintainers>`: `<reason>`**: the maintainers decided the finding needs no change, as "the maintainers" or "a maintainer, `<GitHub username>`". A waiver counts only as a maintainer's line in the set form on the pull request, such as `Waived: R1-3`: see [branching-and-review.md](../process/branching-and-review.md#the-review-record), item 4. Until then the disposition is Open.
4. **Open: `<what settles it>`**: no disposition yet, while the maintainers decide. A clean review leaves none open from an earlier round.

## 3. Decisions

### D1. Is the view with no hold back an exception to two principles, or do they not apply to it

- **Raised by:** R1-1.
- **Options:** A. An exception to PRINCIPLE-003 and to the edge of PRINCIPLE-089, stated as one in decision record DEC-JVMEM-0001, for this view only. B. A reading that the two principles do not apply to a table of a virtual keyspace.
- **Chosen:** A. An exception to PRINCIPLE-003 and to the edge of PRINCIPLE-089, stated as one in decision record DEC-JVMEM-0001, for this view only.
- **Reason:** The principles stay as written. The edge of PRINCIPLE-089 calls anything added to such a keyspace schema state on every node, so a reading that leaves a virtual table out goes against its words.
- **Decided by:** a maintainer, `millerjp`, 2026-11-21, `DEC-JVMEM-0001` in `docs/design/JVMEM-jvm-memory-pools-view/decisions/`.

### D2. Does a read of the view make the Touches row name a request path

- **Raised by:** R1-5.
- **Options:** A. No. The Touches row stays as it is, a public interface and a new feature. B. Yes. The row adds a request path, the spec plans a benchmark of the read, and the review of the code runs the performance checklist.
- **Chosen:** A. No. The Touches row stays as it is, a public interface and a new feature.
- **Reason:** The cost of one read grows neither with the data a node holds nor with the traffic it serves. A statement with `IN` costs one such read for each name that its client lists.
- **Decided by:** a maintainer, `millerjp`, 2026-11-21, `DEC-JVMEM-0011` in `docs/design/JVMEM-jvm-memory-pools-view/decisions/`.

## 4. Limits

None.

## 5. Exit decision

Open.
