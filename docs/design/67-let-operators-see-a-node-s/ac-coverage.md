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

This item is not an item of a fork feature, so no scenario proves a requirement. Every requirement has one row naming its JUnit test, or the reason it has none. "Problem n" is item n of the record's Where problems could occur.

| Id | Source | Requirement | Covering scenario | Test | Status |
|---|---|---|---|---|---|
| REQ-1 | acceptance criterion 1, decision record 0002 | When `nodetool version` runs without `--verbose` against a node whose switch is on, nodetool MUST print exactly one line to standard output, `ReleaseVersion: ` followed by that node's release version. | none | `org.chronitondb.tools.nodetool.VersionOutputTest.versionPrintsReleaseVersion` | Covered |
| REQ-2 | decision record 0002 | When `nodetool version --verbose` runs against a node whose switch is on, nodetool MUST print exactly two lines to standard output, the line of REQ-1 and then `GitSHA: ` followed by the value of `StorageServiceMBean.getGitSHA()` of that node. | none | `org.chronitondb.tools.nodetool.VersionOutputTest.verbosePrintsGitSha` | Covered |
| REQ-3 | problem 1 | While the node's switch is off, nodetool MUST print, for `nodetool version` with or without `--verbose`, exactly the stock output as defined in section 1. | none | `org.chronitondb.tools.nodetool.VersionOutputTest.switchOffPrintsStockOutput` | Covered |
| REQ-4 | acceptance criterion 2 | If the node asked has no MBean `org.chronitondb:type=ReleaseVersion`, then nodetool MUST print, for `nodetool version` with or without `--verbose`, exactly the stock output. | none | `org.chronitondb.tools.nodetool.VersionOutputTest.nodeWithoutReporterPrintsStockOutput` | Covered |
| REQ-5 | acceptance criterion 1 | The node MUST read its release version from the key `ReleaseVersion` of the classpath resource `org/chronitondb/version.properties`. | none | `org.chronitondb.version.ReleaseVersionTest.readsTheKeyFromTheResource` | Covered |
| REQ-6 | problem 4 | If the resource `org/chronitondb/version.properties` is missing, lacks the key `ReleaseVersion`, or holds a value that is empty after trimming, then the node MUST report the release version `Unknown`. | none | `org.chronitondb.version.ReleaseVersionTest.missingValueIsUnknown` | Covered |
| REQ-7 | acceptance criterion 1 | The yaml key `nodetool_release_version_enabled` MUST default to `true`. | none | `org.chronitondb.version.ReleaseVersionReporterTest.switchDefaultsToOn` | Covered |
| REQ-8 | problem 11 | When `nodetool enablereleaseversion` runs against a node with the MBean, the node MUST set the in-memory value of `nodetool_release_version_enabled` to `true`. | none | `org.chronitondb.tools.nodetool.VersionOutputTest.enableSetsSwitchOn` | Covered |
| REQ-9 | problem 7 | When the attribute `Enabled` of the MBean is written, the node MUST log one INFO line with the old and the new value. | none | `org.chronitondb.version.ReleaseVersionReporterTest.writeLogsOldAndNewValue` | Covered |
| REQ-10 | problem 8 | If `nodetool enablereleaseversion` runs against a node with no MBean `org.chronitondb:type=ReleaseVersion`, then nodetool MUST print the one line `enablereleaseversion: the node has no ChronitonDB release version reporter. It runs Apache Cassandra or an older ChronitonDB build.` to standard output and exit with code 1. | none | `org.chronitondb.tools.nodetool.VersionOutputTest.enableAgainstNodeWithoutReporterFails` | Covered |
| REQ-11 | problem 7 | When `ReleaseVersionReporter.register()` registers the MBean, the node MUST log one INFO line with its release version. | none | `org.chronitondb.version.ReleaseVersionReporterTest.registerLogsReleaseVersion` | Covered |
| REQ-12 | problem 7 | When the attribute `ReleaseVersion` of the MBean is read, the node MUST increment the counter `Reported` of the metric type `ReleaseVersion` by one, whatever the switch says. | none | `org.chronitondb.version.ReleaseVersionReporterTest.readCountsReported` | Covered |
| REQ-13 | problem 9 | The node MUST keep returning Apache Cassandra's build version from `StorageServiceMBean.getReleaseVersion()`, with the switch on and off. | none | `org.chronitondb.tools.nodetool.VersionOutputTest.apacheVersionStringUnchanged` | Covered |
| REQ-14 | problem 11 | While the switch is off, the MBean `org.chronitondb:type=ReleaseVersion` MUST stay registered. | none | `org.chronitondb.version.ReleaseVersionReporterTest.reporterStaysRegisteredWhenOff` | Covered |
| REQ-15 | problem 3 | When `ReleaseVersionReporter.register()` runs on a node whose MBean is already registered, it MUST register nothing and log nothing. | none | `org.chronitondb.version.ReleaseVersionReporterTest.registerTwiceRegistersOnce` | Covered |
| REQ-16 | problem 5 | If the JMX connection throws `SecurityException` while nodetool looks the MBean up or reads `Enabled` or `ReleaseVersion`, then nodetool MUST print, for `nodetool version` with or without `--verbose`, exactly the stock output. | none | `org.chronitondb.tools.nodetool.VersionOutputFallbackTest.accessDeniedPrintsStockOutput` | Covered |
| REQ-17 | problem 5 | If the probe has no JMX connection, then nodetool MUST print, for `nodetool version` with or without `--verbose`, exactly the stock output. | none | `org.chronitondb.tools.nodetool.VersionOutputFallbackTest.noConnectionPrintsStockOutput` | Covered |
| REQ-18 | problem 11 | When `nodetool disablereleaseversion` runs against a node with the MBean, the node MUST set the in-memory value of `nodetool_release_version_enabled` to `false`. | none | `org.chronitondb.tools.nodetool.VersionOutputTest.disableSetsSwitchOff` | Covered |
| REQ-19 | problem 8 | If `nodetool disablereleaseversion` runs against a node with no MBean `org.chronitondb:type=ReleaseVersion`, then nodetool MUST print the one line `disablereleaseversion: the node has no ChronitonDB release version reporter. It runs Apache Cassandra or an older ChronitonDB build.` to standard output and exit with code 1. | none | `org.chronitondb.tools.nodetool.VersionOutputTest.disableAgainstNodeWithoutReporterFails` | Covered |
| REQ-20 | problem 4 | When the build target `_createVersionPropFile` runs, the build MUST write the value of the Ant property `chronitondb.version` as the key `ReleaseVersion` of `src/resources/org/chronitondb/version.properties`. | none | `org.chronitondb.version.ReleaseVersionTest.buildWritesTheAntProperty` | Covered |
| REQ-21 | problem 4 | Where the build runs without a value given for `chronitondb.version`, the build MUST use the value `5.0-chronitondb-SNAPSHOT`. | none | `org.chronitondb.version.ReleaseVersionTest.defaultIsSnapshot` | Covered |
| REQ-22 | decision record 0002 | The change MUST leave every pre-existing test unchanged. | none | `org.apache.cassandra.distributed.test.NodeToolTest.testVersionIncludesGitSHAWhenVerbose`, run unchanged, with the gate's check that no pre-existing test changed | Covered |
| REQ-23 | problem 2 | The reference page and `NEWS-chronitondb.txt` MUST state that `nodetool_release_version_enabled` is removed from `cassandra.yaml` before the node runs an Apache Cassandra binary. | none | none: no automated documentation test exists on this line yet, so the docs review of the code pull request checks the two files for the line | Covered |
| REQ-24 | problem 5 | If the JMX connection throws an exception other than `SecurityException` while nodetool looks the MBean up or reads it, then `nodetool version` MUST fail as stock nodetool fails for that exception. | none | `org.chronitondb.tools.nodetool.VersionOutputFallbackTest.otherFailurePropagates` | Covered |
