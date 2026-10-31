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

Every feature spec and every one-item design record answers this checklist. It is organised by the quality characteristics of ISO/IEC 25010. Each line MUST have requirements that meet it, or a stated reason it does not apply. A line with neither blocks approval.

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

Stock Apache Cassandra behaviour is unchanged. With a feature off, the node behaves exactly as stock: new syntax is refused, no new files are written, no new threads start and no new memory is used. Code defaults in stock classes stay as Apache has them. The parity suite proves it.

### CQL does not depend on topology

Whether a CQL statement is valid, and the results it returns, never depend on the replication factor, the number of data centres or the number of replicas. A single node development cluster behaves like a production cluster with three replicas.

### Settings per index or per table over global settings

Behaviour that depends on the data is set per index (or per table) as an option. The yaml setting gives the default at `CREATE`, `ALTER` changes it, and a global yaml maximum bounds it. A lever that can apply to several indexes or tables has three mutually exclusive modes:

1. **Global:** it applies to all of them.
2. **Include:** it applies only to the listed ones.
3. **Exclude:** it applies to all but the listed ones.

### nodetool changes the running value only

A nodetool toggle changes the in-memory value on the node where it runs. The yaml file holds the value at startup. There is no separate persistence of nodetool changes. A restart returns to the yaml value.

## The checklist

Copy this table into the feature spec or design record. Fill the last column for every line.

| ISO/IEC 25010 characteristic | Line | Requirements, or the reason it does not apply |
|---|---|---|
| Performance efficiency | Fastest correct design, with benchmarks in the design and in the gates | |
| Performance efficiency | Memory budgets on coordinator and replica | |
| Reliability | Isolation levers on coordinator and replica: thread pools, limits, load shedding, timeouts, kill switch | |
| Reliability | Automatic fallbacks opt-in, with yaml setting, nodetool toggle, metric and rate-limited log line | |
| Compatibility | Stock Apache Cassandra behaviour unchanged | |
| Compatibility | Stock behaviour unchanged with the feature off | |
| Compatibility | Mixed-version cluster, upgrade and rollback (see the Compatibility section) | |
| Functional suitability | CQL validity and results independent of replication factor, data centres and replica count | |
| Flexibility | Settings per index or per table over global ones, with global, include and exclude modes | |
| Interaction capability | nodetool toggles change the in-memory value only, yaml holds the startup value | |
| Interaction capability | Error messages name the setting or toggle that controls the behaviour | |
| Maintainability | Observability: metrics, traces and diagnostics as a gate item | |
| Security | Threat model answered (see the Threat model section) | |
| Safety | Any risk of data loss or corruption named, with its mitigation | |
