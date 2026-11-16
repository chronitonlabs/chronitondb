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
| References | Issue #141. Line `chronitondb-sandbox`. Apache base commit `76550e931481e965ae3283d8cf4a59c320d74c55` (Apache Cassandra `cassandra-5.0`, build version 5.0.10). The [design record of `nodetool version`](../VER-release-version/design-record.md). Decision records 0002, 0003, 0007, 0008 and 0009. |
| Risk | Normal: the worst Bug Category is Availability, a response crash, where a read of the view or of another table of `system_views` fails. The floor of [classification.md](../../process/classification.md#the-floor) applies, because the feature adds a virtual table and touches configuration, command line tools and JMX MBeans. |
| Size | Normal: one view, its switch with a yaml setting and two nodetool commands, one internal check, and the build key with its reader. It needs no analysis beyond the virtual table code. |
| Reach | One area: virtual tables. Fork code in `org.chronitondb.version`, `org.chronitondb.compat` and `org.chronitondb.tools.nodetool`, with hooks in `org.apache.cassandra.config`, `org.apache.cassandra.service` and `org.apache.cassandra.tools`, and one entry in `build.xml`. |
| Touches | public interface (virtual tables), public interface (configuration), public interface (command line tools and arguments), public interface (jmx mbeans), stock behaviour, new input or privilege, shared state, new feature or switch |

Change history: the git history of this file.

Location: `docs/design/BUILD-build-details-view/feature-spec.md` on the line `chronitondb-sandbox`. The feature key is `BUILD`, a new key. The view has its own switch, and [release.md](../../process/release.md#the-version-a-running-node-reports) treats what sits behind its own switch as its own feature, so the view does not take the key `VER` of `nodetool version`. See [Feature keys and requirement ids](../../process/additive.md#feature-keys-and-requirement-ids). Process: [additive.md](../../process/additive.md).

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in BCP 14 (RFC 2119, RFC 8174) when, and only when, they appear in all capitals, as shown here.

The Risk, Size and Reach rows are the feature's class, as [classification.md](../../process/classification.md) defines it, and match the issue's `risk:`, `size:` and `reach:` labels.

[NEEDS CLARIFICATION: Is the risk Normal, as the issue's label says, or Critical, since section 6 names information disclosure and classification.md rates a Security bug of that kind Critical?]

Two short names are used throughout. "The VER design record" is the merged [design record of `nodetool version`](../VER-release-version/design-record.md), whose requirements are `REQ-VER-nnn`. A code fact is cited as C1 to C14, and section 12 holds each one with its symbol, file, line and the tree it was read in.

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
2. Its switch: the yaml setting `build_view_enabled` and the nodetool commands `enablebuildview` and `disablebuildview`. The view is off by default.
3. Access by Apache Cassandra's own permission rule for `system_views`: a superuser, or a role granted `SELECT`.
4. A node with the view off answers every statement that names the view, and every table listing, as Apache Cassandra does. Section 2.8 lists what is present on every node whatever the switch says.
5. One internal check that hides the view while Apache compatibility mode is on.
6. The build key and the reader class that give the release version, shared with `nodetool version`.
7. One log line for each switch change, and a reference page.

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

## 2. Architecture

The feature is small. A build step writes the release version into a file inside the jar. One class reads it. One virtual table shows it with two values Apache Cassandra already holds. One switch object decides whether the table is registered, and registers `system_views` again with or without it.

### 2.1 Context and scope

The feature runs inside one node and talks to nothing outside it.

1. **A CQL client**: an operator with cqlsh or a monitoring role with a driver. It reads the view on the node its connection reaches.
2. **An operator with nodetool**: turns the switch on or off on one node, over JMX.
3. **An operator who edits `cassandra.yaml`**: sets the value the switch has at start.
4. **The build**: Ant writes the release version into `org/apache/cassandra/config/version.properties` (C10).
5. **Apache Cassandra subsystems inside the node**: the virtual keyspace registry (C2, C3), the configuration (C11), the metrics registry, the MBean server and the log.
6. **Later work, outside this feature**: the work that builds Apache compatibility mode fills the internal check. The `nodetool version` work reuses the build key and the reader.

The feature sends no message to another node, writes no file on a node's disk and starts no thread.

### 2.2 Building blocks

| Block | Where it lives | What it does |
|---|---|---|
| Build key | `build.xml`, target `_createVersionPropFile` | Writes the key `ReleaseVersion` into `version.properties`, as REQ-VER-025 and REQ-VER-033 of the VER design record define it |
| Release version reader | `org.chronitondb.version.ReleaseVersion` | Reads the key once and returns the release version, as REQ-VER-006 and REQ-VER-007 of the VER design record define it |
| The view | `org.chronitondb.version` | A read-only virtual table built on `AbstractVirtualTable` (C13). It is one object, built once and used at every show, which builds one row from the reader and from `FBUtilities` (C9) |
| The view switch | `org.chronitondb.version` | Holds the rule that decides shown or hidden, applies it under one lock, and is the MBean `org.chronitondb:type=BuildView` |
| Apache compatibility check | `org.chronitondb.compat` | One method that says whether Apache compatibility mode is on. It answers off, and it tells the view switch when its answer changes |
| Toggle commands | `org.chronitondb.tools.nodetool` | `enablebuildview` and `disablebuildview`, which write the MBean attribute `Enabled` |
| The setting | the field `build_view_enabled` in `Config.java` | Holds the value from `cassandra.yaml` and the running value |

The view has these columns:

| Column | Type | Kind | Value |
|---|---|---|---|
| `key` | text | partition key | always `local` |
| `release_version` | text | regular | the value the release version reader returns, for example `5.0-chronitondb2` |
| `apache_version` | text | regular | the value of `FBUtilities.getReleaseVersionString()`, for example `5.0.10` |
| `git_sha` | text | regular | the value of `FBUtilities.getGitSHA()`, the git SHA of the build as Apache Cassandra reports it |

A `SELECT` with a key filter or a column list is answered as `AbstractVirtualTable` answers it for every Apache Cassandra virtual table: a filter on another key returns no row, and a column list returns those columns.

The `apache_version` and `git_sha` values are the ones Apache Cassandra reports today through `StorageServiceMBean.getReleaseVersion()` and `getGitSHA()` (C9). The `release_version` and `git_sha` values are the ones `nodetool version` prints once the VER design record is built, because the view and that command read them from the same reader and the same `FBUtilities` method. The values a build without a release version or without a git SHA gives are the ones REQ-VER-007 of the VER design record and `FBUtilities` define. The view adds none of its own.

**Shown and hidden.** The view is in one of two states on a node. It is shown when all three of these hold, and hidden when any one does not:

1. The running value of `build_view_enabled` is `true`.
2. The Apache compatibility check answers off.
3. The final gate is passed.

The final gate is the feature's final milestone gate of [additive.md](../../process/additive.md#milestone-gates). In the code it is one constant, which the last item of the final milestone sets. Until then the running value stays `false` on every node, whatever `cassandra.yaml` holds, the view stays hidden, and the switch refuses to turn on, as [branching-and-review.md](../../process/branching-and-review.md#feature-switches-and-defaults) item 2 requires.

**How the switch shows and hides the view.** Apache Cassandra builds the table list of `system_views` once, when the class loads (C1), and registers the keyspace at start (C2). The registry replaces a keyspace by name (C3). To show the view, the view switch registers a keyspace named `system_views` that holds the table objects of `SystemViewsKeyspace.instance` and the view. To hide it, the view switch registers `SystemViewsKeyspace.instance` again. The table objects of Apache Cassandra are reused, never built again, since some of them hold state. The view switch applies the rule at start, right after Apache Cassandra registered its virtual keyspaces, at each write of the switch, and each time the Apache compatibility check tells it that its answer changed. A write of the running value and the show or hide step that follows it run as one step under one lock, and so does every other show or hide step, so two of them never interleave. On this line a registration removes no table id (C3), so a read of another table of `system_views` that runs during a show or hide step still finds its table.

**What a hidden view looks like.** A statement finds a table by name through the keyspace's table list (C4), so a hidden view is not found and the statement gets the Apache Cassandra answer for a table that does not exist. The listings read the same table lists (C6), so they do not show it. A statement prepared while the view was shown holds the view's table id, and a read looks the table object up by that id with no check for a missing one (C5). So when the view switch hides the view it also drops every prepared statement that reads the view, as Apache Cassandra does for a dropped table (C14). A later execution then gets Apache Cassandra's answer for a prepared statement it does not know, the driver prepares it again, and the lookup by name fails as for any table that does not exist (FREQ-BUILD-019). A read that was already past that point can still reach the view object, since on this line the registry keeps the id of a replaced table (C3). The view object therefore evaluates the shown or hidden rule itself on every read. While the rule says hidden it refuses the read with the error that `Schema.validateTable` raises for its name (C4). It calls that method and copies no error text (FREQ-BUILD-030).

**Access.** The view adds no permission check. Apache Cassandra checks `SELECT` on a table of `system_views` against grants on that table and on the keyspace `system_views`, and a grant on all keyspaces does not count (C7). A superuser passes. On a node whose authorizer requires no authorization, every client passes, as for every table of `system_views` (C7). `GRANT` and `REVOKE` on a table need the table to exist on the node that runs the statement (C8), so a role is granted `SELECT` on the view while the view is shown there, or on the keyspace `system_views` at any time. The reference page gives the grant on the view as the way to let a role read it, because a grant on the keyspace also opens every other table of `system_views`.

[NEEDS CLARIFICATION: On a node whose authorizer requires no authorization, does every client read the view once the switch is on, as for Apache Cassandra's own node views, or does the view stay hidden there?]

**Tests that need a state shipped code cannot reach.** Two states are reached by tests only. Until the final gate, a test turns the view on through a mechanism inside the in-JVM distributed test framework, as [testing.md](../../process/testing.md#scenarios) item 9 requires, with no way around the refusal in shipped code. A test sets the answer of the Apache compatibility check through a test-only way, as decision record 0008 requires. Both ways live in test code only. Shipped classes hold no method, setting or property for either. The design record of the item that adds each one defines it.

What the two commands report while Apache compatibility mode is on is left to the work that builds the mode, since no node can be in the mode before that work (FREQ-BUILD-022).

### 2.3 Runtime view

1. **Start.** Apache Cassandra registers its virtual keyspaces (C2). The view switch then registers its MBean and applies the shown or hidden rule once.
2. **Switch change.** A nodetool command writes the MBean attribute `Enabled`. Under its lock the view switch writes the running value of `build_view_enabled`, logs the old and the new value, and applies the rule before the write returns.
3. **Read.** A `SELECT` on the view goes through Apache Cassandra's virtual table read path (C5) with no change to that path. The view builds one row from three strings held in memory. No other request path is touched.

### 2.4 Data and formats

Not applicable: the feature adds no file on a node's disk, no wire form, no schema row and no cluster metadata. Section 2.2 holds the view's columns.

### 2.5 Cross cutting concepts

Not applicable: the feature has one group of components, and its setting, log line and errors are requirements in section 3.

### 2.6 Deployment

An operator gets one new yaml setting, `build_view_enabled`, and two new nodetool commands, `enablebuildview` and `disablebuildview`. No new file is written on a node. The jar's `version.properties` holds one more key.

### 2.7 Package dependencies and hook points

| ChronitonDB package | MAY import |
|---|---|
| `org.chronitondb.version` | `org.chronitondb.compat`, and from Apache Cassandra `db.virtual`, `db.marshal`, `dht`, `schema`, `config`, `exceptions`, `metrics` and `utils`. The JDK, SLF4J and Guava |
| `org.chronitondb.compat` | The JDK only |
| `org.chronitondb.tools.nodetool` | `org.chronitondb.version` for the MBean interface only, and from Apache Cassandra `tools` and `tools.nodetool`. The JDK and the Airline annotations nodetool commands use |

No package of this feature imports `org.apache.cassandra.auth`, `org.apache.cassandra.transport`, `org.apache.cassandra.net` or `org.apache.cassandra.service.ClientState`.

Hook points, each a stock file this feature edits:

| Stock file | Edit | Why | Delta entry |
|---|---|---|---|
| `build.xml` | One property, `chronitondb.version`, and one entry in the target `_createVersionPropFile` | The release version is read from the build (decision record 0007) | `docs/delta/release-version-in-build-properties.md` |
| `src/java/org/apache/cassandra/config/Config.java` | One field, `build_view_enabled`, default `false` | Apache Cassandra's loader refuses a yaml key that has no field (C11). The field imports no fork code | `docs/delta/build-details-view.md` |
| `src/java/org/apache/cassandra/service/CassandraDaemon.java` | One import and one line in `setupVirtualKeyspaces`, after the two registrations | The view switch has to start after Apache Cassandra registered `system_views` (C2) | `docs/delta/build-details-view.md` |
| `src/java/org/apache/cassandra/tools/NodeTool.java` | Two imports and two entries in the command list of `NodeTool.execute` (C12) | A nodetool command is listed there to exist | `docs/delta/build-details-view.md` |

The VER design record plans the same `build.xml` edit and its own entries in `Config.java` and `NodeTool.java`. Decision record 0007 says that record is updated through change control before its code starts, so that it reuses the build key, the reader and the delta entry of the first row.

### 2.8 Feature class and switches

Feature class: behaviour-changing, because while the view is shown, operations Apache Cassandra already has return one more table.

| Switch | Class | Reason | Default per line | Apache Cassandra operations it changes |
|---|---|---|---|---|
| `build_view_enabled`, with `nodetool enablebuildview` and `nodetool disablebuildview` | behaviour-changing | while on, the table listings of the node hold the view | `chronitondb-sandbox`: off | `SELECT` on `system_virtual_schema.tables` and `system_virtual_schema.columns`, and `DESCRIBE` statements that list or describe the tables of `system_views` (C6) |

With the switch off the node answers every statement that names the view, and every table listing, as Apache Cassandra does. Four things are present on every node whatever the switch says, also while the Apache compatibility check answers on. Each is a departure from [branching-and-review.md](../../process/branching-and-review.md#feature-switches-and-defaults) item 7, of the same kind the VER design record lists in its section 3, and the maintainers approve each by merging this spec:

1. `system_views.settings` and the start log line that prints the configuration show one more setting, `build_view_enabled`, because Apache Cassandra lists every field of `Config` (C11).
2. `nodetool help` lists two more commands.
3. The JMX server holds one more MBean, `org.chronitondb:type=BuildView`. The toggle needs it to turn the view on at runtime.
4. The jar's `version.properties` holds one more key, `ReleaseVersion`. The VER design record already lists this one.

One more departure from the same item: a statement that names the hidden view gets no error that names the switch. Decision record 0009 settles it.

[NEEDS CLARIFICATION: Are the settings row, the two commands in `nodetool help` and the MBean accepted on every node with the switch off, also in Apache compatibility mode?]

## 3. Feature requirements

"The node" is the node that executes the statement or receives the command. "Shown", "hidden" and "the final gate" are defined in section 2.2.

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

FREQ-BUILD-011 (event driven): When `nodetool enablebuildview` runs against a node whose MBean `org.chronitondb:type=BuildView` is registered and whose final gate is passed, the node MUST set the running value of `build_view_enabled` to `true`. Source: stakeholder need.

FREQ-BUILD-012 (event driven): When `nodetool disablebuildview` runs against a node whose MBean `org.chronitondb:type=BuildView` is registered, the node MUST set the running value of `build_view_enabled` to `false`. Source: stakeholder need.

FREQ-BUILD-013 (event driven): When the node accepts a write of the running value of `build_view_enabled`, including a write that keeps the value, the node MUST log one INFO line with the old and the new value. Source: stakeholder need.

FREQ-BUILD-014 (state driven): While all three conditions of the shown or hidden rule in section 2.2 hold, the node MUST show the view. Source: stakeholder need.

FREQ-BUILD-015 (state driven): While any one of the three conditions of the shown or hidden rule in section 2.2 does not hold, the node MUST hide the view. Source: stakeholder need and decision record 0008.

FREQ-BUILD-016 (event driven): When Apache Cassandra has registered its virtual keyspaces at start, when a write of the running value of `build_view_enabled` returns, or when the answer of the Apache compatibility check has changed, the node MUST have shown or hidden the view as FREQ-BUILD-014 and FREQ-BUILD-015 say. Source: decision record 0008 and risk, problem 6 of section 4.

FREQ-BUILD-017 (state driven): While the view is hidden, the node MUST give a CQL statement that names `system_views.chronitondb_build` the answer Apache Cassandra gives the same statement for a table name that `system_views` does not hold, with the view's name where Apache Cassandra puts the table name. Source: decision record 0009.

FREQ-BUILD-018 (state driven): While the view is hidden, the node MUST NOT list the view in `system_virtual_schema.tables`, in `system_virtual_schema.columns` or in the output of a `DESCRIBE` statement. Source: stakeholder need.

FREQ-BUILD-019 (event driven): When the node hides the view, the node MUST drop every prepared statement that reads the view, so that a later execution of one gets the answer Apache Cassandra gives for a prepared statement it does not know. Source: decision record 0009.

FREQ-BUILD-020 (state driven): While the final gate is not passed, the node MUST keep the running value of `build_view_enabled` at `false`, whatever `cassandra.yaml` holds. Source: risk, problem 9 of section 4.

FREQ-BUILD-021 (unwanted behaviour): If `cassandra.yaml` sets `build_view_enabled` to `true` on a node whose final gate is not passed, then the node MUST log one WARN line at start that names the setting. Source: risk, problem 9 of section 4.

FREQ-BUILD-022 (ubiquitous): The shipped code MUST NOT hold a yaml setting, a system property, a nodetool command, an MBean attribute or a method that changes the answer of the Apache compatibility check. Source: decision record 0008.

FREQ-BUILD-023 (ubiquitous): The view MUST be built on `AbstractVirtualTable`, so that a key filter and a column list are answered as on Apache Cassandra's own virtual tables. Source: risk, problem 3 of section 4.

FREQ-BUILD-024 (ubiquitous): The node MUST run each write of the running value together with its show or hide step, and every other show or hide step, one at a time under one lock. Source: risk, problems 1 and 6 of section 4.

FREQ-BUILD-025 (event driven): When the node shows or hides the view, the node MUST keep the definition of every other table of `system_views` and every row those tables hold. Source: risk, problem 1 of section 4.

FREQ-BUILD-026 (unwanted behaviour): If `nodetool enablebuildview` or `nodetool disablebuildview` runs against a node that has no MBean `org.chronitondb:type=BuildView`, then nodetool MUST end on the usage error path that the VER design record defines, with the message `<command>: the node has no build details view switch. It runs Apache Cassandra or an older ChronitonDB build, or the switch failed to register at start.`, where `<command>` is the name of the command. Source: risk, problem 8 of section 4.

FREQ-BUILD-027 (ubiquitous): The view MUST refuse every statement that writes to it or truncates it, with the error Apache Cassandra returns for its read-only virtual tables (C13). Source: risk, problem 4 of section 4.

FREQ-BUILD-028 (ubiquitous): The feature MUST ship a reference page that names the view and its columns, the setting, the two commands, the MBean, the `GRANT` statement on the view as the way to let a role read it, a warning that a grant on the keyspace `system_views` also opens its other tables, and the need to read each node over a connection to that node. Source: risk, problems 4 and 8 of section 4.

FREQ-BUILD-029 (ubiquitous): The reference page and `NEWS-chronitondb.txt` MUST state the rollback steps of section 7.4. Source: risk, problem 5 of section 4.

FREQ-BUILD-030 (unwanted behaviour): If a read reaches the view while the shown or hidden rule says hidden, then the view MUST refuse it with the error that a call of `Schema.validateTable` raises for the view's name. Source: decision record 0009.

FREQ-BUILD-031 (unwanted behaviour): If a write of `true` to the running value of `build_view_enabled` reaches a node whose final gate is not passed, then the node MUST refuse it with an error whose message names the setting. Source: risk, problem 9 of section 4.

FREQ-BUILD-032 (unwanted behaviour): If the node refuses the write of `nodetool enablebuildview` as FREQ-BUILD-031 says, then nodetool MUST end on the stock error path that the VER design record defines, with the node's message. Source: risk, problem 9 of section 4.

## 4. Where problems could occur

Worst case first.

1. **Other tables of `system_views` fail or lose their content when the view is shown or hidden.** An operator or a monitoring tool sees a table such as `system_views.settings` or `system_views.system_logs` missing, empty or failing, on a node where the switch was turned on or off. It comes from registering `system_views` again (C3). A keyspace built from new table objects, or a lookup that runs between the two steps of the registration, would cause it.
2. **A read fails with a server error.** A client sees a server error, from a `NullPointerException`, where it should see the row or the missing table error. It happens when a read finds no table object for a table id, since the read path has no check for a missing one (C5). On this line the registry keeps the id of a replaced table (C3), and Apache Cassandra 6.0 removes it. An import that brings that change would turn the refusal of FREQ-BUILD-030 into this error, and would let a read of another table of `system_views` fail during a show or hide step.
3. **The view shows a wrong value.** An operator reads a release version that differs from the installed one or from what `nodetool version` prints, reads `Unknown`, or reads the Apache Cassandra version under the wrong column. The operator then trusts a wrong build during an upgrade. It comes from the build key, the reader or the view's row.
4. **Build details reach a client that should not see them.** A role with no grant reads the row, a client reads it while the view is off or while the node is in Apache compatibility mode, or a client changes it. It comes from the view switch or from a design that adds its own permission check. One thing is by design: while the view is shown, every logged in user can see the view's name in `system_virtual_schema.tables`, which Apache Cassandra lets every user read (C7). The name tells them the node runs ChronitonDB. It does not tell them which build.
5. **A node rolled back to an Apache Cassandra binary, or to an older ChronitonDB build, does not start.** The operator sees `Invalid yaml. Please remove properties [build_view_enabled] from your cassandra.yaml` (C11), on a node whose yaml names the setting.
6. **The switch does not do what the operator asked, or nobody can tell what it did.** The view stays hidden after `enablebuildview` returned, stays shown after `disablebuildview`, or changes with no line in the log that says so. Two toggles that run at the same time leave the view in a state that does not match the running value. A nodetool toggle changes the running value only, so a restart returns to the yaml value.
7. **A node with the view off differs from Apache Cassandra.** A listing shows the view while it is hidden, or a statement that names the view, prepared or not, gets an answer Apache Cassandra would not give.
8. **A grant or a read goes to a node that has no view.** `GRANT SELECT ON system_views.chronitondb_build` fails with `Resource <table system_views.chronitondb_build> doesn't exist` on a node where the view is hidden or absent (C8). A driver sends the `SELECT` to another node than the operator meant, and the answer is that node's build or a missing table error. A toggle command runs against an Apache Cassandra node in a cluster that is half upgraded. A grant on the view stays behind after the view is switched off, cannot be revoked on a node without the view (C8), and gives its role the read again when a node shows the view. A grant on the keyspace `system_views` lets the role read every other table of it too.
9. **The view can be switched on before the feature is finished.** An operator of a release cut between two milestones turns on a view whose commands, pages and tests are not complete.
10. **A reader of `version.properties` breaks on the new key.** A build script or a tool that reads the file stops working. The VER design record names those readers in the last row of its departures table, and its problem 4 covers a wrong or missing value.

### 4.1 Test plan

No scenario module and no parity suite exist on this line. Each requirement is proven by a unit test or an in-JVM distributed test, and each item's design record names them.

1. Problem 1: an in-JVM distributed test turns the switch on and off several times. After each change it checks that every other table of `system_views` has the definition it had before, and that every row those tables held before, the rows of the log table among them, is still there. New rows are allowed. A unit test reads tables of `system_views` from several threads while two other threads toggle, expects no error, and expects the state of the view to match the running value once the toggles end (FREQ-BUILD-024, FREQ-BUILD-025).
2. Problem 2: an in-JVM distributed test prepares a `SELECT` on the shown view and hides the view. It executes the statement and expects the answer Apache Cassandra gives for a prepared statement it does not know, then prepares it again and expects the missing table error. It compares both answers with the ones a statement on a dropped table gets (FREQ-BUILD-019). A unit test reads the view object directly while the rule says hidden and compares the error with the one `Schema.validateTable` raises for the same name (FREQ-BUILD-030). Both tests fail after an import that changes how the registry treats a replaced table, which is how that change is caught.
3. Problem 3: unit tests of the reader and the build key, as the VER design record plans them for REQ-VER-006, REQ-VER-007, REQ-VER-025 and REQ-VER-033 (FREQ-BUILD-006, FREQ-BUILD-007). A unit test compares each column with its source (FREQ-BUILD-002 to FREQ-BUILD-004). An in-JVM distributed test with two nodes reads the view on each and compares the values with that node's `StorageServiceMBean` values, which are the ones `nodetool version` prints (FREQ-BUILD-001, FREQ-BUILD-005). It also reads with a filter on another key and with a column list (FREQ-BUILD-023).
4. Problem 4: an in-JVM distributed test with authentication and authorization on reads the view as a superuser, as a role granted `SELECT` on the view, as a role granted `SELECT` on the keyspace, as a role granted `SELECT` on all keyspaces only, and as a role with no grant. The last two are refused (FREQ-BUILD-008). A test tries an `INSERT`, an `UPDATE`, a `DELETE` and a `TRUNCATE` and expects Apache Cassandra's refusal (FREQ-BUILD-027). The review of each pull request checks its file list against FREQ-BUILD-009. The tests of problem 7 cover the view being readable while off.
5. Problem 5: no test on this line can start an Apache Cassandra binary. Apache Cassandra's own configuration tests run unchanged to show the setting loads here. A documentation test checks that the reference page and `NEWS-chronitondb.txt` hold the rollback steps (FREQ-BUILD-029).
6. Problem 6: unit tests of the view switch cover each row of the shown or hidden rule (FREQ-BUILD-014, FREQ-BUILD-015), the state right after start, right after a write returns and right after the check's answer changes (FREQ-BUILD-016), and the log line with both values (FREQ-BUILD-013). A test reads the shipped classes and finds no setting, property, command, attribute or method that changes the check's answer (FREQ-BUILD-022). An end to end test of the final milestone runs both commands over JMX and reads the view after each (FREQ-BUILD-011, FREQ-BUILD-012).
7. Problem 7: an in-JVM distributed test compares, with the view hidden, the rows of `system_virtual_schema.tables` and `system_virtual_schema.columns` and the output of `DESCRIBE KEYSPACE system_views` with the same reads on a node that never showed the view (FREQ-BUILD-018). It sends a `SELECT`, a `DESCRIBE TABLE` and a `GRANT` that name the view, and the same three with a table name `system_views` does not hold, and expects answers equal but for the name (FREQ-BUILD-017). It runs once with the view hidden by the switch and once with the switch on and the check answering on, set through the test-only way while the view is shown, and in that second run it also executes a statement prepared before. The unit tests and the in-JVM distributed tests of Apache Cassandra that the line's checks run are run unchanged with the switch off. A pre-existing test that fails stops the work, as [conventions.md](../../process/conventions.md#code-layout) item 5 says.
8. Problem 8: a test runs each toggle command against a node whose MBean is not registered and expects the path and the message of FREQ-BUILD-026. An in-JVM distributed test grants `SELECT` on the shown view, hides the view, and checks that the role's permissions can still be listed, that a `REVOKE` that names the view fails as C8 says, and that the `REVOKE` succeeds once the view is shown again. A documentation test checks the reference page for the `GRANT` statement on the view, the warning about the keyspace grant and the need to connect to each node (FREQ-BUILD-028). The failing `GRANT` is the one of problem 7.
9. Problem 9: until the final milestone, tests start a node with `build_view_enabled: true` and expect the running value `false` and the WARN line (FREQ-BUILD-020, FREQ-BUILD-021), write `true` and expect the refusal with the setting's name (FREQ-BUILD-031), and run `nodetool enablebuildview` and expect the stock error path with that message (FREQ-BUILD-032). The item that passes the final gate replaces them with tests that the write is accepted.
10. Problem 10: the tests the VER design record plans for its build key cover it, and they are built by this feature's first item with the key.

## 5. Quality requirements

Not applicable: the class requires this section from Challenging size, and this feature is Normal size. The design record of each item answers the checklist of [quality-requirements.md](../../process/quality-requirements.md), its counters and other observability lines among them.

## 6. Threat model

| Entry point | Threat (STRIDE) | Mitigation | FREQ |
|---|---|---|---|
| A `SELECT` on the view over CQL | Information disclosure: a client learns the exact build of a node, which helps it pick a known flaw | The view is off by default and hidden in Apache compatibility mode. Apache Cassandra's permission rule for `system_views` decides who reads it. The feature adds no permission code | FREQ-BUILD-008, FREQ-BUILD-009, FREQ-BUILD-010, FREQ-BUILD-015 |
| A `SELECT` on the view over CQL | Information disclosure: while the view is shown, every logged in user sees its name in the table listings and learns that the node runs ChronitonDB | Accepted while the switch is on. The name does not show the build. With the switch off, or in Apache compatibility mode, the listings are the ones of Apache Cassandra | FREQ-BUILD-015, FREQ-BUILD-018 |
| A `SELECT` on the view over CQL | Denial of service: a client reads the view in a loop | None needed. A read builds one row from three strings held in memory, with no disk access, no lock and no message to another node | FREQ-BUILD-005 |
| A write or a `TRUNCATE` on the view over CQL | Tampering: a client changes what the view shows | The view is read only | FREQ-BUILD-027 |
| A statement that names the hidden view | Information disclosure: the answer tells a client that the node runs ChronitonDB | The answer is the one Apache Cassandra gives for a table that does not exist, built by Apache Cassandra's own code | FREQ-BUILD-017, FREQ-BUILD-019, FREQ-BUILD-030 |
| A `GRANT` on the keyspace `system_views` | Information disclosure: a role that should read only the view reads every table of `system_views` | The reference page gives the grant on the view and warns about the grant on the keyspace. The grant rule itself is Apache Cassandra's | FREQ-BUILD-028 |
| The MBean attribute `Enabled` and the two nodetool commands | Elevation of privilege: a JMX user shows the view | Showing the view gives no read access, since the CQL permission rule still applies. JMX access control applies to this MBean as to every MBean, and section 10 of the VER design record describes its modes | FREQ-BUILD-008 |
| The MBean attribute `Enabled` and the two nodetool commands | Repudiation: the switch changes and nothing shows that it did | Each accepted write is logged with the old and the new value, as the confirmed requirements ask. The line does not name the JMX user. A refused write changes nothing and is answered with an error | FREQ-BUILD-013, FREQ-BUILD-031 |
| Two switch writes at the same time | Tampering by a race: the view stays shown while the running value is `false` | Every write and every show or hide step run one at a time under one lock, and the view evaluates the rule itself on every read | FREQ-BUILD-024, FREQ-BUILD-030 |
| The yaml setting `build_view_enabled` | Tampering: someone who can edit `cassandra.yaml` shows the view | No new threat. Whoever edits that file already controls the node | FREQ-BUILD-010 |
| The Ant property `chronitondb.version` at build time | Tampering or spoofing: a build made with a wrong value reports a wrong release version | The form of the value is checked on every build that runs the unit tests, as REQ-VER-033 of the VER design record defines | FREQ-BUILD-006 |
| The Apache compatibility check | Tampering: someone turns the check to make a node show or hide the view | Shipped code holds no setting, property, command, attribute or method that changes its answer. The test-only way lives in test code | FREQ-BUILD-022 |

## 7. Compatibility

### 7.1 On-disk format changes

This feature changes no format, schema or protocol. A virtual table has no file on disk and no row in the schema tables. The feature adds no native protocol message and no message between nodes. The jar's `version.properties` gains one key, which is build output and not a file a node writes.

### 7.2 Mixed-version cluster

1. A read of the view on a node that shows it returns that node's own row, whatever the other nodes run.
2. A read of the view on an Apache Cassandra node, on an older ChronitonDB build, or on a node where the view is hidden gets the missing table error.
3. A driver can send a statement to any node. An operator who wants one node's build reads the view over a connection to that node, as cqlsh makes.
4. A toggle command against a node without the feature ends with an error that says so (FREQ-BUILD-026).
5. Grants are stored for the whole cluster, and the view exists per node. A `GRANT` on the view succeeds only on a node that shows it (C8). Once made, it counts on every node that shows the view.
6. Nodes exchange nothing for this feature, so a node without it is not affected by a node with it.

### 7.3 Upgrade path and prerequisites

An upgrade from Apache Cassandra 5.0, or from an older ChronitonDB build of the line, needs nothing for this feature. The setting defaults to `false`, so an upgraded node behaves as before until an operator turns the switch on. The setting is not part of the line's minimum setup.

### 7.4 Rollback path

Before a node runs an Apache Cassandra binary, or a ChronitonDB build older than this feature:

1. Revoke each grant made on the view itself, over a connection to a node that shows the view: `REVOKE SELECT ON system_views.chronitondb_build FROM <role>`. A `REVOKE` that names the view fails on a node that does not have it (C8). When no node shows the view any more, turn the switch on on one node, revoke there, and turn it off again. A grant left behind gives no access on a node without the view, and gives its role the read again on any node that shows the view later. A grant on the keyspace `system_views` is Apache Cassandra's own and can stay or be revoked at any time.
2. Remove `build_view_enabled` from `cassandra.yaml` on the node. Apache Cassandra refuses to start with a setting it does not know (C11).

Nothing has to be dropped or rebuilt on disk.

### 7.5 Runbook entries

No runbook page exists on this line yet. The feature adds the reference page `docs/reference/build-details-view.md`, which holds the rollback steps of section 7.4 until the line's rollback runbook exists, and an entry in `NEWS-chronitondb.txt` with the same steps.

## 8. Dependencies

No new dependency.

## 9. Risks

| Id | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| R1 | The code of the VER design record starts before its change control update, and both works add the build key and the reader | Low | Two pull requests conflict in `build.xml` and in the reader class | Decision record 0007 requires the update before that code starts. This feature's first item adds the key and the reader first |
| R2 | An import from Apache Cassandra changes how the registry treats a replaced keyspace, as Apache Cassandra 6.0 already does (C3) | Medium | A read that reaches the view while hidden, or a read of another table of `system_views` during a show or hide step, fails with a server error | The tests of problems 1 and 2 fail on such an import, and the fix is then made before the import merges |
| R3 | The work that builds Apache compatibility mode shapes the mode in a way one boolean check cannot express | Low | The check of decision record 0008 has to change | The check is one method in its own package, with one caller |
| R4 | No scenario module and no parity suite exist on the line | High | The switch off proof rests on in-JVM distributed tests written for this feature | The tests of problem 7 compare a node with the view hidden against a node that never showed it |

## 10. Decisions

1. [0002. What nodetool version prints on a ChronitonDB node](../../decisions/0002-nodetool-version-output-on-a-chronitondb-node.md): the release version and the git SHA that `nodetool version` shows, which the view's values equal.
2. [0003. Where the tests prove the release version before a package exists](../../decisions/0003-release-version-tests-before-a-package-exists.md): the build key and the reader are proven on the built jar.
3. [0007. The build details view builds the release version key and its reader](../../decisions/0007-build-details-view-builds-the-release-version-reader.md): this feature adds both, and `nodetool version` reuses them.
4. [0008. The build details view obeys Apache compatibility mode through an internal check](../../decisions/0008-build-details-view-obeys-apache-compatibility-mode.md): one check, off until the mode is built, with no setting.
5. [0009. A hidden build details view answers as a table that does not exist](../../decisions/0009-hidden-build-details-view-answers-as-a-missing-table.md): no error names the switch.

## 11. Milestones outline

1. **Milestone 1, the values and the view under test.** The build key and the reader, the view, the view switch with its setting, its MBean and its log line, and the Apache compatibility check. It makes testable: a granted role reads the three values, a hidden view answers as Apache Cassandra does, and the check hides the view. The view is turned on by tests only, and the switch refuses to turn on for an operator.
2. **Milestone 2, operators can switch the view.** The two nodetool commands, the reference page and the `NEWS-chronitondb.txt` entry, and the passing of the final gate. It makes testable: the feature end to end through `cassandra.yaml` and nodetool, and the rollback steps on the page. This is the final milestone.

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
| C5 | A read of a virtual table looks the table object up by table id and calls it with no check for a missing one | `SinglePartitionReadCommand.VirtualTableSinglePartitionReadCommand.executeLocally`, `src/java/org/apache/cassandra/db/SinglePartitionReadCommand.java:1415`, and `PartitionRangeReadCommand.VirtualTablePartitionRangeReadCommand.executeLocally`, `src/java/org/apache/cassandra/db/PartitionRangeReadCommand.java:555`, ChronitonDB chronitondb-sandbox at `17e0b84a36` | The same lines in Apache Cassandra cassandra-5.0 at `531e98928d`. `SinglePartitionReadCommand.java:1574` and `PartitionRangeReadCommand.java:654`, Apache Cassandra cassandra-6.0 at `383ed3c5ad` and trunk at `30b73cadf3` |
| C6 | The listings read every table of every registered virtual keyspace | `VirtualSchemaKeyspace.VirtualTables.data`, `src/java/org/apache/cassandra/db/virtual/VirtualSchemaKeyspace.java:83`, and `DescribeStatement.executeLocally`, `src/java/org/apache/cassandra/cql3/statements/DescribeStatement.java:135`, ChronitonDB chronitondb-sandbox at `17e0b84a36` | `VirtualSchemaKeyspace.java:83`, Apache Cassandra cassandra-5.0 at `531e98928d`. `VirtualSchemaKeyspace.java:84`, Apache Cassandra cassandra-6.0 at `383ed3c5ad` and trunk at `30b73cadf3`. `DescribeStatement` was not read on Apache now |
| C7 | With no authorization required every client passes. Otherwise an ordinary role needs a grant on the table or its keyspace for a system keyspace, and a grant on all keyspaces does not count. The tables of `system_virtual_schema` are readable by every logged in user | `ClientState.ensurePermission`, `src/java/org/apache/cassandra/service/ClientState.java:475`, the system keyspace rule at line 495, and the static initialiser of `ClientState` at line 92, ChronitonDB chronitondb-sandbox at `17e0b84a36` | `ClientState.java:495` and line 92, Apache Cassandra cassandra-5.0 at `531e98928d`. `ClientState.java:530` and line 99, Apache Cassandra cassandra-6.0 at `383ed3c5ad` and trunk at `30b73cadf3` |
| C8 | `GRANT` and `REVOKE` fail with `Resource <resource> doesn't exist` when the table is not found by name. A keyspace level resource of a virtual system keyspace always exists | `PermissionsManagementStatement.validate`, `src/java/org/apache/cassandra/cql3/statements/PermissionsManagementStatement.java:57`, and `DataResource.exists`, `src/java/org/apache/cassandra/auth/DataResource.java:245`, ChronitonDB chronitondb-sandbox at `17e0b84a36` | The same lines in Apache Cassandra cassandra-5.0 at `531e98928d`. `PermissionsManagementStatement.java:60` and `DataResource.java:246`, Apache Cassandra cassandra-6.0 at `383ed3c5ad` and trunk at `30b73cadf3` |
| C9 | The node reads `CassandraVersion` and `GitSHA` once from `version.properties`, reports them over JMX, and writes the first into `system.local` | `FBUtilities.getReleaseVersionString`, `src/java/org/apache/cassandra/utils/FBUtilities.java:460`, `FBUtilities.getGitSHA` at line 468, `StorageService.getReleaseVersion`, `src/java/org/apache/cassandra/service/StorageService.java:3985`, `StorageService.getGitSHA` at line 3991, and `SystemKeyspace.persistLocalMetadata`, `src/java/org/apache/cassandra/db/SystemKeyspace.java:606`, ChronitonDB chronitondb-sandbox at `17e0b84a36` | `FBUtilities.java:460` and line 468, Apache Cassandra cassandra-5.0 at `531e98928d`. `FBUtilities.java:465` and line 473, Apache Cassandra cassandra-6.0 at `383ed3c5ad`. `FBUtilities.java:466` and line 474, with a third value in `FBUtilities.getBuildDate` at line 482, Apache Cassandra trunk at `30b73cadf3`. `StorageService` and `SystemKeyspace` were not read on Apache now |
| C10 | The build writes `CassandraVersion` and `GitSHA` into `version.properties`. The version is `base.version`, with `-SNAPSHOT` added unless the Ant property `release` is set | target `_createVersionPropFile`, `build.xml:492`, and the `version` property at `build.xml:104`, ChronitonDB chronitondb-sandbox at `17e0b84a36` | `build.xml:492`, Apache Cassandra cassandra-5.0 at `531e98928d`. `build.xml:721`, Apache Cassandra cassandra-6.0 at `383ed3c5ad` and trunk at `30b73cadf3`, where trunk writes a third entry, `BuildDate`, at line 727 |
| C11 | A yaml key with no field in `Config` stops the start with `Invalid yaml. Please remove properties`. The settings table lists every field of `Config` | `YamlConfigurationLoader.PropertiesChecker.check`, `src/java/org/apache/cassandra/config/YamlConfigurationLoader.java:417`, the error at line 423, and `SettingsTable.getProperties`, `src/java/org/apache/cassandra/db/virtual/SettingsTable.java:151`, ChronitonDB chronitondb-sandbox at `17e0b84a36` | `YamlConfigurationLoader.java:423` and `SettingsTable.java:154`, Apache Cassandra cassandra-5.0 at `531e98928d`. `YamlConfigurationLoader.java:560`, Apache Cassandra cassandra-6.0 at `383ed3c5ad` and trunk at `30b73cadf3`, with `SettingsTable.java:155` on cassandra-6.0 and line 156 on trunk |
| C12 | nodetool builds its command list in one method | `NodeTool.execute`, `src/java/org/apache/cassandra/tools/NodeTool.java:96`, the list from line 98, ChronitonDB chronitondb-sandbox at `17e0b84a36` | Not read on Apache now |
| C13 | A virtual table built on `AbstractVirtualTable` refuses writes with `Modification is not supported by table` and truncation with `Truncation is not supported by table` | `AbstractVirtualTable.apply`, `src/java/org/apache/cassandra/db/virtual/AbstractVirtualTable.java:126`, and `AbstractVirtualTable.truncate` at line 132, ChronitonDB chronitondb-sandbox at `17e0b84a36` | Not read on Apache now |
| C14 | The node drops the prepared statements of a dropped table, a prepared statement can be dropped by its id, and the execution of an id the node does not know fails with the prepared query not found error | `QueryProcessor.StatementInvalidatingListener.onDropTable`, `src/java/org/apache/cassandra/cql3/QueryProcessor.java:1117`, `QueryProcessor.evictPrepared` at line 233, `QueryProcessor.getPreparedStatements` at line 239, and `ExecuteMessage.execute`, `src/java/org/apache/cassandra/transport/messages/ExecuteMessage.java:139`, ChronitonDB chronitondb-sandbox at `17e0b84a36` | Not read on Apache now |

What Apache now means for this feature: the next import of cassandra-5.0 changes none of the lines above. A port to a line based on Apache Cassandra 6.0 finds the registry removing a replaced table's id (C3), so the read of problem 2 would find no table object there, and it finds `VirtualKeyspaceRegistry.unregister` to build on.

**ChronitonDB.** The VER design record defines the release version, the build key and the reader. This feature reuses all three and shows the same value over CQL.

**OpenSearch.** OpenSearch answers a request to its root address with the build of the node that answers: a version number, a build hash and a build date as separate values, in `MainResponse.toXContent`, `server/src/main/java/org/opensearch/action/main/MainResponse.java:113`, OpenSearch main at `8b20d26bdb`. Its node listing can show the version and the build hash of every node from one request, in `RestNodesAction`, `server/src/main/java/org/opensearch/rest/action/cat/RestNodesAction.java:176`, OpenSearch main at `8b20d26bdb`. It gets right that the version and the build hash are separate values, which the view follows with `release_version` and `git_sha`. The view does not list every node from one request, because that needs a new value exchanged between nodes, and non-goal 1 leaves it out.

## Glossary

| Term | Definition | Name in code, CQL and docs |
|---|---|---|
| The view | The virtual table this feature adds | `system_views.chronitondb_build`, in docs "build details view" |
| Release version | The ChronitonDB version of an installed build, as the VER design record defines it | the column `release_version`, the class `org.chronitondb.version.ReleaseVersion` |
| Apache version | The Apache Cassandra version in the build, the string Apache Cassandra reports | the column `apache_version`, `FBUtilities.getReleaseVersionString()` |
| Git SHA | The git commit the build was made from | the column `git_sha`, `FBUtilities.getGitSHA()` |
| The switch | The setting that turns the view on or off, with its two nodetool commands | `build_view_enabled`, `enablebuildview`, `disablebuildview` |
| Running value | The value of the switch in the memory of a running node. It starts from `cassandra.yaml`, and a nodetool command changes it until the next restart | the MBean attribute `Enabled` of `org.chronitondb:type=BuildView` |
| Shown, hidden | The two states of the view on a node, by the rule of section 2.2 | in docs "shown" and "hidden" |
| Final gate | The feature's final milestone gate. In the code, one constant the last item of the final milestone sets | in docs "final gate" |
| Apache compatibility check | The one method that says whether Apache compatibility mode is on | a class in `org.chronitondb.compat` |
| Apache compatibility mode | The mode of [release.md](../../process/release.md#the-version-a-running-node-reports) in which a node reports as plain Apache Cassandra. It is not built yet | `apache_compatibility_mode` in release.md |
| Build key | The key `ReleaseVersion` that the build writes into `version.properties` | `ReleaseVersion` |
| Missing table error | The error Apache Cassandra raises for a table name a keyspace does not hold (C4) | raised by `Schema.validateTable` |
