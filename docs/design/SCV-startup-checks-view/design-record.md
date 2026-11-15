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

# Design: #117 Let operators see which startup checks are enabled from CQL

| Field | Value |
|---|---|
| Title | Let operators see which startup checks are enabled from CQL |
| Document type | Specification and description at item level (ISO/IEC/IEEE 15289) |
| Status | Draft |
| Version | 1 |
| Author | Designer: chronitondb-agent |
| Approver | The maintainer who merges the pull request |
| References | Issue #117. Line `chronitondb-sandbox`, read at commit `bc2208e8fe`. Apache base commit `76550e931481e965ae3283d8cf4a59c320d74c55` (Apache `cassandra-5.0`). No feature spec and no plan: the one-item path. Process pages [branching-and-review.md](../../process/branching-and-review.md#feature-switches-and-defaults) and [quality-requirements.md](../../process/quality-requirements.md). Decision records 0001, 0004, 0005 and 0007 to 0009. |
| Risk | Normal: the issue's label `risk:normal`. The worst Bug Category is Degradation, a read of the view that fails or shows a wrong value. The floor applies because the change touches configuration, command line tools, JMX MBeans and virtual tables. The change edits no file of authentication or authorisation: the view takes the stock rule of its keyspace. For the maintainers, who confirm the class when they merge this record: if the hook at node start threw, the node would not start, an Availability fault that [classification.md](../../process/classification.md#risk) rates Critical. REQ-SCV-016 is written to exclude it. |
| Size | Low Hanging Fruit: four small fork classes, two nodetool commands and three one line edits to stock files, with no dependency on other work. |
| Reach | One area: the virtual tables of one node, in the new package `org.chronitondb.startup`, with hooks in `org.apache.cassandra.config`, `org.apache.cassandra.service` and `org.apache.cassandra.tools`. |
| Touches | public interface (configuration), public interface (command line tools and arguments), public interface (jmx mbeans, including metrics), public interface (virtual tables), new input or privilege, new feature or switch |

Change history: the git history of this file.

