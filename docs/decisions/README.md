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
