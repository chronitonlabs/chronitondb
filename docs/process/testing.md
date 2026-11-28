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

The rules behind this policy are stated in full in [principles.md](principles.md#testing). Each item names its principle.

1. Every requirement has at least one test that proves it. A requirement without a test is not done, unless the item's coverage file records why it is deliberately not tested. That reason is part of the design record and is approved with it. The rule is [PRINCIPLE-063](principles.md#principle-063). How deep the tests go is [Test depth](#test-depth): integration through running nodes is the default for every change that a client, an operator or another node can observe, and a test at a lower level adds to it, never replaces it.
2. A fix starts with a test that reproduces the fault, written by the designer on the item's code branch. It MUST fail before the fix and pass after it. The test and the fix merge together, so the line never carries a failing test. A fix to a fork feature MAY use a scenario as its reproducing test, see [Scenarios](#scenarios). A fix to stock Apache Cassandra code uses a test in one of Apache Cassandra's own test harnesses, never a scenario, so the test can be offered to Apache Cassandra with the fix. For example a JUnit unit test, an in-JVM distributed test or a Python distributed test. The rule is [PRINCIPLE-064](principles.md#principle-064).
3. With every fork feature off, every line MUST behave exactly as stock Apache Cassandra, apart from the fixes to stock code and the differences in what operators see that the [delta register](../delta/README.md) lists. The parity suite proves it once it exists. The rule is [PRINCIPLE-020](principles.md#principle-020).
4. A test that existed before a change MUST NOT be weakened: [PRINCIPLE-065](principles.md#principle-065), which says when an assertion of a merged test of ChronitonDB's own may change. A pre-existing test file of stock Apache Cassandra changes in four ways only, and a fork feature puts its tests in its own files: [PRINCIPLE-013](principles.md#principle-013), which gives the four ways. Stock tests are of two kinds. One that asserts behaviour passes unchanged on any change the project makes, unless the change is an approved fix. One that pins a complete listing, such as the help text of a command, changes with the listing, by the added lines that its design record or fix record names. The `stock-tests` check holds the four ways on every pull request, and it reads the permit on the line, never in the pull request. To the check, a test file of Apache Cassandra is a file in a directory named `test`, or a file named `*Test.java`, `*Tests.java`, `test_*.py` or `*_test.py` anywhere, that is not the project's own by [Where things live](conventions.md#where-things-live). A record permits the work of its own issue only, and only the one change it plans. The issue of a pull request from a branch of this repository is the issue of its work branch, `<name>/<issue>-<slug>/<line>`, and its description names that issue on a line `Fixes #<issue>` or `Part of #<issue>`. The issue of a pull request from a fork is the one issue its description names on such a line. The issue is open. The change passes when the line already holds a merged record of that issue that permits it: the fix record of a fix to stock that lists the file in its Planned file list with the word `test`, a design record or fix record with a line `Pinned listing: <path>` that names the file, or an accepted decision record with a line `Approved stock test change: <path> for #<issue>, because <explanation>`, the explanation written in eight different words of two letters or more, with no placeholder left, such as `TBD` or `todo` in any case of letters. The Pinned listing line and the approval line each stand alone at the start of a line, outside any code block, with the path as it is from the repository root and no backticks. The Planned file list entry is a line of its fenced block. The record merges first, in its own pull request. A permit is used up once a change to the file has reached the line with the record or after it, so the record of an issue whose change is merged permits nothing more. A further change needs its own record, and so does a change planned before an import changed the file: the record is merged again in a new version. A pinned listing gains lines of the listing only. In a file of plain data, one with no extension or a `.txt`, `.json` or `.csv` file, any added line is a line of the listing. In a Java file, such as a test class, each added line is one Java string literal followed by a comma or by a `+`, with nothing else on the line but white space and at most a line comment that holds no backslash. The literal holds no escape but Java's own, `\b`, `\t`, `\n`, `\f`, `\r`, `\"`, `\'`, `\\` and the octal ones, so no quote inside it ends it early and no Unicode escape ends it or the comment. The line above it, blank lines and comments aside and its own line comment cut off, ends in the same mark, and a line with a comma may also stand below a line that opens the listing with `(`, `[` or `{`. So a listing of elements gains whole elements, and a text joined by `+`, such as the expected output of a DESCRIBE, gains whole lines. A line with a `+` never stands right below the line that opens a listing, where it would join the element below it, so a line above the first line of a text joined by `+` takes the fourth way. In any other file, such as a Python test, each added line is one quoted string and a comma, alone on the line, below a line that ends in a comma or opens the listing. So no added line joins a string that is already there. The one line a change may alter is the last line of a text joined by `+` in a Java file, to add lines after it: the old last line, one literal and the marks that close it, such as a bracket that closes a call and the end of the statement, comes back unchanged but for a `+` in place of those marks, and the new last line is one literal that closes with the same marks. Where the last literal holds the end of the text, such as the end of the CQL statement a DESCRIBE prints, that literal changes, so the change adds its line above the last one or takes the fourth way. A listing inside a test method that needs any other line takes the fourth way, and so does a line that disables or skips a test. A security fix lands from its private advisory at disclosure, with its record: [security.md](security.md#private-until-disclosure). An import from Apache Cassandra passes, from a branch `import/cassandra-<...>` or `import/CASSANDRA-<n>` of this repository, and the `import-history` check holds what it brings: [upstream.md](upstream.md#the-import-history-check). A commit of another project is no import from Apache Cassandra, so a stock test file it changes takes one of the other ways. A stock test file is deleted, renamed, replaced by a link or changed as a binary file only by an import.
5. A test's verdict MUST NOT depend on how fast the machine runs. A test that needs time to pass uses a clock the test controls, or waits for a condition with a bound. Timed benchmarks follow their own rules, see [Benchmarks](#benchmarks). Seeds are printed so a run can be repeated. The rule is [PRINCIPLE-066](principles.md#principle-066).
6. A fork feature adds no dependence on topology, so a result of a feature that depends on cluster topology is a fault. A feature that runs across nodes is tested at replication factor 1 and at replication factor 3 on the same data, and across two data centres when its behaviour involves a data centre aware consistency level or replication strategy. The rule is [PRINCIPLE-061](principles.md#principle-061).
7. Scenarios are the executable form of a fork feature's EARS requirements. They are for fork features only. Apache Cassandra's own tests are not rewritten as scenarios, and change only as rule 4 allows. See [Scenarios](#scenarios).
8. A dependency patch-version update has no design record. Every one goes through the security engineer, also one a maintainer asks for that is not a security fix. The security engineer names the test classes that cover every use of the library in ChronitonDB. Those tests MUST pass before the update merges. See [maintenance.md](maintenance.md#dependency-patch-version-updates).

## Test depth

ChronitonDB is a database, so a change is proven where its users meet it: through running nodes. These rules say how deep the tests of a change go. They apply to every pull request that changes code or tests, on every path: the short path, the full path and the lighter paths of Low risk work, dependency patch-version updates and imports. A pull request that changes only documents, such as a feature spec, a design record, a release proposal, a VEX statement or process or user documentation, goes straight to its review and never reaches the tester. The developer writes the code and its own tests. The [tester](roles.md#tester) then makes the tests sufficient by these rules and runs them, and the reviewer checks the change against them rule by rule. The rules rest on [PRINCIPLE-063](principles.md#principle-063) and [PRINCIPLE-067](principles.md#principle-067).

The record of these rules is section 4 of the short record on the short path. On every other path it is the pull request's description, in the part that says which tests prove which claim: [branching-and-review.md](branching-and-review.md#pull-requests). On the full path the design record is approved before the code, so the record of a code pull request is its description too.

1. **Integration by default.** Every change that a client, an operator or another node can observe MUST be proven through running nodes with Apache Cassandra's own harnesses, in addition to any unit tests. Through running nodes means at least an in-JVM distributed cluster of two or more nodes, reached the way a real user reaches the change: the native protocol through the Java driver for CQL, nodetool or JMX through the instance for an operator command, and real messages between nodes for cluster behaviour.
2. **Real components.** A test MAY replace a component with a stand in, such as a fake bean, a mock or an injected supplier, only in addition to a test that uses the real component. A failure that the real component cannot be made to produce MAY be injected, with ByteBuddy or the instance initialiser of the in-JVM harness, and the record names each injected failure.
3. **Surface matrix.** What a change touches decides the tests it owes, each through running nodes. The record states which rows apply and why each other row does not.
   1. CQL or the native protocol: statements through the driver on a cluster of several nodes, paging, prepared statements, every error a client can see, and the driver's schema metadata where the schema changes.
   2. Schema, system keyspaces or the lists of virtual tables: `DESCRIBE`, schema agreement across nodes, and the stock listings that pin them.
   3. Data on disk, sstable or commit log formats: both sstable formats, as [PRINCIPLE-067](principles.md#principle-067) asks, a restart and a commit log replay, and Harry reconciliation where rows are written or read.
   4. Between nodes, such as messages, gossip and cluster metadata: mixed versions, a node down and back, replication factor 1 and 3, and two data centres where consistency or replication is data centre aware, as [PRINCIPLE-061](principles.md#principle-061) asks.
   5. Security, such as authentication, authorisation, roles and permissions: a cluster with `PasswordAuthenticator` and `CassandraAuthorizer` on, and every grant and refusal the change states.
   6. Settings, startup and nodetool: the yaml at startup, the runtime toggle through nodetool or JMX, a restart that keeps the startup value, and a bad value refused.
   7. Tools, real node processes and packaging, such as cqlsh, the output of nodetool, the sstable tools and an installed package: the tool or the process run against running nodes, as a Python distributed test where the in-JVM harness cannot reach it. A Python distributed test is REQUIRED for cqlsh, the tools, real node processes and packaging. These tests use Apache Cassandra's own cassandra-dtest and ccm unchanged, each pinned to an exact commit, with their Python requirements pinned to exact versions.
   8. Concurrency or shared state: concurrent clients in the test, and the simulator or a repeated run where ordering matters.
4. **Impact analysis.** The record lists every area of [areas.md](areas.md) and every shared surface the changed code reaches: the callers of each changed stock method, each stock listing or registry the change adds to, and each path the change runs on. For each one it names the existing tests that prove it unaffected, run and passing on the change, or a new test. Nothing the change reaches is left unstated.
5. **Edge cases.** The record lists the edge cases of each requirement and of each area reached: empty, one, many and the limit, missing or undefined values, repeated names or keys, concurrent use, a failure of each dependency, a node down, a restart and a large input. Each has a test, or a stated reason it cannot occur.
6. **Upgrade and rollback.** A new feature, and every change to a surface of rule 3 other than a log line or documentation, has an in-JVM upgrade test of the line's supported path: from the latest Apache Cassandra release of the same major version to the change and back, with a mixed version step that reads and writes on both versions, as [Upgrade and rollback tests](#upgrade-and-rollback-tests) says. Where the change has no format, schema or protocol part, the test still proves that a mixed cluster serves reads and writes and that the rollback reads every row back. The rule is [PRINCIPLE-062](principles.md#principle-062).
7. **Repeats.** Before the hand off to review, every new or changed test class runs repeatedly: 50 times for a unit test class, 10 times for an in-JVM distributed test class, and 3 times for an upgrade test or a Python distributed test. Each run prints its seeds, as [PRINCIPLE-066](principles.md#principle-066) asks. A failure in any run blocks the hand off until it is explained. Continuous integration runs each test once and repeats none. On an import from Apache Cassandra, Apache Cassandra's test classes run once, as part of the full test suites every import runs before the merge, see [When each test runs](#when-each-test-runs). The repeats apply only to the tests the project adds or changes for the import. The tester still writes the impact analysis of what the import touches in the project's own code, and adds tests where that code is affected.
8. **Coverage.** Item 5 of the [Exit criteria](#exit-criteria) applies on every path: line and branch coverage of each changed method and the CRAP score of each changed ChronitonDB method, from the build's JaCoCo targets, attached to the pull request.
9. **Exceptions.** A change MAY skip a rule, or a row of rule 3, only with a reason in the record that names what makes it impossible or empty, such as a change of log text only, of documentation or of a comment. "Low risk" and "small change" are never reasons. The reviewer accepts or refuses each exception.

Where another page or template names the kind of test a claim needs, such as [PRINCIPLE-067](principles.md#principle-067), the test lists of a design record or the test plan of a feature spec, that is a minimum on top of these rules, never in their place.

## Test levels

Which levels a change needs is [Test depth](#test-depth). A level lower in this table adds to the tests through running nodes, never replaces them.

| Level | What it proves | Where |
|---|---|---|
| Unit tests | One class or component behaves as its requirements say, in addition to the tests through running nodes that [Test depth](#test-depth) asks for | `test/unit/` |
| In-JVM distributed tests | Behaviour across several nodes in one JVM: replication, consistency, upgrade paths in process. The default level for every change that a client, an operator or another node can observe | `test/distributed/`, in the directories [conventions.md](conventions.md#where-things-live) names |
| Scenarios | A fork feature's requirements hold as written, with its switch, where it has one, off and on | `test/bdd/` |
| Python distributed tests | Behaviour of real node processes and tools, where in-JVM tests cannot reach. REQUIRED for cqlsh, the tools, real node processes and packaging | Apache Cassandra's cassandra-dtest suite and ccm, each pinned to an exact commit, with pinned Python requirements |
| Upgrade and rollback tests | A node moves from Apache Cassandra to ChronitonDB and back, and from one ChronitonDB release to the next, with data and queries intact during and after the roll | Upgrade tests for the supported paths |
| Benchmarks | Performance claims in a design record hold, and what a feature costs the operations that do not use it is measured against stock | `test/microbench/` and the load tests the design names |
| Golden corpora | Output that must stay identical across library versions and lines, compared with a fixed expected result | Where a feature needs them |
| Parity suite | Stock behaviour is unchanged with every fork feature off | `test/parity/` and the normal build |

The scenario module `test/bdd/` with its shared step library, and the parity suite `test/parity/`, are not built yet. Each needs a hook in `build.xml` with its delta entry. The test framework they use is a dependency, declared and approved before use: [PRINCIPLE-049](principles.md#principle-049). Until the parity suite exists, the required property of rule 3 of the [Policy](#policy) is checked by the stock suites run with every fork feature off.

A change runs its tests in every test configuration whose settings the changed code reads. Apache Cassandra's build has six unit test configurations, `test`, `test-latest`, `test-oa`, `test-compression`, `test-cdc` and `test-system-keyspace-directory`, and two for in-JVM distributed tests. The project's own tests run on the options of the entry condition of [PRINCIPLE-003](principles.md#principle-003), which `test-latest` and the latest configuration of the in-JVM distributed tests set. A test that needs another setting, such as compression or change data capture, sets it on top of those options. For example a change that touches compaction or an on-disk format runs on both sstable formats, since a cluster that met the entry condition can still hold sstables in the older format. The rule is [PRINCIPLE-067](principles.md#principle-067).

## Scenarios

Scenarios are written in Gherkin, in the fork's own test module `test/bdd/`, and run by the test framework that module declares. Each one is the executable form of one or more EARS requirements of a fork feature.

1. Every scenario uses the shared library of CQL and cluster steps. A feature that needs a new step adds it to the library with tests of its own. There is no glue code per feature.
2. Every scenario carries a tag with the id of each requirement it proves, the id itself with `@` in front, for example `@REQ-VER-012` or `@REQ-CLD-004`. These tags map requirements to their scenarios.
3. Every scenario of a feature that has a switch carries exactly one of `@switch-off` and `@switch-on`, for the state of the feature switch it runs with. Where a feature has more than one switch, the tag gives the state of the switch the scenario's requirement is about, and the scenario's steps set the others.
4. `@switch-off` scenarios prove the parts of the switch off rule that apply, [PRINCIPLE-019](principles.md#principle-019): stock operations behave exactly as Apache Cassandra, each way a user or an operator can invoke the feature is refused with an error that names the switch, and a feature with no such way in does nothing while off. See [branching-and-review.md](branching-and-review.md#feature-switches-and-defaults).
5. `@stock` marks a scenario that asserts Apache Cassandra's own behaviour. A `@stock` scenario MUST pass before the change and after it. Every other new or changed scenario MUST fail before the change and pass after it.
6. The designer writes the scenarios of a feature item in the design record's pull request, tagged `@wip`, so they are approved with the requirements before the code starts.
7. `@wip` scenarios merge onto the line but are left out of normal runs, so the line stays green. A separate run fails if a `@wip` scenario passes.
8. The developer removes `@wip` in the code pull request as each scenario passes. The developer MUST NOT change what a scenario means. That is a change to an approved requirement and goes through [change control](additive.md#change-control-after-a-merge).
9. Before a feature's final milestone gate, its switch refuses to turn on. `@switch-on` scenarios get past the refusal only through a mechanism inside the in-JVM distributed test framework. Shipped code has no way around the refusal.
10. Repeated runs of scenarios, to find flaky ones, run in the project's scheduled CI once it exists. Until then each scenario runs once per change, in the developer's pre-commit test run, and the shared step library's own tests are run repeatedly whenever the library changes.
11. A fix to a fork feature MAY use scenarios as its reproducing test. The designer writes a new scenario, or updates one of the feature's existing scenarios, on the item's code branch.
    1. The fix record lists, in its Requirements section, every feature requirement `REQ-<KEY>-nnn` the fault breaks. One fault MAY break several.
    2. Each reproducing scenario carries the tag of at least one listed requirement and the tag `@fix-<issue>`, with the GitHub issue number of the fix, for example `@fix-142`. It carries no `@wip` and is never a `@stock` scenario.
    3. The fix record selects them with the requirement tags and the fix tag joined with `and`: `@REQ-CLD-004 and @fix-142`, or for several requirements `(@REQ-CLD-004 or @REQ-CLD-005) and @fix-142`, naming exactly the requirements it lists. Only the scenarios that carry both tags run, before the fix, where each MUST fail, and after it, where each MUST pass. The requirement tags alone are not enough, because the feature's other scenarios of those requirements already pass before the fix. A `@fix-<issue>` scenario that carries none of the listed requirement tags is refused, since the selection would never run it.
    4. After the fix, every scenario of the feature's key also runs, `@wip` left out, and each MUST pass.
    5. An update of an approved scenario adds only the two tags and new Examples rows, or a new Examples block. Any other change to an approved scenario changes an approved requirement and goes through [change control](additive.md#change-control-after-a-merge).
    6. A fix to stock Apache Cassandra code keeps its reproducing test in one of Apache Cassandra's own test harnesses, as rule 2 of the [Policy](#policy) says.

## Upgrade and rollback tests

1. ChronitonDB writes its own upgrade tests for its supported paths: from the latest Apache Cassandra release of the same major version, set up as the entry condition of [PRINCIPLE-003](principles.md#principle-003) says, to ChronitonDB and back, and from one ChronitonDB release to the next.
2. A milestone that introduces an on-disk format change has upgrade and rollback tests among its exit criteria.
3. Apache's own upgrade tests for paths ChronitonDB does not support, such as a path from an older major version, are not run on the lines.
4. An upgrade test of the project names both versions explicitly. The older version is built under a jar name that tells an Apache Cassandra release from a release of the line. Apache Cassandra's runner names a jar by the Apache version alone, which a release of the line shares. An Apache Cassandra release is built as `dtest-apache-<version>.jar`, for example `dtest-apache-5.0.10.jar`. The form of the jar name of a release of the line is set by the design record of the first upgrade test between two releases of the line.
5. The line's upgrade tests run on Java 17, the Java version of the 5.0 line, for every path whose versions all support Java 17, as every Apache Cassandra 5.0 release does. A path with a version that does not support Java 17 runs on a Java version that every version on the path supports. Apache Cassandra's upgrade test runner refuses Java 17 for upgrade tests today. The change to that stock file that lets it run them carries its delta entry.
6. What these tests read back follows [PRINCIPLE-084](principles.md#principle-084) and [PRINCIPLE-085](principles.md#principle-085): a stored form records the version that wrote it, and a reader has a stated answer for a value it does not recognise.

## Benchmarks

1. Pull request checks block only on counted values, such as allocations per operation, work counters, bytes written per compaction and bytes written per byte of input, and on benchmarks that fail to run. They never block on timing. The rule is [PRINCIPLE-053](principles.md#principle-053).
2. Once dedicated benchmark hardware is in place, timing results are tracked over time, and a change point in the timings blocks the next release.
3. Absolute timing numbers come only from pinned or dedicated hardware.
4. Each design record names its benchmarks and the runs it is compared against: the code before the change and the stock build, with the feature off and on, as [PRINCIPLE-050](principles.md#principle-050) says, or gives the reason the checklist line does not apply, as [quality-requirements.md](quality-requirements.md) allows. No numeric target is asked for up front: the design argues its speed by its mechanism, and the benchmarks prove it by comparison. A measured slowdown of operations that do not use the feature is reported to the maintainers with its numbers, and they decide: [PRINCIPLE-052](principles.md#principle-052). See [templates/design-record.md](templates/design-record.md).

## When each test runs

| When | What runs |
|---|---|
| Before each commit | The developer's pre-commit test run: the build, the code checks, the tests the item adds and the existing tests that cover the changed code. Its results are the test log for that commit |
| Before the hand off to review | The tester's run: every test of the test plan, the existing tests its impact analysis names, and the repeats of rule 7 of [Test depth](#test-depth), with coverage. Its results are attached to the pull request |
| On every pull request to a line, including pull requests from forks | The required checks in [branching-and-review.md](branching-and-review.md#required-checks) and the tests of the changed areas, on GitHub's own runners. Each test runs once, with no repeats |
| Regularly, per line | The full Apache Cassandra test suites, with fork features off and with them on |
| At each milestone | The validation items, the upgrade and rollback tests the exit criteria name, the benchmarks, and the parity suite, on continuous integration, or until it exists on the build machines, with every test that cannot run there listed as a deviation in the milestone report. See [additive.md](additive.md#milestone-gates) |
| At each import from Apache Cassandra | The full test suites, with each test class of Apache Cassandra run once, the parity suite once it exists and the tests named in the import record, before the merge. The tests the project adds or changes for the import also take the repeats of rule 7 of [Test depth](#test-depth) |
| At each release candidate | The full test suites, signatures, installs, upgrade and rollback from the previous ChronitonDB release and from Apache Cassandra, and the parity suite once it exists, before promotion. See [release.md](release.md) |

## Full test suites

1. The full Apache Cassandra test suites run regularly on each line, with every fork feature off and with them on. They also run on every import and every release candidate.
2. They run on dedicated CI infrastructure once it exists, only for branches in this repository. Every pull request, including one from a fork, runs the GitHub checks and the tests of the changed areas on GitHub's own runners.
3. Results are compared with Apache Cassandra's own results for the same tests.
4. The release engineer checks the latest results daily, as a scheduled check once it exists, and opens a corrective item for each real failure.

## The ISO/IEC/IEEE 29119 documents

| 29119 document | ChronitonDB document |
|---|---|
| Test policy and organisational test strategy | This page |
| Test plan | The test plan section of a feature's delivery plan |
| Test design specification and test case specification | Each item's scenarios, through their requirement tags, and its coverage file `ac-coverage.md` next to its design record, written from [the coverage file template](templates/ac-coverage.md). The coverage file has a row only for a requirement proven by another test, naming that test, or deliberately not tested, with the reason. The full requirement to test table is built from both into the item's evidence |
| Test log | The test reports of the developer's pre-commit test run, of the tester's run and of the CI runs, attached to the pull request |
| Test completion report | The milestone report |

For a one-item change, the coverage file and the pull request's verification section stand in for the test plan.

## Exit criteria

An item is done when:

1. Every requirement in its design record has a passing scenario that carries its id, a passing test named in its coverage file, or a reason in its coverage file why it is deliberately not tested. A requirement with none of these fails.
2. For a fix, the regression test failed before the fix and passes after it.
3. The required checks pass.
4. The parity suite passes with every fork feature off. Until it exists, the stock suites the design record names pass with every fork feature off.
5. The evidence carries line and branch coverage for every changed method, and a CRAP score for each changed ChronitonDB method: its complexity weighed against how much of it the tests cover. A score above 30 is a finding the reviewer addresses. Changed stock methods get coverage only.

A milestone is done when, in addition:

1. Every feature requirement the milestone delivers has a passing validation test.
2. The upgrade and rollback tests its exit criteria name pass.
3. The benchmarks the delivery plan names have run, and their results are in the milestone report, against the code before the change and against stock. A measured slowdown of operations that do not use the feature is in the milestone report with its numbers, and the maintainers decide it: [PRINCIPLE-052](principles.md#principle-052).
4. No blocker or major finding is open.
5. The milestone report records the results against the exit criteria in the delivery plan.
