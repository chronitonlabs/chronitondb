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

# Testing

This page is the ChronitonDB test policy and test strategy in the sense of ISO/IEC/IEEE 29119. It says which tests exist, when each runs, and what must pass before work is done.

## Policy

1. Every requirement has at least one test that proves it. A requirement without a test is not done.
2. A fix starts with a test that reproduces the fault, written by the designer on the item's code branch. It MUST fail before the fix and pass after it. The test and the fix merge together, so the line never carries a failing test.
3. With every fork feature off, every line MUST behave exactly as stock Apache Cassandra. The parity suite proves it.
4. A test that existed before a change MUST NOT be weakened. A change to a pre-existing test is additive and named in the design record.
5. Tests MUST NOT depend on wall clock timing. Seeds are printed so a run can be repeated.
6. Results that depend on cluster topology are a fault. Multi node behaviour is tested at replication factor 1 and replication factor 3. See [quality-requirements.md](quality-requirements.md).

## Test levels

| Level | What it proves | Where |
|---|---|---|
| Unit tests | One class or component behaves as its requirements say | `test/unit/` |
| In-JVM distributed tests | Behaviour across several nodes in one JVM: replication, consistency, upgrade paths in process | `test/distributed/` |
| Python distributed tests | Behaviour of real node processes and tools, where in-JVM tests cannot reach | Apache Cassandra's Python dtest suite |
| Upgrade and rollback tests | A node moves from Apache Cassandra to ChronitonDB and back, and from one ChronitonDB release to the next, with data and queries intact during and after the roll | Upgrade tests for the supported paths |
| Benchmarks | Performance claims in a design record hold, and stock performance does not move | `test/microbench/` and the load tests the design names |
| Golden corpora | Output that must stay identical across library versions and lines, compared with a fixed expected result | Where a feature needs them |
| Parity suite | Stock behaviour is unchanged with every fork feature off | `test/parity/` and the normal build |

Changes that touch compaction or on-disk formats run on both sstable formats and both unit test configurations.

## Upgrade and rollback tests

1. ChronitonDB writes its own upgrade tests for its supported paths: from Apache Cassandra on the same major version to ChronitonDB, and from one ChronitonDB release to the next.
2. A milestone that introduces an on-disk format change has upgrade and rollback tests among its exit criteria.
3. Apache's own upgrade tests for paths ChronitonDB does not support are not run on the lines.

## Benchmarks

1. Pull request checks block only on counted values, such as allocations per operation, work counters and index bytes per raw byte, and on benchmarks that fail to run. They never block on timing.
2. Once dedicated benchmark hardware is in place, timing results are tracked over time, and a change point in the timings blocks the next release.
3. Absolute timing numbers come only from pinned or dedicated hardware.
4. Each design record names its benchmarks, their thresholds and the stock runs that must not move. See [templates/design-record.md](templates/design-record.md).

## When each test runs

| When | What runs |
|---|---|
| Before each commit | The developer's pre-commit test run: the build, the code checks, the tests the item adds and the existing tests that cover the changed code. Its results are the test log for that commit |
| On every pull request to a line, including pull requests from forks | The required checks in [branching-and-review.md](branching-and-review.md#required-checks) and the tests of the changed areas, on GitHub's own runners |
| Regularly, per line | The full Apache Cassandra test suites, with fork features off and with them on |
| At each milestone | The validation items, the upgrade and rollback tests the exit criteria name, the benchmarks, and the parity suite |
| At each import from Apache Cassandra | The full test suites, the parity suite and the tests named in the import record, before the merge |
| At each release candidate | The full test suites, signatures, installs, upgrade and rollback from the previous ChronitonDB release and from Apache Cassandra, and the parity suite, before promotion. See [release.md](release.md) |

## Full test suites

1. The full Apache Cassandra test suites run regularly on each line, with every fork feature off and with them on. They also run on every import and every release candidate.
2. They run on dedicated CI infrastructure, only for branches in this repository. Every pull request, including one from a fork, runs the GitHub checks and the tests of the changed areas on GitHub's own runners.
3. Results are compared with Apache Cassandra's own results for the same tests.
4. The release engineer checks the latest results daily, as a scheduled check, and opens a corrective item for each real failure.

## The ISO/IEC/IEEE 29119 documents

| 29119 document | ChronitonDB document |
|---|---|
| Test policy and organisational test strategy | This page |
| Test plan | The test plan section of a feature's delivery plan |
| Test design specification and test case specification | Each item's coverage file, `ac-coverage.md`, next to its design record: one row per requirement, naming its test |
| Test log | The test reports of the developer's pre-commit test run and of the CI runs, attached to the pull request |
| Test completion report | The milestone report |

For a one-item change, the coverage file and the pull request's verification section stand in for the test plan.

## Exit criteria

An item is done when:

1. Every requirement in its design record has a passing test named in its coverage file.
2. For a fix, the regression test failed before the fix and passes after it.
3. The required checks pass.
4. The parity suite passes with every fork feature off.

A milestone is done when, in addition:

1. Every feature requirement the milestone delivers has a passing validation test.
2. The upgrade and rollback tests its exit criteria name pass.
3. The benchmarks meet their thresholds.
4. No blocker or major finding is open.
5. The milestone report records the results against the exit criteria in the delivery plan.
