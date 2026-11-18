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

# Principles

This page states the architectural and design rules the project holds to. Each rule is stated once, here, with an id. A feature spec, a design record, a fix record, a decision record or a review cites a rule by that id. The other pages in this folder give the procedures and point here for the rule. The numbers are not reused, and a gap in the numbers is a number that was never published. In this page "the project" is ChronitonDB.

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in BCP 14 (RFC 2119, RFC 8174) when, and only when, they appear in all capitals, as shown here.

## How to read and cite a principle

1. The id of a principle is `PRINCIPLE-nnn`, with three digits, for example `PRINCIPLE-001`. The principles are numbered across the whole page, in the order they were first written. The heading a principle stands under is not part of its id.
2. An id is never reused and never renumbered. A gap in the numbers is a number that was never published. A principle that is withdrawn after it was published keeps its entry, which then says that it is withdrawn and names the decision record that withdrew it. A principle that moves to another heading keeps its id.
3. The id cannot be mistaken for another id of the project. A requirement id and a decision record id carry a feature key of 3 to 5 capital letters, an issue number or the key `GOV`. See [additive.md](additive.md#feature-keys-and-requirement-ids).
4. A principle says what must be true. Words after "for example" or "such as" give one way to meet it, never the only way.
5. Each principle says where it applies and gives its edge: what the exception is and who decides it. An exception that a principle does not name is a decision of the maintainers, recorded in the design record or fix record of the work that needs it, which names the principle and gives the reason. Such a record is marked: the `Exceptions` row of its document control table names the principle, and the [generated index](../index/documents.md) lists every marked record under the principle it departs from.
6. Each principle links the decision record that set it, where one exists, and the page that gives the procedure.
7. A document cites a principle by its id, as a link to its entry, for example `[PRINCIPLE-016](../process/principles.md#principle-016)` with the path from the citing document. A document cites nothing that a reader of the repository cannot open. See [PRINCIPLE-080](#principle-080).
8. The maintainers approve a new principle, or a change to one, by merging the change to this page, with the decision record behind it where a question was answered.

## Compatibility with Apache Cassandra

### PRINCIPLE-001

**An application behaves as it did on Apache Cassandra, and a user can move back.** An application that moves onto the project's database MUST behave as it did on Apache Cassandra, and a user MUST be able to move back to Apache Cassandra. A change to what an application sees from a stock feature is a feature, and it MUST sit behind a feature switch that is off by default. What an application sees is its results, its errors, its warnings and the bytes on the wire.

1. **Applies to.** Every change on a line. For example a read that would return other rows for a stock statement, a new warning on a stock statement, or a changed frame of the native protocol.
2. **Edge.** A fix to a defect in stock is not a feature and is not gated, see [PRINCIPLE-004](#principle-004). Any other exception is granted by the maintainers one at a time, each in a decision record with its reason.
3. **See.** [DEC-GOV-0001](../decisions/DEC-GOV-0001-what-stays-as-apache-cassandra-has-it.md). [quality-requirements.md](quality-requirements.md#compatibility-with-apache-cassandra), [branching-and-review.md](branching-and-review.md#feature-switches-and-defaults).

### PRINCIPLE-002

**What operators see stays as stock where that is reasonable.** What an operator sees is metrics, nodetool output, logs and JMX. It SHOULD stay as stock where that is reasonable. A difference there MUST be recorded in the delta register and in the release notes. It is recorded, not refused, and it does not by itself make a feature behaviour-changing.

1. **Applies to.** Every change to a surface an operator reads. For example the release version that `nodetool version` prints, or a new column in the output of a stock command.
2. **Edge.** Whether staying as stock is reasonable is judged case by case, by the maintainers when they merge the design. Log lines have their own rule, see [PRINCIPLE-008](#principle-008).
3. **See.** [DEC-GOV-0001](../decisions/DEC-GOV-0001-what-stays-as-apache-cassandra-has-it.md), record [0002](../decisions/0002-nodetool-version-output-on-a-chronitondb-node.md). [The delta register](../delta/README.md), [release.md](release.md#what-nodetool-version-shows).

### PRINCIPLE-003

**Moving between Apache Cassandra and the project is done on the same data files, by a runbook.** A user moves a cluster from Apache Cassandra onto a line, and back, on the same data files, by following a runbook that states its prerequisites. With every fork feature off, the state a node shares with others is as stock has it: schema tables, data files and their components, gossip and messages. Everything the project writes to that shared state can be removed by a step the runbook names. Moving MUST be possible. It is not promised to need no steps.

1. **Applies to.** Every change that writes to disk, to the schema or between nodes, and every line's upgrade runbook. For example a new sstable component, a new schema option, or a setting of the line's minimum setup, which a node checks at every start.
2. **Edge.** The fixes and the differences the delta register lists. The supported paths are from Apache Cassandra of the same major version, and from one release of a line to the next.
3. **See.** [release.md](release.md#the-configuration-file), [release.md](release.md#switching-a-node-from-apaches-package), [testing.md](testing.md#upgrade-and-rollback-tests), [templates/feature-spec.md](templates/feature-spec.md#7-compatibility).

### PRINCIPLE-004

**A fix to a defect in stock is applied, and only the maintainers say what is a fix.** A fix to a defect in stock is not a feature and MUST NOT be gated behind a switch. It is applied, with its fix record, its delta entry and a release note. A change to stock code counts as a fix only when the maintainers approve it as one, by merging its fix record after the reviewer's finding on the evidence. A change to stock behaviour that is not approved as a fix is a behaviour change under [PRINCIPLE-001](#principle-001).

1. **Applies to.** Every change to Apache Cassandra's own code or behaviour. The evidence is a test that reproduces the fault and fails before the change, and either an Apache Cassandra ticket that treats the behaviour as a bug or the documented behaviour the fault breaks.
2. **Edge.** None. A fix record that is not merged is not a fix, and code for it MUST NOT merge before it. The reviews of a security fix stay in its private advisory until disclosure.
3. **See.** [DEC-GOV-0001](../decisions/DEC-GOV-0001-what-stays-as-apache-cassandra-has-it.md). [maintenance.md](maintenance.md#corrective-fixing-a-fault).

### PRINCIPLE-005

**New behaviour is reached through something stock does not have.** A statement that Apache Cassandra rejects only because it uses something Apache Cassandra does not have MAY succeed as a purely additive feature. A statement that Apache Cassandra accepts as valid and refuses for a reason is stock behaviour. Making it succeed is a change to what an application sees, under [PRINCIPLE-001](#principle-001).

1. **Applies to.** Every statement, option and command a feature accepts. For example new syntax, a new keyword, a new option or a new index type is something stock does not have. A missing `ALLOW FILTERING`, a guardrail or a missing index is a reason stock refuses.
2. **Edge.** None.
3. **See.** [DEC-GOV-0001](../decisions/DEC-GOV-0001-what-stays-as-apache-cassandra-has-it.md). [branching-and-review.md](branching-and-review.md#feature-switches-and-defaults).

### PRINCIPLE-006

**The compatibility numbers Apache Cassandra owns are not changed.** The project never changes a compatibility number that Apache Cassandra owns: the messaging version, the sstable and index format version letters, the cluster metadata serialization version, and the ids of CQL operators on the wire. A feature that needs new state between nodes or on disk carries it in a form Apache Cassandra already accepts. Where no such form exists the design stops and asks the maintainers.

1. **Applies to.** Every feature with state on disk or between nodes. For example a new field between nodes travels in an existing extensible field, new data beside an sstable is an optional component, and what an index keeps in cluster metadata is text options.
2. **Edge.** A decision of the maintainers, in a decision record. A changed number that arrives unchanged in an import from Apache Cassandra is Apache Cassandra's own.
3. **See.** [quality-requirements.md](quality-requirements.md#compatibility-with-apache-cassandra).

### PRINCIPLE-007

**Code defaults in stock classes stay as Apache Cassandra has them.** A default of a stock field, such as one in `Config.java`, stays exactly as Apache Cassandra has it. So a cluster that keeps its own configuration file behaves as it did.

1. **Applies to.** Every edit to a stock class. A field the project adds has no stock default: where it is a feature switch its default follows [PRINCIPLE-017](#principle-017).
2. **Edge.** None stated.
3. **See.** [conventions.md](conventions.md#code-layout), [upstream.md](upstream.md#configuration-changes).

### PRINCIPLE-008

**A log line is not a compatibility concern, and stock log lines change in two ways only.** A log line that differs from stock is not a compatibility concern and is never a finding by itself. A log line that fork code adds gets no delta entry. A log line that Apache Cassandra writes changes in two ways only: in an approved fix to a defect in stock, as part of the fix, with its delta entry and no switch, or by a feature whose purpose is to change what Apache Cassandra logs, behind a switch that is off by default. It never changes as a side effect of other work. Of the two, only the fix records the changed line in a delta entry. Such a feature names the lines it changes in its own design record.

1. **Applies to.** Every log line on a line. For example a startup line that names the fork's switches is an added line. A feature that removes sensitive data from stock log lines is the second way.
2. **Edge.** None. What a fork log line may carry is [PRINCIPLE-035](#principle-035).
3. **See.** [classification.md](classification.md#the-floor), [the delta register](../delta/README.md#keeping-it-current).

## Changes to Apache Cassandra code and tests

### PRINCIPLE-009

**Apache Cassandra's files change only where needed.** Apache Cassandra's own files stay as Apache Cassandra has them wherever the project can put its own file beside them. A change to one is made only where it is needed, and it is the smallest that does the job.

1. **Applies to.** Every file that came from Apache Cassandra, edited or not. For example the project keeps its own change log, configuration file, packaging and workflows beside Apache Cassandra's.
2. **Edge.** A change the work needs, with its delta entry. An import from Apache Cassandra changes these files as Apache Cassandra changed them.
3. **See.** [upstream.md](upstream.md#apache-files-change-only-where-needed), [conventions.md](conventions.md#stock-files).

### PRINCIPLE-010

**Fork logic lives in the project's own packages and shares stock logic, never copies it.** Fork logic lives in classes under `org.chronitondb`, and MUST NOT be added as a new class under `org.apache.cassandra`. An edit to a stock source file is a hook that calls fork code, a fix to a defect in stock, or a refactor that lets fork code share stock logic in place of a copy.

1. **Applies to.** All Java code the project writes. For example a new index type is a package of its own with a hook in the stock class that calls it, and a check that fork code needs from a stock class is shared by a refactor, not copied.
2. **Edge.** A fork class that needs package private access to a stock package, and a refactor of stock code, are named in the design record and approved with it. Each stock file that imports fork code is a hook point, listed in the feature spec with its delta entry.
3. **See.** [conventions.md](conventions.md#code-layout), [branching-and-review.md](branching-and-review.md#two-review-standards-picked-by-file).

### PRINCIPLE-011

**Every change carried on top of Apache Cassandra is in the delta register.** Every change the project carries on top of Apache Cassandra has an entry in the delta register: what it is, why it is carried, where it came from and whether it went to Apache Cassandra. Every pull request that changes stock code or stock behaviour adds or updates its entry.

1. **Applies to.** Features, fixes to stock code, and build and packaging changes.
2. **Edge.** The import of a whole Apache Cassandra release or branch needs no entry. A log line that fork code adds needs none, see [PRINCIPLE-008](#principle-008).
3. **See.** [The delta register](../delta/README.md), [upstream.md](upstream.md#the-delta-register).

### PRINCIPLE-012

**Every fix to stock code is offered to Apache Cassandra.** Every fix to stock code is offered to Apache Cassandra, and its delta entry records the offer. A feature is offered only when the maintainers decide, case by case.

1. **Applies to.** Every approved fix to stock, see [PRINCIPLE-004](#principle-004).
2. **Edge.** A security fix is offered through the Apache Cassandra security team until disclosure.
3. **See.** [upstream.md](upstream.md#offering-changes-upstream).

### PRINCIPLE-013

**A stock test file is not edited in feature work.** A pre-existing test file of Apache Cassandra changes only in a fix to stock that the maintainers approved, or unchanged in an import from Apache Cassandra. A fork feature puts its tests in its own files. A stock test MUST pass unchanged on any change the project makes: a behaviour change is behind a switch and the stock suites run with it off, so a stock test that breaks shows the change is wrong, unless the change is an approved fix.

1. **Applies to.** Every test file that came from Apache Cassandra. A fix record that plans one names each existing test method it changes and says what each asserts after the fix. New test methods need no entry. The maintainers approve that list when they merge the fix record. The reviewer checks that the code branch changed those methods and no other existing ones: a changed existing test method the fix record does not name is a blocker.
2. **Edge.** Where a stock test must be extended for another reason, such as a list a stock test keeps of every setting, the maintainers approve the change case by case: an accepted decision record names the file and the issue allowed to change it, with a written explanation of why the change to the test is needed. An approval with no explanation does not count. What may change inside the file is what the record says in words: the reviewer holds the change against them, and the maintainers at the merge.
3. **See.** [testing.md](testing.md#policy), [conventions.md](conventions.md#code-layout).

### PRINCIPLE-014

**Feature work does not fix stock code on the way.** A defect in stock that a fork feature directly needs fixed is fixed as an item of its own, through the corrective path. Every other gap in stock that the feature work meets is recorded as a candidate issue and left for its own item.

1. **Applies to.** Feature work that meets a fault or a gap in Apache Cassandra's code. For example a streaming feature that hits a stock fault in the listing of components waits for the corrective item that fixes it.
2. **Edge.** None. A defect that the maintainers or a user found takes the corrective path whatever feature is in hand.
3. **See.** [maintenance.md](maintenance.md#corrective-fixing-a-fault), [templates/design-record.md](templates/design-record.md#15-not-covered-and-follow-ups).

### PRINCIPLE-015

**A fork feature may differ from the stock feature beside it, inside its own code.** How a fork feature works MAY differ from the stock feature beside it where that is more sensible, as long as the difference stays inside fork code. A change to stock code, or to what the stock feature does, is not under this principle: it follows [PRINCIPLE-001](#principle-001) or [PRINCIPLE-004](#principle-004).

1. **Applies to.** Fork features that stand beside a stock feature of the same kind. For example a fork index may rebuild and size its thread pools differently from a stock index, and a fork compaction strategy may pick its tasks differently from the stock strategies.
2. **Edge.** None.
3. **See.** [templates/design-record.md](templates/design-record.md#5-idiom-and-consistency).

## Feature switches and defaults

### PRINCIPLE-016

**A feature has a switch when something needs it to be turned off.** A behaviour-changing feature always has a feature switch. A purely additive feature has a switch only when something needs it to be turned off: a requirement, a decision of the maintainers, a rule of these pages, or a named risk such as load on a shared path. Otherwise its design says in one line why it needs none. How a switch is set is the design's choice.

1. **Applies to.** Every fork feature. For example a switch is a node setting with a runtime command, or an option on the schema object that owns the data.
2. **Edge.** Work with nothing to turn off, such as documentation, packaging or a build change, has no switch.
3. **See.** [branching-and-review.md](branching-and-review.md#feature-switches-and-defaults).

### PRINCIPLE-017

**A purely additive feature is on by default, a behaviour-changing feature is off.** A purely additive feature is reachable only through something stock Apache Cassandra does not have. It is on by default: its switch, where it has one, ships on, and an operator turns off what they do not want. A behaviour-changing feature changes what an application sees from something stock Apache Cassandra already does: results, errors, warnings, the bytes on the wire or the performance of existing operations. Its default MUST be off on every line.

1. **Applies to.** Every fork feature and each of its switches. The feature spec states the class of each, with the reason, and a maintainer approves the class with the spec.
2. **Edge.** A purely additive feature that is finished after its line's first release has the edge of [PRINCIPLE-018](#principle-018).
3. **See.** [DEC-GOV-0001](../decisions/DEC-GOV-0001-what-stays-as-apache-cassandra-has-it.md). [branching-and-review.md](branching-and-review.md#feature-switches-and-defaults), [release.md](release.md#what-a-release-may-contain).

### PRINCIPLE-018

**A default does not change within a line.** A feature's default does not change within a line. Upgrading within a line never changes behaviour by itself. Within a line, the values the shipped configuration file holds change only for a fix.

1. **Applies to.** Every release of a line.
2. **Edge.** A purely additive feature is on by default on every line, also when it is finished after a line's first release. Such a feature ships off by default on that line when it does work without being asked, such as a background task, a cache it fills or a pool it starts, or when it adds anything nodes share, such as a schema object, a message between nodes or a file that is streamed. Its design says which it is. It is on by default from the next new line.
3. **See.** [branching-and-review.md](branching-and-review.md#feature-switches-and-defaults), [release.md](release.md#what-a-release-may-contain), [upstream.md](upstream.md#configuration-changes).

### PRINCIPLE-019

**With a feature off, nothing of it shows.** With a feature off, the feature MUST change nothing that stock Apache Cassandra does. Three things hold, as they apply, and the tests of the feature's off state prove them. Stock behaviour is unchanged, always. Each way a user or an operator can invoke the feature is refused with an error that names the switch. A feature with no such way in does nothing while off: its background work does not run, and no file, metric or other state of the feature appears.

1. **Applies to.** Every feature that has a switch. For example a new statement is refused with an error that names the switch, and a scheduled background task with its switch off starts no thread, registers no metric and writes no file. While off, a feature writes no new files, starts no new threads and uses no new memory.
2. **Edge.** None.
3. **See.** [branching-and-review.md](branching-and-review.md#feature-switches-and-defaults), [testing.md](testing.md#scenarios).

### PRINCIPLE-020

**Every merged item keeps the line releasable.** Every merged item keeps its line releasable. Before a feature's final milestone gate its switch refuses to turn on, whatever its default, and shipped code has no way round the refusal. With every fork feature off, a line behaves as stock, and the parity suite proves it.

1. **Applies to.** Every line, and every feature that is built over several items.
2. **Edge.** The fixes to stock code and the differences in what operators see that the delta register lists.
3. **See.** [branching-and-review.md](branching-and-review.md#feature-switches-and-defaults), [additive.md](additive.md#milestone-gates), [testing.md](testing.md#policy).

## Settings and operator controls

### PRINCIPLE-021

**A setting that depends on the data belongs to the schema object that owns the data.** Behaviour that depends on the data is set on the schema object that owns the data, not by one global setting. A configured default applies when the object is created, altering the object changes the value, and a configured maximum bounds it.

1. **Applies to.** Every limit or behaviour whose right value depends on the data. For example a size limit of an index is an index option, and a limit of a table level feature is a table option.
2. **Edge.** A design that keeps such a setting global only states the reason, and the maintainers approve it with the design.
3. **See.** [quality-requirements.md](quality-requirements.md#data-dependent-settings-belong-to-the-schema-object).

### PRINCIPLE-022

**A lever over several schema objects has three modes.** A lever that can apply to several schema objects has three mutually exclusive modes. Global: it applies to all of them. Include: it applies only to the listed ones. Exclude: it applies to all but the listed ones. There are no layered overrides by keyspace, table and index.

1. **Applies to.** A lever that cannot live on the schema object itself, see [PRINCIPLE-021](#principle-021). For example a rate limit on a background task that applies to all tables, only to the listed tables, or to all but the listed tables.
2. **Edge.** None.
3. **See.** [quality-requirements.md](quality-requirements.md#data-dependent-settings-belong-to-the-schema-object).

### PRINCIPLE-023

**A runtime command changes the running value only.** A runtime command, such as a nodetool toggle, changes the value in memory only, on the node where it runs. The configuration file holds the value at startup. There is no separate persistence of runtime changes, and a restart returns to the configured value.

1. **Applies to.** Every operator control that can change on a running node.
2. **Edge.** An option on a schema object is not a runtime toggle: it changes through the schema.
3. **See.** [quality-requirements.md](quality-requirements.md#a-runtime-command-changes-the-running-value-only).

### PRINCIPLE-024

**Only an operator control may differ from node to node.** A value may differ from node to node only for an operator control: a kill switch, a limit, a fallback switch or another lever set by configuration or by a runtime command. The design says what a client sees while nodes differ. For a control that refuses work that is a refusal with an error that names the control, never a wrong or partial result. Anything that defines what a statement means or which rows it returns is never per node: it lives in the schema.

1. **Applies to.** Every setting a feature adds. For example a limit an operator lowers on one loaded node refuses work there, and the way an index analyses text is an option of the index, the same on every node.
2. **Edge.** None.
3. **See.** [quality-requirements.md](quality-requirements.md#a-runtime-command-changes-the-running-value-only).

### PRINCIPLE-025

**A refusal names its control.** A refusal names what the user or operator can change to lift it, where there is such a thing. A refusal with nothing to change says why the operation is refused.

1. **Applies to.** Every refusal the project adds. For example a statement refused because a feature is off names the feature switch, a statement refused because a limit is reached names the setting that holds the limit, and a statement refused for want of a permission says which permission is missing.
2. **Edge.** None.
3. **See.** [quality-requirements.md](quality-requirements.md#a-refusal-names-its-control).

### PRINCIPLE-026

**The project's settings live in its own configuration file.** The project ships its own configuration file, `conf/cassandra_chronitondb.yaml`, which carries its own settings and values. Apache Cassandra's `conf/cassandra.yaml` and `conf/cassandra_latest.yaml` stay untouched. A node switched from Apache Cassandra keeps the operator's own file.

1. **Applies to.** Every setting the project adds or ships with another value.
2. **Edge.** None.
3. **See.** [release.md](release.md#the-configuration-file), [upstream.md](upstream.md#configuration-changes).

### PRINCIPLE-027

**An operator control is complete.** A control that an operator sets on a running node validates its input and refuses a bad value with the reason. Its change is logged, see [PRINCIPLE-034](#principle-034). It has a matching way to read the value, and its effect is visible to the operator. No operator command changes user schema: a schema change is a CQL statement.

1. **Applies to.** Every runtime setter a feature adds, in nodetool, JMX or elsewhere. For example a command that sets a limit has a command that prints it, and a metric shows the limit in use.
2. **Edge.** A setter whose effect cannot be shown says why in its design, and the maintainers approve it with the design.
3. **See.** [templates/design-record.md](templates/design-record.md#8-observability).

## Automatic behaviour and fallbacks

### PRINCIPLE-028

**Automatic behaviour is opt in and counted.** Automatic behaviour the user did not ask for, and that changes results, cost or plan, is opt in. An operator can switch it at startup and on a running node, at the scope the design chose. Each use is counted, and logged without flooding.

1. **Applies to.** Every fallback and every other behaviour a feature starts by itself. For example a query that falls back to a scan, or a repair that falls back from incremental to full.
2. **Edge.** A fallback that changes none of the three, such as a node that speaks an older message version to an older peer, is not under this principle.
3. **See.** [quality-requirements.md](quality-requirements.md#automatic-fallbacks-are-opt-in-and-counted).

### PRINCIPLE-029

**A fallback is allowed on the schema object, and the node control wins.** Whether a schema object allows a fallback is an option on that object, off by default. The object is the index, table or other schema object the fallback serves. Each node also has an operator control that turns every fallback off on that node. The node control always wins: the option on the object never turns on what the node control has turned off.

1. **Applies to.** Every fallback under [PRINCIPLE-028](#principle-028). For example an index that may fall back to a scan, or a table that may take a full rebuild in place of an incremental one.
2. **Edge.** None.
3. **See.** [quality-requirements.md](quality-requirements.md#automatic-fallbacks-are-opt-in-and-counted).

### PRINCIPLE-030

**An answer is complete, or it is an error.** Missing data is as bad as wrong data. Every answer a fork feature gives MUST be complete at the requested consistency level, or an error. A confirmed correctness fault in fork code, or on a path a fork feature serves, is fixed, never only documented.

1. **Applies to.** Every result a fork feature returns, to a client or to an operator. For example a read that cannot reach enough replicas errors, and a tool listing that could not read one node says so and never prints a short list as if it were complete.
2. **Edge.** A partial answer is allowed only where it is deliberate, opt in and marked in the response, see [PRINCIPLE-031](#principle-031). A correctness gap in stock outside such a path follows [PRINCIPLE-014](#principle-014).
3. **See.** [classification.md](classification.md#risk).

### PRINCIPLE-031

**A response that is partial or cut short says so itself.** When a response must tell the client something about itself, such as that it is partial or that a limit cut it short, it says so in the response, in the idiom of its surface. For example a CQL result carries a boolean result column in the style of the `[applied]` column of a lightweight transaction, present on every result of that statement shape while the option that can produce the condition is set. A client warning MAY go with it. A custom payload that only some drivers read is not used.

1. **Applies to.** Every response of a fork feature that can be partial, cut short or otherwise marked. A response on another surface, such as the output of a tool, marks the condition in that surface's own idiom.
2. **Edge.** None.
3. **See.** [PRINCIPLE-060](#principle-060).

### PRINCIPLE-032

**The user states the intent, the system does not guess it.** Where syntax or an option would otherwise guess a behaviour for the user, the user states the intent. A statement that cannot tell which of two behaviours is meant fails with an error instead of choosing. A default stays where an established idiom supplies one.

1. **Applies to.** New syntax, options and commands. For example a schema change that would need a rebuild asks the user to say so, and a command that could mean one table or all of them is refused until the user names which.
2. **Edge.** None.
3. **See.** [PRINCIPLE-060](#principle-060).

## Observability and logging

### PRINCIPLE-033

**Observability is a gate item, not an afterthought.** Every outcome has a counter. Every limit reports its limit, the amount used and the number of times it tripped. Each plan decision and each fallback has a trace line. A feature's observability is part of its design and is checked with it.

1. **Applies to.** Every fork feature, in proportion to the runtime behaviour it adds. For example a background job shows what it started, completed and failed, and a limiter shows its limit, its use and its trips.
2. **Edge.** A change that adds no runtime behaviour says so in one line, and a change with no traced request path gives the reason in its tracing test list. The maintainers accept the line by merging the record.
3. **See.** [quality-requirements.md](quality-requirements.md#observability), [templates/design-record.md](templates/design-record.md#8-observability).

### PRINCIPLE-034

**Operator actions and node states are logged.** Every runtime change of a setting logs the old and the new value at INFO. Startup logs the effective state of each fork switch. A state in which the node runs degraded is logged at WARN, without flooding.

1. **Applies to.** Every setting, switch and degraded state a feature adds.
2. **Edge.** The change of a setting that holds a secret is logged without either value.
3. **See.** [quality-requirements.md](quality-requirements.md#observability).

### PRINCIPLE-035

**No log line the project writes carries user data or a secret.** Code the project writes never puts user data or a secret in a log line, at any log level. User data means partition keys, clustering and column values, bind values, query literals, query text that carries them, and search terms. A log line names what it is about by schema object and by a value that identifies no user. Diagnosis that needs the data itself goes through a path with its own access control, as the design chooses.

1. **Applies to.** Every log line fork code writes. For example a line names the keyspace and table, a token, a count, a size or a duration. Tracing or a virtual table is a path with its own access control.
2. **Edge.** None. Log lines that Apache Cassandra writes follow [PRINCIPLE-008](#principle-008).
3. **See.** [quality-requirements.md](quality-requirements.md#observability).

### PRINCIPLE-036

**Nothing is logged once per request or per element.** An event that happens per request or per element, such as a row, a partition, a file or a message, is not logged one by one. Its detail goes to metrics and tracing. Logs carry operator actions and periodic summaries with counts, limited in rate.

1. **Applies to.** Every path of fork code that runs per request or per element. For example the refusals of a query limit, the rows a compaction task rejected and the files a stream skipped are each counted, with at most one summary line in a period for each schema object and reason.
2. **Edge.** None.
3. **See.** [quality-requirements.md](quality-requirements.md#observability).

### PRINCIPLE-037

**A signal is released with the object that owns it.** Every metric, MBean and virtual table row a feature creates is released when its object is dropped. After the drop nothing of it stays registered, and a test proves it.

1. **Applies to.** Every signal a feature registers. For example the metrics of an index go with the index, its table and its keyspace, and the metrics of a pool go when the pool shuts down.
2. **Edge.** None.
3. **See.** [quality-requirements.md](quality-requirements.md#observability).

### PRINCIPLE-039

**A limit reaches the client, and state reaches the operator.** A limit that changes results or rejects work reaches the client and is counted. State that an operator would otherwise search the logs for is exposed where it can be queried. Such a surface holds operational state, not user data.

1. **Applies to.** Every limit and every operational state a feature adds. For example a virtual table row shows the state of a build.
2. **Edge.** A surface carries user data only where the design chose it as the path with its own access control for diagnosis, see [PRINCIPLE-035](#principle-035).
3. **See.** [templates/design-record.md](templates/design-record.md#8-observability).

## Security

### PRINCIPLE-041

**Every new entry point has a threat model.** Every new entry point of a feature is checked with STRIDE: spoofing, tampering, repudiation, information disclosure, denial of service and elevation of privilege. Each mitigation is a requirement. An entry point is syntax, a setting, a command, a file or the network.

1. **Applies to.** Every feature and every one-item change.
2. **Edge.** A change with no new entry point says so, with the reason.
3. **See.** [standards.md](standards.md#requirements-and-architecture), [templates/feature-spec.md](templates/feature-spec.md#6-threat-model).

### PRINCIPLE-042

**A value a client supplies never picks code or a resource.** A name that a client supplies never picks code to load unless it is on an allow list. The project's own list is fixed in the code, proposed by the design with a reason for each entry, and approved by the maintainers in a decision record. A new entry is a new decision. A value a client can set names no class, file, address, command or other resource of the node: names resolve against a fixed set.

1. **Applies to.** Every option, argument and name in a statement that a feature accepts. For example an analyzer name, an option of a compaction strategy, or a file name in a statement.
2. **Edge.** An operator's extension of the allow list in a node's configuration, for code the operator has placed on the node, is not ruled out: it is designed and decided when a feature needs it.
3. **See.** [conventions.md](conventions.md#code-layout).

### PRINCIPLE-043

**Every untrusted input is bounded before the work.** Every untrusted input has a bound that is checked before the expensive step it protects. Over a bound the request fails with a client error that names the input, the object, the count and the limit. It never fails with a server error, a stack trace or an internal path.

1. **Applies to.** Everything a feature parses or takes from a client. For example a length is checked before a parse, the size of a pattern before it is compiled, a count during a walk, and a number of rows before they are held in memory.
2. **Edge.** None.
3. **See.** [templates/design-record.md](templates/design-record.md#10-threat-model-and-security).

### PRINCIPLE-045

**Nothing lets a role learn about data it cannot read.** Nothing the project adds lets a role learn about data it could not `SELECT`: not through results, counts, derived values such as a score, error text, or timing that an attacker can measure in practice.

1. **Applies to.** Every result, error and signal a feature gives a client.
2. **Edge.** None.
3. **See.** [templates/design-record.md](templates/design-record.md#10-threat-model-and-security).

### PRINCIPLE-046

**A limit the project adds binds every client.** A guardrail or limit the project adds binds every client, superusers and clusters without authentication included. Apache Cassandra's own guardrails keep their own rules.

1. **Applies to.** Every guardrail and limit a fork feature adds.
2. **Edge.** None. This is a deliberate difference from how stock guardrails treat superusers, made for security, as [PRINCIPLE-059](#principle-059) asks it to be stated.
3. **See.** [templates/design-record.md](templates/design-record.md#10-threat-model-and-security).

### PRINCIPLE-047

**Every copy of user data has a lifetime.** A new copy of user data, or of anything derived from it, is listed in the design with its lifetime and what deletes it. No copy the project makes outlives its source, and the smaller copy is the default. Every new kind of file that stores values has a test that writes a value, deletes it, runs the purge the design names and searches the files for the value and its derived forms.

1. **Applies to.** Every file, cache and structure a feature adds that holds user data. For example data kept per sstable is registered with the sstable, so that snapshots, streaming, cleanup and compaction see it. Derived data, such as stemmed, hashed or lower cased values, is treated as its source is.
2. **Edge.** None.
3. **See.** [templates/design-record.md](templates/design-record.md#12-compliance-impact).

### PRINCIPLE-048

**A vulnerability is private until disclosure.** All work on a vulnerability happens in private until disclosure. Before disclosure no public text names it, and a fix is described by its mechanics. Only the maintainers decide validity, severity, the disclosure date and publication.

1. **Applies to.** Every vulnerability in the project's code, in Apache Cassandra's code on a line and in a shipped library.
2. **Edge.** None. When Apache Cassandra's code is affected, its security team is notified at once, with the fix.
3. **See.** [security.md](security.md).

### PRINCIPLE-049

**No dependency is used before it is declared and approved.** No new dependency, and no version change of an existing one, is used before it is declared and approved in a feature spec or design record. Every third party component is checked against the Apache Software Foundation licence categories before use. A library update is an item of its own, never made inside the item that needs it.

1. **Applies to.** Every library and other third party component the build pulls in.
2. **Edge.** A patch-version update of an approved library, under the same licence, for a bug or security fix needs no design record. It still goes through the security engineer.
3. **See.** [compliance.md](compliance.md#declaring-dependencies), [maintenance.md](maintenance.md#dependency-patch-version-updates).

## Performance

### PRINCIPLE-050

**Performance first.** The design is the fastest correct design known when it is written. Each design record names the request paths the change touches, the expected cost with its mechanism, and the benchmarks that prove it.

1. **Applies to.** Every fork feature.
2. **Edge.** A design states the reason the rule does not apply to it, and the maintainers approve the reason with the design.
3. **See.** [quality-requirements.md](quality-requirements.md#performance-first), [testing.md](testing.md#benchmarks).

### PRINCIPLE-051

**Isolation levers.** Every fork feature has levers on the coordinator and on each replica that keep it from harming the rest of the node: its own thread pools, limits on work per request, load shedding, timeouts, memory budgets and a kill switch. Each lever has a yaml setting and a metric.

1. **Applies to.** Every fork feature.
2. **Edge.** A design states the reason a lever does not apply to it, and the maintainers approve the reason with the design.
3. **See.** [quality-requirements.md](quality-requirements.md#isolation-levers), [templates/design-record.md](templates/design-record.md#isolation-levers).

### PRINCIPLE-052

**The stock path is guarded.** With a fork feature off, the stock path it touches shows no change in what an application sees, and stock performance does not move. The design names the stock runs that must not move, and for a change with a switch the run with the switch off that must match stock.

1. **Applies to.** Every change that touches a path stock work runs on.
2. **Edge.** None.
3. **See.** [testing.md](testing.md#benchmarks), [templates/design-record.md](templates/design-record.md#apache-cassandra-guard).

### PRINCIPLE-053

**A change is gated on counted values, never on timing.** Pull request checks block only on counted values and on benchmarks that fail to run. They never block on timing. A performance claim rests on paired runs, and an absolute timing number comes only from pinned or dedicated hardware.

1. **Applies to.** Every benchmark a design names. For example allocations per operation, work counters, bytes written per compaction and index bytes per raw byte are counted values.
2. **Edge.** Once dedicated benchmark hardware is in place, a change point in the tracked timings blocks the next release.
3. **See.** [testing.md](testing.md#benchmarks).

## Simplicity of design

### PRINCIPLE-054

**The simplest sufficient design.** A design is the one with the least to understand, build, test, operate and recover that meets the requirements, the decisions of the maintainers and the rules of these pages. The burden of proof is on each addition, never on the simpler design. The search starts from no change, then an existing Apache Cassandra mechanism, then an existing mechanism of the project, then something new.

1. **Applies to.** Every feature spec, design record and fix record. For example a condition an index cannot answer is met by stock filtering of the rows the index returns before a new operator on the replica, and a value an operator needs is a column in an existing virtual table before a new command.
2. **Edge.** The principle is a strong default and no ban: complexity that a requirement, a decision, a rule or a named risk needs is kept. See [PRINCIPLE-056](#principle-056) for what simple never means.
3. **See.** [PRINCIPLE-055](#principle-055).

### PRINCIPLE-055

**An addition names what needs it.** An addition is anything that adds a state, a code path, a setting, a dependency, a stored or sent format, or a step for an operator. For each one the document names what needs it, a requirement, a decision of the maintainers, a rule of these pages or a named risk, and why the simpler design does not meet it. An addition with no such line is left out, or left to a later record with the condition that would bring it back.

1. **Applies to.** Every addition in a design, and every review finding that asks for one. Simplifying code that already works is itself a change with a cost and a risk, and needs the same line.
2. **Edge.** Where the need rests on something not measured or not known, the document says so, marks the addition provisional and names the check that would settle it. No figure is invented to justify it.
3. **See.** [branching-and-review.md](branching-and-review.md#feature-switches-and-defaults) applies the same test to a feature switch.

### PRINCIPLE-056

**Simple never means unsafe.** Simple never means dropping security, data safety, recovery or what an operator needs to see, and never means moving the work to the operator or the client. A needed safeguard is met by the simplest control that is adequate, never by none. Simple is not fewer lines of code: the cost of an option is stated as what happens at runtime, never as its volume of code. Between two designs that both suffice, the one that is cheaper to undo is preferred.

1. **Applies to.** Every choice between designs. For example the cost of an option is its effect on correctness, latency, IO, memory and the operator. An addition that is costly to undo later, such as a stored or sent format or a name users see, says so.
2. **Edge.** None.
3. **See.** [PRINCIPLE-054](#principle-054).

## Decisions and consistency

### PRINCIPLE-057

**What a user or an operator sees is decided by the maintainers, and recorded.** A choice that changes what a user or an operator sees or must act on is decided by the maintainers before it is built. The answer is a decision record, with its reason. A record states the decision cleanly and points to no private material.

1. **Applies to.** For example which rows a query returns, an error, a refusal, a default, a limit, the output of a nodetool command, the name of a metric, an on-disk or wire form and the upgrade path.
2. **Edge.** A choice with no such effect, and one that follows the convention Apache Cassandra already has for that kind of thing, needs no record.
3. **See.** [The decision records](../decisions/README.md#when-a-record-is-written), [roles.md](roles.md#maintainer).

### PRINCIPLE-058

**A defined meaning holds in every shape.** Once the meaning of an operator, an option, a setting or a command argument is defined, it holds in every shape it appears in. When a new shape makes the definition costly, the design keeps the definition and states the cost.

1. **Applies to.** Everything a user or an operator can write. For example `=` on a column means the same alone, in `IN`, in a batch, prepared or literal, and the unit of a setting is the same in the configuration file, in its runtime setter and where it is read back.
2. **Edge.** None. A consequence of the fixed meaning that a user sees in a new shape, such as an error or a limit, is decided under [PRINCIPLE-057](#principle-057).
3. **See.** [templates/design-record.md](templates/design-record.md#5-idiom-and-consistency).

### PRINCIPLE-059

**Consistency over cleverness.** The project stays consistent with the fundamentals of Apache Cassandra and with its own earlier decisions, in preference to a design that is clever in one place. For each user visible choice the design says whether it matches Apache Cassandra, earlier decisions and the idiom it follows.

1. **Applies to.** Every user visible choice. The fundamentals are for example `ALLOW FILTERING`, the meaning of an operator, how a nodetool toggle behaves and how a guardrail warns and fails.
2. **Edge.** A deliberate difference carries its reason, written next to the decision, such as performance, security, compliance or a defect in stock. A decision that reverses an earlier one says so, in a record that supersedes it.
3. **See.** [templates/design-record.md](templates/design-record.md#5-idiom-and-consistency), [the decision records](../decisions/README.md#rules).

### PRINCIPLE-060

**New syntax follows an existing idiom.** New syntax follows an existing idiom, never one invented for the project. A feature has one user facing syntax. The design names the idiom and what a user of that idiom expects the text to mean.

1. **Applies to.** New CQL syntax, options, commands and their output. For example a new nodetool command follows nodetool's own verbs and output style.
2. **Edge.** A conflict between two idioms is decided by the maintainers each time, in a decision record.
3. **See.** [templates/feature-spec.md](templates/feature-spec.md#12-prior-art).

## Compatibility between versions and nodes

### PRINCIPLE-061

**A feature adds no dependence on topology.** A fork feature adds no dependence on topology. Whether a statement that uses it is valid, and the rows it returns for the same data at a consistency level that can be met, are the same at any replication factor, number of data centres and number of replicas. So a feature behaves on a single node development cluster as it does on a production cluster with three replicas.

1. **Applies to.** Every fork feature. One that runs across nodes is tested at replication factor 1 and at replication factor 3 on the same data, and across two data centres when its behaviour involves a data centre aware consistency level or replication strategy.
2. **Edge.** Where Apache Cassandra itself depends on topology, such as availability at a consistency level, that stays as it is.
3. **See.** [quality-requirements.md](quality-requirements.md#a-feature-adds-no-dependence-on-topology), [testing.md](testing.md#policy).

### PRINCIPLE-062

**A change to a shared surface states and proves its upgrade, its rollback and its mixed-version behaviour.** A feature states its on-disk format changes with their version markers, its behaviour in a mixed-version cluster during a rolling upgrade, its upgrade path with prerequisites, its rollback path and its runbook entries. A milestone that introduces an on-disk format change has upgrade and rollback tests among its exit criteria. A newer line reads everything an older line writes.

1. **Applies to.** Every change to a surface nodes or versions share: a file on disk, the schema, a message between nodes, a setting. For example a new component beside an sstable, or a new gossip state.
2. **Edge.** A feature with no format, schema or protocol change says so, and still states its mixed-version and rollback behaviour where its class requires the section.
3. **See.** [additive.md](additive.md#level-1-the-feature-spec), [testing.md](testing.md#upgrade-and-rollback-tests), [templates/feature-spec.md](templates/feature-spec.md#7-compatibility).

## Testing

### PRINCIPLE-063

**Every requirement has a test that proves it.** Every requirement has at least one test that proves it. A requirement that needs tests at two levels keeps one id and lists both tests. A requirement that states two behaviours is split into two ids.

1. **Applies to.** Every requirement of a feature spec, a design record and a fix record.
2. **Edge.** A requirement that is deliberately not tested has its reason in the item's coverage file, approved with the design record.
3. **See.** [testing.md](testing.md#policy), [templates/ac-coverage.md](templates/ac-coverage.md).

### PRINCIPLE-064

**A fix starts with a test that reproduces the fault.** A fix starts with a test that reproduces the fault. It MUST fail before the fix and pass after it. The test and the fix merge together, so the line never carries a failing test.

1. **Applies to.** Every corrective and emergency change. A fix to stock code keeps its reproducing test in one of Apache Cassandra's own test harnesses, so the test can be offered to Apache Cassandra with the fix.
2. **Edge.** A dependency patch-version update has no reproducing test: the tests that cover every use of the library MUST pass.
3. **See.** [testing.md](testing.md#policy), [maintenance.md](maintenance.md#corrective-fixing-a-fault).

### PRINCIPLE-065

**A test that existed before a change is not weakened.** A test that existed before a change MUST NOT be weakened. An assertion, an expected value or an error text of a merged test of the project's own changes only when the record that plans the change says which one changes, from what to what, and why the old expectation is no longer right. The reviewer checks each against the record. A changed assertion the record does not name is a blocker. New tests and new assertions are free.

1. **Applies to.** The project's own tests, once merged. Apache Cassandra's test files follow [PRINCIPLE-013](#principle-013).
2. **Edge.** None.
3. **See.** [testing.md](testing.md#policy).

### PRINCIPLE-066

**A test's verdict does not depend on speed or on a retry.** A test's verdict MUST NOT depend on how fast the machine runs. A test that needs time to pass uses a clock the test controls, or waits for a condition with a bound. An assertion is never retried, and a randomised test prints its seed so a run can be repeated.

1. **Applies to.** Every test the project writes. A test of a fork feature runs with the feature on, unless it is about the off state, and one that is skipped without a stated condition counts as a failure.
2. **Edge.** Timed benchmarks follow their own rules, see [PRINCIPLE-053](#principle-053). A retry is for a failure of the test infrastructure only.
3. **See.** [testing.md](testing.md#policy).

### PRINCIPLE-067

**The kind of test proves the claim.** The kind of test is picked from the claim the design makes. A kind that cannot prove the claim does not count, however many of its tests pass. A change runs its tests in every test configuration whose settings the changed code reads.

1. **Applies to.** Every test plan. For example a claim about several nodes needs a distributed test, a claim about an upgrade needs an upgrade test, and a change that touches compaction or an on-disk format runs on both sstable formats.
2. **Edge.** None.
3. **See.** [testing.md](testing.md#test-levels).

### PRINCIPLE-068

**A TLA+ model where the maintainers ask for one.** A design whose correctness depends on ordering, concurrency or shared state, across nodes or within one node across a crash and restart, is a candidate for a TLA+ model. The design record says why a model is believed to be needed and asks the maintainers, and the model is written only when they say yes.

1. **Applies to.** Every design record and fix record. For example a new message between a coordinator and its replicas, or a file a node writes in two steps and reads back after a crash.
2. **Edge.** A design with no such dependence says in one line why it needs none, and asks nothing.
3. **See.** [quality-requirements.md](quality-requirements.md#a-tla-model-where-the-maintainers-ask-for-one).

## Risk

### PRINCIPLE-069

**The risk of a change is the worst it could cause.** The risk of a change is the worst it could cause if it were wrong. Anything unknown counts as its strictest value. A change is Low risk only when the worst it could cause is a wrong document, a wrong package or a failing test, and nothing a running node does can change.

1. **Applies to.** Every change. For example a refactor on a request path is Normal unless its tests show the behaviour is the same.
2. **Edge.** A maintainer may change the class of a change at any time.
3. **See.** [classification.md](classification.md#risk).

### PRINCIPLE-070

**A change to a public interface or to stock behaviour is never Low risk.** A change that touches a public interface or stock behaviour is at least Normal risk, whatever the worst it could cause. So is a change to a file that guards the process, such as the CI workflows, the build file and these pages.

1. **Applies to.** Every change. The public interfaces are the areas of compatibility that Apache Cassandra lists for its own enhancement proposals, and virtual tables.
2. **Edge.** None.
3. **See.** [classification.md](classification.md#the-floor).

### PRINCIPLE-071

**The Critical floor is about what code does.** Work that touches authentication, authorisation, encryption, audit logging, the decoding of bytes from the network, the node's data on disk, repair, streaming or compaction is risk Critical, whatever else its class would be. The floor is about what code does, not who wrote it or where it lives: a class of the project that takes part in one of these areas is on the floor as a change to the Apache Cassandra code of that area is.

1. **Applies to.** Every change, in Apache Cassandra's files or in the project's own.
2. **Edge.** The maintainers MAY say that a given change is not Critical. An import from Apache Cassandra is not on the floor merely because Apache Cassandra's own commits touch one of these areas. It is Critical when it changes, or conflicts with, something the project added or edited in such an area, or when the maintainers say so.
3. **See.** [classification.md](classification.md#the-critical-floor), [PRINCIPLE-074](#principle-074).

### PRINCIPLE-072

**Every change says where problems could occur.** A change says where it could go wrong if a part of it is wrong, worst case first, and names the test that would catch each problem. The answer is never "None" or "Low", and never an argument that the change is safe.

1. **Applies to.** Every feature spec, every fix record, every design record that its feature spec does not cover, and the pull request of Low risk work.
2. **Edge.** A problem that no test can catch says why, and how it is watched instead.
3. **See.** [classification.md](classification.md#where-problems-could-occur).

## Imports from Apache Cassandra

### PRINCIPLE-073

**Every Apache Cassandra patch release is taken, whole.** Every Apache Cassandra patch release of a line's major version is imported into that line in whole. A release is never skipped. A single fix MAY be taken ahead of the release that contains it, for any stated reason, when the maintainers merge it.

1. **Applies to.** Every line. Before Apache Cassandra's first release of a major version, the line follows the Apache Cassandra branch week by week.
2. **Edge.** An import is held while a finding on it is open, see [PRINCIPLE-074](#principle-074).
3. **See.** [upstream.md](upstream.md#whole-apache-releases).

### PRINCIPLE-074

**A fault in imported code is decided before the import merges.** A correctness, security or performance finding of major severity or worse in imported Apache Cassandra code goes to the maintainers before the import's pull request merges. So does any finding that an imported change conflicts with something the project adds. The import does not merge until the maintainers decide for each finding: report it to Apache Cassandra, hold the import, fix it as a fix to stock, or accept it.

1. **Applies to.** Every import: a whole release, a branch merge, a single fix and a commit from another project.
2. **Edge.** Findings on shape limits and style in Apache Cassandra's own code are listed in the import's assessment and go no further. An import is never changed for style alone.
3. **See.** [upstream.md](upstream.md#whole-apache-releases).

### PRINCIPLE-075

**Code brought in keeps its identity and its credit.** An imported commit keeps its original author and message, and a commit that brings in a change from elsewhere names where it came from: the Apache Cassandra ticket and commit, or the other project and commit. Work adapted from another project credits each of its authors. A commit from another project comes in unchanged or not at all.

1. **Applies to.** Every import from Apache Cassandra and every piece of code taken or adapted from another project.
2. **Edge.** None. The author of an import is never rewritten, also not to pass a check.
3. **See.** [upstream.md](upstream.md#imports-keep-their-upstream-identity), [conventions.md](conventions.md#code-from-elsewhere), [compliance.md](compliance.md#notice-and-credits).

### PRINCIPLE-076

**Another implementation is reviewed, never assumed right.** Another implementation is never the right design because it exists. A design says how other systems solved the problem and what each got right and wrong, before it proposes anything like them. Code or text under a licence that is not compatible with the Apache License 2.0 MUST NOT be copied, and the behaviour of such a system is taken only from its public documentation. The project owes compatibility to Apache Cassandra, not to any other project derived from it.

1. **Applies to.** The prior art of every feature spec and design record.
2. **Edge.** None. Contributors working on the project's behalf do not search for or read patents for design work: a patent concern goes to the maintainers.
3. **See.** [templates/feature-spec.md](templates/feature-spec.md#12-prior-art), [compliance.md](compliance.md#third-party-licences).

## Documentation and naming

### PRINCIPLE-077

**Documentation ships with the change.** An item is not done until the user documentation, operator documentation and runbook entries it affects are in the same pull request. Everything a change adds that a user or an operator sees is documented by its exact name: a setting, an option, a metric, a virtual table, a command and an error text.

1. **Applies to.** Every item that changes what a user or an operator sees.
2. **Edge.** None. Release notes are generated from the commits at release.
3. **See.** [additive.md](additive.md#documentation-with-each-item), [conventions.md](conventions.md#where-things-live).

### PRINCIPLE-078

**A claim about code names the code it was read in.** A claim about what code does is read in the code before it informs a design, and names the project, the branch and the commit, with the symbol and the file and line. Analysis keeps three sources apart: the line, the Apache Cassandra release the line is based on, and Apache Cassandra upstream now.

1. **Applies to.** The process pages and every document written from a template.
2. **Edge.** A claim that could not be read in the code says that it is not verified.
3. **See.** [conventions.md](conventions.md#claims-about-code).

### PRINCIPLE-079

**Names are additions, and say what they mean.** No metric, MBean, virtual table, column, setting or command of Apache Cassandra is renamed, and stock metric types gain no new metrics. The project's signals and settings live under its own names, which never contain "cassandra" or "axon", and no key or value contains "stock". A setting that means what a comparable system's setting means SHOULD carry its name, and an option that defers to the node's global setting takes the value `inherit`.

1. **Applies to.** Every new user facing name: yaml keys, nodetool commands, MBeans, metric types, packages and options.
2. **Edge.** A name the maintainers fixed in a decision record.
3. **See.** [conventions.md](conventions.md#names).

### PRINCIPLE-080

**A document is complete with the repository alone.** A document, a code comment and a commit of the project cite only what a reader of the repository can open: these pages, the decision records, the design documents, the code and public sources. A rule is cited by its id from this page. Nothing cites private material, such as a note or a conversation.

1. **Applies to.** Every document, comment and commit message. For example a requirement that follows from a rule names the principle, and a record never links to the brief it was written from.
2. **Edge.** The work on a vulnerability stays in its private advisory until disclosure, see [PRINCIPLE-048](#principle-048).
3. **See.** [The decision records](../decisions/README.md#rules), [additive.md](additive.md).

### PRINCIPLE-081

**A published standard comes before a house rule.** The project uses a published standard in place of a house rule wherever one fits. Where a page of this folder and a standard differ, the page says why.

1. **Applies to.** The process, the documents and the formats the project publishes.
2. **Edge.** None.
3. **See.** [standards.md](standards.md).
