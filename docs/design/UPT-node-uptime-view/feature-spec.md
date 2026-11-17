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

# Feature spec: Node uptime view in CQL

| Field | Value |
|---|---|
| Title | Node uptime view in CQL |
| Document type | Specification and description (ISO/IEC/IEEE 15289) |
| Status | Draft |
| Version | 1 |
| Author | Architect: chronitondb-agent |
| Approver | The maintainer who merges the pull request |
| References | Issue #143. Line `chronitondb-sandbox`. Apache base commit `76550e931481e965ae3283d8cf4a59c320d74c55` (Apache Cassandra `cassandra-5.0`, build version 5.0.10). Decision records 0007 to 0010. |
| Risk | Normal: the issue's label `risk:normal`, which the maintainers confirm when they merge this spec. The worst Bug Category given as the reason of the label is Degradation: a wrong start time or uptime in the view, or an exception on a read of the view with no other effect. The floor of [classification.md](../../process/classification.md#the-floor) applies, because the feature adds a virtual table, a configuration setting and a metric. For the maintainers: a fault in what a node runs at start would keep that node from starting, an Availability fault that [classification.md](../../process/classification.md#risk) rates Critical. Problem 1 of section 4 names that fault and its tests. Only a maintainer changes the label. |
| Size | Normal: one view, its yaml setting, one hook at start and one read counter. It needs no analysis beyond the virtual table code. |
| Reach | One area: virtual tables. Fork code in `org.chronitondb.uptime`, with one hook in `org.apache.cassandra.db.virtual` and one field in `org.apache.cassandra.config`. |
| Touches | public interface (virtual tables), public interface (configuration), public interface (jmx mbeans, including metrics), stock behaviour, new input or privilege, new feature or switch |

Change history: the git history of this file.

