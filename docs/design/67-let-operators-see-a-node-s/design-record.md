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

# Design: #67 Let operators see a node's ChronitonDB version from nodetool

| Field | Value |
|---|---|
| Title | Let operators see a node's ChronitonDB version from nodetool |
| Document type | Specification and description at item level (ISO/IEC/IEEE 15289) |
| Status | Draft |
| Version | 1 |
| Author | Designer: chronitondb-agent |
| Approver | The maintainer who merges the pull request |
| References | Issue #67. Line `chronitondb-sandbox`. Apache base commit `76550e931481e965ae3283d8cf4a59c320d74c55` (Apache `cassandra-5.0`, build version 5.0.10). No feature spec and no plan: the one item path. Process pages [release.md](../../process/release.md#what-nodetool-version-shows) and [quality-requirements.md](../../process/quality-requirements.md). Decision records 0001 and 0002. |
| Risk | Normal: the worst Bug Category is Degradation, a wrong first line of `nodetool version` that a script reads, with no data or availability effect. The floor of [classification.md](../../process/classification.md#the-floor) applies as well, since the change touches three public interfaces, command line tools, configuration and JMX MBeans, and the one stock behaviour the maintainers excepted. |
| Size | Low Hanging Fruit: seven small edits in stock files, each a line or a few lines, seven new fork Java files (six classes and one interface), no dependency on other work. |
| Reach | One area: the version reporting of one node, in `org.apache.cassandra.tools.nodetool`, `org.apache.cassandra.service.StorageService` and the new packages `org.chronitondb.version` and `org.chronitondb.tools.nodetool`. |
| Touches | public interface (command line tools and arguments), public interface (configuration), public interface (jmx mbeans, including metrics), stock behaviour (the output of `nodetool version`, the one excepted behaviour), new feature or switch |

Change history: the git history of this file.

Location: `docs/design/67-let-operators-see-a-node-s/`, with the coverage file `ac-coverage.md` and the page skeleton `page-release-version.md` next to it. Every section is filled, or carries a waiver with its reason.

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in BCP 14 (RFC 2119, RFC 8174) when, and only when, they appear in all capitals, as shown here.

The Risk, Size and Reach rows are the item's class, as [classification.md](../../process/classification.md) defines it, and match the issue's `risk:normal`, `size:low-hanging-fruit` and `reach:one-area` labels. The issue also carries `kind:perfective`, so the item takes the one item path of [maintenance.md](../../process/maintenance.md#the-one-item-path): this directory, plain `REQ-n` ids, no feature key and no scenarios ([additive.md, Feature keys and requirement ids](../../process/additive.md#feature-keys-and-requirement-ids), item 7). The switch rules of [branching-and-review.md](../../process/branching-and-review.md#feature-switches-and-defaults) bind it all the same, because release.md gives this change a switch (item 2 of its list). In this record, "release.md item n" means item n of the list under [What nodetool version shows](../../process/release.md#what-nodetool-version-shows). Any other list of that page is named with its section. "Problem n" means item n of [Where problems could occur](#where-problems-could-occur).

## Contents

- [1. Problem, acceptance criteria and requirements](#1-problem-acceptance-criteria-and-requirements)
  - [How it works](#how-it-works)
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

An operator cannot tell which ChronitonDB build a node runs. `nodetool version` prints Apache Cassandra's version string, read from `org/apache/cassandra/config/version.properties` that the build writes (`src/java/org/apache/cassandra/utils/FBUtilities.java:443` to `465`, `build.xml:492` to `499`). During a rolling upgrade there is no way to ask a node whether it is on the new ChronitonDB release yet.

Acceptance criteria:

1. From the issue: an operator can ask a node, with nodetool, which ChronitonDB version it is running.
2. Derived from the issue's rolling upgrade case: the answer is the asked node's own, not the operator's nodetool install's, so an upgrade can be checked node by node.

The maintainers settled the shape of the answer in release.md, What nodetool version shows, and in decision record 0002. `nodetool version` shows the release version, for example `5.0-chronitondb3`, on the stock `ReleaseVersion:` line, and the git SHA of the build on the stock `GitSHA:` line only with `--verbose`. No Apache release line appears. It is the one behaviour-changing feature that is on by default (release.md item 1). It has a switch like every feature (item 2). The version and the git SHA are read from the build, never written into the code (item 3). `bin/cassandra -v`, the start log line `Cassandra version:` and the cqlsh banner stay as they are (item 5). No stock test changes (decision record 0002).

### How it works

Three parts, each small.

**1. The build writes the release version.** `build.xml` gains, next to `base.version` at `build.xml:36`, a condition that records whether the build was given a value, `chronitondb.version.given`, set the way `version` is set from `release` (`build.xml:104` to `107`), and then the property `chronitondb.version` with the default `5.0-chronitondb-SNAPSHOT`. An Ant property set on the command line wins over one set in the file, so the release pipeline passes `-Dchronitondb.version=<version>` and needs no file change. The pipeline passes the release version, for example `5.0-chronitondb3`, because release.md, How a release is made, item 6 promotes the candidate unchanged, so the candidate build carries the release version it becomes. This design accepts any non blank string.

The target `_createVersionPropFile` (`build.xml:492` to `499`) also writes `org/chronitondb/version.properties` with the one key `ReleaseVersion`. It writes it where the stock target writes the stock file: under `src/resources`, from which `build-project` copies every resource into the classes directory (`build.xml:108` to `109`, `544` to `547`). The stock target creates its directory first (`build.xml:494`) and the fork block does the same, so the target also works when it runs alone, as `generate-idea-files` (`build.xml:1924`) and `.build/run-tests.sh:451` run it. Three stock edits follow from that place: `.gitignore` gains `src/resources/org/chronitondb/`, as line 8 ignores the stock directory, the `clean` target deletes the fork directory as it deletes the stock one (`build.xml:419`), and the source artifact excludes the fork file as it excludes the stock one (`build.xml:949`). The IDE reads resources from `src/resources`, so it sees the fork file the way it sees the stock one. The git SHA needs no second copy: the stock file already carries `GitSHA` from the same build (`build.xml:497`, `.build/build-git.xml:33` to `41`), and `FBUtilities.getGitSHA()` reads it (`FBUtilities.java:468` to `474`).

For the tests, the test macro `testmacrohelper` passes two more JVM arguments next to `-Dstorage-config` (`build.xml:1156`): `-Dchronitondb.version=${chronitondb.version}` and `-Dchronitondb.version.given=${chronitondb.version.given}`. That is how `ReleaseVersionTest` compares the resource with the value the build was given and knows whether the build was given one.

**2. The node exposes the value over JMX.** The class `org.chronitondb.version.ReleaseVersion` reads the properties file once from the classpath, as `FBUtilities.loadedProperties` does for the stock file (`FBUtilities.java:443` to `458`), and returns `FBUtilities.UNKNOWN_RELEASE_VERSION`, the string `Unknown` (`FBUtilities.java:117`), when the file or the key is missing or the value is blank after trimming.

The MBean `org.chronitondb:type=ReleaseVersion` is the class `org.chronitondb.version.ReleaseVersionReporter`, which implements `ReleaseVersionReporterMBean`, named as the JMX Standard MBean rules require and as every stock MBean is named, for example `StorageService implements StorageServiceMBean` (`src/java/org/apache/cassandra/service/StorageService.java:293`). It exposes the read only attribute `ReleaseVersion` and the writable attribute `Enabled`. It holds the counter `Reported` in a final field, registered once through `CassandraMetricsRegistry.Metrics.counter` (`src/java/org/apache/cassandra/metrics/CassandraMetricsRegistry.java:55`) with a `MetricName` under the fork group.

`register()` looks the name up with `MBeanWrapper.instance.isRegistered(String)` (`src/java/org/apache/cassandra/utils/MBeanWrapper.java:119`). When the MBean is already there it does nothing. Otherwise it registers through `registerMBean(obj, name, OnException.LOG)` (`MBeanWrapper.java:90`) and then logs the release version at INFO. The wrapper catches every exception of the registration and hands it to `OnException.LOG`, which writes `Error in MBean wrapper:` at ERROR (`MBeanWrapper.java:176` to `185` and `366`), so a registration failure is logged and the node goes on starting with no catch in fork code. `StorageService.initServer` calls `register()` right after its own `registerMBeans()` (`StorageService.java:1018`), so the fork MBean exists exactly when the stock `StorageService` MBean exists. Before that point stock `nodetool version` fails too, with `Server is not initialized yet` (`src/java/org/apache/cassandra/tools/NodeTool.java:323` to `324`).

The switch is the yaml key `nodetool_release_version_enabled`, a new `volatile boolean` field of `Config` with the default `true`, read and written through `DatabaseDescriptor.getRawConfig()` (`src/java/org/apache/cassandra/config/DatabaseDescriptor.java:385`). The setter of `Enabled` logs the old and the new value at INFO on every write, as `StorageService.setCompactionThroughputMbPerSec` does (`StorageService.java:1925` to `1933`). The MBean stays registered while the switch is off, so the toggle can turn the feature on at runtime. The `ReleaseVersion` attribute returns the value whatever the switch says: the switch decides what nodetool prints, not what JMX shows. The start log line reads the value from `ReleaseVersion` directly, not through the attribute, so the counter is 0 after start.

**3. nodetool asks the node.** The stock command `version` (`src/java/org/apache/cassandra/tools/nodetool/Version.java:25` to `39`) gets one hook line at the top of `execute`: `if (VersionOutput.print(probe, verbose)) return;`. The fork class `org.chronitondb.tools.nodetool.ReleaseVersionProbe` finds the MBean on the probe's connection, `NodeProbe.getMbeanServerConn()` (`src/java/org/apache/cassandra/tools/NodeProbe.java:772`), with `isRegistered` and then a `JMX.newMBeanProxy`. `VersionOutput.print` returns `false`, and the stock lines run unchanged, in four cases:

1. The probe has no connection, `getMbeanServerConn()` returns `null`. That is the in-JVM distributed test framework, whose `InternalNodeProbe.connect` sets the field to `null` and points the proxies at the node's own singletons (`test/distributed/org/apache/cassandra/distributed/mock/nodetool/InternalNodeProbe.java:61` to `70`). The stock distributed test `NodeToolTest` runs nodetool that way, so it prints stock output and passes unchanged.
2. The MBean is absent: the node runs Apache Cassandra or an older ChronitonDB build.
3. `Enabled` is `false`.
4. The connection throws `SecurityException` on the lookup or on the read of `Enabled` or `ReleaseVersion`, because JMX authorization lets the role read `StorageService` but not this MBean. The role sees what it is allowed to see, which is the stock output, with nothing else printed.

Any other exception from the lookup or the reads, for example `IOException`, propagates as it does from the stock calls, which `NodeTool.execute` reports as `error: ...` with exit status 2 (`NodeTool.java:289` to `292` and `326` to `334`): such a failure breaks the stock calls on the same connection too. Otherwise `print` writes the release version line, with `--verbose` the git SHA line from the stock `probe.getGitSHA()` (`NodeProbe.java:864` to `867`), and returns `true`.

Two new commands, `enablereleaseversion` and `disablereleaseversion`, use `ReleaseVersionProbe` to set `Enabled`, and are added to the command list in `src/java/org/apache/cassandra/tools/NodeTool.java:98` to `246`, next to `Version.class` at line 243, and to the Debian shell completion list, `debian/nodetool-completion`, next to `disableauditlog` and `enableauditlog` at lines 79 and 88. They print nothing on success, as `disableauditlog` does (`src/java/org/apache/cassandra/tools/nodetool/DisableAuditLog.java:25` to `35`). When `isRegistered` answers `false`, they print one line that names the command to `probe.output().out` and call `System.exit(1)`, as `Status` does for its own error (`src/java/org/apache/cassandra/tools/nodetool/Status.java:59` and `89` to `96`). When the lookup throws, a role without `DESCRIBE` on the MBean for example, the exception propagates as from any stock command without a grant.

The output when the switch is on, as decision record 0002 settles it:

```
$ nodetool version
ReleaseVersion: 5.0-chronitondb3
$ nodetool version --verbose
ReleaseVersion: 5.0-chronitondb3
GitSHA: 1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b
```

Stock prints `ReleaseVersion: 5.0.10` on a release build, `ReleaseVersion: 5.0.10-SNAPSHOT` on any other build, and with `--verbose` a second line `GitSHA: <sha>` (`Version.java:36` to `38`, `build.xml:104` to `107`). "Stock output" in this record means the lines the stock code of `Version.execute` prints on the same node from `StorageServiceMBean.getReleaseVersion()` and `getGitSHA()`. The stock distributed test `NodeToolTest.testVersionIncludesGitSHAWhenVerbose` asserts that `version` prints no `GitSHA:` line and `version --verbose` does (`test/distributed/org/apache/cassandra/distributed/test/NodeToolTest.java:137` to `149`). Decision record 0002 keeps both assertions true with no change to that test.

The milestone gate rule, that a switch refuses to turn on before the feature's final milestone gate ([additive.md, Milestone gates](../../process/additive.md#milestone-gates)), binds a feature with milestones. This item has none: its one gate is the maintainer's merge of the code pull request (maintenance.md, The one-item path, item 4), and release.md items 2 to 4 say the switch is on by default from the line's first release, which the feature blocks until it is in. So the switch works from the merge of the code pull request.

### Requirements

REQ-1 (event driven): When `nodetool version` runs without `--verbose` against a node whose switch is on, nodetool MUST print exactly one line to standard output, `ReleaseVersion: ` followed by that node's release version. Source: acceptance criterion 1 and decision record 0002.

REQ-2 (event driven): When `nodetool version --verbose` runs against a node whose switch is on, nodetool MUST print exactly two lines to standard output, the line of REQ-1 and then `GitSHA: ` followed by the value of `StorageServiceMBean.getGitSHA()` of that node. Source: decision record 0002.

REQ-3 (state driven): While the node's switch is off, nodetool MUST print, for `nodetool version` with or without `--verbose`, exactly the stock output as defined in section 1. Source: problem 1, under the stock behaviour rule of quality-requirements.md.

REQ-4 (unwanted behaviour): If the node asked has no MBean `org.chronitondb:type=ReleaseVersion`, then nodetool MUST print, for `nodetool version` with or without `--verbose`, exactly the stock output. Source: acceptance criterion 2.

REQ-5 (ubiquitous): The node MUST read its release version from the key `ReleaseVersion` of the classpath resource `org/chronitondb/version.properties`. Source: acceptance criterion 1, as release.md item 3 shapes it: read from the build.

REQ-6 (unwanted behaviour): If the resource `org/chronitondb/version.properties` is missing, lacks the key `ReleaseVersion`, or holds a value that is empty after trimming, then the node MUST report the release version `Unknown`. Source: problem 4.

REQ-7 (ubiquitous): The yaml key `nodetool_release_version_enabled` MUST default to `true`. Source: acceptance criterion 1, as release.md item 2 shapes it: on by default, nothing to configure first.

REQ-8 (event driven): When `nodetool enablereleaseversion` runs against a node with the MBean, the node MUST set the in-memory value of `nodetool_release_version_enabled` to `true`. Source: problem 11.

REQ-9 (event driven): When the attribute `Enabled` of the MBean is written, the node MUST log one INFO line with the old and the new value. Source: problem 7.

REQ-10 (unwanted behaviour): If `nodetool enablereleaseversion` runs against a node with no MBean `org.chronitondb:type=ReleaseVersion`, then nodetool MUST print the one line `enablereleaseversion: the node has no ChronitonDB release version reporter. It runs Apache Cassandra or an older ChronitonDB build.` to standard output and exit with code 1. Source: problem 8.

REQ-11 (event driven): When `ReleaseVersionReporter.register()` registers the MBean, the node MUST log one INFO line with its release version. Source: problem 7.

REQ-12 (event driven): When the attribute `ReleaseVersion` of the MBean is read, the node MUST increment the counter `Reported` of the metric type `ReleaseVersion` by one, whatever the switch says. Source: problem 7.

REQ-13 (ubiquitous): The node MUST keep returning Apache Cassandra's build version from `StorageServiceMBean.getReleaseVersion()`, with the switch on and off. Source: problem 9.

REQ-14 (state driven): While the switch is off, the MBean `org.chronitondb:type=ReleaseVersion` MUST stay registered. Source: problem 11.

REQ-15 (event driven): When `ReleaseVersionReporter.register()` runs on a node whose MBean is already registered, it MUST register nothing and log nothing. Source: problem 3.

REQ-16 (unwanted behaviour): If the JMX connection throws `SecurityException` while nodetool looks the MBean up or reads `Enabled` or `ReleaseVersion`, then nodetool MUST print, for `nodetool version` with or without `--verbose`, exactly the stock output. Source: problem 5.

REQ-17 (unwanted behaviour): If the probe has no JMX connection, then nodetool MUST print, for `nodetool version` with or without `--verbose`, exactly the stock output. Source: problem 5.

REQ-18 (event driven): When `nodetool disablereleaseversion` runs against a node with the MBean, the node MUST set the in-memory value of `nodetool_release_version_enabled` to `false`. Source: problem 11.

REQ-19 (unwanted behaviour): If `nodetool disablereleaseversion` runs against a node with no MBean `org.chronitondb:type=ReleaseVersion`, then nodetool MUST print the one line `disablereleaseversion: the node has no ChronitonDB release version reporter. It runs Apache Cassandra or an older ChronitonDB build.` to standard output and exit with code 1. Source: problem 8.

REQ-20 (event driven): When the build target `_createVersionPropFile` runs, the build MUST write the value of the Ant property `chronitondb.version` as the key `ReleaseVersion` of `src/resources/org/chronitondb/version.properties`. Source: problem 4, as release.md item 3 shapes it: read from the build.

REQ-21 (optional feature): Where the build runs without a value given for `chronitondb.version`, the build MUST use the value `5.0-chronitondb-SNAPSHOT`. Source: problem 4.

REQ-22 (ubiquitous): The change MUST leave every pre-existing test unchanged. Source: decision record 0002.

REQ-23 (ubiquitous): The reference page and `NEWS-chronitondb.txt` MUST state that `nodetool_release_version_enabled` is removed from `cassandra.yaml` before the node runs an Apache Cassandra binary. Source: problem 2.

REQ-24 (unwanted behaviour): If the JMX connection throws an exception other than `SecurityException` while nodetool looks the MBean up or reads it, then `nodetool version` MUST fail as stock nodetool fails for that exception. Source: problem 5.

## 2. Decisions implemented

1. Decision record 0001, The first maintainers, 2026-11-01: the maintainers who approve this record. Nothing in it binds the design.
2. Decision record 0002, What nodetool version prints on a ChronitonDB node, 2026-11-10, added in this pull request: the first line keeps the label `ReleaseVersion:` with the node's ChronitonDB release version as its value, the `GitSHA:` line keeps its label and appears only with `--verbose`, and no stock test changes. REQ-1, REQ-2, REQ-22 and the first row of the departures table in section 3 implement it.
3. The process pages, which carry the maintainers' settled decisions on this feature and are read on the line at commit `c51f02cba9`: [release.md, What nodetool version shows](../../process/release.md#what-nodetool-version-shows) (what it shows, on by default, a switch, read from the build, the three outputs that stay as they are), [release.md, What a release may contain](../../process/release.md#what-a-release-may-contain) item 4 (the one exception to off by default), [release.md, The version a running node reports](../../process/release.md#the-version-a-running-node-reports) item 5 (the node version is a separate feature, so `FBUtilities.getReleaseVersionString()` stays as it is here), [quality-requirements.md](../../process/quality-requirements.md) (the checklist in section 6), [branching-and-review.md, Feature switches and defaults](../../process/branching-and-review.md#feature-switches-and-defaults) item 1 (a yaml setting and a nodetool toggle) and item 7 (stock behaviour with the feature off), [maintenance.md, The one-item path](../../process/maintenance.md#the-one-item-path), [governance.md, Changes to this page](../../process/governance.md#changes-to-this-page) (a process page changes only through the documentation only path), [conventions.md, Names](../../process/conventions.md#names) (no `cassandra` or `axon` in a new name, the JMX domain `org.chronitondb`, fork metrics under their own types), [conventions.md, Code layout](../../process/conventions.md#code-layout) (fork code under `org.chronitondb`, a stock edit is the hook only), [conventions.md, Change logs and release notes](../../process/conventions.md#change-logs-and-release-notes) item 2 (`NEWS-chronitondb.txt` is written in the pull request that makes the change) and [conventions.md, Where things live](../../process/conventions.md#where-things-live) item 5 (documentation ships in the same pull request as the code).

As of 2026-11-10 the register holds records 0001 and 0002, the second added by this pull request. No newer record exists on versions, nodetool or configuration.

## 3. Stock behaviour preservation

Feature class: behaviour-changing, because it changes what the stock command `nodetool version` prints, the one behaviour-changing feature the maintainers allow on by default (release.md, What a release may contain, item 4).

| Switch | Class | Reason | Default per line | Stock operations it changes |
|---|---|---|---|---|
| `nodetool_release_version_enabled`, with `nodetool enablereleaseversion` and `nodetool disablereleaseversion` | behaviour-changing | it replaces the value on the first line of `nodetool version` with the node's ChronitonDB release version | `true` on every line (release.md, What a release may contain, item 4) | `nodetool version`, with and without `--verbose` |

| Stock behaviour today (file and line) | This change | Switch that controls it | Error text naming the switch |
|---|---|---|---|
| `nodetool version` prints `ReleaseVersion: ` and the value of `StorageServiceMBean.getReleaseVersion()`, which is Apache's build version (`src/java/org/apache/cassandra/tools/nodetool/Version.java:36`, `src/java/org/apache/cassandra/service/StorageService.java:3985` to `3988`) | with the switch on and the MBean present, the line carries the node's ChronitonDB release version instead. The `GitSHA:` line under `--verbose` (`Version.java:37` to `38`) keeps its label, its flag and its value | `nodetool_release_version_enabled`, in memory through `nodetool disablereleaseversion` | none: the switch refuses nothing, it only picks the value. The toggles against a node without the MBean print the line of REQ-10 or REQ-19, which names the command |
| `system_views.settings` lists one row per `Config` field (`src/java/org/apache/cassandra/db/virtual/SettingsTable.java:154`), and the start log line `Node configuration:` prints every field (`src/java/org/apache/cassandra/config/Config.java:1347` to `1376`) | both show one more entry, `nodetool_release_version_enabled`, on every node, switch on or off | none: the key exists whether the feature is on or off, because Apache's loader refuses a key without a `Config` field (`src/java/org/apache/cassandra/config/YamlConfigurationLoader.java:423`) and the toggle of branching-and-review.md item 1 needs the field | none |
| `nodetool help` lists the commands of `NodeTool.java:98` to `246` | the list has two more entries, `enablereleaseversion` and `disablereleaseversion`, on every node | none: the toggle branching-and-review.md item 1 requires is a command, and a command is listed | none |
| the start log holds the lines of `StorageService.initServer` (`StorageService.java:969` to `971`) and registers the stock MBeans at `StorageService.java:1018` | one more INFO line, `ChronitonDB release version: <value>`, after the stock MBean registration, on every node, switch on or off | none: the line says which build runs, which is what the issue asks for, and a log line is none of the results, errors, warnings, wire bytes, files, metrics or code defaults the stock behaviour rule names | none |
| the JMX server holds Apache's MBeans and metrics only | one more MBean, `org.chronitondb:type=ReleaseVersion`, and one more counter, `org.chronitondb.metrics:type=ReleaseVersion,name=Reported`, exist on every node, switch on or off | none: the MBean is the handle of the toggle branching-and-review.md item 1 requires, and holding it is how the feature can be turned on at runtime. The "no new memory" of item 7 reads as the feature's work, which the node does not do while off: one object and one counter, under a kilobyte, allocated once | none |

Everything else stays stock. `FBUtilities.getReleaseVersionString()` and `getGitSHA()` (`FBUtilities.java:460` to `474`) are not touched, so gossip, `system.local`, drivers, `bin/cassandra -v` (`bin/cassandra:236` to `237`, which runs `org.apache.cassandra.tools.GetVersion`, `src/java/org/apache/cassandra/tools/GetVersion.java:22` to `25`), the cqlsh banner and the start log lines `Cassandra version:` and `Git SHA:` (`StorageService.java:969` to `970`) print what they print today, and none of those files is in the Planned file list. No code default in a stock class changes: the new `Config` field is new, with the default the maintainers set. No stock metric, MBean, file, thread or name changes. REQ-22 keeps every pre-existing test as it is, and the lint of the gate refuses a modified pre-existing test.

### Stock hook points

There is no feature spec for a one item change, so the hook points are listed here with their delta entry, `docs/delta/nodetool-version-shows-release-version.md`.

1. `src/java/org/apache/cassandra/tools/nodetool/Version.java`: one import and one line at the top of `execute`, calling `org.chronitondb.tools.nodetool.VersionOutput.print(probe, verbose)`.
2. `src/java/org/apache/cassandra/tools/NodeTool.java`: two imports and two entries in the command list (lines 98 to 246), `EnableReleaseVersion.class` and `DisableReleaseVersion.class`.
3. `src/java/org/apache/cassandra/service/StorageService.java`: one import and one line after `registerMBeans();` at line 1018 in `initServer`, `ReleaseVersionReporter.instance.register()`.
4. `src/java/org/apache/cassandra/config/Config.java`: one field, `public volatile boolean nodetool_release_version_enabled = true;`, placed with the other boolean switches near line 112. It is a field, not a hook that imports fork code, but it is a stock edit and so it is listed.
5. `build.xml`: the condition and the property next to `base.version` (line 36), one `mkdir` and one `propertyfile` block inside `_createVersionPropFile` (lines 492 to 499), one `delete` in `clean` next to line 419, one `exclude` in the source artifact next to line 949, and two `jvmarg` lines in `testmacrohelper` next to line 1156. A build file, not Java, listed for the same reason.
6. `.gitignore`: one line, `src/resources/org/chronitondb/`, next to line 8.
7. `debian/nodetool-completion`: two command names, next to lines 79 and 88.

## 4. Prior art reviewed

Stock Apache Cassandra, read on this line at the Apache base commit:

1. The build writes `CassandraVersion` and `GitSHA` into `version.properties` under `src/resources` at `build.xml:492` to `499`, from `version` (`base.version` or `base.version-SNAPSHOT`, lines 104 to 107) and `git.sha` (`.build/build-git.xml:22` to `41`, `git describe --always --dirty`, `Unknown` without git), creates the directory first (line 494), ignores it in git (`.gitignore:8`), deletes it in `clean` (line 419) and keeps it out of the source artifact (line 949). The design copies all of this for the fork's one value and reuses the stock `GitSHA`.
2. `FBUtilities.getReleaseVersionString()` and `getGitSHA()` read the file once through a memoized supplier and return `Unknown` when it is missing (`FBUtilities.java:443` to `474`). The loader is private and reads one fixed path, so the design copies the shape and uses the stock constant `UNKNOWN_RELEASE_VERSION` (`FBUtilities.java:117`).
3. `nodetool version` is three lines of code over two MBean getters (`Version.java:33` to `39`, `NodeProbe.java:859` to `867`, `StorageServiceMBean.java:108` and `114`). The design leaves them in place and adds one line before them.
4. Stock boolean toggles are command pairs: `enableauditlog` and `disableauditlog` (`DisableAuditLog.java:25` to `35`), `enablebinary` and `disablebinary`, `enablegossip` and `disablegossip`. The design follows the pair idiom. A command that finds its precondition false prints a line to `probe.output().out` and exits 1, as `Status` does (`Status.java:59` and `89` to `96`).
5. A runtime setting is a `volatile` field of `Config` written through a setter that logs the old and the new value at INFO on every write, for example `StorageService.setCompactionThroughputMbPerSec` (`StorageService.java:1925` to `1933`). The design follows it with one field and the MBean setter.
6. `MBeanWrapper.registerMBean(obj, name, OnException.LOG)` catches every registration failure and logs it at ERROR (`MBeanWrapper.java:90`, `176` to `185`, `366`), and `isRegistered(String)` (`MBeanWrapper.java:119`) answers whether a name is taken. The design uses both and adds no catch of its own.
7. Apache's yaml loader refuses a key it does not know, `Invalid yaml. Please remove properties ... from your cassandra.yaml` (`YamlConfigurationLoader.java:321` and `423`). So the key is a `Config` field, and the rollback line in section 9 exists.
8. JMX authorization: `AuthorizationProxy` maps `isRegistered` to the `DESCRIBE` permission, `getAttribute` to `SELECT` and `setAttribute` to `MODIFY` on the target MBean (`src/java/org/apache/cassandra/auth/jmx/AuthorizationProxy.java:418` to `437`) and throws `SecurityException("Access Denied")` without a grant (`AuthorizationProxy.java:179`). A role granted `StorageService` only would fail on the fork MBean, which is why REQ-16 exists.
9. The in-JVM distributed test framework runs nodetool with no JMX connection (`InternalNodeProbe.java:61` to `70`), which is why REQ-17 exists.
10. Apache trunk and the 6.0 line: `nodetool version` has the same shape, on picocli instead of airline, so a 6.0 port writes the two toggle commands again in picocli. Not part of this item.
11. Apache JIRA: CASSANDRA-17753 added the `GitSHA` line and the stock test that asserts it (commit `230fe8e647`). Its comments put the line behind `--verbose` because a released build is fixed to one SHA, so the SHA is a development detail that should not reach the plain user facing output. Decision record 0002 keeps that rule.

Other systems, by behaviour from their public documentation:

1. OpenSearch, a fork of another search engine, reports its own version number in the same field its base product used, `version.number` of `GET /`, and adds a `distribution: opensearch` field beside it. The fork's version takes the existing field, and the base product's version is not shown.
2. Ubuntu reports its own release through `lsb_release -a` and `/etc/os-release`, never the Debian version it was built from. A downstream distribution names itself.
3. Keeping Apache's line next to a new one was considered and not taken: the maintainers settled on no Apache release line (release.md). The reason stands: a ChronitonDB line carries Apache fixes ahead of an Apache release and can lag or lead the Apache patch release its build version names, so an Apache line would name a release the node does not contain exactly.

No patents were searched or read.

## 5. Idiom and consistency

User visible choices and what each follows:

1. **The two lines of `nodetool version` on a ChronitonDB node, settled by decision record 0002.** `ReleaseVersion: <release version>`, and `GitSHA: <sha>` only with `--verbose`. Stock match: the labels, the flag and the line count do not change, only the first value. Earlier decision match: release.md names the value "the release version" and says the command shows the git SHA, which it does under the stock flag. Idiom: the Ubuntu and OpenSearch pattern, the fork's version in the existing field. OpenSearch equivalent: `version.number`, which carries OpenSearch's own number by default, and `build_hash`, always present. The two options not taken are in the decision record: both lines always, which changes the line count and makes the stock assertion `stdoutNotContains("GitSHA:")` at `NodeToolTest.java:143` fail, and a new label `ChronitonDB:`, which a script that reads `ReleaseVersion:` would not find.
2. **The yaml key `nodetool_release_version_enabled`, default `true`.** Stock match: the `<thing>_enabled` form of `hinted_handoff_enabled` (`Config.java:112`). Earlier decision match: release.md item 2, a switch on by default. Idiom: conventions.md, a setting named for what it does, no `cassandra` or `axon` in it. OpenSearch equivalent: none, the version output has no switch there.
3. **The commands `enablereleaseversion` and `disablereleaseversion`.** Stock match: the enable and disable pairs, silent on success. Earlier decision match: branching-and-review.md, Feature switches and defaults, item 1 asks for a nodetool toggle. Idiom: lower case, no separator, as every stock command. OpenSearch equivalent: none.
4. **The toggles' failure against a node without the MBean: one line on standard output naming the command, exit code 1.** Stock match: `Status` prints its error to `probe.output().out` and exits 1 (`Status.java:89` to `96`). Earlier decision match: quality-requirements.md, an error names the toggle that controls the behaviour. Idiom: a precondition failure is a short line and exit 1, a broken connection is `error:` and exit 2, as `NodeTool.execute` does. OpenSearch equivalent: none, a command line toggle has no counterpart there.
5. **The MBean `org.chronitondb:type=ReleaseVersion` with `ReleaseVersion` and `Enabled`.** Stock match: `StorageServiceMBean` exposes `ReleaseVersion` as a read only attribute. Earlier decision match: conventions.md, the domain `org.chronitondb`. Idiom: one MBean per feature, the attribute named as stock names the same value. OpenSearch equivalent: `GET /` field `version.number`.
6. **The metric `org.chronitondb.metrics:type=ReleaseVersion,name=Reported`.** Stock match: a Dropwizard counter through `CassandraMetricsRegistry.Metrics.counter` (`CassandraMetricsRegistry.java:55`), with a `MetricName` whose group and MBean name are the fork's (`CassandraMetricsRegistry.java:959` to `975`, the constructor that takes the MBean name). Earlier decision match: conventions.md, fork metrics use their own types and stock types gain nothing. Idiom: a counter's name is a past participle. OpenSearch equivalent: none.
7. **The build value `5.0-chronitondb-SNAPSHOT` for a build made without `chronitondb.version`.** Stock match: `base.version-SNAPSHOT` for a build without `-Drelease` (`build.xml:107`). Earlier decision match: release.md, Version numbers, a release version never carries an Apache patch number, so none is in it. Idiom: Apache's own word for an unreleased build. OpenSearch equivalent: `-SNAPSHOT` on unreleased builds.
8. **The word `Unknown`.** Stock match: `FBUtilities.UNKNOWN_RELEASE_VERSION` (`FBUtilities.java:117`), reused, not copied. Earlier decision match: none touches it. Idiom: stock's own word for a missing build value. OpenSearch equivalent: none, its build never lacks the value.
9. **Stock output, and nothing else, under a JMX role without a grant on the fork MBean.** Stock match: the role gets exactly what it got before the change, on standard output and standard error alike. Earlier decision match: the stock behaviour rule, which binds this case with the switch off too, since the lookup runs before the switch is known. Idiom: a permission decides what a caller sees, it does not make an allowed call fail. The reference page tells an operator who uses JMX authorization to grant the fork MBean to the roles that should see the release version. OpenSearch equivalent: none, a denied `GET /` is a 403 error there and nothing is shown.

## 6. Quality requirements

| ISO/IEC 25010 characteristic | Line | Requirements, or the reason it does not apply |
|---|---|---|
| Performance efficiency | Fastest correct design, with benchmarks in the design and in the gates | Does not apply, because no request path runs the code: one properties load at node start and two to four JMX calls per `nodetool version`. Section 7. |
| Performance efficiency | Memory budgets on coordinator and replica | Does not apply, because the only memory is one `Properties` object of one entry, one MBean and one counter, loaded once, under a kilobyte together. |
| Reliability | Isolation levers on coordinator and replica: thread pools, limits, load shedding, timeouts, kill switch | REQ-3, REQ-8 and REQ-18: the kill switch is the yaml key and the toggle. No thread, pool, limit or timeout exists, because the code does no work outside a JMX call the operator makes. |
| Reliability | Automatic fallbacks opt-in, with yaml setting, nodetool toggle, metric and rate-limited log line | Does not apply, because there is no fallback to a costlier path. REQ-4, REQ-16 and REQ-17 make nodetool print the stock lines when the node has no MBean, the role may not read it or the probe has no connection: that is the stock code path running as it runs today, at the same cost. It has the yaml setting and the toggle. It has no counter and no log line, because it runs in the nodetool process, which has no metrics registry and no log, and the node never sees which line nodetool printed. Section 5 item 9 states the choice and Problem 5 names what an operator sees. |
| Reliability | Coordination between nodes model checked, when the design changes it | Does not apply, because nothing crosses the network but the operator's JMX call to one node. |
| Compatibility | Stock Apache Cassandra behaviour unchanged | REQ-13, REQ-22. Section 3: the one excepted behaviour with its switch, and the four presences every fork switch with a nodetool toggle brings, each in the departures table with its reason. |
| Compatibility | Stock behaviour unchanged with the feature off | REQ-3, REQ-4, REQ-16, REQ-17. The test `VersionOutputTest` compares the off output with the stock output byte for byte. While off the node holds one MBean and one counter under fork names, the toggle's handle, and no file, thread or stock name. |
| Compatibility | Mixed-version cluster, upgrade and rollback (see the Compatibility section) | REQ-4, REQ-10, REQ-19, REQ-23 and the rollback line in section 9. |
| Functional suitability | CQL validity and results independent of replication factor, data centres and replica count | Does not apply, because the change has no CQL and reads no data. |
| Flexibility | Settings per index or per table over global ones, with global, include and exclude modes | Does not apply, because the setting is a property of the node, not of data. |
| Interaction capability | nodetool toggles change the in-memory value only, yaml holds the startup value | REQ-7, REQ-8, REQ-18. The setter writes the `Config` field and nothing else, so no file changes. |
| Interaction capability | Error messages name the setting or toggle that controls the behaviour | REQ-10 and REQ-19 name the command. The switch itself refuses nothing, so it has no error text. |
| Maintainability | Observability: metrics, traces and diagnostics as a gate item | REQ-9, REQ-11, REQ-12. Section 8. |
| Security | Threat model answered (see the Threat model section) | Section 10, with REQ-16 as the one mitigation. |
| Safety | Any risk of data loss or corruption named, with its mitigation | None: the code reads one classpath resource and one `Config` field and writes nothing to disk, to the commit log or to any table. |

The design changes no coordination between nodes, so it carries no model.

## 7. Performance

### Hot path statement

No request type touches the new code. Coordinator reads and writes, replica reads, memtable writes, flush, compaction, streaming and repair never call it. The code runs at node start (one properties load, one MBean registration, one log line), on a JMX read of the MBean, and inside the nodetool process.

### Expected cost

| Path | Metric | Stock today | Expected with the change | Why (mechanism) |
|---|---|---|---|---|
| Node start | wall time | one properties load for `version.properties` | two properties loads | one more `getResourceAsStream` and `Properties.load` of a one entry file, well under a millisecond |
| Node start | heap | one `Properties` object | two `Properties` objects, one MBean, one counter | tens of bytes each, allocated once |
| `nodetool version`, switch on | JMX round trips | 1, or 2 with `--verbose` | 3, or 4 with `--verbose`: `isRegistered`, `getAttribute(Enabled)`, `getAttribute(ReleaseVersion)`, then `getGitSHA` | two more remote calls in the nodetool process, nothing on a request path |
| `nodetool version`, MBean present and switch off | JMX round trips | 1, or 2 with `--verbose` | 3, or 4 with `--verbose`: `isRegistered`, `getAttribute(Enabled)`, then the stock calls | two more remote calls in the nodetool process |
| `nodetool version`, MBean absent | JMX round trips | 1, or 2 with `--verbose` | 2, or 3 with `--verbose`: `isRegistered`, then the stock calls | one more remote call in the nodetool process |

### Isolation levers

The yaml key `nodetool_release_version_enabled` and the toggle pair. Off: `nodetool version` prints stock output and the node does nothing new but hold the MBean and the counter. No thread pool, no memory limit and no timeout exist, since the node runs no work of its own for this feature.

### Benchmarks that prove it

| Claim | Benchmark | Command | Pairs | Threshold |
|---|---|---|---|---|
| none | none, there is no request path to measure | none | none | none |

### Regression threshold and gate

No benchmark gates this pull request. The gate runs the tests of section 14.

### Stock guard

The stock suites of section 14 run unchanged with the switch off and on. No timing claim is made, so no stock run must stay within a number.

### What was not measured

Nothing was measured, because the change is off every request path. No follow-up issue is needed.

## 8. Observability

1. **Counted.** `org.chronitondb.metrics:type=ReleaseVersion,name=Reported`, a counter of reads of the `ReleaseVersion` attribute, by nodetool or any other JMX client, switch on or off (REQ-12). The outcomes of this feature on the node are the reads of that attribute, and each one counts. Nodetool's own choice between the fork line and the stock lines happens in the nodetool process, where no registry exists, and the node does not see it: with the switch off, nodetool reads `Enabled` and prints stock output without reading `ReleaseVersion`, so the counter does not move for that call. The value of the switch is visible as the `Enabled` attribute. The counter is created once with the reporter and held in a final field. The start log line of REQ-11 reads the value directly, not through the attribute, so the counter is 0 right after start.
2. **Timed.** Nothing: no duration to measure.
3. **Logged.** When `register()` registers the MBean, one INFO line `ChronitonDB release version: {}` (REQ-11), after the stock MBean registration in `initServer`. On every write of `Enabled`, one INFO line `Changed nodetool_release_version_enabled from {} to {}` (REQ-9), whether or not the value changed, as the stock setter of `StorageService.java:1925` to `1933` does. On a registration failure, the ERROR line `MBeanWrapper.OnException.LOG` writes. Nothing per request, nothing rate limited, since the operator makes every call.
4. **Traced.** Does not apply: no query runs, so there is no trace session to write to.
5. **Client visible.** The nodetool output itself.
6. **Exposed.** The MBean `org.chronitondb:type=ReleaseVersion` with `ReleaseVersion` and `Enabled`, and the yaml key in `system_views.settings`, which lists every `Config` field (`SettingsTable.java:59` and `154`).
7. **Toggled.** `nodetool enablereleaseversion` and `nodetool disablereleaseversion`, in memory, and the writable `Enabled` attribute they use.
8. **Audited.** Nothing beyond the INFO lines. The toggle changes what nodetool prints, not data or access.
9. **Released on drop.** The MBean and the counter live as long as the node. Nothing drops them, and no release method exists.
10. **Documented.** The reference page in section 13 lists the key, the commands, the MBean and the metric by exact name.
11. **Tested.** `ReleaseVersionReporterTest` and `VersionOutputTest` in section 14 assert the counter, the log lines and the switch. No tracing test, see section 14.

No line above TRACE carries a key, a term, a literal or a secret: the lines carry a version string and a boolean.

## 9. Compatibility

**On-disk format.** None changed. The change writes no file at runtime.

**Mixed-version cluster.** Each node answers for itself. A ChronitonDB nodetool asking an Apache Cassandra node, or a ChronitonDB node from before this change, finds no MBean and prints stock output (REQ-4). An Apache Cassandra nodetool asking a ChronitonDB node runs Apache's `Version.execute`, which reads `StorageServiceMBean.getReleaseVersion()`, and prints Apache's version string, unchanged (REQ-13). Nothing new goes into gossip, schema, messages or sstables, so nodes of both kinds coexist as today. A node that is still starting, before `initServer` registered the MBeans, answers `Server is not initialized yet` to both nodetools, as stock does today.

**Upgrade path.** None needed. The feature is on by default and needs no yaml change.

**Rollback path.** Before a node runs an Apache Cassandra binary again, the operator removes `nodetool_release_version_enabled` from its `cassandra.yaml` if it was written there, because Apache's loader refuses an unknown key and the node does not start (`YamlConfigurationLoader.java:423`). A node that never wrote the key into its yaml needs nothing. The reference page and `NEWS-chronitondb.txt` carry this line (REQ-23). There is no runbook page on this line yet, see section 15.

**Surfaces touched and their versions.** Command line tools and arguments: the output of `nodetool version` on a node with the switch on, and two new commands, no stock command renamed, `nodetool help` lists two more. Configuration: one new key, which `ConfigCompatibilityTest` accepts, since it checks that no past key disappears (`test/unit/org/apache/cassandra/config/ConfigCompatibilityTest.java:166` to `192`). JMX MBeans and metrics: one new MBean and one new metric under fork domains, no stock name changed. Virtual tables: one new row in `system_views.settings`, section 3. Gossip, messaging, native protocol, sstables, commit log, hints, caches and operational routines: untouched, with the stock suites of section 14 passing unchanged as the proof.

**What the switch writes to shared state.** Nothing, off or on.

**The other lines.** This item targets `chronitondb-sandbox` only. On the 6.0 line nodetool is picocli, so the two toggle commands and the hook in `Version` are written again. The node side ports as it is. The build side ports with one change, the default value `6.0-chronitondb-SNAPSHOT`.

## 10. Threat model and security

New entry points, each checked with STRIDE:

1. **The yaml key.** Input: a boolean parsed by snakeyaml into a `Config` field, like every other key. Bound: `true` or `false`, anything else fails yaml loading as stock does. Spoofing, tampering, repudiation: the file is the operator's, as every key. Information disclosure, denial of service, elevation: none, the key picks one of two output values. No mitigation needed beyond stock, no permission.
2. **The MBean `org.chronitondb:type=ReleaseVersion`.** Input: `setEnabled(boolean)` over JMX. Bound: a boolean. Spoofing and elevation: JMX authentication and the stock `AuthorizationProxy` apply to every MBean, this one included (`AuthorizationProxy.java:79`, `144` and `192`): the setter needs the stock `MODIFY` permission on this MBean, the reads `SELECT` and the lookup `DESCRIBE` (`AuthorizationProxy.java:418` to `437`), no new permission. A role without them gets `SecurityException` from the toggles, as from any stock command without a grant, and stock output from `nodetool version` (REQ-16). The stock `AuthorizationProxyTest` runs unchanged as the proof that the proxy guards MBeans by name, and `VersionOutputFallbackTest` proves REQ-16. Information disclosure: the attribute exposes a release version, which is the package version, readable by whoever can read the package list on the host. Nothing new leaks. Repudiation: every write logs at INFO. Denial of service: reading one string cannot load the node. Tampering: the setter writes one boolean of the running node, gone at restart.
3. **The two nodetool commands.** Input: none, no arguments. They call the setter above under the same JMX rules.
4. **The properties file.** Input: a classpath resource inside the jar the build wrote. An attacker who can replace a jar can replace any class, so the file adds no new surface.

Audit entries: the INFO lines of section 8. Limits: none, no threshold exists. Errors to client errors: none, there is no client. The toggle against a node without the MBean fails with exit code 1 and the line of REQ-10 or REQ-19.

## 11. Dependencies

No new dependency. The code uses the JDK's JMX classes, Apache's `MBeanWrapper`, `CassandraMetricsRegistry` and airline, which the tree already ships. The tests use JUnit and the stock test classes.

## 12. Compliance impact

Copies of data: none, no user data is read or written. Erasure, minimisation, masking: nothing applies, the value is a version string. Access control: the JMX rules of section 10. Audit: the INFO lines. Logging: INFO lines at registration and on each write of the switch, no personal data. Cryptography: none. Data residency, backups and snapshots: untouched. Supply chain: no new library. Secure defaults: the default `true` shows the version an operator can read from the package anyway. Retention: nothing is stored. Isolation levers: the switch.

For operators: the setting `nodetool_release_version_enabled` in `cassandra.yaml`, default `true`, decides whether `nodetool version` prints the node's ChronitonDB release version or Apache Cassandra's version string. `nodetool disablereleaseversion` turns it off until the next restart, `nodetool enablereleaseversion` turns it on. Remove the key from `cassandra.yaml` before the node runs an Apache Cassandra binary.

## 13. Documentation

No documentation page exists on this line yet, and [conventions.md, Where things live](../../process/conventions.md#where-things-live) has no row for documentation pages, so this item proposes the first reference page at `docs/reference/release-version.md`, written by the developer from the skeleton `page-release-version.md` next to this record, because documentation ships in the same pull request as the code (conventions.md, Where things live, item 5). The maintainers approve the path with this record, and a later item moves the page when a layout is decided. The page is a reference page in the Diátaxis sense and carries:

1. `nodetool version`: the output with the switch on, with and without `--verbose`, and the stock output with it off or against an Apache Cassandra node.
2. The yaml key `nodetool_release_version_enabled`: type boolean, default `true`, runtime change through the two commands, in memory only.
3. The commands `nodetool enablereleaseversion` and `nodetool disablereleaseversion`: synopsis, what they change, in memory only, silent on success, the line and exit code of REQ-10 and REQ-19 against a node without the MBean.
4. The MBean `org.chronitondb:type=ReleaseVersion` with its attributes `ReleaseVersion` and `Enabled`, and the JMX permissions a role needs to see the fork output under JMX authorization.
5. The metric `org.chronitondb.metrics:type=ReleaseVersion,name=Reported`: counter, counts reads of the release version, no alert threshold.
6. The build property `chronitondb.version` and the value `5.0-chronitondb-SNAPSHOT` of a build made without it.
7. Failure behaviour: `Unknown` when the properties file or its value is missing, stock output against a node without the MBean or under a role without a grant on it, the exit code 1 line of the toggles.
8. Known limitations: `bin/cassandra -v`, the start log line `Cassandra version:` and the cqlsh banner show Apache's version, by release.md item 5.
9. The rollback line: remove the key from `cassandra.yaml` before running an Apache Cassandra binary (REQ-23).

`NEWS-chronitondb.txt` is created with its first entry, since the line has none yet and conventions.md, Change logs and release notes, item 2 says it is written in the pull request that makes the change: the new output of `nodetool version`, the key, and the rollback line (REQ-23). The delta entry `docs/delta/nodetool-version-shows-release-version.md` with its row in `docs/delta/README.md` records the stock edits. `docs/process/release.md` item 4 still says the feature is not built yet: a process page changes only through the documentation only path (governance.md, Changes to this page), so that edit is a follow-up, not part of this item.

## 14. Testing

Unit tests under `test/unit/org/chronitondb/`, on real JMX where nodetool is involved. Nothing is multi node in behaviour, each node answers for itself, so replication factor does not apply. The in-JVM distributed framework runs nodetool with no JMX connection, so it cannot exercise this feature and this item adds no distributed test. No sstable format or compaction is touched. The parity suite does not exist on this line yet. This item is not an item of a fork feature, so it has no scenarios, and the template's `Scenario runner` and `Scenario tags` lines are left out. The two stock lists below relate as follows: Existing suites at risk names the stock suites whose files or behaviour this change touches, which the gate runs first, and Stock suites run unchanged is the wider set that proves stock behaviour with the switch off and on, and includes the first.

What each test of the list under Tests for this change proves:

1. `ReleaseVersionTest`: `readsTheKeyFromTheResource`, `ReleaseVersion.fromClasspath().value()` equals the `ReleaseVersion` value of the resource `org/chronitondb/version.properties`, read again by the test with `getResourceAsStream` (REQ-5). `buildWritesTheAntProperty`, that value equals the system property `chronitondb.version` the test macro forwards from the build (REQ-20). `defaultIsSnapshot`, when the forwarded `chronitondb.version.given` is `false`, which it is in the gate and in CI, the value equals `5.0-chronitondb-SNAPSHOT`, and the test is skipped with a JUnit assumption when a value was given (REQ-21). `missingValueIsUnknown`, a `ReleaseVersion` built from an empty `Properties`, from one whose `ReleaseVersion` is empty, from one whose value is spaces only, and from a resource name that does not exist, each returns `Unknown` (REQ-6).
2. `ReleaseVersionReporterTest`: `registerTwiceRegistersOnce`, `register()` registers `org.chronitondb:type=ReleaseVersion`, and a second call leaves one MBean, throws nothing and logs nothing, no ERROR line from the wrapper and no second start line (REQ-15). `switchDefaultsToOn`, the default of `nodetool_release_version_enabled` is `true` (REQ-7). `writeLogsOldAndNewValue`, `setEnabled(false)` makes `isEnabled()` and `DatabaseDescriptor.getRawConfig().nodetool_release_version_enabled` `false` and logs the line with the old and the new value, and `setEnabled(false)` again logs it again (REQ-9). `readCountsReported`, each read of `getReleaseVersion()` raises the counter `Reported` by one, with the switch on and with it off, asserted as a difference from the value read before (REQ-12). `reporterStaysRegisteredWhenOff`, the MBean stays registered after `setEnabled(false)` (REQ-14). `registerLogsReleaseVersion`, `register()` on a node without the MBean logs the start line with the release version (REQ-11). The log lines are asserted through the logback appender the stock tests use.
3. `VersionOutputTest`, on `CQLTester` with `requireNetwork()`, which runs `StorageService.instance.initServer()` and so the registration hook (`test/unit/org/apache/cassandra/cql3/CQLTester.java:613` to `636`), `startJMXServer()` (`CQLTester.java:373`) and `ToolRunner.invokeNodetool`, which runs `bin/nodetool` as its own process against that JMX server (`test/unit/org/apache/cassandra/tools/ToolRunner.java:184` to `192`, `CQLTester.java:541` to `548`), so `System.exit` in a toggle is safe: `versionPrintsReleaseVersion`, `version` prints exactly `ReleaseVersion: ` plus `ReleaseVersion.fromClasspath().value()` and a newline (REQ-1). `verbosePrintsGitSha`, `version --verbose` prints that line and `GitSHA: ` plus `FBUtilities.getGitSHA()` (REQ-2). `disableSetsSwitchOff`, after `disablereleaseversion` the switch is `false` (REQ-18). `switchOffPrintsStockOutput`, with the switch off `version` and `version --verbose` print exactly the stock output, built from `FBUtilities.getReleaseVersionString()` and `getGitSHA()` (REQ-3). `enableSetsSwitchOn`, after `enablereleaseversion` the switch is `true` (REQ-8). `apacheVersionStringUnchanged`, `probe.getReleaseVersion()` equals `FBUtilities.getReleaseVersionString()` with the switch on and off (REQ-13). With the MBean unregistered through `MBeanWrapper.instance.unregisterMBean` for one test and put back with `register()` after it: `nodeWithoutReporterPrintsStockOutput`, `version` prints stock output (REQ-4), `enableAgainstNodeWithoutReporterFails`, `enablereleaseversion` exits with code 1 with the one line of REQ-10 on standard output (REQ-10), and `disableAgainstNodeWithoutReporterFails`, the same for `disablereleaseversion` and the line of REQ-19 (REQ-19).
4. `VersionOutputFallbackTest`: a `NodeProbe` subclass on the protected constructor (`NodeProbe.java:233`) whose `connect()` sets `mbeanServerConn` to a `java.lang.reflect.Proxy` stub of `MBeanServerConnection` and `ssProxy` to a stub `StorageServiceMBean` with fixed version and SHA strings, and `output()` to streams the test reads. Each test runs `new Version().execute(probe)` with and without `--verbose` and compares standard output with the two stock lines built from the stub's strings: `accessDeniedPrintsStockOutput`, three stubs, one that throws `SecurityException` on `isRegistered`, one that answers `true` there and throws on `getAttribute("Enabled")`, and one that throws on `getAttribute("ReleaseVersion")` only, each prints exactly the stock output and nothing on standard error (REQ-16). `noConnectionPrintsStockOutput`, `mbeanServerConn` left `null`, exactly the stock output (REQ-17). `otherFailurePropagates`, a stub that throws `IOException` on `isRegistered`, `execute` throws it (REQ-24).

REQ-22 is proven by the stock suites below running unchanged, `NodeToolTest.testVersionIncludesGitSHAWhenVerbose` first among them, and by the gate's check that no pre-existing test changed. REQ-23 has no automated test, see `ac-coverage.md`.

### Tests for this change

org.chronitondb.version.ReleaseVersionTest
org.chronitondb.version.ReleaseVersionReporterTest
org.chronitondb.tools.nodetool.VersionOutputTest
org.chronitondb.tools.nodetool.VersionOutputFallbackTest

### Existing suites at risk

org.apache.cassandra.distributed.test.NodeToolTest
org.apache.cassandra.tools.GetVersionTest
org.apache.cassandra.config.ConfigCompatibilityTest
org.apache.cassandra.db.virtual.SettingsTableTest
org.apache.cassandra.service.StorageServiceTest

### Stock suites run unchanged

org.apache.cassandra.distributed.test.NodeToolTest
org.apache.cassandra.tools.GetVersionTest
org.apache.cassandra.config.ConfigCompatibilityTest
org.apache.cassandra.config.YamlConfigurationLoaderTest
org.apache.cassandra.config.DatabaseDescriptorTest
org.apache.cassandra.db.virtual.SettingsTableTest
org.apache.cassandra.service.StorageServiceTest
org.apache.cassandra.tools.nodetool.GetAuditLogTest
org.apache.cassandra.auth.jmx.AuthorizationProxyTest
org.apache.cassandra.metrics.CassandraMetricsRegistryTest

### Tracing test

does not apply, because no query runs through the change, so there is no trace session to show it in

### Formats and configurations

no

## 15. Not covered and follow-ups

1. `bin/cassandra -v`, the start log line `Cassandra version:` and the cqlsh banner stay as they are, by release.md item 5, which says any change to them is decided in its own feature spec. Their files are not in the Planned file list, and `GetVersionTest` runs unchanged.
2. The node version `<Apache version>+chronitondb.<feature level>` in gossip and `system.local` is a separate behaviour-changing feature with its own switch, off by default, by release.md, The version a running node reports. Nothing here touches `FBUtilities.getReleaseVersionString()`.
3. `conf/cassandra_chronitondb.yaml` does not exist on this line. When the item that creates it lands, the key goes into it, commented out with its default, as release.md, The configuration file, says. Candidate issue.
4. Tests on a built package. Release.md item 3 says the feature's tests prove the version and the git SHA on a built package. No package exists on this line: `packaging/` is not created yet (release.md, Packaging, item 1). This item proves both on the built jar, which is what a package wraps, and the package test is owed by the packaging item, since the feature and the packaging both block a line's first release. This split changes what item 3 asks of this item, so it is a question for the maintainers, posted on the item, and this record follows their answer.
5. The release pipeline that passes `-Dchronitondb.version` does not exist. Until it does, every build shows `5.0-chronitondb-SNAPSHOT`.
6. A runbook page for the rollback to Apache Cassandra does not exist on this line. The rollback line lives on the reference page and in `NEWS-chronitondb.txt` until the runbook item creates it.
7. The 6.0 port, which rewrites the two toggle commands and the `Version` hook for picocli and changes the build default to `6.0-chronitondb-SNAPSHOT`.
8. The metrics reference page generated from the registry, with its doc test, does not exist yet. The reference page of section 13 lists the metric by hand until then.
9. `docs/process/release.md` item 4 says the feature is not built yet. After the code merges, a documentation only change updates it, as governance.md, Changes to this page, requires. Candidate issue.
10. The Red Hat package has no shell completion file on this line, so only the Debian completion list gains the two commands.

## New terms

1. **Release version**: the ChronitonDB version of an installed build, `<line>-chronitondb<n>`, as release.md defines it, or `5.0-chronitondb-SNAPSHOT` on a build made without one. In code `ReleaseVersion`, in yaml `nodetool_release_version_enabled`, in docs "release version".
2. **Release version reporter**: the node side object behind the MBean `org.chronitondb:type=ReleaseVersion`. In code `ReleaseVersionReporter`, in the lines of REQ-10 and REQ-19 "release version reporter".

## Where problems could occur

1. **A script that parses `nodetool version` reads a ChronitonDB value where it expected an Apache one.** Seen by an operator whose tooling compares the first line with an Apache version pattern, on every node with the switch on, which is every node by default. From the output change of REQ-1. Decision record 0002 settles the line, and the switch is the way out for an operator who needs the old line.
2. **A node rolled back to an Apache Cassandra binary does not start.** Seen as `Invalid yaml. Please remove properties [nodetool_release_version_enabled] from your cassandra.yaml` at start, on a node whose operator wrote the key into the yaml. From the new `Config` field. Not from the default: a yaml that never names the key loads on both binaries.
3. **The MBean registration throws, or runs twice.** Seen as an ERROR line at start, or two ERROR lines when `initServer` runs twice, as it does in tests. From the hook in `StorageService`. The stock wrapper turns a failure into a logged error (`MBeanWrapper.java:176` to `185`), and REQ-15 keeps a second call silent.
4. **The build writes a wrong, empty or missing value, or writes it where the classes and the IDE do not see it.** Seen as `ReleaseVersion: Unknown`, a value the pipeline did not intend, or a test that fails only in the IDE. From the `build.xml` edit or a pipeline passing the wrong property. REQ-6, REQ-20 and REQ-21 make the missing, empty and wrong cases visible rather than a crash or a blank line, and the file lives where the stock file lives.
5. **`nodetool version` fails, or quietly prints Apache's version, where stock worked.** Seen as `error: Access Denied` from nodetool, by a JMX role that may read `StorageService` but not the fork MBean, against ChronitonDB and Apache nodes alike, since the lookup runs before the node kind is known. Seen as a `NullPointerException` in the in-JVM distributed tests, where the probe has no connection. Seen as Apache's version, with nothing to say why, by an operator whose role was not granted the fork MBean, who then cannot tell a node that is not upgraded from a grant that is missing. From the `isRegistered` and `getAttribute` calls in `ReleaseVersionProbe`. REQ-16 and REQ-17 turn the first two into stock output, REQ-24 keeps every other failure as stock reports it, and the reference page tells the operator which permissions the role needs.
6. **The MBean is registered under a name the JMX server does not accept, or the interface is not a Standard MBean.** Seen as an ERROR at every start and stock output from every nodetool, with no test failing if the test reads the reporter in process. From `ReleaseVersionReporter` and its interface name.
7. **An operator cannot tell what a node's switch is, when it changed, or which release version the node read.** Seen during an upgrade as a node that prints Apache's version with no trace of who turned the switch off, or as a node whose build value nobody can check without nodetool. From the toggle and the build value being invisible. REQ-9 logs every write with both values, REQ-11 logs the value at start, REQ-12 counts the reads, and the `Enabled` attribute shows the current value.
8. **A toggle runs against an Apache Cassandra node in a mixed cluster.** Seen as a stack trace from `InstanceNotFoundException` or a silent exit, by an operator who runs the toggle on every node of a cluster that is half upgraded. From the two commands. REQ-10 and REQ-19 make that one line and exit code 1.
9. **The Apache version string changes for other nodes and drivers.** Seen as drivers or peers that treat the node as a pre-release of 5.0.0 (release.md, The version a running node reports, item 2). From any edit to `FBUtilities.getReleaseVersionString()` or `StorageService.getReleaseVersion()`. Neither file is in the Planned file list for that purpose, and REQ-13 pins it.
10. **A clean clone does not build, or ships the generated file.** Seen as `ant generate-idea-files` failing on a missing directory, `git status` showing an untracked generated file, or the source artifact carrying it. From the build edit. The `mkdir`, the `.gitignore` line, the `clean` delete and the artifact exclude follow the stock file's handling.
11. **The feature cannot be turned on again after it was turned off.** Seen as `nodetool enablereleaseversion` failing with `InstanceNotFoundException` on a node where the switch is off. From an MBean that is registered only while on. REQ-14 keeps it registered, and REQ-8 and REQ-18 set the value through it.

### Test plan

1. Problem 1: `VersionOutputTest.versionPrintsReleaseVersion` and `switchOffPrintsStockOutput` pin the exact on and off output, so the change is deliberate and visible, and decision record 0002 fixes the line. No test can make a third party script agree with the choice. Watched through the reference page and the `NEWS-chronitondb.txt` entry.
2. Problem 2: no test on this line can start an Apache binary. `YamlConfigurationLoaderTest` and `ConfigCompatibilityTest` run unchanged to show the key loads here. Watched through the rollback line of REQ-23 in the docs and the news file, which the docs review checks.
3. Problem 3: `ReleaseVersionReporterTest.registerTwiceRegistersOnce` calls `register()` twice and asserts one MBean and no ERROR line.
4. Problem 4: `ReleaseVersionTest` reads the file the build wrote, compares it with the value the build was given, checks the default, and proves `Unknown` for a missing resource, a missing key and a blank value.
5. Problem 5: `VersionOutputFallbackTest` makes the connection throw `SecurityException` at each of the three calls, leaves it `null`, and makes it throw `IOException`, and asserts stock output for the first four and the exception for the last. `NodeToolTest` runs unchanged over the in-JVM framework.
6. Problem 6: `VersionOutputTest.versionPrintsReleaseVersion` runs `bin/nodetool` over real JMX against the node's JMX server, so a registration that silently fails makes it print stock output and fail.
7. Problem 7: `ReleaseVersionReporterTest.writeLogsOldAndNewValue`, `registerLogsReleaseVersion` and `readCountsReported` assert the two log lines and the counter.
8. Problem 8: `VersionOutputTest.enableAgainstNodeWithoutReporterFails` and `disableAgainstNodeWithoutReporterFails` assert the line and the exit code against a node whose MBean was unregistered.
9. Problem 9: `VersionOutputTest.apacheVersionStringUnchanged` compares `probe.getReleaseVersion()` with `FBUtilities.getReleaseVersionString()` with the switch on and off, and `GetVersionTest` runs unchanged.
10. Problem 10: no unit test runs `ant` from a clean clone. The gate's build runs `_createVersionPropFile` through `build-project` on every commit, and `.build/run-tests.sh` runs it alone before the tests, so a missing directory fails the gate. Watched through the reviewer's check of the `build.xml` diff against the stock file's four places.
11. Problem 11: `ReleaseVersionReporterTest.reporterStaysRegisteredWhenOff` and `VersionOutputTest.enableSetsSwitchOn` after `disableSetsSwitchOff`.

## Planned file list

```
.gitignore stock
build.xml stock
debian/nodetool-completion stock
src/java/org/apache/cassandra/config/Config.java stock
src/java/org/apache/cassandra/service/StorageService.java stock
src/java/org/apache/cassandra/tools/NodeTool.java stock
src/java/org/apache/cassandra/tools/nodetool/Version.java stock
src/java/org/chronitondb/version/ReleaseVersion.java new
src/java/org/chronitondb/version/ReleaseVersionReporterMBean.java new
src/java/org/chronitondb/version/ReleaseVersionReporter.java new
src/java/org/chronitondb/tools/nodetool/ReleaseVersionProbe.java new
src/java/org/chronitondb/tools/nodetool/VersionOutput.java new
src/java/org/chronitondb/tools/nodetool/EnableReleaseVersion.java new
src/java/org/chronitondb/tools/nodetool/DisableReleaseVersion.java new
test/unit/org/chronitondb/version/ReleaseVersionTest.java test
test/unit/org/chronitondb/version/ReleaseVersionReporterTest.java test
test/unit/org/chronitondb/tools/nodetool/VersionOutputTest.java test
test/unit/org/chronitondb/tools/nodetool/VersionOutputFallbackTest.java test
docs/reference/release-version.md new
docs/delta/nodetool-version-shows-release-version.md new
docs/delta/README.md edit
NEWS-chronitondb.txt new
docs/design/67-let-operators-see-a-node-s/ac-coverage.md edit
```

`build.xml` and `.gitignore` are protected paths. They are listed because the value comes from the build (release.md item 3), and the stock build already writes and ignores the stock values from the same places. The Java classes under `org.chronitondb`: `ReleaseVersion` reads the properties, `ReleaseVersionReporterMBean` is the JMX interface, `ReleaseVersionReporter` implements it, holds the switch and the counter and registers itself, `ReleaseVersionProbe` finds the MBean through a `NodeProbe` for the three commands, `VersionOutput` prints the lines, and the two commands toggle the switch.

### Shared with open items

None.

### Waivers

None.

## Requirement quality checklist (ISO/IEC/IEEE 29148)

Each of REQ-1 to REQ-24 was checked against the seven qualities before this record went to review:

1. **Necessary:** each traces to an acceptance criterion, a problem named in Where problems could occur, or decision record 0002. Where a process page shapes the requirement, the source names it after the criterion or problem.
2. **Unambiguous:** each names exact text, an exact key, an exact MBean or an exact value, and "stock output" is defined in section 1. No "fast" or "large" appears.
3. **Singular:** one key word and one EARS shape each. The two toggles have their own ids, REQ-8, REQ-18, REQ-10 and REQ-19, and the build and the node sides are REQ-20, REQ-21 and REQ-5.
4. **Verifiable:** each has one row in `ac-coverage.md` naming its test, or for REQ-23 the reason it has none.
5. **Feasible:** each mechanism is cited with file and line in sections 1 and 3, or is the new code of the Planned file list.
6. **Consistent:** REQ-3, REQ-4, REQ-13, REQ-16, REQ-17 and REQ-22 keep stock behaviour, REQ-1 and REQ-2 change only the excepted output, and none contradicts release.md or decision record 0002.
7. **Traceable:** each has an id, a source and exactly one coverage row.
