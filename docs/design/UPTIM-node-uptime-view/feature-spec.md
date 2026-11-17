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
| References | Issue #144. Line `chronitondb-sandbox`. Apache base commit `76550e931481e965ae3283d8cf4a59c320d74c55` (Apache Cassandra `cassandra-5.0`). Decision records 0007 to 0013. |
| Risk | Normal: by the label the worst Bug Category is Availability, a response crash, which is a read of the view that fails. The floor of [classification.md](../../process/classification.md#the-floor) applies, because the feature adds a virtual table, a configuration setting, two nodetool commands and MBeans. The class table of that page rates two faults of this feature Critical, and by its rule the worst row decides: a wrong value in the view, and a node that does not start because of the view. Problems 1 and 4 of section 4 name them with their tests. The feature stays at Normal risk as an exception to the class table, which decision record 0010 records. |
| Size | Normal: the work needs several items, which are the view, its switch with the nodetool commands, the error that names the switch, and the documentation. |
| Reach | One area: virtual tables. Fork code in `org.chronitondb.uptime` and `org.chronitondb.uptime.tools`, with one hook each in `org.apache.cassandra.service`, `org.apache.cassandra.schema` and `org.apache.cassandra.tools`, and one field in `org.apache.cassandra.config`. |
| Touches | public interface (virtual tables), public interface (configuration), public interface (command line tools and arguments), public interface (jmx mbeans, including metrics), stock behaviour, new input or privilege, shared state, request path, new feature or switch |

Change history: the git history of this file.

Location: `docs/design/UPTIM-node-uptime-view/feature-spec.md` on the line `chronitondb-sandbox`. The feature key is `UPTIM`, a new key. See [Feature keys and requirement ids](../../process/additive.md#feature-keys-and-requirement-ids). Process: [additive.md](../../process/additive.md).

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in BCP 14 (RFC 2119, RFC 8174) when, and only when, they appear in all capitals, as shown here.

The Risk, Size and Reach rows are the feature's class, as [classification.md](../../process/classification.md) defines it, and match the issue's `risk:`, `size:` and `reach:` labels.

A code fact is cited as C1 to C17. Section 12 holds each one with its symbol, file, line and the tree it was read in.

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

This feature adds one read-only virtual table, `system_views.chronitondb_uptime`, called the view in this document. It holds one row about the node that executes the statement: the start time of the node's process and the uptime of that process in whole seconds. After a restart the row holds a later start time and an uptime that counts from the new start.

The users are operators who check nodes with cqlsh or with a tool that uses a driver.

In scope:

1. The view and its two values.
2. Its switch: the yaml setting `uptime_view_enabled`, off by default, and the two nodetool commands `enableuptimeview` and `disableuptimeview`, which change the running value on one node.
3. Access by the permission rule Apache Cassandra has for the tables of `system_views`.
4. The answer of a node whose view is off: the view is not listed, and a statement that reads or writes it is refused with an error that names the switch.
5. One INFO log line for each command that changes the node, and one counter of the reads of the view.
6. A reference page and an entry in `NEWS-chronitondb.txt`.

### Non-goals

1. Rows for other nodes from one connection. A node answers for itself only, so nodes exchange nothing new for this feature.
2. Reads without a grant. The view is read by the rule of the other tables of `system_views`.
3. A history or a count of past starts. The view shows the running process only.
4. A new metric for the uptime. The JVM already shows it over JMX, where `nodetool info` reads it (C11).
5. A change to `nodetool info` or to `system_views.gossip_info`. Both stay as they are.
6. A change to permission code. The view relies on the rule Apache Cassandra has.
7. A nodetool command that prints the state of the view. The row of the setting in `system_views.settings` shows the running value, and the table listings show whether the view is on.
8. A way to keep a nodetool change over a restart. A restart returns to the value in `cassandra.yaml`.
9. Other lines. The issue names the line `chronitondb-sandbox` only. Section 12 says what differs on Apache Cassandra 6.0.

## 2. Architecture

The feature is small. One virtual table builds one row from two values of the node's JVM. A switch decides whether the node lists the table in `system_views`. The switch changes at start from `cassandra.yaml` and on a running node through two nodetool commands, which call one MBean of the feature. While the view is off, a statement that reads or writes it gets an error that names the switch.

### 2.1 Context and scope

The feature runs inside one node and talks to nothing outside it.

1. **A CQL client**: an operator with cqlsh, or a tool with a driver. It reads the view on the node its connection reaches.
2. **An operator with nodetool**: runs `enableuptimeview` or `disableuptimeview` against one node. The command reaches the node over JMX, as every nodetool command does.
3. **An operator who edits `cassandra.yaml`**: sets `uptime_view_enabled` for the next start of the node.
4. **Apache Cassandra subsystems inside the node**: the registry of virtual keyspaces (C4), the configuration (C10), the lookup of a table by name (C6), the metrics registry, the JMX server and the log.
5. **The JVM of the node**: its `java.lang.management.RuntimeMXBean` gives the start time and the uptime, as it does for `nodetool info` (C11).

The feature sends no message to another node, writes no file and starts no thread.

### 2.2 Building blocks

| Block | Where it lives | What it does |
|---|---|---|
| The setting | the field `uptime_view_enabled` in `Config.java` | Holds the value from `cassandra.yaml` at start, and the running value after that. Its default is `false` |
| The view | `org.chronitondb.uptime` | A read-only virtual table built on `AbstractVirtualTable` (C15). It builds one row at each read |
| The switch | `org.chronitondb.uptime` | Holds the view state and the final gate. Turns the view on and off, at start and for the two commands |
| The switch MBean | `org.chronitondb.uptime`, registered as `org.chronitondb.uptime:type=UptimeView` through Apache Cassandra's `MBeanWrapper` (C17) | Two operations, `enable` and `disable`, that the two commands call |
| The two commands | `org.chronitondb.uptime.tools` | `nodetool enableuptimeview` and `nodetool disableuptimeview`. Each calls one operation of the switch MBean on the node nodetool is connected to |
| The off error | `org.chronitondb.uptime`, called from `Schema.validateTable` | Refuses a statement that reads or writes the view while it is off |
| The read counter | `org.chronitondb.uptime` | One Dropwizard `Counter` with the MBean name `org.chronitondb.metrics:type=UptimeView,name=Reads`, created and removed through Apache Cassandra's metrics registry (C17) |

**Terms.** These words have one meaning in this document.

1. The **view state** of a node is one value that the switch holds: **on**, **off** or **between on and off**. It alone decides whether the node answers a read of the view with the row. The view is on when the node lists it in `system_views` and answers a read of it with the row. The view is off when the node does not list it, holds no read counter and refuses a read of it.
2. The **running value** is the value of `uptime_view_enabled` in the memory of the running node. It starts as the value the node loaded from `cassandra.yaml`.
3. The **final gate** is the feature's final milestone gate of [additive.md](../../process/additive.md#milestone-gates). In the code it is one fixed value, not passed until the last item of the feature changes it to passed. Nothing in a shipped build changes it: no setting, no property and no command.
4. A **switch change** is a change of the view state of one node to on or to off, made by the start step or by a command.
5. A node is **between on and off** from the first step of a switch change until its last step. A switch change that a step ended part way leaves the node there, until a later switch change to off ends (decision record 0011). Such a node refuses every read of the view with the off error. It may list the view or not, and hold the read counter or not. It counts as neither on nor off in this document.
6. A **read** of the view is one request of Apache Cassandra's read path for the view's data. One statement makes one or more such requests, and a statement that pages can make one for each page.

Once the final gate is passed, the view is on exactly when the running value is `true`, on every node that has finished its start and is not between on and off. Until the final gate is passed, the view is off on every node, whatever the running value says.

**The columns.**

| Column | Type | Kind | Value |
|---|---|---|---|
| `key` | text | partition key | always `local`, as in `system.local` |
| `started_at` | timestamp | regular | the start time of the node's JVM |
| `uptime_seconds` | bigint | regular | the uptime of the node's JVM at the read, in whole seconds |

A `SELECT` with a key filter or a column list is answered as `AbstractVirtualTable` answers it for every virtual table of Apache Cassandra: a filter on another key returns no row, and a column list returns those columns (C15).

**The values.** The view takes both values from the JVM it runs in, at each read.

1. `started_at` is the value of `RuntimeMXBean.getStartTime()`.
2. `uptime_seconds` is the value of `RuntimeMXBean.getUptime()`, divided by 1000 and rounded down. `nodetool info` reads the same method of the same JVM and divides in the same way for its `Uptime (seconds)` line (C11). The two tools read at different moments, so their values differ by the time between the two reads. Two reads taken less than one second apart differ by at most 1.

The node stores neither value and takes neither from another node. A node that restarts is a new process, so its row holds the start time and the uptime of the new JVM. This is how an operator tells a node that restarted from one that did not. The view shows both values as the JVM reports them. The feature adds no rule of its own for a clock that is changed on a running node.

**What every node does at start.** Apache Cassandra registers its virtual keyspaces once at start, before it loads its stored prepared statements and before it accepts a client connection (C2, C3). Right after the registration of `system_views`, one added line calls the start step of the switch. The start step does these things in order:

1. It registers the switch MBean. Every node does this, whatever the setting says, so that the two commands can reach the node. The step builds the MBean object and hands it, with its name as text, to `MBeanWrapper.registerMBean` in the mode that logs a failure and goes on. That method builds the JMX name and registers the MBean, and it catches the exception of either and logs it (C17). What the node does when JMX refuses the MBean is said below, under "When JMX refuses an MBean of the feature".
2. It reads the setting. When the setting is `false`, the start step ends here.
3. When the setting is `true` and the final gate is not passed, it logs one WARN line that names the setting and ends. The node goes on with its start with the view off (decision record 0007). The running value stays `true`, so `system_views.settings` shows `true` on such a node while the view is off.
4. When the setting is `true` and the final gate is passed, it turns the view on.

The start step has no catch of its own. The one exception it does not let out is the one `MBeanWrapper` catches in step 1. What a node whose setting is `false` runs of the feature at start is the load of the classes of the start step, the constructors of the switch and of its MBean object, the call of `MBeanWrapper` in step 1 and the read of one boolean field. Those constructors and the static initialisers of those classes only assign fields, and getting the logger of their class is their one call into other code (FREQ-UPTIM-044). Any other throwable thrown in the start step ends the start of the node as a throwable from the registration of Apache Cassandra's own virtual keyspaces does: the node logs `Exception encountered during startup` with the throwable and exits (C3). On a node whose setting is `false` that can then only be an error of the JVM, such as a class that does not load or memory that runs out, which ends the start of an Apache Cassandra node in the same way wherever it is thrown. The node never goes on to serve without the view when its configuration asks for the view, because that would be an automatic fallback, and [quality-requirements.md](../../process/quality-requirements.md#automatic-fallbacks-are-opt-in-and-counted) allows one only with a setting, a toggle and a metric of its own. An operator who meets such a fault removes `uptime_view_enabled` from the `cassandra.yaml` of the node or sets it to `false`. The start step then ends at its second step, and the node starts without the view.

**When JMX refuses an MBean of the feature.** The feature registers two MBeans: the switch MBean at start, and the MBean of the read counter at each switch change to on. Both go through Apache Cassandra's `MBeanWrapper` in the mode that logs a failure and goes on, the counter's inside the metrics registry (C17). A node goes on when JMX refuses one of them, as it does for an MBean of Apache Cassandra itself (decision record 0012). Apache Cassandra logs one ERROR line for a registration that it attempts and JMX refuses. Without the switch MBean the node starts, with the view on or off as its setting and the final gate say, and the two commands print the refusal for a node that has no switch MBean, until the next start of the node. Without the MBean of the read counter the switch change succeeds and the view is on, the counter counts in the metrics registry and in the metrics reporters of the node, and the node shows no counter of the view over JMX until the view is turned off and on again. The metrics registry attempts no registration for a name that JMX already holds: it registers nothing and writes no line (C17). JMX then goes on showing the MBean that holds the name, which is no counter of the view. [NEEDS CLARIFICATION: whether the feature logs one ERROR line of its own when JMX already holds the name of the read counter, or logs nothing, as Apache Cassandra does for its own metrics. This draft logs nothing.] When the view is turned off, the registry unregisters whatever MBean holds the name of the counter, as it does for every metric it removes (C17). So a switch change to off also removes an MBean of that name that the feature did not register. Decision record 0012 says why this is no automatic fallback in the sense of [quality-requirements.md](../../process/quality-requirements.md#automatic-fallbacks-are-opt-in-and-counted): the view answers as its switch says, and what the node lacks is one way to manage or to watch it.

**Turning the view on and off.** Apache Cassandra keeps the tables of a virtual keyspace in a fixed list, and a keyspace registered under a name that is already registered replaces the earlier one (C4). The switch turns the view on by registering `system_views` again with the tables Apache Cassandra registered, as the same objects, and the view. It turns the view off by registering `system_views` again with the tables Apache Cassandra registered, as the same objects, and nothing else. The listings read the registered keyspace (C7), so they show the view exactly while it is on. The switch builds the view object once, the first time it turns the view on, and registers that same object at each later turn on.

A switch change to on is these steps in this order: set the view state to between on and off, create the read counter, register `system_views` with the view, set the view state to on. A switch change to off is these steps in this order: set the view state to between on and off, register `system_views` without the view, remove the read counter, set the view state to off. A switch change to on starts only from a node whose view is off. A switch change to off starts from a node whose view is on or that is between on and off, and from no other node. Its two middle steps can run where they are already done: registering replaces what is registered (C4), and removing a counter that is not there removes no counter (C17). In both cases the registry unregisters whatever MBean holds the name of the counter, as the paragraph on JMX above says.

The view state and the read counter of the switch change that set it are one value. The switch writes that value in one step, and every thread that reads the view sees it from then on. A read takes the value once, at its start. So a read that finds the view on has the counter of the switch change that turned the view on, and the view decides nothing by itself.

The node runs the start step and the two operations of the switch MBean one at a time, under one lock of the switch. A command that arrives while the start step or another command runs waits for it. So two commands never mix their steps, and a command that arrives while the start step runs is served after the start step has ended. A command that arrives before the start step has registered the switch MBean finds no switch MBean and is refused, as said below. What runs under the lock is a counter in the metrics registry, a put in the registry of virtual keyspaces, two fields in memory and one log line. None of it waits for another node or for a client.

A command that makes a switch change does these things in this order. It logs one INFO line that holds the name of the setting, the running value before the command and the running value the command asks for. [NEEDS CLARIFICATION: whether the INFO line is logged before the change with the value the command asks for, as in this draft, or once the change is done with the value the node then has, with one ERROR line for a command that a step ended part way.] It runs the steps of its switch change but the last. It sets the running value. It runs the last step, which sets the view state to on or to off. So the INFO line is in the log before anything on the node changes, also when a later step ends the command part way, and the node answers a read with the row only once every other step has ended. The command changes nothing but the memory of the node, as the toggles of Apache Cassandra do (C13). It writes no file, so a restart returns to the value in `cassandra.yaml`. One command changes the node and makes no switch change: `disableuptimeview` on a node whose view is off and whose running value is `true`. It logs the INFO line and sets the running value, and it registers nothing.

The two commands, and the two operations of the switch MBean they call, behave as follows.

| Call | State of the node | What the node does |
|---|---|---|
| `enableuptimeview` | final gate not passed, whatever the running value | Refuses with the text `The node uptime view cannot be turned on in this build.` The view stays off and the running value stays as it is |
| `enableuptimeview` | final gate passed, view off | Logs the INFO line and makes the switch change to on, with the running value set to `true` before its last step |
| `enableuptimeview` | final gate passed, view on | Nothing. No log line. The command succeeds |
| `enableuptimeview` | final gate passed, between on and off | Refuses with the text `The node uptime view is between on and off on this node. Run nodetool disableuptimeview first.` The node stays as it is, and no line is logged (decision record 0013) |
| `disableuptimeview` | view on, or between on and off | Logs the INFO line and makes the switch change to off, with the running value set to `false` before its last step |
| `disableuptimeview` | view off, running value `true`, which only a node whose final gate is not passed can have | Logs the INFO line and sets the running value to `false`. It makes no switch change, and the view stays off |
| `disableuptimeview` | view off, running value `false` | Nothing. No log line. The command succeeds |

The two commands report through the two forms nodetool has for every command (C12). A refusal is printed as nodetool prints the wrong use of a command: the line `nodetool: ` followed by the text of the refusal, the line that points to `nodetool help`, and exit status 1. A step that threw is printed as nodetool prints the failure of a command: the line `error: ` followed by the message, a stack trace, and exit status 2. nodetool by itself picks the form by the class of the throwable (C12). The commands of the feature pick it by what happened: a refusal of the switch gets the first form, and a throwable from a step gets the second form whatever its class, an `IllegalArgumentException` or an `IllegalStateException` included.

A command of the feature that runs against a node with no switch MBean is refused with the text `This node has no switch for the node uptime view.` A node has a switch MBean when the MBean that JMX holds under `org.chronitondb.uptime:type=UptimeView` is an instance of the interface of the switch MBean. The command asks JMX for that before it calls an operation. So it never calls an operation of another MBean that holds the name, and it never gets the answer nodetool by itself gives for a missing MBean, `Server is not initialized yet, cannot run nodetool.` (C12). A node with no switch MBean is one of four: a node that runs Apache Cassandra, a node of a ChronitonDB build without the feature, a node whose log holds the ERROR line of a refused registration, or a node of this build that has not yet reached the start step, which runs after the JMX server of the node has started (C3). The reference page names the four and tells the operator of a node that is still starting to run the command again.

A step that throws ends the command there, and nodetool prints the failure. The feature does not undo the steps that were done (decision record 0011). When the step comes after the first step of a switch change, the node is then between on and off: it refuses every read of the view, and it may list the view or hold the read counter. A statement on the view that is no read follows the table listing (decision record 0013): it gets the answer of a node whose view is on where the node lists the view, and the answer of a node whose view is off where it does not. So where the node still lists the view, a `GRANT` on the view works and a write is refused as a write to a read-only table (C15). `disableuptimeview` is the way back, and the only one, since `enableuptimeview` is refused on such a node: on such a node it makes the switch change to off in full, whatever the running value says, so it brings the node to the off state, with the view off, no counter and the running value `false`.

**What a view that is off looks like.** The view is not in the registered `system_views`, so no listing shows it. The table listings of a node are the rows of `system_virtual_schema.tables` and `system_virtual_schema.columns` and the output of the four `DESCRIBE` statements that list tables: `DESCRIBE TABLES`, `DESCRIBE KEYSPACE system_views`, `DESCRIBE SCHEMA` and `DESCRIBE FULL SCHEMA` (C7). "Every table listing" in this document means these six.

A `SELECT`, `INSERT`, `UPDATE`, `DELETE` or `TRUNCATE` finds its table by name through `Schema.validateTable`, also inside a `BATCH`, and a table that is not found fails there with `table <name> does not exist` (C6). One added line on that branch asks the feature first. When the keyspace name is exactly `system_views` and the table name is exactly `chronitondb_uptime`, compared letter for letter as `Schema.validateTable` received them, the feature throws an invalid request error, the kind of error Apache Cassandra throws there, with this message, called the off error in this document:

`The node uptime view system_views.chronitondb_uptime is off on this node. Its switch is uptime_view_enabled in cassandra.yaml and nodetool enableuptimeview.`

The text names the switch and promises nothing, so it is true before and after the final gate. A name that differs in case, which a client can send in double quotes, is another table to Apache Cassandra and gets the Apache Cassandra error.

For every other name the branch throws the Apache Cassandra error as before. Every other statement that names the view while it is off, such as `DESCRIBE TABLE`, `GRANT` or `REVOKE`, does not pass through that branch and gets the answer Apache Cassandra gives for a table name that `system_views` does not hold.

A statement that a client prepared while the view was on stays in the node's cache of prepared statements after the view is turned off. A read finds a virtual table by its id and not by its name (C5), so such a statement can still reach the view. The view therefore reads the view state at each read, and refuses a read with the off error unless the view is on. A read that runs at the moment of a switch change gets the row or the off error. A statement that pages can so get a page with the row and then the off error, when the view is turned off between two of its reads. The statement stays in the cache, so it answers with the row again once the view is turned on again.

A node also stores prepared statements on disk and prepares them again at start (C14). A stored statement that reads the view cannot be prepared again on a node that starts with the view off. Apache Cassandra then logs one warning with the statement's text and removes the statement from the store (C14). This is what Apache Cassandra does for a stored statement on any table that no longer exists.

**The read counter.** [quality-requirements.md](../../process/quality-requirements.md#observability) asks for a counter for every outcome. The feature has one counter, of the reads the view answered. It is one Dropwizard `Counter` with the MBean name `org.chronitondb.metrics:type=UptimeView,name=Reads`, in the form [conventions.md](../../process/conventions.md#names) items 3 and 4 ask for. It is created and removed through Apache Cassandra's metrics registry (C17). A switch change to on creates it and a switch change to off removes it. So a node whose view is on holds it, a node whose view is off does not, and a node between on and off may hold it. A switch change to on starts from a node whose view is off, which holds no counter, so each one creates a new counter that starts at 0. The registry removes the MBean of the counter in the mode that ignores a failure (C17). That MBean has no code of its own that runs when JMX removes it, so by the contract of the JDK's `MBeanServer.unregisterMBean` the removal fails only when the MBean is not registered. The view raises the counter it took with the view state at the start of the read, and never looks a counter up by name. So a read that runs at the moment the view is turned off cannot create the counter again: at most it raises a counter that was just removed, and that count is lost. The view raises the counter by one each time Apache Cassandra's read path asks the view for its data while the view is on. A read whose key filter then leaves no row for the client is counted too, since the view built the row for it. The counter counts those requests and not statements. How many requests one statement makes is decided by Apache Cassandra's read path, so the counter is no count of statements, and the reference page says so. A read that Apache Cassandra's permission check refuses does not reach the view and is not counted.

**Access.** The view adds no permission check. Apache Cassandra checks `SELECT` on a table of `system_views` against grants on that table and on the keyspace `system_views`, and a grant on all keyspaces does not count (C8). A superuser passes. On a node whose authorizer requires no authorization, every client passes, as for every table of `system_views` (C8). `GRANT` and `REVOKE` on a table need the table to exist on the node that runs the statement (C9). So a role is granted `SELECT` on the view on a node where the view is on, or on the keyspace `system_views` on any node. Grants are stored for the whole cluster, so a grant on the view stays when the view is turned off, and counts again when the view is turned on. The reference page says so.

**Tests that need a state a shipped build cannot reach.** Until the last item of the feature, the final gate is not passed, so no shipped code turns the view on. After it, no shipped code reaches the state before the gate. A test that needs the other state rewrites the method of the gate inside the class loader of its test node, before the node starts, as Apache Cassandra's own in-JVM distributed tests rewrite classes (C16). This is the mechanism inside the in-JVM distributed test framework that [testing.md](../../process/testing.md#scenarios) item 9 requires. An in-JVM distributed test node registers no MBean unless its test starts it with the JMX feature of the framework (C16), so each test that calls the switch MBean or looks for the read counter over JMX starts its nodes with that feature.

### 2.3 Runtime view

Not applicable: this section is required from Challenging size, and this feature is Normal size. Section 2.2 says what the feature runs at start, at a switch change, at a read and at the lookup of a table by name.

### 2.4 Data and formats

Not applicable: the feature adds no file on disk, no wire form, no schema row and no cluster metadata. Section 2.2 holds the columns of the view.

### 2.5 Cross cutting concepts

Not applicable: this section is required from Challenging size, and this feature is Normal size. Section 2.2 names the setting, the log lines, the counter and the errors.

### 2.6 Deployment

Not applicable: this section is required from Challenging size, and this feature is Normal size. Section 2.8 and section 7 say what changes for an operator.

### 2.7 Package dependencies and hook points

| ChronitonDB package | MAY import |
|---|---|
| `org.chronitondb.uptime` | From Apache Cassandra `db.virtual`, `db.marshal`, `dht`, `schema`, `config`, `metrics`, `exceptions` and `utils`, which holds `MBeanWrapper`. The JDK, SLF4J and Guava |
| `org.chronitondb.uptime.tools` | The interface of the switch MBean in `org.chronitondb.uptime`. From Apache Cassandra `tools`. The JDK and the Airline library that the nodetool commands of the line already use |

Neither package imports `org.apache.cassandra.auth`, `org.apache.cassandra.transport`, `org.apache.cassandra.net` or `org.apache.cassandra.service.ClientState`.

Hook points, each a file of Apache Cassandra that this feature edits. All four are recorded in one delta entry, `docs/delta/node-uptime-view.md`, which the item that makes the first edit adds.

| File | Edit | Why |
|---|---|---|
| `src/java/org/apache/cassandra/config/Config.java` | One field, `uptime_view_enabled`, default `false` | Apache Cassandra's loader refuses a yaml key that has no field (C10). The field imports no fork code |
| `src/java/org/apache/cassandra/service/CassandraDaemon.java` | One import, and one call of the start step in `setupVirtualKeyspaces`, right after the registration of `system_views` | The start step has to run after Apache Cassandra registered `system_views` and before the node loads stored statements or accepts clients (C2, C3) |
| `src/java/org/apache/cassandra/schema/Schema.java` | One import, and one call in `validateTable` on the branch for a table that is not found | The off error has to replace the error for a missing table, for the view's name only (C6) |
| `src/java/org/apache/cassandra/tools/NodeTool.java` | Two imports, and two entries in the list of commands | nodetool finds its commands in that list (C12) |

The feature edits no file under `conf/`. Apache Cassandra's `conf/cassandra.yaml` and `conf/cassandra_latest.yaml` stay untouched, as [release.md](../../process/release.md#the-configuration-file) says. That page gives ChronitonDB a configuration file of its own, `conf/cassandra_chronitondb.yaml`, which carries ChronitonDB's own settings. The file does not exist on this line yet, and this feature does not create it. Where the line holds the file when the pull request of the last item of the feature is opened, that item adds the setting to it, commented out with its default (FREQ-UPTIM-040). [NEEDS CLARIFICATION: whether this feature adds the setting to that file when the file exists at its last item, as in this draft, or leaves it to the item that creates the file, as the design records of the release version and of the commit log disk check on this line do. In both cases the setting goes in commented out with its default.] Until the file exists no shipped yaml file names the setting, and the reference page is where an operator finds it.

### 2.8 Feature class and switches

Feature class: behaviour-changing, because while the view is on, operations Apache Cassandra already has return one more table, and because the parts named below are present on every node.

| Switch | Class | Reason | Default per line | Apache Cassandra operations it changes |
|---|---|---|---|---|
| `uptime_view_enabled` in `cassandra.yaml`, with `nodetool enableuptimeview` and `nodetool disableuptimeview` for the running value | behaviour-changing | while on, the table listings of the node hold the view | `chronitondb-sandbox`: off | `SELECT` on `system_virtual_schema.tables` and `system_virtual_schema.columns`, and the `DESCRIBE` statements that list or describe the tables of `system_views` (C7) |

While the view is on, the node also holds the read counter, over JMX and in any metrics reporter the node has configured. The counter has the feature's own metric type, so no metric type of Apache Cassandra gains a metric.

[branching-and-review.md](../../process/branching-and-review.md#feature-switches-and-defaults) item 1 asks for a yaml setting and a nodetool toggle for every feature. Item 7 of the same page asks that a node with the feature off behaves exactly as Apache Cassandra. The two cannot both hold in full: a toggle that can turn the view on has to exist while the view is off. Decision record 0009 keeps the toggle and accepts the first three things of this list on every node. Four things are present on every node of a build that holds the feature, whatever the switch says:

1. One more row in `system_views.settings`, and one more name in the start log line that prints the configuration, both for `uptime_view_enabled`, because Apache Cassandra lists every field of `Config` (C10).
2. Two more commands in the output of `nodetool help`.
3. One more MBean, `org.chronitondb.uptime:type=UptimeView`.
4. The off error, in place of `table chronitondb_uptime does not exist`, for a `SELECT`, `INSERT`, `UPDATE`, `DELETE` or `TRUNCATE` that names `system_views.chronitondb_uptime`. Item 7 of the same page asks for this error.

Beyond these four, a node whose view is off differs from Apache Cassandra in its log only. The log of a node of a build that holds the feature, whatever its view state is or was, can hold these lines because of the feature and no other:

1. The WARN line of the start step, when the setting is `true` before the final gate.
2. The INFO line of each command that changes the node, an `enableuptimeview` or a `disableuptimeview` (FREQ-UPTIM-014).
3. The ERROR line that Apache Cassandra's `MBeanWrapper` writes when JMX refuses the switch MBean, or refuses a registration of the MBean of the read counter that the metrics registry attempted.
4. The warning of C14 at the start of a node that stored a prepared statement on the view while the view was on.

The feature writes no line of its own for a command that is refused, for a command that finds the node as it asks for or for a step that throws. nodetool prints those to the operator.

Nothing else differs from Apache Cassandra while the view is off: the node holds no metric of the feature, lists no table of it, writes no file and starts no thread for it. A node between on and off is no such node, and section 2.2 says what it can hold.

Item 2 of the same page says that the switch refuses to turn on before the final milestone gate, and names no form for a node start. Decision record 0007 chose the form: the node starts with the view off and logs one warning that names the setting, and `enableuptimeview` is refused.

## 3. Feature requirements

"The node" is the node that executes the statement, runs the command or starts. "On", "off", "the running value", "the final gate" and "the off error" are defined in section 2.2. "Every table listing" and "between on and off" are defined there too. "The view state" and "a read" are defined there as well. A node that is between on and off is neither on nor off, and FREQ-UPTIM-029, FREQ-UPTIM-036, FREQ-UPTIM-038, FREQ-UPTIM-041 and FREQ-UPTIM-043 say what holds for it.

FREQ-UPTIM-001 (state driven): While the view is on, the node MUST answer `SELECT * FROM system_views.chronitondb_uptime`, sent by a client that passes Apache Cassandra's permission check, with exactly one row, whose columns are those of section 2.2 and whose `key` is `local`. Source: stakeholder need.

FREQ-UPTIM-002 (ubiquitous): The `started_at` column MUST hold the value that the `RuntimeMXBean.getStartTime()` method of the node's JVM returns. Source: stakeholder need.

FREQ-UPTIM-003 (ubiquitous): The `uptime_seconds` column MUST hold the value that the `RuntimeMXBean.getUptime()` method of the node's JVM returns at the read, divided by 1000 and rounded down, which is how `nodetool info` computes its `Uptime (seconds)` line. Source: stakeholder need.

FREQ-UPTIM-004 (ubiquitous): The node MUST take the values of the row from its own running process only, with no message to another node and no value stored by an earlier process of the node. Source: stakeholder need.

FREQ-UPTIM-005 (state driven): While the view is on, the node MUST refuse every statement that writes to the view or truncates it, with the error Apache Cassandra returns for its read-only virtual tables (C15). Source: risk, problem 5 of section 4.

FREQ-UPTIM-006 (unwanted behaviour): If the node's authorizer requires authorization and a role that is not a superuser holds `SELECT` on neither the view nor the keyspace `system_views`, then the node MUST refuse that role's `SELECT` on the view while it is on with the unauthorized error Apache Cassandra returns for the other tables of `system_views`. Source: stakeholder need.

FREQ-UPTIM-007 (ubiquitous): The feature MUST NOT change a file under `src/java/org/apache/cassandra/auth` or the file `ClientState.java`. Source: stakeholder need.

FREQ-UPTIM-008 (ubiquitous): The yaml setting `uptime_view_enabled` MUST default to `false`. Source: stakeholder need.

FREQ-UPTIM-009 (event driven): When a node starts with `uptime_view_enabled` set to `true` and the final gate is passed, the node MUST turn the view on before it loads its stored prepared statements, which it does before it accepts a client connection (C3). Source: stakeholder need.

FREQ-UPTIM-010 (event driven): When `nodetool enableuptimeview` runs against a node whose final gate is passed and whose view is off, the node MUST turn the view on and set the running value to `true`. Source: stakeholder need.

FREQ-UPTIM-011 (event driven): When `nodetool disableuptimeview` runs against a node whose view is on or whose running value is `true`, the node MUST turn the view off, if it is on, and set the running value to `false`. Source: stakeholder need.

FREQ-UPTIM-012 (event driven): When `enableuptimeview` runs against a node whose final gate is passed and whose view is on, or `disableuptimeview` runs against a node whose view is off and whose running value is `false`, the node MUST leave the view, the running value and the log as they are, and the command succeeds. Source: risk, problem 6 of section 4.

FREQ-UPTIM-013 (ubiquitous): The commands of the feature MUST change only the memory of the node they run against, with nothing written to `cassandra.yaml` or to any other file, so that a restart returns to the value in `cassandra.yaml`. Source: stakeholder need.

FREQ-UPTIM-014 (event driven): When a command of the feature is neither refused nor covered by FREQ-UPTIM-012, the node MUST log, before it changes anything, one INFO line that holds the name `uptime_view_enabled`, the running value before the command and the running value the command asks for. Source: stakeholder need.

FREQ-UPTIM-015 (state driven): While the view is off, the node MUST NOT list the view in `system_virtual_schema.tables`, in `system_virtual_schema.columns` or in the output of `DESCRIBE TABLES`, `DESCRIBE KEYSPACE system_views`, `DESCRIBE SCHEMA` or `DESCRIBE FULL SCHEMA`. Source: stakeholder need.

FREQ-UPTIM-016 (state driven): While the view is off, the node MUST refuse a `SELECT`, `INSERT`, `UPDATE`, `DELETE` or `TRUNCATE` that names the view, alone or in a `BATCH`, with an invalid request error whose message is the off error of section 2.2. Source: stakeholder need.

FREQ-UPTIM-017 (state driven): While the view is off, the node MUST refuse the execution of a statement on the view that a client prepared while the view was on, with an invalid request error whose message is the off error of section 2.2. Source: stakeholder need.

FREQ-UPTIM-018 (state driven): While the view is off, the node MUST give every statement that names the view and is covered by neither FREQ-UPTIM-016 nor FREQ-UPTIM-017 the answer Apache Cassandra gives the same statement for a table name that `system_views` does not hold, with the view's name where Apache Cassandra puts the table name. Source: stakeholder need.

FREQ-UPTIM-019 (ubiquitous): The node MUST give a statement that names a table that does not exist, under any name other than exactly `chronitondb_uptime` in exactly `system_views`, a name that differs only in case included, the error Apache Cassandra gives it. Source: stakeholder need.

FREQ-UPTIM-020 (ubiquitous): The feature MUST NOT change the output of `nodetool info` or the rows of `system_views.gossip_info`. Source: stakeholder need.

FREQ-UPTIM-021 (ubiquitous): The feature MUST start no thread and write no file. Source: stakeholder need.

FREQ-UPTIM-022 (unwanted behaviour): If a node starts with `uptime_view_enabled` set to `true` while the final gate is not passed, then the node MUST finish its start with the view off. Source: decision record 0007.

FREQ-UPTIM-023 (unwanted behaviour): If a node starts with `uptime_view_enabled` set to `true` while the final gate is not passed, then the node MUST log one WARN line that names `uptime_view_enabled`. Source: decision record 0007.

FREQ-UPTIM-024 (unwanted behaviour): If `nodetool enableuptimeview` runs against a node whose final gate is not passed, then the node MUST refuse the call, whatever the running value, so that nodetool prints the line `nodetool: The node uptime view cannot be turned on in this build.` and exits with status 1, with the view left off and the running value left as it is. Source: decision record 0007.

FREQ-UPTIM-025 (state driven): While the view is on, the node MUST hold in Apache Cassandra's metrics registry one Dropwizard `Counter` under the metric name whose MBean name is `org.chronitondb.metrics:type=UptimeView,name=Reads`. Source: [quality-requirements.md](../../process/quality-requirements.md#observability), item 1.

FREQ-UPTIM-026 (event driven): When Apache Cassandra's read path asks the view for its data while the view is on, the view MUST raise by one the counter of the switch change that turned the view on, also for a read whose key filter leaves no row. Source: [quality-requirements.md](../../process/quality-requirements.md#observability), item 1.

FREQ-UPTIM-027 (state driven): While the view is off, the node MUST NOT hold a metric of the feature. Source: stakeholder need.

FREQ-UPTIM-028 (unwanted behaviour): If a throwable is thrown in the start step of the switch, outside the registration of the switch MBean, then the start step MUST let that throwable out to its caller, without catching it. Source: risk, problem 1 of section 4.

FREQ-UPTIM-029 (unwanted behaviour): If a step of a command of the feature throws, then the command MUST end there, so that nodetool prints the line `error: ` with the message and exits with status 2, with the steps already done left as they are. Source: decision record 0011.

FREQ-UPTIM-030 (ubiquitous): The feature MUST ship a reference page, `docs/reference/node-uptime-view.md`, that names the view and its columns with their units, the setting with its default, the two commands with their refusals and the four cases of a node with no switch MBean, the return to the yaml value at a restart, the off error, the state between on and off with `disableuptimeview` as the way back, the read counter with what it counts and with what the node does when JMX already holds its name, and the need to read each node over a connection to that node. Source: stakeholder need.

FREQ-UPTIM-031 (ubiquitous): The reference page MUST give the `GRANT` statement on the view as the way to let a role read it, and say that a grant on the keyspace `system_views` also opens its other tables, that every client reads the view while it is on where the authorizer requires no authorization, that `GRANT` and `REVOKE` on the view work only on a node where the view is on, and that a grant on the view stays when the view is turned off. Source: risk, problems 5 and 9 of section 4.

FREQ-UPTIM-032 (ubiquitous): The reference page and `NEWS-chronitondb.txt` MUST state the upgrade order of section 7.3, the rollback step of section 7.4 and the way back of section 2.2 for a node that a fault in the start step stopped. Source: risk, problems 1 and 8 of section 4.

FREQ-UPTIM-033 (unwanted behaviour): If the registration of the switch MBean fails at the start of a node, then the node MUST go on with its start, with the failure logged in the ERROR line of Apache Cassandra's `MBeanWrapper` (C17). Source: decision record 0012.

FREQ-UPTIM-034 (ubiquitous): The node MUST run the start step and the operations of the switch MBean one at a time, so that a command waits for a start step or a command that is running. Source: risk, problem 6 of section 4.

FREQ-UPTIM-035 (event driven): When the view is turned on or off, the node MUST keep every table that Apache Cassandra registered in `system_views` registered as the same object, with the rows and the state it had before. Source: risk, problem 2 of section 4.

FREQ-UPTIM-036 (unwanted behaviour): If a step of a command threw and left the node between on and off, then a later `disableuptimeview` MUST bring the node to the off state, with the view off, no metric of the feature and the running value `false`. Source: decision record 0011.

FREQ-UPTIM-037 (event driven): When a read of the view runs at the moment of a switch change, the node MUST answer it with the row or with the off error, with no metric of the feature left on the node once the view is off. Source: risk, problem 6 of section 4.

FREQ-UPTIM-038 (state driven): While the node is between on and off, the node MUST refuse every read of the view with an invalid request error whose message is the off error of section 2.2. Source: decision record 0011.

FREQ-UPTIM-039 (unwanted behaviour): If a command of the feature runs against a node that has no switch MBean, then the command MUST print the line `nodetool: This node has no switch for the node uptime view.` and exit with status 1. Source: risk, problem 9 of section 4.

FREQ-UPTIM-040 (optional feature): Where the line holds the file `conf/cassandra_chronitondb.yaml` when the pull request of the last item of the feature is opened, the feature MUST add the setting `uptime_view_enabled` to that file, commented out with its default `false`. Source: [release.md](../../process/release.md#the-configuration-file), item 1.

FREQ-UPTIM-041 (unwanted behaviour): If `nodetool enableuptimeview` runs against a node whose final gate is passed and that is between on and off, then the node MUST refuse the call, so that nodetool prints the line `nodetool: The node uptime view is between on and off on this node. Run nodetool disableuptimeview first.` and exits with status 1, with the node left as it is. Source: decision record 0013.

FREQ-UPTIM-042 (unwanted behaviour): If JMX does not take the MBean of the read counter at a switch change to on, then the node MUST finish the switch change with the view on and the counter in the metrics registry. Source: decision record 0012.

FREQ-UPTIM-043 (state driven): While the node is between on and off, the node MUST give a statement on the view that is no read the answer of a node whose view is on where the node lists the view, and the answer of a node whose view is off where it does not. Source: decision record 0013.

FREQ-UPTIM-044 (ubiquitous): The constructors and the static initialisers of the classes that the start step runs on a node whose setting is `false` MUST only assign fields, with the getting of a logger as their one call into other code. Source: risk, problem 1 of section 4.

## 4. Where problems could occur

Worst case first.

1. **A node does not start.** An operator sees a node that exits during its start. It is every node, the switch off included, if the call of the start step fails, for example because a class of the start step does not load or memory runs out. A constructor or a static initialiser of the start step that throws would stop every node too, and FREQ-UPTIM-044 rules that out. A registration of the switch MBean that JMX refuses does not stop a node (FREQ-UPTIM-033, decision record 0012). By design it is also each node whose configuration turns the view on, once the final gate is passed, if turning the view on throws. Such a node logs `Exception encountered during startup` with the throwable and exits (C3). A fault that every node of a cluster shares stops each node that is restarted, so a rolling restart shows it on the first node. A node whose fault is in turning the view on starts again once the setting is removed from its `cassandra.yaml` or set to `false`.
2. **Other tables of `system_views` are missing or fail.** An operator or a monitoring tool sees a table such as `system_views.settings` missing, or a read of it failing, after a switch change or while one runs. It comes from the switch, which registers `system_views` again: a list that lacks a table of Apache Cassandra, a table built a second time, or a moment in which a table is not found.
3. **Statements on other tables get a wrong answer.** A client sees a wrong error for a table that does not exist, or a statement on an existing table fails or is slower to prepare. It comes from the line added to `Schema.validateTable`, which every `SELECT`, `INSERT`, `UPDATE`, `DELETE` and `TRUNCATE` passes (C6).
4. **The view shows a wrong value.** An operator reads a start time that is not the one of the running process, or an uptime in the wrong unit or one that differs from `nodetool info` by more than the time between the two reads. After a restart the row still shows the values of the process before it. The operator then takes a node for restarted that was not, or the other way round, in the middle of a rolling restart. It comes from the view.
5. **The values reach a client that should not see them, or a client changes them.** A role with no grant reads the row, or a client writes to the view. It comes from a view that is not built on Apache Cassandra's read-only table, or from a change to permission code. Two things are by design. While the view is on, every logged in user can see the view's name in `system_virtual_schema.tables`, which Apache Cassandra lets every user read (C8). And on a node whose authorizer requires no authorization, every client reads the view while it is on, as it reads every table of `system_views` (C8).
6. **The switch does not do what the operator asked.** The view stays on after `disableuptimeview`, or off after `enableuptimeview` once the final gate is passed. A statement prepared while the view was on still returns the row after the view is turned off. A restart does not return to the yaml value. A command reports success after a change that failed, or a change that failed part way leaves a node that answers a read of the view with the row, or that `disableuptimeview` cannot bring back to the off state, or it leaves no INFO line. Two commands at the same time, or a command during the start, leave the listing and the running value in disagreement. The INFO line is missing or holds the wrong values. The read counter is missing while the view is on, stays after the view is turned off, comes back through a read that runs while the view is turned off, or does not rise with the reads after the view is turned on again. One thing is by design: a node whose JMX did not take the MBean of the read counter shows no counter of the view over JMX while the view is on, and the counter counts in the metrics registry (decision record 0012). Where another MBean holds the name of the counter, JMX shows that MBean until the view is turned off.
7. **A node whose view is off differs from Apache Cassandra by more than section 2.8 says.** A listing shows the view, a metric of the feature exists, or a statement that names the view gets an answer that is neither the off error nor the answer Apache Cassandra gives.
8. **A node started on an Apache Cassandra binary, or on an older ChronitonDB build, with the setting in its yaml does not start.** The operator sees `Invalid yaml. Please remove properties [uptime_view_enabled] from your cassandra.yaml` (C10). It happens after a rollback, and during an upgrade when the setting is written before the node has its new binary. The refusal is Apache Cassandra's own, for any key it does not know.
9. **A grant, a read or a command goes to a node that cannot serve it.** `GRANT SELECT ON system_views.chronitondb_uptime` fails with `Resource <table system_views.chronitondb_uptime> doesn't exist` on a node where the view is off (C9). A driver sends the `SELECT` to another node than the operator meant, and the answer is that node's row or the off error. A grant on the view stays after the view is turned off and gives its role the read again when the view is turned on. A command of the feature run against an Apache Cassandra node or an older ChronitonDB build finds no switch MBean, and answers with a text that misleads the operator.
10. **The view can be turned on before the feature is finished.** An operator of a build cut between two items turns on a view whose tests and pages are not complete. Or such a node refuses to start because of the setting, against decision record 0007.

### 4.1 Test plan

No scenario module and no parity suite exist on this line. Each requirement is proven by a unit test or an in-JVM distributed test, and each item's design record names them. Until the last item, a test that needs the view on passes the final gate by the rewrite of section 2.2. From the last item on, a test that needs the state before the gate uses the same rewrite the other way.

1. Problem 1: an in-JVM distributed test starts a node with the default configuration and expects the node to start, the view off and no metric of the feature (FREQ-UPTIM-008, FREQ-UPTIM-027). A test with the JMX feature makes the registration of the switch MBean fail, by a name that is already registered, starts a node with the setting `false` and one with the setting `true` and the gate passed, and expects each to start, with the ERROR line of `MBeanWrapper` in its log (FREQ-UPTIM-033). It runs `enableuptimeview` against one of them, where the MBean of the test holds the name of the switch MBean, and expects the line `nodetool: This node has no switch for the node uptime view.`, exit status 1 and no call of an operation of the MBean of the test (FREQ-UPTIM-039). A second test starts a node with the setting `true`, the gate passed and the method that turns the view on rewritten to throw. It expects the start of the test node to fail with the throwable the rewrite threw, itself or in the cause chain (FREQ-UPTIM-028). The review of the pull request that adds the start step checks the constructors and the static initialisers of its classes against FREQ-UPTIM-044. The same test then starts the node with the setting `false` and the same rewrite and expects it to start, which proves the way back. A documentation test checks the reference page and `NEWS-chronitondb.txt` for the way back (FREQ-UPTIM-032). Every in-JVM distributed test of the line starts its nodes through `setupVirtualKeyspaces` (C2), so a call of the start step that fails makes all of them fail. No test can show that the call never fails. These tests show that it does not fail on the builds they run on.
2. Problem 2: an in-JVM distributed test reads the table names of `system_views` and the columns of each from `system_virtual_schema`, turns the view on, turns it off and turns it on again. After each switch change it expects the same names and columns, with the view added exactly while it is on, and a `SELECT` on every table of `system_views` to succeed (FREQ-UPTIM-010, FREQ-UPTIM-011, FREQ-UPTIM-015). Inside the node it takes each table object of `system_views` from the registry before the first switch change and after the last and expects the same objects, and it expects a row that `system_views.system_logs` held before a switch change to be there after it (FREQ-UPTIM-035). A second test reads `system_views.settings` in a loop from one thread while another thread makes 100 switch changes, and expects no read to fail. A third test makes 100 calls of `enableuptimeview` from one thread and 100 calls of `disableuptimeview` from another at the same time. When both have ended it expects the view on or off, the listing and the running value to agree with it, one counter when the view is on and none when it is off (FREQ-UPTIM-034). Apache Cassandra's own unit tests and in-JVM distributed tests that the line's checks run are run unchanged with the switch off. A pre-existing test is not weakened, as [conventions.md](../../process/conventions.md#code-layout) item 5 says.
3. Problem 3: a test sends a `SELECT`, an `INSERT`, an `UPDATE`, a `DELETE` and a `TRUNCATE` that name a table `system_views` does not hold, other than the view, and one of each that names a table a user keyspace does not hold. It expects the text `table <name> does not exist` for each, where `<name>` is the table name without its keyspace, as Apache Cassandra writes it. It sends the same five statements with the view's name in another case in double quotes, `system_views."Chronitondb_Uptime"`, with the view off, and expects the same Apache Cassandra text and not the off error (FREQ-UPTIM-019). Apache Cassandra's own tests of missing tables run unchanged. The review of the pull request that edits `Schema.validateTable` checks that the added line is on the branch for a table that is not found only, so a statement on a table that exists runs no code of the feature.
4. Problem 4: unit tests build the row from a time source of their own. One gives the uptimes 999, 1000 and 1999 milliseconds and expects 0, 1 and 1 in `uptime_seconds` (FREQ-UPTIM-003). One expects `started_at` to hold the start time its time source gives (FREQ-UPTIM-002). A unit test of the node's own time source expects its start time to equal `RuntimeMXBean.getStartTime()` of the test's JVM, and its uptime to lie between two reads of `RuntimeMXBean.getUptime()` that the test takes before and after (FREQ-UPTIM-002, FREQ-UPTIM-003). An in-JVM distributed test reads the view, runs `nodetool info` on the same node and reads the view again. It expects exactly one row with the `key` `local` at each read, and the `Uptime (seconds)` line to lie between the two `uptime_seconds` values (FREQ-UPTIM-001, FREQ-UPTIM-003). It also reads with a filter on another key and with a column list. A test starts two JVM processes one after the other. Each prints the start time and the uptime of the node's own time source. The test expects the second start time to be later than the first (FREQ-UPTIM-004). The review of each pull request checks that the feature sends no message and reads no stored value for the row (FREQ-UPTIM-004). No test on this line restarts a node as a real process, because the nodes of an in-JVM distributed test share one JVM (C16).
5. Problem 5: an in-JVM distributed test with authentication and authorization on reads the view as a superuser, as a role granted `SELECT` on the view, as a role granted `SELECT` on the keyspace, as a role granted `SELECT` on all keyspaces only, and as a role with no grant. The last two are refused with the unauthorized error (FREQ-UPTIM-006). A test tries an `INSERT`, an `UPDATE`, a `DELETE` and a `TRUNCATE` on the view while it is on and expects Apache Cassandra's refusal (FREQ-UPTIM-005). A check of the changed files of each pull request expects none under `src/java/org/apache/cassandra/auth` and not `ClientState.java` (FREQ-UPTIM-007), and its review checks the imports against section 2.7. A documentation test checks the reference page for the grant statement and the warnings (FREQ-UPTIM-031).
6. Problem 6: an in-JVM distributed test with the JMX feature starts a node with the setting `false`, runs `enableuptimeview` and reads the row. It runs `disableuptimeview` and expects the off error. It prepares a `SELECT` while the view is on, turns the view off and expects the off error from the execution of the prepared statement, then turns the view on and expects the row from the same prepared statement (FREQ-UPTIM-010, FREQ-UPTIM-011, FREQ-UPTIM-016, FREQ-UPTIM-017). After each command it reads the row of `uptime_view_enabled` in `system_views.settings` and expects the new running value. It expects one INFO line with the name of the setting, the running value before the command and the value the command asked for, for each command that changed the node, and no new line of the feature for a command that found the node as it asked for (FREQ-UPTIM-012, FREQ-UPTIM-014). A test turns the view on by a command, restarts the node whose yaml says `false` and expects the view off, and the other way round (FREQ-UPTIM-009, FREQ-UPTIM-013). The review of each pull request checks that the feature writes no file and starts no thread (FREQ-UPTIM-013, FREQ-UPTIM-021). A test rewrites the step that registers `system_views` with the view to throw an `IllegalStateException` after it has registered, and runs `enableuptimeview`. It expects nodetool to print the line `error: ` with the message of the throwable and to exit with status 2, the INFO line of the command in the log, the view still in `system_virtual_schema.tables` and the running value still `false`, since the steps done stay (FREQ-UPTIM-014, FREQ-UPTIM-029). It expects the off error from a `SELECT` on the view on that node (FREQ-UPTIM-038). On that node, which still lists the view, it expects `Modification is not supported by table` from an `INSERT` on the view and success from a `GRANT` on it (FREQ-UPTIM-043). It runs `enableuptimeview` again without the rewrite and expects the line `nodetool: The node uptime view is between on and off on this node. Run nodetool disableuptimeview first.`, exit status 1, no new INFO line and the node as it was (FREQ-UPTIM-041). It then runs `disableuptimeview` and expects one more INFO line, the view off in every table listing, no metric of the feature and the running value `false` (FREQ-UPTIM-036). It runs `enableuptimeview` once more and expects the row and the read counter at 0. A test with the JMX feature registers an MBean of its own under the name of the read counter, runs `enableuptimeview` and expects the command to succeed, the row from a `SELECT` and the counter at 1 in the metrics registry (FREQ-UPTIM-042). It then runs `disableuptimeview` and expects no MBean under the name of the read counter, since the registry unregisters by name. A test expects the read counter at 0 right after the view is turned on, in the metrics registry and over JMX, at 1 after one `SELECT` on the view, unchanged after a `SELECT` that the permission check refused, absent after the view is turned off, at 0 again after the view is turned on again, at 1 after the execution of a `SELECT` that was prepared before the view was turned off, and at 2 after a `SELECT` with a filter on another key (FREQ-UPTIM-025, FREQ-UPTIM-026, FREQ-UPTIM-027). Every `SELECT` of this test runs with paging off. A test reads the view in a loop from one thread while another thread makes 100 switch changes and ends with `disableuptimeview`. It expects each read to give the row or the off error, and no metric of the feature once the loop has ended (FREQ-UPTIM-037). A documentation test checks the reference page for each part FREQ-UPTIM-030 names.
7. Problem 7: an in-JVM distributed test reads, with the view off, the rows of `system_virtual_schema.tables` and `system_virtual_schema.columns` for `system_views` and the output of the four `DESCRIBE` statements, and expects the name `chronitondb_uptime` in none of the six (FREQ-UPTIM-015). It lists every name of the metrics registry that starts with `org.chronitondb` and expects none of this feature (FREQ-UPTIM-027). It sends a `SELECT`, an `INSERT`, an `UPDATE`, a `DELETE`, a `TRUNCATE` and a `BATCH` with an `INSERT` that name the view, and the prepare of a `SELECT`, and expects the off error for each (FREQ-UPTIM-016). It sends a `DESCRIBE TABLE`, a `GRANT`, a `REVOKE` and a `LIST ALL PERMISSIONS` that name the view, sends the same four with another table name that `system_views` does not hold, and expects each pair of answers to be equal but for the name (FREQ-UPTIM-018). It runs once with the setting `false`, and once with the setting `true` and the final gate not passed. A test reads the output of `nodetool info` and the rows of `system_views.gossip_info` with the view off and with the view on and expects the same lines and columns (FREQ-UPTIM-020). A test with the JMX feature and the view off reads the names in `system_views.settings`, the commands in the output of `nodetool help` and the MBean names whose domain starts with `org.chronitondb`. It expects of this feature exactly the row `uptime_view_enabled`, the two commands and the switch MBean, as section 2.8 lists them. A check of the changed files of each pull request expects no file of Apache Cassandra under `conf/` among them, and, where the line holds `conf/cassandra_chronitondb.yaml` when the pull request of the last item is opened, expects that pull request to add the commented line of `uptime_view_enabled` with the value `false` to it (FREQ-UPTIM-040).
8. Problem 8: no test on this line can start an Apache Cassandra binary. The in-JVM distributed tests of problems 1, 6 and 10 start their nodes with the setting `true` and `false`, and the test node loads its configuration through Apache Cassandra's `YamlConfigurationLoader` with the check for unknown keys on (C10), so a setting that does not load fails them. A documentation test checks that the reference page and `NEWS-chronitondb.txt` hold the upgrade order and the rollback step (FREQ-UPTIM-032).
9. Problem 9: an in-JVM distributed test with one node whose view is on and one whose view is off sends the `GRANT` on the view to each. It expects the failure of C9 on the node whose view is off and success on the other. It then turns the view off and on again on the first node and expects the role's `SELECT` to succeed again. The documentation test of problem 5 checks the page for these points (FREQ-UPTIM-031). No test on this line can run a command against an Apache Cassandra node. The test of problem 1 runs a command against a node that has no switch MBean (FREQ-UPTIM-039). The reference page says that the commands need a build that holds the feature (FREQ-UPTIM-030).
10. Problem 10: a test starts a node with the setting `true` and the final gate not passed. It expects the node to start, the view off, the value `true` in the row of `uptime_view_enabled` in `system_views.settings`, and one WARN line of the feature that names the setting (FREQ-UPTIM-022, FREQ-UPTIM-023). On that node it runs `enableuptimeview` and expects the line `nodetool: The node uptime view cannot be turned on in this build.`, exit status 1, the view still off and the running value still `true` (FREQ-UPTIM-024). It then runs `disableuptimeview` and expects one INFO line, the running value `false`, and the keyspace object that the registry holds for `system_views` to be the one it held before the command (FREQ-UPTIM-011).

## 5. Quality requirements

Not applicable: this section is required from Challenging size, and this feature is Normal size. Each item's design record answers the checklist of [quality-requirements.md](../../process/quality-requirements.md) in small form.

## 6. Threat model

| Entry point | Threat (STRIDE) | Mitigation | FREQ |
|---|---|---|---|
| A `SELECT` on the view over CQL | Information disclosure: a client learns when a node last started | The view is off by default. Apache Cassandra's permission rule for `system_views` decides who reads it. The feature changes no permission code | FREQ-UPTIM-006, FREQ-UPTIM-007, FREQ-UPTIM-008 |
| A `SELECT` on the view over CQL, on a node whose authorizer requires no authorization | Information disclosure: every client reads the row while the view is on | The view follows the rule of the other tables of `system_views`, which every client of such a node reads already. The view is off by default, and the reference page warns about this case | FREQ-UPTIM-008, FREQ-UPTIM-031 |
| A statement that names the view while it is off | Information disclosure: the off error tells every logged in user that the node runs ChronitonDB | Accepted. The switch rules ask for an error that names the switch. The error holds no value of the node | FREQ-UPTIM-016 |
| The table listings while the view is on | Information disclosure: every logged in user sees the view's name | Accepted while the switch is on. While the view is off, no listing shows it | FREQ-UPTIM-015 |
| A `SELECT` on the view over CQL | Denial of service: a client reads the view in a loop | A read builds one row from two values of the node's own process, with no disk access and no message to another node | FREQ-UPTIM-004 |
| A write or a `TRUNCATE` on the view over CQL | Tampering: a client changes what the view shows | The view is read only | FREQ-UPTIM-005 |
| The two commands and the switch MBean over JMX | Elevation of privilege, tampering: someone turns the view on or off | Whoever reaches the node's JMX server can already run every nodetool command. Turning the view on gives no read access, since the CQL permission rule still applies | FREQ-UPTIM-006 |
| The two commands and the switch MBean over JMX | Denial of service: someone makes switch changes in a loop | A switch change replaces one registered keyspace in memory. The tables of Apache Cassandra stay the same objects, and their reads go on | FREQ-UPTIM-010, FREQ-UPTIM-011 |
| The two commands and the switch MBean over JMX | Repudiation: the switch changes and nothing shows that it did | Each command that changes the node logs its INFO line before it changes anything, with the running value before the command and the value it asks for | FREQ-UPTIM-014 |
| The yaml setting `uptime_view_enabled` | Tampering: someone who can edit `cassandra.yaml` and restart the node turns the view on | No new threat. Whoever edits that file already controls the node. Apache Cassandra logs the configuration at start (C10) | FREQ-UPTIM-008 |
| The read counter over JMX | Information disclosure: whoever reads the node's MBeans sees the counter and learns that the view is on | The counter exists from a switch change to on until the switch change to off that follows, so a node between on and off can still hold it (decision record 0011). A node whose view is off holds none, also when a read ran while the view was turned off. The counter holds a count and no start time | FREQ-UPTIM-027, FREQ-UPTIM-036, FREQ-UPTIM-037 |

## 7. Compatibility

### 7.1 On-disk format changes

This feature changes no format, schema or protocol. A virtual table has no file on disk and no row in the schema tables. The feature adds no native protocol message and no message between nodes.

### 7.2 Mixed-version cluster

1. A read of the view on a node where it is on returns that node's own row, whatever the other nodes run.
2. A read of the view on a node of this build where it is off gets the off error. On an Apache Cassandra node or an older ChronitonDB build it gets `table chronitondb_uptime does not exist`.
3. A driver can send a statement to any node. An operator who wants one node's row reads the view over a connection to that node, as cqlsh makes.
4. Grants are stored for the whole cluster, and the view exists per node. A `GRANT` on the view succeeds only on a node where the view is on (C9). Once made, it counts on every node where the view is on.
5. The two commands work against a node of a build that holds the feature. Against another node they print that the node has no switch for the view (FREQ-UPTIM-039).
6. Nodes exchange nothing for this feature, so a node without it is not affected by a node with it.

### 7.3 Upgrade path and prerequisites

An upgrade from Apache Cassandra 5.0, or from an older ChronitonDB build of the line, needs nothing for this feature. The setting defaults to `false`, so an upgraded node behaves as before until an operator turns the view on. The upgrade order for an operator who wants the view: first start the node on the new binary. Then turn the view on with `nodetool enableuptimeview`, which lasts until the node stops. To have the view on after later starts too, add the setting to the node's `cassandra.yaml`. A node that starts on its old binary with the setting in its `cassandra.yaml` does not start (C10). The setting is not part of the line's minimum setup.

### 7.4 Rollback path

The rollback step: remove `uptime_view_enabled` from the `cassandra.yaml` of a node before the node starts on an Apache Cassandra binary or on a ChronitonDB build older than this feature. Such a binary refuses the key and does not start (C10). Nothing has to be dropped or rebuilt on disk. A prepared statement on the view that the node stored is removed at the next start, with one warning in the log (C14). A grant on the view stays in the cluster and gives nothing while no node has the view on.

### 7.5 Runbook entries

No runbook page exists on this line yet. The feature adds the reference page `docs/reference/node-uptime-view.md`, which holds the upgrade order of section 7.3, the rollback step of section 7.4 and the way back after a fault in the start step, until the line's runbooks exist. The feature also adds an entry in `NEWS-chronitondb.txt` with the same three points (FREQ-UPTIM-032). The item that writes them creates the folder `docs/reference/` or the file `NEWS-chronitondb.txt` when the line does not hold it yet.

## 8. Dependencies

Not applicable: the feature adds no library and changes no version. The two commands use the Airline library that the nodetool commands of the line already use.

## 9. Risks

Not applicable: this section is required from Challenging size or for cross-cutting reach, and this feature is Normal size with one area. Section 4 names where problems could occur, and section 12 says what a port to another line finds.

## 10. Decisions

1. [0007. A node starts with the node uptime view off when its configuration turns the view on before the final gate](../../decisions/0007-node-uptime-view-off-before-the-final-gate.md): one warning that names the setting, never a refusal to start, and `enableuptimeview` is refused.
2. [0008. The node uptime view is delivered in one milestone](../../decisions/0008-node-uptime-view-delivered-in-one-milestone.md): the view, the switch, the tests and the documentation pass one gate.
3. [0009. The node uptime view keeps its nodetool toggle](../../decisions/0009-node-uptime-view-keeps-its-nodetool-toggle.md): the yaml setting and two nodetool commands, with a settings row, two commands and one MBean on every node.
4. [0010. The node uptime view stays at Normal risk](../../decisions/0010-node-uptime-view-stays-at-normal-risk.md): an exception to the class table for a wrong value in the view and a node that does not start.
5. [0011. A switch change of the node uptime view that fails is not undone](../../decisions/0011-node-uptime-view-failed-switch-change-is-not-undone.md): the command stops and reports the error, and `disableuptimeview` is the way back.
6. [0012. A node goes on when JMX refuses an MBean of the node uptime view](../../decisions/0012-node-uptime-view-goes-on-when-jmx-refuses-an-mbean.md): one ERROR line of Apache Cassandra, never a failed start or a failed command.
7. [0013. enableuptimeview is refused on a node that is between on and off](../../decisions/0013-node-uptime-view-enable-refused-between-on-and-off.md): the refusal names `disableuptimeview`, and a statement that is no read follows the table listing.

## 11. Milestones outline

The delivery plan gives the detail and proposes the line.

1. **Milestone 1, the node uptime view.** The view, the setting, the switch with its MBean and the two commands, the off error, the read counter, the reference page and the `NEWS-chronitondb.txt` entry. The last item passes the final gate. It makes testable: a granted role reads the row, the uptime agrees with `nodetool info`, an operator turns the view on and off on a running node, a restart returns to the yaml value, and a node whose view is off answers as section 2.8 says. This is the final milestone (decision record 0008).
   - For the design record: say whether a test loads a `cassandra.yaml` file that holds `uptime_view_enabled`, beside the in-JVM distributed tests that load the setting through the test node's configuration.
   - For the design record: say what an operator does when `disableuptimeview` fails again on a node that is between on and off.
   - For the design record: cite each caller of `Schema.validateTable` that the record relies on by its symbol, as C6 does.
   - For the design record: say what the reference page tells an operator whose `disableuptimeview` failed again, a restart of the node included.

## 12. Prior art

These rules apply to every source:

1. Describe and cite behaviour, published designs, papers, public documentation and code under licences compatible with the Apache License 2.0.
2. Code or text under an incompatible licence, for example the Elastic License, SSPL, BUSL or a proprietary licence, MUST NOT be copied. The behaviour of such a system is taken only from its public documentation. Code under a compatible licence MAY be used only with credit. See [conventions.md](../../process/conventions.md#code-from-elsewhere).
3. Contributors working on the project's behalf MUST NOT search for or read patents for design work. Any patent concern goes to the maintainers.

**Apache Cassandra.** Three sources are kept apart.

- Our line: ChronitonDB chronitondb-sandbox at `17e0b84a36`.
- Apache base: Apache Cassandra cassandra-5.0 at `76550e9314`. No file under `src/` or `test/` differs between the Apache base and our line. So each fact below holds in the Apache base at the same file and line as on our line.
- Apache now: Apache Cassandra cassandra-5.0 at `9e36adecef`, cassandra-6.0 at `d60653e71c` and trunk at `7d7d6b30db`.

Apache Cassandra shows the uptime of a node's process through `nodetool info` only, over JMX (C11). No table of `system_views` on our line holds a start time or an uptime of the process (C1). `system_views.gossip_info` has a `generation` column for each node, `GossipInfoTable.buildTableMetadata`, `src/java/org/apache/cassandra/db/virtual/GossipInfoTable.java:168`, the column at line 177, ChronitonDB chronitondb-sandbox at `17e0b84a36`. It holds the gossip generation of a node, which `SystemKeyspace.incrementAndGetGeneration`, `src/java/org/apache/cassandra/db/SystemKeyspace.java:1129`, the same tree, sets from the clock in whole seconds or from the stored generation plus one. So it changes at a restart, but it is no start time of the process and gives no uptime. Apache now adds a table `system_views.local` on cassandra-6.0 and trunk, with a `gossip_generation` column and no start time and no uptime (C1). The view takes its place in `system_views` from Apache Cassandra's own node views, its `key` column with the value `local` from `system.local`, its uptime from the call `nodetool info` makes, and the form of its two commands from Apache Cassandra's pairs such as `enablebackup` and `disablebackup` (C12, C13).

| Id | What the code does | Our line | Apache now |
|---|---|---|---|
| C1 | The tables of `system_views` are a fixed list that the constructor builds once. No table holds a start time or an uptime of the process | `SystemViewsKeyspace.SystemViewsKeyspace`, `src/java/org/apache/cassandra/db/virtual/SystemViewsKeyspace.java:30`, the list from line 32, ChronitonDB chronitondb-sandbox at `17e0b84a36` | The same file in Apache Cassandra cassandra-5.0 at `9e36adecef`. A longer list in `SystemViewsKeyspace.java:33`, with `LocalTable` at line 69, Apache Cassandra cassandra-6.0 at `d60653e71c` and trunk at `7d7d6b30db`. `LocalTable.LocalTable`, `src/java/org/apache/cassandra/db/virtual/LocalTable.java:71`, has the column `gossip_generation` at line 84 and no start time or uptime, in both |
| C2 | The node registers `system_views` once at start. The in-JVM distributed test node calls the same method | `CassandraDaemon.setupVirtualKeyspaces`, `src/java/org/apache/cassandra/service/CassandraDaemon.java:534`, the registration at line 537, and `Instance.startup`, `test/distributed/org/apache/cassandra/distributed/impl/Instance.java:581`, the call at line 650, ChronitonDB chronitondb-sandbox at `17e0b84a36` | The same file in Apache Cassandra cassandra-5.0 at `9e36adecef`. `CassandraDaemon.java:641`, the registration at line 644, Apache Cassandra cassandra-6.0 at `d60653e71c` and trunk at `7d7d6b30db`. `Instance` was not read on Apache now |
| C3 | At start the node starts its JMX server, registers its virtual keyspaces, loads its stored prepared statements and then sets up its client transports, in this order. A throwable that leaves the start code ends the start: the node logs `Exception encountered during startup` with the throwable and exits | `CassandraDaemon.setup`, `src/java/org/apache/cassandra/service/CassandraDaemon.java:229`, the four calls at lines 246, 291, 377 and 443, and `CassandraDaemon.activate` at line 718 with its call of `exitOrFail` at line 759, ChronitonDB chronitondb-sandbox at `17e0b84a36` | The same file in Apache Cassandra cassandra-5.0 at `9e36adecef`. `CassandraDaemon.setup`, `CassandraDaemon.java:244`, the four calls at lines 261, 331, 394 and 447, and the call of `exitOrFail` at line 874, Apache Cassandra cassandra-6.0 at `d60653e71c` and trunk at `7d7d6b30db` |
| C4 | The registry of virtual keyspaces holds each keyspace by name and each table by id. A keyspace has a fixed list of tables. Registering a keyspace under a name that is already registered replaces the keyspace in one step and then puts each of its tables under its id. On our line the clean up of the earlier keyspace's tables removes nothing, because it removes by the table object from a map keyed by id. The id of a virtual table is computed from its keyspace and name | `VirtualKeyspaceRegistry.register`, `src/java/org/apache/cassandra/db/virtual/VirtualKeyspaceRegistry.java:41`, the replacement at line 43, the clean up at line 46 and the puts at line 47, `VirtualKeyspace.VirtualKeyspace`, `src/java/org/apache/cassandra/db/virtual/VirtualKeyspace.java:36`, and `TableMetadata.Builder.build`, `src/java/org/apache/cassandra/schema/TableMetadata.java:848`, the id at line 857, ChronitonDB chronitondb-sandbox at `17e0b84a36` | The same file in Apache Cassandra cassandra-5.0 at `9e36adecef`. `VirtualKeyspaceRegistry.register`, `VirtualKeyspaceRegistry.java:42`, removes the earlier keyspace's tables by id at line 47 before it puts the new ones, and an `unregister` method exists at line 51, Apache Cassandra cassandra-6.0 at `d60653e71c` and trunk at `7d7d6b30db`. `VirtualKeyspace` and `TableMetadata` were not read on Apache now |
| C5 | A read of a virtual table finds the table by its id in the registry | `SinglePartitionReadCommand.VirtualTableSinglePartitionReadCommand.executeLocally`, `src/java/org/apache/cassandra/db/SinglePartitionReadCommand.java:1413`, the lookup at line 1415, and `PartitionRangeReadCommand.VirtualTablePartitionRangeReadCommand.executeLocally`, `src/java/org/apache/cassandra/db/PartitionRangeReadCommand.java:553`, the lookup at line 555, ChronitonDB chronitondb-sandbox at `17e0b84a36` | The same files in Apache Cassandra cassandra-5.0 at `9e36adecef`. The lookups are at `SinglePartitionReadCommand.java:1574` and `PartitionRangeReadCommand.java:654`, Apache Cassandra cassandra-6.0 at `d60653e71c` and trunk at `7d7d6b30db` |
| C6 | A statement finds its table by name, and a missing one fails with `table <name> does not exist`. `SELECT`, the statements that modify data and `TRUNCATE` call this method | `Schema.validateTable`, `src/java/org/apache/cassandra/schema/Schema.java:429`, the error at line 440, called from `SelectStatement.RawStatement.prepare`, `src/java/org/apache/cassandra/cql3/statements/SelectStatement.java:1213`, at line 1215, from `ModificationStatement.Parsed.prepare`, `src/java/org/apache/cassandra/cql3/statements/ModificationStatement.java:951`, at line 953, and from `TruncateStatement.validate`, `src/java/org/apache/cassandra/cql3/statements/TruncateStatement.java:59`, at line 61. Two more callers send no statement of their own to this branch: `StorageProxy.legacyCas`, `src/java/org/apache/cassandra/service/StorageProxy.java:331`, the call at line 344, on the path of a conditional write that `ModificationStatement` already checked, and the offline tool `SSTableExpiredBlockers.main`, `src/java/org/apache/cassandra/tools/SSTableExpiredBlockers.java:51`, the call at line 66. ChronitonDB chronitondb-sandbox at `17e0b84a36` | The same files `Schema.java` and `SelectStatement.java` in Apache Cassandra cassandra-5.0 at `9e36adecef`. `SchemaProvider.validateTable`, `src/java/org/apache/cassandra/schema/SchemaProvider.java:95`, the same text at line 106, Apache Cassandra cassandra-6.0 at `d60653e71c` and trunk at `7d7d6b30db`. `ModificationStatement` and `TruncateStatement` were not read on Apache now, and `SelectStatement` was not read on cassandra-6.0 and trunk |
| C7 | The listings read every table of every registered virtual keyspace | `VirtualSchemaKeyspace.VirtualTables.data`, `src/java/org/apache/cassandra/db/virtual/VirtualSchemaKeyspace.java:83`, the read of the registry at line 87, and `DescribeStatement.executeLocally`, `src/java/org/apache/cassandra/cql3/statements/DescribeStatement.java:135`, with the virtual keyspaces added at line 142, ChronitonDB chronitondb-sandbox at `17e0b84a36` | The same file `VirtualSchemaKeyspace.java` in Apache Cassandra cassandra-5.0 at `9e36adecef`. `VirtualSchemaKeyspace.java:84`, the read at line 88, Apache Cassandra cassandra-6.0 at `d60653e71c` and trunk at `7d7d6b30db`. `DescribeStatement` was not read on Apache now |
| C8 | With no authorization required every client passes. Otherwise an ordinary role needs a grant on the table or its keyspace for a system keyspace, and a grant on all keyspaces does not count. `system_views` is a system keyspace. The tables of `system_virtual_schema` are readable by every logged in user | `ClientState.ensurePermission`, `src/java/org/apache/cassandra/service/ClientState.java:475`, the return for no authorization at line 477, the system keyspace rule at line 495, the static initialiser of `ClientState` at line 92, and `SchemaConstants.isSystemKeyspace`, `src/java/org/apache/cassandra/schema/SchemaConstants.java:144`, ChronitonDB chronitondb-sandbox at `17e0b84a36` | The same file `ClientState.java` in Apache Cassandra cassandra-5.0 at `9e36adecef`. `ClientState.java:510`, line 512, line 530 and line 99, Apache Cassandra cassandra-6.0 at `d60653e71c` and trunk at `7d7d6b30db`. `SchemaConstants` was not read on Apache now |
| C9 | `GRANT` and `REVOKE` fail with `Resource <resource> doesn't exist` when the table is not found by name | `PermissionsManagementStatement.validate`, `src/java/org/apache/cassandra/cql3/statements/PermissionsManagementStatement.java:45`, the error at line 58, and `DataResource.exists`, `src/java/org/apache/cassandra/auth/DataResource.java:245`, the table case at line 255, ChronitonDB chronitondb-sandbox at `17e0b84a36` | The same file `PermissionsManagementStatement.java` in Apache Cassandra cassandra-5.0 at `9e36adecef`. `PermissionsManagementStatement.java:48` and line 61, Apache Cassandra cassandra-6.0 at `d60653e71c` and trunk at `7d7d6b30db`. `DataResource` was not read on Apache now |
| C10 | A yaml key with no field in `Config` stops the start with `Invalid yaml. Please remove properties`. The settings table lists every field of `Config`, is read only, and the node logs every field once when it loads its configuration | `YamlConfigurationLoader.PropertiesChecker.check`, `src/java/org/apache/cassandra/config/YamlConfigurationLoader.java:417`, the error at line 423, `SettingsTable`, `src/java/org/apache/cassandra/db/virtual/SettingsTable.java:46`, with `SettingsTable.getProperties` at line 151, and `Config.log`, `src/java/org/apache/cassandra/config/Config.java:1347`. An in-JVM distributed test node loads its configuration through the same loader, with the check for unknown keys on: `Instance.loadConfig`, `test/distributed/org/apache/cassandra/distributed/impl/Instance.java:826`, the call of `YamlConfigurationLoader.fromMap` at line 832. ChronitonDB chronitondb-sandbox at `17e0b84a36` | The same files in Apache Cassandra cassandra-5.0 at `9e36adecef`. `YamlConfigurationLoader.java:554` with the error at line 560, Apache Cassandra cassandra-6.0 at `d60653e71c` and trunk at `7d7d6b30db`, with `SettingsTable.java:152` and `Config.java:1557` on cassandra-6.0, and `SettingsTable.java:153` and `Config.java:1561` on trunk |
| C11 | `nodetool info` prints the uptime on its `Uptime (seconds)` line. The uptime is `RuntimeMXBean.getUptime()` of the node's JVM, read over JMX and divided by 1000 as whole numbers. A nodetool command can reach any MBean of the node through the connection of its probe | `Info.execute`, `src/java/org/apache/cassandra/tools/nodetool/Info.java:48`, the uptime at line 65, `NodeProbe.getUptime`, `src/java/org/apache/cassandra/tools/NodeProbe.java:874`, with the proxy of the `RuntimeMXBean` made at line 331, and `NodeProbe.getMbeanServerConn` at line 772, ChronitonDB chronitondb-sandbox at `17e0b84a36` | The same files in Apache Cassandra cassandra-5.0 at `9e36adecef`. `Info.java:61` on cassandra-6.0 at `d60653e71c` and trunk at `7d7d6b30db`, with `NodeProbe.java:921` and line 814 on cassandra-6.0, and `NodeProbe.java:942` and line 835 on trunk |
| C12 | nodetool finds its commands in one list of command classes, which holds pairs such as `EnableBackup` and `DisableBackup`. It prints what a command throws in one of two forms. An `IllegalArgumentException` or an `IllegalStateException` gives the line `nodetool: ` with the message, a line that points to `nodetool help`, and exit status 1. Any other throwable gives the line `error: ` with the message of its root cause, the line `-- StackTrace --` with the stack trace, and exit status 2. A root cause of the kind `InstanceNotFoundException` gives the message `Server is not initialized yet, cannot run nodetool.` | `NodeTool.execute`, `src/java/org/apache/cassandra/tools/NodeTool.java:96`, the list from line 98, with `EnableBackup` at line 127, the two catches at lines 277 and 289, `NodeTool.badUse` at line 318 and `NodeTool.err` at line 324 with the message at line 328, ChronitonDB chronitondb-sandbox at `17e0b84a36` | The same file in Apache Cassandra cassandra-5.0 at `9e36adecef`. On cassandra-6.0 at `d60653e71c` and trunk at `7d7d6b30db` the list is gone: `NodeTool.execute`, `NodeTool.java:98`, builds its commands through `NodeTool.createCommandLine` at line 196 |
| C13 | A toggle of Apache Cassandra such as `enablebackup` writes the field of `Config` in the memory of the node and writes no file | `StorageService.setIncrementalBackupsEnabled`, `src/java/org/apache/cassandra/service/StorageService.java:2050`, and `DatabaseDescriptor.setIncrementalBackupsEnabled`, `src/java/org/apache/cassandra/config/DatabaseDescriptor.java:3787`, ChronitonDB chronitondb-sandbox at `17e0b84a36` | Not read on Apache now |
| C14 | At start the node prepares again each statement it stored. One that cannot be prepared again is logged in a warning with its text and removed from the store | `QueryProcessor.preloadPreparedStatements`, `src/java/org/apache/cassandra/cql3/QueryProcessor.java:165`, the warning at line 192 and the removal at line 193, ChronitonDB chronitondb-sandbox at `17e0b84a36` | The same file in Apache Cassandra cassandra-5.0 at `9e36adecef`. `QueryProcessor.java:202`, the warning at line 229 and the removal at line 230, Apache Cassandra cassandra-6.0 at `d60653e71c` and trunk at `7d7d6b30db` |
| C15 | A virtual table built on `AbstractVirtualTable` answers both kinds of read from its `data()` method. It refuses writes with `Modification is not supported by table` and truncation with `Truncation is not supported by table` | `AbstractVirtualTable.data`, `src/java/org/apache/cassandra/db/virtual/AbstractVirtualTable.java:66`, `AbstractVirtualTable.select` at lines 78 and 91, and the two refusals at lines 128 and 134, ChronitonDB chronitondb-sandbox at `17e0b84a36` | The same file in Apache Cassandra cassandra-5.0 at `9e36adecef`. `AbstractVirtualTable.java:68`, line 130 and line 136, Apache Cassandra cassandra-6.0 at `d60653e71c` and trunk at `7d7d6b30db`, where the two `select` methods at lines 80 and 93 also take a row filter and limits |
| C16 | A test of the in-JVM distributed test framework can rewrite a class inside a test node's class loader before the node starts. A test node registers no MBean unless its test starts it with the JMX feature of the framework | `ByteBuddyExamplesTest.writeFailureTest`, `test/distributed/org/apache/cassandra/distributed/test/ByteBuddyExamplesTest.java:51`, the initializer at line 54, and `MBeanWrapper.getMBeanWrapper`, `src/java/org/apache/cassandra/utils/MBeanWrapper.java:61`, the wrapper that registers nothing at line 73, ChronitonDB chronitondb-sandbox at `17e0b84a36` | Not read on Apache now |
| C17 | `MBeanWrapper` registers an MBean in one of three modes: throw the failure, log it in an ERROR line and go on, or ignore it. Given a name as text, it builds the JMX name in the same mode. The modes handle an `Exception`. In an in-JVM distributed test it registers nothing unless the test uses the JMX feature (C16). The metrics registry returns the counter that holds a name, or creates one, and registers its MBean in the logging mode unless JMX already holds the name. It removes a counter and unregisters the MBean under the counter's name in the mode that ignores a failure, whether or not it held the counter. The MBean of a counter implements only the registry's own interfaces | `MBeanWrapper.registerMBean`, `src/java/org/apache/cassandra/utils/MBeanWrapper.java:84`, the form that takes the name as text at line 90, `MBeanWrapper.create` at line 144, `MBeanWrapper.PlatformMBeanWrapper.registerMBean` at line 176 with its catch at line 182 and `MBeanWrapper.PlatformMBeanWrapper.unregisterMBean` at line 201, the three modes in `MBeanWrapper.OnException` at line 363 with the logging mode at line 366, `CassandraMetricsRegistry.counter`, `src/java/org/apache/cassandra/metrics/CassandraMetricsRegistry.java:55`, `CassandraMetricsRegistry.remove` at line 208 with the unregistration at line 212, `CassandraMetricsRegistry.registerMBean` at line 234 with the check and the registration at lines 262 and 263, and `CassandraMetricsRegistry.JmxCounter` at line 476 on `CassandraMetricsRegistry.AbstractBean` at line 302, ChronitonDB chronitondb-sandbox at `17e0b84a36` | Not read on Apache now |

What Apache now means for this feature. The next import of cassandra-5.0 changes none of the files above that were read there. A port to a line based on Apache Cassandra 6.0 finds three differences. The registry there removes the earlier keyspace's tables by id before it puts the new ones (C4), so registering `system_views` again would leave every table of it unfound for a moment, and the port designs its switch change on the `unregister` method or on a keyspace of its own. The lookup of a table by name moved to `SchemaProvider` (C6), so the line for the off error moves there. nodetool builds its commands in another way (C12), so the two commands are added in another place. `system_views.local` there shows the gossip generation and no uptime (C1), so the view is not made redundant by it.

**OpenSearch.** OpenSearch reports both values of a node's JVM in its node APIs. It reads the start time once, when the class that holds the JVM details loads: the static initialiser of `JvmInfo`, `server/src/main/java/org/opensearch/monitor/jvm/JvmInfo.java:83`, with the read of `RuntimeMXBean.getStartTime()` at line 199, OpenSearch main at `00d9641beb`. It reads the uptime at each request for the node statistics: `JvmStats.jvmStats`, `server/src/main/java/org/opensearch/monitor/jvm/JvmStats.java:79`, with the read of `RuntimeMXBean.getUptime()` at line 155, OpenSearch main at `00d9641beb`. Its node listing has an `uptime` column for every node from one request: `RestNodesAction.getTableWithHeader`, `server/src/main/java/org/opensearch/rest/action/cat/RestNodesAction.java:167`, the column at line 201, OpenSearch main at `00d9641beb`. The view takes the same two values from the JVM. It does not list every node from one request, because that needs a new value exchanged between nodes, and non-goal 1 leaves it out.

## Glossary

Not applicable: this section is required from Challenging size, and this feature is Normal size. Section 2.2 defines the terms this document uses: the view, the view state with on, off and between on and off, the running value, the final gate, a switch change, a read, every table listing and the off error.
