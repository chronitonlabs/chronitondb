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

This file follows a draft of the record with three open points. Its rows change with the record when the maintainers have decided them.

The acceptance criteria. Criterion 1 is covered by REQ-SCV-001 and REQ-SCV-002. Criterion 2 by REQ-SCV-003 to REQ-SCV-007. Criterion 3 by REQ-SCV-008 and REQ-SCV-018. Criteria 4 and 5 by REQ-SCV-009 and REQ-SCV-011 to REQ-SCV-013. Criterion 6 by REQ-SCV-010. Criterion 7 by REQ-SCV-013. Criterion 8 by REQ-SCV-009. Criterion 9 has no requirement of its own: the feature edits no file of the startup checks, and the stock suites of section 14 of the record run unchanged. Criterion 10 by REQ-SCV-007, REQ-SCV-017, REQ-SCV-019 to REQ-SCV-021 and REQ-SCV-023.

| Id | Source | Requirement | Covering scenario | Test | Status |
|---|---|---|---|---|---|
| REQ-SCV-001 | stakeholder need, criterion 1 | The switch MUST be off on a node whose `cassandra.yaml` does not set `startup_checks_view_enabled`. | none | `org.chronitondb.startup.StartupChecksViewTest.offByDefault` | Covered |
| REQ-SCV-002 | stakeholder need, criterion 1 | While the switch is off, the node MUST NOT list the view in `system_virtual_schema.tables`. | none | `org.chronitondb.startup.StartupChecksViewTest.notListedWhileOff` | Covered |
| REQ-SCV-003 | stakeholder need, criterion 2 | While the switch is on, the node MUST list the view in `system_virtual_schema.tables`. | none | `org.chronitondb.startup.StartupChecksViewTest.listedWhileOn` | Covered |
| REQ-SCV-004 | stakeholder need, criterion 2 | When a node whose `cassandra.yaml` sets `startup_checks_view_enabled` to `true` has registered its virtual keyspaces at start, the switch MUST be on. | none | `org.chronitondb.startup.test.StartupChecksViewStartTest.yamlSwitchesTheViewOn` | Covered |
| REQ-SCV-005 | stakeholder need, criterion 2 | When `nodetool enablestartupchecksview` runs against a node, the node MUST set the switch on. | none | `org.chronitondb.startup.StartupChecksViewTest.toggleLogsOldAndNew` | Covered |
| REQ-SCV-006 | stakeholder need, criterion 2 | When `nodetool disablestartupchecksview` runs against a node, the node MUST set the switch off. | none | `org.chronitondb.startup.StartupChecksViewTest.toggleLogsOldAndNew` | Covered |
| REQ-SCV-007 | quality-requirements.md item 3 | When a nodetool command changes the value of the switch, the node MUST log the old and the new value at INFO. | none | `org.chronitondb.startup.StartupChecksViewTest.toggleLogsOldAndNew` | Covered |
| REQ-SCV-008 | stakeholder need, criterion 3 | While the switch is on, a `SELECT` of every row of the view MUST return exactly one row for each always-run check and one for each switchable check of the node. | none | `org.chronitondb.startup.StartupCheckRowsTest.oneRowForEachCheck` | Covered |
| REQ-SCV-009 | stakeholder need, criteria 4 and 8 | The view MUST have the columns `name`, `enabled` and `source` and no other column. | none | `org.chronitondb.startup.StartupChecksViewTest.columns` | Covered |
| REQ-SCV-010 | stakeholder need, criterion 6 | The row of an always-run check MUST show `enabled` as `true` and `source` as `always_on`. | none | `org.chronitondb.startup.StartupCheckRowsTest.alwaysRunRows` | Covered |
| REQ-SCV-011 | stakeholder need, criteria 4 and 5 | The row of a switchable check whose start option is not set and that has no yaml entry MUST show `source` as `default` and `enabled` as the default of the check. | none | `org.chronitondb.startup.StartupCheckRowsTest.defaultRows` | Covered |
| REQ-SCV-012 | stakeholder need, criteria 4 and 5 | The row of a switchable check whose start option is not set and that has a yaml entry MUST show `source` as `yaml` and `enabled` as the value `StartupChecksOptions.isEnabled` returns for the check. | none | `org.chronitondb.startup.StartupCheckRowsTest.yamlRows` | Covered |
| REQ-SCV-013 | stakeholder need, criterion 7 | The row of a switchable check whose start option is set MUST show `source` as `system_property` and `enabled` as the value the stock check acts on. | none | `org.chronitondb.startup.StartupCheckRowsTest.systemPropertyRows` | Covered |
| REQ-SCV-014 | problem 3 and branching-and-review.md item 7 | If the view is read while the switch is off, then the node MUST refuse the read with an invalid request error whose message names `startup_checks_view_enabled`. | none | `org.chronitondb.startup.StartupChecksViewTest.readWhileOffIsRefused` | Covered |
| REQ-SCV-015 | problem 4 | If a role without the `SELECT` permission on the view reads it on a node with authorisation on, then the node MUST refuse the read as unauthorised. | none | `org.chronitondb.startup.StartupChecksViewAuthTest.readNeedsSelect` | Covered |
| REQ-SCV-016 | problem 1 | If an `Exception` is thrown while the node applies the switch at start, then the hook MUST return normally. | none | `org.chronitondb.startup.StartupChecksViewTest.startNeverThrows` | Covered |
| REQ-SCV-017 | problem 1 | If an `Exception` is thrown while the node applies the switch, at start or from nodetool, then the node MUST log the failed warning. | none | `org.chronitondb.startup.StartupChecksViewTest.startNeverThrows` | Covered |
| REQ-SCV-018 | stakeholder need, criterion 3, and problem 5 | The fixed list of always-run names MUST hold a name for every check of type `non_configurable_check` that the daemon registers. | none | `org.chronitondb.startup.StartupCheckRowsTest.everyRegisteredCheckHasAName` | Covered |
| REQ-SCV-019 | quality-requirements.md item 1 | When the view serves a read, the node MUST raise the counter `org.chronitondb.metrics:type=StartupChecksView,name=Reads` by one. | none | `org.chronitondb.startup.StartupChecksViewTest.countsReads` | Covered |
| REQ-SCV-020 | quality-requirements.md item 1 | When the view refuses a read because the switch is off, the node MUST raise the counter `org.chronitondb.metrics:type=StartupChecksView,name=RefusedReads` by one. | none | `org.chronitondb.startup.StartupChecksViewTest.readWhileOffIsRefused` | Covered |
| REQ-SCV-021 | quality-requirements.md item 1 | When the node logs the failed warning, the node MUST raise the counter `org.chronitondb.metrics:type=StartupChecksView,name=FailedSwitches` by one. | none | `org.chronitondb.startup.StartupChecksViewTest.startNeverThrows` | Covered |
| REQ-SCV-022 | problem 6 | If `nodetool enablestartupchecksview` or `nodetool disablestartupchecksview` runs against a node without the MBean `org.chronitondb:type=StartupChecksView`, then the command MUST print the missing MBean line and exit with a status other than 0. | none | `org.chronitondb.tools.nodetool.StartupChecksViewCommandsTest.missingMBean` | Covered |
| REQ-SCV-023 | stakeholder need, criterion 10, and problem 7 | The reference page `docs/reference/startup-checks-view.md` MUST contain each of these exact texts: `startup_checks_view_enabled`, `enablestartupchecksview`, `disablestartupchecksview`, the name of the view, each of the 15 always-run names, the four values of `source`, the three counter names and the text of the refusal. | none | `org.chronitondb.startup.StartupChecksViewDocsTest.exactNamesAreDocumented` | Covered |
| REQ-SCV-024 | problem 2 | `NEWS-chronitondb.txt` MUST contain the rollback sentence. | none | `org.chronitondb.startup.StartupChecksViewDocsTest.rollbackLineInNews` | Covered |
