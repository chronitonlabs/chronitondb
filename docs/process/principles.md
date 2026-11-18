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
3. The id cannot be mistaken for another id of the project: no other id of the project starts with `PRINCIPLE-`. See [additive.md](additive.md#feature-keys-and-requirement-ids).
4. A principle says what must be true. Words after "for example" or "such as" are examples, of a way to meet the principle or of what it covers. They are never the whole list.
5. Each principle says where it applies and gives its edge: what the exception is and who decides it. An exception that a principle does not name is a decision of the maintainers. The design record or fix record of the work that needs it states the exception, with the principle and the reason, and names the principle in the `Exceptions` row of its document control table. The maintainers decide the exception by merging the record. A principle may also name an exception that is marked in the same row, as [PRINCIPLE-064](#principle-064) does. The [generated index](../index/documents.md) lists every marked record under the principle it departs from.
6. Each principle links the decision record that set it, where one exists, and the page that gives the procedure.
7. A document cites a principle by its id, as a link to its entry, for example `[PRINCIPLE-016](../process/principles.md#principle-016)` with the path from the citing document. A document cites nothing that a reader of the repository cannot open. See [PRINCIPLE-080](#principle-080).
8. The maintainers approve a new principle, or a change to one, by merging the change to this page, with the decision record behind it where a question was answered. The change is first read against the four questions of [governance.md](governance.md#changes-to-this-page). The first published version of this page is approved by the merge that publishes it.
9. What Apache Cassandra does is evidence for a design, and never by itself the reason to allow something: the design states the reason.

## Compatibility with Apache Cassandra

### PRINCIPLE-001

**An application behaves as it did on Apache Cassandra, and a user can move back.** An application that moves onto the project's database MUST behave as it did on Apache Cassandra, and a user MUST be able to move back to Apache Cassandra. A change to what an application sees from a stock feature is a feature, and it MUST sit behind a feature switch that is off by default. What an application sees is its results, its errors, its warnings and the bytes on the wire.

1. **Applies to.** Every change on a line. For example a read that would return other rows for a stock statement, a new warning on a stock statement, or a changed frame of the native protocol. A keyword the project adds is unreserved, so that a name an application already uses keeps working.
2. **Edge.** A fix to a defect in stock is not a feature and is not gated, see [PRINCIPLE-004](#principle-004). Which Apache Cassandra release a cluster can move back to, and by which steps, is stated for each release, and a line whose major version Apache Cassandra has not released yet has no entry point from Apache Cassandra: [PRINCIPLE-003](#principle-003).
3. **See.** [DEC-GOV-0001](../decisions/DEC-GOV-0001-what-stays-as-apache-cassandra-has-it.md). [quality-requirements.md](quality-requirements.md#compatibility-with-apache-cassandra), [branching-and-review.md](branching-and-review.md#feature-switches-and-defaults).

### PRINCIPLE-002

**What operators see stays as stock where that is reasonable.** What an operator sees is metrics, nodetool output, logs and JMX. It SHOULD stay as stock where that is reasonable. A difference there MUST be recorded in the delta register and in the release notes. It is recorded, not refused, and it does not by itself make a feature behaviour-changing.

1. **Applies to.** Every change to a surface an operator reads. For example the release version that `nodetool version` prints, or a new column in the output of a stock command. The rows of Apache Cassandra's virtual tables are what operators see, not what an application sees.
2. **Edge.** Whether staying as stock is reasonable is judged case by case, by the maintainers when they merge the design. A stock surface that lists what the node holds, such as the settings virtual table, the startup configuration line, `tpstats` or the list of virtual tables, shows what the project adds to those. That is not a difference to record. Log lines have their own rule, see [PRINCIPLE-008](#principle-008).
3. **See.** [DEC-GOV-0001](../decisions/DEC-GOV-0001-what-stays-as-apache-cassandra-has-it.md), record [0002](../decisions/0002-nodetool-version-output-on-a-chronitondb-node.md). [The delta register](../delta/README.md), [release.md](release.md#what-nodetool-version-shows).

### PRINCIPLE-003

**Moving between Apache Cassandra and the project is done on the same data files, by a runbook.** A user moves a cluster from Apache Cassandra onto a line, and back, on the same data files, by following a runbook that states its prerequisites. The entry condition for moving onto a line is a cluster on the latest Apache Cassandra release of the line's major version, with all of that version's own options on. Moving back needs documented steps. It does not have to be a swap of binaries on untouched files. Each release states which Apache Cassandra release, or releases, a cluster on it can move back to, and says when there is none yet. With every fork feature off, the state a node shares with others is as stock has it: schema tables, data files and their components, gossip and messages, and the state a node reads back after a restart: the commit log, hints, the batchlog and Paxos state. Everything the project writes to that shared state can be removed by a step the runbook names. A thing that makes an Apache Cassandra node refuse to start is acceptable when the release's steps say how to remove it. A state with no steps back is not acceptable: data that Apache Cassandra cannot read and that cannot be converted. Moving MUST be possible. It is not promised to need no steps.

1. **Applies to.** Every change that writes to disk, to the schema or between nodes, and every line's upgrade runbook. For example a new sstable component, a new schema option, or a setting of the line's minimum setup, which a node checks at every start. The options of the entry condition are the values of Apache Cassandra's `conf/cassandra_latest.yaml`, such as no storage compatibility mode for an older major version, the newest sstable format and UUID sstable identifiers. The project ships those values, and moving back is to an Apache Cassandra configured the same way. For example the steps for moving back remove the project's keys from the configuration file, revoke a permission the project added, and leave no file in the data directories that Apache Cassandra cannot parse and no class name in the schema that it cannot load.
2. **Edge.** The fixes and the differences the delta register lists. The supported paths are from Apache Cassandra of the same major version onto a line, and from one release of a line to a later release of the same line. A line whose major version Apache Cassandra has not released yet, such as a 6.0 line before Apache Cassandra 6.0, has no entry point from Apache Cassandra, and its release notes say so. The project owns no path from one major version to the next ahead of Apache Cassandra: a move from one line to the next exists only once Apache Cassandra has released the newer line's major version. No older version of Apache Cassandra is supported, and no compatibility mode for one. A step of Apache Cassandra's own that has no way back is named in the release's steps as a prerequisite. So is the Java version of the line, in both directions. With a feature on, an object that does not use it keeps the schema state it has on Apache Cassandra: [PRINCIPLE-089](#principle-089).
3. **See.** [release.md](release.md#the-configuration-file), [release.md](release.md#switching-a-node-from-apaches-package), [release.md](release.md#moving-back-to-apache-cassandra), [testing.md](testing.md#upgrade-and-rollback-tests), [templates/feature-spec.md](templates/feature-spec.md#7-compatibility).

### PRINCIPLE-004

**A fix to a defect in stock is applied, and only the maintainers say what is a fix.** A fix to a defect in stock is not a feature and MUST NOT be gated behind a switch. It is applied, with its fix record, its delta entry and a release note. A change to stock code counts as a fix only when the maintainers approve it as one, by merging its fix record after the reviewer's finding on the evidence. A change to stock behaviour that is not approved as a fix is a behaviour change under [PRINCIPLE-001](#principle-001).

1. **Applies to.** Every change to Apache Cassandra's own code or behaviour. The evidence is a test that reproduces the fault and fails before the change, and either an Apache Cassandra ticket that treats the behaviour as a bug or the documented behaviour the fault breaks.
2. **Edge.** A fix is not gated and applies on each node as it is upgraded. Where a fix would cause errors or wrong results while a cluster is half upgraded, its fix record says so, and the maintainers decide how that fix rolls out. A fix record that is not merged is not a fix, and code for it MUST NOT merge before it. The reviews of a security fix stay in its private advisory until disclosure.
3. **See.** [DEC-GOV-0001](../decisions/DEC-GOV-0001-what-stays-as-apache-cassandra-has-it.md). [maintenance.md](maintenance.md#corrective-fixing-a-fault).

### PRINCIPLE-005

**New behaviour is reached through something stock does not have.** A statement that Apache Cassandra rejects only because it uses something Apache Cassandra does not have MAY succeed as a purely additive feature. A statement that Apache Cassandra accepts as valid and refuses for a reason is stock behaviour. Making it succeed is a change to what an application sees, under [PRINCIPLE-001](#principle-001). A statement that Apache Cassandra accepts and ignores is stock behaviour too, and giving it an effect is such a change.

1. **Applies to.** Every statement, option and command a feature accepts. For example new syntax, a new keyword, a new option or a new index type is something stock does not have. A missing `ALLOW FILTERING`, a guardrail or a missing index is a reason stock refuses.
2. **Edge.** None.
3. **See.** [DEC-GOV-0001](../decisions/DEC-GOV-0001-what-stays-as-apache-cassandra-has-it.md). [branching-and-review.md](branching-and-review.md#feature-switches-and-defaults).

### PRINCIPLE-006

**The numbers, ids and stored names Apache Cassandra owns are not changed.** The project never changes a version number, a format letter, a numbered id or a stored name by which Apache Cassandra recognises a file, a message or a grant. Among them are the messaging version, the sstable and index format version letters, the commit log, hint and saved cache versions, the cluster metadata serialization version on a line that has one, the ids of verbs, message parameters, gossip states, request failure codes and CQL operators, the native protocol's versions and codes, and the names of sstable components and of permissions. A feature that needs new state between nodes or on disk carries it in a form Apache Cassandra already accepts. An id the project adds to a set Apache Cassandra numbers is carried under a string key, or taken from the range Apache Cassandra keeps for others where there is one. It is never the next free number, and it is never reused. Such an id says only which number to use. A new verb is still a form an Apache Cassandra node cannot read, so the feature that sends it is held back until every node has it: [PRINCIPLE-016](#principle-016). Where no such form exists the design stops and asks the maintainers.

1. **Applies to.** Every feature with state on disk or between nodes. For example a new field on a request between nodes travels in the custom parameter map, which an Apache Cassandra node skips. State that must go with a write is carried in the write's own data, such as a column or a cell, or is derived on the replica from the schema: the commit log, hints and the batchlog keep the mutation and no message parameter. New data beside an sstable is an optional component, and what an index keeps in cluster metadata is text options. A form Apache Cassandra accepts is one that an Apache Cassandra node reads past or ignores.
2. **Edge.** A decision of the maintainers, in a decision record. A changed number that arrives unchanged in an import from Apache Cassandra is Apache Cassandra's own.
3. **See.** [quality-requirements.md](quality-requirements.md#compatibility-with-apache-cassandra).

### PRINCIPLE-007

**Code defaults in stock classes stay as Apache Cassandra has them.** A default of a stock field, such as one in `Config.java`, stays exactly as Apache Cassandra has it. So a cluster that keeps its own configuration file behaves as it did.

1. **Applies to.** Every edit to a stock class. A field the project adds has no stock default: where it is a feature switch its default follows [PRINCIPLE-017](#principle-017).
2. **Edge.** A fix to a defect in stock that must change such a default is applied with its fix record, its delta entry and a release note, see [PRINCIPLE-004](#principle-004). A default that Apache Cassandra changes arrives with its import.
3. **See.** [conventions.md](conventions.md#code-layout), [upstream.md](upstream.md#configuration-changes).

### PRINCIPLE-008

**A log line is not a compatibility concern, and stock log lines change in two ways only.** A log line that differs from stock is not a compatibility concern and is never a finding by itself, unless a test of Apache Cassandra reads the line or fails on it: then [PRINCIPLE-013](#principle-013) decides. A log line that fork code adds gets no delta entry. A log line that Apache Cassandra writes changes in two ways only: in an approved fix to a defect in stock, as part of the fix, with no switch, or by a feature whose purpose is to change what Apache Cassandra logs, behind a switch that is off by default. It never changes as a side effect of other work. An approved fix that changes a stock log line has its delta entry as any fix to stock does: [PRINCIPLE-011](#principle-011). It is the only change to a stock log line that gets an entry. A feature's change that touches only stock log lines gets no entry: the feature's own record tracks it and git shows it, and its pull request description carries the line `No delta entry: <reason>`, with its reason after the colon. Nothing more is asked for the log lines themselves: no list for each line.

1. **Applies to.** Every log line on a line. For example a startup line that names the fork's switches is an added line. A feature that removes sensitive data from stock log lines is the second way.
2. **Edge.** A log line that Apache Cassandra changes arrives with its import. A stock line that lists settings, pools or tables shows what the project adds to those, and that is not a change to the line. What a fork log line may carry is [PRINCIPLE-035](#principle-035).
3. **See.** [classification.md](classification.md#the-floor), [the delta register](../delta/README.md#keeping-it-current).

### PRINCIPLE-089

**Schema state is written only for an object that uses the feature.** Schema state the project adds is written only for a schema object that uses the feature it belongs to, never for every object. An object that does not use the feature has exactly the schema state it has on Apache Cassandra, with the feature on as with it off. When an object stops using the feature, what the feature wrote for it is removed.

1. **Applies to.** Everything a feature keeps in the schema, as it is stored and as nodes exchange it. For example an option the project adds to tables is written for a table whose statement set it and for no other table, and a new kind of index adds state for the indexes of that kind only. An object uses a feature when a statement asked for the feature on it. An absent value means that the object does not use the feature, and it means that on every node.
2. **Edge.** For an object that uses the feature, a configured default is resolved and stored with the object as [PRINCIPLE-021](#principle-021) says. Whether such an object keeps working with the feature off is [PRINCIPLE-019](#principle-019). Anything the project adds to the definition of a keyspace that Apache Cassandra defines in code is schema state on every node. So only a feature that is held back until every node has it adds such a thing: [PRINCIPLE-016](#principle-016).
3. **See.** [PRINCIPLE-003](#principle-003), [templates/feature-spec.md](templates/feature-spec.md#7-compatibility).

## Changes to Apache Cassandra code and tests

### PRINCIPLE-009

**Apache Cassandra's files change only where needed.** Apache Cassandra's own files stay as Apache Cassandra has them wherever the project can put its own file beside them. A change to one is made only where it is needed, and it is the smallest that does the job.

1. **Applies to.** Every file that came from Apache Cassandra, edited or not. For example the project keeps its own change log, configuration file, logging configuration, packaging and workflows beside Apache Cassandra's.
2. **Edge.** A change the work needs, with its delta entry. An import from Apache Cassandra changes these files as Apache Cassandra changed them.
3. **See.** [upstream.md](upstream.md#apache-files-change-only-where-needed), [conventions.md](conventions.md#stock-files).

### PRINCIPLE-010

**Fork logic lives in the project's own packages and shares stock logic, never copies it.** Fork logic lives in classes under `org.chronitondb`, and MUST NOT be added as a new class under `org.apache.cassandra`. An edit to a stock source file is the smallest that does the job: a hook that calls fork code or registers it, such as a grammar rule, a field in the stock configuration class or an entry in a stock list, a fix to a defect in stock, a refactor that lets fork code share stock logic in place of a copy, or the change a switched feature makes to stock behaviour under [PRINCIPLE-001](#principle-001) or [PRINCIPLE-008](#principle-008).

1. **Applies to.** All Java code the project writes. For example a new index type is a package of its own with a hook in the stock class that calls it, and a check that fork code needs from a stock class is shared by a refactor, not copied.
2. **Edge.** A new class that an approved fix to stock needs, source or test, is stock code and lives under `org.apache.cassandra`. A class of the project, source or test, that needs package private access to a stock package, and a refactor of stock code, are named in the design record and approved with it. Each stock file that imports fork code is a hook point, listed in the feature spec with its delta entry.
3. **See.** [conventions.md](conventions.md#code-layout), [branching-and-review.md](branching-and-review.md#two-review-standards-picked-by-file).

### PRINCIPLE-011

**Every change carried on top of Apache Cassandra is in the delta register.** Every change the project carries on top of Apache Cassandra has an entry in the delta register: what it is, why it is carried, where it came from and whether it went to Apache Cassandra. Every pull request that changes stock code or stock behaviour adds or updates its entry.

1. **Applies to.** Features, fixes to stock code, and build and packaging changes.
2. **Edge.** The import of a whole Apache Cassandra release or branch needs no entry. A log line that fork code adds needs none. A feature's change that touches only log lines that Apache Cassandra writes needs none either: only an approved fix that changes such a line has an entry, see [PRINCIPLE-008](#principle-008). A change to a stock file that no entry describes gives its reason in the pull request description, on the line `No delta entry: <reason>`, and the reviewer judges the reason.
3. **See.** [The delta register](../delta/README.md), [upstream.md](upstream.md#the-delta-register).

### PRINCIPLE-012

**Every fix to stock code is offered to Apache Cassandra.** Every fix to stock code is offered to Apache Cassandra, and its delta entry records the offer. A feature is offered only when the maintainers decide, case by case.

1. **Applies to.** Every approved fix to stock, see [PRINCIPLE-004](#principle-004).
2. **Edge.** A security fix is offered through the Apache Cassandra security team until disclosure.
3. **See.** [upstream.md](upstream.md#offering-changes-upstream).

### PRINCIPLE-013

**A stock test file changes in four ways only.** A pre-existing test file of Apache Cassandra changes in four ways only: in a fix to stock that the maintainers approved, unchanged in an import from Apache Cassandra, by lines added to a complete listing it pins, or by a change the maintainers approved case by case, as the Edge says. A fork feature puts its tests in its own files. Stock tests are of two kinds. A stock test that asserts behaviour MUST pass unchanged on any change the project makes: a behaviour change is behind a switch and the stock suites run with it off, so such a test that breaks shows the change is wrong, unless the change is an approved fix. A stock test that pins a complete listing breaks on a correct addition, switch or no switch, so it changes with the listing: the design record or fix record names the test or data file and the lines added, and no existing expectation is removed or altered.

1. **Applies to.** Every test file that came from Apache Cassandra: a test class, a test configuration file or a test data file. A test of the project sets the configuration it needs in its own class. A complete listing is for example the help text of a nodetool command that a test compares, the table options that `DescribeStatementTest.tableParametersCql` lists, the class list of `DatabaseDescriptorRefTest`, or a golden file. A fix record that plans a change to a stock test names each existing test method it changes and says what each asserts after the fix. New test methods need no entry. The maintainers approve that list when they merge the fix record. The reviewer checks that the code branch changed those methods and no other existing ones: a changed existing test method the fix record does not name is a blocker.
2. **Edge.** The fourth way covers any other change to a stock test, such as an existing line of a pinned listing that must be altered or removed. The maintainers approve it case by case: an accepted decision record names the file and the issue allowed to change it, with a written explanation of why the change to the test is needed. An approval with no explanation does not count. What may change inside the file is what the record says in words: the reviewer holds the change against them, and the maintainers at the merge.
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

**A feature has a switch when something needs it to be turned off.** A behaviour-changing feature always has a feature switch. So does a feature built in more than one milestone, whatever its class: being reachable before it is finished is a risk that needs it turned off. So does a feature that sends, gossips, streams or commits anything a node without it cannot read: it is not used until every node has it. Any other purely additive feature has a switch only when something needs it to be turned off: a requirement, a decision of the maintainers, a rule of these pages, or a named risk such as load on a shared path. Otherwise its design says in one line why it needs none. How a switch is set is the design's choice.

1. **Applies to.** Every fork feature. For example a switch is a node setting with a runtime command, or an option on the schema object that owns the data.
2. **Edge.** Work with nothing to turn off, such as documentation, packaging or a build change, has no switch. A feature that is held back until every node has it ships off, also when it is purely additive. It uses one of two ways, and its design says which and why. The ordinary way is the operator's: the feature ships off, the operator upgrades every node, turns the feature on with a runtime command and then sets it in the configuration file so that a restart keeps it. The release's steps say that order, and that the feature is turned off on every node before the first node moves back. The other way is an automatic gate on what each node reports, used where the design shows that the operator's switch alone is not safe enough for that feature. Such a feature never falls back in silence to an older behaviour: [PRINCIPLE-028](#principle-028).
3. **See.** [branching-and-review.md](branching-and-review.md#feature-switches-and-defaults).

### PRINCIPLE-017

**A purely additive feature is on by default, a behaviour-changing feature is off.** A purely additive feature is reachable only through something stock Apache Cassandra does not have. It is on by default: its switch, where it has one, ships on, and an operator turns off what they do not want. A behaviour-changing feature changes what an application sees from something stock Apache Cassandra already does: results, errors, warnings or the bytes on the wire. Its default MUST be off on every line.

1. **Applies to.** Every fork feature and each of its switches. The feature spec states the class of each, with the reason, and a maintainer approves the class with the spec. The default of a switch of the project is its default in the code. The shipped configuration file states the same value, and a test loads the shipped file and fails where the two differ. So a cluster switched from Apache Cassandra and a fresh cluster behave the same: an additive feature is on for a cluster the moment it switches, and the release notes say so. A stock setting the project ships with another value is in the file only, see [PRINCIPLE-007](#principle-007).
2. **Edge.** A purely additive feature that is finished after its line's first release has the edge of [PRINCIPLE-018](#principle-018). A feature that is held back until every node has it has the edge of [PRINCIPLE-016](#principle-016).
3. **See.** [DEC-GOV-0001](../decisions/DEC-GOV-0001-what-stays-as-apache-cassandra-has-it.md). [branching-and-review.md](branching-and-review.md#feature-switches-and-defaults), [release.md](release.md#what-a-release-may-contain).

### PRINCIPLE-018

**An upgrade within a line changes a running cluster only through a fix or an import.** An upgrade within a line changes what a running cluster does only through a fix, a security fix or an import from Apache Cassandra, each named in the release notes. A feature's default does not change within a line. A new feature that is purely additive arrives switched on, unless it does work without being asked or adds anything nodes share, in which case it arrives off on that line. Within a line, the values the shipped configuration file holds change only for a fix, a security fix or an import from Apache Cassandra.

1. **Applies to.** Every release of a line. What a shipped name and a configuration file keep across those releases is [PRINCIPLE-082](#principle-082) and [PRINCIPLE-083](#principle-083).
2. **Edge.** A purely additive feature is on by default on every line, also when it is finished after a line's first release. Such a feature ships off by default on that line when it does work without being asked, such as a background task, a cache it fills or a pool it starts, or when it adds anything nodes share, such as a schema object, a message between nodes or a file that is streamed. Its design says which it is. It is on by default from the next new line. An import that changes an on-disk version is named as such in the release notes, with the oldest release of the line a cluster can still roll back to.
3. **See.** [branching-and-review.md](branching-and-review.md#feature-switches-and-defaults), [release.md](release.md#what-a-release-may-contain), [upstream.md](upstream.md#configuration-changes).

### PRINCIPLE-019

**With a feature off, stock behaviour is unchanged, and only schema objects that already exist keep working.** With a feature off, the feature MUST change nothing that stock Apache Cassandra does. Three things hold, as they apply, and the tests of the feature's off state prove them. Stock behaviour is unchanged, always. Each way a user or an operator can invoke the feature is refused with an error that names the switch, except the use of a schema object that already exists, which the Edge keeps. A feature with no such way in does nothing while off: its background work does not run, and no file, metric or other state of the feature appears, apart from what the Edge names.

1. **Applies to.** Every feature that has a switch. For example a new statement is refused with an error that names the switch, and a scheduled background task with its switch off starts no thread, registers no metric and writes no file. While off, a feature writes no new files. A feature that is switched off starts no threads, does no work and sets aside no memory for itself. For a feature whose objects live in the schema, this holds for new objects: an object that already exists is kept and served on every node, as the Edge says, and a node with the switch off does the work of keeping it. A class of the project that an option of Apache Cassandra can name is a way in too, see [PRINCIPLE-042](#principle-042).
2. **Edge.** What Apache Cassandra builds once at startup exists while the feature is off and holds nothing: a virtual table, a metric group table or the directory of a table defined in code. A read of a virtual table of the feature is a way in, so while the feature is off it is refused with the error that names the switch. A stock surface that lists what the node holds, such as the settings virtual table, still lists the feature's settings, see [PRINCIPLE-002](#principle-002). For a feature whose objects live in the schema, off on a node means that the node accepts no statement that creates or alters such an object. An object that already exists keeps working on every node, and the design says how the feature is removed. Where a node setting is read is [PRINCIPLE-024](#principle-024).
3. **See.** [branching-and-review.md](branching-and-review.md#feature-switches-and-defaults), [testing.md](testing.md#scenarios).

### PRINCIPLE-020

**Every merged item keeps the line releasable.** Every merged item keeps its line releasable. A feature built in more than one milestone always has a switch, see [PRINCIPLE-016](#principle-016). Until the feature passes its final milestone gate the switch refuses to turn on, whatever its default, and shipped code has no way round the refusal. With every fork feature off, a line behaves as stock, and the parity suite proves it once it exists.

1. **Applies to.** Every line, and every feature that is built over several items. A feature with no switch that is built over several items merges no item that makes unfinished work reachable: where an item would, that is a risk that needs a switch, see [PRINCIPLE-016](#principle-016). A feature with no switch counts as off when nothing uses it.
2. **Edge.** The fixes to stock code and the differences in what operators see that the delta register lists.
3. **See.** [branching-and-review.md](branching-and-review.md#feature-switches-and-defaults), [additive.md](additive.md#milestone-gates), [testing.md](testing.md#policy).

## Settings and operator controls

### PRINCIPLE-021

**A setting that depends on the data belongs to the schema object that owns the data.** Behaviour that depends on the data is set on the schema object that owns the data, not by one global setting. A configured default applies when the object is created: the node that receives the statement resolves it, and it is stored with the object. A change to the object changes the value. A configured maximum bounds what a node accepts, not what it already holds. Where a node setting is read is [PRINCIPLE-024](#principle-024).

1. **Applies to.** Every limit or behaviour whose right value depends on the data. For example a size limit of an index is an option of the index, and a threshold of a compaction strategy of the project is an option in the table's `compaction` map, as the options of Apache Cassandra's own strategies are. Apache Cassandra has no statement that alters an index, so a design that puts a setting on an index says how the value is changed.
2. **Edge.** A design that keeps such a setting global only states the reason, and the maintainers approve it with the design.
3. **See.** [quality-requirements.md](quality-requirements.md#data-dependent-settings-belong-to-the-schema-object).

### PRINCIPLE-022

**A lever over several schema objects has three modes.** A lever that can apply to several schema objects has three mutually exclusive modes. Global: it applies to all of them. Include: it applies only to the listed ones. Exclude: it applies to all but the listed ones. There are no layered overrides by keyspace, table and index.

1. **Applies to.** A lever that cannot live on the schema object itself, see [PRINCIPLE-021](#principle-021). For example a rate limit on a background task that applies to all tables, only to the listed tables, or to all but the listed tables.
2. **Edge.** None. This differs from the audit log options of Apache Cassandra, where both lists may be set and exclude wins. The difference is deliberate: with one mode in force, an operator reads one list to know what the lever applies to.
3. **See.** [quality-requirements.md](quality-requirements.md#data-dependent-settings-belong-to-the-schema-object).

### PRINCIPLE-023

**A runtime command changes the running value only.** A runtime command, such as a nodetool toggle, changes the value in memory only, on the node it is sent to. The node's configuration at startup holds the starting value: the file, an override the operator gave at startup, or the default in the code. There is no separate persistence of runtime changes, and a restart returns to the configured value.

1. **Applies to.** Every operator control that can change on a running node.
2. **Edge.** An option on a schema object is not a runtime toggle: it changes through the schema.
3. **See.** [quality-requirements.md](quality-requirements.md#a-runtime-command-changes-the-running-value-only).

### PRINCIPLE-024

**Only an operator control may differ from node to node.** A value may differ from node to node only for an operator control: a kill switch, a limit, a fallback switch or another lever set by configuration or by a runtime command. The design says what a client sees while nodes differ. For a control that refuses work that is a refusal, never a wrong or partial result, and the refusal names its control as [PRINCIPLE-025](#principle-025) says. Anything that defines what a statement means or which rows it returns is never per node: it lives in the schema. A node setting, whether a switch, a default or a maximum, is read only by the node that receives the statement from the client, never where a committed schema change is applied.

1. **Applies to.** Every setting a feature adds. For example an operator lowers a limit on one loaded node. A statement that node coordinates is refused with a client error that names the limit. A request that node serves as a replica is refused there, and the client sees a request failure only where the request cannot meet its consistency level from the other replicas. A time to live that decides which rows a read returns is an option of the table, the same on every node.
2. **Edge.** A behaviour-changing feature with no schema object can have its switch only as a node setting. Its design says what a client sees while nodes differ, and the release's steps say how the switch is set on every node.
3. **See.** [quality-requirements.md](quality-requirements.md#a-runtime-command-changes-the-running-value-only).

### PRINCIPLE-025

**A refusal names its control.** A refusal names what the user or operator can change to lift it, where there is such a thing. A refusal with nothing to change says why the operation is refused.

1. **Applies to.** Every refusal the project adds. For example a statement refused because a feature is off names the feature switch, a statement refused because a limit is reached names the setting that holds the limit, and a statement refused for want of a permission says which permission is missing.
2. **Edge.** The error that names the control is promised on a coordinator. A refusal on a replica keeps the shape Apache Cassandra gives it: it reaches the client as a request failure with a reason code, and the control is named in a metric, a trace line and a rate limited log line on the replica.
3. **See.** [quality-requirements.md](quality-requirements.md#a-refusal-names-its-control).

### PRINCIPLE-026

**The project's settings live in its own configuration file.** The project ships its own configuration file, `conf/cassandra_chronitondb.yaml`, which carries its own settings and values. The values live in that file. The definition of a setting is a field reachable from the stock configuration class, where an import can conflict. Apache Cassandra's `conf/cassandra.yaml` and `conf/cassandra_latest.yaml` stay untouched. A node switched from Apache Cassandra keeps the operator's own file.

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
2. **Edge.** A fallback that changes none of the three, such as a node that speaks an older message version to an older peer, is not under this principle. Choosing between plans that return the same rows, by an estimate, is not a fallback and is not under this principle. A switch to a path whose cost the operator cannot predict is. What Apache Cassandra does automatically to a request the feature produced, such as a hint, a batchlog replay, a dropped mutation, a speculative retry or a read repair, is stock behaviour and is not under this principle.
3. **See.** [quality-requirements.md](quality-requirements.md#automatic-fallbacks-are-opt-in-and-counted).

### PRINCIPLE-029

**A fallback is allowed on the schema object, and the node control wins.** Whether a schema object allows a fallback is an option on that object, off by default. The object is the index, table or other schema object the fallback serves. Each node also has an operator control that turns every fallback off on that node. The node control always wins: the option on the object never turns on what the node control has turned off.

1. **Applies to.** Every fallback under [PRINCIPLE-028](#principle-028). For example an index that may fall back to a scan, or a table that may take a full rebuild in place of an incremental one.
2. **Edge.** None.
3. **See.** [quality-requirements.md](quality-requirements.md#automatic-fallbacks-are-opt-in-and-counted).

### PRINCIPLE-030

**An answer is complete, marked as partial, or an error.** Missing data is as bad as wrong data. Every answer a fork feature gives MUST be complete at the requested consistency level, or an error. A confirmed correctness fault in fork code, or on a path a fork feature serves, is fixed, never only documented.

1. **Applies to.** Every result a fork feature returns, to a client or to an operator. For example a read that cannot reach enough replicas errors, and a tool listing that could not read one node says so and never prints a short list as if it were complete.
2. **Edge.** A partial answer is allowed only where it is deliberate, opt in and marked in the response, see [PRINCIPLE-031](#principle-031). A correctness gap in stock outside such a path follows [PRINCIPLE-014](#principle-014). For a write, an error means the outcome is unknown, as in Apache Cassandra.
3. **See.** [classification.md](classification.md#risk).

### PRINCIPLE-031

**A response that is partial or cut short says so itself.** When a response must tell the client something about itself, such as that it is partial or that a limit cut it short, it says so in the response, in the idiom of its surface. For example a CQL result carries a boolean result column in the style of the `[applied]` column of a lightweight transaction, present on every result of that statement shape while the option that can produce the condition is set. A client warning MAY go with it. The marking reaches every client the same way and never depends on what a driver chooses to read.

1. **Applies to.** Every response of a fork feature that can be partial, cut short or otherwise marked. The design proves by test that a prepared statement decodes the same on every node. A response on another surface, such as the output of a tool, marks the condition in that surface's own idiom.
2. **Edge.** None.
3. **See.** [PRINCIPLE-060](#principle-060).

### PRINCIPLE-032

**The user states the intent, the system does not guess it.** Where syntax or an option would otherwise guess a behaviour for the user, the user states the intent. A statement that cannot tell which of two behaviours is meant fails with an error instead of choosing. A default stays where an established idiom supplies one.

1. **Applies to.** New syntax, options and commands. For example a schema change that would need a rebuild asks the user to say so, and a command that could mean one table or all of them is refused until the user names which.
2. **Edge.** None.
3. **See.** [PRINCIPLE-060](#principle-060).

## Observability and logging

### PRINCIPLE-033

**Observability is a gate item, not an afterthought.** Every outcome has a counter. Every limit reports its limit, the amount used and the number of times it tripped. Each decision a feature makes on a request path that changes the work done, and each fallback, has a trace line. A feature's observability is part of its design and is checked with it.

1. **Applies to.** Every fork feature, in proportion to the runtime behaviour it adds. For example a background job shows what it started, completed and failed, and a limiter shows its limit, its use and its trips.
2. **Edge.** A change that adds no runtime behaviour says so in one line, and a change with no traced request path gives the reason in its tracing test list. The maintainers accept the line by merging the record.
3. **See.** [quality-requirements.md](quality-requirements.md#observability), [templates/design-record.md](templates/design-record.md#8-observability).

### PRINCIPLE-034

**Operator actions and node states are logged.** Every runtime change of a setting logs the old and the new value at INFO. Startup logs the effective state of each fork switch. A state in which the node runs degraded is logged at WARN, without flooding.

1. **Applies to.** Every setting, switch and degraded state a feature adds.
2. **Edge.** The change of a setting that holds a secret is logged without either value. Such a setting is logged without its value at startup too, and its value is hidden on every surface that prints settings, such as the startup line and the settings virtual table.
3. **See.** [quality-requirements.md](quality-requirements.md#observability).

### PRINCIPLE-035

**No log line the project writes carries user data or a secret.** Code the project writes never puts user data or a secret in a log line, at any log level. User data means partition keys, clustering and column values, bind values, query literals, query text that carries them, and any other value or term a user supplied in a statement. A log line names what it is about by schema object and by a value that identifies no user. A trace line the project's code writes follows the same rule and carries no user data. Diagnosis that needs the data itself goes through a path with its own access control, as the design chooses.

1. **Applies to.** Every log line and trace line the project's own code writes. For example a line names the keyspace and table, a token under a hashing partitioner, a count, a size or a duration. A line of the project that logs a stock exception or a stock object logs its class and the schema object, never its message or its string form, unless the design shows that form holds no user data. A virtual table in `system_views` is a path with its own access control: reading it needs a grant on the table or its keyspace. The tables of `system_virtual_schema` are not, since Apache Cassandra lets every role read them. Tracing is not such a path: Apache Cassandra lets every authenticated role read the trace tables.
2. **Edge.** Log lines that Apache Cassandra writes follow [PRINCIPLE-008](#principle-008). A stock log line that prints a statement prints a value given to a feature of the project as it prints every other value, and that is left as it is. The design names in one line the stock lines its input reaches.
3. **See.** [quality-requirements.md](quality-requirements.md#observability).

### PRINCIPLE-036

**Events per request or per element are counted, not logged one by one.** An event that happens per request or per element, such as a row, a partition, a file or a message, is not logged one by one. Its detail goes to metrics and tracing. Logs carry operator actions and periodic summaries with counts, limited in rate.

1. **Applies to.** Every path of fork code that runs per request or per element. For example the refusals of a query limit, the rows a compaction task rejected and the files a stream skipped are each counted, with at most one summary line in a period for each schema object and reason.
2. **Edge.** The start, the end and the failure of a background task are not events per element, as long as the rate of tasks is bounded by a setting or by the schema and not by the request rate. What happens to each row, partition or file inside the task is counted and summed up in the end line. An unexpected server error MAY be logged at ERROR for each failing request. Such an error is a defect, not an expected failure such as a bad statement, a timeout, an unavailable or a refused permission. Each use is assessed in the design, which says why the error is unexpected, what bounds how often it can fire and what the log holds if it fires on every request, and the reviewer checks that assessment. On a request path where Apache Cassandra's own request handling logs an exception that escapes, the use is the escape: the design makes every expected failure an exception type that Apache Cassandra returns to the client without logging. The line carries no user data, see [PRINCIPLE-035](#principle-035).
3. **See.** [quality-requirements.md](quality-requirements.md#observability).

### PRINCIPLE-037

**A signal is released with the object that owns it.** Every metric, MBean and virtual table row a feature creates is released when its object is dropped. After the drop nothing of it stays registered, and a test proves it.

1. **Applies to.** Every signal a feature registers. For example the metrics of an index go with the index, its table and its keyspace, and the metrics of a pool go when the pool shuts down.
2. **Edge.** None.
3. **See.** [quality-requirements.md](quality-requirements.md#observability).

### PRINCIPLE-039

**A limit reaches the client, and state reaches the operator.** A limit that changes results or rejects work reaches the client and is counted. State that an operator would otherwise search the logs for is exposed where it can be queried. Such a surface holds operational state, not user data.

1. **Applies to.** Every limit and every operational state a feature adds. For example a virtual table row shows the state of a build. A surface for operators follows the permission scheme Apache Cassandra already has for that kind of surface, see [PRINCIPLE-045](#principle-045).
2. **Edge.** A surface carries user data only where the design chose it as the path with its own access control for diagnosis, see [PRINCIPLE-035](#principle-035). Such a surface sits where Apache Cassandra asks for a grant of its own, such as a virtual table in `system_views`.
3. **See.** [templates/design-record.md](templates/design-record.md#8-observability).

## Security

### PRINCIPLE-041

**Every new entry point has a threat model.** Every new entry point of a feature is checked with STRIDE: spoofing, tampering, repudiation, information disclosure, denial of service and elevation of privilege. Each mitigation is a requirement. An entry point is syntax, a setting, a command, a file or the network.

1. **Applies to.** Every feature and every one-item change.
2. **Edge.** A change with no new entry point says so, with the reason.
3. **See.** [standards.md](standards.md#requirements-and-architecture), [templates/feature-spec.md](templates/feature-spec.md#6-threat-model).

### PRINCIPLE-042

**In what the project adds, a value a client supplies never picks code or a resource.** In the project's own lookups, a name that a client supplies never picks code to load unless it is on an allow list. The project's own list is fixed in the code, proposed by the design with a reason for each entry, and approved by the maintainers in a decision record. A new entry is a new decision. The allow list governs the project's own lookups, and an option of Apache Cassandra that takes a class name keeps its behaviour. A class of the project that such an option can reach refuses by itself when its feature is off, with the error that names the switch. A value a client can set in something the project adds names no class, file, address, command or other resource of the node: names resolve against a fixed set.

1. **Applies to.** Every option, argument and name in a statement that a feature accepts. For example the name of a codec, an option of a compaction strategy, or a file name in a statement. A class of the project that an option of Apache Cassandra can reach refuses where the statement that names it is received, see [PRINCIPLE-024](#principle-024).
2. **Edge.** An operator's extension of the allow list in a node's configuration, for code the operator has placed on the node, is not ruled out: it is designed and decided when a feature needs it.
3. **See.** [conventions.md](conventions.md#code-layout).

### PRINCIPLE-043

**Every untrusted input is bounded before the work.** Every untrusted input has a bound that is checked before the expensive step it protects. Untrusted input is input from a client. A peer is trusted as in Apache Cassandra, behind internode authentication and encryption, and the project's serializers are not asked to bound what they read from a peer. Over a bound the request fails with a client error that names the input, the object, the count and the limit. It never fails with a server error, a stack trace or an internal path.

1. **Applies to.** Everything a feature parses or takes from a client. For example a length is checked before a parse, the size of a pattern before it is compiled, a count during a walk, and a number of rows before they are held in memory.
2. **Edge.** The client error that names the bound is promised on a coordinator. A bound checked on a replica has the edge of [PRINCIPLE-025](#principle-025).
3. **See.** [templates/design-record.md](templates/design-record.md#10-threat-model-and-security).

### PRINCIPLE-045

**Nothing lets a role learn about data it cannot read.** Nothing the project adds lets a role learn about data it could not `SELECT`, or could `SELECT` only masked: not through results, counts, derived values such as a rank or an estimate, error text, or timing that an attacker can measure in practice.

1. **Applies to.** Every result, error and signal a feature gives a client.
2. **Edge.** This principle is about what the statements a feature adds or changes return to a role from user tables: results, counts, derived values, errors and timing. A read of a surface for operators, such as a virtual table, a metric or JMX, follows the permission scheme Apache Cassandra already has for that kind of surface. The project adds no scheme of its own there and filters nothing by the reader's `SELECT` permission. Counts, sizes and states per schema object on such a surface are operational data. User data appears there only as the edge of [PRINCIPLE-039](#principle-039) allows. Where a statement checks access is [PRINCIPLE-090](#principle-090).
3. **See.** [templates/design-record.md](templates/design-record.md#10-threat-model-and-security).

### PRINCIPLE-046

**A limit the project adds binds every client.** A guardrail or limit the project adds binds every client, superusers and clusters without authentication included. Apache Cassandra's own guardrails keep their own rules.

1. **Applies to.** Every guardrail and limit a fork feature adds. Such a limit follows Apache Cassandra's guardrails in what the client sees: a warn value and a fail value, a warning and then a failure in the guardrail's message form, and values an operator can change at runtime. It is built from the project's own classes, so that it binds every client, is counted and logs no line for each violation.
2. **Edge.** None. This is a deliberate difference from how stock guardrails treat superusers and every client of a cluster without authentication, made for security, as [PRINCIPLE-059](#principle-059) asks it to be stated.
3. **See.** [templates/design-record.md](templates/design-record.md#10-threat-model-and-security).

### PRINCIPLE-047

**Every copy of user data has a lifetime.** A new copy of user data, or of anything derived from it, is listed in the design with its lifetime and what deletes it. A copy the project makes lives no longer than the last copy Apache Cassandra keeps of its source, and where a design can keep less, such as a hash or a prefix in place of the value, the smaller copy is the default. Where Apache Cassandra keeps the source, in a snapshot, a backup, an sstable not yet compacted, the commit log or hints, the project's copy may stay with it. Data kept per sstable is purged by the compaction that purges its source. Every new kind of file that stores values has a test that writes a value, deletes it, runs the stock steps that remove the source and searches the files the feature writes for the value and its derived forms. The design lists the stock copies that also hold the value.

1. **Applies to.** Every file, cache and structure a feature adds that holds user data. For example data kept per sstable is written by an observer of the sstable writer, so that every rewrite rebuilds it: flush, compaction, cleanup, scrub, upgrade, anticompaction and a stream that carries rows. Its file carries the sstable's file name prefix in the sstable's directory, so it is deleted with the sstable. It is registered in the sstable's component list, so snapshots and whole file streaming carry it. Derived data, such as hashed, truncated or normalised values, is treated as its source is.
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

### PRINCIPLE-090

**Access is checked in the statement's authorise step.** Whatever access a statement of the project needs is checked in the statement's authorise step. That is the step in which Apache Cassandra's own statements check access, against Apache Cassandra's permissions and resources. The same holds for anything the project adds to an existing statement. Before that step has passed, the statement reads no stored data and does no work that depends on stored data, and no error says anything about stored data.

1. **Applies to.** Every statement a feature adds, and every clause, option or function it adds to an existing statement. For example a new schema statement checks there the permission on the object it changes. A new clause of a read is covered by the check the read already makes on its table, and any further permission the clause needs is checked in the same step.
2. **Edge.** This principle says where the check sits. What a role may learn is [PRINCIPLE-045](#principle-045), and this principle asks for no permission beyond that. A surface for operators that is not a statement, such as a command or JMX, follows the permission scheme Apache Cassandra has for it, as the edge of [PRINCIPLE-045](#principle-045) says. A check that Apache Cassandra itself makes at another point, for a statement of the same kind, stays where Apache Cassandra has it. Apache Cassandra prepares a statement before it authorises it, so an error raised while a statement is prepared can reach a role with no permission. At that point the project's code reads no stored data and says no more about the schema than Apache Cassandra's own statements say there.
3. **See.** [PRINCIPLE-041](#principle-041), [templates/design-record.md](templates/design-record.md#10-threat-model-and-security).

## Performance

### PRINCIPLE-050

**Performance and availability come first on a request path.** On a request path, or a background path that competes with requests, performance and availability come first and win over simplicity. The design is the fastest correct design known, and the one that keeps the node available. Speed is argued by mechanism, the work the design does per request and why that is less, and proved by benchmarks that compare the change with the code before it and with stock, with the feature off and on. No numeric target is demanded up front, and no design waits for one. Complexity added for speed or availability stays in proportion to what the path needs, and the design says what each such addition buys.

1. **Applies to.** Every design. For example compaction, streaming and repair are background paths that compete with requests. Each design record names the request paths the change touches, the expected cost with its mechanism, and the benchmarks that prove it. A benchmark of a path Apache Cassandra also has runs on the stock build too. A benchmark of code only the project has compares with the code before it and names the stock operation it stands beside.
2. **Edge.** Off those paths the simplest sufficient design stands, see [PRINCIPLE-054](#principle-054). A design that touches no such path says so in one line.
3. **See.** [quality-requirements.md](quality-requirements.md#performance-first), [testing.md](testing.md#benchmarks).

### PRINCIPLE-051

**A feature that adds work to a shared path cannot starve the rest of the node.** A fork feature that adds work to a shared path cannot starve the rest of the node. Its design names what bounds its threads, its memory and its work per operation, how it sheds load, how long it may run, and how an operator turns it off, on every node role that does the work. Each bound can be set by an operator at the scope the design chose and is visible in a metric. Working out what level of isolation a feature needs is part of its architecture: it is investigated and argued for each feature, and the design states the result with its reasons.

1. **Applies to.** Every fork feature. For example a search feature needs isolation, such as pools, limits, shedding, timeouts and budgets of its own, and a nodetool command or an uptime view does not.
2. **Edge.** A feature that adds no work to a shared path says so in one line. Where the work runs inside a stage, a pool or a limiter of Apache Cassandra, the feature has no bound of its own there: the design names the stock bound it shares, says what it adds to each operation, and shows by benchmark what that does to stock work in the same pool.
3. **See.** [quality-requirements.md](quality-requirements.md#isolation-levers), [templates/design-record.md](templates/design-record.md#isolation-levers).

### PRINCIPLE-052

**The stock path is guarded.** With a fork feature off, the stock path it touches shows no change in what an application sees. A fork feature SHOULD NOT slow operations that do not use it. That is measured by benchmark against stock, with the feature off and with it on but unused, and the design names those runs. A measured slowdown does not block by a fixed threshold. It is reported to the maintainers with its numbers and what causes it, and they decide whether to accept it, have it fixed or put it behind a switch. A speed up needs no switch.

1. **Applies to.** Every change that touches a path stock work runs on.
2. **Edge.** None.
3. **See.** [testing.md](testing.md#benchmarks), [templates/design-record.md](templates/design-record.md#apache-cassandra-guard).

### PRINCIPLE-053

**A change is gated on counted values, never on timing.** The performance checks of a pull request block only on counted values and on benchmarks that fail to run. They never block on timing. A performance claim rests on paired runs, and an absolute timing number comes only from pinned or dedicated hardware.

1. **Applies to.** Every benchmark a design names. For example allocations per operation, work counters, bytes written per compaction and bytes written per byte of input are counted values.
2. **Edge.** Once dedicated benchmark hardware is in place, a change point in the tracked timings blocks the next release. A slowdown of operations that do not use a feature blocks by no fixed threshold, in a pull request check or at a release: the maintainers decide it, see [PRINCIPLE-052](#principle-052).
3. **See.** [testing.md](testing.md#benchmarks).

## Simplicity of design

### PRINCIPLE-054

**The simplest sufficient design.** A design is the one with the least to understand, build, test, operate and recover that meets the requirements, the decisions of the maintainers and the rules of these pages. The burden of proof is on each addition, never on the simpler design. The search starts from no change, then an existing Apache Cassandra mechanism, then an existing mechanism of the project, then something new.

1. **Applies to.** Every feature spec, design record and fix record. For example a value an operator needs is a column in an existing virtual table before a new command, and a value that a stock mechanism already computes, such as a count a stock metric holds, is read from it before a new structure keeps it.
2. **Edge.** The principle is a strong default and no ban: complexity that a requirement, a decision, a rule or a named risk needs is kept. On a request path, or a background path that competes with requests, performance and availability come first: speed is argued by mechanism and proved by comparing benchmarks, no numeric target is demanded up front, and complexity stays in proportion, see [PRINCIPLE-050](#principle-050). Off those paths the simplest sufficient design stands. See [PRINCIPLE-056](#principle-056) for what simple never means.
3. **See.** [PRINCIPLE-055](#principle-055).

### PRINCIPLE-055

**An addition names what needs it.** An addition is anything that adds a state, a code path, a setting, a dependency, a stored or sent format, or a step for an operator. For each one the document names what needs it, a requirement, a decision of the maintainers, a rule of these pages or a named risk, and why the simpler design does not meet it. An addition with no such line is left out, or left to a later record with the condition that would bring it back.

1. **Applies to.** Every addition in a design, and every review finding that asks for one. Simplifying code that already works is itself a change with a cost and a risk, and needs the same line.
2. **Edge.** Where the need rests on something not measured or not known, the document says so, marks the addition provisional and names the check that would settle it. No figure is invented to justify it. An addition for speed or availability on a path [PRINCIPLE-050](#principle-050) covers is justified by its mechanism and a comparing benchmark, and is not provisional for want of a numeric target.
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
2. **Edge.** A choice with no effect a user or an operator sees needs no record. Nor does a detail of form where Apache Cassandra's convention for that kind of thing leaves no other choice, such as the unit of a new metric or the error class that invalid CQL gets. Which rows, errors, refusals, defaults, limits and outputs a feature has is never such a detail, even where it follows a convention: what Apache Cassandra does is evidence, and never by itself the reason.
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

1. **Applies to.** Every fork feature. One that runs across nodes is tested at replication factor 1 and at replication factor 3 on the same data, and across two data centres when its behaviour involves a data centre aware consistency level or replication strategy. A warning that differs between the two runs for one of the stock reasons the edge names is not a fault.
2. **Edge.** Where Apache Cassandra itself depends on topology, that stays as it is and the feature matches it exactly. Apache Cassandra couples more than availability to topology: whether a filtering query needs reconciliation, the guardrail and the warning that follow from it, the plan, and which replica's warnings reach the client.
3. **See.** [quality-requirements.md](quality-requirements.md#a-feature-adds-no-dependence-on-topology), [testing.md](testing.md#policy).

### PRINCIPLE-062

**A change to a shared surface states and proves its upgrade, its rollback and its mixed-version behaviour.** A feature states its on-disk format changes with their version markers, its behaviour in a mixed-version cluster during a rolling upgrade, its upgrade path with prerequisites, its rollback path and its runbook entries. A milestone that introduces an on-disk format change has upgrade and rollback tests among its exit criteria. A newer line reads every data file an older line writes, and exchanges messages with it, once Apache Cassandra has released the newer line's major version. Before that the newer line has no path from the older one, see [PRINCIPLE-003](#principle-003). A file that only speeds a restart, such as a saved cache, may be discarded instead, and the design says so. Streams and repair between two lines follow Apache Cassandra: they run only between nodes on the same messaging version, and the runbook says so.

1. **Applies to.** Every change to a surface nodes or versions share: a file on disk, the schema, a message between nodes, a setting. For example a new component beside an sstable, or a new gossip state. What a configuration file keeps across the releases of a line, what a stored form records and what a reader does with a value it does not recognise are [PRINCIPLE-083](#principle-083), [PRINCIPLE-084](#principle-084) and [PRINCIPLE-085](#principle-085).
2. **Edge.** A feature with no format, schema or protocol change says so, and still states its mixed-version and rollback behaviour where its class requires the section.
3. **See.** [additive.md](additive.md#level-1-the-feature-spec), [testing.md](testing.md#upgrade-and-rollback-tests), [templates/feature-spec.md](templates/feature-spec.md#7-compatibility).

### PRINCIPLE-083

**A configuration file that works on one release of a line starts every later release of that line.** A configuration file that a node starts with on one release of a line starts every later release of the same line, unchanged, and each setting in it keeps its meaning. No release within a line needs a key that the release before it did not have: a new setting has a default in the code. No release within a line stops reading a key or a value that an earlier release of the line accepted.

1. **Applies to.** Every setting the project adds or changes, in every file a node reads at start, and every release of a line. For example a setting added within a line takes its default when the file leaves it out, a renamed setting still loads under its old key as [PRINCIPLE-082](#principle-082) says, and a setting that no longer does anything still loads and says so.
2. **Edge.** A fix, a security fix or an import from Apache Cassandra MAY have to refuse a key or a value that an earlier release accepted, or add to what a node checks at start. The release notes then name the key and say what the operator sets, as [PRINCIPLE-018](#principle-018) asks. For a fix of the project's own the maintainers decide it by merging the fix record. The rule runs forward only. A file that holds a key a later release added does not start an earlier release, so the rollback path of [PRINCIPLE-062](#principle-062) says which keys are removed first. Moving to the next line follows that line's upgrade runbook, once Apache Cassandra has released that line's major version. Moving back to Apache Cassandra follows the release's steps, which remove the project's keys: [PRINCIPLE-003](#principle-003).
3. **See.** [release.md](release.md#the-configuration-file), [upstream.md](upstream.md#configuration-changes).

### PRINCIPLE-084

**A stored form records the version that wrote it.** Every form the project defines and stores records the version that wrote it, from the first release that writes the form. A reader decides how to read from that record, never from the version of the code that is reading. The version is the project's own. It stands beside the versions Apache Cassandra owns, which stay as they are: [PRINCIPLE-006](#principle-006).

1. **Applies to.** Every form the project defines that outlives the process that wrote it. For example a file beside an sstable, a file in which a background task keeps its progress, bytes the project serialises into a column of a table, and a payload that is kept for later delivery. A form with one version so far records it too: a form that starts without the record cannot gain it later without a guess.
2. **Edge.** A value whose form Apache Cassandra defines and types, such as a named option of a schema object or a column of a declared type, needs no version of its own: its meaning does not change under the same name, see [PRINCIPLE-058](#principle-058). A form that is sent and never stored says in its design how the receiver knows which version wrote it. What a reader does with a version it does not recognise is [PRINCIPLE-085](#principle-085).
3. **See.** [PRINCIPLE-062](#principle-062), [templates/feature-spec.md](templates/feature-spec.md#7-compatibility).

### PRINCIPLE-085

**A reader says what it does with a value it does not recognise.** Code of the project that reads a stored or sent value has a stated answer for a value it does not recognise, such as a version, a code, a name or a field that another release wrote. The reader either passes over the value in a way that leaves the rest of what it reads correct, or refuses the work with an error that names what it met. It never reads such a value as one it knows, other than a named neutral value the Edge allows, and it never guesses.

1. **Applies to.** Every form the project defines or adds to, on disk, in the schema or between nodes, and each reader of it. For example a file whose recorded version is newer than the reader knows, a status code in a message from a newer node, and an option value in the schema that the release of the reading node does not have. The design names each such value and the reader's answer.
2. **Edge.** This is about a value that another release, or a node with other features on, wrote in good order. It is not a check on a hostile sender: a peer is trusted as [PRINCIPLE-043](#principle-043) says, and input from a client is bounded there. Passing over a value is allowed only where the form lets the reader find the end of the value, or where a named neutral value loses nothing the reader needs. A file that only speeds a restart may be discarded instead, as [PRINCIPLE-062](#principle-062) allows. Where the answer is that the node does not start, the design says so, and the upgrade or rollback path names the step that avoids it. A refusal follows [PRINCIPLE-025](#principle-025).
3. **See.** [PRINCIPLE-084](#principle-084). [PRINCIPLE-016](#principle-016) holds a feature back until every node has it.

## Data on disk and writes between nodes

### PRINCIPLE-086

**A file read back after a crash is complete or absent, never half written.** A file the project writes and a node reads back later is, after a crash at any moment of the write, either complete or absent to its reader. A reader never takes a half written file for a complete one. The design says what the node does when the file is absent: rebuild it, start the work again or refuse.

1. **Applies to.** Every file the project's code writes and reads back, in a data directory or elsewhere. For example a file beside an sstable, a file in which a background task keeps its progress, and a saved copy of state held in memory. One way to meet it is to write under a temporary name and rename the finished file. Another is a marker written last, without which the reader treats the file as absent. A file beside an sstable can be written inside the transaction Apache Cassandra uses for the sstable's own files.
2. **Edge.** A file that is appended to, such as a log, is read up to its last complete record, and the design says how the reader finds that record. What an unfinished write leaves behind is removed at the next start or by the next write, so that no partial copy of user data stays: [PRINCIPLE-047](#principle-047). A design whose files are written in more than one step is a candidate for a model under [PRINCIPLE-068](#principle-068).
3. **See.** [PRINCIPLE-087](#principle-087), [quality-requirements.md](quality-requirements.md#the-checklist).

### PRINCIPLE-087

**Disk errors go through Apache Cassandra's error types, so the operator's disk failure policy acts.** The policy an operator set for a failed or corrupt disk acts on the project's files as it acts on Apache Cassandra's own. So code of the project that cannot read or write a file in a data directory, or that finds one corrupt, reports the failure through the error types Apache Cassandra uses for such failures. Such a failure is never caught and only logged.

1. **Applies to.** Every read and write of a file by the project's code in a directory the node's failure policy covers. For example a read of a file beside an sstable on a request path, a write of such a file during compaction, and a background task that writes a file of its own. The request or the task that met the failure fails as it would on a failure in one of Apache Cassandra's files, and never returns a partial answer: [PRINCIPLE-030](#principle-030).
2. **Edge.** A file the node can do without, such as one that only speeds a restart, MAY be discarded and rebuilt when it cannot be read or is corrupt, where the design says so, and each such event is counted. A write that fails is still reported. A file that is absent after a crash is not a disk failure: [PRINCIPLE-086](#principle-086). A tool that runs without a node has no policy to meet and reports the error itself.
3. **See.** [PRINCIPLE-086](#principle-086), [quality-requirements.md](quality-requirements.md#the-checklist).

### PRINCIPLE-088

**A write between nodes may arrive once, twice, late or out of order, and the code handles each.** What a feature does when a write is applied on a node leaves the same end state whether the write arrives once, twice, late or out of order, by any route Apache Cassandra delivers it. The feature's own state follows the data as Apache Cassandra reconciles it, never the order of arrival. The design also says what the feature does for data that arrives as files and never passes the write path.

1. **Applies to.** Every feature that keeps or changes state when a write is applied, and every message of the project that changes state on the node that receives it. For example data a feature derives from each write, and a message that records a step of a background task on another node. The routes are for example the coordinator's request, a retry by the client after an error, a hint delivered hours later, a replay of the batchlog, a replay of the commit log at restart, read repair and a Paxos commit. Streaming, and with it repair, brings data as files, which pass the write path for some tables only. A late write can arrive after the object it was written for was altered or dropped.
2. **Edge.** This is about delivery, not about a hostile sender: a peer is trusted as [PRINCIPLE-043](#principle-043) says. The retries, hints and replays themselves are Apache Cassandra's behaviour and stay as they are: [PRINCIPLE-028](#principle-028). State that must go with a write is carried in the write's own data, so that every route carries it: [PRINCIPLE-006](#principle-006). A feature that changes no state when a write is applied says so in one line.
3. **See.** [PRINCIPLE-030](#principle-030), [PRINCIPLE-068](#principle-068), [testing.md](testing.md#test-levels).

## Testing

### PRINCIPLE-063

**Every requirement has a test that proves it.** Every requirement has at least one test that proves it. A requirement that needs tests at two levels keeps one id and lists both tests. A requirement that states two behaviours is split into two ids.

1. **Applies to.** Every requirement of a feature spec, a design record and a fix record.
2. **Edge.** A requirement that is deliberately not tested has its reason in the item's coverage file, approved with the design record.
3. **See.** [testing.md](testing.md#policy), [templates/ac-coverage.md](templates/ac-coverage.md).

### PRINCIPLE-064

**A fix starts with a test that reproduces the fault.** A fix starts with a test that reproduces the fault. It MUST fail before the fix and pass after it. The test and the fix merge together, so the line never carries a failing test.

1. **Applies to.** Every corrective and emergency change. A fix to stock code keeps its reproducing test in one of Apache Cassandra's own test harnesses, so the test can be offered to Apache Cassandra with the fix.
2. **Edge.** A dependency patch-version update has no reproducing test: the tests that cover every use of the library MUST pass. A fault that no test can reproduce is an exception to this principle: its fix record says why no test can and how the fix is checked instead, names this principle in its `Exceptions` row, and the maintainers decide it by merging the record.
3. **See.** [testing.md](testing.md#policy), [maintenance.md](maintenance.md#corrective-fixing-a-fault).

### PRINCIPLE-065

**A test that existed before a change is not weakened.** A test that existed before a change MUST NOT be weakened. An assertion, an expected value or an error text of a merged test of the project's own changes only when the record that plans the change says which one changes, from what to what, and why the old expectation is no longer right. The reviewer checks each against the record. A changed assertion the record does not name is a blocker. New tests and new assertions are free.

1. **Applies to.** The project's own tests, once merged. Apache Cassandra's test files follow [PRINCIPLE-013](#principle-013).
2. **Edge.** None.
3. **See.** [testing.md](testing.md#policy).

### PRINCIPLE-066

**A test's verdict does not depend on speed or on a retry.** A test's verdict MUST NOT depend on how fast the machine runs. A test that needs time to pass uses a clock the test controls, or waits for a condition with a bound. An assertion is never retried after it fails, except inside a bounded wait for a condition, and a randomised test prints its seed so a run can be repeated.

1. **Applies to.** Every test the project writes. A test of a fork feature runs with the feature on, unless it is about the off state, and one that is skipped without a stated condition counts as a failure.
2. **Edge.** Timed benchmarks follow their own rules, see [PRINCIPLE-053](#principle-053). A retry is for a failure of the test infrastructure only. A test added to a stock test class for a fix to stock follows this rule in its own methods and leaves the existing ones as they are.
3. **See.** [testing.md](testing.md#policy).

### PRINCIPLE-067

**The kind of test proves the claim.** The kind of test is picked from the claim the design makes. A kind that cannot prove the claim does not count, however many of its tests pass. A change runs its tests in every test configuration whose settings the changed code reads.

1. **Applies to.** Every test plan. For example a claim about several nodes needs a distributed test, a claim about an upgrade needs an upgrade test, and a change that touches compaction or an on-disk format runs on both sstable formats.
2. **Edge.** The project's own tests run on the options of the entry condition, since no other setup is supported: [PRINCIPLE-003](#principle-003). A cluster that met the entry condition can still hold sstables in the older format, so a change that touches compaction or an on-disk format also runs on both sstable formats.
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

1. **Applies to.** Every change, in Apache Cassandra's files or in the project's own. The node's data on disk is sstables and their components read from any source, the commit log and its replay, hints, saved caches and any other file the node reads back at startup. Streaming is the sending and receiving of data files between nodes, for repair, bootstrap, replacement, decommission and rebuild. The list of areas is closed: a new area is a change to this principle, which the maintainers decide.
2. **Edge.** The maintainers MAY say that a given change is not Critical. An import from Apache Cassandra is not on the floor merely because Apache Cassandra's own commits touch one of these areas. It is Critical when it changes, or conflicts with, something the project added or edited in such an area, or when the maintainers say so. The rule on findings in imported code applies in full, see [PRINCIPLE-074](#principle-074).
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

**Names are additions, and say what they mean.** A name of Apache Cassandra follows the rule for what it names. A name an application sees, such as a keyword, a column of a result or an error code, changes only behind a feature switch that is off by default: [PRINCIPLE-001](#principle-001). A name an operator sees, such as a metric, an MBean, a virtual table, a setting or a command, stays as stock where that is reasonable, and a difference is recorded: [PRINCIPLE-002](#principle-002). The project's signals and settings live under its own names, and stock metric types gain no new metrics. Those names never contain "cassandra" or "axon", and no key or value contains "stock". A setting that means what an existing setting means in the idiom the design follows SHOULD carry that setting's name, and an option that defers to the node's global setting takes the value `inherit`. Such an option is an operator control under [PRINCIPLE-024](#principle-024) and never decides what a statement returns. Apache Cassandra has no single word for this, so the value is the project's own.

1. **Applies to.** Every new user facing name: yaml keys, nodetool commands, MBeans, metric types, packages and options. What happens to a name of the project's own once a release has shipped it is [PRINCIPLE-082](#principle-082).
2. **Edge.** A name the maintainers fixed in a decision record. A file that stands beside one of Apache Cassandra's files MAY carry that file's name, as the configuration file of [PRINCIPLE-026](#principle-026) does. An object of a kind Apache Cassandra already measures, such as a thread pool, appears under the stock metric type with the project's scope. On a line whose metric registry accepts only the types on its own list, the project's type is added to that list, a hook point with its delta entry. A fix to a defect in stock that needs a new metric on a stock metric type is applied with its fix record, and the metric is recorded as a difference in what operators see, see [PRINCIPLE-004](#principle-004) and [PRINCIPLE-002](#principle-002).
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

### PRINCIPLE-082

**A name the project has shipped is not renamed or removed within a line.** A name of the project's own that a release has shipped is not renamed in place and is not removed within a line. Where a better name is wanted, the new name is added and the old one is kept as an alias: it keeps working with the same meaning, and it says that it is deprecated where its surface can say so. The old name is removed no earlier than the first release of the next line, and the release notes name it.

1. **Applies to.** Every name of the project's own that a user or an operator can write or read, once a release holds it. For example a setting, an option of a schema object and its values, a keyword, a command and its arguments, a metric, an MBean and its operations, and a virtual table and its columns. A renamed setting still loads under its old key, and a renamed metric is still registered under its old name.
2. **Edge.** A name of Apache Cassandra follows [PRINCIPLE-079](#principle-079), and one that Apache Cassandra renames or removes arrives with its import. Where a surface cannot carry two names, such as a column of a result, the shipped name stays for the line. A shipped name that an import from Apache Cassandra takes for something else is a conflict the maintainers decide before the import merges: [PRINCIPLE-074](#principle-074). The new name is chosen as [PRINCIPLE-057](#principle-057) and [PRINCIPLE-079](#principle-079) say. A fix or a security fix that must refuse a shipped name follows the edge of [PRINCIPLE-083](#principle-083), and the release notes name it.
3. **See.** [conventions.md](conventions.md#names), [release.md](release.md#what-a-release-may-contain).
