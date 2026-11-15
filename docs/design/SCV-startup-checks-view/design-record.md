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
| References | Issue #117. Line `chronitondb-sandbox`, read at commit `bc2208e8fe`. Apache base commit `76550e931481e965ae3283d8cf4a59c320d74c55` (Apache `cassandra-5.0`). No feature spec and no plan: the one-item path. Process pages [branching-and-review.md](../../process/branching-and-review.md#feature-switches-and-defaults) and [quality-requirements.md](../../process/quality-requirements.md). Decision records 0001, 0004 and 0005. |
| Risk | Normal: the issue's label `risk:normal`. The worst Bug Category is Degradation, a read of the view that fails or shows a wrong value. The floor applies because the change touches configuration, command line tools, JMX MBeans and virtual tables. The change edits no file of authentication or authorisation: the view takes the stock rule of its keyspace. For the maintainers, who confirm the class when they merge this record: if the hook at node start threw, the node would not start, an Availability fault that [classification.md](../../process/classification.md#risk) rates Critical. REQ-SCV-016 is written to exclude it. |
| Size | Low Hanging Fruit: four small fork classes, two nodetool commands and three one line edits to stock files, with no dependency on other work. |
| Reach | One area: the virtual tables of one node, in the new package `org.chronitondb.startup`, with hooks in `org.apache.cassandra.config`, `org.apache.cassandra.service` and `org.apache.cassandra.tools`. |
| Touches | public interface (configuration), public interface (command line tools and arguments), public interface (jmx mbeans, including metrics), public interface (virtual tables), new input or privilege, new feature or switch |

Change history: the git history of this file.

