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

# Acceptance coverage for #67

Location: next to its design record, in `docs/design/VER-release-version/`, the directory of the fork feature with the key `VER`. Process: [testing.md](../../process/testing.md).

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in BCP 14 (RFC 2119, RFC 8174) when, and only when, they appear in all capitals, as shown here.

## Contents

- [Coverage](#coverage)

## Coverage

This item is a fork feature that fits one item, with the key `VER`. It adds no scenario, for the reason the design record gives under its control table, so every requirement has one row naming its JUnit test. "Problem n" is item n of the record's Where problems could occur. REQ-VER-026 names a stock test that runs unchanged, with the gate's check that no pre-existing test changed as the other half of its proof, and REQ-VER-027, REQ-VER-028, REQ-VER-029, REQ-VER-032 and REQ-VER-035 name a documentation test that reads the two files.

| Id | Source | Requirement | Covering scenario | Test | Status |
|---|---|---|---|---|---|
| REQ-VER-001 | acceptance criterion 1 and decision record 0002 | When `nodetool version` runs without `--verbose` against a node that has the MBean and whose switch is on, over a connection that answers the lookup and the reads, nodetool MUST print exactly one line to standard output, `ReleaseVersion: ` followed by that node's release version. | none | `org.chronitondb.tools.nodetool.VersionOutputTest.versionPrintsReleaseVersion` | Covered |
| REQ-VER-002 | decision record 0002 | When `nodetool version --verbose` runs against a node that has the MBean and whose switch is on, over a connection that answers the lookup and the reads, nodetool MUST print exactly two lines to standard output, the line of REQ-VER-001 and then `GitSHA: ` followed by the value of `StorageServiceMBean.getGitSHA()` of that node. | none | `org.chronitondb.tools.nodetool.VersionOutputTest.verbosePrintsGitSha` | Covered |
| REQ-VER-003 | problem 1 | While the node's switch is off, nodetool MUST print, for `nodetool version` with or without `--verbose` over a connection that answers the lookup and the read of `Enabled`, exactly the stock output as defined in section 1. | none | `org.chronitondb.tools.nodetool.VersionOutputTest.switchOffPrintsStockOutput` | Covered |
| REQ-VER-004 | problem 8 | If the node asked has no MBean `org.chronitondb:type=ReleaseVersion`, then nodetool MUST print, for `nodetool version` with or without `--verbose`, exactly the stock output as defined in section 1. | none | `org.chronitondb.tools.nodetool.VersionOutputTest.nodeWithoutReporterPrintsStockOutput` | Covered |
| REQ-VER-005 | acceptance criterion 2 | When nodetool prints the release version line of REQ-VER-001, the value MUST be the one the asked node's attribute `ReleaseVersion` returned over the connection. | none | `org.chronitondb.tools.nodetool.VersionOutputStubTest.printsTheNodesOwnValue` | Covered |
| REQ-VER-006 | acceptance criterion 1 | The node MUST read its release version from the key `ReleaseVersion` of the classpath resource `org/apache/cassandra/config/version.properties`, with `String.trim()` applied. | none | `org.chronitondb.version.ReleaseVersionTest.readsTheKeyFromTheResource` | Covered |
| REQ-VER-007 | problem 4 | If the resource `org/apache/cassandra/config/version.properties` is missing, cannot be loaded, lacks the key `ReleaseVersion`, or holds a value that is empty after `String.trim()`, then the attribute `ReleaseVersion` MUST return `Unknown`. | none | `org.chronitondb.version.ReleaseVersionReporterTest.attributeIsUnknownWithoutValue` | Covered |
| REQ-VER-008 | acceptance criterion 1 | The yaml key `nodetool_release_version_enabled` MUST default to `true`. | none | `org.chronitondb.version.ReleaseVersionReporterTest.switchDefaultsToOn` | Covered |
| REQ-VER-009 | problem 10 | When `nodetool enablereleaseversion` runs against a node with the MBean, the node MUST set the in-memory value of `nodetool_release_version_enabled` to `true`. | none | `org.chronitondb.tools.nodetool.VersionOutputTest.enableSetsSwitchOn` | Covered |
| REQ-VER-010 | problem 10 | When `nodetool disablereleaseversion` runs against a node with the MBean, the node MUST set the in-memory value of `nodetool_release_version_enabled` to `false`. | none | `org.chronitondb.tools.nodetool.VersionOutputTest.disableSetsSwitchOff` | Covered |
| REQ-VER-011 | problem 7 | When the attribute `Enabled` of the MBean is written, the node MUST log one INFO line with the old and the new value. | none | `org.chronitondb.version.ReleaseVersionReporterTest.writeLogsOldAndNewValue` | Covered |
| REQ-VER-012 | problem 8 | If `nodetool enablereleaseversion` runs against a node with no MBean `org.chronitondb:type=ReleaseVersion`, then nodetool MUST end on the usage error path with the message `enablereleaseversion: the node has no ChronitonDB release version reporter. It runs Apache Cassandra or an older ChronitonDB build, or the reporter failed to register at start.` | none | `org.chronitondb.tools.nodetool.VersionOutputTest.enableAgainstNodeWithoutReporterFails` | Covered |
| REQ-VER-013 | problem 8 | If `nodetool disablereleaseversion` runs against a node with no MBean `org.chronitondb:type=ReleaseVersion`, then nodetool MUST end on the usage error path with the message `disablereleaseversion: the node has no ChronitonDB release version reporter. It runs Apache Cassandra or an older ChronitonDB build, or the reporter failed to register at start.` | none | `org.chronitondb.tools.nodetool.VersionOutputTest.disableAgainstNodeWithoutReporterFails` | Covered |
| REQ-VER-014 | problem 6 | When `StorageService.initServer` runs, the node MUST register the MBean `org.chronitondb:type=ReleaseVersion` through `MBeanWrapper.instance`. | none | `org.chronitondb.tools.nodetool.VersionOutputTest.initServerRegistersTheMBean` | Covered |
| REQ-VER-015 | problem 7 | When `ReleaseVersionReporter.register()` runs, the node MUST log one INFO line `ChronitonDB release version: ` followed by its release version. | none | `org.chronitondb.version.ReleaseVersionReporterTest.registerLogsReleaseVersion` | Covered |
| REQ-VER-016 | problem 3 | If registering the MBean throws, then `register()` MUST return without throwing. | none | `org.chronitondb.version.ReleaseVersionReporterTest.registerFailureIsLogged` | Covered |
| REQ-VER-017 | problem 7 | When the attribute `ReleaseVersion` of the MBean is read, the node MUST increment the counter `Reported` of the metric type `ReleaseVersion` by one, whatever the switch says. | none | `org.chronitondb.version.ReleaseVersionReporterTest.readCountsReported` | Covered |
| REQ-VER-018 | problem 9 | The node MUST keep returning Apache Cassandra's build version from `StorageServiceMBean.getReleaseVersion()`, with the switch on and off. | none | `org.chronitondb.tools.nodetool.VersionOutputTest.apacheVersionStringUnchanged` | Covered |
| REQ-VER-019 | problem 10 | While the switch is off, the MBean `org.chronitondb:type=ReleaseVersion` MUST stay registered. | none | `org.chronitondb.version.ReleaseVersionReporterTest.reporterStaysRegisteredWhenOff` | Covered |
| REQ-VER-020 | problem 5 | If the JMX connection throws `SecurityException` while nodetool looks the MBean up or reads `Enabled` or `ReleaseVersion`, then nodetool MUST print, for `nodetool version` with or without `--verbose`, exactly the stock output as defined in section 1. | none | `org.chronitondb.tools.nodetool.VersionOutputStubTest.accessDeniedPrintsStockOutput` | Covered |
| REQ-VER-021 | problem 5 | If the probe has no JMX connection, then nodetool MUST print, for `nodetool version` with or without `--verbose`, exactly the stock output as defined in section 1. | none | `org.chronitondb.tools.nodetool.VersionOutputStubTest.noConnectionPrintsStockOutput` | Covered |
| REQ-VER-022 | problem 5 | If the JMX connection throws an exception other than `SecurityException`, and other than one whose root cause is `InstanceNotFoundException`, while nodetool looks the MBean up or reads `Enabled` or `ReleaseVersion`, then `nodetool version` MUST end on the stock error path. | none | `org.chronitondb.tools.nodetool.VersionOutputStubTest.otherFailureReportsAsStock` | Covered |
| REQ-VER-023 | problem 5 | If `nodetool enablereleaseversion` runs with no JMX connection, then nodetool MUST end on the usage error path with the message `enablereleaseversion needs a JMX connection`. | none | `org.chronitondb.tools.nodetool.VersionOutputStubTest.enableWithoutConnectionFails` | Covered |
| REQ-VER-024 | problem 5 | If `nodetool disablereleaseversion` runs with no JMX connection, then nodetool MUST end on the usage error path with the message `disablereleaseversion needs a JMX connection`. | none | `org.chronitondb.tools.nodetool.VersionOutputStubTest.disableWithoutConnectionFails` | Covered |
| REQ-VER-025 | problem 4 | When the build target `_createVersionPropFile` runs, the build MUST write the value of the Ant property `chronitondb.version` as the key `ReleaseVersion` of `org/apache/cassandra/config/version.properties`. | none | `org.chronitondb.version.ReleaseVersionTest.buildWritesTheKey` | Covered |
| REQ-VER-026 | decision record 0002 | The change MUST leave every pre-existing test unchanged. | none | `org.apache.cassandra.distributed.test.NodeToolTest.testVersionIncludesGitSHAWhenVerbose` | Covered |
| REQ-VER-027 | problem 2 | The reference page MUST state that the operator removes `nodetool_release_version_enabled` from `cassandra.yaml` before the node runs an Apache Cassandra binary or a ChronitonDB build older than this feature. | none | `org.chronitondb.version.ReleaseVersionDocsTest.rollbackLineOnReferencePage` | Covered |
| REQ-VER-028 | problem 5 | The reference page MUST state the JMX permissions a role needs on `org.chronitondb:type=ReleaseVersion` under the authorization proxy, `cassandra.jmx.authorizer`: `DESCRIBE` and `SELECT` to see the release version with `nodetool version`, `DESCRIBE` and `MODIFY` to run the two commands. | none | `org.chronitondb.version.ReleaseVersionDocsTest.permissionsAreDocumented` | Covered |
| REQ-VER-029 | problem 2 | `NEWS-chronitondb.txt` MUST state that the operator removes `nodetool_release_version_enabled` from `cassandra.yaml` before the node runs an Apache Cassandra binary or a ChronitonDB build older than this feature. | none | `org.chronitondb.version.ReleaseVersionDocsTest.rollbackLineInNews` | Covered |
| REQ-VER-030 | problem 5 | If the JMX connection throws an exception whose root cause is not `InstanceNotFoundException` while `nodetool enablereleaseversion` looks the MBean up or writes `Enabled`, then nodetool MUST end on the stock error path. | none | `org.chronitondb.tools.nodetool.VersionOutputStubTest.enableFailureReportsAsStock` | Covered |
| REQ-VER-031 | problem 5 | If the JMX connection throws an exception whose root cause is not `InstanceNotFoundException` while `nodetool disablereleaseversion` looks the MBean up or writes `Enabled`, then nodetool MUST end on the stock error path. | none | `org.chronitondb.tools.nodetool.VersionOutputStubTest.disableFailureReportsAsStock` | Covered |
| REQ-VER-032 | problem 5 | The reference page MUST list the outputs that keep Apache Cassandra's version string on a ChronitonDB node: `bin/cassandra -v`, the start log line `Cassandra version:`, the cqlsh banner, `nodetool describecluster`, `nodetool gossipinfo`, and `nodetool version` run from an Apache Cassandra nodetool or a ChronitonDB nodetool older than this feature. | none | `org.chronitondb.version.ReleaseVersionDocsTest.knownLimitationsAreDocumented` | Covered |
| REQ-VER-033 | problem 4 | The value of the key `ReleaseVersion` in `org/apache/cassandra/config/version.properties`, after `String.trim()`, MUST match in full `5\.0-chronitondb([1-9][0-9]*|-SNAPSHOT)`, the release version form of release.md, Version numbers, or the default, on every build that runs the unit tests, which the gate, CI and the release pipeline all do. | none | `org.chronitondb.version.ReleaseVersionTest.valueHasTheReleaseForm` | Covered |
| REQ-VER-034 | problem 7 | When the attribute `Enabled` of the MBean is read, the node MUST return the current value of `nodetool_release_version_enabled`. | none | `org.chronitondb.version.ReleaseVersionReporterTest.enabledReadsTheSwitch` | Covered |
| REQ-VER-035 | problem 7 | The reference page MUST contain each of these exact texts: `nodetool_release_version_enabled`, `enablereleaseversion`, `disablereleaseversion`, `org.chronitondb:type=ReleaseVersion`, `org.chronitondb.metrics:type=ReleaseVersion,name=Reported`, `Unknown`, `5.0-chronitondb-SNAPSHOT` and `the node has no ChronitonDB release version reporter`. | none | `org.chronitondb.version.ReleaseVersionDocsTest.exactNamesAreDocumented` | Covered |