Location: `docs/design/SCV-startup-checks-view/`, the directory of the fork feature with the key `SCV`, which this record proposes and the merge of its pull request reserves ([additive.md, Feature keys and requirement ids](../../process/additive.md#feature-keys-and-requirement-ids), item 2), with the coverage file `ac-coverage.md` next to it. Every section is filled, or carries a waiver with its reason.

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in BCP 14 (RFC 2119, RFC 8174) when, and only when, they appear in all capitals, as shown here.

The Risk, Size and Reach rows are the item's class, as [classification.md](../../process/classification.md) defines it, and match the issue's `risk:normal`, `size:low-hanging-fruit` and `reach:one-area` labels. The issue also carries `kind:additive`, so the item is a fork feature small enough for one item and takes the one-item path of [maintenance.md](../../process/maintenance.md#the-one-item-path) with a feature key: this directory, the ids `REQ-SCV-nnn`, and the feature class stated in [section 3](#3-stock-behaviour-preservation).

## Contents

- [1. Problem, acceptance criteria and requirements](#1-problem-acceptance-criteria-and-requirements)
  - [Requirements](#requirements)
- [2. Decisions implemented](#2-decisions-implemented)
- [3. Stock behaviour preservation](#3-stock-behaviour-preservation)
  - [Stock hook points](#stock-hook-points)
- [4. Prior art reviewed](#4-prior-art-reviewed)
- [5. Idiom and consistency](#5-idiom-and-consistency)
- [6. Quality requirements](#6-quality-requirements)
- [7. Performance](#7-performance)
  - [Hot path statement](#hot-path-statement)
  - [Expected cost](#expected-cost)
  - [Isolation levers](#isolation-levers)
  - [Benchmarks that prove it](#benchmarks-that-prove-it)
  - [Regression threshold and gate](#regression-threshold-and-gate)
  - [Stock guard](#stock-guard)
  - [What was not measured](#what-was-not-measured)
- [8. Observability](#8-observability)
- [9. Compatibility](#9-compatibility)
- [10. Threat model and security](#10-threat-model-and-security)
- [11. Dependencies](#11-dependencies)
- [12. Compliance impact](#12-compliance-impact)
- [13. Documentation](#13-documentation)
- [14. Testing](#14-testing)
  - [Tests for this change](#tests-for-this-change)
  - [Existing suites at risk](#existing-suites-at-risk)
  - [Stock suites run unchanged](#stock-suites-run-unchanged)
  - [Tracing test](#tracing-test)
  - [Formats and configurations](#formats-and-configurations)
- [15. Not covered and follow-ups](#15-not-covered-and-follow-ups)
- [New terms](#new-terms)
- [Where problems could occur](#where-problems-could-occur)
  - [Test plan](#test-plan)
- [Planned file list](#planned-file-list)
  - [Shared with open items](#shared-with-open-items)
  - [Waivers](#waivers)
- [Requirement quality checklist (ISO/IEC/IEEE 29148)](#requirement-quality-checklist-isoiecieee-29148)

## 1. Problem, acceptance criteria and requirements

An operator cannot see from CQL which startup checks a node has on. A node of this line runs 19 startup checks. Four of them can be switched in `cassandra.yaml`, under `startup_checks`: `check_dc`, `check_rack`, `check_filesystem_ownership` and `check_data_resurrection` (`StartupChecks.StartupCheckType`, `src/java/org/apache/cassandra/service/StartupChecks.java:106` to `125` at `bc2208e8fe`). The other 15 always run.

The stock table `system_views.settings` does not answer the question. Its row `startup_checks` shows the map of `Config.startup_checks` (`SettingsTable.getValue`, `src/java/org/apache/cassandra/db/virtual/SettingsTable.java:97` at `bc2208e8fe`), which holds only the checks that `cassandra.yaml` names (`Config.startup_checks`, `src/java/org/apache/cassandra/config/Config.java:960` at `bc2208e8fe`). A check left at its default is not in the map, so the operator has to know each default. Two defaults are on and two are off. Three start options can also override the yaml value: `cassandra.ignore_dc`, `cassandra.ignore_rack` and `cassandra.enable_fs_ownership_check` (section 4, stock item 4). And the 15 checks that always run have no name at all on this line.

Users: operators who run and compare nodes, and the tools they query nodes with over CQL.

Acceptance criteria, as the maintainers confirmed them for this item:

1. With the view switched off, which is the default, the node behaves as stock: no new table and no change to what `DESCRIBE` shows.
2. The view is switched on in `cassandra.yaml`, and it has a nodetool toggle as every fork feature does.
3. With the view on, a `SELECT` returns one row for each check the node runs at start, 19 on this line today.
4. Each row shows the check's name, whether the check is on or off, and where that value came from.
5. The source is one of: the default, `cassandra.yaml`, a start option, or always on.
6. The 15 checks an operator cannot switch show on, with the source always on.
7. A start option that overrides the yaml shows its own value, with the source start option.
8. No row shows any other setting of a check, so the ownership token of `check_filesystem_ownership` never appears.
9. Which checks run at start, and what they log, stay as stock.
10. The feature meets the quality checklist of [quality-requirements.md](../../process/quality-requirements.md): logged, measured and documented.

Nothing was placed out of scope.

What this record builds, in short. One virtual table, `system_views.startup_checks` (decision record 0007), with three columns:

```
CREATE TABLE system_views.startup_checks (
    name text PRIMARY KEY,
    enabled boolean,
    source text
)
```

The table exists only while the switch is on. The switch is the setting `startup_checks_view_enabled` in `cassandra.yaml`, default `false`, with the nodetool commands `enablestartupchecksview` and `disablestartupchecksview`, which change the running value only.

An example. A node with the view on, no `startup_checks` block in `cassandra.yaml`, started with `-Dcassandra.ignore_rack=true`. The 15 always-run rows have the names of decision record 0008.

```
SELECT * FROM system_views.startup_checks;

 name                          | enabled | source
-------------------------------+---------+-----------------
 check_data_resurrection       |   False | default
 check_dc                      |    True | default
 check_filesystem_ownership    |   False | default
 check_rack                    |   False | system_property
 data_dirs                     |    True | always_on
 jemalloc                      |    True | always_on
 jmx_ports                     |    True | always_on
 jmx_properties                |    True | always_on
 jvm_options                   |    True | always_on
 kernel_bug_1057843            |    True | always_on
 legacy_auth_tables            |    True | always_on
 lz4_native                    |    True | always_on
 max_map_count                 |    True | always_on
 native_library_initialization |    True | always_on
 process_environment           |    True | always_on
 read_ahead_kb_setting         |    True | always_on
 sstables_format               |    True | always_on
 system_keyspace_state         |    True | always_on
 valid_launch_date             |    True | always_on
```

The same node with the view off: the table does not exist, as on stock.

How a row is worked out. Every section and every requirement below means these rules.

1. The always-run rows are a fixed list of 15 names, one for each of the 15 checks of `StartupChecks.DEFAULT_TESTS` whose type is `non_configurable_check` ([New terms](#new-terms), item 4). The list is a map in `StartupCheckRows` from the check object, read from its public static field of `StartupChecks`, to the row name that decision record 0008 gives it. Each row shows `enabled` as `true` and `source` as `always_on`.
2. The switchable rows are one for each constant of `StartupChecks.StartupCheckType` other than `non_configurable_check`, named by the constant. So a constant that a later change adds, such as the `check_commitlog_shared_disk` of the commit log disk check, gets its row with no change to this feature.
3. For a switchable row, the view first looks for the check's start option: `cassandra.ignore_dc` for `check_dc`, `cassandra.ignore_rack` for `check_rack`, `cassandra.enable_fs_ownership_check` for `check_filesystem_ownership`, none for any other constant. When the start option is set, `source` is `system_property`, and `enabled` is the value the start option gives ([New terms](#new-terms), item 6): the opposite of the option's value for the two `ignore` options, and the option's value for the third.
4. Otherwise, when `cassandra.yaml` has an entry for the check under `startup_checks`, `source` is `yaml` and `enabled` is what `StartupChecksOptions.isEnabled` returns for the check. This holds with or without the key `enabled` in the yaml entry (decision record 0009).
5. Otherwise `source` is `default` and `enabled` is what `StartupChecksOptions.isEnabled` returns for the check, which is then the default of its constant.

The view reads the options from `DatabaseDescriptor.getStartupChecksOptions` (`src/java/org/apache/cassandra/config/DatabaseDescriptor.java:1143` at `bc2208e8fe`), the object the stock checks were run with, and works the rows out again at each read.

The words this record uses with one fixed meaning are in [New terms](#new-terms): the switch, the view, a read, an always-run check, a switchable check, a check of the node, a start option, the value a start option gives, a yaml entry and a failed switch.

### Requirements

In the sources below, "criterion n" is item n of the acceptance criteria above, and "problem n" is item n of [Where problems could occur](#where-problems-could-occur).

REQ-SCV-001 (event driven): When a node whose `cassandra.yaml` does not set `startup_checks_view_enabled` starts, the switch MUST be off. Source: stakeholder need, criterion 1.

REQ-SCV-002 (state driven): While the switch is off, the node MUST NOT list the view in `system_virtual_schema.tables`. Source: stakeholder need, criterion 1.

REQ-SCV-003 (state driven): While the switch is on, the node MUST list the view in `system_virtual_schema.tables`. Source: stakeholder need, criterion 2.

REQ-SCV-004 (event driven): When a node whose `cassandra.yaml` sets `startup_checks_view_enabled` to `true` starts, the switch MUST be on. Source: stakeholder need, criterion 2.

REQ-SCV-005 (event driven): When `nodetool enablestartupchecksview` runs against a node, the node MUST set the switch on. Source: stakeholder need, criterion 2.

REQ-SCV-006 (event driven): When `nodetool disablestartupchecksview` runs against a node, the node MUST set the switch off. Source: stakeholder need, criterion 2.

REQ-SCV-007 (event driven): When a nodetool command changes the value of the switch, the node MUST log the changed line. Source: [quality-requirements.md](../../process/quality-requirements.md#observability) item 3.

REQ-SCV-008 (state driven): While the switch is on, the set of names that a `SELECT` of every row of the view returns MUST equal the set of names of the checks of the node. Source: stakeholder need, criterion 3.

REQ-SCV-009 (ubiquitous): The columns of the view MUST be exactly `name`, `enabled` and `source`. Source: stakeholder need, criteria 4 and 8.

REQ-SCV-010 (ubiquitous): The row of an always-run check MUST show `source` as `always_on`. Source: stakeholder need, criterion 6.

REQ-SCV-011 (ubiquitous): The row of a switchable check whose start option is not set and that has no yaml entry MUST show `source` as `default`. Source: stakeholder need, criterion 5.

REQ-SCV-012 (ubiquitous): The row of a switchable check whose start option is not set and that has a yaml entry MUST show `source` as `yaml`. Source: stakeholder need, criterion 5, and decision record 0009.

REQ-SCV-013 (ubiquitous): The row of a switchable check whose start option is set MUST show `source` as `system_property`. Source: stakeholder need, criterion 7.

REQ-SCV-014 (unwanted behaviour): If the view is read while the switch is off, then the node MUST refuse the read with an invalid request error whose message is the refusal text. Source: problem 3 and [branching-and-review.md](../../process/branching-and-review.md#feature-switches-and-defaults) item 7.

REQ-SCV-015 (unwanted behaviour): If a role without the `SELECT` permission on the view reads it on a node with authorisation on, then the node MUST refuse the read as unauthorised. Source: problem 4 and decision record 0007.

REQ-SCV-016 (unwanted behaviour): If the hook at node start is a failed switch, then the hook MUST return normally. Source: problem 1.

REQ-SCV-017 (unwanted behaviour): If a failed switch happens, then the node MUST log the failed warning. Source: problem 1.

REQ-SCV-018 (ubiquitous): The fixed list of always-run names MUST hold a name for every check of type `non_configurable_check` that the daemon registers. Source: stakeholder need, criterion 3, problem 5 and decision record 0008.

REQ-SCV-019 (event driven): When the view serves a read, the node MUST raise the counter `org.chronitondb.metrics:type=StartupChecksView,name=Reads` by one. Source: [quality-requirements.md](../../process/quality-requirements.md#observability) item 1.

REQ-SCV-020 (event driven): When the view refuses a read because the switch is off, the node MUST raise the counter `org.chronitondb.metrics:type=StartupChecksView,name=RefusedReads` by one. Source: [quality-requirements.md](../../process/quality-requirements.md#observability) item 1.

REQ-SCV-021 (event driven): When the node logs the failed warning while the counter `org.chronitondb.metrics:type=StartupChecksView,name=FailedSwitches` exists, the node MUST raise that counter by one. Source: [quality-requirements.md](../../process/quality-requirements.md#observability) item 1.

REQ-SCV-022 (unwanted behaviour): If `nodetool enablestartupchecksview` or `nodetool disablestartupchecksview` runs against a node without the MBean `org.chronitondb:type=StartupChecksView`, then the command MUST print the missing MBean line. Source: problem 6.

REQ-SCV-023 (ubiquitous): The reference page `docs/reference/startup-checks-view.md` MUST contain each of these exact texts: `startup_checks_view_enabled`, `enablestartupchecksview`, `disablestartupchecksview`, `system_views.startup_checks`, each of the 15 always-run names, the four values of `source`, the three counter names and the refusal text. Source: stakeholder need, criterion 10, and problem 7.

REQ-SCV-024 (ubiquitous): The file `NEWS-chronitondb.txt` MUST contain the rollback sentence. Source: problem 2.

REQ-SCV-025 (ubiquitous): The row of an always-run check MUST show `enabled` as `true`. Source: stakeholder need, criterion 6.

REQ-SCV-026 (ubiquitous): The row of a switchable check whose start option is set MUST show `enabled` as the value the start option gives. Source: stakeholder need, criterion 7.

REQ-SCV-027 (ubiquitous): The row of a switchable check whose start option is not set MUST show `enabled` as the value `StartupChecksOptions.isEnabled` returns for the check. Source: stakeholder need, criterion 4.

REQ-SCV-028 (unwanted behaviour): If `nodetool enablestartupchecksview` or `nodetool disablestartupchecksview` runs against a node without the MBean `org.chronitondb:type=StartupChecksView`, then the command MUST exit with a status other than 0. Source: problem 6.

REQ-SCV-029 (unwanted behaviour): If the MBean operation of `nodetool enablestartupchecksview` or `nodetool disablestartupchecksview` is a failed switch, then the command MUST exit with a status other than 0. Source: problem 10.

REQ-SCV-030 (unwanted behaviour): If the hook at node start or the MBean operation of `nodetool enablestartupchecksview` is a failed switch, then the switch MUST be off afterwards. Source: problem 10.

## 2. Decisions implemented

1. Decision record 0001, The first maintainers, 2026-11-01: the maintainers who approve this record. Nothing in it binds the design.
2. Decision record 0004, The commit log disk check is off by default, 2026-11-15: the one earlier decision on a default of a fork feature near startup checks. This feature is off by default too (REQ-SCV-001).
3. Decision record 0005, The commit log disk check is switched under `startup_checks`, 2026-11-15: that feature adds the constant `check_commitlog_shared_disk`. Rule 2 of section 1 gives the constant its row once its code is on the line. That record set aside the nodetool toggle for a startup check, which has run before nodetool can reach the node. The reason does not hold here: the view can be switched while the node runs, so this feature has its toggle.
4. Decision record 0007, The startup checks view lives in system_views, 2026-11-15, added in this pull request with the status Accepted, which the maintainer's merge of this pull request makes true. The view is the table `system_views.startup_checks`, and a role reads it under the stock access rule of that keyspace. No file of authentication or authorisation is edited. Section 3, REQ-SCV-015 and section 10 implement it.
5. Decision record 0008, The startup checks that always run take the names of Apache Cassandra 6.0, 2026-11-15, added in this pull request the same way. The 15 always-run rows have the names of its table, and the row of the Sigar check is `process_environment`. Rule 1 of section 1, REQ-SCV-018 and New terms implement it.
6. Decision record 0009, A startup check named in cassandra.yaml shows the source yaml, 2026-11-15, added in this pull request the same way. A switchable check with a yaml entry shows `yaml`, with or without the key `enabled`, and the feature adds no code to the loading of the configuration. Rule 4 of section 1, REQ-SCV-012 and the known limitations of section 13 implement it.
7. The process pages, read on the line at commit `bc2208e8fe`: [branching-and-review.md, Feature switches and defaults](../../process/branching-and-review.md#feature-switches-and-defaults) items 1, 3 and 7, [quality-requirements.md](../../process/quality-requirements.md), [maintenance.md, The one-item path](../../process/maintenance.md#the-one-item-path), [conventions.md, Names](../../process/conventions.md#names) and [conventions.md, Code layout](../../process/conventions.md#code-layout).

As of 2026-11-15 the register on the line holds records 0001 to 0006. Records 0002 and 0003 are about `nodetool version`, and record 0006 is about how the commit log disk check compares directories. Records 0007 to 0009 are added by this pull request. No newer record exists on startup checks, virtual tables or configuration.

## 3. Stock behaviour preservation

This statement and the switch table below it follow the form of [section 2.8 of the feature spec template](../../process/templates/feature-spec.md#28-feature-class-and-switches), because a fork feature that fits one item has no feature spec.

Feature class: purely additive, because the view is reachable only through a table name and a setting that stock Apache Cassandra rejects, and no stock operation changes its result, its error, its warning or its cost (branching-and-review.md, Feature switches and defaults, item 3). A purely additive feature MAY be on by default. This one is off by default, as the maintainers confirmed in criterion 1.

| Switch | Class | Reason | Default per line | Stock operations it changes |
|---|---|---|---|---|
| `startup_checks_view_enabled` in `cassandra.yaml`, with `nodetool enablestartupchecksview` and `nodetool disablestartupchecksview` | purely additive | with the switch on, the node has one more virtual table, which stock does not have | `chronitondb-sandbox`: off | none. While on, the lists of tables that `system_virtual_schema.tables` and `DESCRIBE` show hold one more table |

Item 2 of the same list says a switch refuses to turn on before the feature's final milestone gate. A feature that fits one item has no milestone. As for the commit log disk check, the one code pull request of this item holds the whole feature, so no build of the line holds the switch before the feature is whole, and the switch needs no code that refuses it.

Item 7 of the same list also says that with a feature off its syntax is refused with an error that names the switch. The only syntax of this feature is the name of the view. Acceptance criterion 1 says the table does not exist with the switch off, so a statement that names it gets the error Apache Cassandra gives for any table that does not exist, and no stock file is edited to change that error. The one read that can reach the view while the switch is off gets the refusal text, which names the switch (REQ-SCV-014).

Row 1 of the table below applies only with the switch on. Rows 2 to 4 are presences on every node, switch on or off: a departure from [branching-and-review.md](../../process/branching-and-review.md#feature-switches-and-defaults) item 7, which says that with a feature off no new memory is used and stock operations behave as Apache's do. The maintainers approve each by merging this record.

| Stock behaviour today (file and line) | This change | Switch that controls it | Error text naming the switch |
|---|---|---|---|
| `system_views` holds the tables that the constructor of `SystemViewsKeyspace` lists (`src/java/org/apache/cassandra/db/virtual/SystemViewsKeyspace.java:32` to `58` at `bc2208e8fe`), and `system_virtual_schema.tables` and `DESCRIBE` show the tables of every registered virtual keyspace (`VirtualSchemaKeyspace.VirtualTables.data`, `src/java/org/apache/cassandra/db/virtual/VirtualSchemaKeyspace.java:87` at `bc2208e8fe`, and `DescribeStatement.execute`, `src/java/org/apache/cassandra/cql3/statements/DescribeStatement.java:142` at `bc2208e8fe`) | with the switch on, `system_views` holds one more table, `startup_checks`, and both lists show it. With the switch off both lists are stock's | `startup_checks_view_enabled`, in memory through `nodetool enablestartupchecksview` and `nodetool disablestartupchecksview` | the refusal text of [New terms](#new-terms), item 12, for a read that reaches the view while the switch is off (REQ-SCV-014). A statement that names the table while it is not registered gets stock's own error for a table that does not exist |
| `system_views.settings` lists one row per `Config` field (`SettingsTable.getValue`, `SettingsTable.java:97` at `bc2208e8fe`), and the start log line `Node configuration:` prints every field (`Config.log`, `Config.java:1376` at `bc2208e8fe`) | both show one more entry, `startup_checks_view_enabled`, on every node | none: Apache's loader refuses a key without a `Config` field (`YamlConfigurationLoader.PropertiesChecker.check`, `src/java/org/apache/cassandra/config/YamlConfigurationLoader.java:423` at `bc2208e8fe`), so the yaml setting needs the field | none |
| `nodetool help` lists the commands of `NodeTool.execute` (`src/java/org/apache/cassandra/tools/NodeTool.java:98` to `246` at `bc2208e8fe`) | the list has two more entries, `enablestartupchecksview` and `disablestartupchecksview`, on every node | none: the toggle that branching-and-review.md item 1 requires is a command, and a command is listed | none |
| the JMX server holds Apache's MBeans and metrics only | one more MBean, `org.chronitondb:type=StartupChecksView`, and three more counters of the fork's own type `StartupChecksView` in the group `org.chronitondb.metrics`, exist on every node from the hook at node start. Together one object and three counters, a few hundred bytes, allocated once. No stock metric changes | none: the MBean is the handle of the toggle, and holding it is how the view can be switched on while the node runs. The counters exist from registration, so that the metrics a node exports do not depend on which commands ran against it | none |

Everything else stays stock. `StartupChecks.java` is not edited, so which checks run, their order and what they log stay as they are (criterion 9). No code default in a stock class changes: the one field `Config` gains is new. No stock file under `conf/` changes. No file of authentication or authorisation changes. No test that exists on the line changes.

### Stock hook points

There is no feature spec for a one-item change, so the hook points are listed here with their delta entry, `docs/delta/startup-checks-view.md`.

1. `src/java/org/apache/cassandra/config/Config.java`: one field, `public volatile boolean startup_checks_view_enabled = false;`, after `startup_checks` at line 960. It is a field, not a hook that imports fork code, but it is a stock edit and so it is listed.
2. `src/java/org/apache/cassandra/service/CassandraDaemon.java`: one import and one line at the end of `CassandraDaemon.setupVirtualKeyspaces` (`CassandraDaemon.java:534` to `544` at `bc2208e8fe`), `StartupChecksView.instance.start();`. The call creates the counters, registers the MBean, and switches the view on when the `Config` field is `true`. It returns normally whatever `Exception` is thrown in it (REQ-SCV-016). The in-JVM distributed test framework calls the same method for each instance (`Instance.startup`, `test/distributed/org/apache/cassandra/distributed/impl/Instance.java:650` at `bc2208e8fe`), so its instances run the hook too.
3. `src/java/org/apache/cassandra/tools/NodeTool.java`: two imports and two entries in the command list (lines 98 to 246), `EnableStartupChecksView.class` and `DisableStartupChecksView.class`.

How the view is registered, by decision record 0007. `VirtualKeyspaceRegistry.register` puts a keyspace into the registry and replaces one of the same name (`VirtualKeyspaceRegistry.register`, `src/java/org/apache/cassandra/db/virtual/VirtualKeyspaceRegistry.java:41` to `48` at `bc2208e8fe`). To register the view, the feature registers a `VirtualKeyspace` named `system_views` that holds the tables of `SystemViewsKeyspace.instance`, the same objects, and the view. To remove it, the feature registers `SystemViewsKeyspace.instance` again. No stock file is edited for it. The stock tables stay in the registry's map of tables by id through both calls, because the call puts each of them again under its own id and removes none (section 15 item 4), so a read of a stock table of `system_views` finds its table at every moment of a switch. The view is one table object, created at the first registration and kept for the life of the node. The registry on this line has no call that removes a table, so after a switch off the view stays reachable by its table id for a statement prepared earlier. REQ-SCV-014 covers that read.

How the switch is applied. `StartupChecksView.instance` is one object. Its constructor creates no counter and no table, so that loading the class cannot fail. Its methods `start`, `enable` and `disable` are `synchronized`, and each does all of its work inside one `try` that catches `Exception`. A run of one of them in which an `Exception` is thrown is a failed switch.

1. `start` is the hook. It creates the three counters through `CassandraMetricsRegistry.Metrics.counter` (`CassandraMetricsRegistry.counter`, `src/java/org/apache/cassandra/metrics/CassandraMetricsRegistry.java:55` to `61` at `bc2208e8fe`), registers the MBean through `MBeanWrapper.instance.registerMBean` with `OnException.LOG` (`MBeanWrapper.registerMBean`, `src/java/org/apache/cassandra/utils/MBeanWrapper.java:90` at `bc2208e8fe`), as stock services do, and then, when the `Config` field is `true`, registers the view. On a failed switch it sets the `Config` field to `false`, logs the failed warning, raises `FailedSwitches` when that counter exists, and returns.
2. `enable` is the MBean operation behind `nodetool enablestartupchecksview`. With the switch off it registers the view, sets the `Config` field to `true` and logs the changed line. With the switch on it does nothing. On a failed switch it leaves the `Config` field at `false`, logs the failed warning, raises `FailedSwitches` when that counter exists, and throws the exception on to the caller.
3. `disable` is the MBean operation behind `nodetool disablestartupchecksview`. With the switch on it removes the view, sets the `Config` field to `false` and logs the changed line. With the switch off it does nothing. On a failed switch it leaves the `Config` field as it was, logs the failed warning, raises `FailedSwitches` when that counter exists, and throws the exception on to the caller.

A nodetool command whose MBean operation throws ends as any stock nodetool command does then: it prints the error and exits with the status 1 or 2 (`NodeTool.execute`, `src/java/org/apache/cassandra/tools/NodeTool.java:277` to `293` at `bc2208e8fe`). No cause of a failed registration is known on this line. An import of Apache Cassandra that adds a table named `startup_checks` to `SystemViewsKeyspace` would clash with the view. `StartupChecksViewTest.notListedWhileOff` fails on such an import, because the table is then listed with the switch off.

The new package `org.chronitondb.startup` imports from `org.apache.cassandra.config`, `org.apache.cassandra.service`, `org.apache.cassandra.db.virtual`, `org.apache.cassandra.metrics`, `org.apache.cassandra.schema`, `org.apache.cassandra.utils` and `org.apache.cassandra.exceptions`, all through public members. It needs no package private access to a stock package.

## 4. Prior art reviewed

Stock Apache Cassandra, read on this line at commit `bc2208e8fe`:

1. The daemon registers 19 checks: the 18 of `StartupChecks.DEFAULT_TESTS` (`StartupChecks.java:135` to `152` at `bc2208e8fe`) and `FileSystemOwnershipCheck` (`CassandraDaemon.CassandraDaemon`, `src/java/org/apache/cassandra/service/CassandraDaemon.java:220` at `bc2208e8fe`). A check says which constant of `StartupChecks.StartupCheckType` it is with `StartupCheck.getStartupCheckType`, whose default is `non_configurable_check` (`StartupCheck.getStartupCheckType`, `src/java/org/apache/cassandra/service/StartupCheck.java:54` to `57` at `bc2208e8fe`). Four checks override it. The other 15 are public static fields of `StartupChecks` with no name but the field's.
2. `StartupChecksOptions.apply` gives every constant an `enabled` value: `false` for a constant declared disabled by default, `true` for the others, and always `true` for `non_configurable_check` (`StartupChecksOptions.apply`, `src/java/org/apache/cassandra/config/StartupChecksOptions.java:81` to `96` at `bc2208e8fe`). `StartupChecksOptions.isEnabled` reads it (`StartupChecksOptions.java:66` to `69` at `bc2208e8fe`).
3. Every always-run check starts with `options.isDisabled(getStartupCheckType())`, which is never true for it. Two of them also return at once on a platform other than Linux (`StartupChecks.checkReadAheadKbSetting`, `StartupChecks.java:471` at `bc2208e8fe`, and `StartupChecks.checkMaxMapCount`, `StartupChecks.java:546` at `bc2208e8fe`), and `StartupChecks.checkKernelBug1057843` lets the start option `cassandra.ignore_kernel_bug_1057843_check` skip its test of the kernel version (`StartupChecks.java:211` to `215` at `bc2208e8fe`). The view shows whether a check is on, not what it found or skipped, so these rows stay `true` and `always_on`. The reference page says so.
4. Three start options override the yaml value of a switchable check. `StartupChecks.checkDatacenter` takes the opposite of `cassandra.ignore_dc` when the option is set (`StartupChecks.java:741` to `748` at `bc2208e8fe`). `StartupChecks.checkRack` does the same with `cassandra.ignore_rack` (`StartupChecks.java:778` to `785` at `bc2208e8fe`). `FileSystemOwnershipCheck.isEnabled` takes `cassandra.enable_fs_ownership_check` when it is set and the yaml value otherwise (`FileSystemOwnershipCheck.isEnabled`, `src/java/org/apache/cassandra/service/FileSystemOwnershipCheck.java:276` to `280` at `bc2208e8fe`). The keys are the constants `CassandraRelevantProperties.FILE_SYSTEM_CHECK_ENABLE`, `CassandraRelevantProperties.IGNORE_DC` and `CassandraRelevantProperties.IGNORE_RACK` (`src/java/org/apache/cassandra/config/CassandraRelevantProperties.java:233`, `275` and `284` at `bc2208e8fe`). A start option is present when the system properties hold its key (`CassandraRelevantProperties.isPresent`, `CassandraRelevantProperties.java:1030` to `1033` at `bc2208e8fe`), and its boolean value is read by `CassandraRelevantProperties.getBoolean` (`CassandraRelevantProperties.java:753` to `758` at `bc2208e8fe`). `check_data_resurrection` has no such option (`DataResurrectionCheck.execute`, `src/java/org/apache/cassandra/service/DataResurrectionCheck.java:169` at `bc2208e8fe`).
5. Stock builds the options once, while it loads the configuration: `DatabaseDescriptor.applyAll` calls `DatabaseDescriptor.applyStartupChecks` (`src/java/org/apache/cassandra/config/DatabaseDescriptor.java:475` and `1148` to `1151` at `bc2208e8fe`). The constructor of `StartupChecksOptions` copies the outer map of `Config.startup_checks` and keeps its inner maps, and `apply` then writes `enabled` into each inner map that lacks it (`StartupChecksOptions.java:43` to `47` and `81` to `96` at `bc2208e8fe`). So after the configuration is loaded, the entry of a check that the yaml named without `enabled` holds the key too. This was read and not run. Decision record 0009 rests on it.
6. A virtual table is a class with a `TableMetadata` and a `data` method, as `SystemPropertiesTable` is (`src/java/org/apache/cassandra/db/virtual/SystemPropertiesTable.java:36` to `61` at `bc2208e8fe`). A read finds the table in the registry by its table id (`PartitionRangeReadCommand.VirtualTablePartitionRangeReadCommand.executeLocally`, `src/java/org/apache/cassandra/db/PartitionRangeReadCommand.java:555`, and `SinglePartitionReadCommand.VirtualTableSinglePartitionReadCommand.executeLocally`, `src/java/org/apache/cassandra/db/SinglePartitionReadCommand.java:1415`, both at `bc2208e8fe`). Each read command that reaches a virtual table calls the table once. A table name is resolved through the keyspace metadata, which for a virtual keyspace comes from the registry (`Schema.getKeyspaceMetadata`, `src/java/org/apache/cassandra/schema/Schema.java:318` to `324` at `bc2208e8fe`).
7. Who may read. `system_views` is a system keyspace (`SchemaConstants.VIRTUAL_SYSTEM_KEYSPACE_NAMES`, `src/java/org/apache/cassandra/schema/SchemaConstants.java:63` to `64` at `bc2208e8fe`). For an ordinary role, a permission on a system keyspace must be granted on that keyspace or its table, and a grant on all keyspaces does not count (`ClientState.ensurePermission`, `src/java/org/apache/cassandra/service/ClientState.java:485` to `499` at `bc2208e8fe`). The tables of `system_virtual_schema` are readable with no grant, because `ClientState.READABLE_SYSTEM_RESOURCES` names them (`ClientState.java:72` to `93` and `463` at `bc2208e8fe`). With authorisation off, every role reads every table.
8. `system_views.system_properties` already shows the start options a node was started with, and `system_views.settings` the yaml block. An operator can combine the two today, and must still know each default, each override rule and which checks exist. The view does that work.
9. A stock toggle has commands named `enable` and `disable` with the thing, such as `enablebackup` and `disablebackup` (`NodeTool.execute`, `NodeTool.java:116` and `127` at `bc2208e8fe`), and a fork command reaches its MBean through `NodeProbe.getMbeanServerConn` (`src/java/org/apache/cassandra/tools/NodeProbe.java:772` at `bc2208e8fe`).

Apache `cassandra-6.0` and trunk, read from `apache/cassandra` at commit `84bca651ef` (`cassandra-6.0`) and `2249e37b51` (trunk):

1. CASSANDRA-21093, "Custom startup checks plugin", fixed in 6.0, gave every check a name. `StartupCheck.name` returns "the name of a startup check, as it would appear in the configuration" (`StartupCheck.java:44` at `2249e37b51`). The always-run checks this line shares with 6.0 are named `kernel_bug_1057843`, `jemalloc`, `lz4_native`, `valid_launch_date`, `jmx_ports`, `jmx_properties`, `jvm_options`, `native_library_initialization`, `read_ahead_kb_setting`, `max_map_count`, `data_dirs`, `sstables_format`, `system_keyspace_state` and `legacy_auth_tables` (`StartupChecks.checkKernelBug1057843` to `StartupChecks.checkLegacyAuthTables`, `StartupChecks.java:237` to `934` at `84bca651ef`). The switchable checks keep their yaml names, such as `check_filesystem_ownership` (`FileSystemOwnershipCheck.name`, `FileSystemOwnershipCheck.java:115` to `118` at `2249e37b51`).
2. The fifteenth always-run check of this line, `StartupChecks.initSigarLibrary`, warns when the node runs in a degraded mode (`StartupChecks.java:422` to `431` at `bc2208e8fe`). 6.0 has no Sigar library. Its check for the same warning is `StartupChecks.checkProcessEnvironment`, named `process_environment` (`StartupChecks.java:513` to `531` at `84bca651ef`).
3. 6.0 can also list the registered checks, `StartupChecks.getChecks` (`StartupChecks.java:143` to `146` at `2249e37b51`), and remove a virtual keyspace, `VirtualKeyspaceRegistry.unregister` (`VirtualKeyspaceRegistry.java:51` to `59` at `2249e37b51`). This line has neither.
4. Neither branch has a virtual table of startup checks: no table that the constructor of `SystemViewsKeyspace` lists is about them (`SystemViewsKeyspace.SystemViewsKeyspace`, `src/java/org/apache/cassandra/db/virtual/SystemViewsKeyspace.java:33` to `77` at `2249e37b51`).

Apache JIRA, read with their comments on 2026-11-15:

1. CASSANDRA-21093: the comments settle why the names are strings on 6.0. The enum of this line validates the names of `cassandra.yaml` for free, and a custom check needs a name the enum cannot hold.
2. CASSANDRA-17736, "Settings Virtual Table should display the values assigned to a property in the DatabaseDescriptor on startup and not null (as per the yaml)", open. It records the same gap for other settings: the settings table shows what the yaml holds, not what the node acts on. Its comments set the rule this design follows for the switch: a JMX setter updates the `Config` field, so the settings table shows the running value.
3. A search for a virtual table of startup checks, `project = CASSANDRA AND text ~ "startup checks virtual table"`, returned 17 tickets and none that asks for one.

Other systems, by behaviour: OpenSearch runs a fixed list of bootstrap checks at node start, `BootstrapChecks.checks` (`server/src/main/java/org/opensearch/bootstrap/BootstrapChecks.java:213` to `243` at `83addf7027`, in `opensearch-project/OpenSearch`, Apache License 2.0). No API that lists them was found, which was not verified further. So OpenSearch has no equivalent to compare a name or a default with.

No patents were searched or read.

These rules apply to every source:

1. Describe and cite behaviour, published designs, papers, public documentation and code under licences compatible with the Apache License 2.0.
2. Code or text under an incompatible licence, for example the Elastic License, SSPL, BUSL or a proprietary licence, MUST NOT be copied. The behaviour of such a system is taken only from its public documentation. Code under a compatible licence MAY be used only with credit. See [conventions.md](../../process/conventions.md#code-from-elsewhere).
3. Contributors working on the project's behalf MUST NOT search for or read patents for design work. Any patent concern goes to the maintainers.

## 5. Idiom and consistency

OpenSearch has no equivalent of any choice below, as section 4 says, so each item names stock, the earlier decisions and the idiom only.

1. **Off by default.** Stock match: a stock node has no such table. Earlier decision match: decision record 0004 keeps a fork feature off by default. Idiom: opt in.
2. **A top level yaml setting, `startup_checks_view_enabled`, with two nodetool commands.** Stock match: boolean settings end in `_enabled`, and toggles are `enable` and `disable` commands. Earlier decision match: branching-and-review.md item 1. It differs on purpose from decision record 0005, which has no toggle, for the reason section 2 gives. The setting is not an entry under `startup_checks`, because the view is not a startup check. Idiom: stock.
3. **The view in `system_views`, named `startup_checks`.** Decision record 0007. Stock match: the home of `settings` and `system_properties`, and the name of the yaml block. Idiom: stock.
4. **Three columns, `name`, `enabled` and `source`.** Stock match: `name` is the key of `settings` and `system_properties`, and `enabled` is the key stock uses under `startup_checks`. Stock has no `source` column. Earlier decision match: none. Idiom: CQL.
5. **The values of `source`: `default`, `yaml`, `system_property` and `always_on`.** Stock match: stock calls a start option a system property, in the table `system_properties` and in the warning of `StartupChecks.checkDatacenter`. Lower case words joined by `_`, as stock names are. Earlier decision match: none. Idiom: stock.
6. **The names of the 15 always-run rows.** Decision record 0008. Stock match: this line has no names, and the names match Apache Cassandra 6.0. Earlier decision match: differs on purpose from the `check_` in front of `check_commitlog_shared_disk` (decision record 0005), because that name is a yaml name of a switchable check and these are not. Idiom: Apache Cassandra 6.0.
7. **The source `yaml` for every yaml entry.** Decision record 0009. Stock match: stock fills the key `enabled` in while it loads the yaml and keeps no note of it. Earlier decision match: keeps a node with the feature off as stock (branching-and-review.md item 7). Idiom: CQL.
8. **A refusal that names the switch.** Stock match: none, stock has no switched table. Earlier decision match: branching-and-review.md item 7. Idiom: the fork's.
9. **The counters `Reads`, `RefusedReads` and `FailedSwitches` of the type `StartupChecksView`, and the MBean `org.chronitondb:type=StartupChecksView`.** Stock match: Dropwizard counters through `CassandraMetricsRegistry`. Earlier decision match: conventions.md, Names, items 3 and 4. Idiom: a counter named for what it counts.

## 6. Quality requirements

| ISO/IEC 25010 characteristic | Line | Requirements, or the reason it does not apply |
|---|---|---|
| Performance efficiency | Fastest correct design, with benchmarks in the design and in the gates | Does not apply, because the only request that runs the code is a read of the view, which builds at most one row for each check from values already in memory. Section 7. |
| Performance efficiency | Memory budgets on coordinator and replica | Does not apply, because the feature holds one MBean, three counters and, from the first switch on, one table object. A read allocates about 20 small rows. |
| Reliability | Isolation levers on coordinator and replica: thread pools, limits, load shedding, timeouts, kill switch | REQ-SCV-001, REQ-SCV-006 and REQ-SCV-014: the kill switch is the setting and its toggle. No thread, pool or limit exists, because a read runs on the thread that serves the query and does no IO. |
| Reliability | Automatic fallbacks opt-in, with yaml setting, nodetool toggle, metric and rate-limited log line | Does not apply, because there is no fallback. |
| Reliability | Coordination between nodes model checked, when the design changes it | Does not apply, because each node answers for itself and nothing crosses the network. |
| Compatibility | Stock Apache Cassandra behaviour unchanged | REQ-SCV-001 and REQ-SCV-002. Section 3: the one change behind the switch and the three presences, each with its reason. |
| Compatibility | Stock behaviour unchanged with the feature off | REQ-SCV-002 and REQ-SCV-014. The stock suites of section 14 run unchanged with the switch at its default, off. |
| Compatibility | Mixed-version cluster, upgrade and rollback (see the Compatibility section) | REQ-SCV-024 and section 9. |
| Functional suitability | CQL validity and results independent of replication factor, data centres and replica count | Met: a virtual table is local to the node that serves the query, and its rows come from that node's configuration only. |
| Flexibility | Settings per index or per table over global ones, with global, include and exclude modes | Does not apply, because the setting is a property of the node, not of data. |
| Interaction capability | nodetool toggles change the in-memory value only, yaml holds the startup value | REQ-SCV-001 and REQ-SCV-004 to REQ-SCV-006: the commands change the `Config` field in memory, and a restart returns to the yaml value. |
| Interaction capability | Error messages name the setting or toggle that controls the behaviour | REQ-SCV-014, and the failed warning of REQ-SCV-017, whose text names the setting. |
| Maintainability | Observability: metrics, traces and diagnostics as a gate item | REQ-SCV-007, REQ-SCV-017 and REQ-SCV-019 to REQ-SCV-021. Section 8. Item 6 of the observability rules is answered in section 8, item 9. |
| Security | Threat model answered (see the Threat model section) | REQ-SCV-009 and REQ-SCV-015. Section 10. |
| Safety | Any risk of data loss or corruption named, with its mitigation | None from the code: the feature reads settings and writes nothing to disk, to the commit log or to any table. |

The design changes no coordination between nodes, so it carries no model.

## 7. Performance

### Hot path statement

One request type touches the new code: a CQL read of the view, on the node that serves it. Coordinator reads and writes of other tables, replica reads, memtable writes, flush, compaction, streaming and repair never call it.

### Expected cost

| Path | Metric | Stock today | Expected with the change | Why (mechanism) |
|---|---|---|---|---|
| Node start | work | the stock registration of two virtual keyspaces | one more MBean, three counters, and with the switch on one more registration | one call of `VirtualKeyspaceRegistry.register` |
| A read of the view | rows built | none, the table does not exist | one row for each check, 19 today, built again at each read | one lookup in an `EnumMap` and at most one system property read for each switchable check |
| Every other request | work | as today | as today | no stock request path calls the new code |

### Isolation levers

The setting `startup_checks_view_enabled` and its two nodetool commands. Off, the default: the table is not registered, and a read that still reaches it is refused. No thread pool, no memory limit and no timeout exist, since a read does no IO.

### Benchmarks that prove it

| Claim | Benchmark | Command | Pairs | Threshold |
|---|---|---|---|---|
| none | none, there is no stock request path to measure | none | none | none |

### Regression threshold and gate

No benchmark gates this pull request. The gate runs the tests of section 14.

### Stock guard

The stock suites of section 14 run unchanged, with the switch at its default, off, which is the state in which the node must match stock.

### What was not measured

Nothing was measured, because the change is off every stock request path. No follow-up issue is needed.

## 8. Observability

1. **Counted.** Three counters of the type `StartupChecksView`, registered by the hook at node start. `org.chronitondb.metrics:type=StartupChecksView,name=Reads` rises by one for each read the view serves (REQ-SCV-019). A read is one read command, as [New terms](#new-terms), item 3, says, so a `SELECT` that stock runs as several read commands counts once for each. `org.chronitondb.metrics:type=StartupChecksView,name=RefusedReads` rises by one for each read refused because the switch is off (REQ-SCV-020). `org.chronitondb.metrics:type=StartupChecksView,name=FailedSwitches` rises by one for each failed warning (REQ-SCV-021).
2. **Timed.** Nothing: a read does no IO and has no duration worth a timer.
3. **Logged.** The changed line, at INFO, for a change of the switch by nodetool, with the old and the new value (REQ-SCV-007). The failed warning, at WARN, with the exception as the last logging argument (REQ-SCV-017). Both texts are in [New terms](#new-terms). A switch on from the yaml at start logs no line of its own: the stock line `Node configuration:` already shows the setting. Nothing is logged for a read.
4. **Traced.** Nothing of its own: a read makes no plan decision and has no fallback. A traced read shows the stock trace lines of a virtual table read.
5. **Client visible.** The rows, and the refusal of REQ-SCV-014.
6. **Exposed.** The MBean `org.chronitondb:type=StartupChecksView`, with the attribute `Enabled` and the operations `enable` and `disable`. The three counters over JMX and through any configured metrics reporter. The switch also shows in the row `startup_checks_view_enabled` of `system_views.settings`, at its running value, because the toggle writes the `Config` field.
7. **Toggled.** In `cassandra.yaml`, read at start, and with the two nodetool commands, in memory only.
8. **Audited.** Nothing of its own. A read of the view is a `SELECT`, which the stock audit log records as any other when it is on.
9. **Released on drop.** When the switch goes off the view leaves the lists of tables and its name no longer resolves. Its one table object stays in the registry by its id, because the registry on this line has no call that removes a table (section 3). It holds no rows: they are built at each read. The MBean and the counters live as long as the node, because the MBean is the handle of the toggle.
10. **Documented.** The reference page of section 13 lists every name (REQ-SCV-023).
11. **Tested.** Section 14.

No line above TRACE carries a key, a term, a literal or a secret: the two lines carry `true` or `false`.

## 9. Compatibility

1. **On-disk format changes.** None. The feature writes no file.
2. **Mixed-version cluster.** Does not apply to behaviour between nodes: each node holds its own view, and nothing crosses the network. A client that reads the view on every node gets stock's error for a missing table from a node without the feature or with the switch off.
3. **Upgrade path and prerequisites.** None. A `cassandra.yaml` that does not set the key loads on every binary.
4. **Rollback path.** An operator who wrote `startup_checks_view_enabled` into `cassandra.yaml` removes it before starting an Apache Cassandra binary or a ChronitonDB build older than this change on that node. Such a binary refuses a key it does not know (`YamlConfigurationLoader.PropertiesChecker.check`, `YamlConfigurationLoader.java:423` at `bc2208e8fe`). REQ-SCV-024 puts the rollback sentence in `NEWS-chronitondb.txt`, and the reference page carries it.
5. **Runbook entries.** No runbook exists on this line. The rollback sentence lives on the reference page and in `NEWS-chronitondb.txt`.
6. **Surfaces touched.** Configuration: one new key. Command line tools: two new nodetool commands. JMX and metrics: one MBean and three counters. Virtual tables: one table, with the switch on only. No version of any surface is bumped.
7. **Shared state.** The switch writes nothing to shared state, off or on. The view is not in the schema that nodes exchange.
8. **The other line.** The item carries one line label, `chronitondb-sandbox`. On a 6.0 line the names come from `StartupCheck.name` and the list from `StartupChecks.getChecks` (section 4). That port is section 15 item 1.

## 10. Threat model and security

One new entry point: a CQL read of the view. Its only input is the statement, which the stock parser and the stock virtual table code handle. The view parses nothing of its own. The two nodetool commands take no argument and reach the node over JMX, under the stock JMX authentication and authorisation.

By STRIDE:

1. **Spoofing, tampering, repudiation.** Do not apply: the view is read only, takes no write and changes no data. A read is in the stock audit log when that is on.
2. **Information disclosure.** A row tells a reader which checks a node runs, among them whether the ownership check and the data resurrection check are on. The view shows no other setting of a check (REQ-SCV-009), so the ownership token never appears. The stock tables `settings` and `system_properties` already show the same facts, and the token, to a role that may read `system_views`. The permission the view needs is `SELECT` on the table, by the stock rule of its keyspace (decision record 0007), with the negative test of REQ-SCV-015. The feature edits no file of authentication or authorisation.
3. **Denial of service.** A read builds about 20 rows from memory. It holds no lock that a stock path takes. The hook at start returns normally whatever `Exception` is thrown in it (REQ-SCV-016).
4. **Elevation of privilege.** Does not apply: the view grants nothing. Switching it needs JMX access to the node, as every nodetool command does.

Errors map to client errors as stock maps them: the refusal of REQ-SCV-014 is an invalid request, and the refusal of REQ-SCV-015 is stock's unauthorised error. No limit with warn and fail thresholds exists, because the number of rows is fixed by the build.

## 11. Dependencies

No new dependency.

## 12. Compliance impact

The view copies no user data, so nothing needs erasure, masking, retention or a residency rule, and backups and snapshots hold nothing new. It shows node configuration: check names and whether each is on. Access control is the stock rule of the view's keyspace. A read is audited as any `SELECT`. The feature logs `true` and `false` only, uses no cryptography and adds no library. The default is the safe one: off.

For operators: the view is switched with `startup_checks_view_enabled` in `cassandra.yaml`, default `false`, and at runtime with `nodetool enablestartupchecksview` and `nodetool disablestartupchecksview`, which do not survive a restart.

## 13. Documentation

This item adds one reference page, `docs/reference/startup-checks-view.md`, written by the developer from the skeleton `page-startup-checks-view.md` next to this record. The page carries:

1. The setting, its type, its default and the two nodetool commands.
2. The view, its three columns and the example of section 1.
3. The four values of `source` and the rule that decides between them, with the three start options by name.
4. The names of the rows, and what each always-run check is.
5. Who may read the view.
6. The refusal text, the two log lines and the three counters by their full names.
7. Failure behaviour: a read while the switch is off is refused. A node without the MBean answers the nodetool commands with the missing MBean line. A switch that fails logs the failed warning, and the nodetool command exits with a status other than 0. A read never times out on IO, because it does none. Coordinator failure, a missing replica, a limit and an index that is not built do not apply, because the view is local.
8. Known limitations. A row says whether a check is on, not what it found. Two always-run checks do nothing on a platform other than Linux, and `cassandra.ignore_kernel_bug_1057843_check` skips part of one. A yaml entry without the key `enabled` shows `yaml`, although its value is the default of the check (decision record 0009). A read of the view that runs at the moment the view is switched on can fail once with a server error. The view is local: each node answers for itself.
9. The rollback sentence.

`NEWS-chronitondb.txt` gains an entry for the view and the rollback sentence (REQ-SCV-024). The delta entry `docs/delta/startup-checks-view.md` with its row in `docs/delta/README.md` records the stock edits and the presences of section 3.

Apache's `conf/cassandra.yaml` stays untouched. `conf/cassandra_chronitondb.yaml` does not exist on this line, see section 15 item 3.

## 14. Testing

Five unit test classes and one in-JVM distributed test class. The distributed test starts one node. Nothing is multi node in behaviour, so replication factor does not apply. No sstable format or compaction is touched. The parity suite does not exist on this line yet, see waiver 1. This item adds no scenario, under waiver 2, so the template's `Scenario runner` and `Scenario tags` lines are left out.

How the tests reach the feature. The unit tests that read the view or run nodetool extend `CQLTester`. Its network setup registers `system_virtual_schema` only (`CQLTester.startServices`, `test/unit/org/apache/cassandra/cql3/CQLTester.java:635` at `bc2208e8fe`), so each such test registers `SystemViewsKeyspace.instance` itself before it starts the view. They run the commands through `ToolRunner.invokeNodetool` against the test's JMX server, as the stock nodetool tests do (`ToolRunner.invokeNodetool`, `test/unit/org/apache/cassandra/tools/ToolRunner.java:184` at `bc2208e8fe`). `StartupChecksView` takes the call that registers a keyspace as a constructor argument: `instance` passes `VirtualKeyspaceRegistry.instance::register`, and a test passes a call that throws. `StartupCheckRows` takes the options, the map `Config.startup_checks` and the system properties as arguments, so its tests need no node.

What each test of the list under Tests for this change proves:

1. `StartupCheckRowsTest.oneRowForEachCheck`: the names of the rows are the 15 always-run names and the name of each constant of `StartupCheckType` other than `non_configurable_check`, and no other name (REQ-SCV-008).
2. `StartupCheckRowsTest.alwaysRunRows`: each of the 15 always-run rows shows `true` and `always_on` (REQ-SCV-010, REQ-SCV-025).
3. `StartupCheckRowsTest.defaultRows`: with the options of `new StartupChecksOptions()`, an empty map and no start option, each of the four switchable rows shows `default` (REQ-SCV-011).
4. `StartupCheckRowsTest.yamlRows`: with a map that holds `check_dc` with `enabled` set to `false` and `check_filesystem_ownership` with no key `enabled`, and no start option, those two rows show `yaml` and the other two show `default` (REQ-SCV-012).
5. `StartupCheckRowsTest.systemPropertyRows`: with `cassandra.ignore_dc` set to `true`, `check_dc` shows `false` and `system_property`. With it set to `false`, `true` and `system_property`. The same for `cassandra.ignore_rack` and `check_rack`. With `cassandra.enable_fs_ownership_check` set to `true`, and then to `false`, `check_filesystem_ownership` shows that value and `system_property`, and the row's `enabled` equals what `FileSystemOwnershipCheck.isEnabled` returns for the same options. Each case also sets the opposite value in the options, to prove that the start option wins (REQ-SCV-013, REQ-SCV-026).
6. `StartupCheckRowsTest.enabledWithoutStartOption`: with no start option, for each switchable check and for options built with no entry, with `enabled` set to `true` and with `enabled` set to `false`, the row's `enabled` equals what `StartupChecksOptions.isEnabled` returns. With no entry that is `true` for `check_dc` and `check_rack` and `false` for `check_filesystem_ownership` and `check_data_resurrection` (REQ-SCV-027).
7. `StartupCheckRowsTest.everyRegisteredCheckHasAName`: the test builds the checks as the daemon does, `new StartupChecks().withDefaultTests().withTest(new FileSystemOwnershipCheck())`, reads the private list `StartupChecks.preFlightChecks` (`StartupChecks.java:130` at `bc2208e8fe`) by reflection, and asserts that every check of type `non_configurable_check` in it is a key of the fixed list, and that the fixed list has no other key. An import that adds an always-run check fails here (REQ-SCV-018).
8. `StartupChecksViewTest.notListedWhileOff` and `listedWhileOn`: a `SELECT` on `system_virtual_schema.tables` finds no row for the view before `nodetool enablestartupchecksview`, one row after it, and none after `nodetool disablestartupchecksview` (REQ-SCV-002, REQ-SCV-003).
9. `StartupChecksViewTest.columns`: the metadata of the view has exactly the columns `name`, `enabled` and `source` (REQ-SCV-009).
10. `StartupChecksViewTest.toggleLogsOldAndNew`: `nodetool enablestartupchecksview` against a node with the switch off exits with 0, the row `startup_checks_view_enabled` of `system_views.settings` then shows `true`, and the log holds the changed line with `false` and `true`. `nodetool disablestartupchecksview` then exits with 0, the row shows `false`, and the log holds the changed line with `true` and `false` (REQ-SCV-005, REQ-SCV-006, REQ-SCV-007).
11. `StartupChecksViewTest.readWhileOffIsRefused`: a statement prepared while the switch is on, executed after a switch off, fails with an invalid request whose message is the refusal text, and `RefusedReads` rose by one (REQ-SCV-014, REQ-SCV-020).
12. `StartupChecksViewTest.countsReads`: `Reads` rose by one after one `SELECT` of every row of the view (REQ-SCV-019).
13. `StartupChecksViewTest.startNeverThrows`: with a registration that throws `IllegalStateException` and the `Config` field at `true`, `start` returns (REQ-SCV-016).
14. `StartupChecksViewTest.failedSwitchOn`: with a registration that throws `IllegalStateException`, after `start` with the `Config` field at `true`, and again after `enable`, the `Config` field is `false`, the log holds the failed warning and `FailedSwitches` rose by one (REQ-SCV-017, REQ-SCV-021, REQ-SCV-030).
15. `StartupChecksViewAuthTest.readNeedsSelect`: with authentication and authorisation on, a role with no grant is refused as unauthorised, and the same role reads the view after `GRANT SELECT` on it (REQ-SCV-015).
16. `StartupChecksViewCommandsTest.missingMBean`: each command, run against a JMX server that has no `org.chronitondb:type=StartupChecksView`, prints the missing MBean line and exits with a status other than 0 (REQ-SCV-022, REQ-SCV-028).
17. `StartupChecksViewCommandsTest.failedSwitchStatus`: `nodetool enablestartupchecksview`, run against a view built with a registration that throws, exits with a status other than 0, and so does `nodetool disablestartupchecksview` against a view that is on and whose registration then throws (REQ-SCV-029).
18. `StartupChecksViewStartTest.yamlSwitchesTheViewOn`: an in-JVM cluster of one node configured with `startup_checks_view_enabled` set to `true` starts, the row `startup_checks_view_enabled` of `system_views.settings` shows `true`, and a `SELECT` of the view returns 19 rows (REQ-SCV-004, and criteria 2 and 3 end to end).
19. `StartupChecksViewStartTest.defaultNodeHasNoView`: an in-JVM cluster of one node with the default configuration starts, the row `startup_checks_view_enabled` of `system_views.settings` shows `false`, `system_virtual_schema.tables` has no row for the view, and a `SELECT` of it fails with stock's error for a table that does not exist (REQ-SCV-001, and REQ-SCV-002 end to end).
20. `StartupChecksViewDocsTest.exactNamesAreDocumented` and `rollbackLineInNews`: the reference page contains each text of REQ-SCV-023, and `NEWS-chronitondb.txt` contains the rollback sentence (REQ-SCV-023, REQ-SCV-024).

### Tests for this change

org.chronitondb.startup.StartupCheckRowsTest
org.chronitondb.startup.StartupChecksViewTest
org.chronitondb.startup.StartupChecksViewAuthTest
org.chronitondb.startup.StartupChecksViewDocsTest
org.chronitondb.tools.nodetool.StartupChecksViewCommandsTest
org.chronitondb.startup.test.StartupChecksViewStartTest

### Existing suites at risk

org.apache.cassandra.db.virtual.SettingsTableTest
org.apache.cassandra.db.virtual.SystemPropertiesTableTest
org.apache.cassandra.config.DatabaseDescriptorTest
org.apache.cassandra.config.ConfigCompatibilityTest
org.apache.cassandra.config.YamlConfigurationLoaderTest
org.apache.cassandra.service.StartupChecksTest

### Stock suites run unchanged

org.apache.cassandra.db.virtual.SettingsTableTest
org.apache.cassandra.db.virtual.SystemPropertiesTableTest
org.apache.cassandra.config.DatabaseDescriptorTest
org.apache.cassandra.config.ConfigCompatibilityTest
org.apache.cassandra.config.YamlConfigurationLoaderTest
org.apache.cassandra.service.StartupChecksTest
org.apache.cassandra.config.StartupCheckOptionsTest
org.apache.cassandra.distributed.test.DataResurrectionCheckTest

### Tracing test

does not apply, because a read of the view makes no plan decision and has no fallback, so the feature adds no trace line

### Formats and configurations

no

## 15. Not covered and follow-ups

1. The port to a 6.0 line, where the names come from `StartupCheck.name` and the list from `StartupChecks.getChecks`. This item carries one line label. Candidate issue, for a maintainer to open when a 6.0 line takes the feature.
2. The row of the commit log disk check. Its constant is not on the line yet. Rule 2 of section 1 gives it a row when its code merges, with no change here. Its code pull request adds the name to the reference page of this feature if this feature merged first.
3. `conf/cassandra_chronitondb.yaml` does not exist on this line. When the item that creates it lands, the setting goes into it, commented out with its default. Candidate issue.
4. `VirtualKeyspaceRegistry.register` removes the tables of a replaced keyspace by the table object, from a map keyed by table id, so it removes none (`VirtualKeyspaceRegistry.java:46` at `bc2208e8fe`). Apache trunk removes by id (`VirtualKeyspaceRegistry.register`, `VirtualKeyspaceRegistry.java:42` to `49` at `2249e37b51`). This design makes no such fix. An import that brings it changes two things for this feature. A statement prepared earlier and run after a switch off finds no table, so `StartupChecksViewTest.readWhileOffIsRefused` fails on that import and the integrator sees it. And a read of a stock table of `system_views` that races a switch could find no table for a moment. The item of that import decides how the view is then registered. Candidate for an import.
5. The scenarios of the feature `SCV`, once the scenario module `test/bdd/` exists on the line, see waiver 2.
6. `NEWS-chronitondb.txt` and `docs/reference/` do not exist on the line today. The design records of the release version feature and of the commit log disk check plan to create both. The Planned file list names `NEWS-chronitondb.txt` as `new`. If one of those merges first, the word becomes `edit`, through change control.

## New terms

1. **The switch**: the value of the field `Config.startup_checks_view_enabled` of the running node, once the hook at node start has returned. On when `true`, off when `false`. In yaml `startup_checks_view_enabled`, in nodetool `enablestartupchecksview` and `disablestartupchecksview`, in docs "the startup checks view setting".
2. **The view**: the virtual table of this feature, `system_views.startup_checks` (decision record 0007). In code `org.chronitondb.startup.StartupChecksTable`, in docs "the startup checks view". Key `SCV`.
3. **A read**: one read command that reaches the view. Stock runs a `SELECT` of every row that fits one page as one read command, and a `SELECT` that names several values of `name`, or that takes several pages, as one read command for each value or page.
4. **An always-run check**: a check the daemon registers whose `StartupCheck.getStartupCheckType` returns `non_configurable_check`. On this line the 15 fields of `StartupChecks`: `checkKernelBug1057843`, `checkJemalloc`, `checkLz4Native`, `checkValidLaunchDate`, `checkJMXPorts`, `checkJMXProperties`, `inspectJvmOptions`, `checkNativeLibraryInitialization`, `initSigarLibrary`, `checkMaxMapCount`, `checkReadAheadKbSetting`, `checkDataDirs`, `checkSSTablesFormat`, `checkSystemKeyspaceState` and `checkLegacyAuthTables`. Its name in the view is the row name decision record 0008 gives its field.
5. **A switchable check**: a constant of `StartupChecks.StartupCheckType` other than `non_configurable_check`. On this line `check_filesystem_ownership`, `check_dc`, `check_rack` and `check_data_resurrection`. Its name in the view is the name of the constant. **A check of the node**: an always-run check or a switchable check.
6. **A start option**: a Java system property the node was started with. A start option is set when `CassandraRelevantProperties.isPresent` is true for it. **The value a start option gives**: for `check_dc` the opposite of what `CassandraRelevantProperties.IGNORE_DC.getBoolean` returns, for `check_rack` the opposite of what `CassandraRelevantProperties.IGNORE_RACK.getBoolean` returns, and for `check_filesystem_ownership` what `CassandraRelevantProperties.FILE_SYSTEM_CHECK_ENABLE.getBoolean` returns. These are the values the stock checks act on (section 4, stock item 4).
7. **A yaml entry**: a key for the check in the map `Config.startup_checks` of the running node.
8. **A failed switch**: a run of `StartupChecksView.start`, `enable` or `disable` in which an `Exception` is thrown. `start` is the hook at node start, and `enable` and `disable` are the MBean operations of the two nodetool commands (section 3).
9. **The changed line**: the INFO line with this text, the old value first: `The startup checks view setting startup_checks_view_enabled changed from {} to {}.`
10. **The failed warning**: the WARN line with this text. Its first value is the value the run was to give the switch: the value of the yaml setting for `start`, `true` for `enable` and `false` for `disable`. Its second value is the value of the switch afterwards: `The startup checks view could not be switched to {}. The setting startup_checks_view_enabled is {}.`
11. **The missing MBean line**: this exact text: `This node has no startup checks view: the MBean org.chronitondb:type=StartupChecksView was not found.`
12. **The refusal text**: this exact text: `The startup checks view is off. Set startup_checks_view_enabled to true in cassandra.yaml, or run nodetool enablestartupchecksview.`
13. **The rollback sentence**: this exact text, on one line: `Before a node runs an Apache Cassandra binary, or a ChronitonDB build older than this feature, remove startup_checks_view_enabled from its cassandra.yaml.`

## Where problems could occur

1. **A node does not start.** Seen by an operator as a node that exits during startup, on every node, if the hook in `CassandraDaemon.setupVirtualKeyspaces` throws. From `StartupChecksView.start`. REQ-SCV-016 makes it return normally whatever `Exception` is thrown, and REQ-SCV-017 logs it. An `Error`, such as a class of the feature missing from the jar, is not caught: stock code does not catch it at this point either.
2. **A node rolled back to an Apache Cassandra binary, or to an older ChronitonDB build, does not start.** Seen as a node that refuses its `cassandra.yaml` with `Invalid yaml. Please remove properties`, on a node whose operator wrote the key into the yaml. From the new key. Not from the default.
3. **A node that switched the view off still serves it.** Seen as rows from a table that the node no longer lists, for a statement prepared while the switch was on. From the registry, which keeps the table by its id. REQ-SCV-014.
4. **A role reads the view that should not.** Seen as a role with no grant that learns which checks a node runs. From the place the view is registered in. REQ-SCV-015.
5. **A row is wrong or missing.** Seen by an operator as a check shown on that is off, a source that is not the real one, or a check the node runs that has no row, so that the operator trusts a wrong picture of the node. From the rules of section 1, from a start option the view does not know, or from an import that adds a check or changes how a check reads its start option. REQ-SCV-008, REQ-SCV-010 to REQ-SCV-013 and REQ-SCV-025 to REQ-SCV-027, and REQ-SCV-018 for the import.
6. **A nodetool command fails without a reason.** Seen as a stack trace from `nodetool enablestartupchecksview` against an Apache Cassandra node or an older build. From the lookup of the MBean. REQ-SCV-022 and REQ-SCV-028.
7. **The page names the setting, a command, a row or a counter wrongly.** Seen as a documented name the node does not know. From a page written by hand. REQ-SCV-023.
8. **The stock tables of `system_views` break on a node that switched the view on.** Seen as a stock table of `system_views` that is missing or fails after `nodetool enablestartupchecksview`. From the registration of a second `system_views` keyspace object (decision record 0007, section 3).
9. **Every in-JVM distributed test fails to start its instances.** Seen by a developer as an error at instance start in every in-JVM test, with the switch off too. From the hook call, if the in-JVM test framework loads the fork class once for all instances. Not seen on a real node.
10. **A switch fails and the operator does not learn it.** Seen as a `nodetool enablestartupchecksview` that ends cleanly on a node that then has no view, or as a settings row that shows `true` on such a node. From a failed switch. REQ-SCV-017, REQ-SCV-029 and REQ-SCV-030.
11. **A read of the view fails at the moment of a switch on.** Seen as one server error for a `SELECT` of the view that runs while `nodetool enablestartupchecksview` is running, on that node only. From the stock registry, which makes the name of a table known before it makes the table reachable by id (`VirtualKeyspaceRegistry.register`, `VirtualKeyspaceRegistry.java:43` and `47` at `bc2208e8fe`). The same read succeeds when run again. Stock tables are not affected (section 3).

### Test plan

1. Problem 1: `StartupChecksViewTest.startNeverThrows` and `failedSwitchOn`, and the stock suites that start a daemon run unchanged.
2. Problem 2: no test on this line can start an Apache binary. `StartupChecksViewDocsTest.rollbackLineInNews` proves the rollback sentence is in the news file. Watched through the reference page.
3. Problem 3: `StartupChecksViewTest.readWhileOffIsRefused`.
4. Problem 4: `StartupChecksViewAuthTest.readNeedsSelect`.
5. Problem 5: the seven tests of `StartupCheckRowsTest`. Its `systemPropertyRows` compares the ownership row with `FileSystemOwnershipCheck.isEnabled`, so an import that changes how that check reads its start option fails there.
6. Problem 6: `StartupChecksViewCommandsTest.missingMBean`.
7. Problem 7: `StartupChecksViewDocsTest.exactNamesAreDocumented`.
8. Problem 8: `StartupChecksViewTest.listedWhileOn` also reads `system_views.settings` after `enable` and after `disable`, and `SettingsTableTest` and `SystemPropertiesTableTest` run unchanged.
9. Problem 9: `DataResurrectionCheckTest`, unchanged, and `StartupChecksViewStartTest.defaultNodeHasNoView` start instances through the hook call.
10. Problem 10: `StartupChecksViewTest.failedSwitchOn` and `StartupChecksViewCommandsTest.failedSwitchStatus`.
11. Problem 11: no test. The window is between two statements of one stock method, and a test cannot hold it open without an edit to that stock file. The reference page states it as a known limitation.

## Planned file list

```
src/java/org/apache/cassandra/config/Config.java stock
src/java/org/apache/cassandra/service/CassandraDaemon.java stock
src/java/org/apache/cassandra/tools/NodeTool.java stock
src/java/org/chronitondb/startup/StartupChecksView.java new
src/java/org/chronitondb/startup/StartupChecksViewMBean.java new
src/java/org/chronitondb/startup/StartupChecksTable.java new
src/java/org/chronitondb/startup/StartupCheckRows.java new
src/java/org/chronitondb/tools/nodetool/EnableStartupChecksView.java new
src/java/org/chronitondb/tools/nodetool/DisableStartupChecksView.java new
test/unit/org/chronitondb/startup/StartupCheckRowsTest.java test
test/unit/org/chronitondb/startup/StartupChecksViewTest.java test
test/unit/org/chronitondb/startup/StartupChecksViewAuthTest.java test
test/unit/org/chronitondb/startup/StartupChecksViewDocsTest.java test
test/unit/org/chronitondb/tools/nodetool/StartupChecksViewCommandsTest.java test
test/distributed/org/chronitondb/startup/test/StartupChecksViewStartTest.java test
docs/reference/startup-checks-view.md new
docs/delta/startup-checks-view.md new
docs/delta/README.md edit
NEWS-chronitondb.txt new
```

The three stock files carry the hook points of section 3 and nothing else. `StartupChecksView` holds the switch, the MBean operations, the counters and the two log lines, and `StartupChecksViewMBean` is its MBean interface. `StartupChecksTable` is the virtual table. `StartupCheckRows` works out the rows by the rules of section 1. The two commands toggle the switch. The coverage file next to this record is not in the list. No protected path and no library file is in the list.

The open pull requests were listed on 2026-11-15: there is none. The merged design record of the release version feature plans edits to `Config.java` and `NodeTool.java` too, and both merged records plan `NEWS-chronitondb.txt` and `docs/delta/README.md`. Their code pull requests are not open yet.

### Shared with open items

None.

### Waivers

1. Exit criterion 4 of [testing.md](../../process/testing.md#exit-criteria), the parity suite passes with every fork feature off. The parity suite does not exist on this line. In its place the stock suites of section 14 run unchanged with the switch at its default, off. Waived because there is no parity suite to run. The maintainers approve the waiver with this record.
2. [testing.md, Scenarios](../../process/testing.md#scenarios) item 6: the designer writes the scenarios of a feature item in this pull request, tagged `@wip`. Waived because nothing that runs a scenario exists on this line: no `test/bdd/` module, no shared step library and no Cucumber runner. Every requirement is proven instead by a JUnit test named in `ac-coverage.md`. The maintainers approve the waiver with this record.

## Requirement quality checklist (ISO/IEC/IEEE 29148)

Each of REQ-SCV-001 to REQ-SCV-030 was checked against the seven qualities before this record went to review:

1. **Necessary:** each traces to an acceptance criterion of section 1, a problem named in Where problems could occur, a decision record or a line of quality-requirements.md. REQ-SCV-007 and REQ-SCV-019 to REQ-SCV-021 answer its observability rules.
2. **Unambiguous:** each names an exact text, an exact name, an exact counter or an exact value, and the fixed terms are defined in New terms. No "fast" or "large" appears.
3. **Singular:** one key word and one EARS shape each. The `source` of a row has REQ-SCV-010 to REQ-SCV-013 and its `enabled` has REQ-SCV-025 to REQ-SCV-027. The line a command prints against a node without the MBean is REQ-SCV-022 and its exit status is REQ-SCV-028. The three counters have their own ids.
4. **Verifiable:** each has one row in `ac-coverage.md` naming its test.
5. **Feasible:** each mechanism is cited by symbol, file and line in sections 3 and 4, or is the new code of the Planned file list.
6. **Consistent:** REQ-SCV-001 and REQ-SCV-004 split the start by what the yaml sets. REQ-SCV-016, REQ-SCV-017, REQ-SCV-021, REQ-SCV-029 and REQ-SCV-030 cover a failed switch, and REQ-SCV-030 is the one case in which the switch is off after REQ-SCV-004 or REQ-SCV-005 applied. REQ-SCV-011 to REQ-SCV-013 split the switchable rows into three cases that do not overlap, and REQ-SCV-026 and REQ-SCV-027 into two. None contradicts a decision record or a stock behaviour rule.
7. **Traceable:** each has an id, a source and exactly one coverage row.
