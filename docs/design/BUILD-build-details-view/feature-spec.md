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

# Feature spec: Build details view in CQL

| Field | Value |
|---|---|
| Title | Build details view in CQL |
| Document type | Specification and description (ISO/IEC/IEEE 15289) |
| Status | Draft |
| Version | 1 |
| Author | Architect: chronitondb-agent |
| Approver | The maintainer who merges the pull request |
| References | Issue #141. Line `chronitondb-sandbox`. Apache base commit `76550e931481e965ae3283d8cf4a59c320d74c55` (Apache Cassandra `cassandra-5.0`, build version 5.0.10). The [design record of `nodetool version`](../VER-release-version/design-record.md). Decision records 0002, 0003 and 0007 to 0015. |
| Risk | Normal: the worst Bug Category is Availability, a response crash, where a read of the view or of another table of `system_views` fails. A start step that let an exception out would stop the node from starting, an Availability fault that [classification.md](../../process/classification.md#risk) rates Critical. FREQ-BUILD-027 is written to exclude it. Decision record 0010 keeps the feature at Normal risk, also for a fault that shows the build details to a client that should not see them. The floor of [classification.md](../../process/classification.md#the-floor) applies, because the feature adds a virtual table, a configuration setting and a metric. |
| Size | Normal: one view, its yaml setting, one rule applied at start, one internal check, one read counter, and the build key with its reader. It needs no analysis beyond the virtual table code. |
| Reach | One area: virtual tables. Fork code in `org.chronitondb.version` and `org.chronitondb.compat`, with hooks in `org.apache.cassandra.config` and `org.apache.cassandra.service`, and one entry in `build.xml`. |
| Touches | public interface (virtual tables), public interface (configuration), public interface (jmx mbeans, including metrics), stock behaviour, new input or privilege, shared state, new feature or switch |

Change history: the git history of this file.

Location: `docs/design/BUILD-build-details-view/feature-spec.md` on the line `chronitondb-sandbox`. The feature key is `BUILD`, a new key. The view has its own switch, and [release.md](../../process/release.md#the-version-a-running-node-reports) treats what sits behind its own switch as its own feature, so the view does not take the key `VER` of `nodetool version`. See [Feature keys and requirement ids](../../process/additive.md#feature-keys-and-requirement-ids). Process: [additive.md](../../process/additive.md).

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in BCP 14 (RFC 2119, RFC 8174) when, and only when, they appear in all capitals, as shown here.

The Risk, Size and Reach rows are the feature's class, as [classification.md](../../process/classification.md) defines it, and match the issue's `risk:`, `size:` and `reach:` labels.

Two short names are used throughout. "The VER design record" is the merged [design record of `nodetool version`](../VER-release-version/design-record.md), whose requirements are `REQ-VER-nnn`. A code fact is cited as C1 to C18, and section 12 holds each one with its symbol, file, line and the tree it was read in.

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

During a rolling upgrade an operator needs to know which ChronitonDB release each node runs. Over CQL a node shows only its Apache Cassandra version, in `system.local` (C9). It never shows its ChronitonDB release. Operators and the monitoring roles they set up often reach a node over CQL only.

This feature adds one read-only virtual table, `system_views.chronitondb_build`, called the view in this document. It holds one row with three values of the node that executes the statement: the ChronitonDB release version, the Apache Cassandra version in the build, and the git SHA of the build.

The users are operators who run upgrades, and the monitoring roles they grant.

In scope:

1. The view and its three values.
2. Its switch: the yaml setting `build_view_enabled`, which the node reads at start. The view is off by default, and a change of the switch needs a restart of the node (decision record 0011).
3. Access by Apache Cassandra's own permission rule for `system_views`: a superuser, or a role granted `SELECT`. On a node whose authorizer requires no authorization, that rule lets every client read (decision record 0012).
4. A node that hides the view answers every statement that names the view, and every table listing, as Apache Cassandra does. Section 2.8 lists what is present on every node whatever the switch says.
5. One internal check that hides the view while Apache compatibility mode is on.
6. The build key and the reader class that give the release version, shared with `nodetool version`.
7. One counter of the reads of the view, which exists only on a node that shows the view (decision record 0014).
8. A reference page.

### Non-goals

1. The build of every node from one connection. A node answers for itself only, so nodes exchange nothing new.
2. The newest Apache Cassandra release the line fully contains. The view shows the version in the build, the string Apache Cassandra itself reports. The release notes name the other one.
3. A change to `system.local`, `system.peers_v2`, the cqlsh banner, `SHOW VERSION` or `bin/cassandra -v`. [release.md](../../process/release.md#the-version-a-running-node-reports) keeps them as they are.
4. A change to what `nodetool version` prints. The VER design record owns that. This feature adds only the build key and the reader that both share.
5. Building Apache compatibility mode. This feature only obeys it, through the check of decision record 0008.
6. A change to permission code. The view relies on the rule Apache Cassandra has. A design that needs a change there is not this feature.
7. An error that names the switch while the view is off. Decision record 0009 chose the Apache Cassandra answer for a table that does not exist.
8. Other values, such as a build date. The view holds three values.
9. Other lines. The feature is specified for `chronitondb-sandbox`. A port to another line is its own work, and section 12 names what differs on Apache Cassandra 6.0.
10. A nodetool command, or an MBean that reads or changes the switch. Decision record 0011 chose the yaml setting only, so nothing changes the switch while the node runs. The one MBean of the feature is the one Apache Cassandra creates for the read counter (decision record 0014).

## 2. Architecture

The feature is small. A build step writes the release version into a file inside the jar. One class reads it. One virtual table shows it with two values Apache Cassandra already holds. At start, one rule decides whether the node registers `system_views` again with that table added. The state of the view never changes while the node runs. A node that shows the view counts the reads of it.

### 2.1 Context and scope

The feature runs inside one node and talks to nothing outside it.

1. **A CQL client**: an operator with cqlsh or a monitoring role with a driver. It reads the view on the node its connection reaches.
2. **An operator who edits `cassandra.yaml`**: sets the switch and restarts the node.
3. **The build**: Ant writes the release version into `org/apache/cassandra/config/version.properties` (C10).
4. **Apache Cassandra subsystems inside the node**: the virtual keyspace registry (C2, C3), the configuration (C11), the metrics registry (C16) and the log.
5. **Later work, outside this feature**: the work that builds Apache compatibility mode fills the internal check. The `nodetool version` work reuses the build key and the reader.

The feature sends no message to another node, writes no file on a node's disk and starts no thread. Its one MBean is the one of the read counter, and only a node that shows the view has it.

### 2.2 Building blocks

| Block | Where it lives | What it does |
|---|---|---|
| Build key | `build.xml`, target `_createVersionPropFile` | Writes the key `ReleaseVersion` into `version.properties`, as REQ-VER-025 and REQ-VER-033 of the VER design record define it |
| Release version reader | `org.chronitondb.version.ReleaseVersion` | Reads the key once and returns the release version, as REQ-VER-006 and REQ-VER-007 of the VER design record define it |
| The view | `org.chronitondb.version` | A read-only virtual table built on `AbstractVirtualTable` (C13). It builds one row from the reader and from `FBUtilities` (C9) |
| The rule | `org.chronitondb.version` | One function that takes its three conditions as arguments and returns shown or hidden |
| The start step | `org.chronitondb.version` | Reads the three conditions once at start and applies the rule. When the rule says shown, it creates the read counter and registers `system_views` with the view added. It takes no argument and lets no exception out |
| The read counter | `org.chronitondb.version` | One counter, `org.chronitondb.metrics:type=BuildView,name=Reads`. It exists only on a node that shows the view, and the view raises it at each read (decision record 0014) |
| Apache compatibility check | `org.chronitondb.compat` | One class with one method that says whether Apache compatibility mode is on, and no state. It answers off, until the work that builds the mode changes it (decision record 0008) |
| The setting | the field `build_view_enabled` in `Config.java` | Holds the value from `cassandra.yaml` |

The view has these columns:

| Column | Type | Kind | Value |
|---|---|---|---|
| `key` | text | partition key | always `local` |
| `release_version` | text | regular | the value the release version reader returns, for example `5.0-chronitondb2` |
| `apache_version` | text | regular | the value of `FBUtilities.getReleaseVersionString()`, for example `5.0.10` |
| `git_sha` | text | regular | the value of `FBUtilities.getGitSHA()`, the git SHA of the build as Apache Cassandra reports it |

A `SELECT` with a key filter or a column list is answered as `AbstractVirtualTable` answers it for every Apache Cassandra virtual table: a filter on another key returns no row, and a column list returns those columns.

The `apache_version` and `git_sha` values are the ones Apache Cassandra reports today through `StorageServiceMBean.getReleaseVersion()` and `getGitSHA()` (C9). The `release_version` and `git_sha` values are the ones `nodetool version` prints once the VER design record is built, because the view and that command read them from the same reader and the same `FBUtilities` method. The values a build without a release version or without a git SHA gives are the ones REQ-VER-007 of the VER design record and `FBUtilities` define. The view adds none of its own.

**Shown and hidden.** The view is in one of two states on a node, shown or hidden. The node decides the state once, at start, and keeps it until the node stops. The view is shown when all three of these hold at start, and hidden when any one does not:

1. The setting `build_view_enabled` is `true` in the configuration the node loaded.
2. The Apache compatibility check answers off.
3. The final gate is passed.

The final gate is the feature's final milestone gate of [additive.md](../../process/additive.md#milestone-gates). In the code it is one constant, which the last item of the final milestone sets. Until then the view stays hidden on every node, whatever the configuration the node loaded holds. A node whose loaded configuration sets the switch to `true` before the final gate starts as any other node does, keeps the view hidden and logs one warning that names the setting (decision record 0013). It never refuses to start for this reason. [branching-and-review.md](../../process/branching-and-review.md#feature-switches-and-defaults) item 2 says that the switch refuses to turn on before the final milestone gate, and names no form. Decision record 0013 chose this form. The feature never writes the field of the setting, so `system_views.settings` shows the value the node loaded, `true` on such a node, whatever the state of the view.

**How the node shows the view.** Apache Cassandra builds the table list of `system_views` once, when the class loads (C1), and registers the keyspace at start (C2). The registry replaces a keyspace by name (C3). The start step runs right after Apache Cassandra registered its virtual keyspaces. At that point the node has not yet loaded its stored prepared statements and accepts no client connection (C5). When the rule says shown, the start step does four things in this order. It builds a keyspace named `system_views` that holds the table objects of `SystemViewsKeyspace.instance` and the view. It creates the read counter. It registers the keyspace. It logs one INFO line that names the view. The table objects of Apache Cassandra are reused, never built again, since some of them hold state. When the rule says hidden, the start step registers nothing and creates no counter, and the registry stays as Apache Cassandra left it.

The start step lets no exception out: when one is thrown, the node logs an error that names the view and goes on with its start (FREQ-BUILD-027, FREQ-BUILD-028). The view is shown from the moment the keyspace is registered, and the counter exists before that, so a shown view always has its counter. When an exception is thrown after the counter was created and before the keyspace is registered, the start step removes the counter again (C16), so the view stays hidden and the node holds no metric of the feature (FREQ-BUILD-031).

The start step writes a log line in three cases only: the INFO line when it shows the view, the warning before the final gate, and the error for an exception. On a node whose loaded configuration sets the switch to `false` it writes none (FREQ-BUILD-033). A node with the switch on, the final gate passed and the Apache compatibility check answering on gets no line from the start step either. No node is in that mode before the work that builds it, and that work decides what such a node logs.

**The read counter.** A node that shows the view counts the reads of the view (decision record 0014). The counter is `org.chronitondb.metrics:type=BuildView,name=Reads`. It has the feature's own metric type, `BuildView`, in the group `org.chronitondb.metrics`, as [conventions.md](../../process/conventions.md#names) items 3 and 4 ask, in the form the counters of the merged [design record of the commit log disk check](../CLD-commitlog-disk-check/design-record.md) have. Apache Cassandra registers each metric of its registry as an MBean (C16), so the counter shows over JMX and through any metrics reporter the node has configured. It is the one MBean of the feature.

The start step creates the counter only when the rule says shown. A node that hides the view holds no metric and no MBean of the feature. The counter lives until the node stops, as the shown state does. It starts at 0 at each start of the node and is stored nowhere.

The view raises the counter by one each time Apache Cassandra's read path asks the view for its data, which is each call of the view's `data()` method (C17). A `SELECT` with no key filter, or with a filter on one key value, is one read, also when the filter matches no row. A `SELECT` whose `IN` list names several key values is one read for each value. A `SELECT` that Apache Cassandra's permission check refuses does not reach the view and is not counted, since that check runs before the statement is executed (C17).

**What a hidden view looks like.** The view is not in the registry. A statement finds a table by name through the keyspace's table list (C4), so the view is not found and the statement gets the Apache Cassandra answer for a table that does not exist. The listings read the same table lists (C6), so they do not show it. All of this is Apache Cassandra's own code, which the feature does not touch.

A node stores the statements its clients prepared and loads them again at start (C12). A statement that reads the view, prepared while the view was shown, is in that store. When the node next starts with the view hidden, Apache Cassandra cannot prepare the statement again. It logs one warning that holds the statement's text and removes the statement from the store (C12). This is what Apache Cassandra does for a stored statement on any table that no longer exists. A client that executes the statement after that start gets the answer Apache Cassandra gives for a prepared statement it does not know, and preparing it again fails as for any table that does not exist.

**Access.** The view adds no permission check. Apache Cassandra checks `SELECT` on a table of `system_views` against grants on that table and on the keyspace `system_views`, and a grant on all keyspaces does not count (C7). A superuser passes. On a node whose authorizer requires no authorization, every client passes, as for every table of `system_views` (C7). That is the authorizer Apache Cassandra's `cassandra.yaml` ships with (C14). Decision record 0012 accepts it: once the view is shown on such a node, every client reads it. `GRANT` and `REVOKE` on a table need the table to exist on the node that runs the statement (C8), so a role is granted `SELECT` on the view on a node that shows it, or on the keyspace `system_views` on any node. The reference page gives the grant on the view as the way to let a role read it, because a grant on the keyspace also opens every other table of `system_views`.

A grant on the view can outlive the view. Grants are stored for the whole cluster, and a `REVOKE` that names the view fails on a node that does not show it (C8). The rule for operators is therefore one rule for the cluster, not one for each node: revoke a grant on the view over a connection to a node that shows the view, before the last node of the cluster that shows the view is restarted with the view hidden. Decision record 0015 accepts a grant that is left behind after that, and the reference page says what it does (FREQ-BUILD-035):

1. It gives no access while no node shows the view.
2. It gives its role the read again on every node that shows the view later.
3. It can be revoked on any node that shows the view, whenever one does.
4. It goes when its role is dropped, on any node, since Apache Cassandra removes every grant of a role it drops (C18).

The feature adds no code for a grant that is left behind.

**Tests that need a state shipped code cannot reach.** The rule is one function of its three conditions, so unit tests cover every row of it with no node. The start step takes no argument: it reads the setting, the check and the final gate itself. Two states are therefore reached by in-JVM distributed tests only: the view shown before the final gate, and the check answering on. For both, the test rewrites the code that answers inside the class loader of its test node, before the node starts, as Apache Cassandra's own in-JVM distributed tests do (C15). This rewrite is the mechanism inside the in-JVM distributed test framework that [testing.md](../../process/testing.md#scenarios) item 9 requires, and the test-only way of decision record 0008. Shipped classes hold no method, setting or property that passes the gate or changes the check's answer. The design record of the item that adds each test defines its rewrite.

### 2.3 Runtime view

1. **Start.** Apache Cassandra registers its virtual keyspaces (C2). The start step then applies the shown or hidden rule once. After that the node loads its stored prepared statements and opens client connections (C5).
2. **Read.** A `SELECT` on the view goes through Apache Cassandra's virtual table read path with no change to that path. The view raises the read counter and builds one row from three strings held in memory. No other request path is touched.

### 2.4 Data and formats

Not applicable: the feature adds no file on a node's disk, no wire form, no schema row and no cluster metadata. Section 2.2 holds the view's columns.

### 2.5 Cross cutting concepts

Not applicable: the feature has one group of components. Its setting is FREQ-BUILD-010, its log lines are FREQ-BUILD-018, FREQ-BUILD-028 and FREQ-BUILD-032, its metric is FREQ-BUILD-029 to FREQ-BUILD-031, and the errors a client gets are in FREQ-BUILD-015 and FREQ-BUILD-022.

### 2.6 Deployment

An operator gets one new yaml setting, `build_view_enabled`. No new file is written on a node. The jar's `version.properties` holds one more key. A node that shows the view has one more MBean, the read counter.

### 2.7 Package dependencies and hook points

| ChronitonDB package | MAY import |
|---|---|
| `org.chronitondb.version` | `org.chronitondb.compat`, and from Apache Cassandra `db.virtual`, `db.marshal`, `dht`, `schema`, `config`, `metrics` and `utils`. The JDK, SLF4J and Guava |
| `org.chronitondb.compat` | The JDK only |

No package of this feature imports `org.apache.cassandra.auth`, `org.apache.cassandra.transport`, `org.apache.cassandra.net`, `org.apache.cassandra.tools` or `org.apache.cassandra.service.ClientState`.

Hook points, each a stock file this feature edits:

| Stock file | Edit | Why | Delta entry |
|---|---|---|---|
| `build.xml` | One property, `chronitondb.version`, and one entry in the target `_createVersionPropFile` | The release version is read from the build (decision record 0007) | `docs/delta/release-version-in-build-properties.md` |
| `src/java/org/apache/cassandra/config/Config.java` | One field, `build_view_enabled`, default `false` | Apache Cassandra's loader refuses a yaml key that has no field (C11). The field imports no fork code | `docs/delta/build-details-view.md` |
| `src/java/org/apache/cassandra/service/CassandraDaemon.java` | One import and one line in `setupVirtualKeyspaces`, after the two registrations | The start step has to run after Apache Cassandra registered `system_views` (C2) | `docs/delta/build-details-view.md` |

The VER design record plans the same `build.xml` edit and its own entries in `Config.java` and `NodeTool.java`. Decision record 0007 says that record is updated through change control before its code starts, so that it reuses the build key, the reader and the delta entry of the first row, and so that its tests compare the first line of `nodetool version` with the `release_version` column of the view.

### 2.8 Feature class and switches

Feature class: behaviour-changing, because while the view is shown, operations Apache Cassandra already has return one more table.

| Switch | Class | Reason | Default per line | Apache Cassandra operations it changes |
|---|---|---|---|---|
| `build_view_enabled`, a yaml setting read at start | behaviour-changing | while on, the table listings of the node hold the view | `chronitondb-sandbox`: off | `SELECT` on `system_virtual_schema.tables` and `system_virtual_schema.columns`, and `DESCRIBE` statements that list or describe the tables of `system_views` (C6) |

While the view is shown, the node also holds the read counter, over JMX and in any metrics reporter it has configured. The counter has the feature's own metric type, so no metric of Apache Cassandra changes and none is added to a metric type of Apache Cassandra. A node that hides the view holds no such counter.

With the switch off the node answers every statement that names the view, and every table listing, as Apache Cassandra does. Two things are present on every node whatever the switch says, also while the Apache compatibility check answers on. Each is a departure from [branching-and-review.md](../../process/branching-and-review.md#feature-switches-and-defaults) item 7:

1. `system_views.settings` and the start log line that prints the configuration show one more setting, `build_view_enabled`, because Apache Cassandra lists every field of `Config` (C11). Decision record 0011 accepts it on every node, whatever the switch says. No node is in Apache compatibility mode before the work that builds the mode, since the check answers off until then (decision record 0008), so this feature decides nothing about the row on such a node.
2. The jar's `version.properties` holds one more key, `ReleaseVersion`. The VER design record already lists this one.

Two more departures from the same page:

1. The switch has no nodetool toggle, where item 1 asks for a yaml setting and a nodetool toggle. Decision record 0011 settles it. The switch cannot change while the node runs, so the node has no switch change to log. The start log line that prints the configuration shows the value the node started with (C11).
2. A statement that names the hidden view gets no error that names the switch, where item 7 asks for one. Decision record 0009 settles it.

## 3. Feature requirements

"The node" is the node that executes the statement. "Shown", "hidden", "the rule", "the start step" and "the final gate" are defined in section 2.2.

FREQ-BUILD-001 (state driven): While the view is shown, the node MUST answer `SELECT * FROM system_views.chronitondb_build`, sent by a client that passes Apache Cassandra's permission check, with exactly one row, whose columns are those of section 2.2 and whose `key` is `local`. Source: stakeholder need.

FREQ-BUILD-002 (ubiquitous): The `release_version` column MUST hold the value the release version reader of FREQ-BUILD-007 returns on the node. Source: stakeholder need.

FREQ-BUILD-003 (ubiquitous): The `apache_version` column MUST hold the value `FBUtilities.getReleaseVersionString()` returns on the node. Source: stakeholder need.

FREQ-BUILD-004 (ubiquitous): The `git_sha` column MUST hold the value `FBUtilities.getGitSHA()` returns on the node. Source: stakeholder need.

FREQ-BUILD-005 (ubiquitous): The node MUST build the row from its own build values only, with no message to another node. Source: stakeholder need.

FREQ-BUILD-006 (ubiquitous): The build MUST write the key `ReleaseVersion` into `org/apache/cassandra/config/version.properties` as REQ-VER-025 and REQ-VER-033 of the VER design record define it. Source: decision record 0007.

FREQ-BUILD-007 (ubiquitous): The node MUST read its release version through one reader class, `org.chronitondb.version.ReleaseVersion`, which behaves as REQ-VER-006 and REQ-VER-007 of the VER design record define. Source: decision record 0007.

FREQ-BUILD-008 (unwanted behaviour): If the node's authorizer requires authorization and a role that is not a superuser holds `SELECT` on neither the view nor the keyspace `system_views`, then the node MUST refuse that role's `SELECT` on the shown view with the unauthorized error Apache Cassandra returns for the other tables of `system_views`. Source: stakeholder need.

FREQ-BUILD-009 (ubiquitous): The feature MUST NOT change a file under `src/java/org/apache/cassandra/auth/` or the file `src/java/org/apache/cassandra/service/ClientState.java`. Source: risk, problem 4 of section 4.

FREQ-BUILD-010 (ubiquitous): The yaml setting `build_view_enabled` MUST default to `false`. Source: stakeholder need.

FREQ-BUILD-011 (event driven): When the node starts, the node MUST apply the rule once, after Apache Cassandra registered its virtual keyspaces and before the node loads its stored prepared statements, which it does before it accepts a client connection (C5). Source: decision record 0011.

FREQ-BUILD-012 (ubiquitous): The node MUST keep the state the rule gave at start, shown or hidden, until the node stops. Source: decision record 0011.

FREQ-BUILD-013 (event driven): When the node applies the rule and all three conditions of the rule hold, the node MUST show the view. Source: stakeholder need.

FREQ-BUILD-014 (event driven): When the node applies the rule and any one of the three conditions of the rule does not hold, the node MUST hide the view. Source: stakeholder need and decision record 0008.

FREQ-BUILD-015 (state driven): While the view is hidden, the node MUST give a CQL statement that names `system_views.chronitondb_build` the answer Apache Cassandra gives the same statement for a table name that `system_views` does not hold, with the view's name where Apache Cassandra puts the table name. Source: decision record 0009.

FREQ-BUILD-016 (state driven): While the view is hidden, the node MUST NOT list the view in `system_virtual_schema.tables`, in `system_virtual_schema.columns` or in the output of a `DESCRIBE` statement. Source: stakeholder need.

FREQ-BUILD-017 (state driven): While the view is hidden, the feature MUST leave the virtual keyspace registry as Apache Cassandra registered it. Source: stakeholder need.

FREQ-BUILD-018 (unwanted behaviour): If the configuration the node loaded sets `build_view_enabled` to `true` on a node whose final gate is not passed, then the node MUST log one WARN line at start that names the setting. Source: decision record 0013.

FREQ-BUILD-019 (ubiquitous): The feature MUST NOT add a yaml setting, a system property, a nodetool command, an MBean attribute or a method that changes the answer of the Apache compatibility check. Source: decision record 0008.

FREQ-BUILD-020 (ubiquitous): The view MUST be built on `AbstractVirtualTable`, so that a key filter and a column list are answered as on Apache Cassandra's own virtual tables. Source: risk, problem 3 of section 4.

FREQ-BUILD-021 (event driven): When the node shows the view, the node MUST register every other table of `system_views` as the table object Apache Cassandra built, so that the definition and the rows of each stay as Apache Cassandra gives them. Source: risk, problem 2 of section 4.

FREQ-BUILD-022 (ubiquitous): The view MUST refuse every statement that writes to it or truncates it, with the error Apache Cassandra returns for its read-only virtual tables (C13). Source: risk, problem 4 of section 4.

FREQ-BUILD-023 (ubiquitous): The feature MUST ship a reference page that names the view and its columns, the setting and the restart a change of it needs, the `GRANT` statement on the view as the way to let a role read it, a warning that a grant on the keyspace `system_views` also opens its other tables, a warning that every client reads the shown view on a node whose authorizer requires no authorization, and the need to read each node over a connection to that node. Source: decision record 0012 and risk, problems 4, 6 and 8 of section 4.

FREQ-BUILD-024 (ubiquitous): The reference page and `NEWS-chronitondb.txt` MUST state the upgrade order of section 7.3 and the rollback step of section 7.4. Source: risk, problem 5 of section 4.

FREQ-BUILD-025 (ubiquitous): The feature MUST NOT add a nodetool command, or an MBean other than the one Apache Cassandra creates for the read counter of FREQ-BUILD-029. Source: decision records 0011 and 0014.

FREQ-BUILD-026 (unwanted behaviour): If the node starts with the view hidden and its store holds a prepared statement that reads the view, then the node MUST start as Apache Cassandra starts with a stored statement on a table that no longer exists, with one warning and the statement removed (C12). Source: risk, problem 7 of section 4.

FREQ-BUILD-027 (unwanted behaviour): If an exception is thrown in the start step, then the start step MUST still return normally. Source: risk, problem 1 of section 4.

FREQ-BUILD-028 (unwanted behaviour): If an exception is thrown in the start step, then the node MUST log one ERROR line that names the view. Source: risk, problem 1 of section 4.

FREQ-BUILD-029 (state driven): While the view is shown, the node MUST hold the counter `org.chronitondb.metrics:type=BuildView,name=Reads` in Apache Cassandra's metrics registry (C16). Source: decision record 0014.

FREQ-BUILD-030 (event driven): When Apache Cassandra's read path asks the shown view for its data, the view MUST raise the counter of FREQ-BUILD-029 by one. Source: decision record 0014.

FREQ-BUILD-031 (state driven): While the view is hidden, the node MUST NOT hold a metric or an MBean of the feature. Source: decision record 0014.

FREQ-BUILD-032 (event driven): When the node shows the view, the node MUST log one INFO line that names the view. Source: risk, problem 6 of section 4.

FREQ-BUILD-033 (state driven): While the configuration the node loaded sets `build_view_enabled` to `false`, the start step MUST NOT write a log line. Source: stakeholder need.

FREQ-BUILD-034 (ubiquitous): The reference page MUST contain the exact text `org.chronitondb.metrics:type=BuildView,name=Reads` and say that the counter exists only on a node that shows the view. Source: decision record 0014.

FREQ-BUILD-035 (ubiquitous): The reference page MUST state when to revoke a grant on the view and the four things a grant left behind does, as section 2.2, Access, lists them. Source: decision record 0015.

## 4. Where problems could occur

Worst case first.

1. **A node does not start.** An operator sees a node that exits during its start: every node, if the hook line or the start step throws with the switch off, or the nodes with the switch on, if building or registering the keyspace throws. It comes from the one line in `CassandraDaemon.setupVirtualKeyspaces` and from the start step (C2).
2. **Other tables of `system_views` fail or lose their content on a node that shows the view.** An operator or a monitoring tool sees a table such as `system_views.settings` or `system_views.system_logs` missing, empty or failing, on a node started with the switch on. It comes from registering `system_views` again at start (C3). A keyspace built from new table objects, or one that leaves a table out, would cause it.
3. **The view shows a wrong value.** An operator reads a release version that differs from the installed one or from what `nodetool version` prints, reads `Unknown`, or reads the Apache Cassandra version under the wrong column. The operator then trusts a wrong build during an upgrade. It comes from the build key, the reader or the view's row.
4. **Build details reach a client that should not see them.** A role with no grant reads the row, a client reads it while the switch is off or while the node is in Apache compatibility mode, or a client changes it. It comes from the rule, the start step or a design that adds its own permission check. Decision record 0010 rates this problem at Normal risk with the rest of the feature. Two things are by design. While the view is shown, every logged in user can see the view's name in `system_virtual_schema.tables`, which Apache Cassandra lets every user read (C7). The name tells them the node runs ChronitonDB. It does not tell them which build. And on a node whose authorizer requires no authorization, every client reads the shown view (decision record 0012).
5. **A node started on an Apache Cassandra binary, or on an older ChronitonDB build, with the setting in its yaml does not start.** The operator sees `Invalid yaml. Please remove properties [build_view_enabled] from your cassandra.yaml` (C11). It happens after a rollback, and during an upgrade when the setting is written before the node has its new binary. The refusal is Apache Cassandra's own, for any key it does not know, and comes from no fault in the feature's code.
6. **The switch does not do what the operator asked.** The view is hidden on a node started with the switch on, the check answering off and the final gate passed, or is shown on a node started with the switch off. An operator edits `cassandra.yaml`, does not restart the node, and expects the view to change. On a node that shows the view, the read counter is missing or does not rise with the reads, or the log does not say that the view is shown.
7. **A node that hides the view differs from Apache Cassandra.** A listing shows the view while it is hidden, or a statement that names the view gets an answer Apache Cassandra would not give. A node that stored a prepared statement on the view starts, with the view hidden, in another way than Apache Cassandra starts with a stored statement on a table that no longer exists, where it logs one warning and removes the statement (C12). A node that hides the view holds a metric or an MBean of the feature, or a node with the switch off writes a log line of the feature at start.
8. **A grant or a read goes to a node that has no view.** `GRANT SELECT ON system_views.chronitondb_build` fails with `Resource <table system_views.chronitondb_build> doesn't exist` on a node where the view is hidden or absent (C8). A driver sends the `SELECT` to another node than the operator meant, and the answer is that node's build or a missing table error. A grant on the view stays behind after the view is switched off, cannot be revoked on a node without the view (C8), and gives its role the read again when a node shows the view. Decision record 0015 accepts that, with the rule on the reference page. A grant on the keyspace `system_views` lets the role read every other table of it too.
9. **The view can be switched on before the feature is finished.** An operator of a release cut between two milestones turns on a view whose pages and tests are not complete. Or such a node refuses to start because of the setting, against decision record 0013.
10. **A reader of `version.properties` breaks on the new key.** A build script or a tool that reads the file stops working. The VER design record names those readers in the last row of its departures table, and its problem 4 covers a wrong or missing value.

### 4.1 Test plan

No scenario module and no parity suite exist on this line. Each requirement is proven by a unit test or an in-JVM distributed test, and each item's design record names them.

1. Problem 1: a unit test runs the start step on a node with the default configuration and expects it to return normally and the registry unchanged. A test makes the registration of the keyspace fail inside the start step and expects the start step to return normally, one ERROR line that names the view, the view hidden and no metric of the feature in the metrics registry (FREQ-BUILD-027, FREQ-BUILD-028, FREQ-BUILD-031). Every in-JVM distributed test of this plan starts its nodes through the hook line (C2), so a hook line that throws fails them all.
2. Problem 2: an in-JVM distributed test starts one node that shows the view and one that hides it. Inside the first node it checks that every other table of `system_views` in the registry is the table object of `SystemViewsKeyspace.instance`. On the first it reads every other table of `system_views` and expects no error and the definitions the second node has. A second test reads the rows of `system_views.settings` on a node that hides the view, restarts the node with the view shown, reads them again and expects the same rows but for the row of `build_view_enabled`, which holds the configured value at each start (FREQ-BUILD-021).
3. Problem 3: unit tests of the reader and the build key, as the VER design record plans them for REQ-VER-006, REQ-VER-007, REQ-VER-025 and REQ-VER-033 (FREQ-BUILD-006, FREQ-BUILD-007). A unit test compares each column with its source (FREQ-BUILD-002 to FREQ-BUILD-004). An in-JVM distributed test with two nodes reads the view on each. It compares `apache_version` and `git_sha` with that node's `StorageServiceMBean` values and with the two values `nodetool version --verbose` prints on that node (C9), and `release_version` with the value the reader returns inside that node (FREQ-BUILD-001, FREQ-BUILD-005). No test on this line can compare `release_version` with the output of `nodetool version`, because that command prints the Apache Cassandra version until the code of the VER design record is on the line. Until then the shared reader is the proof, and section 2.7 names where that comparison is added. It also reads with a filter on another key and with a column list (FREQ-BUILD-020).
4. Problem 4: an in-JVM distributed test with authentication and authorization on reads the view as a superuser, as a role granted `SELECT` on the view, as a role granted `SELECT` on the keyspace, as a role granted `SELECT` on all keyspaces only, and as a role with no grant. The last two are refused (FREQ-BUILD-008). It reads the read counter before and after the two refused reads and expects the same value (FREQ-BUILD-030). A test tries an `INSERT`, an `UPDATE`, a `DELETE` and a `TRUNCATE` and expects Apache Cassandra's refusal (FREQ-BUILD-022). The review of each pull request checks its file list against FREQ-BUILD-009. The tests of problem 7 cover the view being readable while off.
5. Problem 5: no test on this line can start an Apache Cassandra binary. Apache Cassandra's own configuration tests run unchanged to show the setting loads here. A documentation test checks that the reference page and `NEWS-chronitondb.txt` hold the upgrade order and the rollback step (FREQ-BUILD-024).
6. Problem 6: unit tests call the rule with every combination of its three conditions (FREQ-BUILD-013, FREQ-BUILD-014). An in-JVM distributed test starts a node with the switch on and reads the view once the node accepts connections, then restarts the node with the switch off and expects the missing table error. A test prepares a `SELECT` on the shown view, restarts the node with the view still shown, and expects the stored statement to be loaded again with no warning (FREQ-BUILD-011). A test sets the `Config` field in the memory of a started node, to `true` on a node that hides the view and to `false` on a node that shows it, and expects the state of the view unchanged (FREQ-BUILD-012). A test reads the start log of a node that shows the view and expects one INFO line that names the view (FREQ-BUILD-032). Inside that node it expects the read counter in the metrics registry at 0 (FREQ-BUILD-029). It then expects the counter at 1 after one `SELECT` on the view, at 2 after a `SELECT` with a filter on another key, and at 4 after a `SELECT` whose `IN` list names two key values (FREQ-BUILD-030). A test lists the MBeans of that node whose domain starts with `org.chronitondb` and expects the read counter and no other MBean of this feature, and the review of each pull request checks that it adds no nodetool command (FREQ-BUILD-025). A test reads the class of the check by reflection and expects one method, the one that answers, and no field. The review of each pull request checks that it adds no setting, property, command or attribute for the check (FREQ-BUILD-019). A documentation test checks the reference page for the restart and for the name of the read counter (FREQ-BUILD-023, FREQ-BUILD-034).
7. Problem 7: an in-JVM distributed test reads, with the view hidden, the rows of `system_virtual_schema.tables` and `system_virtual_schema.columns` for `system_views` and the output of `DESCRIBE KEYSPACE system_views`, and expects the tables of `SystemViewsKeyspace.instance` and no other (FREQ-BUILD-016). Inside that node it expects the keyspace the registry holds under `system_views` to be `SystemViewsKeyspace.instance` itself (FREQ-BUILD-017), and no metric of the feature in the metrics registry and no MBean of the feature in the node's MBean server (FREQ-BUILD-031). It sends a `SELECT`, a `DESCRIBE TABLE` and a `GRANT` that name the view, and the same three with a table name `system_views` does not hold, and expects answers equal but for the name (FREQ-BUILD-015). It runs once with the switch off, and once with the switch on, the final gate passed and the check answering on. In the run with the switch off it also expects no log line of the start step in the start log (FREQ-BUILD-033). Until the final milestone the gate is passed by the rewrite of section 2.2, as the check's answer is. A test prepares a `SELECT` on the shown view, restarts the node with the switch off, and expects the node to start with the one warning of C12, the execution to get the answer Apache Cassandra gives for a prepared statement it does not know, and a new prepare to get the missing table error (FREQ-BUILD-015, FREQ-BUILD-026). The unit tests and the in-JVM distributed tests of Apache Cassandra that the line's checks run are run unchanged with the switch off. A pre-existing test that fails stops the work, as [conventions.md](../../process/conventions.md#code-layout) item 5 says.
8. Problem 8: an in-JVM distributed test with one node that shows the view and one that hides it sends the `GRANT` on the view to each. It expects the failure of C8 on the node that hides it and success on the other. It then checks that the role's permissions can be listed on both nodes, that a `REVOKE` that names the view fails on the node that hides it as C8 says, and that it succeeds on the node that shows it. A second test grants a role `SELECT` on the view, restarts the node with the switch off and then with the switch on again, and expects the role's `SELECT` on the view to succeed again and a `REVOKE` on that node to succeed, as section 2.2, Access, says of a grant left behind. A documentation test checks the reference page for the `GRANT` statement on the view, the two warnings and the need to connect to each node (FREQ-BUILD-023), and for the revoke rule with the four things a grant left behind does (FREQ-BUILD-035).
9. Problem 9: until the final milestone, tests start a node with `build_view_enabled: true` and expect the node to start, the view hidden, the value `true` in the row of `build_view_enabled` in `system_views.settings`, and the WARN line (FREQ-BUILD-014, FREQ-BUILD-018). The item that passes the final gate replaces them with a test that the view is shown.
10. Problem 10: the tests the VER design record plans for its build key cover it, and they are built by this feature's first item with the key.

## 5. Quality requirements

Not applicable: the class requires this section from Challenging size, and this feature is Normal size. The design record of each item answers the checklist of [quality-requirements.md](../../process/quality-requirements.md). The feature has one metric, the read counter of FREQ-BUILD-029 to FREQ-BUILD-031 (decision record 0014), and three log lines, FREQ-BUILD-018, FREQ-BUILD-028 and FREQ-BUILD-032.

## 6. Threat model

| Entry point | Threat (STRIDE) | Mitigation | FREQ |
|---|---|---|---|
| A `SELECT` on the view over CQL | Information disclosure: a client learns the exact build of a node, which helps it pick a known flaw | The view is off by default and hidden in Apache compatibility mode. Apache Cassandra's permission rule for `system_views` decides who reads it. The feature adds no permission code | FREQ-BUILD-008, FREQ-BUILD-009, FREQ-BUILD-010, FREQ-BUILD-014 |
| A `SELECT` on the view over CQL, on a node whose authorizer requires no authorization | Information disclosure: every client reads the build once the view is shown | Accepted by decision record 0012. Such a node lets every client read and change every table already. The view is off by default, and the reference page warns about this case | FREQ-BUILD-010, FREQ-BUILD-023 |
| A `SELECT` on the view over CQL | Information disclosure: while the view is shown, every logged in user sees its name in the table listings and learns that the node runs ChronitonDB | Accepted while the switch is on. The name does not show the build. With the switch off, or in Apache compatibility mode, the listings are the ones of Apache Cassandra | FREQ-BUILD-014, FREQ-BUILD-016 |
| A `SELECT` on the view over CQL | Denial of service: a client reads the view in a loop | None needed. A read builds one row from three strings held in memory, with no disk access, no lock and no message to another node | FREQ-BUILD-005 |
| A write or a `TRUNCATE` on the view over CQL | Tampering: a client changes what the view shows | The view is read only | FREQ-BUILD-022 |
| A statement that names the hidden view | Information disclosure: the answer tells a client that the node runs ChronitonDB | The view is not registered, so the answer is the one Apache Cassandra gives for a table that does not exist, from Apache Cassandra's own code | FREQ-BUILD-015, FREQ-BUILD-017 |
| A `GRANT` on the keyspace `system_views` | Information disclosure: a role that should read only the view reads every table of `system_views` | The reference page gives the grant on the view and warns about the grant on the keyspace. The grant rule itself is Apache Cassandra's | FREQ-BUILD-023 |
| The read counter over JMX | Information disclosure: whoever reads the node's MBeans sees the name of the counter and learns that the node runs ChronitonDB and shows the view | The counter exists only on a node that shows the view, so not with the switch off and not in Apache compatibility mode. It holds a count of reads and no build value. The same JMX connection already reads the Apache Cassandra version and the git SHA through `StorageServiceMBean` (C9) | FREQ-BUILD-025, FREQ-BUILD-031 |
| The yaml setting `build_view_enabled` | Tampering: someone who can edit `cassandra.yaml` and restart the node shows the view | No new threat. Whoever edits that file already controls the node. Showing the view gives no read access, since the CQL permission rule still applies | FREQ-BUILD-008, FREQ-BUILD-010 |
| The yaml setting `build_view_enabled` | Repudiation: the switch changes and nothing shows that it did | The state of the view changes only at a start, and the start log line that prints the configuration shows the value (C11). Nothing can change it while the node runs | FREQ-BUILD-012, FREQ-BUILD-025 |
| The Ant property `chronitondb.version` at build time | Tampering or spoofing: a build made with a wrong value reports a wrong release version | The form of the value is checked on every build that runs the unit tests, as REQ-VER-033 of the VER design record defines | FREQ-BUILD-006 |
| The Apache compatibility check | Tampering: someone turns the check to make a node show or hide the view | The feature adds no setting, property, command, attribute or method that changes its answer. A test changes it by a rewrite inside its test node's class loader (C15) | FREQ-BUILD-019 |

## 7. Compatibility

### 7.1 On-disk format changes

This feature changes no format, schema or protocol. A virtual table has no file on disk and no row in the schema tables. The feature adds no native protocol message and no message between nodes. The jar's `version.properties` gains one key, which is build output and not a file a node writes.

### 7.2 Mixed-version cluster

1. A read of the view on a node that shows it returns that node's own row, whatever the other nodes run.
2. A read of the view on an Apache Cassandra node, on an older ChronitonDB build, or on a node where the view is hidden gets the missing table error.
3. A driver can send a statement to any node. An operator who wants one node's build reads the view over a connection to that node, as cqlsh makes.
4. Grants are stored for the whole cluster, and the view exists per node. A `GRANT` on the view succeeds only on a node that shows it (C8). Once made, it counts on every node that shows the view.
5. Nodes exchange nothing for this feature, so a node without it is not affected by a node with it.
6. The read counter exists only on a node that shows the view. A monitoring tool that reads it finds no such MBean on an Apache Cassandra node, on an older ChronitonDB build, or on a node where the view is hidden.

### 7.3 Upgrade path and prerequisites

An upgrade from Apache Cassandra 5.0, or from an older ChronitonDB build of the line, needs nothing for this feature. The setting defaults to `false`, so an upgraded node behaves as before until an operator sets the switch and restarts the node. An operator who wants the view during a rolling upgrade adds the setting to the `cassandra.yaml` of a node after the node stopped on its old binary and before it starts on the new one. A node that starts on its old binary with the setting in its `cassandra.yaml` does not start (C11). The setting is not part of the line's minimum setup.

### 7.4 Rollback path

Before a node runs an Apache Cassandra binary, or a ChronitonDB build older than this feature, one step is needed on that node: remove `build_view_enabled` from its `cassandra.yaml`. Apache Cassandra refuses to start with a setting it does not know (C11).

Grants on the view need no step on each node, since grants are stored for the whole cluster. The rule of section 2.2, Access, applies once for the cluster: revoke the grants made on the view over a connection to a node that shows it, before the last node that shows the view is rolled back or restarted with the view hidden. A grant left behind is accepted and does what section 2.2, Access, lists (decision record 0015). A grant on the keyspace `system_views` is Apache Cassandra's own and can stay or be revoked at any time, on any node.

Nothing has to be dropped or rebuilt on disk. A prepared statement on the view that the node stored is removed at the next start, with one warning in the log (C12). The read counter is gone with the process that held it.

### 7.5 Runbook entries

No runbook page exists on this line yet. The feature adds the reference page `docs/reference/build-details-view.md`, which holds the rollback step of section 7.4 and the rule for grants until the line's rollback runbook exists, and an entry in `NEWS-chronitondb.txt` with the same step.

## 8. Dependencies

No new dependency.

## 9. Risks

| Id | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| R1 | The code of the VER design record starts before its change control update, and both works add the build key and the reader | Low | Two pull requests conflict in `build.xml` and in the reader class | Decision record 0007 requires the update before that code starts. This feature's first item adds the key and the reader first |
| R2 | An import from Apache Cassandra changes how the registry takes a keyspace registered again, or how `system_views` builds its tables (C1, C3) | Low | On a node that shows the view, the view or another table of `system_views` is missing or fails | The tests of problem 2 fail on such an import, and the fix is then made before the import merges |
| R3 | The work that builds Apache compatibility mode shapes the mode in a way one check read at start cannot express, for example a mode that changes while the node runs | Low | The check of decision record 0008 and the rule of section 2.2 have to change, through change control | The check is one method in its own package, with one caller |
| R4 | No scenario module and no parity suite exist on the line | High | The switch off proof rests on in-JVM distributed tests written for this feature | The tests of problem 7 compare the listings of a node that hides the view with the table list Apache Cassandra builds |

## 10. Decisions

1. [0002. What nodetool version prints on a ChronitonDB node](../../decisions/0002-nodetool-version-output-on-a-chronitondb-node.md): the release version and the git SHA that `nodetool version` shows, which the view's values equal.
2. [0003. Where the tests prove the release version before a package exists](../../decisions/0003-release-version-tests-before-a-package-exists.md): the build key and the reader are proven on the built jar.
3. [0007. The build details view builds the release version key and its reader](../../decisions/0007-build-details-view-builds-the-release-version-reader.md): this feature adds both, and `nodetool version` reuses them.
4. [0008. The build details view obeys Apache compatibility mode through an internal check](../../decisions/0008-build-details-view-obeys-apache-compatibility-mode.md): one check, off until the mode is built, with no setting.
5. [0009. A hidden build details view answers as a table that does not exist](../../decisions/0009-hidden-build-details-view-answers-as-a-missing-table.md): no error names the switch.
6. [0010. The build details view stays at Normal risk](../../decisions/0010-build-details-view-stays-at-normal-risk.md): a fault that shows the build details is rated with the rest of the feature.
7. [0011. The build details view is switched by its yaml setting only](../../decisions/0011-build-details-view-switched-by-yaml-setting-only.md): no nodetool command and no MBean for the switch, and a change needs a restart.
8. [0012. The build details view follows the Apache Cassandra permission rule where authorization is off](../../decisions/0012-build-details-view-readable-where-authorization-is-off.md): every client of such a node reads the shown view.
9. [0013. A node starts with the build details view hidden when its configuration turns the view on before the final gate](../../decisions/0013-build-details-view-hidden-before-the-final-gate.md): one warning, and never a refusal to start.
10. [0014. A node that shows the build details view counts its reads](../../decisions/0014-build-details-view-counts-its-reads.md): one counter, with its MBean, only on a node that shows the view.
11. [0015. A grant on the build details view that outlives the view is documented](../../decisions/0015-grant-on-the-build-details-view-that-outlives-the-view.md): no permission code changes, and the reference page gives the rule.

## 11. Milestones outline

1. **Milestone 1, the values and the view under test.** The build key and the reader, the view, the setting, the start step with its rule, the read counter, and the Apache compatibility check. It makes testable: a granted role reads the three values, a hidden view answers as Apache Cassandra does, and the check hides the view. The view is shown by tests only, and the switch refuses to turn on for an operator.
2. **Milestone 2, operators can switch the view.** The reference page and the `NEWS-chronitondb.txt` entry, and the passing of the final gate. It makes testable: the feature end to end through `cassandra.yaml` and a restart, and the rollback step and the rule for grants on the page. This is the final milestone.

## 12. Prior art

These rules apply to every source:

1. Describe and cite behaviour, published designs, papers, public documentation and code under licences compatible with the Apache License 2.0.
2. Code or text under an incompatible licence, for example the Elastic License, SSPL, BUSL or a proprietary licence, MUST NOT be copied. The behaviour of such a system is taken only from its public documentation. Code under a compatible licence MAY be used only with credit. See [conventions.md](../../process/conventions.md#code-from-elsewhere).
3. Contributors working on the project's behalf MUST NOT search for or read patents for design work. Any patent concern goes to the maintainers.

**Apache Cassandra.** Three sources are kept apart.

- Our line: ChronitonDB chronitondb-sandbox at `17e0b84a36`.
- Apache base: Apache Cassandra cassandra-5.0 at `76550e9314`. Every file under `src/` and `test/` on our line is the file of the Apache base, and `build.xml` differs only in two Java version properties at lines 47 and 48. So each fact below holds in the Apache base at the same file and line as on our line.
- Apache now: Apache Cassandra cassandra-5.0 at `531e98928d`, cassandra-6.0 at `383ed3c5ad` and trunk at `30b73cadf3`.

Apache Cassandra shows a node's version over CQL in `system.local` only, as the Apache version (C9). No table of `system_views` on our line shows the build (C1). Apache now adds a table `system_views.local` on cassandra-6.0 and trunk, with a `release_version` column that holds the Apache Cassandra version from cluster metadata (C1). It shows no git SHA and no downstream release. The view takes its place in `system_views` from Apache Cassandra's own node views, and its `key` column with the value `local` from `system.local` and that new table.

| Id | What the code does | Our line | Apache now |
|---|---|---|---|
| C1 | The tables of `system_views` are a fixed list built when the class loads | `SystemViewsKeyspace.SystemViewsKeyspace`, `src/java/org/apache/cassandra/db/virtual/SystemViewsKeyspace.java:30`, ChronitonDB chronitondb-sandbox at `17e0b84a36` | The same file in Apache Cassandra cassandra-5.0 at `531e98928d`. A longer list in `SystemViewsKeyspace.java:33`, Apache Cassandra trunk at `30b73cadf3`, the same in cassandra-6.0 at `383ed3c5ad`, with `LocalTable`, whose `release_version` column is set in `LocalTable.data`, `src/java/org/apache/cassandra/db/virtual/LocalTable.java:127`, Apache Cassandra trunk at `30b73cadf3` |
| C2 | The node registers the two virtual keyspaces at start, and the in-JVM distributed test node calls the same method | `CassandraDaemon.setupVirtualKeyspaces`, `src/java/org/apache/cassandra/service/CassandraDaemon.java:534`, and `Instance`, `test/distributed/org/apache/cassandra/distributed/impl/Instance.java:650`, ChronitonDB chronitondb-sandbox at `17e0b84a36` | `CassandraDaemon.java:534`, Apache Cassandra cassandra-5.0 at `531e98928d`. `CassandraDaemon.java:641`, Apache Cassandra cassandra-6.0 at `383ed3c5ad` and trunk at `30b73cadf3`. `Instance` was not read on Apache now |
| C3 | Registering a keyspace replaces one of the same name. The table ids of the replaced one stay in the registry, because the removal passes the table where the map is keyed by table id | `VirtualKeyspaceRegistry.register`, `src/java/org/apache/cassandra/db/virtual/VirtualKeyspaceRegistry.java:41`, the removal at line 46, ChronitonDB chronitondb-sandbox at `17e0b84a36` | The same file in Apache Cassandra cassandra-5.0 at `531e98928d`. On cassandra-6.0 at `383ed3c5ad` and trunk at `30b73cadf3` the removal passes the table id, `VirtualKeyspaceRegistry.java:47`, and `VirtualKeyspaceRegistry.unregister` exists at line 51 |
| C4 | A statement finds its table by name in the keyspace's table list, and a missing one fails with `table <name> does not exist` | `Schema.validateTable`, `src/java/org/apache/cassandra/schema/Schema.java:429`, the error at line 440, ChronitonDB chronitondb-sandbox at `17e0b84a36` | `Schema.java:440`, Apache Cassandra cassandra-5.0 at `531e98928d`. `SchemaProvider.validateTable`, `src/java/org/apache/cassandra/schema/SchemaProvider.java:95`, the same text at line 106, Apache Cassandra cassandra-6.0 at `383ed3c5ad` and trunk at `30b73cadf3` |
| C5 | At start the node registers its virtual keyspaces, then loads its stored prepared statements, then sets up its client transports, which accept connections only after that | `CassandraDaemon.setup`, `src/java/org/apache/cassandra/service/CassandraDaemon.java:229`, the three calls at lines 291, 377 and 443, ChronitonDB chronitondb-sandbox at `17e0b84a36` | The same lines in Apache Cassandra cassandra-5.0 at `531e98928d`. `CassandraDaemon.setup`, `CassandraDaemon.java:244`, the three calls at lines 331, 394 and 447, Apache Cassandra cassandra-6.0 at `383ed3c5ad` and trunk at `30b73cadf3` |
| C6 | The listings read every table of every registered virtual keyspace | `VirtualSchemaKeyspace.VirtualTables.data`, `src/java/org/apache/cassandra/db/virtual/VirtualSchemaKeyspace.java:83`, and `DescribeStatement.executeLocally`, `src/java/org/apache/cassandra/cql3/statements/DescribeStatement.java:135`, ChronitonDB chronitondb-sandbox at `17e0b84a36` | `VirtualSchemaKeyspace.java:83`, Apache Cassandra cassandra-5.0 at `531e98928d`. `VirtualSchemaKeyspace.java:84`, Apache Cassandra cassandra-6.0 at `383ed3c5ad` and trunk at `30b73cadf3`. `DescribeStatement` was not read on Apache now |
| C7 | With no authorization required every client passes. Otherwise an ordinary role needs a grant on the table or its keyspace for a system keyspace, and a grant on all keyspaces does not count. The tables of `system_virtual_schema` are readable by every logged in user | `ClientState.ensurePermission`, `src/java/org/apache/cassandra/service/ClientState.java:475`, the return for no authorization at line 477, the system keyspace rule at line 495, and the static initialiser of `ClientState` at line 92, ChronitonDB chronitondb-sandbox at `17e0b84a36` | `ClientState.java:477`, line 495 and line 92, Apache Cassandra cassandra-5.0 at `531e98928d`. `ClientState.java:512`, line 530 and line 99, Apache Cassandra cassandra-6.0 at `383ed3c5ad` and trunk at `30b73cadf3` |
| C8 | `GRANT` and `REVOKE` fail with `Resource <resource> doesn't exist` when the table is not found by name. A keyspace level resource of a virtual system keyspace always exists | `PermissionsManagementStatement.validate`, `src/java/org/apache/cassandra/cql3/statements/PermissionsManagementStatement.java:57`, and `DataResource.exists`, `src/java/org/apache/cassandra/auth/DataResource.java:245`, ChronitonDB chronitondb-sandbox at `17e0b84a36` | The same lines in Apache Cassandra cassandra-5.0 at `531e98928d`. `PermissionsManagementStatement.java:60` and `DataResource.java:246`, Apache Cassandra cassandra-6.0 at `383ed3c5ad` and trunk at `30b73cadf3` |
| C9 | The node reads `CassandraVersion` and `GitSHA` once from `version.properties`, reports them over JMX and through `nodetool version`, and writes the first into `system.local` | `FBUtilities.getReleaseVersionString`, `src/java/org/apache/cassandra/utils/FBUtilities.java:460`, `FBUtilities.getGitSHA` at line 468, `StorageService.getReleaseVersion`, `src/java/org/apache/cassandra/service/StorageService.java:3985`, `StorageService.getGitSHA` at line 3991, `SystemKeyspace.persistLocalMetadata`, `src/java/org/apache/cassandra/db/SystemKeyspace.java:606`, and `Version.execute`, `src/java/org/apache/cassandra/tools/nodetool/Version.java:34`, which prints the first value and with `--verbose` the second, ChronitonDB chronitondb-sandbox at `17e0b84a36` | `FBUtilities.java:460` and line 468, Apache Cassandra cassandra-5.0 at `531e98928d`. `FBUtilities.java:465` and line 473, Apache Cassandra cassandra-6.0 at `383ed3c5ad`. `FBUtilities.java:466` and line 474, with a third value in `FBUtilities.getBuildDate` at line 482, Apache Cassandra trunk at `30b73cadf3`. `StorageService`, `SystemKeyspace` and `Version` were not read on Apache now |
| C10 | The build writes `CassandraVersion` and `GitSHA` into `version.properties`. The version is `base.version`, with `-SNAPSHOT` added unless the Ant property `release` is set | target `_createVersionPropFile`, `build.xml:492`, and the `version` property at `build.xml:104`, ChronitonDB chronitondb-sandbox at `17e0b84a36` | `build.xml:492`, Apache Cassandra cassandra-5.0 at `531e98928d`. `build.xml:721`, Apache Cassandra cassandra-6.0 at `383ed3c5ad` and trunk at `30b73cadf3`, where trunk writes a third entry, `BuildDate`, at line 727 |
| C11 | A yaml key with no field in `Config` stops the start with `Invalid yaml. Please remove properties`. The settings table lists every field of `Config`, and the node logs every field once when it loads its configuration | `YamlConfigurationLoader.PropertiesChecker.check`, `src/java/org/apache/cassandra/config/YamlConfigurationLoader.java:417`, the error at line 423, `SettingsTable.getProperties`, `src/java/org/apache/cassandra/db/virtual/SettingsTable.java:151`, and `Config.log`, `src/java/org/apache/cassandra/config/Config.java:1347`, ChronitonDB chronitondb-sandbox at `17e0b84a36` | `YamlConfigurationLoader.java:423` and `SettingsTable.java:154`, Apache Cassandra cassandra-5.0 at `531e98928d`. `YamlConfigurationLoader.java:560`, Apache Cassandra cassandra-6.0 at `383ed3c5ad` and trunk at `30b73cadf3`, with `SettingsTable.java:155` on cassandra-6.0 and line 156 on trunk. `Config.log` was not read on Apache now |
| C12 | At start the node prepares again each statement it stored. One that cannot be prepared again is logged in a warning with its text and removed from the store | `QueryProcessor.preloadPreparedStatements`, `src/java/org/apache/cassandra/cql3/QueryProcessor.java:171`, the warning at line 192 and the removal at line 193, ChronitonDB chronitondb-sandbox at `17e0b84a36` | Not read on Apache now |
| C13 | A virtual table built on `AbstractVirtualTable` refuses writes with `Modification is not supported by table` and truncation with `Truncation is not supported by table` | `AbstractVirtualTable.apply`, `src/java/org/apache/cassandra/db/virtual/AbstractVirtualTable.java:126`, and `AbstractVirtualTable.truncate` at line 132, ChronitonDB chronitondb-sandbox at `17e0b84a36` | Not read on Apache now |
| C14 | The `cassandra.yaml` that Apache Cassandra ships sets an authorizer that requires no authorization | the setting `authorizer`, `conf/cassandra.yaml:217`, ChronitonDB chronitondb-sandbox at `17e0b84a36` | Not read on Apache now |
| C15 | A test of the in-JVM distributed test framework can rewrite a class inside a test node's class loader before the node starts | `ByteBuddyExamplesTest.writeFailureTest`, `test/distributed/org/apache/cassandra/distributed/test/ByteBuddyExamplesTest.java:51`, the initializer at line 54, ChronitonDB chronitondb-sandbox at `17e0b84a36` | Not read on Apache now |

| C16 | The metrics registry registers a counter under its name and as an MBean under the MBean name its `MetricName` carries. A `MetricName` takes any group, type and MBean name. `remove` takes the metric and its MBean out again | `CassandraMetricsRegistry.counter`, `src/java/org/apache/cassandra/metrics/CassandraMetricsRegistry.java:55`, `CassandraMetricsRegistry.remove` at line 208 and the five argument constructor of `CassandraMetricsRegistry.MetricName` at line 818, ChronitonDB chronitondb-sandbox at `17e0b84a36` | The same file in Apache Cassandra cassandra-5.0 at `531e98928d`. On cassandra-6.0 at `383ed3c5ad` and trunk at `30b73cadf3` the registry refuses a metric whose type is not in its fixed set of metric groups: `CassandraMetricsRegistry.verifyUnknownMetric`, `CassandraMetricsRegistry.java:272`, called from `CassandraMetricsRegistry.register` at line 431, which `CassandraMetricsRegistry.counter` at line 305 calls |
| C17 | A read of a virtual table calls one of the two `select` methods of the table: once for each partition key the statement names, or once for a range. On `AbstractVirtualTable` both call `data()`, the first through `data(DecoratedKey)`. A statement's permission check runs before the statement is executed | `SinglePartitionReadCommand.VirtualTableSinglePartitionReadCommand.executeLocally`, `src/java/org/apache/cassandra/db/SinglePartitionReadCommand.java:1413`, the group of one command for each key in `SinglePartitionReadCommand.VirtualTableGroup` at line 1318, `PartitionRangeReadCommand.VirtualTablePartitionRangeReadCommand.executeLocally`, `src/java/org/apache/cassandra/db/PartitionRangeReadCommand.java:553`, `AbstractVirtualTable.select`, `src/java/org/apache/cassandra/db/virtual/AbstractVirtualTable.java:78` and line 91, `AbstractVirtualTable.data` at line 72, and `QueryProcessor.processStatement`, `src/java/org/apache/cassandra/cql3/QueryProcessor.java:266`, ChronitonDB chronitondb-sandbox at `17e0b84a36` | The same lines of the three files under `db` in Apache Cassandra cassandra-5.0 at `531e98928d`. On cassandra-6.0 at `383ed3c5ad` and trunk at `30b73cadf3` the two `select` methods also take a row filter and limits, `AbstractVirtualTable.java:80` and line 93, with `data` at line 74, and the calls are at `SinglePartitionReadCommand.java:1575` and `PartitionRangeReadCommand.java:655`. `QueryProcessor` was not read on Apache now |
| C18 | Dropping a role removes every grant made to it | `DropRoleStatement.execute`, `src/java/org/apache/cassandra/cql3/statements/DropRoleStatement.java:67`, the call of `revokeAllFrom` at line 75, ChronitonDB chronitondb-sandbox at `17e0b84a36` | The same file in Apache Cassandra cassandra-5.0 at `531e98928d`. `DropRoleStatement.java:74`, the call at line 82, Apache Cassandra cassandra-6.0 at `383ed3c5ad` and trunk at `30b73cadf3` |

What Apache now means for this feature: the next import of cassandra-5.0 changes none of the lines above that were read there. C12 to C15 were not read on Apache now. A port to a line based on Apache Cassandra 6.0 finds a metrics registry that refuses a metric type it does not list (C16), so the read counter needs its own answer there, which that port designs. A port to a line based on Apache Cassandra 6.0 finds a registry that removes the table ids of a replaced keyspace before it adds the ones of the new keyspace (C3). The start step registers the same table objects again, at a point where the node accepts no client connection (C5), so the design holds there too.

**ChronitonDB.** The VER design record defines the release version, the build key and the reader. This feature reuses all three and shows the same value over CQL.

**OpenSearch.** OpenSearch answers a request to its root address with the build of the node that answers: a version number, a build hash and a build date as separate values, in `MainResponse.toXContent`, `server/src/main/java/org/opensearch/action/main/MainResponse.java:113`, OpenSearch main at `8b20d26bdb`. Its node listing can show the version and the build hash of every node from one request, in `RestNodesAction`, `server/src/main/java/org/opensearch/rest/action/cat/RestNodesAction.java:176`, OpenSearch main at `8b20d26bdb`. It gets right that the version and the build hash are separate values, which the view follows with `release_version` and `git_sha`. The view does not list every node from one request, because that needs a new value exchanged between nodes, and non-goal 1 leaves it out.

## Glossary

| Term | Definition | Name in code, CQL and docs |
|---|---|---|
| The view | The virtual table this feature adds | `system_views.chronitondb_build`, in docs "build details view" |
| Release version | The ChronitonDB version of an installed build, as the VER design record defines it | the column `release_version`, the class `org.chronitondb.version.ReleaseVersion` |
| Apache version | The Apache Cassandra version in the build, the string Apache Cassandra reports | the column `apache_version`, `FBUtilities.getReleaseVersionString()` |
| Git SHA | The git commit the build was made from | the column `git_sha`, `FBUtilities.getGitSHA()` |
| The switch | The yaml setting that turns the view on or off. The node reads it at start | `build_view_enabled` |
| The rule | The three conditions of section 2.2 that decide at start whether the view is shown or hidden | in docs "the rule" |
| Shown, hidden | The two states of the view on a node, by the rule. A node keeps its state from start to stop | in docs "shown" and "hidden" |
| The start step | The code that applies the rule once at start and, when the rule says shown, creates the read counter and registers `system_views` with the view | a class in `org.chronitondb.version` |
| Read counter | The counter of the reads of the view. It exists only on a node that shows the view | `org.chronitondb.metrics:type=BuildView,name=Reads` |
| Final gate | The feature's final milestone gate. In the code, one constant the last item of the final milestone sets | in docs "final gate" |
| Apache compatibility check | The one method that says whether Apache compatibility mode is on | a class in `org.chronitondb.compat` |
| Apache compatibility mode | The mode of [release.md](../../process/release.md#the-version-a-running-node-reports) in which a node reports as plain Apache Cassandra. It is not built yet | `apache_compatibility_mode` in release.md |
| Build key | The key `ReleaseVersion` that the build writes into `version.properties` | `ReleaseVersion` |
| Missing table error | The error Apache Cassandra raises for a table name a keyspace does not hold (C4) | raised by `Schema.validateTable` |
