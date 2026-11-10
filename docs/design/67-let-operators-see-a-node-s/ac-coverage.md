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

Location: next to its design record, in `docs/design/67-let-operators-see-a-node-s/`. Process: [testing.md](../../process/testing.md).

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in BCP 14 (RFC 2119, RFC 8174) when, and only when, they appear in all capitals, as shown here.

## Contents

- [Coverage](#coverage)

## Coverage

This item is not an item of a fork feature, so no scenario proves a requirement. Every requirement has one row naming its JUnit test.

| Id | Source | Requirement | Covering scenario | Test | Status |
|---|---|---|---|---|---|
| REQ-1 | issue, acceptance criteria 1 and 2 | When `nodetool version` runs without `--verbose` against a node whose switch is on, nodetool MUST print exactly one line, `ReleaseVersion: ` followed by that node's release version. | none | `org.chronitondb.tools.nodetool.VersionOutputTest.versionPrintsReleaseVersion` | Covered |
| REQ-2 | release.md, the git SHA of the build | When `nodetool version --verbose` runs against a node whose switch is on, nodetool MUST print exactly two lines, the line of REQ-1 and then `GitSHA: ` followed by the value of `StorageServiceMBean.getGitSHA()` of that node. | none | `org.chronitondb.tools.nodetool.VersionOutputTest.verbosePrintsGitSha` | Covered |
| REQ-3 | release.md item 2, the stock behaviour rule | While the node's switch is off, nodetool MUST print, for `nodetool version` with or without `--verbose`, exactly the stock output as defined in section 1. | none | `org.chronitondb.tools.nodetool.VersionOutputTest.switchOffPrintsStockOutput` | Covered |
| REQ-4 | issue, acceptance criterion 2 | If the node asked has no MBean `org.chronitondb:type=ReleaseVersion`, then nodetool MUST print, for `nodetool version` with or without `--verbose`, exactly the stock output. | none | `org.chronitondb.tools.nodetool.VersionOutputTest.nodeWithoutReporterPrintsStockOutput` | Covered |
| REQ-5 | release.md item 3 | The node MUST read its release version from the key `ReleaseVersion` of the classpath resource `org/chronitondb/version.properties`. | none | `org.chronitondb.version.ReleaseVersionTest.readsTheBuildValue` | Covered |
| REQ-6 | risk, Where problems could occur item 4 | If the resource `org/chronitondb/version.properties` is missing, lacks the key `ReleaseVersion`, or holds it with an empty value, then the node MUST report the release version `Unknown`. | none | `org.chronitondb.version.ReleaseVersionTest.missingValueIsUnknown` | Covered |
| REQ-7 | release.md item 2 | The yaml key `nodetool_release_version_enabled` MUST default to `true`. | none | `org.chronitondb.version.ReleaseVersionReporterTest.switchDefaultsToOn` | Covered |
| REQ-8 | quality-requirements.md, nodetool changes the running value only | When `nodetool enablereleaseversion` runs against a node with the MBean, the node MUST set the in-memory value of `nodetool_release_version_enabled` to `true`, with no write to any file. | none | `org.chronitondb.tools.nodetool.VersionOutputTest.enableSetsSwitchOn` | Covered |
| REQ-9 | quality-requirements.md, Observability item 3 | When the value of the switch changes at runtime, the node MUST log one INFO line with the old and the new value. | none | `org.chronitondb.version.ReleaseVersionReporterTest.toggleLogsOldAndNewValue` | Covered |
| REQ-10 | issue, acceptance criterion 2, mixed clusters | If `nodetool enablereleaseversion` or `nodetool disablereleaseversion` runs against a node with no MBean `org.chronitondb:type=ReleaseVersion`, then nodetool MUST exit with code 1 after writing the one line `The node has no ChronitonDB release version reporter. It runs Apache Cassandra or an older ChronitonDB build.` to standard error. | none | `org.chronitondb.tools.nodetool.VersionOutputTest.toggleAgainstNodeWithoutReporterFails` | Covered |
| REQ-11 | quality-requirements.md, Observability | When a node starts, it MUST log one INFO line with its release version. | none | `org.chronitondb.version.ReleaseVersionReporterTest.registerLogsReleaseVersion` | Covered |
| REQ-12 | quality-requirements.md, every outcome has a counter | When the attribute `ReleaseVersion` of the MBean is read, the node MUST increment the counter `Reported` of the metric type `ReleaseVersion` by one, whatever the switch says. | none | `org.chronitondb.version.ReleaseVersionReporterTest.readCountsReported` | Covered |
| REQ-13 | release.md, The version a running node reports, item 7 | The node MUST keep returning Apache Cassandra's build version from `StorageServiceMBean.getReleaseVersion()`, with the switch on and off. | none | `org.chronitondb.tools.nodetool.VersionOutputTest.apacheVersionStringUnchanged` | Covered |
| REQ-14 | branching-and-review.md, Feature switches and defaults, item 1 | While the switch is off, the MBean `org.chronitondb:type=ReleaseVersion` MUST stay registered. | none | `org.chronitondb.version.ReleaseVersionReporterTest.reporterStaysRegisteredWhenOff` | Covered |
| REQ-15 | risk, Where problems could occur item 3 | A second call of `ReleaseVersionReporter.register()` on the same node MUST register nothing and throw nothing. | none | `org.chronitondb.version.ReleaseVersionReporterTest.registerIsIdempotent` | Covered |
| REQ-16 | risk, Where problems could occur item 3 | If registering the MBean throws, then the node MUST log the error and go on starting. | none | `org.chronitondb.version.ReleaseVersionReporterTest.registerFailureIsLoggedNotThrown` | Covered |
| REQ-17 | risk, Where problems could occur item 5 | If the JMX connection throws `SecurityException` while nodetool looks the MBean up or reads `Enabled`, then nodetool MUST print, for `nodetool version` with or without `--verbose`, exactly the stock output. | none | `org.chronitondb.tools.nodetool.VersionOutputPermissionTest.accessDeniedPrintsStockOutput` | Covered |
| REQ-18 | quality-requirements.md, nodetool changes the running value only | When `nodetool disablereleaseversion` runs against a node with the MBean, the node MUST set the in-memory value of `nodetool_release_version_enabled` to `false`, with no write to any file. | none | `org.chronitondb.tools.nodetool.VersionOutputTest.disableSetsSwitchOff` | Covered |
| REQ-19 | the runtime change log convention of section 8 | If a toggle sets the switch to the value it already has, then the node MUST log one INFO line saying the value is unchanged, and no line of REQ-9. | none | `org.chronitondb.version.ReleaseVersionReporterTest.unchangedToggleLogsUnchanged` | Covered |
| REQ-20 | release.md item 3 | When the build target `_createVersionPropFile` runs, the build MUST write the Ant property `chronitondb.version` as the key `ReleaseVersion` of `org/chronitondb/version.properties` in the compiled classes directory. | none | `org.chronitondb.version.ReleaseVersionTest.readsTheBuildValue` | Covered |
