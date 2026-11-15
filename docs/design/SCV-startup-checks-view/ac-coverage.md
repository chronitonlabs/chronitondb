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

# Acceptance coverage for #117

Location: next to its design record, in `docs/design/SCV-startup-checks-view/`, the directory of the fork feature with the key `SCV`. Process: [testing.md](../../process/testing.md).

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in BCP 14 (RFC 2119, RFC 8174) when, and only when, they appear in all capitals, as shown here.

## Contents

- [Coverage](#coverage)

## Coverage

This item is a fork feature that fits one item, with the key `SCV`. It adds no scenario, under waiver 2 of the design record's Waivers, so every requirement has one row naming its JUnit test. "Criterion n" is item n of the acceptance criteria in section 1 of the record, and "problem n" is item n of its Where problems could occur.

The acceptance criteria. Criterion 1 is covered by REQ-SCV-001, REQ-SCV-002 and REQ-SCV-031. Rows 2 to 4 of the departures table in section 3 of the record are what criterion 2 needs on a node with the switch off: the setting's field, the two commands and the MBean. Criterion 2 by REQ-SCV-003 to REQ-SCV-007. Criterion 3 by REQ-SCV-008 and REQ-SCV-018. Criterion 4 by REQ-SCV-009 and REQ-SCV-027. Criterion 5 by REQ-SCV-010 to REQ-SCV-013. Criterion 6 by REQ-SCV-010 and REQ-SCV-025. Criterion 7 by REQ-SCV-013 and REQ-SCV-026. Criterion 8 by REQ-SCV-009. Criterion 9 by REQ-SCV-035 for the list of checks the daemon registers, and by REQ-SCV-032 for a node with the switch on against one with it off. What a check logs has no test: the record's section 14 says why, under Criterion 9 in three parts. Criterion 10 by REQ-SCV-007, REQ-SCV-017, REQ-SCV-019 to REQ-SCV-021 and REQ-SCV-023.

The problems. Problem 1 is covered by REQ-SCV-016 and REQ-SCV-017. Problem 2 by REQ-SCV-024. Problem 3 by REQ-SCV-014. Problem 4 by REQ-SCV-015. Problem 5 by REQ-SCV-008, REQ-SCV-010 to REQ-SCV-013, REQ-SCV-018 and REQ-SCV-025 to REQ-SCV-027. Problem 6 by REQ-SCV-022 and REQ-SCV-028. Problem 7 by REQ-SCV-023. Problem 8 by REQ-SCV-033 and REQ-SCV-034. Problem 9 by REQ-SCV-016 and by the in-JVM tests that item 9 of the record's Test plan names. Problem 10 by REQ-SCV-017, REQ-SCV-029 and REQ-SCV-030.

| Id | Source | Requirement | Covering scenario | Test | Status |
|---|---|---|---|---|---|
| REQ-SCV-001 | stakeholder need, criterion 1 | When a node whose `cassandra.yaml` does not set `startup_checks_view_enabled` starts, the switch MUST be off. | none | `org.chronitondb.startup.test.StartupChecksViewStartTest.defaultNodeHasNoView` | Covered |
| REQ-SCV-002 | stakeholder need, criterion 1 | While the switch is off, the node MUST NOT list the view in `system_virtual_schema.tables`. | none | `org.chronitondb.startup.StartupChecksViewTest.notListedWhileOff` | Covered |
| REQ-SCV-003 | stakeholder need, criterion 2 | While the switch is on, the node MUST list the view in `system_virtual_schema.tables`. | none | `org.chronitondb.startup.StartupChecksViewTest.listedWhileOn` | Covered |
| REQ-SCV-004 | stakeholder need, criterion 2 | When a node whose `cassandra.yaml` sets `startup_checks_view_enabled` to `true` starts, the switch MUST be on, unless the hook is a failed switch. | none | `org.chronitondb.startup.test.StartupChecksViewStartTest.yamlSwitchesTheViewOn` | Covered |
| REQ-SCV-005 | stakeholder need, criterion 2 | When `nodetool enablestartupchecksview` runs against a node, the node MUST set the switch on, unless the MBean operation is a failed switch. | none | `org.chronitondb.startup.StartupChecksViewTest.toggleLogsOldAndNew` | Covered |
| REQ-SCV-006 | stakeholder need, criterion 2 | When `nodetool disablestartupchecksview` runs against a node, the node MUST set the switch off. | none | `org.chronitondb.startup.StartupChecksViewTest.toggleLogsOldAndNew` | Covered |
| REQ-SCV-007 | quality-requirements.md item 3 | When `start`, `enable` or `disable` ends with the `Config` field at another value than at its entry, the node MUST log the changed line. | none | `org.chronitondb.startup.StartupChecksViewTest.toggleLogsOldAndNew` | Covered |
| REQ-SCV-008 | stakeholder need, criterion 3 | While the switch is on, the set of names that a `SELECT` of every row of the view returns MUST equal the set of names of the checks of the node. | none | `org.chronitondb.startup.test.StartupChecksViewStartTest.yamlSwitchesTheViewOn` | Covered |
| REQ-SCV-009 | stakeholder need, criteria 4 and 8 | The columns of the view MUST be exactly `name`, `enabled` and `source`. | none | `org.chronitondb.startup.StartupChecksViewTest.columns` | Covered |
| REQ-SCV-010 | stakeholder need, criterion 6 | The row of an always-run check MUST show `source` as `always_on`. | none | `org.chronitondb.startup.StartupCheckRowsTest.alwaysRunRows` | Covered |
| REQ-SCV-011 | stakeholder need, criterion 5 | The row of a switchable check whose start option is not set and that has no yaml entry MUST show `source` as `default`. | none | `org.chronitondb.startup.StartupCheckRowsTest.defaultRows` | Covered |
| REQ-SCV-012 | stakeholder need, criterion 5, and decision record 0009 | The row of a switchable check whose start option is not set and that has a yaml entry MUST show `source` as `yaml`. | none | `org.chronitondb.startup.StartupCheckRowsTest.yamlRows` | Covered |
| REQ-SCV-013 | stakeholder need, criterion 7 | The row of a switchable check whose start option is set MUST show `source` as `system_property`. | none | `org.chronitondb.startup.StartupCheckRowsTest.systemPropertyRows` | Covered |
| REQ-SCV-014 | problem 3 and branching-and-review.md item 7 | If the view is read while the switch is off, then the node MUST refuse the read with an invalid request error whose message is the refusal text. | none | `org.chronitondb.startup.StartupChecksViewTest.readWhileOffIsRefused` | Covered |
| REQ-SCV-015 | problem 4 and decision record 0007 | If a role without the `SELECT` permission on the view reads it on a node with authorisation on, then the node MUST refuse the read as unauthorised. | none | `org.chronitondb.startup.StartupChecksViewAuthTest.readNeedsSelect` | Covered |
| REQ-SCV-016 | problem 1 | If the hook at node start is a failed switch, then the hook MUST return normally. | none | `org.chronitondb.startup.StartupChecksViewTest.startNeverThrows` | Covered |
| REQ-SCV-017 | problem 1 | If a failed switch happens, then the node MUST log the failed warning. | none | `org.chronitondb.startup.StartupChecksViewTest.failedSwitch` | Covered |
| REQ-SCV-018 | stakeholder need, criterion 3, problem 5 and decision record 0008 | The fixed list of always-run names MUST hold a name for every check of type `non_configurable_check` that the daemon registers. | none | `org.chronitondb.startup.StartupCheckRowsTest.everyRegisteredCheckHasAName` | Covered |
| REQ-SCV-019 | quality-requirements.md item 1 | When the view serves a read, the node MUST raise the counter `org.chronitondb.metrics:type=StartupChecksView,name=Reads` by one. | none | `org.chronitondb.startup.StartupChecksViewTest.countsReads` | Covered |
| REQ-SCV-020 | quality-requirements.md item 1 | When the view refuses a read because the switch is off, the node MUST raise the counter `org.chronitondb.metrics:type=StartupChecksView,name=RefusedReads` by one. | none | `org.chronitondb.startup.StartupChecksViewTest.readWhileOffIsRefused` | Covered |
| REQ-SCV-021 | quality-requirements.md item 1 | If a failed switch happens and the counter `org.chronitondb.metrics:type=StartupChecksView,name=FailedSwitches` exists, then the node MUST raise that counter by one. | none | `org.chronitondb.startup.StartupChecksViewTest.failedSwitch` | Covered |
| REQ-SCV-022 | problem 6 | If `nodetool enablestartupchecksview` or `nodetool disablestartupchecksview` runs against a node without the MBean `org.chronitondb:type=StartupChecksView`, then the command MUST print the missing MBean line. | none | `org.chronitondb.tools.nodetool.StartupChecksViewCommandsTest.missingMBean` | Covered |
| REQ-SCV-023 | stakeholder need, criterion 10, and problem 7 | The reference page `docs/reference/startup-checks-view.md` MUST contain each of these exact texts: `startup_checks_view_enabled`, `enablestartupchecksview`, `disablestartupchecksview`, `system_views.startup_checks`, each of the 15 always-run names, the four values of `source`, the three counter names and the refusal text. | none | `org.chronitondb.startup.StartupChecksViewDocsTest.exactNamesAreDocumented` | Covered |
| REQ-SCV-024 | problem 2 | The file `NEWS-chronitondb.txt` MUST contain the rollback sentence. | none | `org.chronitondb.startup.StartupChecksViewDocsTest.rollbackLineInNews` | Covered |
| REQ-SCV-025 | stakeholder need, criterion 6 | The row of an always-run check MUST show `enabled` as `true`. | none | `org.chronitondb.startup.StartupCheckRowsTest.alwaysRunRows` | Covered |
| REQ-SCV-026 | stakeholder need, criterion 7 | The row of a switchable check whose start option is set MUST show `enabled` as the value the start option gives. | none | `org.chronitondb.startup.StartupCheckRowsTest.systemPropertyRows` | Covered |
| REQ-SCV-027 | stakeholder need, criterion 4 | The row of a switchable check whose start option is not set MUST show `enabled` as the value `StartupChecksOptions.isEnabled` returns for the check. | none | `org.chronitondb.startup.StartupCheckRowsTest.enabledWithoutStartOption` | Covered |
| REQ-SCV-028 | problem 6 | If `nodetool enablestartupchecksview` or `nodetool disablestartupchecksview` runs against a node without the MBean `org.chronitondb:type=StartupChecksView`, then the command MUST exit with a status other than 0. | none | `org.chronitondb.tools.nodetool.StartupChecksViewCommandsTest.missingMBean` | Covered |
| REQ-SCV-029 | problem 10 | If the MBean operation of `nodetool enablestartupchecksview` or `nodetool disablestartupchecksview` is a failed switch, then the command MUST exit with a status other than 0. | none | `org.chronitondb.tools.nodetool.StartupChecksViewCommandsTest.failedSwitchStatus` | Covered |
| REQ-SCV-030 | problem 10 | If a failed switch happens, then the switch MUST be off afterwards. | none | `org.chronitondb.startup.StartupChecksViewTest.failedSwitch` | Covered |
| REQ-SCV-031 | stakeholder need, criterion 1 | While the switch is off, each of the statements `DESCRIBE TABLES`, `DESCRIBE FULL SCHEMA`, `DESCRIBE KEYSPACE system_views` and `DESCRIBE TABLE system_views.startup_checks` MUST give the result it gives on a node that never switched the view on. | none | `org.chronitondb.startup.StartupChecksViewTest.describeUnchangedWhileOff` | Covered |
| REQ-SCV-032 | stakeholder need, criterion 9 | The startup check run of a node, which is the list of checks of the daemon's `StartupChecks` object and the options the daemon gives `StartupChecks.verify`, MUST be the same with the field `Config.startup_checks_view_enabled` at `true` as with it at `false`. | none | `org.chronitondb.startup.test.StartupChecksViewStartTest.sameChecksWithTheSwitchOn` | Covered |
| REQ-SCV-033 | problem 8 | When the view is switched on or off, the set of tables of `system_views`, other than the view, that `system_virtual_schema.tables` lists MUST stay the same. | none | `org.chronitondb.startup.StartupChecksViewTest.stockTablesUnchanged` | Covered |
| REQ-SCV-034 | problem 8 | When the view is switched on or off, the table object that serves a stock table of `system_views` MUST stay the same. | none | `org.chronitondb.startup.StartupChecksViewTest.stockTablesUnchanged` | Covered |
| REQ-SCV-035 | stakeholder need, criterion 9 | The list of startup checks that the daemon registers MUST begin with the checks of `StartupChecks.withDefaultTests`, in their order, followed by one `FileSystemOwnershipCheck`. | none | `org.chronitondb.startup.StartupCheckRowsTest.daemonRegistersTheStockChecks` | Covered |
