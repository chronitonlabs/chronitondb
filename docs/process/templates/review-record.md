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

# Review record: {work product} of #{issue} {title}

| Field | Value |
|---|---|
| Title | Review record: {work product} of #{issue} {title} |
| Document type | Record (ISO/IEC/IEEE 15289) |
| Status | Open or Closed |
| Work product | {Design record, fix record, code change, feature spec, plan and delivery plan, milestone report, change control, import, release proposal, release promotion, dependency update or documentation change}: `{the main document's path, or the branch}` |
| Pull request | #{n} |
| Version reviewed | {the head commit the newest round read, by its short hash, or Not reviewed yet} |
| Review type | {Inspection or Technical review} (ISO/IEC 20246) |
| Reviewer | {the GitHub account that posts the verdict: the project's review App. Never the author's account} |
| Author | {role}: {GitHub username} |
| Decision maker | The maintainer who merges the pull request |
| References | Issue #{issue}. {The record, spec or plan the work product implements, by path.} |

A review record has no version. Its history is the commits of this file.

Location: `docs/reviews/<work>.md`, where `<work>` is the pull request's branch without its first part, `agent/` or a username, and without the line. An import branch keeps its first part, as `import-`. Process: [branching-and-review.md](../branching-and-review.md#the-review-record). Structure: the review record of ISO/IEC 20246 and the review report and anomaly list of IEEE 1028. The review record of a security fix is not committed: it is kept in the private advisory and stays there after disclosure, see [security.md](../security.md#private-until-disclosure).

Only the project's own automation keeps this record: it is the committed record of the review of a pull request the automation wrote. An outside contributor writes none, and the findings on such a pull request come as ordinary review comments. The author keeps this record current and commits it with the change: when the pull request opens, after each review round and after the last one. It states in the third person what each round found, what was done about each finding and what the maintainers decided.

{How the record is kept. The pull request opens with it: Status Open, Version reviewed `Not reviewed yet`, the Rounds table and the anomaly list with their header rows only, `No decisions.`, `None.` and `Open.`. After each round, and before the work goes back to the reviewer, the author adds the round's row, one row for each finding with its disposition, each decision a maintainer took and what the round did not read. The counts of a round equal the counts of the reviewer's comment for that round, and every finding of an earlier round has a disposition. After a clean review the author adds its round and its findings, sets Status to Closed and writes the exit decision. Entries are short and plain: what was found, where, what was done about it and who decided. A decision is stated cleanly, with its options and its reason, never in a maintainer's own words from a conversation. The record cites nothing a reader of the repository cannot open.}

## Contents

- [1. Rounds](#1-rounds)
- [2. Anomaly list](#2-anomaly-list)
- [3. Decisions](#3-decisions)
  - [D{n}. {The question in one line}](#dn-the-question-in-one-line)
- [4. Limits](#4-limits)
- [5. Exit decision](#5-exit-decision)

## 1. Rounds

| Round | Date | Version reviewed | Scope | Verdict | Blockers | Majors | Minors | Nits |
|---|---|---|---|---|---|---|---|---|
| {n} | {YYYY-MM-DD} | `{short hash}` | {The whole change, or the changes since `{short hash}`} | {Changes requested or Clean} | {n} | {n} | {n} | {n} |

## 2. Anomaly list

One row per finding, in the reviewer's order. The id is `R<round>-<number>`. A finding raised again in a later round gets a new id and names the earlier one.

| Id | Location | Description | Classification | Disposition |
|---|---|---|---|---|
| R{round}-{n} | {the symbol or the heading}, `{path}:{line}` at `{commit}`, or {the pull request title or body} | {What is wrong, in short.} | {Blocker, Major, Minor or Nit} | {Fixed in `{short hash}`, Accepted: {reason}, Waived by {the maintainers}: {reason}, or Open: {what settles it}} |

1. **Fixed in `<hash>`**: the commit that fixes the finding, a commit of the pull request's branch. Several commits are joined with "and". A finding on the pull request's title or body is "Fixed in the pull request title" or "body".
2. **Accepted: `<reason>`**: the work product stays as it is, for the reason given. The reviewer judges the reason in the next round.
3. **Waived by `<the maintainers>`: `<reason>`**: the maintainers decided the finding needs no change, as "the maintainers" or "a maintainer, `<GitHub username>`". A waiver counts only as a maintainer's line in the set form on the pull request, such as `Waived: R1-3`: see [branching-and-review.md](../branching-and-review.md#the-review-record), item 4. Until then the disposition is Open.
4. **Open: `<what settles it>`**: no disposition yet, while the maintainers decide. A clean review leaves none open from an earlier round.

## 3. Decisions

{One subsection per decision the maintainers took during the review, in the form below, or the one line "No decisions.". A decision counts only as a maintainer's line in the set form on the pull request, such as `Decided: D1 B`, with the id of the decision and the letter of its Chosen line: see [branching-and-review.md](../branching-and-review.md#the-review-record), item 4.}

### D{n}. {The question in one line}

- **Raised by:** R{round}-{n}.
- **Options:** A. {option}. B. {option}.
- **Chosen:** {letter}. {option}.
- **Reason:** {Why, in one or two sentences.}
- **Decided by:** {the maintainers, or a maintainer by GitHub username}, {YYYY-MM-DD}, {the decision record by its id and path, such as `DEC-GOV-0001` in `docs/decisions/`, when there is one}.

## 4. Limits

{What a round did not read or run, with the round and the reason, or the one line "None.". A clean round leaves nothing not reviewed.}

## 5. Exit decision

{While Status is Open, the one line "Open.". Once Closed, one of these three. Accept: round {n} on `{short hash}` found no blocker and no major, and every finding has a disposition. The maintainers decide by merging. Rework: after round {n} blockers or majors remain, and the open points went to the maintainers as decision D{n}. Reject: the maintainers closed the pull request, for the reason given.}