Location: `docs/design/SCV-startup-checks-view/`, the directory of the fork feature with the key `SCV`, which this record proposes and the merge of its pull request reserves ([additive.md, Feature keys and requirement ids](../../process/additive.md#feature-keys-and-requirement-ids), item 2), with the coverage file `ac-coverage.md` next to it. Every section is filled, or carries a waiver with its reason.

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in BCP 14 (RFC 2119, RFC 8174) when, and only when, they appear in all capitals, as shown here.

The Risk, Size and Reach rows are the item's class, as [classification.md](../../process/classification.md) defines it, and match the issue's `risk:normal`, `size:low-hanging-fruit` and `reach:one-area` labels. The issue also carries `kind:additive`, so the item is a fork feature small enough for one item and takes the one-item path of [maintenance.md](../../process/maintenance.md#the-one-item-path) with a feature key: this directory, the ids `REQ-SCV-nnn`, and the feature class stated in [section 3](#3-stock-behaviour-preservation).

This version is a draft. Three points are open for the maintainers and are marked "Open point" where they bind the text. [Section 2](#2-decisions-implemented) lists them. The record is not ready for review until each has its decision record.

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

What this record builds, in short. One virtual table, `system_views.startup_checks` (Open point 1), with three columns:

```
CREATE TABLE system_views.startup_checks (
    name text PRIMARY KEY,
    enabled boolean,
    source text
)
```

The table exists only while the switch is on. The switch is the setting `startup_checks_view_enabled` in `cassandra.yaml`, default `false`, with the nodetool commands `enablestartupchecksview` and `disablestartupchecksview`, which change the running value only.

An example. A node with the view on, no `startup_checks` block in `cassandra.yaml`, started with `-Dcassandra.ignore_rack=true`. The 15 always-run rows are shown with the names of Open point 2, option A.

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

1. The always-run rows are a fixed list of 15 names, one for each of the 15 checks of `StartupChecks.DEFAULT_TESTS` whose type is `non_configurable_check` ([New terms](#new-terms), item 3). Each shows `enabled` as `true` and `source` as `always_on`.
2. The switchable rows are one for each constant of `StartupChecks.StartupCheckType` other than `non_configurable_check`, named by the constant. So a constant that a later change adds, such as the `check_commitlog_shared_disk` of the commit log disk check, gets its row with no change to this feature.
3. For a switchable row, the view first looks for the check's start option: `cassandra.ignore_dc` for `check_dc`, `cassandra.ignore_rack` for `check_rack`, `cassandra.enable_fs_ownership_check` for `check_filesystem_ownership`, none for any other constant. When the start option is set, `source` is `system_property`, and `enabled` is the value the stock check acts on: the opposite of the option's value for the two `ignore` options, and the option's value for the third.
4. Otherwise, when `cassandra.yaml` has an entry for the check under `startup_checks`, `source` is `yaml` and `enabled` is what `StartupChecksOptions.isEnabled` returns for the check (Open point 3).
5. Otherwise `source` is `default` and `enabled` is what `StartupChecksOptions.isEnabled` returns for the check, which is then the default of its constant.

The words this record uses with one fixed meaning are in [New terms](#new-terms): the switch, the view, an always-run check, a switchable check, a start option and a yaml entry.

### Requirements

In the sources below, "criterion n" is item n of the acceptance criteria above, and "problem n" is item n of [Where problems could occur](#where-problems-could-occur).

REQ-SCV-001 (ubiquitous): The switch MUST be off on a node whose `cassandra.yaml` does not set `startup_checks_view_enabled`. Source: stakeholder need, criterion 1.

REQ-SCV-002 (state driven): While the switch is off, the node MUST NOT list the view in `system_virtual_schema.tables`. Source: stakeholder need, criterion 1.

REQ-SCV-003 (state driven): While the switch is on, the node MUST list the view in `system_virtual_schema.tables`. Source: stakeholder need, criterion 2.

REQ-SCV-004 (event driven): When a node whose `cassandra.yaml` sets `startup_checks_view_enabled` to `true` has registered its virtual keyspaces at start, the switch MUST be on. Source: stakeholder need, criterion 2.

REQ-SCV-005 (event driven): When `nodetool enablestartupchecksview` runs against a node, the node MUST set the switch on. Source: stakeholder need, criterion 2.

REQ-SCV-006 (event driven): When `nodetool disablestartupchecksview` runs against a node, the node MUST set the switch off. Source: stakeholder need, criterion 2.

REQ-SCV-007 (event driven): When a nodetool command changes the value of the switch, the node MUST log the old and the new value at INFO. Source: [quality-requirements.md](../../process/quality-requirements.md#observability) item 3.

REQ-SCV-008 (state driven): While the switch is on, a `SELECT` of every row of the view MUST return exactly one row for each always-run check and one for each switchable check of the node. Source: stakeholder need, criterion 3.

REQ-SCV-009 (ubiquitous): The view MUST have the columns `name`, `enabled` and `source` and no other column. Source: stakeholder need, criteria 4 and 8.

REQ-SCV-010 (ubiquitous): The row of an always-run check MUST show `enabled` as `true` and `source` as `always_on`. Source: stakeholder need, criterion 6.

REQ-SCV-011 (ubiquitous): The row of a switchable check whose start option is not set and that has no yaml entry MUST show `source` as `default` and `enabled` as the default of the check. Source: stakeholder need, criteria 4 and 5.

REQ-SCV-012 (ubiquitous): The row of a switchable check whose start option is not set and that has a yaml entry MUST show `source` as `yaml` and `enabled` as the value `StartupChecksOptions.isEnabled` returns for the check. Source: stakeholder need, criteria 4 and 5.

REQ-SCV-013 (ubiquitous): The row of a switchable check whose start option is set MUST show `source` as `system_property` and `enabled` as the value the stock check acts on. Source: stakeholder need, criterion 7.

REQ-SCV-014 (unwanted behaviour): If the view is read while the switch is off, then the node MUST refuse the read with an invalid request error whose message names `startup_checks_view_enabled`. Source: problem 3 and [branching-and-review.md](../../process/branching-and-review.md#feature-switches-and-defaults) item 7.

REQ-SCV-015 (unwanted behaviour): If a role without the `SELECT` permission on the view reads it on a node with authorisation on, then the node MUST refuse the read as unauthorised. Source: problem 4.

REQ-SCV-016 (unwanted behaviour): If an `Exception` is thrown while the node applies the switch at start, then the hook MUST return normally. Source: problem 1.

REQ-SCV-017 (unwanted behaviour): If an `Exception` is thrown while the node applies the switch, at start or from nodetool, then the node MUST log the failed warning. Source: problem 1.

REQ-SCV-018 (ubiquitous): The fixed list of always-run names MUST hold a name for every check of type `non_configurable_check` that the daemon registers. Source: stakeholder need, criterion 3, and problem 5.

REQ-SCV-019 (event driven): When the view serves a read, the node MUST raise the counter `org.chronitondb.metrics:type=StartupChecksView,name=Reads` by one. Source: [quality-requirements.md](../../process/quality-requirements.md#observability) item 1.

REQ-SCV-020 (event driven): When the view refuses a read because the switch is off, the node MUST raise the counter `org.chronitondb.metrics:type=StartupChecksView,name=RefusedReads` by one. Source: [quality-requirements.md](../../process/quality-requirements.md#observability) item 1.

REQ-SCV-021 (event driven): When the node logs the failed warning, the node MUST raise the counter `org.chronitondb.metrics:type=StartupChecksView,name=FailedSwitches` by one. Source: [quality-requirements.md](../../process/quality-requirements.md#observability) item 1.

REQ-SCV-022 (unwanted behaviour): If `nodetool enablestartupchecksview` or `nodetool disablestartupchecksview` runs against a node without the MBean `org.chronitondb:type=StartupChecksView`, then the command MUST print the missing MBean line and exit with a status other than 0. Source: problem 6.

REQ-SCV-023 (ubiquitous): The reference page `docs/reference/startup-checks-view.md` MUST contain each of these exact texts: `startup_checks_view_enabled`, `enablestartupchecksview`, `disablestartupchecksview`, the name of the view, each of the 15 always-run names, the four values of `source`, the three counter names and the text of the refusal. Source: stakeholder need, criterion 10, and problem 7.

REQ-SCV-024 (ubiquitous): `NEWS-chronitondb.txt` MUST contain the rollback sentence. Source: problem 2.

## 2. Decisions implemented

1. Decision record 0001, The first maintainers, 2026-11-01: the maintainers who approve this record. Nothing in it binds the design.
2. Decision record 0004, The commit log disk check is off by default, 2026-11-15: the one earlier decision on a default of a fork feature near startup checks. This feature is off by default too (REQ-SCV-001).
3. Decision record 0005, The commit log disk check is switched under `startup_checks`, 2026-11-15: that feature adds the constant `check_commitlog_shared_disk`. Rule 2 of section 1 gives the constant its row once its code is on the line. That record set aside the nodetool toggle for a startup check, which has run before nodetool can reach the node. The reason does not hold here: the view can be switched while the node runs, so this feature has its toggle.
4. The process pages, read on the line at commit `bc2208e8fe`: [branching-and-review.md, Feature switches and defaults](../../process/branching-and-review.md#feature-switches-and-defaults) items 1, 3 and 7, [quality-requirements.md](../../process/quality-requirements.md), [maintenance.md, The one-item path](../../process/maintenance.md#the-one-item-path), [conventions.md, Names](../../process/conventions.md#names) and [conventions.md, Code layout](../../process/conventions.md#code-layout).

As of 2026-11-15 the register on the line holds records 0001 to 0006. Records 0002 and 0003 are about `nodetool version`, and record 0006 is about how the commit log disk check compares directories. No newer record exists on startup checks, virtual tables or configuration.

Open points. Each is a choice an operator sees, so the maintainers decide it, and its answer becomes a decision record in this pull request. Until then the text follows the first option of each.

1. **Open point 1: where the view lives, and so who may read it.** The first option is `system_views.startup_checks`: the stock home of such tables, where an ordinary role needs `SELECT` granted on the table or on `system_views`. The second is a keyspace of the fork's own, where `SELECT` on all keyspaces is enough. A third, readable by every role with no grant, would edit `ClientState`, a file of authorisation.
2. **Open point 2: the names of the 15 always-run rows.** The first option is the names Apache Cassandra 6.0 gives those checks (section 4). The second puts `check_` in front of each, as the four switchable names have it. The third is the Java field names of this line.
3. **Open point 3: what `source` shows for a yaml entry without the key `enabled`.** Stock fills the key in before any fork code can run (section 4, stock item 5), so the view cannot tell such an entry from one that sets the key, without new code in the stock loader of the configuration. The first option shows `yaml` for every check that has a yaml entry. The second adds that code, which then runs at every node start, with the view on or off.

## 3. Stock behaviour preservation

This statement and the switch table below it follow the form of [section 2.8 of the feature spec template](../../process/templates/feature-spec.md#28-feature-class-and-switches), because a fork feature that fits one item has no feature spec.

Feature class: purely additive, because the view is reachable only through a table name and a setting that stock Apache Cassandra rejects, and no stock operation changes its result, its error, its warning or its cost (branching-and-review.md, Feature switches and defaults, item 3). A purely additive feature MAY be on by default. This one is off by default, as the maintainers confirmed in criterion 1.

| Switch | Class | Reason | Default per line | Stock operations it changes |
|---|---|---|---|---|
| `startup_checks_view_enabled` in `cassandra.yaml`, with `nodetool enablestartupchecksview` and `nodetool disablestartupchecksview` | purely additive | with the switch on, the node has one more virtual table, which stock does not have | `chronitondb-sandbox`: off | none. While on, the lists of tables that `system_virtual_schema.tables` and `DESCRIBE` show hold one more table |

Item 2 of the same list says a switch refuses to turn on before the feature's final milestone gate. A feature that fits one item has no milestone. As for the commit log disk check, the one code pull request of this item holds the whole feature, so no build of the line holds the switch before the feature is whole, and the switch needs no code that refuses it.

Row 1 of the table below applies only with the switch on. Rows 2 to 4 are presences on every node, switch on or off: a departure from [branching-and-review.md](../../process/branching-and-review.md#feature-switches-and-defaults) item 7, which says that with a feature off no new memory is used and stock operations behave as Apache's do. The maintainers approve each by merging this record.

| Stock behaviour today (file and line) | This change | Switch that controls it | Error text naming the switch |
|---|---|---|---|
| `system_views` holds the tables that the constructor of `SystemViewsKeyspace` lists (`src/java/org/apache/cassandra/db/virtual/SystemViewsKeyspace.java:32` to `58` at `bc2208e8fe`), and `system_virtual_schema.tables` and `DESCRIBE` show the tables of every registered virtual keyspace (`VirtualSchemaKeyspace.VirtualTables.data`, `src/java/org/apache/cassandra/db/virtual/VirtualSchemaKeyspace.java:87` at `bc2208e8fe`, and `DescribeStatement.java:142` at `bc2208e8fe`) | with the switch on, `system_views` holds one more table, `startup_checks`, and both lists show it. With the switch off both lists are stock's | `startup_checks_view_enabled`, in memory through `nodetool enablestartupchecksview` and `nodetool disablestartupchecksview` | `The startup checks view is off. Set startup_checks_view_enabled to true in cassandra.yaml, or run nodetool enablestartupchecksview.` for a read that reaches the view while the switch is off (REQ-SCV-014). A statement that names the table while it is not registered gets stock's own error for a table that does not exist |
| `system_views.settings` lists one row per `Config` field (`SettingsTable.getValue`, `SettingsTable.java:97` at `bc2208e8fe`), and the start log line `Node configuration:` prints every field (`Config.log`, `Config.java:1376` at `bc2208e8fe`) | both show one more entry, `startup_checks_view_enabled`, on every node | none: Apache's loader refuses a key without a `Config` field (`YamlConfigurationLoader.PropertiesChecker.check`, `src/java/org/apache/cassandra/config/YamlConfigurationLoader.java:423` at `bc2208e8fe`), so the yaml setting needs the field | none |
| `nodetool help` lists the commands of `NodeTool.execute` (`src/java/org/apache/cassandra/tools/NodeTool.java:98` to `246` at `bc2208e8fe`) | the list has two more entries, `enablestartupchecksview` and `disablestartupchecksview`, on every node | none: the toggle that branching-and-review.md item 1 requires is a command, and a command is listed | none |
| the JMX server holds Apache's MBeans and metrics only | one more MBean, `org.chronitondb:type=StartupChecksView`, and three more counters of the fork's own type `StartupChecksView` in the group `org.chronitondb.metrics`, exist on every node from the hook of section 3. Together one object and three counters, a few hundred bytes, allocated once. No stock metric changes | none: the MBean is the handle of the toggle, and holding it is how the view can be switched on while the node runs. The counters exist from registration, so that the metrics a node exports do not depend on which commands ran against it | none |

Everything else stays stock. `StartupChecks.java` is not edited, so which checks run, their order and what they log stay as they are (criterion 9). No code default in a stock class changes: the one field `Config` gains is new. No stock file under `conf/` changes. No file of authentication or authorisation changes. No test that exists on the line changes.

### Stock hook points

There is no feature spec for a one-item change, so the hook points are listed here with their delta entry, `docs/delta/startup-checks-view.md`.

1. `src/java/org/apache/cassandra/config/Config.java`: one field, `public volatile boolean startup_checks_view_enabled = false;`, after `startup_checks` at line 960. It is a field, not a hook that imports fork code, but it is a stock edit and so it is listed.
2. `src/java/org/apache/cassandra/service/CassandraDaemon.java`: one import and one line at the end of `CassandraDaemon.setupVirtualKeyspaces` (`CassandraDaemon.java:534` to `544` at `bc2208e8fe`), `StartupChecksView.instance.start();`. The call registers the MBean and the counters, and registers the view when the `Config` field is `true`. It never throws (REQ-SCV-016). The in-JVM distributed test framework calls the same method for each instance (`Instance.startup`, `test/distributed/org/apache/cassandra/distributed/impl/Instance.java:650` at `bc2208e8fe`), so its instances run the hook too.
3. `src/java/org/apache/cassandra/tools/NodeTool.java`: two imports and two entries in the command list (lines 98 to 246), `EnableStartupChecksView.class` and `DisableStartupChecksView.class`.

How the view is registered, under the first option of Open point 1. `VirtualKeyspaceRegistry.register` puts a keyspace into the registry and replaces one of the same name (`VirtualKeyspaceRegistry.register`, `src/java/org/apache/cassandra/db/virtual/VirtualKeyspaceRegistry.java:41` to `48` at `bc2208e8fe`). To switch on, the feature registers a `VirtualKeyspace` named `system_views` that holds the tables of `SystemViewsKeyspace.instance`, the same objects, and the view. To switch off, it registers `SystemViewsKeyspace.instance` again. No stock file is edited for it. The registry on this line has no call that removes a table, so after a switch off the view object stays reachable by its table id for a statement prepared earlier. REQ-SCV-014 covers that read.

The new package `org.chronitondb.startup` imports from `org.apache.cassandra.config`, `org.apache.cassandra.service`, `org.apache.cassandra.db.virtual`, `org.apache.cassandra.metrics`, `org.apache.cassandra.schema` and `org.apache.cassandra.exceptions`, all through public members. It needs no package private access to a stock package.

## 4. Prior art reviewed

Stock Apache Cassandra, read on this line at commit `bc2208e8fe`:

1. The daemon registers 19 checks: the 18 of `StartupChecks.DEFAULT_TESTS` (`StartupChecks.java:135` to `152` at `bc2208e8fe`) and `FileSystemOwnershipCheck` (`CassandraDaemon.CassandraDaemon`, `src/java/org/apache/cassandra/service/CassandraDaemon.java:220` at `bc2208e8fe`). A check says which constant of `StartupChecks.StartupCheckType` it is with `StartupCheck.getStartupCheckType`, whose default is `non_configurable_check` (`StartupCheck.getStartupCheckType`, `src/java/org/apache/cassandra/service/StartupCheck.java:54` to `57` at `bc2208e8fe`). Four checks override it. The other 15 are public static fields of `StartupChecks` with no name but the field's.
2. `StartupChecksOptions.apply` gives every constant an `enabled` value: `false` for a constant declared disabled by default, `true` for the others, and always `true` for `non_configurable_check` (`StartupChecksOptions.apply`, `src/java/org/apache/cassandra/config/StartupChecksOptions.java:81` to `96` at `bc2208e8fe`). `StartupChecksOptions.isEnabled` reads it (`StartupChecksOptions.java:66` to `69` at `bc2208e8fe`).
3. Every always-run check starts with `options.isDisabled(getStartupCheckType())`, which is never true for it. Two of them also return at once on a platform other than Linux (`StartupChecks.checkReadAheadKbSetting`, `StartupChecks.java:471` at `bc2208e8fe`, and `StartupChecks.checkMaxMapCount`, `StartupChecks.java:546` at `bc2208e8fe`), and `StartupChecks.checkKernelBug1057843` lets the start option `cassandra.ignore_kernel_bug_1057843_check` skip its test of the kernel version (`StartupChecks.java:211` to `215` at `bc2208e8fe`). The view shows whether a check is on, not what it found or skipped, so these rows stay `true` and `always_on`. The reference page says so.
4. Three start options override the yaml value of a switchable check. `StartupChecks.checkDatacenter` takes the opposite of `cassandra.ignore_dc` when the option is set (`StartupChecks.java:741` to `748` at `bc2208e8fe`). `StartupChecks.checkRack` does the same with `cassandra.ignore_rack` (`StartupChecks.java:778` to `785` at `bc2208e8fe`). `FileSystemOwnershipCheck.isEnabled` takes `cassandra.enable_fs_ownership_check` when it is set and the yaml value otherwise (`FileSystemOwnershipCheck.isEnabled`, `src/java/org/apache/cassandra/service/FileSystemOwnershipCheck.java:276` to `280` at `bc2208e8fe`). The keys are in `CassandraRelevantProperties` (`src/java/org/apache/cassandra/config/CassandraRelevantProperties.java:233`, `275` and `284` at `bc2208e8fe`). `check_data_resurrection` has no such option (`DataResurrectionCheck.execute`, `src/java/org/apache/cassandra/service/DataResurrectionCheck.java:169` at `bc2208e8fe`).
5. Stock builds the options once, while it loads the configuration: `DatabaseDescriptor.applyAll` calls `DatabaseDescriptor.applyStartupChecks` (`src/java/org/apache/cassandra/config/DatabaseDescriptor.java:475` and `1148` to `1151` at `bc2208e8fe`). The constructor of `StartupChecksOptions` copies the outer map of `Config.startup_checks` and keeps its inner maps, and `apply` then writes `enabled` into each inner map that lacks it (`StartupChecksOptions.java:43` to `47` and `81` to `96` at `bc2208e8fe`). So after the configuration is loaded, the entry of a check that the yaml named without `enabled` holds the key too. This was read and not run. Open point 3 rests on it.
6. A virtual table is a class with a `TableMetadata` and a `data` method, as `SystemPropertiesTable` is (`src/java/org/apache/cassandra/db/virtual/SystemPropertiesTable.java:36` to `61` at `bc2208e8fe`). A read finds the table in the registry by its table id (`PartitionRangeReadCommand.java:555` and `SinglePartitionReadCommand.java:1415` at `bc2208e8fe`). A table name is resolved through the keyspace metadata, which for a virtual keyspace comes from the registry (`Schema.getKeyspaceMetadata`, `src/java/org/apache/cassandra/schema/Schema.java:318` to `324` at `bc2208e8fe`).
7. Who may read. `system_views` is a system keyspace (`SchemaConstants.VIRTUAL_SYSTEM_KEYSPACE_NAMES`, `src/java/org/apache/cassandra/schema/SchemaConstants.java:63` to `64` at `bc2208e8fe`). For an ordinary role, a permission on a system keyspace must be granted on that keyspace or its table, and a grant on all keyspaces does not count (`ClientState.ensurePermission`, `src/java/org/apache/cassandra/service/ClientState.java:485` to `499` at `bc2208e8fe`). The tables of `system_virtual_schema` are readable with no grant, because `ClientState.READABLE_SYSTEM_RESOURCES` names them (`ClientState.java:72` to `93` and `463` at `bc2208e8fe`). With authorisation off, every role reads every table.
8. `system_views.system_properties` already shows the start options a node was started with, and `system_views.settings` the yaml block. An operator can combine the two today, and must still know each default, each override rule and which checks exist. The view does that work.
9. A stock toggle has commands named `enable` and `disable` with the thing, such as `enablebackup` and `disablebackup` (`NodeTool.java:116` and `127` at `bc2208e8fe`), and a fork command reaches its MBean through `NodeProbe.getMbeanServerConn` (`src/java/org/apache/cassandra/tools/NodeProbe.java:772` at `bc2208e8fe`).

Apache `cassandra-6.0` and trunk, read from `apache/cassandra` at commit `84bca651ef` (`cassandra-6.0`) and `2249e37b51` (trunk):

1. CASSANDRA-21093, "Custom startup checks plugin", fixed in 6.0, gave every check a name. `StartupCheck.name` returns "the name of a startup check, as it would appear in the configuration" (`StartupCheck.java:44` at `2249e37b51`). The always-run checks this line shares with 6.0 are named `kernel_bug_1057843`, `jemalloc`, `lz4_native`, `valid_launch_date`, `jmx_ports`, `jmx_properties`, `jvm_options`, `native_library_initialization`, `read_ahead_kb_setting`, `max_map_count`, `data_dirs`, `sstables_format`, `system_keyspace_state` and `legacy_auth_tables` (`StartupChecks.java:242` to `934` at `84bca651ef`). The switchable checks keep their yaml names, such as `check_filesystem_ownership` (`FileSystemOwnershipCheck.name`, `FileSystemOwnershipCheck.java:115` to `118` at `2249e37b51`).
2. The fifteenth always-run check of this line, `StartupChecks.initSigarLibrary`, warns when the node runs in a degraded mode (`StartupChecks.java:422` to `431` at `bc2208e8fe`). 6.0 has no Sigar library. Its check for the same warning is `StartupChecks.checkProcessEnvironment`, named `process_environment` (`StartupChecks.java:513` to `531` at `84bca651ef`).
3. 6.0 can also list the registered checks, `StartupChecks.getChecks` (`StartupChecks.java:143` to `146` at `2249e37b51`), and remove a virtual keyspace, `VirtualKeyspaceRegistry.unregister` (`VirtualKeyspaceRegistry.java:51` to `59` at `2249e37b51`). This line has neither.
4. Neither branch has a virtual table of startup checks: no table of `SystemViewsKeyspace` at `2249e37b51` is about them.

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
3. **The view in `system_views`, named `startup_checks`.** Open point 1. Stock match: the home of `settings` and `system_properties`, and the name of the yaml block. Idiom: stock.
4. **Three columns, `name`, `enabled` and `source`.** Stock match: `name` is the key of `settings` and `system_properties`, and `enabled` is the key stock uses under `startup_checks`. Stock has no `source` column. Earlier decision match: none. Idiom: CQL.
5. **The values of `source`: `default`, `yaml`, `system_property` and `always_on`.** Stock match: stock calls a start option a system property, in the table `system_properties` and in the warning of `StartupChecks.checkDatacenter`. Lower case words joined by `_`, as stock names are. Earlier decision match: none. Idiom: stock.
6. **The names of the 15 always-run rows.** Open point 2.
7. **A refusal that names the switch.** Stock match: none, stock has no switched table. Earlier decision match: branching-and-review.md item 7. Idiom: the fork's.
8. **The counters `Reads`, `RefusedReads` and `FailedSwitches` of the type `StartupChecksView`, and the MBean `org.chronitondb:type=StartupChecksView`.** Stock match: Dropwizard counters through `CassandraMetricsRegistry`. Earlier decision match: conventions.md, Names, items 3 and 4. Idiom: a counter named for what it counts.

## 6. Quality requirements

| ISO/IEC 25010 characteristic | Line | Requirements, or the reason it does not apply |
|---|---|---|
| Performance efficiency | Fastest correct design, with benchmarks in the design and in the gates | Does not apply, because the only request that runs the code is a read of the view, which builds at most one row for each check from values already in memory. Section 7. |
| Performance efficiency | Memory budgets on coordinator and replica | Does not apply, because the feature holds one MBean, three counters and, while on, one table object. A read allocates about 20 small rows. |
| Reliability | Isolation levers on coordinator and replica: thread pools, limits, load shedding, timeouts, kill switch | REQ-SCV-001, REQ-SCV-006 and REQ-SCV-014: the kill switch is the setting and its toggle. No thread, pool or limit exists, because a read runs on the thread that serves the query and does no IO. |
| Reliability | Automatic fallbacks opt-in, with yaml setting, nodetool toggle, metric and rate-limited log line | Does not apply, because there is no fallback. |
| Reliability | Coordination between nodes model checked, when the design changes it | Does not apply, because each node answers for itself and nothing crosses the network. |
| Compatibility | Stock Apache Cassandra behaviour unchanged | REQ-SCV-001 and REQ-SCV-002. Section 3: the one change behind the switch and the three presences, each with its reason. |
| Compatibility | Stock behaviour unchanged with the feature off | REQ-SCV-002 and REQ-SCV-014. The stock suites of section 14 run unchanged with the switch at its default, off. |
| Compatibility | Mixed-version cluster, upgrade and rollback (see the Compatibility section) | REQ-SCV-024 and section 9. |
| Functional suitability | CQL validity and results independent of replication factor, data centres and replica count | Met: a virtual table is local to the node that serves the query, and its rows come from that node's configuration only. |
| Flexibility | Settings per index or per table over global ones, with global, include and exclude modes | Does not apply, because the setting is a property of the node, not of data. |
| Interaction capability | nodetool toggles change the in-memory value only, yaml holds the startup value | REQ-SCV-004 to REQ-SCV-006: the commands change the `Config` field in memory, and a restart returns to the yaml value. |
| Interaction capability | Error messages name the setting or toggle that controls the behaviour | REQ-SCV-014 and REQ-SCV-017. |
| Maintainability | Observability: metrics, traces and diagnostics as a gate item | REQ-SCV-007, REQ-SCV-017 and REQ-SCV-019 to REQ-SCV-021. Section 8. |
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
| A read of the view | rows built | none, the table does not exist | one row for each check, 19 today | one lookup in an `EnumMap` and at most one system property read for each switchable check |
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

1. **Counted.** Three counters of the type `StartupChecksView`, registered by the hook at node start. `org.chronitondb.metrics:type=StartupChecksView,name=Reads` rises by one for each read the view serves (REQ-SCV-019). `org.chronitondb.metrics:type=StartupChecksView,name=RefusedReads` rises by one for each read refused because the switch is off (REQ-SCV-020). `org.chronitondb.metrics:type=StartupChecksView,name=FailedSwitches` rises by one for each failed warning (REQ-SCV-021).
2. **Timed.** Nothing: a read does no IO and has no duration worth a timer.
3. **Logged.** A change of the switch by nodetool, at INFO, with the old and the new value (REQ-SCV-007). Its text: `The startup checks view setting startup_checks_view_enabled changed from {} to {}.` The failed warning, at WARN, with the exception as the last logging argument (REQ-SCV-017). Its text: `The startup checks view could not be switched to {}. The setting startup_checks_view_enabled stays at {}.` Nothing is logged for a read.
4. **Traced.** Nothing of its own: a read makes no plan decision and has no fallback. A traced read shows the stock trace lines of a virtual table read.
5. **Client visible.** The rows, and the refusal of REQ-SCV-014.
6. **Exposed.** The MBean `org.chronitondb:type=StartupChecksView`, with the attribute `Enabled` and the operations `enable` and `disable`. The three counters over JMX and through any configured metrics reporter. The switch also shows in the row `startup_checks_view_enabled` of `system_views.settings`, at its running value, because the toggle writes the `Config` field.
7. **Toggled.** In `cassandra.yaml`, read at start, and with the two nodetool commands, in memory only.
8. **Audited.** Nothing of its own. A read of the view is a `SELECT`, which the stock audit log records as any other when it is on.
9. **Released on drop.** The view is released when the switch goes off. The MBean and the counters live as long as the node.
10. **Documented.** The reference page of section 13 lists every name (REQ-SCV-023).
11. **Tested.** Section 14.

No line above TRACE carries a key, a term, a literal or a secret: the two lines carry `true` or `false`.

## 9. Compatibility

1. **On-disk format changes.** None. The feature writes no file.
2. **Mixed-version cluster.** Does not apply to behaviour between nodes: each node holds its own view, and nothing crosses the network. A client that reads the view on every node gets stock's error for a missing table from a node without the feature or with the switch off.
3. **Upgrade path and prerequisites.** None. A `cassandra.yaml` that does not set the key loads on every binary.
4. **Rollback path.** An operator who wrote `startup_checks_view_enabled` into `cassandra.yaml` MUST remove it before starting an Apache Cassandra binary or a ChronitonDB build older than this change on that node. Such a binary refuses a key it does not know (`YamlConfigurationLoader.PropertiesChecker.check`, `YamlConfigurationLoader.java:423` at `bc2208e8fe`). REQ-SCV-024 puts the rollback sentence in `NEWS-chronitondb.txt`, and the reference page carries it.
5. **Runbook entries.** No runbook exists on this line. The rollback sentence lives on the reference page and in `NEWS-chronitondb.txt`.
6. **Surfaces touched.** Configuration: one new key. Command line tools: two new nodetool commands. JMX and metrics: one MBean and three counters. Virtual tables: one table, with the switch on only. No version of any surface is bumped.
7. **Shared state.** The switch writes nothing to shared state, off or on. The view is not in the schema that nodes exchange.
8. **The other line.** The item carries one line label, `chronitondb-sandbox`. On a 6.0 line the names come from `StartupCheck.name` and the list from `StartupChecks.getChecks` (section 4). That port is section 15 item 1.

## 10. Threat model and security

One new entry point: a CQL read of the view. Its only input is the statement, which the stock parser and the stock virtual table code handle. The view parses nothing of its own. The two nodetool commands take no argument and reach the node over JMX, under the stock JMX authentication and authorisation.

By STRIDE:

1. **Spoofing, tampering, repudiation.** Do not apply: the view is read only, takes no write and changes no data. A read is in the stock audit log when that is on.
2. **Information disclosure.** A row tells a reader which checks a node runs, among them whether the ownership check and the data resurrection check are on. The view shows no other setting of a check (REQ-SCV-009), so the ownership token never appears. The stock tables `settings` and `system_properties` already show the same facts, and the token, to a role that may read `system_views`. The permission the view needs is `SELECT` on the table, by the stock rule of its keyspace (Open point 1), with the negative test of REQ-SCV-015. The feature edits no file of authentication or authorisation.
3. **Denial of service.** A read builds about 20 rows from memory. It holds no lock that a stock path takes. The hook at start never throws (REQ-SCV-016).
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
7. Failure behaviour: a read while the switch is off is refused. A node without the MBean answers the nodetool commands with the missing MBean line. A read never times out on IO, because it does none. Coordinator failure, a missing replica, a limit and an index that is not built do not apply, because the view is local.
8. Known limitations. A row says whether a check is on, not what it found. Two always-run checks do nothing on a platform other than Linux, and `cassandra.ignore_kernel_bug_1057843_check` skips part of one. The limit of Open point 3. The view is local: each node answers for itself.
9. The rollback sentence.

`NEWS-chronitondb.txt` gains an entry for the view and the rollback sentence (REQ-SCV-024). The delta entry `docs/delta/startup-checks-view.md` with its row in `docs/delta/README.md` records the stock edits and the presences of section 3.

Apache's `conf/cassandra.yaml` stays untouched. `conf/cassandra_chronitondb.yaml` does not exist on this line, see section 15 item 3.

## 14. Testing

Five unit test classes and one in-JVM distributed test class. The distributed test starts one node. Nothing is multi node in behaviour, so replication factor does not apply. No sstable format or compaction is touched. The parity suite does not exist on this line yet, see waiver 1. This item adds no scenario, under waiver 2, so the template's `Scenario runner` and `Scenario tags` lines are left out.

What each test of the list under Tests for this change proves:

1. `StartupCheckRowsTest.oneRowForEachCheck`: the rows hold the 15 always-run names and one row for each constant of `StartupCheckType` other than `non_configurable_check`, and no other row (REQ-SCV-008).
2. `StartupCheckRowsTest.alwaysRunRows`: each of the 15 rows shows `true` and `always_on` (REQ-SCV-010).
3. `StartupCheckRowsTest.defaultRows`: with the options of `new StartupChecksOptions()` and no start option, `check_dc` and `check_rack` show `true` and `default`, and `check_filesystem_ownership` and `check_data_resurrection` show `false` and `default` (REQ-SCV-011).
4. `StartupCheckRowsTest.yamlRows`: with options built from a map that sets `enabled` to `false` for `check_dc` and to `true` for `check_data_resurrection`, the two rows show those values and `yaml`, and the other two still show `default` (REQ-SCV-012).
5. `StartupCheckRowsTest.systemPropertyRows`: with `cassandra.ignore_dc` set to `true`, `check_dc` shows `false` and `system_property`. With it set to `false`, `true` and `system_property`. The same for `cassandra.ignore_rack` and `check_rack`. With `cassandra.enable_fs_ownership_check` set to `true`, `check_filesystem_ownership` shows `true` and `system_property`, and the row's `enabled` equals what `FileSystemOwnershipCheck.isEnabled` returns for the same options. Each case also sets the opposite value in the options, to prove that the start option wins (REQ-SCV-013).
6. `StartupCheckRowsTest.everyRegisteredCheckHasAName`: the test reads the list of checks that `new StartupChecks().withDefaultTests()` holds and asserts that every check of type `non_configurable_check` in it is one of the 15 the fixed list names, and that the fixed list names no other. An import that adds an always-run check fails here (REQ-SCV-018).
7. `StartupChecksViewTest.offByDefault`: `new Config().startup_checks_view_enabled` is `false` (REQ-SCV-001).
8. `StartupChecksViewTest.notListedWhileOff` and `listedWhileOn`: a `SELECT` on `system_virtual_schema.tables` finds no row for the view before `enable`, one row after it, and none after `disable` (REQ-SCV-002, REQ-SCV-003).
9. `StartupChecksViewTest.columns`: the metadata of the view has exactly the columns `name`, `enabled` and `source` (REQ-SCV-009).
10. `StartupChecksViewTest.toggleLogsOldAndNew`: `enable` on a view that is off logs the INFO line with `false` and `true`, and `disable` logs it with `true` and `false` (REQ-SCV-005, REQ-SCV-006, REQ-SCV-007).
11. `StartupChecksViewTest.readWhileOffIsRefused`: a statement prepared while the switch is on, executed after `disable`, fails with an invalid request whose message is the refusal text, and `RefusedReads` rose by one (REQ-SCV-014, REQ-SCV-020).
12. `StartupChecksViewTest.countsReads`: `Reads` rose by one after one `SELECT` of the view (REQ-SCV-019).
13. `StartupChecksViewTest.startNeverThrows`: with a registration that throws `IllegalStateException`, `start` returns, the log holds the failed warning, the `Config` field is `false` and `FailedSwitches` rose by one (REQ-SCV-016, REQ-SCV-017, REQ-SCV-021).
14. `StartupChecksViewAuthTest.readNeedsSelect`: with authentication and authorisation on, a role with no grant is refused as unauthorised, and the same role reads the view after `GRANT SELECT` on it (REQ-SCV-015).
15. `StartupChecksViewCommandsTest.missingMBean`: each command, run against a probe whose MBean server has no `org.chronitondb:type=StartupChecksView`, prints the missing MBean line and returns a status other than 0 (REQ-SCV-022).
16. `StartupChecksViewStartTest.yamlSwitchesTheViewOn`: an in-JVM cluster of one node configured with `startup_checks_view_enabled` set to `true` starts, and a `SELECT` of the view returns 19 rows (REQ-SCV-004, and criteria 2 and 3 end to end).
17. `StartupChecksViewStartTest.defaultNodeHasNoView`: an in-JVM cluster of one node with the default configuration starts, `system_virtual_schema.tables` has no row for the view, and a `SELECT` of it fails with stock's error for a table that does not exist (REQ-SCV-002 end to end).
18. `StartupChecksViewDocsTest.exactNamesAreDocumented` and `rollbackLineInNews`: the reference page contains each text of REQ-SCV-023, and `NEWS-chronitondb.txt` contains the rollback sentence (REQ-SCV-023, REQ-SCV-024).

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
2. The row of the commit log disk check. Its constant is not on the line yet. Rule 2 of section 1 gives it a row when its code merges, with no change here. Its code pull request SHOULD add the name to the reference page of this feature if this feature merged first.
3. `conf/cassandra_chronitondb.yaml` does not exist on this line. When the item that creates it lands, the setting goes into it, commented out with its default. Candidate issue.
4. `VirtualKeyspaceRegistry.register` removes the tables of a replaced keyspace by the table object, from a map keyed by table id, so it removes none (`VirtualKeyspaceRegistry.java:46` at `bc2208e8fe`). Apache trunk removes by id (`VirtualKeyspaceRegistry.java:42` to `49` at `2249e37b51`). This design does not depend on a fix and does not make one. Candidate for an import.
5. The scenarios of the feature `SCV`, once the scenario module `test/bdd/` exists on the line, see waiver 2.
6. `NEWS-chronitondb.txt` and `docs/reference/` do not exist on the line today. The design records of the release version feature and of the commit log disk check plan to create both. The Planned file list names `NEWS-chronitondb.txt` as `new`. If one of those merges first, the word becomes `edit`, through change control.

## New terms

1. **The switch**: the value of the field `Config.startup_checks_view_enabled` of the running node. On when `true`. In yaml `startup_checks_view_enabled`, in nodetool `enablestartupchecksview` and `disablestartupchecksview`, in docs "the startup checks view setting".
2. **The view**: the virtual table of this feature, `system_views.startup_checks` under the first option of Open point 1. In code `org.chronitondb.startup.StartupChecksTable`, in docs "the startup checks view". Key `SCV`.
3. **An always-run check**: a check the daemon registers whose `StartupCheck.getStartupCheckType` returns `non_configurable_check`. On this line the 15 fields of `StartupChecks`: `checkKernelBug1057843`, `checkJemalloc`, `checkLz4Native`, `checkValidLaunchDate`, `checkJMXPorts`, `checkJMXProperties`, `inspectJvmOptions`, `checkNativeLibraryInitialization`, `initSigarLibrary`, `checkMaxMapCount`, `checkReadAheadKbSetting`, `checkDataDirs`, `checkSSTablesFormat`, `checkSystemKeyspaceState` and `checkLegacyAuthTables`.
4. **A switchable check**: a constant of `StartupChecks.StartupCheckType` other than `non_configurable_check`. On this line `check_filesystem_ownership`, `check_dc`, `check_rack` and `check_data_resurrection`.
5. **A start option**: a Java system property the node was started with. A start option is set when `CassandraRelevantProperties.isPresent` is true for it.
6. **A yaml entry**: a key for the check in the map `Config.startup_checks` of the running node.
7. **The failed warning**: the WARN line of section 8, item 3.
8. **The missing MBean line**: this exact text: `This node has no startup checks view: the MBean org.chronitondb:type=StartupChecksView was not found.`
9. **The rollback sentence**: this exact text, on one line: `Before a node runs an Apache Cassandra binary, or a ChronitonDB build older than this feature, remove startup_checks_view_enabled from its cassandra.yaml.`

## Where problems could occur

1. **A node does not start.** Seen by an operator as a node that exits during startup, on every node, if the hook in `CassandraDaemon.setupVirtualKeyspaces` throws. From `StartupChecksView.start`. REQ-SCV-016 makes it return normally whatever `Exception` is thrown, and REQ-SCV-017 logs it.
2. **A node rolled back to an Apache Cassandra binary, or to an older ChronitonDB build, does not start.** Seen as a node that refuses its `cassandra.yaml` with `Invalid yaml. Please remove properties`, on a node whose operator wrote the key into the yaml. From the new key. Not from the default.
3. **A node that switched the view off still serves it.** Seen as rows from a table that the node no longer lists, for a statement prepared while the switch was on. From the registry, which keeps the table by its id. REQ-SCV-014.
4. **A role reads the view that should not.** Seen as a role with no grant that learns which checks a node runs. From the place the view is registered in. REQ-SCV-015.
5. **A row is wrong or missing.** Seen by an operator as a check shown on that is off, a source that is not the real one, or a check the node runs that has no row, so that the operator trusts a wrong picture of the node. From the rules of section 1, from a start option the view does not know, or from an import that adds a check. REQ-SCV-008 and REQ-SCV-010 to REQ-SCV-013, and REQ-SCV-018 for the import.
6. **A nodetool command fails without a reason.** Seen as a stack trace from `nodetool enablestartupchecksview` against an Apache Cassandra node or an older build. From the lookup of the MBean. REQ-SCV-022.
7. **The page names the setting, a command, a row or a counter wrongly.** Seen as a documented name the node does not know. From a page written by hand. REQ-SCV-023.
8. **The stock tables of `system_views` break on a node that switched the view on.** Seen as a stock table of `system_views` that is missing or fails after `nodetool enablestartupchecksview`. From the registration of a second `system_views` keyspace object, under the first option of Open point 1.
9. **Every in-JVM distributed test fails to start its instances.** Seen by a developer as an error at instance start in every in-JVM test, with the switch off too. From the hook call, if the in-JVM test framework loads the fork class once for all instances. Not seen on a real node.

### Test plan

1. Problem 1: `StartupChecksViewTest.startNeverThrows`, and the stock suites that start a daemon run unchanged.
2. Problem 2: no test on this line can start an Apache binary. `StartupChecksViewDocsTest.rollbackLineInNews` proves the rollback sentence is in the news file. Watched through the reference page.
3. Problem 3: `StartupChecksViewTest.readWhileOffIsRefused`.
4. Problem 4: `StartupChecksViewAuthTest.readNeedsSelect`.
5. Problem 5: the six tests of `StartupCheckRowsTest`.
6. Problem 6: `StartupChecksViewCommandsTest.missingMBean`.
7. Problem 7: `StartupChecksViewDocsTest.exactNamesAreDocumented`.
8. Problem 8: `StartupChecksViewTest.listedWhileOn` also reads `system_views.settings` after `enable` and after `disable`, and `SettingsTableTest` and `SystemPropertiesTableTest` run unchanged.
9. Problem 9: `DataResurrectionCheckTest`, unchanged, and `StartupChecksViewStartTest.defaultNodeHasNoView` start instances through the hook call.

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

The three stock files carry the hook points of section 3 and nothing else. `StartupChecksView` holds the switch, the MBean, the counters and the two log lines. `StartupChecksTable` is the virtual table. `StartupCheckRows` works out the rows by the rules of section 1. The two commands toggle the switch. The coverage file next to this record is not in the list. No protected path and no library file is in the list.

The open pull requests were listed on 2026-11-15: there is none. The merged design record of the release version feature plans edits to `Config.java` and `NodeTool.java` too, and both merged records plan `NEWS-chronitondb.txt` and `docs/delta/README.md`. Their code pull requests are not open yet.

### Shared with open items

None.

### Waivers

1. Exit criterion 4 of [testing.md](../../process/testing.md#exit-criteria), the parity suite passes with every fork feature off. The parity suite does not exist on this line. In its place the stock suites of section 14 run unchanged with the switch at its default, off. Waived because there is no parity suite to run. The maintainers approve the waiver with this record.
2. [testing.md, Scenarios](../../process/testing.md#scenarios) item 6: the designer writes the scenarios of a feature item in this pull request, tagged `@wip`. Waived because nothing that runs a scenario exists on this line: no `test/bdd/` module, no shared step library and no Cucumber runner. Every requirement is proven instead by a JUnit test named in `ac-coverage.md`. The maintainers approve the waiver with this record.

## Requirement quality checklist (ISO/IEC/IEEE 29148)

This version is a draft with three open points, so the check of REQ-SCV-001 to REQ-SCV-024 against the seven qualities is not done yet. It is done, and this section rewritten, before the record goes to review.

1. **Necessary:** to check.
2. **Unambiguous:** to check.
3. **Singular:** to check.
4. **Verifiable:** to check.
5. **Feasible:** to check.
6. **Consistent:** to check.
7. **Traceable:** to check.
