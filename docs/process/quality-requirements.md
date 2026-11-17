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

Every feature spec and every one-item design record answers this checklist. A feature spec answers it when its class requires the Quality requirements section, see [classification.md](classification.md). It is organised by the quality characteristics of ISO/IEC 25010. Each line MUST have requirements that meet it, or a stated reason it does not apply. A line with neither blocks approval.

## The project rules

These rules apply to every fork feature. Each one is a line in the checklist.

### Performance first

The design is the fastest correct design known when it is written. Each design record names the request paths the change touches, the expected cost with its mechanism, and the benchmarks that prove it. The benchmarks run in the gates described in [testing.md](testing.md#benchmarks).

### Isolation levers

Every fork feature has levers on the coordinator and on each replica that keep it from harming the rest of the node: its own thread pools, limits on work per request, load shedding, timeouts, memory budgets and a kill switch. Each lever has a yaml setting and a metric.

### Observability

Observability is a gate item, not an afterthought.

1. Every outcome has a counter.
2. Every limit reports its limit, the amount used and the number of times it tripped.
3. Every runtime change of a setting logs the old and the new value at INFO.
4. Each plan decision and each fallback has a trace line.
5. No log line above TRACE carries a key, a term, a literal or a secret.
6. Every metric, MBean and virtual table row a feature creates is released when its object is dropped.

### Automatic fallbacks are opt-in and counted

Any automatic fallback, such as falling back to a scan, is off by default. It has a yaml setting, a nodetool toggle, a metric that counts each use and a rate-limited log line.

### Stock behaviour unchanged

Stock Apache Cassandra behaviour is unchanged for anyone not using a ChronitonDB feature, except the one exception in [release.md](release.md#what-a-release-may-contain), `nodetool version`. A behaviour-changing feature is always off by default, but for that exception, and changes stock behaviour only for operators who switch it on. With a feature off, the node behaves exactly as stock: every way to use the feature is refused with an error that names the switch, no new files are written, no new threads start and no new memory is used. For example a statement in the feature's syntax is refused, and so is a nodetool command of the feature. Code defaults in stock classes stay as Apache has them. The parity suite proves it.

### CQL does not depend on topology

Whether a CQL statement is valid, and the results it returns, never depend on the replication factor, the number of data centres or the number of replicas. A single node development cluster behaves like a production cluster with three replicas.

### Data dependent settings belong to the schema object

Behaviour that depends on the data is set on the schema object that owns the data, not by one global setting: an index option for an index, a table option for a table. A configured default applies when the object is created, altering the object changes the value, and a configured maximum bounds it. A lever that can apply to several such objects has three mutually exclusive modes:

1. **Global:** it applies to all of them.
2. **Include:** it applies only to the listed ones.
3. **Exclude:** it applies to all but the listed ones.

### A runtime command changes the running value only

A runtime command, such as a nodetool toggle, changes the value in memory only, on the node where it runs. The configuration file holds the value at startup. There is no separate persistence of runtime changes. A restart returns to the configured value. An option on a schema object is not a runtime toggle: it changes through the schema, as the rule above says.

### A refusal names its control

A refusal names what the user or operator can change to lift it, where there is such a thing. For example a statement refused because a feature is off names the feature switch. A statement refused because a limit is reached names the setting that holds the limit.

### Coordination between nodes is model checked

A design that adds or changes how nodes coordinate, such as a new message exchange, a state shared between nodes or an ordering rule, carries a TLA+ model of that protocol, checked by the TLC model checker. The model files and the checker's result go in the item's design directory, and the design record names them in its Quality requirements section.

## The checklist

Copy this table into the feature spec or design record. Fill the last column for every line.

| ISO/IEC 25010 characteristic | Line | Requirements, or the reason it does not apply |
|---|---|---|
| Performance efficiency | Fastest correct design, with benchmarks in the design and in the gates | |
| Performance efficiency | Memory budgets on coordinator and replica | |
| Reliability | Isolation levers on coordinator and replica: thread pools, limits, load shedding, timeouts, kill switch | |
| Reliability | Automatic fallbacks opt-in, with yaml setting, nodetool toggle, metric and rate-limited log line | |
| Reliability | Coordination between nodes model checked, when the design changes it | |
| Compatibility | Stock Apache Cassandra behaviour unchanged | |
| Compatibility | Stock behaviour unchanged with the feature off | |
| Compatibility | Mixed-version cluster, upgrade and rollback (see the Compatibility section) | |
| Functional suitability | CQL validity and results independent of replication factor, data centres and replica count | |
| Flexibility | Data dependent settings on the schema object that owns the data, with a configured default and maximum, and global, include and exclude modes | |
| Interaction capability | A runtime command changes the in-memory value only, the configuration file holds the startup value | |
| Interaction capability | A refusal names what the user or operator can change to lift it | |
| Maintainability | Observability: metrics, traces and diagnostics as a gate item | |
| Security | Threat model answered (see the Threat model section) | |
| Safety | Any risk of data loss or corruption named, with its mitigation | |
