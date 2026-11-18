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

# Quality requirements

Every one-item design record answers this checklist, and so does every feature spec whose class requires the Quality requirements section, see [classification.md](classification.md). It is organised by the quality characteristics of ISO/IEC 25010. Each line MUST have requirements that meet it, or a stated reason it does not apply. A line with neither blocks approval.

## The project rules

These rules apply to every fork feature. Each one is a line in the checklist. Each rule is stated in full in [principles.md](principles.md), with where it applies and its edge. This page keeps one sentence of each and the id of its principle, and a document cites the rule by that id.

### Performance first

On a request path, or a background path that competes with requests, performance and availability come first, and the design is the fastest correct design known when it is written: [PRINCIPLE-050](principles.md#principle-050). Speed is argued by mechanism and proved by comparing benchmarks, and no numeric target is demanded up front. Off those paths the simplest sufficient design stands: [PRINCIPLE-054](principles.md#principle-054). The benchmarks run in the gates described in [testing.md](testing.md#benchmarks). The stock path is guarded under [PRINCIPLE-052](principles.md#principle-052), and what gates a change is in [PRINCIPLE-053](principles.md#principle-053).

### Isolation levers

A fork feature that adds work to a shared path cannot starve the rest of the node, and its design names what bounds it on every node role that does the work: [PRINCIPLE-051](principles.md#principle-051). Working out what level of isolation a feature needs is part of its architecture. A feature that adds no work to a shared path says so in one line.

### Observability

Observability is a gate item, not an afterthought.

1. Every outcome has a counter: [PRINCIPLE-033](principles.md#principle-033).
2. Every limit reports its limit, the amount used and the number of times it tripped: [PRINCIPLE-033](principles.md#principle-033).
3. Every runtime change of a setting logs the old and the new value at INFO: [PRINCIPLE-034](principles.md#principle-034).
4. Each decision a feature makes on a request path that changes the work done, and each fallback, has a trace line: [PRINCIPLE-033](principles.md#principle-033).
5. Code ChronitonDB writes never puts user data or a secret in a log line, at any log level, and a trace line it writes carries no user data: [PRINCIPLE-035](principles.md#principle-035). A log line that Apache Cassandra writes changes only as [PRINCIPLE-008](principles.md#principle-008) says.
6. Every metric, MBean and virtual table row a feature creates is released when its object is dropped: [PRINCIPLE-037](principles.md#principle-037).

Two more principles bind what a feature logs and exposes. Nothing is logged once per request or per element: [PRINCIPLE-036](principles.md#principle-036). Its edges are the start, end and failure lines of a background task, and an ERROR line for an unexpected server error, which the design assesses and the reviewer checks. A limit reaches the client and state reaches the operator: [PRINCIPLE-039](principles.md#principle-039).

### Automatic fallbacks are opt-in and counted

Automatic behaviour the user did not ask for, and that changes results, cost or plan, is opt in, and each use is counted: [PRINCIPLE-028](principles.md#principle-028). Whether a schema object allows a fallback is an option on that object, off by default, and the operator control of a node that turns every fallback off always wins: [PRINCIPLE-029](principles.md#principle-029).

### Compatibility with Apache Cassandra

An application that moves onto ChronitonDB behaves as it did on Apache Cassandra, and a user can move back, by the steps each release states: [PRINCIPLE-001](principles.md#principle-001) and [PRINCIPLE-003](principles.md#principle-003). The rules that follow from it are principles too:

1. What operators see stays as stock where that is reasonable, and a difference there is recorded in the [delta register](../delta/README.md) and the release notes, not refused: [PRINCIPLE-002](principles.md#principle-002).
2. A user moves between Apache Cassandra and ChronitonDB on the same data files, by a runbook: [PRINCIPLE-003](principles.md#principle-003).
3. A fix to a defect in stock is not a feature and is not gated, and a change to stock code is a fix only when the maintainers approve it as one: [PRINCIPLE-004](principles.md#principle-004). See [maintenance.md](maintenance.md#corrective-fixing-a-fault).
4. A statement that Apache Cassandra rejects only because it uses something Apache Cassandra does not have MAY succeed as a purely additive feature. One that Apache Cassandra refuses for a reason is stock behaviour: [PRINCIPLE-005](principles.md#principle-005).
5. ChronitonDB never changes a compatibility number that Apache Cassandra owns without a decision of the maintainers: [PRINCIPLE-006](principles.md#principle-006).
6. Code defaults in stock classes stay as Apache has them: [PRINCIPLE-007](principles.md#principle-007).
7. A log line that differs from stock is not a compatibility concern: [PRINCIPLE-008](principles.md#principle-008).
8. With a feature off, the feature changes nothing that stock Apache Cassandra does, and the tests of its off state prove it: [PRINCIPLE-019](principles.md#principle-019). The parity suite proves it for the line once it exists: [PRINCIPLE-020](principles.md#principle-020).
9. Schema state is written only for an object that uses the feature: [PRINCIPLE-089](principles.md#principle-089).

Five more principles bind what a feature stores, reads back and sends between nodes: [PRINCIPLE-084](principles.md#principle-084), [PRINCIPLE-085](principles.md#principle-085), [PRINCIPLE-086](principles.md#principle-086), [PRINCIPLE-087](principles.md#principle-087) and [PRINCIPLE-088](principles.md#principle-088). They are answered under the checklist's lines on mixed-version clusters and on data loss or corruption.

### A feature adds no dependence on topology

A fork feature adds no dependence on topology: [PRINCIPLE-061](principles.md#principle-061). So a feature behaves on a single node development cluster as it does on a production cluster with three replicas.

### Data dependent settings belong to the schema object

Behaviour that depends on the data is set on the schema object that owns the data, not by one global setting: [PRINCIPLE-021](principles.md#principle-021). A lever that can apply to several such objects has three mutually exclusive modes, global, include and exclude: [PRINCIPLE-022](principles.md#principle-022).

### A runtime command changes the running value only

A runtime command, such as a nodetool toggle, changes the value in memory only, on the node it is sent to, and the node's configuration at startup holds the starting value: [PRINCIPLE-023](principles.md#principle-023). A value may differ from node to node only for an operator control: [PRINCIPLE-024](principles.md#principle-024).

### A refusal names its control

A refusal names what the user or operator can change to lift it, where there is such a thing: [PRINCIPLE-025](principles.md#principle-025).

### A TLA+ model where the maintainers ask for one

A design whose correctness depends on ordering, concurrency or shared state, across nodes or within one node across a crash and restart, is a candidate for a TLA+ model. The designer does not write one on its own judgement: the design record says why a model is believed to be needed and asks the maintainers, and the model is written only when they say yes. A design with no such dependence says in one line why it needs none, and asks nothing. A model that is written is checked by the TLC model checker. The model files and the checker's result go in the item's design directory, and the design record names them in its Quality requirements section. The rule is [PRINCIPLE-068](principles.md#principle-068).

## The checklist

Copy this table into the feature spec or design record. Fill the last column for every line.

| ISO/IEC 25010 characteristic | Line | Requirements, or the reason it does not apply |
|---|---|---|
| Performance efficiency | On a request path, or a background path that competes with requests, the fastest correct design known, argued by its mechanism and proved by comparing benchmarks | |
| Performance efficiency | Memory of a feature that adds work to a shared path bounded on every node role that does the work | |
| Reliability | A feature that adds work to a shared path cannot starve the rest of the node: threads and work per operation bounded, load shed, run time limited and a way for an operator to turn it off, on every node role that does the work | |
| Reliability | Automatic fallbacks opt in on the schema object, with a node control that turns them off, each use counted and logged without flooding | |
| Reliability | A TLA+ model where the maintainers asked for one, or one line on why the design needs none | |
| Compatibility | An application behaves as it did on Apache Cassandra, and a change to what it sees from a stock feature is behind a switch that is off by default | |
| Compatibility | What operators see stays as stock where that is reasonable, and each difference is recorded in the delta register and the release notes | |
| Compatibility | Stock behaviour unchanged with the feature off | |
| Compatibility | Mixed-version cluster, upgrade and rollback (see the Compatibility section) | |
| Functional suitability | CQL validity and results independent of replication factor, data centres and replica count | |
| Flexibility | Data dependent settings on the schema object that owns the data, with a configured default and maximum, and global, include and exclude modes | |
| Interaction capability | A runtime command changes the in-memory value only, the node's configuration at startup holds the starting value | |
| Interaction capability | A refusal names what the user or operator can change to lift it | |
| Maintainability | Observability: metrics, traces and diagnostics as a gate item | |
| Security | Threat model answered (see the Threat model section) | |
| Safety | Any risk of data loss or corruption named, with its mitigation | |
