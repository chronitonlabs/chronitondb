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

# New features (additive maintenance)

A new feature is additive maintenance in ISO/IEC/IEEE 14764:2022. A feature that needs several items takes three levels of specification. A feature that fits in one item takes the one-item path.

## Size boundary

1. A feature that fits one item, one design record and one pull request per line takes the one-item path described in [maintenance.md](maintenance.md#the-one-item-path). Its design record carries the feature spec's mandatory sections in small form.
2. A feature that needs several items, or a design decision across components, takes the three levels below.
3. If a one-item change turns out to need several items or a design decision across components, the designer stops and asks the maintainers. Such a change moves to the three levels below and keeps its maintenance category.

## The three levels

Each level is approved by a merged pull request before the next level starts. Lower levels cite the level above. They never restate it.

| Level | Document | Author | Location |
|---|---|---|---|
| 1 | Feature spec | Architect | `docs/design/<feature>/feature-spec.md` |
| 2 | Plan and delivery plan | Architect | `docs/design/<feature>/plan.md` and `docs/design/<feature>/delivery-plan.md` |
| 3 | Item design record | Designer | `docs/design/<issue>-<slug>/` |
| Gates | Milestone reports | Architect | `docs/design/<feature>/milestones/` |

All three live on the line the feature targets.

Each large feature has its own public GitHub issue, opened by the architect. Its number names the branches of the feature spec, plan, delivery plan, milestone report and change control pull requests. Each item then has its own issue, opened by the designer.

### Level 1: the feature spec

The feature spec says what the feature is and why. It is written from [templates/feature-spec.md](templates/feature-spec.md) and contains:

1. Purpose and scope, with non-goals.
2. Architecture in short arc42 form: context, building blocks, interfaces, on-disk and wire formats, runtime behaviour, observability, limits.
3. Feature requirements, each with an id `FREQ-n`, one EARS shape, one BCP 14 key word and a source.
4. Quality requirements, answering every line of [quality-requirements.md](quality-requirements.md).
5. Threat model: every new entry point checked with STRIDE, each mitigation a FREQ, or the statement that there is no new entry point.
6. Compatibility: on-disk format changes with their version markers, behaviour in a mixed-version cluster during a rolling upgrade, the upgrade path and prerequisites, the rollback path, and the runbook entries. A feature with no format, schema or protocol change says so.
7. Dependencies: each new library or version change with its ASF licence category, NOTICE and credit lines, known vulnerabilities and the reason it is needed. See [compliance.md](compliance.md).
8. Risks, each with likelihood, impact and mitigation.
9. Decisions, as links to decision records.
10. A milestone outline.

A maintainer approves the feature spec by merging its pull request.

### Level 2: the plan and the delivery plan

The plan lists the items that deliver the feature spec. It is written from [templates/plan.md](templates/plan.md). For each item it gives:

1. The feature requirements the item delivers.
2. Its acceptance criteria.
3. Its dependencies on other items.
4. The line it targets.
5. Whether it can run in parallel with other items.

Every feature requirement MUST be delivered by at least one item. Small, cohesive work stays in one item. Work is split only at a real boundary: a real prerequisite, output that can be built in parallel, or a part that needs its own review.

The delivery plan orders the items. It follows ISO/IEC/IEEE 16326 and is written from [templates/delivery-plan.md](templates/delivery-plan.md). It contains:

1. **Milestones.** Each milestone is an increment that can be tested and shown.
2. **Order rationale.** Why the milestones come in this order, for example the riskiest part first.
3. **Exit criteria.** What must be true before a milestone is done. A milestone that introduces an on-disk format change has upgrade and rollback tests among its exit criteria.
4. **Release and line mapping.** The release and line each milestone ships in.
5. **Parallel work limit.** How many items may be in progress at once.
6. **Re-plan triggers.** What events cause a re-plan.
7. **Test plan.** The ISO/IEC/IEEE 29119 test plan for the feature. See [testing.md](testing.md).

The plan and the delivery plan are each approved by a merged pull request before any item starts.

### Level 3: the item design record

Each item gets a design record from [templates/design-record.md](templates/design-record.md), written by the designer. Each requirement `REQ-n` cites an acceptance criterion in the plan, and through it a feature requirement. A maintainer approves the design record by merging its pull request. Only then does implementation start.

## The line for a feature

There is no standing default line for new features. The architect proposes the line in the delivery plan. The maintainers decide when they merge it. A feature built on one line and later ported to the other carries the port as later milestones, made of items merged into the other line the same way.

## Validation items

Each milestone in the plan has validation items next to its build items. A validation item holds end to end tests written from the feature requirements: in-JVM distributed tests, and Python distributed tests where needed. The developer builds them. The reviewer reviews them like any item. They MUST pass before the milestone report is written.

## Documentation with each item

An item is not done until the user documentation, operator documentation and runbook entries it affects are in the same pull request. The reviewer checks them. At each milestone gate the architect checks that the feature's documentation reads as one whole. Release notes are generated from commits at release.

## Milestone gates

Only the current milestone is in progress. When all its items are merged:

1. The architect writes the milestone report in `docs/design/<feature>/milestones/` from [templates/milestone-report.md](templates/milestone-report.md). It is the ISO/IEC/IEEE 29119 test completion report for the milestone: what was tested and at which levels, results against the exit criteria, deviations, remaining risks, and a go or no-go recommendation.
2. The report reviews every risk in the feature spec as open, reduced, closed or happened. It adds new risks with likelihood, impact and mitigation. It says whether the remaining milestones should be re-ordered.
3. A maintainer approves the gate by merging the report's pull request.
4. The next milestone starts only after that merge.

Until its final milestone gate, the feature's switch refuses to turn on. The final gate makes the feature switchable: operators MAY then turn it on with yaml or nodetool. Its default stays off for the life of the line. A default MAY be on only in a new line. See [branching-and-review.md](branching-and-review.md#every-fork-feature-is-off-by-default) and [release.md](release.md#what-a-release-may-contain).

## Change control after a merge

An approved feature spec, plan or delivery plan changes only through this path:

1. Whoever finds a needed change raises it with the maintainers. Work that depends on it waits.
2. The maintainers' answer becomes a [decision record](../decisions/README.md).
3. The architect updates the feature spec, plan or delivery plan in a small pull request that cites the decision record.
4. Waiting work resumes after that pull request is merged.

Re-planning normally happens at a milestone gate. Changes to the risk list follow the same path.

One exception: a patch-version update of an approved library, under the same licence, for a bug fix or a security fix, MAY be made by the developer inside the item. The same pull request records it in the feature spec's Dependencies section with its reason.

## How work moves between approval points

Once a maintainer approves a step, the next step starts without further request:

1. After the plan and delivery plan merge, the items of the first milestone start.
2. After an item's design record merges, its implementation starts.
3. When an item's pull request opens, its review starts.
4. After a milestone report merges, the items of the next milestone start.

Each step starts only from an approved document. Nothing starts that is not in a merged plan. The work items of an approved plan are requested by the maintainer who approved it, and that maintainer answers for them.