Location: `docs/design/UPT-node-uptime-view/feature-spec.md` on the line `chronitondb-sandbox`. The feature key is `UPT`, a new key. See [Feature keys and requirement ids](../../process/additive.md#feature-keys-and-requirement-ids). Process: [additive.md](../../process/additive.md).

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in BCP 14 (RFC 2119, RFC 8174) when, and only when, they appear in all capitals, as shown here.

The Risk, Size and Reach rows are the feature's class, as [classification.md](../../process/classification.md) defines it, and match the issue's `risk:`, `size:` and `reach:` labels.

A code fact is cited as C1 to C14. Section 12 holds each one with its symbol, file, line and the tree it was read in.

## Contents

- [1. Purpose and scope](#1-purpose-and-scope)
  - [Non-goals](#non-goals)
- [2. Architecture](#2-architecture)
  - [2.1 Context and scope](#21-context-and-scope)
  - [2.2 Building blocks](#22-building-blocks)
  - [2.3 Runtime view](#23-runtime-view)
  - [2.4 Data and formats](#24-data-and-formats)
  - [2.5 Cross cutting concepts](#25-cross-cutting-concepts)
  - [2.6 Deployment](#26-deployment)
  - [2.7 Package dependencies and hook points](#27-package-dependencies-and-hook-points)
  - [2.8 Feature class and switches](#28-feature-class-and-switches)
- [3. Feature requirements](#3-feature-requirements)
- [4. Where problems could occur](#4-where-problems-could-occur)
  - [4.1 Test plan](#41-test-plan)
- [5. Quality requirements](#5-quality-requirements)
- [6. Threat model](#6-threat-model)
- [7. Compatibility](#7-compatibility)
  - [7.1 On-disk format changes](#71-on-disk-format-changes)
  - [7.2 Mixed-version cluster](#72-mixed-version-cluster)
  - [7.3 Upgrade path and prerequisites](#73-upgrade-path-and-prerequisites)
  - [7.4 Rollback path](#74-rollback-path)
  - [7.5 Runbook entries](#75-runbook-entries)
- [8. Dependencies](#8-dependencies)
- [9. Risks](#9-risks)
- [10. Decisions](#10-decisions)
- [11. Milestones outline](#11-milestones-outline)
- [12. Prior art](#12-prior-art)
- [Glossary](#glossary)

## 1. Purpose and scope

During a rolling restart an operator needs to know which nodes have already restarted. Today the operator runs `nodetool info` on each node and reads its `Uptime (seconds)` line (C11). Over CQL a node shows no start time and no uptime of its process (C1). Operators and their tools often reach a node over CQL only.

This feature adds one read-only virtual table, `system_views.chronitondb_uptime`, called the view in this document. It holds one row about the node that executes the statement: the host id of the node, the start time of the node's process and the uptime of that process in whole seconds. After a restart the row holds a later start time and an uptime that counts from the new start.

The users are operators who run rolling restarts, and the CQL tools they use.

In scope:

1. The view and its values.
2. Its switch: the yaml setting `uptime_view_enabled`, which the node reads at start. The view is off by default, and a change of the switch needs a restart of the node (decision record 0007).
3. Access by Apache Cassandra's own permission rule for `system_views`.
4. A node that hides the view answers every statement that names the view, and every table listing, as Apache Cassandra does (decision record 0010). Section 2.8 lists what is present on every node whatever the switch says.
5. One counter of the reads of the view, which exists only on a node that shows the view.
6. A reference page and an entry in `NEWS-chronitondb.txt`.

### Non-goals

1. Rows for other nodes from one connection. A node answers for itself only, so nodes exchange nothing new.
2. An uptime that counts from the moment the node accepts clients. The uptime counts from the start of the process, as `nodetool info` counts it.
3. A change to `nodetool info`. It stays as it is today.
4. A change to `system_views.gossip_info`.
5. A history of past starts. The view shows the running process only.
6. A nodetool command, or an MBean that reads or changes the switch. Decision record 0007 chose the yaml setting only, so nothing changes the switch while the node runs.
7. An error that names the switch while the view is hidden. Decision record 0010 chose the Apache Cassandra answer for a table that does not exist.
8. A change to permission code. The view relies on the rule Apache Cassandra has.
9. A start time that follows the clock of the node. Decision record 0009 chose the start time read once at start, so after a clock change the start time plus the uptime can differ from the clock.
10. Other lines. The issue names the line `chronitondb-sandbox` only. Section 12 says what differs on Apache Cassandra 6.0.

## 2. Architecture

The feature is small. One virtual table builds one row from the host id of the node and two values of the node's JVM. Apache Cassandra builds the table list of `system_views` once at start (C1). One line added to that list asks the feature for its tables: none while the view is hidden, the view while it is shown. The state of the view never changes while the node runs. A node that shows the view counts the reads of it.

### 2.1 Context and scope

The feature runs inside one node and talks to nothing outside it.

1. **A CQL client**: an operator with cqlsh, or a tool with a driver. It reads the view on the node its connection reaches.
2. **An operator who edits `cassandra.yaml`**: sets the switch and restarts the node.
3. **Apache Cassandra subsystems inside the node**: the table list of `system_views` (C1), the configuration (C8), the metrics registry (C12), `StorageService` for the host id (C11) and the log.
4. **The JVM of the node**: its `java.lang.management.RuntimeMXBean` gives the start time and the uptime, as it does for `nodetool info` (C11).

The feature sends no message to another node, writes no file on a node's disk and starts no thread. Its one MBean is the one of the read counter, and only a node that shows the view has it.

### 2.2 Building blocks

| Block | Where it lives | What it does |
|---|---|---|
| The setting | the field `uptime_view_enabled` in `Config.java` | Holds the value from `cassandra.yaml`. Its default is `false` |
| The hook | `org.chronitondb.uptime`, one static method that the constructor of `SystemViewsKeyspace` calls | Decides whether the view is shown or hidden and returns the tables the feature adds to `system_views`: an empty list when the view is hidden, a list that holds the view when it is shown. It catches no throwable |
| The final gate | `org.chronitondb.uptime` | One static method with no argument that says whether the final gate is passed. It returns `false` until the last item of the final milestone changes it |
| The time source | `org.chronitondb.uptime` | One interface with two methods, the start time and the uptime, both in milliseconds. The node's own implementation returns the two values of the JVM's `RuntimeMXBean`. A unit test passes its own |
| The view | `org.chronitondb.uptime` | A read-only virtual table built on `AbstractVirtualTable` (C10). It builds one row at each read |
| The read counter | `org.chronitondb.uptime` | One Dropwizard `Counter`. Its MBean name is `org.chronitondb.metrics:type=UptimeView,name=Reads` and its name in the metrics registry is `org.chronitondb.metrics.UptimeView.Reads`. It exists only on a node that shows the view |

The view has these columns:

| Column | Type | Kind | Value |
|---|---|---|---|
| `key` | text | partition key | always `local`, as in `system.local` |
| `host_id` | uuid | regular | the host id of the node, the id `nodetool info` prints on its `ID` line (C11) |
| `started_at` | timestamp | regular | the start time of the node's JVM, read once at start |
| `uptime_seconds` | bigint | regular | the uptime of the node's JVM at the read, in whole seconds |

A `SELECT` with a key filter or a column list is answered as `AbstractVirtualTable` answers it for every Apache Cassandra virtual table: a filter on another key returns no row, and a column list returns those columns.

**The values.** The view takes each value from the process it runs in.

1. `host_id` is the value `StorageService.getLocalHostUUID` returns at the read, the method behind the `ID` line of `nodetool info` (C11). When that method returns no id, the column holds no value, where `nodetool info` prints `null`.
2. `started_at` is the value of `RuntimeMXBean.getStartTime()`. The hook reads it once, when it builds the view, and the view returns that same value at every read until the node stops (decision record 0009). The Java API documentation calls the value approximate.
3. `uptime_seconds` is the value of `RuntimeMXBean.getUptime()` at the read, divided by 1000 and rounded down. `nodetool info` reads the same method of the same JVM and divides in the same way for its `Uptime (seconds)` line (C11). The two tools read at different moments, so their values differ by the time between the two reads.

The node stores none of these values and takes none from another node. A node that restarts is a new process, so its row holds the start time and the uptime of the new JVM. This is how an operator tells a node that restarted from one that did not.

After a change of the clock on a running node, `started_at` stays as it was read, and `started_at` plus `uptime_seconds` can differ from the clock of the node (decision record 0009). How the JVM computes its uptime was not read for this document, and no requirement rests on it.

**Shown and hidden.** The view is in one of two states on a node, shown or hidden. The hook decides the state once, at start, and the node keeps it until it stops. The view is shown when both of these hold at start, and hidden when either does not:

1. The setting `uptime_view_enabled` is `true` in the configuration the node loaded.
2. The final gate is passed.

The final gate is the feature's final milestone gate of [additive.md](../../process/additive.md#milestone-gates). In the code it is one static method that returns a fixed value: `false` until the last item of the final milestone changes it to `true`. Until that item the view stays hidden on every node, whatever the configuration the node loaded holds.

**What the hook does.** Apache Cassandra builds the table list of `system_views` in the constructor of `SystemViewsKeyspace`, which runs once, when the node registers its virtual keyspaces at start (C1, C2). At that point the node has not yet loaded its stored prepared statements and accepts no client connection (C3). The last entry of the list is the call of the hook, in the form of the `addAll` entries Apache Cassandra has there (C1). The hook takes one of three paths:

1. The setting is `false`. The hook returns an empty list right after it read the setting. It reads no gate, writes no log line, creates no metric and runs no other code of the feature.
2. The setting is `true` and the final gate is not passed. The hook logs one WARN line that names the setting and returns an empty list. The node goes on with its start as any other node does and never refuses to start for this reason (decision record 0008). The feature never writes the field of the setting, so `system_views.settings` shows the value the node loaded, `true` on such a node, while the view is hidden.
3. The setting is `true` and the final gate is passed. The hook reads the start time from the time source, creates the read counter, builds the view, logs one INFO line that names the view and returns a list that holds the view.

Apache Cassandra then registers `system_views` once, with the list as the constructor built it (C2). The feature registers nothing itself and never registers a keyspace again. The node is in its state, shown or hidden, before it accepts a client connection (C3), and every requirement written for a shown or a hidden view holds from the moment the node accepts client connections until the node stops.

**When the hook hits a fault.** The hook catches no throwable. A throwable that is thrown in it leaves the hook and ends the load of the class `SystemViewsKeyspace`. It reaches `CassandraDaemon.setupVirtualKeyspaces` as it is, or wrapped by the JVM in an `ExceptionInInitializerError`. Apache Cassandra calls that method at start with no guard around the call. So the throwable ends the start of the node as a throwable from the constructor of one of Apache Cassandra's own virtual tables does: the node logs `Exception encountered during startup` with the throwable and exits (C3). The node never goes on to serve without the view. A node that went on without the view would be an automatic fallback, and [quality-requirements.md](../../process/quality-requirements.md#automatic-fallbacks-are-opt-in-and-counted) allows one only with its own setting, toggle and metric, which this feature does not add.

The feature adds no log line, no metric and no setting for such a fault. An operator who meets it fixes the fault, or removes `uptime_view_enabled` from the `cassandra.yaml` of the node or sets it to `false`. The hook then returns right after it read the setting, and the node starts without the view. The reference page says so.

What every node runs, the switch off included, is the call of the hook, which loads the class of the hook, and the read of the setting, which is a read of one boolean field of the configuration the node already loaded. A fault there would stop every node at start. Every in-JVM distributed test starts its nodes through the same constructor (C2), so such a fault fails every one of them (problem 1 of section 4).

**The read counter.** A node that shows the view counts the reads of the view, because [quality-requirements.md](../../process/quality-requirements.md#observability) asks for a counter for every outcome. The counter is one Dropwizard `Counter`, the kind `CassandraMetricsRegistry.counter` makes (C12). Its metric name has the group `org.chronitondb.metrics`, the feature's own metric type `UptimeView`, the name `Reads` and no scope, as [conventions.md](../../process/conventions.md#names) items 3 and 4 ask, in the form the counters of the merged [design record of the commit log disk check](../CLD-commitlog-disk-check/design-record.md) have. The name is built with the five argument constructor of `CassandraMetricsRegistry.MetricName`, which takes the MBean name as it is written (C12). The MBean name is `org.chronitondb.metrics:type=UptimeView,name=Reads`, which shows over JMX. The registry name joins the group, the type and the name with dots, `org.chronitondb.metrics.UptimeView.Reads`, and is what a metrics reporter the node has configured shows (C12). The counter is registered as every metric of Apache Cassandra is, and the feature adds no check of its own on that registration.

The hook creates the counter only on its third path. A node that hides the view holds no metric and no MBean of the feature. The counter lives until the node stops. It starts at 0 at each start of the node and is stored nowhere.

The view raises the counter by one in its `data()` method, and it overrides no other read method of `AbstractVirtualTable`. So the counter counts each time the node builds the row, and never statements. Apache Cassandra's read path calls `data()` once for each partition key a statement names, also when the key matches no row, and once for a read with no key filter (C10, C13). A statement that a client fetches in pages is run as one read for each page it fetches (C13). The view holds one row, so with a page size of one row a `SELECT` with no key filter fills its first page, Apache Cassandra cannot tell that no row follows, and the client's fetch of the next page, which is empty, builds the row a second time. A `SELECT` that Apache Cassandra's permission check refuses does not reach the view and is not counted, since that check runs before the statement is executed (C13). The reference page says what the counter counts.

**What a hidden view looks like.** The hook added nothing, so the table list of `system_views` is the one Apache Cassandra builds. A statement finds a table by name through the keyspace's table list (C4), so the view is not found and the statement gets the Apache Cassandra answer for a table that does not exist. The listings read the same table lists (C5), so they do not show it. All of this is Apache Cassandra's own code, which the feature does not touch.

A node stores the statements its clients prepared and loads them again at start (C9). A statement that reads the view, prepared while the view was shown, is in that store. When the node next starts with the view hidden, Apache Cassandra cannot prepare the statement again. It logs one warning that holds the statement's text and removes the statement from the store (C9). This is what Apache Cassandra does for a stored statement on any table that no longer exists.

**Access.** The view adds no permission check. Apache Cassandra checks `SELECT` on a table of `system_views` against grants on that table and on the keyspace `system_views`, and a grant on all keyspaces does not count (C6). A superuser passes. On a node whose authorizer requires no authorization, every client passes, as for every table of `system_views` (C6). `GRANT` and `REVOKE` on a table need the table to exist on the node that runs the statement (C7). So a role is granted `SELECT` on the view on a node that shows it, or on the keyspace `system_views` on any node. The reference page gives the grant on the view as the way to let a role read it, because a grant on the keyspace also opens every other table of `system_views`.

A grant on the view can outlive the view. Apache Cassandra stores grants for the whole cluster, and a `REVOKE` that names the view fails on a node that does not show it (C7). The feature adds no code for a grant that is left behind, because such code would change permission handling, which non-goal 8 leaves out. The rule for operators is one rule for the cluster: revoke a grant on the view over a connection to a node that shows the view, before the last node of the cluster that shows the view is rolled back or restarted with the view hidden. The reference page gives the rule and says what a grant left behind does:

1. It gives no access while no node shows the view.
2. It gives its role the read again on every node that shows the view later.
3. It can be revoked on any node that shows the view, whenever one does.
4. It goes when its role is dropped, on any node, since Apache Cassandra removes every grant of a role it drops (C7).

**Tests that need a state shipped code cannot reach.** The hook takes no argument: it reads the setting and the final gate itself. Two states are therefore reached by in-JVM distributed tests only: the view shown before the final gate, and a hook that hits a fault. For each, the test rewrites a method of the feature inside the class loader of its test node, before the node starts, as Apache Cassandra's own in-JVM distributed tests do (C14): the method of the gate, or a method the hook calls on its third path, which the rewrite makes throw. The framework builds a new class loader at each start of a test node and applies the rewrite again, so a rewrite holds over the restarts of a test (C14). This rewrite is the mechanism inside the in-JVM distributed test framework that [testing.md](../../process/testing.md#scenarios) item 9 requires. Shipped classes hold no setting, no property and no second code path that changes what the gate returns or that makes the hook throw.

The nodes of an in-JVM distributed test are class loaders inside one JVM (C14). A test node that restarts keeps the JVM, so its start time does not change. What a restart does to the values is therefore proven on JVM processes the test starts one after the other (problem 3 of section 4.1). An in-JVM distributed test node registers no MBean unless its test starts it with the JMX feature of the framework (C14), so each test of section 4.1 that looks for an MBean starts its nodes with that feature. The design record of the item that adds each test defines its rewrite.

### 2.3 Runtime view

Not applicable: this section is required from Challenging size, and this feature is Normal size. Section 2.2 says what the feature runs at start and at a read, the only two paths it touches.

### 2.4 Data and formats

Not applicable: the feature adds no file on a node's disk, no wire form, no schema row and no cluster metadata. Section 2.2 holds the view's columns.

### 2.5 Cross cutting concepts

Not applicable: the feature has one group of components. Section 5 names its setting, its log lines and its metric by requirement.

### 2.6 Deployment

Not applicable: this section is required from Challenging size, and this feature is Normal size. Section 7 says what changes for an operator: one new yaml setting, and one more MBean on a node that shows the view.

### 2.7 Package dependencies and hook points

| ChronitonDB package | MAY import |
|---|---|
| `org.chronitondb.uptime` | From Apache Cassandra `db.virtual`, `db.marshal`, `dht`, `schema`, `config`, `metrics`, `utils` and the class `service.StorageService`. The JDK, SLF4J and Guava |

The package does not import `org.apache.cassandra.auth`, `org.apache.cassandra.transport`, `org.apache.cassandra.net`, `org.apache.cassandra.tools` or `org.apache.cassandra.service.ClientState`.

Hook points, each a stock file this feature edits:

| Stock file | Edit | Why | Delta entry |
|---|---|---|---|
| `src/java/org/apache/cassandra/config/Config.java` | One field, `uptime_view_enabled`, default `false` | Apache Cassandra's loader refuses a yaml key that has no field (C8). The field imports no fork code | `docs/delta/node-uptime-view.md` |
| `src/java/org/apache/cassandra/db/virtual/SystemViewsKeyspace.java` | One import and one `addAll` entry at the end of the table list in the constructor | The view has to be in the list Apache Cassandra registers as `system_views` (C1, C2) | `docs/delta/node-uptime-view.md` |

### 2.8 Feature class and switches

Feature class: behaviour-changing, because while the view is shown, operations Apache Cassandra already has return one more table.

| Switch | Class | Reason | Default per line | Apache Cassandra operations it changes |
|---|---|---|---|---|
| `uptime_view_enabled`, a yaml setting read at start | behaviour-changing | while on, the table listings of the node hold the view | `chronitondb-sandbox`: off | `SELECT` on `system_virtual_schema.tables` and `system_virtual_schema.columns`, and `DESCRIBE` statements that list or describe the tables of `system_views` (C5) |

While the view is shown, the node also holds the read counter, over JMX and in any metrics reporter it has configured. The counter has the feature's own metric type, so no metric of Apache Cassandra changes and none is added to a metric type of Apache Cassandra. A node that hides the view holds no such counter.

A node that hides the view answers every statement that names the view, and every table listing, as Apache Cassandra does. One thing is present on every node whatever the switch says, a departure from [branching-and-review.md](../../process/branching-and-review.md#feature-switches-and-defaults) item 7: `system_views.settings` and the start log line that prints the configuration show one more setting, `uptime_view_enabled`, because Apache Cassandra lists every field of `Config` (C8). Decision record 0007 accepts it.

Three more departures from the same page:

1. The switch has no nodetool toggle, where item 1 asks for a yaml setting and a nodetool toggle. Decision record 0007 settles it. The switch cannot change while the node runs, so the node has no switch change to log. The start log line that prints the configuration shows the value the node started with (C8).
2. Item 2 says that the switch refuses to turn on before the final milestone gate, and names no form. Decision record 0008 chose the form: the node starts, keeps the view hidden and logs one warning that names the setting.
3. A statement that names the hidden view gets no error that names the switch, where item 7 asks for one. Decision record 0010 settles it.

## 3. Feature requirements

"The node" is the node that executes the statement, or the node that starts. "Shown", "hidden", "the hook", "the final gate" and "the time source" are defined in section 2.2. A requirement written for a shown or a hidden view holds from the moment the node accepts client connections until the node stops.

FREQ-UPT-001 (state driven): While the view is shown, the node MUST answer `SELECT * FROM system_views.chronitondb_uptime`, sent by a client that passes Apache Cassandra's permission check, with exactly one row, whose columns are those of section 2.2 and whose `key` is `local`. Source: stakeholder need.

FREQ-UPT-002 (ubiquitous): The `host_id` column MUST hold the value `StorageService.getLocalHostUUID` returns on the node at the read, and no value when that method returns no id. Source: stakeholder need.

FREQ-UPT-003 (ubiquitous): The `started_at` column MUST hold, at every read, the value the hook read once from the `RuntimeMXBean.getStartTime()` method of the node's JVM when it built the view. Source: decision record 0009.

FREQ-UPT-004 (ubiquitous): The `uptime_seconds` column MUST hold the value the `RuntimeMXBean.getUptime()` method of the node's JVM returns at the read, divided by 1000 and rounded down. Source: stakeholder need.

FREQ-UPT-005 (ubiquitous): The node MUST take the values of the row from its own running process only, with no message to another node and no value stored by an earlier process of the node. Source: stakeholder need.

FREQ-UPT-006 (event driven): When a node has restarted as a new process, the row of that node MUST hold the start time and the uptime of the new process. Source: stakeholder need.

FREQ-UPT-007 (unwanted behaviour): If the node's authorizer requires authorization and a role that is not a superuser holds `SELECT` on neither the view nor the keyspace `system_views`, then the node MUST refuse that role's `SELECT` on the shown view with the unauthorized error Apache Cassandra returns for the other tables of `system_views`. Source: stakeholder need.

FREQ-UPT-008 (ubiquitous): The view MUST refuse every statement that writes to it or truncates it, with the error Apache Cassandra returns for its read-only virtual tables (C10). Source: risk, problem 4 of section 4.

FREQ-UPT-009 (ubiquitous): The yaml setting `uptime_view_enabled` MUST default to `false`. Source: stakeholder need.

FREQ-UPT-010 (event driven): When the node starts, the hook MUST decide once whether the view is shown or hidden, before the node loads its stored prepared statements, which it does before it accepts a client connection (C3). Source: decision record 0007.

FREQ-UPT-011 (ubiquitous): The node MUST keep the state the hook decided, shown or hidden, until the node stops. Source: decision record 0007.

FREQ-UPT-012 (event driven): When the hook decides and the configuration the node loaded sets `uptime_view_enabled` to `true` and the final gate is passed, the node MUST show the view. Source: stakeholder need.

FREQ-UPT-013 (event driven): When the hook decides and the configuration the node loaded sets `uptime_view_enabled` to `false` or the final gate is not passed, the node MUST hide the view. Source: stakeholder need and decision record 0008.

FREQ-UPT-014 (unwanted behaviour): If the configuration the node loaded sets `uptime_view_enabled` to `true` on a node whose final gate is not passed, then the hook MUST log one WARN line that names the setting. Source: decision record 0008.

FREQ-UPT-015 (unwanted behaviour): If the configuration the node loaded sets `uptime_view_enabled` to `true` on a node whose final gate is not passed, then the hook MUST return an empty list, as it does for a setting of `false`, so that the node goes on with its start. Source: decision record 0008.

FREQ-UPT-016 (state driven): While the view is hidden, the node MUST give a CQL statement that names `system_views.chronitondb_uptime` the answer Apache Cassandra gives the same statement for a table name that `system_views` does not hold, with the view's name where Apache Cassandra puts the table name. Source: decision record 0010.

FREQ-UPT-017 (state driven): While the view is hidden, the node MUST NOT list the view in `system_virtual_schema.tables`, in `system_virtual_schema.columns` or in the output of a `DESCRIBE` statement. Source: stakeholder need.

FREQ-UPT-018 (state driven): While the view is hidden, the node MUST NOT hold a metric or an MBean of the feature. Source: stakeholder need.

FREQ-UPT-019 (state driven): While the configuration the node loaded sets `uptime_view_enabled` to `false`, the hook MUST return an empty list right after it read the setting, with no other code of the feature run. Source: risk, problem 1 of section 4.

FREQ-UPT-020 (state driven): While the view is shown, the node MUST hold one Dropwizard `Counter` in Apache Cassandra's metrics registry, under the registry name `org.chronitondb.metrics.UptimeView.Reads`, created with the MBean name `org.chronitondb.metrics:type=UptimeView,name=Reads` (C12). Source: stakeholder need.

FREQ-UPT-021 (event driven): When Apache Cassandra's read path calls the `data()` method of the view, the view MUST raise the counter of FREQ-UPT-020 by one. Source: stakeholder need.

FREQ-UPT-022 (event driven): When the hook decides that the view is shown, the hook MUST log one INFO line that names the view. Source: stakeholder need.

FREQ-UPT-023 (unwanted behaviour): If a throwable is thrown in the hook, then the hook MUST let that throwable out to its caller, without catching it. Source: risk, problem 1 of section 4.

FREQ-UPT-024 (ubiquitous): The feature MUST NOT add a nodetool command, or an MBean other than the one Apache Cassandra creates for the read counter of FREQ-UPT-020. Source: decision record 0007.

FREQ-UPT-025 (ubiquitous): The feature MUST ship a reference page that names the view and its columns with their units, the setting with its default and the restart a change of it needs, the answer a hidden view gives, the `GRANT` statement on the view as the way to let a role read it, a warning that a grant on the keyspace `system_views` also opens its other tables, a warning that every client reads the shown view on a node whose authorizer requires no authorization, and the need to read each node over a connection to that node. Source: stakeholder need and risk, problems 4, 6 and 8 of section 4.

FREQ-UPT-026 (ubiquitous): The reference page MUST say that `started_at` is read once at the start of the node, that `uptime_seconds` is the value `nodetool info` computes, and that after a change of the clock on a running node `started_at` plus `uptime_seconds` can differ from the clock of the node. Source: decision record 0009.

FREQ-UPT-027 (ubiquitous): The reference page MUST contain the exact texts `org.chronitondb.metrics:type=UptimeView,name=Reads` and `org.chronitondb.metrics.UptimeView.Reads`, and say that the counter exists only on a node that shows the view and counts each time the node builds the row, so that a statement fetched in pages can count more than once. Source: risk, problem 6 of section 4.

FREQ-UPT-028 (ubiquitous): The reference page and `NEWS-chronitondb.txt` MUST state the upgrade order of section 7.3 and the rollback step of section 7.4. Source: risk, problem 5 of section 4.

FREQ-UPT-029 (ubiquitous): The reference page MUST state when to revoke a grant on the view and the four things a grant left behind does, as section 2.2, Access, lists them. Source: risk, problem 8 of section 4.

FREQ-UPT-030 (ubiquitous): The reference page MUST say that a throwable in the hook ends the start of a node whose configuration turns the view on, and that such a node starts without the view once `uptime_view_enabled` is removed from its `cassandra.yaml` or set to `false`. Source: risk, problem 1 of section 4.

## 4. Where problems could occur

Worst case first.

1. **A node does not start.** An operator sees a node that exits during its start. It is every node, the switch off included, if the call of the hook fails or the read of the setting throws. That comes from the one entry in the constructor of `SystemViewsKeyspace` and from the first lines of the hook (C1). By design it is also each node whose configuration turns the view on, if anything in the hook throws. Such a node logs `Exception encountered during startup` with the throwable and exits, as for a throwable from the constructor of one of Apache Cassandra's own virtual tables (C3). A fault that every node of a cluster shares stops each node that is restarted with the switch on, so a rolling restart shows it on the first node. The node starts without the view once the setting is removed from its `cassandra.yaml` or set to `false`. The opposite fault is a hook that catches a throwable and lets the node go on with a read counter and no view, which FREQ-UPT-023 excludes.
2. **Other tables of `system_views` fail or are missing.** An operator or a monitoring tool sees a table such as `system_views.settings` missing or failing. It comes from the entry this feature adds to the table list in the constructor of `SystemViewsKeyspace` (C1): an entry in the wrong place, or a list the hook returns that the builder of the table list refuses.
3. **The view shows a wrong value.** An operator reads a start time that is not the one of the running process, an uptime in the wrong unit or one that differs from `nodetool info` by more than the time between the two reads, or a host id that is not the node's. After a restart the row still shows the values of the process before it. The operator then takes a node for restarted that was not, or the other way round, in the middle of a rolling restart. It comes from the time source, the hook's one read of the start time or the view's row.
4. **The values reach a client that should not see them, or a client changes them.** A role with no grant reads the row, a client reads it while the switch is off, or a client writes to the view. It comes from the hook or from a design that adds its own permission check. Two things are by design. While the view is shown, every logged in user can see the view's name in `system_virtual_schema.tables`, which Apache Cassandra lets every user read (C6). And on a node whose authorizer requires no authorization, every client reads the shown view, as it reads every table of `system_views` (C6).
5. **A node started on an Apache Cassandra binary, or on an older ChronitonDB build, with the setting in its yaml does not start.** The operator sees `Invalid yaml. Please remove properties [uptime_view_enabled] from your cassandra.yaml` (C8). It happens after a rollback, and during an upgrade when the setting is written before the node has its new binary. The refusal is Apache Cassandra's own, for any key it does not know, and comes from no fault in the feature's code.
6. **The switch does not do what the operator asked.** The view is hidden on a node started with the switch on and the final gate passed, or is shown on a node started with the switch off. An operator edits `cassandra.yaml`, does not restart the node, and expects the view to change. On a node that shows the view, the read counter is missing or does not rise with the reads, or the log does not say that the view is shown. By design, the counter counts more than one for a statement fetched in pages of one row, so an operator who takes it for a count of statements reads it too high.
7. **A node that hides the view differs from Apache Cassandra.** A listing shows the view while it is hidden, or a statement that names the view gets an answer Apache Cassandra would not give. A node that stored a prepared statement on the view starts, with the view hidden, in another way than Apache Cassandra starts with a stored statement on a table that no longer exists, where it logs one warning and removes the statement (C9). A node that hides the view holds a metric or an MBean of the feature, or a node with the switch off writes a log line of the feature at start.
8. **A grant or a read goes to a node that has no view.** `GRANT SELECT ON system_views.chronitondb_uptime` fails with `Resource <table system_views.chronitondb_uptime> doesn't exist` on a node where the view is hidden or absent (C7). A driver sends the `SELECT` to another node than the operator meant, and the answer is that node's row or a missing table error. A grant on the view stays behind after the view is switched off, cannot be revoked on a node without the view (C7), and gives its role the read again when a node shows the view. A grant on the keyspace `system_views` lets the role read every other table of it too.
9. **The view can be switched on before the feature is finished.** An operator of a release cut between two milestones turns on a view whose pages and tests are not complete. Or such a node refuses to start because of the setting, against decision record 0008.
10. **An operator misreads the row after a clock change.** The clock of a running node is set back or forward. `started_at` stays, so `started_at` plus `uptime_seconds` differs from the clock, and an operator who compares them suspects a fault. This is by design (decision record 0009).

### 4.1 Test plan

No scenario module and no parity suite exist on this line. Each requirement is proven by a unit test or an in-JVM distributed test, and each item's design record names them.

Four rules hold for every test of this plan. Until the final milestone, each in-JVM distributed test that needs the view shown passes the gate by the rewrite of section 2.2. A log line of the feature is a line logged by a class of `org.chronitondb.uptime`, and the design record of the item says how a test reads the logging class from the log. A test that expects no metric of the feature expects no name in the metrics registry that starts with `org.chronitondb.metrics.UptimeView`. A test that expects no MBean of the feature starts its nodes with the JMX feature of the framework (C14) and expects no MBean whose name holds `type=UptimeView`.

1. Problem 1: an in-JVM distributed test starts a node with the default configuration and expects the node to start, no log line of the feature, no metric of the feature and no MBean of the feature. A second run does the same with the method of the gate and each method the hook calls on its third path rewritten to throw, and expects the same, since a node with the switch off calls none of them (FREQ-UPT-019). That run also proves the way back of FREQ-UPT-030. Two more runs start a node with the switch on, the gate passed by its rewrite and one method of the third path rewritten to throw, a `RuntimeException` in the first run and a `java.lang.Error` in the second. Each expects the start of the test node to fail with the throwable its rewrite threw, itself or in the cause chain of what the start throws (FREQ-UPT-023). The review of the pull request that adds the hook checks that it holds no `catch` block. These runs are on in-JVM distributed test nodes, which call `setupVirtualKeyspaces` themselves (C2). What a node started by `CassandraDaemon.activate` logs and how it exits is Apache Cassandra's own code, which the feature does not touch (C3). A documentation test checks the reference page for what a throwable in the hook does and for the way back (FREQ-UPT-030). Every in-JVM distributed test of the line starts its nodes through the constructor of `SystemViewsKeyspace` (C2), so a call of the hook that fails makes all of them fail. No test can show that the call never fails. These tests show that it does not fail on the builds they run on.
2. Problem 2: an in-JVM distributed test starts one node that shows the view and one that hides it. It expects the table names of `system_views` on the first to be those of the second and the view. For every other table it expects the columns that `system_virtual_schema.columns` lists to be equal on both nodes, and a `SELECT` on it to succeed on both. Apache Cassandra's own unit tests and in-JVM distributed tests that the line's checks run are run unchanged with the switch off. A pre-existing test that fails stops the work, as [conventions.md](../../process/conventions.md#code-layout) item 5 says.
3. Problem 3: unit tests build the view with a time source of their own. One gives the uptimes 999, 1000 and 1999 milliseconds and expects 0, 1 and 1 in `uptime_seconds` (FREQ-UPT-004). One changes the start time of its time source after the view is built and expects `started_at` to hold the first value at every read (FREQ-UPT-003). A unit test of the node's own time source expects its start time to equal `RuntimeMXBean.getStartTime()` of the test's JVM, and its uptime to lie between two reads of `RuntimeMXBean.getUptime()` that the test takes before and after (FREQ-UPT-003, FREQ-UPT-004). An in-JVM distributed test reads the view, runs `nodetool info` on the same node and reads the view again. It expects the `ID` line to equal `host_id`, and the `Uptime (seconds)` line to lie between the two `uptime_seconds` values (FREQ-UPT-001, FREQ-UPT-002, FREQ-UPT-004). It also reads with a filter on another key and with a column list. A test starts two JVM processes one after the other. Each builds the row with the node's own time source and prints it. The test expects the second `started_at` to be later than the first, and not earlier than the time the test read after the first process ended (FREQ-UPT-005, FREQ-UPT-006). The design record of the item says how the test starts the two processes. The review of each pull request checks that the feature writes no file and reads none for its values (FREQ-UPT-005). No test on this line restarts a node as a real process, because the nodes of an in-JVM distributed test share one JVM (C14).
4. Problem 4: an in-JVM distributed test with authentication and authorization on reads the view as a superuser, as a role granted `SELECT` on the view, as a role granted `SELECT` on the keyspace, as a role granted `SELECT` on all keyspaces only, and as a role with no grant. The last two are refused (FREQ-UPT-007). It reads the read counter before and after the two refused reads and expects the same value (FREQ-UPT-021). A test tries an `INSERT`, an `UPDATE`, a `DELETE` and a `TRUNCATE` and expects Apache Cassandra's refusal (FREQ-UPT-008). The review of each pull request checks its imports against section 2.7. The tests of problem 7 cover the view being readable while off.
5. Problem 5: no test on this line can start an Apache Cassandra binary. Apache Cassandra's own configuration tests run unchanged to show the setting loads here. A documentation test checks that the reference page and `NEWS-chronitondb.txt` hold the upgrade order and the rollback step (FREQ-UPT-028).
6. Problem 6: in-JVM distributed tests start a node in each of the four combinations of the setting and the gate, the gate passed by its rewrite or left as it is, and expect the view shown only with the setting `true` and the gate passed (FREQ-UPT-012, FREQ-UPT-013). A test starts a node with the switch on and reads the view once the node accepts connections, then restarts the node with the switch off and expects the missing table error. A test prepares a `SELECT` on the shown view, restarts the node with the view still shown, and expects the stored statement to be loaded again with no warning (FREQ-UPT-010). A test sets the `Config` field in the memory of a started node, to `true` on a node that hides the view and to `false` on a node that shows it, and expects the state of the view unchanged (FREQ-UPT-011). A test reads the start log of a node that shows the view and expects one INFO line that names the view and no other log line of the feature (FREQ-UPT-022). Inside that node it expects the read counter in the metrics registry under its registry name, at 0, and one MBean whose name holds `type=UptimeView`, the one with `name=Reads` (FREQ-UPT-020, FREQ-UPT-024). It then sends three statements with paging off. It expects the counter at 1 after one `SELECT` on the view, at 2 after a `SELECT` with a filter on another key, and at 4 after a `SELECT` whose `IN` list names two key values. It then sends one `SELECT` with no key filter with a page size of one row, fetches every page, and expects the counter at 6 (FREQ-UPT-021). The review of each pull request checks that it adds no nodetool command and no other MBean (FREQ-UPT-024). A documentation test checks the reference page for the restart, for the two names of the read counter and for what the counter counts (FREQ-UPT-025, FREQ-UPT-027).
7. Problem 7: an in-JVM distributed test reads, with the view hidden, the rows of `system_virtual_schema.tables` and `system_virtual_schema.columns` for `system_views` and the output of `DESCRIBE KEYSPACE system_views`, and expects no table named `chronitondb_uptime` (FREQ-UPT-017). Inside that node it expects no metric of the feature and no MBean of the feature (FREQ-UPT-018). It sends a `SELECT`, a `DESCRIBE TABLE` and a `GRANT` that name the view, and the same three with a table name `system_views` does not hold, and expects answers equal but for the name (FREQ-UPT-016). It runs once with the switch off, and once with the switch on and the final gate not passed. In the run with the switch off it also expects no log line of the feature in the start log (FREQ-UPT-019). A test prepares a `SELECT` on the shown view, reads how many statements on the view the node stored, and restarts the node with the switch off. It expects the node to start with one warning of C9 for each of those statements and none of them left in the store, and a new prepare to get the missing table error (FREQ-UPT-016).
8. Problem 8: an in-JVM distributed test with one node that shows the view and one that hides it sends the `GRANT` on the view to each. It expects the failure of C7 on the node that hides it and success on the other. It then expects a `REVOKE` that names the view to fail on the node that hides it, as C7 says, and to succeed on the node that shows it. A second test grants a role `SELECT` on the view, restarts the node with the switch off and then with the switch on again, and expects the role's `SELECT` on the view to succeed again and a `REVOKE` on that node to succeed, as section 2.2, Access, says of a grant left behind. A documentation test checks the reference page for the `GRANT` statement on the view, the two warnings and the need to connect to each node (FREQ-UPT-025), and for the revoke rule with the four things a grant left behind does (FREQ-UPT-029).
9. Problem 9: until the final milestone, a test starts a node with `uptime_view_enabled: true` and expects the node to start, the view hidden, the value `true` in the row of `uptime_view_enabled` in `system_views.settings`, and one WARN line of the feature that names the setting (FREQ-UPT-013, FREQ-UPT-014, FREQ-UPT-015). The item that passes the final gate replaces it with a test that the view is shown.
10. Problem 10: no test can change the clock of the machine it runs on. The unit test of problem 3 that changes the start time of its time source proves that `started_at` stays (FREQ-UPT-003). A documentation test checks the reference page for the three statements of FREQ-UPT-026. The case is watched through the reference page.

## 5. Quality requirements

This section is required from Challenging size. It is filled here because the feature has to meet the checklist of [quality-requirements.md](../../process/quality-requirements.md).

| ISO/IEC 25010 characteristic | Line | Requirements, or the reason it does not apply |
|---|---|---|
| Performance efficiency | Fastest correct design, with benchmarks in the design and in the gates | No benchmark. A read builds one row from one value held in memory and two calls into the node's own process, with no disk access, no lock and no message (FREQ-UPT-005). No request path of Apache Cassandra changes. The hook runs once at start (FREQ-UPT-010) |
| Performance efficiency | Memory budgets on coordinator and replica | Does not apply. A node that shows the view holds one table object, one counter and one number for it. A node that hides it holds one boolean field |
| Reliability | Isolation levers on coordinator and replica: thread pools, limits, load shedding, timeouts, kill switch | The feature starts no thread and has no queue, so it has no pool, limit or timeout to set. The switch is its kill switch (FREQ-UPT-009, FREQ-UPT-013) |
| Reliability | Automatic fallbacks opt-in, with yaml setting, nodetool toggle, metric and rate-limited log line | The feature has no fallback. A fault in the hook ends the start of the node (FREQ-UPT-023) |
| Reliability | Coordination between nodes model checked, when the design changes it | Does not apply. Nodes exchange nothing for this feature (FREQ-UPT-005) |
| Compatibility | Stock Apache Cassandra behaviour unchanged | FREQ-UPT-007, FREQ-UPT-008, FREQ-UPT-009 and FREQ-UPT-016 to FREQ-UPT-019. Section 2.8 lists what changes while the view is shown |
| Compatibility | Stock behaviour unchanged with the feature off | FREQ-UPT-016 to FREQ-UPT-019. Section 2.8 names the one thing present on every node, the row of the setting, and the three departures from the switch rules, each with its decision record |
| Compatibility | Mixed-version cluster, upgrade and rollback (see the Compatibility section) | Section 7, FREQ-UPT-028 |
| Functional suitability | CQL validity and results independent of replication factor, data centres and replica count | FREQ-UPT-005. The row depends on the node that executes the statement only. Whether a statement that names the view is valid depends on the switch of that node, never on the topology |
| Flexibility | Settings per index or per table over global ones, with global, include and exclude modes | Does not apply. The feature has no behaviour that depends on data. Its one setting is a switch for the node |
| Interaction capability | nodetool toggles change the in-memory value only, yaml holds the startup value | Does not apply. The switch has no nodetool toggle (decision record 0007, FREQ-UPT-024) |
| Interaction capability | Error messages name the setting or toggle that controls the behaviour | The feature raises no error of its own. A hidden view gets Apache Cassandra's answer for a table that does not exist, which does not name the setting (decision record 0010, FREQ-UPT-016). The WARN line before the final gate names the setting (FREQ-UPT-014), and so does the reference page (FREQ-UPT-025) |
| Maintainability | Observability: metrics, traces and diagnostics as a gate item | The read counter (FREQ-UPT-020, FREQ-UPT-021), the INFO line (FREQ-UPT-022) and the WARN line (FREQ-UPT-014). No trace line, because the feature has no plan decision and no fallback. No runtime change of a setting exists to log. The counter lives as long as the view does, until the node stops |
| Security | Threat model answered (see the Threat model section) | Section 6 |
| Safety | Any risk of data loss or corruption named, with its mitigation | The feature reads no user data and writes no file. One row of a system table goes by Apache Cassandra's own code: a stored prepared statement on the view is removed at a start with the view hidden (C9). A client prepares it again once the view is shown |

## 6. Threat model

| Entry point | Threat (STRIDE) | Mitigation | FREQ |
|---|---|---|---|
| A `SELECT` on the view over CQL | Information disclosure: a client learns when a node last started | The view is off by default. Apache Cassandra's permission rule for `system_views` decides who reads it. The feature adds no permission code | FREQ-UPT-007, FREQ-UPT-009 |
| A `SELECT` on the view over CQL, on a node whose authorizer requires no authorization | Information disclosure: every client reads the row once the view is shown | The view follows the rule of the other tables of `system_views`, which every client of such a node reads already. The view is off by default, and the reference page warns about this case | FREQ-UPT-009, FREQ-UPT-025 |
| A `SELECT` on the view over CQL | Information disclosure: while the view is shown, every logged in user sees its name in the table listings and learns that the node runs ChronitonDB | Accepted while the switch is on. With the switch off, the listings are the ones of Apache Cassandra | FREQ-UPT-013, FREQ-UPT-017 |
| A `SELECT` on the view over CQL | Denial of service: a client reads the view in a loop | None needed. A read builds one row from values of the node's own process, with no disk access, no lock and no message to another node | FREQ-UPT-005 |
| A write or a `TRUNCATE` on the view over CQL | Tampering: a client changes what the view shows | The view is read only | FREQ-UPT-008 |
| A statement that names the hidden view | Information disclosure: the answer tells a client that the node runs ChronitonDB | The view is not in the table list, so the answer is the one Apache Cassandra gives for a table that does not exist, from Apache Cassandra's own code | FREQ-UPT-016 |
| A `GRANT` on the keyspace `system_views` | Information disclosure: a role that should read only the view reads every table of `system_views` | The reference page gives the grant on the view and warns about the grant on the keyspace. The grant rule itself is Apache Cassandra's | FREQ-UPT-025 |
| The read counter over JMX | Information disclosure: whoever reads the node's MBeans sees the name of the counter and learns that the node runs ChronitonDB and shows the view | The counter exists only on a node that shows the view. It holds a count and no start time | FREQ-UPT-018, FREQ-UPT-024 |
| The yaml setting `uptime_view_enabled` | Tampering: someone who can edit `cassandra.yaml` and restart the node shows the view | No new threat. Whoever edits that file already controls the node. Showing the view gives no read access, since the CQL permission rule still applies | FREQ-UPT-007, FREQ-UPT-009 |
| The yaml setting `uptime_view_enabled` | Repudiation: the switch changes and nothing shows that it did | The state of the view changes only at a start, and the start log line that prints the configuration shows the value (C8). Nothing can change it while the node runs | FREQ-UPT-011, FREQ-UPT-024 |

## 7. Compatibility

### 7.1 On-disk format changes

This feature changes no format, schema or protocol. A virtual table has no file on disk and no row in the schema tables. The feature adds no native protocol message and no message between nodes.

### 7.2 Mixed-version cluster

1. A read of the view on a node that shows it returns that node's own row, whatever the other nodes run.
2. A read of the view on an Apache Cassandra node, on an older ChronitonDB build, or on a node where the view is hidden gets the missing table error.
3. A driver can send a statement to any node. An operator who wants one node's row reads the view over a connection to that node, as cqlsh makes.
4. Grants are stored for the whole cluster, and the view exists per node. A `GRANT` on the view succeeds only on a node that shows it (C7). Once made, it counts on every node that shows the view.
5. Nodes exchange nothing for this feature, so a node without it is not affected by a node with it.
6. The read counter exists only on a node that shows the view. A monitoring tool that reads it finds no such MBean on an Apache Cassandra node, on an older ChronitonDB build, or on a node where the view is hidden.

### 7.3 Upgrade path and prerequisites

An upgrade from Apache Cassandra 5.0, or from an older ChronitonDB build of the line, needs nothing for this feature. The setting defaults to `false`, so an upgraded node behaves as before until an operator sets the switch and restarts the node. An operator who wants the view during a rolling upgrade adds the setting to the `cassandra.yaml` of a node after the node stopped on its old binary and before it starts on the new one. A node that starts on its old binary with the setting in its `cassandra.yaml` does not start (C8). The setting is not part of the line's minimum setup.

### 7.4 Rollback path

Before a node runs an Apache Cassandra binary, or a ChronitonDB build older than this feature, one step is needed on that node: remove `uptime_view_enabled` from its `cassandra.yaml`. Apache Cassandra refuses to start with a setting it does not know (C8).

Grants on the view need no step on each node, since grants are stored for the whole cluster. The rule of section 2.2, Access, applies once for the cluster: revoke the grants made on the view over a connection to a node that shows it, before the last node that shows the view is rolled back or restarted with the view hidden. A grant on the keyspace `system_views` is Apache Cassandra's own and can stay or be revoked at any time, on any node.

Nothing has to be dropped or rebuilt on disk. A prepared statement on the view that the node stored is removed at the next start, with one warning in the log (C9). The read counter is gone with the process that held it.

### 7.5 Runbook entries

No runbook page exists on this line yet. The feature adds the reference page `docs/reference/node-uptime-view.md`, in the folder the merged [design record of the commit log disk check](../CLD-commitlog-disk-check/design-record.md) uses for its page. The page holds the upgrade order of section 7.3, the rollback step of section 7.4, the rule for grants and the way back after a throwable in the hook, until the line's runbooks exist. The feature also adds an entry in `NEWS-chronitondb.txt` with the upgrade order and the rollback step (FREQ-UPT-028).

## 8. Dependencies

No new dependency.

## 9. Risks

| Id | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| R1 | Other work on the line adds a table to `system_views` or a field to `Config.java` at the same time. The build details view of issue #141 does both and is not merged when this is written | Medium | Two pull requests conflict in a stock file, or one feature's table drops out of `system_views` when both are on the line | This feature adds its view to the list Apache Cassandra itself builds and registers, so code that reads the tables of `SystemViewsKeyspace.instance` finds the view. The work that merges second resolves the conflict, and the test of problem 2 runs with both on the line |
| R2 | An import from Apache Cassandra changes the constructor of `SystemViewsKeyspace` (C1) | Low | The import conflicts at the entry of the hook | The edit is one entry at the end of the list. The integrator keeps it at the end, and the tests of problems 1 and 2 fail if it is lost |
| R3 | No scenario module and no parity suite exist on the line | High | The switch off proof rests on in-JVM distributed tests written for this feature | The tests of problem 7 compare the answers of a node that hides the view with the answers for a table that does not exist, and Apache Cassandra's own tests run unchanged with the switch off |
| R4 | A fault in the hook, in the code or in one build, shows only on a node whose configuration turns the view on | Low | That node does not start until the fault is fixed or the setting is removed from its `cassandra.yaml` | The tests of problem 1 run the hook on every build. The switch is off by default, the reference page gives the way back (FREQ-UPT-030), and a rolling restart shows the fault on the first node |

## 10. Decisions

1. [0007. The node uptime view is switched by its yaml setting only](../../decisions/0007-node-uptime-view-switched-by-yaml-setting-only.md): no nodetool command and no MBean for the switch, and a change needs a restart.
2. [0008. A node starts with the node uptime view hidden when its configuration turns the view on before the final gate](../../decisions/0008-node-uptime-view-hidden-before-the-final-gate.md): one warning, and never a refusal to start.
3. [0009. The node uptime view shows the start time read once at start](../../decisions/0009-node-uptime-view-start-time-read-once-at-start.md): the start time changes only at a restart, and after a clock change it can differ from the clock less the uptime.
4. [0010. A hidden node uptime view answers as a table that does not exist](../../decisions/0010-hidden-node-uptime-view-answers-as-a-missing-table.md): no error names the switch.

## 11. Milestones outline

The delivery plan gives the detail and proposes the line.

1. **Milestone 1, the view under test.** The setting, the hook with the final gate not passed, the time source, the view and the read counter. It makes testable: a granted role reads the row, the values equal those of `nodetool info`, and a hidden view answers as Apache Cassandra does. The view is shown by tests only, and a node whose configuration turns it on starts with the view hidden.
2. **Milestone 2, operators can switch the view.** The reference page and the `NEWS-chronitondb.txt` entry, and the passing of the final gate. It makes testable: the feature end to end through `cassandra.yaml` and a restart, and the rollback step and the rule for grants on the page. This is the final milestone.

## 12. Prior art

These rules apply to every source:

1. Describe and cite behaviour, published designs, papers, public documentation and code under licences compatible with the Apache License 2.0.
2. Code or text under an incompatible licence, for example the Elastic License, SSPL, BUSL or a proprietary licence, MUST NOT be copied. The behaviour of such a system is taken only from its public documentation. Code under a compatible licence MAY be used only with credit. See [conventions.md](../../process/conventions.md#code-from-elsewhere).
3. Contributors working on the project's behalf MUST NOT search for or read patents for design work. Any patent concern goes to the maintainers.

**Apache Cassandra.** Three sources are kept apart.

- Our line: ChronitonDB chronitondb-sandbox at `17e0b84a36`.
- Apache base: Apache Cassandra cassandra-5.0 at `76550e9314`. No file under `src/` or `test/` differs between the Apache base and our line. So each fact below holds in the Apache base at the same file and line as on our line.
- Apache now: Apache Cassandra cassandra-5.0 at `41fb172e73`, cassandra-6.0 at `ee7b57dfef` and trunk at `1085b1823f`.

Apache Cassandra shows the uptime of a node's process through `nodetool info` only, over JMX (C11). No table of `system_views` on our line holds a start time or an uptime of the process (C1). `system_views.gossip_info` has a `generation` column for each node, `GossipInfoTable.getGeneration`, `src/java/org/apache/cassandra/db/virtual/GossipInfoTable.java:118`, ChronitonDB chronitondb-sandbox at `17e0b84a36`. It holds the gossip generation of a node and not the start time of its process, and the issue asks for the start time and the uptime. Apache now adds a table `system_views.local` on cassandra-6.0 and trunk, with a `gossip_generation` column and no start time and no uptime (C1). The view takes its place in `system_views` from Apache Cassandra's own node views, its `key` column with the value `local` from `system.local`, and its uptime from the call `nodetool info` makes.

| Id | What the code does | Our line | Apache now |
|---|---|---|---|
| C1 | The tables of `system_views` are a fixed list that the constructor builds, once, when the class loads. Some entries are `addAll` calls that take a list from another class. No table holds a start time or an uptime of the process | `SystemViewsKeyspace.SystemViewsKeyspace`, `src/java/org/apache/cassandra/db/virtual/SystemViewsKeyspace.java:30`, the list from line 32, an `addAll` entry at line 55, ChronitonDB chronitondb-sandbox at `17e0b84a36` | The same file in Apache Cassandra cassandra-5.0 at `41fb172e73`. A longer list in `SystemViewsKeyspace.java:33`, the list from line 35, with `LocalTable` at line 69, Apache Cassandra trunk at `1085b1823f`, the same in cassandra-6.0 at `ee7b57dfef`. `LocalTable.LocalTable`, `src/java/org/apache/cassandra/db/virtual/LocalTable.java:71`, has the column `gossip_generation` at line 84 and no start time or uptime, in both |
| C2 | The node registers `system_views` once at start, in the one place that reads `SystemViewsKeyspace.instance`. The in-JVM distributed test node calls the same method | `CassandraDaemon.setupVirtualKeyspaces`, `src/java/org/apache/cassandra/service/CassandraDaemon.java:534`, the registration at line 537, and `Instance.startup`, `test/distributed/org/apache/cassandra/distributed/impl/Instance.java:581`, the call at line 650, ChronitonDB chronitondb-sandbox at `17e0b84a36` | `CassandraDaemon.java:534`, Apache Cassandra cassandra-5.0 at `41fb172e73`. `CassandraDaemon.java:641`, Apache Cassandra cassandra-6.0 at `ee7b57dfef` and trunk at `1085b1823f`. `Instance` was not read on Apache now |
| C3 | At start the node starts its JMX server, registers its virtual keyspaces, loads its stored prepared statements and then sets up its client transports, in this order. It registers the virtual keyspaces with no guard around the call. A throwable that leaves the start code ends the start: the node logs `Exception encountered during startup` with the throwable and exits | `CassandraDaemon.setup`, `src/java/org/apache/cassandra/service/CassandraDaemon.java:229`, the four calls at lines 246, 291, 377 and 443, and `CassandraDaemon.activate` at line 718 with its call of `exitOrFail` at line 759, ChronitonDB chronitondb-sandbox at `17e0b84a36` | The same lines in Apache Cassandra cassandra-5.0 at `41fb172e73`. `CassandraDaemon.setup`, `CassandraDaemon.java:244`, the four calls at lines 261, 331, 394 and 447, and the call of `exitOrFail` at line 874, Apache Cassandra cassandra-6.0 at `ee7b57dfef` and trunk at `1085b1823f` |
| C4 | A statement finds its table by name in the keyspace's table list, and a missing one fails with `table <name> does not exist` | `Schema.validateTable`, `src/java/org/apache/cassandra/schema/Schema.java:429`, the error at line 440, ChronitonDB chronitondb-sandbox at `17e0b84a36` | `Schema.java:429` and line 440, Apache Cassandra cassandra-5.0 at `41fb172e73`. `SchemaProvider.validateTable`, `src/java/org/apache/cassandra/schema/SchemaProvider.java:95`, the same text at line 106, Apache Cassandra cassandra-6.0 at `ee7b57dfef` and trunk at `1085b1823f` |
| C5 | The listings read every table of every registered virtual keyspace | `VirtualSchemaKeyspace.VirtualTables.data`, `src/java/org/apache/cassandra/db/virtual/VirtualSchemaKeyspace.java:83`, and `DescribeStatement.executeLocally`, `src/java/org/apache/cassandra/cql3/statements/DescribeStatement.java:135`, ChronitonDB chronitondb-sandbox at `17e0b84a36` | `VirtualSchemaKeyspace.java:83`, Apache Cassandra cassandra-5.0 at `41fb172e73`. `VirtualSchemaKeyspace.java:84`, Apache Cassandra cassandra-6.0 at `ee7b57dfef` and trunk at `1085b1823f`. `DescribeStatement` was not read on Apache now |
| C6 | With no authorization required every client passes. Otherwise an ordinary role needs a grant on the table or its keyspace for a system keyspace, and a grant on all keyspaces does not count. The tables of `system_virtual_schema` are readable by every logged in user | `ClientState.ensurePermission`, `src/java/org/apache/cassandra/service/ClientState.java:475`, the return for no authorization at line 477, the system keyspace rule at line 495, and the static initialiser of `ClientState` at line 92, ChronitonDB chronitondb-sandbox at `17e0b84a36` | The same lines in Apache Cassandra cassandra-5.0 at `41fb172e73`. `ClientState.java:510`, line 530 and line 99, Apache Cassandra cassandra-6.0 at `ee7b57dfef` and trunk at `1085b1823f` |
| C7 | `GRANT` and `REVOKE` fail with `Resource <resource> doesn't exist` when the table is not found by name. A keyspace level resource of a virtual system keyspace always exists. Grants are kept in the table `system_auth.role_permissions`. Dropping a role removes every grant made to it | `PermissionsManagementStatement.validate`, `src/java/org/apache/cassandra/cql3/statements/PermissionsManagementStatement.java:45`, the error at line 58, `DataResource.exists`, `src/java/org/apache/cassandra/auth/DataResource.java:245`, the class comment of `CassandraAuthorizer`, `src/java/org/apache/cassandra/auth/CassandraAuthorizer.java:56`, and `DropRoleStatement.execute`, `src/java/org/apache/cassandra/cql3/statements/DropRoleStatement.java:67`, the call of `revokeAllFrom` at line 75, ChronitonDB chronitondb-sandbox at `17e0b84a36` | `PermissionsManagementStatement.java:45`, line 58 and `DataResource.java:245`, Apache Cassandra cassandra-5.0 at `41fb172e73`. `PermissionsManagementStatement.java:48`, line 61 and `DataResource.java:246`, Apache Cassandra cassandra-6.0 at `ee7b57dfef` and trunk at `1085b1823f`. `CassandraAuthorizer` and `DropRoleStatement` were not read on Apache now |
| C8 | A yaml key with no field in `Config` stops the start with `Invalid yaml. Please remove properties`. The settings table lists every field of `Config`, and the node logs every field once when it loads its configuration | `YamlConfigurationLoader.PropertiesChecker.check`, `src/java/org/apache/cassandra/config/YamlConfigurationLoader.java:417`, the error at line 423, `SettingsTable.getProperties`, `src/java/org/apache/cassandra/db/virtual/SettingsTable.java:151`, and `Config.log`, `src/java/org/apache/cassandra/config/Config.java:1347`, ChronitonDB chronitondb-sandbox at `17e0b84a36` | The same lines in Apache Cassandra cassandra-5.0 at `41fb172e73`. `YamlConfigurationLoader.java:554` with the error at line 560, Apache Cassandra cassandra-6.0 at `ee7b57dfef` and trunk at `1085b1823f`, with `SettingsTable.java:152` and `Config.java:1557` on cassandra-6.0, and `SettingsTable.java:153` and `Config.java:1561` on trunk |
| C9 | At start the node prepares again each statement it stored. One that cannot be prepared again is logged in a warning with its text and removed from the store | `QueryProcessor.preloadPreparedStatements`, `src/java/org/apache/cassandra/cql3/QueryProcessor.java:171`, the warning at line 192 and the removal at line 193, ChronitonDB chronitondb-sandbox at `17e0b84a36` | The same lines in Apache Cassandra cassandra-5.0 at `41fb172e73`. `QueryProcessor.java:208`, the warning at line 229 and the removal at line 230, Apache Cassandra cassandra-6.0 at `ee7b57dfef` and trunk at `1085b1823f` |
| C10 | A virtual table built on `AbstractVirtualTable` answers both kinds of read from its `data()` method, the read of one key through `data(DecoratedKey)`. It refuses writes with `Modification is not supported by table` and truncation with `Truncation is not supported by table` | `AbstractVirtualTable.data`, `src/java/org/apache/cassandra/db/virtual/AbstractVirtualTable.java:66` and line 72, `AbstractVirtualTable.select` at lines 78 and 91, `AbstractVirtualTable.apply` at line 126 and `AbstractVirtualTable.truncate` at line 132, ChronitonDB chronitondb-sandbox at `17e0b84a36` | The same file in Apache Cassandra cassandra-5.0 at `41fb172e73`. `AbstractVirtualTable.java:68`, line 128 and line 134, Apache Cassandra cassandra-6.0 at `ee7b57dfef` and trunk at `1085b1823f`, where the read of a range at line 93 also takes a row filter and limits |
| C11 | `nodetool info` prints the host id on its `ID` line and the uptime on its `Uptime (seconds)` line. The uptime is `RuntimeMXBean.getUptime()` of the node's JVM, read over JMX and divided by 1000 as whole numbers. The host id is the one `StorageService.getLocalHostUUID` returns | `Info.execute`, `src/java/org/apache/cassandra/tools/nodetool/Info.java:48`, the `ID` line at line 53 and the uptime at line 65, `NodeProbe.getUptime`, `src/java/org/apache/cassandra/tools/NodeProbe.java:874`, with the proxy of the `RuntimeMXBean` made at line 331, and `StorageService.getLocalHostUUID`, `src/java/org/apache/cassandra/service/StorageService.java:2707`, ChronitonDB chronitondb-sandbox at `17e0b84a36` | The same lines in Apache Cassandra cassandra-5.0 at `41fb172e73`. `Info.java:49` and line 61 on cassandra-6.0 at `ee7b57dfef` and trunk at `1085b1823f`, with `NodeProbe.java:921` and `StorageService.java:2054` on cassandra-6.0, and `NodeProbe.java:942` and `StorageService.java:2055` on trunk |
| C12 | The metrics registry registers a counter under its registry name and as an MBean under the MBean name its `MetricName` carries. The registry name joins the group, the type, the name and the scope with dots. The five argument constructor of `MetricName` takes the MBean name as it is written | `CassandraMetricsRegistry.counter`, `src/java/org/apache/cassandra/metrics/CassandraMetricsRegistry.java:55`, the five argument constructor of `CassandraMetricsRegistry.MetricName` at line 818 and `MetricName.getMetricName` at line 872, ChronitonDB chronitondb-sandbox at `17e0b84a36` | The same lines in Apache Cassandra cassandra-5.0 at `41fb172e73`. On cassandra-6.0 at `ee7b57dfef` and trunk at `1085b1823f` the constructor is at line 1201 and `getMetricName` at line 1271, and the registry refuses a metric whose type is not in its fixed set of metric groups: `CassandraMetricsRegistry.verifyUnknownMetric`, `CassandraMetricsRegistry.java:272`, called at line 438 |
| C13 | A read of a virtual table calls one of the two `select` methods of the table: once for each partition key the statement names, or once for a range. A statement's permission check runs before the statement is executed. A `SELECT` is executed in pages when the client sets a page size smaller than the statement's limit, and each page the client fetches is a new read | `SinglePartitionReadCommand.VirtualTableSinglePartitionReadCommand.executeLocally`, `src/java/org/apache/cassandra/db/SinglePartitionReadCommand.java:1413`, `PartitionRangeReadCommand.VirtualTablePartitionRangeReadCommand.executeLocally`, `src/java/org/apache/cassandra/db/PartitionRangeReadCommand.java:553`, `QueryProcessor.processStatement`, `src/java/org/apache/cassandra/cql3/QueryProcessor.java:266`, with the permission check at line 271 and the execution at line 276, `SelectStatement.execute`, `src/java/org/apache/cassandra/cql3/statements/SelectStatement.java:280`, with the choice of paging at line 338, `AbstractQueryPager.fetchPage`, `src/java/org/apache/cassandra/service/pager/AbstractQueryPager.java:63`, with the new read at line 70, and `DataLimits.isExhausted`, `src/java/org/apache/cassandra/db/filter/DataLimits.java:139`, ChronitonDB chronitondb-sandbox at `17e0b84a36` | `SinglePartitionReadCommand.java:1413`, `PartitionRangeReadCommand.java:553` and `QueryProcessor.java:266`, Apache Cassandra cassandra-5.0 at `41fb172e73`. `SinglePartitionReadCommand.java:1572`, `PartitionRangeReadCommand.java:652` and `QueryProcessor.java:302`, Apache Cassandra cassandra-6.0 at `ee7b57dfef` and trunk at `1085b1823f`. `SelectStatement`, `AbstractQueryPager` and `DataLimits` were not read on Apache now |
| C14 | A test of the in-JVM distributed test framework can rewrite a class inside a test node's class loader before the node starts. Each test node is a class loader inside the JVM of the test, and the framework builds a new one at each start of a test node and runs the test's initializer on it again. A test node registers no MBean unless its test starts it with the JMX feature of the framework | `ByteBuddyExamplesTest.writeFailureTest`, `test/distributed/org/apache/cassandra/distributed/test/ByteBuddyExamplesTest.java:51`, the initializer at line 54, `AbstractCluster.Wrapper.newInstance`, `test/distributed/org/apache/cassandra/distributed/impl/AbstractCluster.java:299`, the class loader at line 303 and the call of the initializer at line 306, `MBeanWrapper.getMBeanWrapper`, `src/java/org/apache/cassandra/utils/MBeanWrapper.java:61`, the wrapper that registers nothing at line 73, and `Instance.startJmx`, `test/distributed/org/apache/cassandra/distributed/impl/Instance.java:776`, ChronitonDB chronitondb-sandbox at `17e0b84a36` | Not read on Apache now |

What Apache now means for this feature: the next import of cassandra-5.0 changes none of the lines above that were read there. A port to a line based on Apache Cassandra 6.0 finds a longer table list with the same `addAll` form (C1), so the hook has the same place there. It finds a metrics registry that refuses a metric type it does not list (C12), so the read counter needs its own answer there, which that port designs. It also finds `system_views.local`, which shows the gossip generation and no uptime (C1), so the view is not made redundant by it.

**OpenSearch.** OpenSearch reports both values of a node's JVM in its node APIs. It reads the start time once, when the class that holds the JVM details loads: the static initialiser of `JvmInfo`, `server/src/main/java/org/opensearch/monitor/jvm/JvmInfo.java:83`, with the read of `RuntimeMXBean.getStartTime()` at line 199, OpenSearch main at `00d9641beb`. It reads the uptime at each request for the node statistics: `JvmStats.jvmStats`, `server/src/main/java/org/opensearch/monitor/jvm/JvmStats.java:79`, with the read of `RuntimeMXBean.getUptime()` at line 155, OpenSearch main at `00d9641beb`. Its node listing has an `uptime` column for every node from one request: `RestNodesAction`, `server/src/main/java/org/opensearch/rest/action/cat/RestNodesAction.java:201`, OpenSearch main at `00d9641beb`. The view follows the first two: a start time read once and an uptime read at each request, both from the JVM. It does not list every node from one request, because that needs a new value exchanged between nodes, and non-goal 1 leaves it out.

## Glossary

Not applicable: this section is required from Challenging size, and this feature is Normal size. Section 2.2 defines the terms this document uses: the view, the setting, the hook, the final gate, the time source, the read counter, shown and hidden.
