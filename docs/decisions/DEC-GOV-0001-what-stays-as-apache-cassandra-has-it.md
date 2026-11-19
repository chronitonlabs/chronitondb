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

# DEC-GOV-0001. What stays as Apache Cassandra has it, and what may differ

| Field | Value |
|---|---|
| Document type | Record (ISO/IEC/IEEE 15289), MADR |
| Status | Accepted |
| Date | 2026-11-18 |
| Deciders | The maintainers |
| References | [quality-requirements.md, Compatibility with Apache Cassandra](../process/quality-requirements.md#compatibility-with-apache-cassandra), [branching-and-review.md, Feature switches and defaults](../process/branching-and-review.md#feature-switches-and-defaults), [maintenance.md, Corrective: fixing a fault](../process/maintenance.md#corrective-fixing-a-fault), [release.md, What a release may contain](../process/release.md#what-a-release-may-contain), records 0002 and 0004 |
| Areas | project |
| Supersedes | None |

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in BCP 14 (RFC 2119, RFC 8174) when, and only when, they appear in all capitals, as shown here.

## Contents

- [Context and problem statement](#context-and-problem-statement)
- [Considered options](#considered-options)
- [Decision outcome](#decision-outcome)
  - [Consequences](#consequences)
- [More information](#more-information)

## Context and problem statement

The process pages said that stock Apache Cassandra behaviour is unchanged for anyone not using a ChronitonDB feature, with one named exception, `nodetool version`. The rule named one case and gave no route for the next one. The pages already held cases it did not list: a fix to a defect in stock code, the configuration file ChronitonDB ships, the start check of the minimum setup and the install paths of the package. The rule also treated what an operator sees in the same way as what an application sees, and it did not say who decides that a change to stock code is a fix. The project needed one rule that covers these cases.

## Considered options

1. Keep the rule and name each further case as another exception.
2. State the rule by who sees a difference, an application or an operator, and state apart what a fix to a defect in stock is and how it is approved.

## Decision outcome

Chosen option: "State the rule by who sees a difference", because a rule that says what must hold covers the cases the pages already have and the ones to come, and a list of exceptions does not.

1. An application that moves onto ChronitonDB MUST behave as it did on Apache Cassandra, and a user MUST be able to move back to Apache Cassandra.
2. A change to what an application sees from a stock feature is a feature. What an application sees is its results, its errors, its warnings and the bytes on the wire. Such a feature MUST sit behind a feature switch that is off by default.
3. What an operator sees SHOULD stay as stock where that is reasonable. What an operator sees is metrics, nodetool output, logs and JMX. A difference there MUST be recorded in the delta register and in the release notes. It is recorded, not refused.
4. A fix to a defect in stock is not a feature and MUST NOT be gated behind a switch. It is applied, with its fix record, its delta entry and a release note.
5. A change to stock code counts as a fix to a defect only when the maintainers approve it as one. The evidence is a test that reproduces the fault and fails before the change, and either an Apache Cassandra ticket that treats the behaviour as a bug or the documented behaviour the fault breaks. The reviewer reviews that evidence in the fix record's pull request and says whether the fault is a defect and whether it needs an Apache ticket. The maintainers' merge of that pull request, made with the reviewer's finding in it, is the approval. A fix record that is not merged is not a fix, and code for it MUST NOT merge before it. The reviews of a security fix stay in its private advisory until disclosure, and the maintainers read them there.
6. A change to stock behaviour that the maintainers have not approved as a fix is a behaviour change under point 2.
7. A statement that Apache Cassandra rejects only because it uses something Apache Cassandra does not have, such as new syntax, a new keyword, a new option or a new index type, MAY succeed on ChronitonDB as a purely additive feature. A statement that Apache Cassandra accepts as valid and refuses for a reason, such as a missing `ALLOW FILTERING`, a guardrail or a missing index, is stock behaviour: making it succeed is a change under point 2.
8. The release version that `nodetool version` prints is a difference of the kind in point 3. It is no longer an exception to a rule.

### Consequences

- Good: one rule covers a fix to stock, the shipped configuration file, the start check and a changed tool output, with no list of exceptions to keep.
- Good: the feature switch rule keeps its full weight where it matters most, on what an application sees.
- Good: a fix to stock has one stated route, and its approval is a merge that anyone can see.
- Bad: a difference an operator sees is judged case by case, on whether staying as stock is reasonable. The delta register and the release notes are how operators learn of each one.
- Bad: the parity suite can no longer compare every output with stock. It compares what an application sees, and it reads the delta register for the recorded differences and fixes.

## More information

Records 0002 and 0004 stay as they were merged, and this record supersedes neither. Record 0002 still decides what `nodetool version` prints. Record 0004 still decides that the commit log disk check is off by default. Both speak of one exception to the off by default rule, which is how the pages put it when they were merged. Point 8 is how the pages put it now.

The pull request that adds this record changes the pages that stated the old rule, so that every copy changes together: the rule Compatibility with Apache Cassandra and its checklist lines in [quality-requirements.md](../process/quality-requirements.md), rules 3, 4 and 8 of Feature switches and defaults and the review standard for stock files in [branching-and-review.md](../process/branching-and-review.md), What a release may contain and What nodetool version shows in [release.md](../process/release.md), the Feature class and Parity suite entries of the glossary in [README.md](../process/README.md), Claims about code in [conventions.md](../process/conventions.md), the floor in [classification.md](../process/classification.md), Stock faults in [maintenance.md](../process/maintenance.md), Offering changes upstream in [upstream.md](../process/upstream.md), rule 3 of the Policy in [testing.md](../process/testing.md), section 2.8 of the [feature spec template](../process/templates/feature-spec.md), section 8 of the [fix record template](../process/templates/fix-record.md) and the front page of the repository.
