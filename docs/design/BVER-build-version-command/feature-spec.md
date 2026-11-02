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

# Feature spec: Build version command

| Field | Value |
|---|---|
| Title | Build version command |
| Document type | Specification and description (ISO/IEC/IEEE 15289) |
| Status | Draft |
| Version | 1 |
| Author | Architect: chronitondb-agent |
| Approver | The maintainer who merges the pull request |
| References | Line `chronitondb-sandbox` at `1cb54f6e83`, Apache base `cassandra-5.0` at `76550e9314` with `base.version` 5.0.10, decision record [0002](../../decisions/0002-build-version-command-shape.md), [additive.md](../../process/additive.md) |

Change history: the git history of this file.

Location: `docs/design/BVER-build-version-command/feature-spec.md` on the `chronitondb-sandbox` line, with the [feature key](../../process/additive.md#feature-keys-and-requirement-ids) `BVER` in the directory name. Process: [additive.md](../../process/additive.md).

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in BCP 14 (RFC 2119, RFC 8174) when, and only when, they appear in all capitals, as shown here.

## 1. Purpose and scope

ChronitonDB is a fork of Apache Cassandra, and its builds carry a version of their own, `<Apache version>-chronitondb<n>`, next to the Apache version they contain ([release.md](../../process/release.md#version-numbers)). Nothing in the build or in a running node knows that version today: the build writes only Apache's `CassandraVersion` and `GitSHA` into `version.properties` (`build.xml:492` to `499`), and `nodetool version` prints only Apache's release version (`src/java/org/apache/cassandra/tools/nodetool/Version.java:36`). An operator rolling a cluster from one ChronitonDB release to the next cannot ask a node which ChronitonDB build it runs.

This feature adds that. The build writes a `ChronitonDBVersion` entry next to Apache's, a node serves it over JMX from an MBean in the `org.chronitondb` domain, and the new command `nodetool chronitondbversion` prints it as one line, for example `ChronitonDBVersion: 5.0.10-chronitondb1`, for the node it connects to. The command takes the global options every nodetool command takes, host, port, user name, password, password file and print port (`src/java/org/apache/cassandra/tools/NodeTool.java:351` to `367`), and no option of its own, and asks one node, as `nodetool version` does.

A line is a trunk of the fork per Apache major version ([branching-and-review.md](../../process/branching-and-review.md#the-lines)). This feature targets the `chronitondb-sandbox` line only, the throwaway line of the process dry run, and exists to exercise the development process end to end on it. The line has no release, so the feature passes its final gate like any other feature and reaches no user. No other line gets it.

In scope: the version entry, the `BuildVersion` class with its MBean, the three commands (`nodetool chronitondbversion` and the two toggles), the switch with its yaml setting and toggles, the counters and the log line the checklist of quality-requirements.md asks for, the tests, and the reference documentation.

### Non-goals

1. Printing Apache's release version or the git SHA from this command. `nodetool version` prints them already (`Version.java:36` and `:38`), and the chosen shape is one line (decision record 0002). The command has no `-v` option. Nodetool refuses one through its stock usage error.
2. Changing what `nodetool version`, `bin/cassandra -v`, `system.local`, gossip or the drivers report. Those carry Apache's release version today and are stock behaviour. The node reported version form of [release.md](../../process/release.md#the-version-a-running-node-reports), a planned second string `<Apache version>+chronitondb.<feature level>` that a node will report in those places, is a separate feature.
3. Reporting the version of the nodetool jar itself. The command reports the node it connects to, as every nodetool command does (decision record 0002).
4. A virtual table, a cqlsh command or a native protocol change carrying the version. Nobody asked for one. The switch appears as a row of `system_views.settings` like every `Config` field, see section 2.6, and that row carries the switch, not the version.

## 2. Architecture

### 2.1 Context and scope

The operator's nodetool talks to one node over JMX, as for every nodetool command (`NodeTool.java:390` and `:444`). The node answers from a string it read from `version.properties` through its own class loader. No other node, client or external system is involved.

### 2.2 Building blocks

| Block | Where | Interface |
|---|---|---|
| Version entry | `build.xml`, target `_createVersionPropFile` (`build.xml:492` to `499`), which writes `version.properties` under `${build.src.resources}/org/apache/cassandra/config/` (`build.xml:108` to `109`). From there the file reaches the class path: the jar of a release, the classes directory of a test run | The entry `ChronitonDBVersion` in `org/apache/cassandra/config/version.properties`, next to `CassandraVersion` and `GitSHA` |
| The `BuildVersion` class | The package `org.chronitondb.version` under `src/java/`: one class, `BuildVersion`, its MBean interface `BuildVersionMBean`, and the two refusals as nested classes of `BuildVersion` | `BuildVersion` loads the entry, holds the gate field, checks the switch on each version read, sets the switch off at startup while the gate field is false, holds the two counters as fields, and implements the MBean `org.chronitondb:type=BuildVersion` with the read attribute `Version` and the read and write attribute `Enabled`. It is registered through `MBeanWrapper` (`src/java/org/apache/cassandra/utils/MBeanWrapper.java:90` to `98`) from `StorageService.initServer`, see section 2.3 |
| Switch | The `Config` field `build_version_command_enabled` (`src/java/org/apache/cassandra/config/Config.java`), a `volatile` primitive `boolean` like `hinted_handoff_enabled` (`Config.java:112`), with the initial value `true` | The yaml setting of the same name, set into the field by the stock yaml loader at startup, and the `Enabled` attribute, which `BuildVersion` reads and writes on the `Config` object that `DatabaseDescriptor.getRawConfig()` returns (`src/java/org/apache/cassandra/config/DatabaseDescriptor.java:385` to `388`), so `DatabaseDescriptor` is not changed |
| Commands | The package `org.chronitondb.tools.nodetool` under `src/java/`, three `NodeToolCmd` classes registered in nodetool's command list (`NodeTool.java:243` to `252`) | `nodetool chronitondbversion`, `nodetool enablebuildversioncommand`, `nodetool disablebuildversioncommand`. They reach the MBean through the JMX connection `NodeProbe` exposes (`src/java/org/apache/cassandra/tools/NodeProbe.java:772` to `775`), so `NodeProbe` itself is not changed |
| Counters | Two `Counter` fields of `BuildVersion`, registered by it alongside the MBean as MBeans of their own that the stock metrics registry creates, in every switch state | Two counters of the metric type `BuildVersion`, a type of ChronitonDB's own so that no stock type gains a metric (Names rule 4 of [conventions.md](../../process/conventions.md#names)), in the JMX domain `org.chronitondb`, the domain of every ChronitonDB MBean (Names rule 3), so that no user facing name of the feature contains `cassandra` (Names rule 1). Their MBean names are `org.chronitondb:type=BuildVersion,name=ReadsServed` and `org.chronitondb:type=BuildVersion,name=ReadsRefused`, with no scope part. The stock registry takes a metric's MBean name as a string through the five argument `MetricName` constructor (`src/java/org/apache/cassandra/metrics/CassandraMetricsRegistry.java:818`), which is how the stock name factory places stock metrics under its own domain (`src/java/org/apache/cassandra/metrics/DefaultNameFactory.java:26` and `:47` to `68`), so `BuildVersion` builds its two names the same way with the fork's domain and the registry's `counter` method registers each (`CassandraMetricsRegistry.java:55` to `58`). The stock factory is not used, and the registry's own name builder is not either, since it quotes every part of the name (`CassandraMetricsRegistry.java:959` to `964`). Whether a fork metric also appears under the stock domain through the registry's alias (`CassandraMetricsRegistry.java:63` to `68`) is left to the first feature on a line with a release, and nothing on this line binds it |
| Lift | The package `org.chronitondb.version` under `test/distributed/`: the class `BuildVersionLift`, an instance initializer of the in-JVM distributed test framework | Registered on a cluster's builder before the cluster starts, it sets the gate field of `BuildVersion` to true, by reflection on the non final static field, inside each instance's class loader before the instances start. Test code only, see section 2.5 |

### 2.3 Runtime view

1. Build: every target that runs `_createVersionPropFile` writes `ChronitonDBVersion=<Apache version>-chronitondb<n>` into `version.properties`. `<Apache version>` is the `base.version` property (`build.xml:36`), never the `${version}` form, which stock writes into `CassandraVersion` and which carries `-SNAPSHOT` unless the `release` property is set (`build.xml:104` to `107`). The two properties are independent: a build with neither `release` nor `chronitondb.release` set writes `5.0.10-chronitondb0` next to `5.0.10-SNAPSHOT`. `<n>` is the release number, the value of the ant property `chronitondb.release` from any ant property source, for example the command line `-Dchronitondb.release=1` or `build.properties` (`build.xml:30` to `31`), with the white space around it trimmed. The property unset, empty or made of white space only gives `0`. A trimmed value that is not a release number, as the glossary defines it, fails the build inside `_createVersionPropFile` with an error that names the property, so only a target that writes the entry fails. The build trims and checks the value by the glossary's definitions, and the ant mechanism that does so is the design record's. The entry carries the trimmed value. The entry does not tell a build given `0` from a build given no number, and nothing else marks either case. A release always has a release number of 1 or more ([release.md](../../process/release.md#version-numbers)), so `0` names an unreleased build.
2. Startup: `StorageService.initServer` (`src/java/org/apache/cassandra/service/StorageService.java:967` to `971`), which a real node reaches through `CassandraDaemon.setup` (`src/java/org/apache/cassandra/service/CassandraDaemon.java:383`), an in-JVM test instance calls only when it starts with the framework's GOSSIP feature (`test/distributed/org/apache/cassandra/distributed/impl/Instance.java:704` and `:709`, the other branch at `:723` to `:740` ends in `completeInitialization` and never calls it) and the unit test JVM calls when a test starts its services (`test/unit/org/apache/cassandra/cql3/CQLTester.java:633` to `638`), creates `BuildVersion`, one object per node, and a second call of `initServer` in the same JVM reuses it. That call is the node start of the glossary. An in-JVM instance started without GOSSIP has no `BuildVersion` and no MBean, so every in-JVM distributed test of this feature starts its instances with the GOSSIP and JMX features (FREQ-BVER-023). By then the stock yaml loader has set the switch to its yaml value. The yaml value is the only startup source of the switch. While the gate field is false, `BuildVersion` first sets the switch to false, whatever the yaml value, and logs that at INFO with the old and the new value, also when both are false. That is the only startup log line of the feature: while the gate field is true the switch keeps the yaml value and nothing logs it. Only after that step does `BuildVersion` register the MBean and the two counters, so no read is served before the step has run. The gate field and that startup step stay in the code after the gate field turns true, and the step then does nothing.
3. Version read: the switch check and the counters sit inside `BuildVersion`, so every caller of its version read, over JMX or by a Java call, is refused and counted alike. Shipped code has no Java caller of it. On the first read the switch serves, `BuildVersion` loads `version.properties` through its own class loader, `BuildVersion.class.getClassLoader()`, as `FBUtilities` does for Apache's keys (`src/java/org/apache/cassandra/utils/FBUtilities.java:444`), with hand written one time loading code of its own, since the memoized supplier `FBUtilities` uses is private to it (`FBUtilities.java:443` to `458`), and with one load even when two first reads arrive at once. The loader takes the properties stream as its input, so a unit test feeds it each case of FREQ-BVER-006 without a served read. The node's version is then the trimmed value of the entry, or `Unknown` when the node cannot read one, and `BuildVersion` keeps it for the life of the node with no later retry. It logs nothing about the load in any case, since the value `Unknown` makes a missing entry visible. A refused read loads nothing and logs nothing: the counter records it. `nodetool chronitondbversion` connects and reads `Version`. With the switch on the node returns the node's version and counts `ReadsServed`, and the command prints `ChronitonDBVersion: ` followed by it on stdout and exits with status 0. With the switch off the node answers with the read refusal and counts `ReadsRefused`, and the command prints nothing on stdout and reports the refusal through the stock error path, with the node's message, which names the setting, in the text on stderr.
4. Toggles: `nodetool enablebuildversioncommand` writes `Enabled` to on, `nodetool disablebuildversioncommand` writes it to off. The gate refusal is the only refusal the feature's own code makes of a write, apart from what stock JMX authorisation refuses before the write reaches the MBean: every other write of `Enabled` is an accepted write. On an accepted write the node changes the `Config` field in memory, logs the old and the new value of the switch at INFO, also when they are equal, and the command prints nothing and exits with status 0, like stock `nodetool enablehandoff` (`src/java/org/apache/cassandra/tools/nodetool/EnableHandoff.java:28` to `32`). While the gate field is false a write to on gets the gate refusal: the switch stays as it is, nothing is logged, and the toggle reports the refusal through the stock error path. A write to off is accepted in every state.
5. No coordinator, replica, memtable, flush, compaction, streaming or repair path is touched.

### 2.4 Data and formats

The one new entry in `version.properties`, a file on the class path. No data file on disk, no wire form, no schema and no cluster metadata is added or changed. Stock code reads `version.properties` by key (`FBUtilities.java:465` and `:473`), so the new entry changes nothing for it.

### 2.5 Cross cutting concepts

1. Settings: one yaml setting, `build_version_command_enabled`, a `volatile` primitive `boolean`. Stock refuses a yaml key it does not know (`src/java/org/apache/cassandra/config/YamlConfigurationLoader.java:422` to `423`), so the setting is a `Config` field. The stock loader leaves a field whose key is absent at its initial value, `true` here, the default, and refuses a key given no value (`YamlConfigurationLoader.java:370` to `376` and `:419` to `420`).
2. Limits: none. A read returns one string held in memory.
3. Observability: the counters `ReadsServed` and `ReadsRefused` of the metric type `BuildVersion`, and one INFO line with the old and the new value of the switch for every accepted write of `Enabled` and for the startup step of section 2.3 item 2 while the gate field is false, also when the two values are equal. The line names the setting, and its exact text is settled in the design record of the item that builds `BuildVersion`. No trace line, since the feature makes no query plan decision and has no fallback. The MBean and the counters live for the life of the node, so there is nothing to release.
4. Error handling: the read refusal names the setting `build_version_command_enabled` and no toggle or other command, so that it never sends an operator to a toggle the gate refuses. The gate refusal says that the feature has not passed its final gate, and names no setting or toggle, since none controls the gate. The exact text of each is settled in the design record of the item that builds `BuildVersion`, within these bounds: each is a nested class of `BuildVersion` that extends `RuntimeException` and is neither `IllegalArgumentException` nor `IllegalStateException` nor a subclass of either, which nodetool treats as usage errors (`NodeTool.java:277` to `288`), so that it reaches the stock error path, and each carries the node's text as its own message with no cause, since the stock error path prints the message of the root cause (`NodeTool.java:291` and `:330`). A version the node cannot read is `Unknown`, the stock idiom for a missing `GitSHA` (`FBUtilities.java:117` and `:473`). There is no system property override of the ChronitonDB version, unlike stock's own two keys (`FBUtilities.java:464` and `:472`).
5. Security: the MBean sits behind the node's JMX authentication and authorisation like every stock MBean (`conf/cassandra-env.sh:237` to `247`, `src/java/org/apache/cassandra/auth/jmx/AuthorizationProxy.java:79`). Stock authorises JMX access per MBean, a read of an attribute with `SELECT` and a write with `MODIFY` (`AuthorizationProxy.java:422` to `427`), so on a cluster with JMX authorisation on a role needs `SELECT` on the version MBean for `nodetool chronitondbversion` and for a read of `Enabled`, and `MODIFY` on it for the toggles. The counter MBeans need no permission for the commands to work. Section 6.3 and the reference page state it.
6. Gate: before the feature's final gate the switch refuses to turn on ([branching-and-review.md](../../process/branching-and-review.md#feature-switches-and-defaults), rule 2). The final gate is the merge of the milestone report of milestone 1, this feature's only milestone ([additive.md](../../process/additive.md#milestone-gates)). The code knows nothing of that merge. It reads the gate field, the static boolean `finalGatePassed` of `BuildVersion`, read at run time and never a compile time constant, and the requirements of section 3 are written against that field. Every build on this line carries false in it until a one line code change, in a pull request a maintainer merges after the report, sets it to true. The process pages on this line define no step that makes that change. Which step makes it, and whether it is an item of this feature's plan, is for the maintainers to decide before the plan is written, and their answer becomes a decision record. Until that change exists the switch stays off for users on this line. Tests get past the gate only through the lift, which sets the field to true by reflection inside each instance's class loader before the instances of a cluster start, so a lifted cluster starts with the field true on every instance. The in-JVM framework loads a class per instance unless the class carries the framework's `Shared` annotation or the framework's default filter names it (`test/distributed/org/apache/cassandra/distributed/impl/AbstractCluster.java:1161` to `1166` and `:1186` to `1197`), so `org.chronitondb` classes, their static fields included, are per instance like `org.apache.cassandra` ones, see risk R7. The lift is the only test code that touches the field: no unit test sets it, so tests of the switch on state exist only as in-JVM distributed tests. Shipped code has no setter and no other path to the field but the one line change ([testing.md](../../process/testing.md#scenarios), rule 9).

### 2.6 Deployment

1. New yaml key `build_version_command_enabled` for an operator's `cassandra.yaml`. Its yaml value is `true` when the key is absent, the default. The sandbox line ships no `conf/cassandra_chronitondb.yaml`, the fork's own configuration file of [release.md](../../process/release.md#the-configuration-file), that file is not in the scope of section 1, and Apache's two yaml files stay untouched, so no configuration file in the tree carries the key. An operator who wants the feature off adds `build_version_command_enabled: false` to the node's `cassandra.yaml`.
2. New nodetool commands `chronitondbversion`, `enablebuildversioncommand` and `disablebuildversioncommand`.
3. New MBean `org.chronitondb:type=BuildVersion` and the two counter MBeans `org.chronitondb:type=BuildVersion,name=ReadsServed` and `org.chronitondb:type=BuildVersion,name=ReadsRefused`, all three in the fork's JMX domain and none in Apache's.
4. A new row `build_version_command_enabled` in `system_views.settings`, which lists every `Config` field (`src/java/org/apache/cassandra/db/virtual/SettingsTable.java:59` and `:153` to `154`), showing the switch's value, `false` while the gate field is false.
5. No new file on disk.

### 2.7 Package dependencies and hook points

The rule is by whole package and covers the packages under `src/java`: a ChronitonDB package MAY use any class of a package listed in its row, by an import statement or by its qualified name, and no class of any other package. A name without a star covers that one package, and a name ending in `.*` covers the package and its subpackages. Test code under `test/` is not bound by it. The names in brackets are notes on what the feature uses from each package and bind nothing.

| ChronitonDB package | MAY import |
|---|---|
| `org.chronitondb.version` | `java.*`, `javax.management.*`, `org.slf4j`, `com.codahale.metrics`, `org.apache.cassandra.config` (`Config`, `DatabaseDescriptor`), `org.apache.cassandra.metrics` (the registry and its `MetricName`), `org.apache.cassandra.utils` (`MBeanWrapper`) |
| `org.chronitondb.tools.nodetool` | `java.*`, `javax.management.*`, `io.airlift.airline`, `org.apache.cassandra.tools` (`NodeProbe`, `NodeTool.NodeToolCmd`), `org.chronitondb.version` (`BuildVersionMBean`) |

Hook points, the stock files that import ChronitonDB code:

| Stock file | Why | Delta entry |
|---|---|---|
| `src/java/org/apache/cassandra/tools/NodeTool.java` | The command list (`NodeTool.java:243` to `252`) is the only way a command joins nodetool. Three list entries and the imports they need | `nodetool-build-version-commands`, written by the items the plan gives the commands |
| `src/java/org/apache/cassandra/service/StorageService.java` | `initServer` (`StorageService.java:967` to `971`) is the one startup step a real node, an in-JVM test instance started with the GOSSIP feature (`Instance.java:704` and `:709`) and the unit test JVM share, so the MBean exists in all three. One call and the import it needs, after the three version log lines at `:969` to `:971` | `startup-build-version-mbean`, written by the item the plan gives `BuildVersion` |

Stock files edited without importing ChronitonDB code, each with its own delta entry written by the item the plan gives the edit: `build.xml` (the entry, `build-version-entry`) and `src/java/org/apache/cassandra/config/Config.java` (the field, `config-build-version-command-enabled`). Apache's own fields and their defaults in `Config.java` stay as they are. The new field, with its initial value `true`, is the only addition. `DatabaseDescriptor.java` is not edited. The register is [docs/delta](../../delta/README.md). How the commands and the edits are split across items is the plan's.

### 2.8 Feature class and switches

Feature class: purely additive, because the feature is reachable only by asking for things stock Apache Cassandra does not have, a nodetool command that stock nodetool refuses as unrecognised, a yaml setting that stock refuses at startup, and an MBean that stock does not register, and because it changes no stock operation. The feature class rule of [branching-and-review.md](../../process/branching-and-review.md#feature-switches-and-defaults) names new syntax, new index types and new settings as the ways a purely additive feature is reached. This spec reads that list as examples of things stock does not have, which a new command and a new MBean are too. A maintainer approves the class with the spec ([branching-and-review.md](../../process/branching-and-review.md#feature-switches-and-defaults), rule 6), so the merge of this spec approves that reading and the class.

| Switch | Class | Reason | Default per line | Stock operations it changes |
|---|---|---|---|---|
| `build_version_command_enabled`, toggled by `nodetool enablebuildversioncommand` and `nodetool disablebuildversioncommand` | purely additive | It gates only the `Version` read and `nodetool chronitondbversion` | `chronitondb-sandbox`: on | none |

The default is the yaml value the switch takes when the yaml key is absent, in every state. The switch takes the yaml value as its startup value once the gate field is true. While the gate field is false the switch is off on every node, whatever the yaml value: FREQ-BVER-015 and FREQ-BVER-016 govern the startup value and the writes then, and FREQ-BVER-009 governs the startup value once the field is true. FREQ-BVER-010, the yaml value when the key is absent, holds in every state.

What a user who sets no ChronitonDB key and runs no ChronitonDB command sees with the feature present and the switch off, which is every node of this line while the gate field is false:

1. `nodetool help` lists three more commands, `chronitondbversion`, `enablebuildversioncommand` and `disablebuildversioncommand`, because one command list feeds both the parser and the help command (`NodeTool.java:243` to `252`, `withDefaultCommand(CassHelp.class)` at `:251` and `withCommands(commands)` at `:252`).
2. `SELECT * FROM system_views.settings` returns one more row, `build_version_command_enabled`, with the value `false` (`SettingsTable.java:59` and `:153` to `154`).
3. The JMX tree has the domain `org.chronitondb` with the version MBean and the two counter MBeans of the metric type `BuildVersion`, and no new name in any stock domain.
4. The node holds in memory the `BuildVersion` object, its MBean registration and the two counters, and after the first served read the version string: a fixed set of objects that grows with no request and no data.

Nothing else: no thread, no file, no log line but the one startup line of section 2.3 item 2 while the gate field is false, no change to the output of any stock command for the commands and settings stock has, and no change to any stock MBean, metric or virtual table row. The three help entries and the settings row are additions inside a stock output, and this spec lists them as such.

How this spec reads rule 7 against rule 1 of the feature switch rules of [branching-and-review.md](../../process/branching-and-review.md#feature-switches-and-defaults). Rule 1 gives every feature a nodetool toggle, and a toggle that works with the feature off needs an MBean registered with the feature off, so some memory of every feature exists in every state. This spec reads the words "no new memory is used" of rule 7, and of the stock behaviour rule of [quality-requirements.md](../../process/quality-requirements.md#stock-behaviour-unchanged), as no memory that grows with requests or data: with the switch off this feature holds only the fixed objects its switch, its counters and its version need, listed above, and allocates nothing per request beyond the JMX reply of a refused read. The merge of this spec approves that reading with the class, or a maintainer asks for a decision record.

## 3. Feature requirements

FREQ-BVER-001 (event-driven): When the build runs the target `_createVersionPropFile`, the build SHALL write the entry `ChronitonDBVersion` into `version.properties` with the value `<Apache version>-chronitondb<n>`, with `<Apache version>` the build's `base.version` property and `<n>` the release number given as the trimmed value of the build property `chronitondb.release`. Source: decision record 0002 and the version numbers of release.md.

FREQ-BVER-002 (unwanted behaviour): If the build property `chronitondb.release` is not set, is empty or is made of white space only, then the build SHALL use `0` as `<n>`. Source: decision record 0002.

FREQ-BVER-003 (unwanted behaviour): If the build property `chronitondb.release` is set to a value that is not a release number, then the target `_createVersionPropFile` SHALL fail the build with an error that names the property. Source: risk R2.

FREQ-BVER-004 (event-driven): When a JMX client reads the `Version` attribute of the `BuildVersion` MBean on a node whose switch is on, the node SHALL return the node's version. Source: decision record 0002.

FREQ-BVER-005 (event-driven): When a JMX client reads the `Version` attribute of the `BuildVersion` MBean on a node whose switch is off, the node SHALL refuse the read with an error that names the setting `build_version_command_enabled`. Source: the feature switch rules of branching-and-review.md, rule 7.

FREQ-BVER-006 (unwanted behaviour): If the node cannot read a `ChronitonDBVersion` entry, because `version.properties` is absent from the class path, fails to load, has no such key or has an empty or white space only value for it, then the node SHALL take `Unknown` as the node's version. Source: the stock idiom of `FBUtilities.java:117` and `:473`, and risk R1.

FREQ-BVER-007 (event-driven): When an operator runs `nodetool chronitondbversion` against a node whose switch is on, the command SHALL print on stdout the one line `ChronitonDBVersion: ` followed by the node's version. Source: decision record 0002.

FREQ-BVER-008 (event-driven): When an operator runs `nodetool chronitondbversion` against a node whose switch is off, the command SHALL print nothing on stdout and report the node's read refusal through the stock error path, with the setting `build_version_command_enabled` in the text on stderr. Source: the feature switch rules of branching-and-review.md, rule 7.

FREQ-BVER-009 (state-driven): While the gate field is true, the node SHALL take the startup value of the switch from the yaml value of `build_version_command_enabled`. Source: the feature switch rules of branching-and-review.md, rule 1.

FREQ-BVER-010 (optional feature): Where the yaml configuration of a node does not name `build_version_command_enabled`, the node SHALL take `true` as its yaml value, the default. Source: section 2.8 and the feature switch rules of branching-and-review.md, rule 3.

FREQ-BVER-011 (event-driven): When an operator runs `nodetool enablebuildversioncommand` or `nodetool disablebuildversioncommand`, the command SHALL write the `Enabled` attribute of the node's `BuildVersion` MBean to on or to off as the command's name says. Source: the feature switch rules of branching-and-review.md, rule 1.

FREQ-BVER-012 (event-driven): When the node accepts a write of `Enabled`, the node SHALL change the `Config` field `build_version_command_enabled` in memory and nothing on disk. Source: the nodetool rule of quality-requirements.md.

FREQ-BVER-013 (event-driven): When a JMX client reads the `Enabled` attribute of the `BuildVersion` MBean, the node SHALL return the value of the switch. Source: the nodetool rule of quality-requirements.md, so that an operator and a test can read what the toggles change.

FREQ-BVER-014 (event-driven): When the node accepts a write of `Enabled` or sets the switch off at startup while the gate field is false, the node SHALL log the old and the new value of the switch at INFO, also when the two values are equal. Source: observability rule 3 of quality-requirements.md.

FREQ-BVER-015 (state-driven): While the gate field is false, the node SHALL start with the switch off, whatever the yaml value, from the startup step of `initServer` on. Source: the feature switch rules of branching-and-review.md, rule 2.

FREQ-BVER-016 (state-driven): While the gate field is false, the node SHALL refuse a write of `Enabled` to on with an error that says the feature has not passed its final gate. Source: the feature switch rules of branching-and-review.md, rule 2.

FREQ-BVER-017 (ubiquitous): The node SHALL accept a write of `Enabled` to off in every state. Source: the feature switch rules of branching-and-review.md, rule 7, so that an operator can turn the feature off at any time.

FREQ-BVER-018 (event-driven): When the node refuses a write of `Enabled`, the toggle SHALL report the refusal through the stock error path. Source: the stock idiom of `NodeTool.java:289` to `292`.

FREQ-BVER-019 (event-driven): When the lift is registered on the builder of an in-JVM test cluster before the cluster starts, every instance of the cluster SHALL start with the gate field true. Source: the scenario rules of testing.md, rule 9.

FREQ-BVER-020 (ubiquitous): The node SHALL register the `BuildVersion` MBean and the counters `ReadsServed` and `ReadsRefused` at its node start, whatever the switch's value. Source: the feature switch rules of branching-and-review.md, rule 1, so that the toggles and the counters exist with the switch off.

FREQ-BVER-021 (ubiquitous): The node SHALL count the version reads it serves in the counter `ReadsServed` and the version reads it refuses in the counter `ReadsRefused`, both of the metric type `BuildVersion`. Source: observability rule 1 of quality-requirements.md.

FREQ-BVER-022 (ubiquitous): The command `nodetool version` SHALL print, with this feature present and whatever the switch's value, exactly the output stock Apache Cassandra 5.0 prints on `chronitondb-sandbox` and nothing else, the line `ReleaseVersion: ` with the release version, and with `-v` also the line `GitSHA: ` with the git SHA. Source: the stock behaviour rule of quality-requirements.md.

FREQ-BVER-023 (ubiquitous): The in-JVM distributed tests of this feature SHALL start each instance of their clusters with the GOSSIP and JMX features of the in-JVM framework. Source: the in-JVM framework, which runs the node start only with GOSSIP (`Instance.java:704` and `:709`) and starts the JMX connector only with JMX (`IsolatedJmx.java:127` to `128`).

## 4. Quality requirements

In this table the words gates and gate item are the checks of quality-requirements.md a change passes, not the final gate of section 2.5.

| ISO/IEC 25010 characteristic | Line | Requirements, or the reason it does not apply |
|---|---|---|
| Performance efficiency | Fastest correct design, with benchmarks in the design and in the gates | Does not apply: the feature touches no request path. A read returns one string loaded once from the class path, the stock mechanism of `FBUtilities.getReleaseVersionString` (`FBUtilities.java:443` to `466`). No benchmark |
| Performance efficiency | Memory budgets on coordinator and replica | Does not apply: the node holds one string, one MBean and two counters, and no per request state |
| Reliability | Isolation levers on coordinator and replica: thread pools, limits, load shedding, timeouts, kill switch | The kill switch is the feature switch, FREQ-BVER-009 to FREQ-BVER-013 and FREQ-BVER-017. No thread pool, limit, shedding or timeout: a read does no work beyond returning a string held in memory |
| Reliability | Automatic fallbacks opt-in, with yaml setting, nodetool toggle, metric and rate-limited log line | Does not apply: the feature has no fallback. A version the node cannot read is `Unknown` (FREQ-BVER-006), the stock idiom, and takes no other path |
| Reliability | Coordination between nodes model checked, when the design changes it | Does not apply: nodes never exchange the version |
| Compatibility | Stock Apache Cassandra behaviour unchanged | FREQ-BVER-022. The feature adds a command, an MBean, a setting and a properties entry that stock refuses or ignores, and changes no stock operation |
| Compatibility | Stock behaviour unchanged with the feature off | FREQ-BVER-005, FREQ-BVER-008, FREQ-BVER-015 and FREQ-BVER-022. With the switch off a user sees the additions section 2.8 lists, the three `nodetool help` entries, the settings row, the version MBean and the two counter MBeans, and the node holds the fixed objects listed there: no thread, no file, no memory that grows with requests or data, and no change to any stock output |
| Compatibility | Mixed-version cluster, upgrade and rollback (see the Compatibility section) | Section 6: no format, schema or protocol change. A nodetool and a node of different builds fail the way stock nodetool fails on a missing MBean or an unrecognised command |
| Functional suitability | CQL validity and results independent of replication factor, data centres and replica count | Does not apply: the feature has no CQL |
| Flexibility | Settings per index or per table over global ones, with global, include and exclude modes | Does not apply: the setting gates one command on one node and depends on no data |
| Interaction capability | nodetool toggles change the in-memory value only, yaml holds the startup value | FREQ-BVER-009, FREQ-BVER-011, FREQ-BVER-012 and FREQ-BVER-013 |
| Interaction capability | Error messages name the setting or toggle that controls the behaviour | FREQ-BVER-005 and FREQ-BVER-008. The gate refusal of FREQ-BVER-016 names the gate, which no setting or toggle controls |
| Maintainability | Observability: metrics, traces and diagnostics as a gate item | FREQ-BVER-014, FREQ-BVER-020 and FREQ-BVER-021. No trace line, since there is no query plan decision and no fallback. The MBean and the counters live for the life of the node, so nothing is released |
| Security | Threat model answered (see the Threat model section) | Section 5, FREQ-BVER-002, FREQ-BVER-003, FREQ-BVER-005, FREQ-BVER-009, FREQ-BVER-013, FREQ-BVER-014 and FREQ-BVER-021 |
| Safety | Any risk of data loss or corruption named, with its mitigation | Does not apply: the feature reads one string and writes nothing on disk |

## 5. Threat model

| Entry point | Threat (STRIDE) | Mitigation | FREQ |
|---|---|---|---|
| `BuildVersion` MBean, read of `Version` over JMX | Information disclosure: which ChronitonDB build a node runs | Stock JMX authentication and authorisation cover the new MBean as every other (`conf/cassandra-env.sh:237` to `247`, `AuthorizationProxy.java:79`). The switch refuses the read when off. The same class of fact is already readable from `StorageServiceMBean.getReleaseVersion` (`src/java/org/apache/cassandra/service/StorageServiceMBean.java:108`) | FREQ-BVER-005 |
| `BuildVersion` MBean, read of `Version` over JMX | Denial of service: repeated reads | A read returns one string held in memory and allocates only the JMX reply. Each read that reaches the MBean is counted, so a flood is visible | FREQ-BVER-021 |
| `BuildVersion` MBean, read of `Enabled` over JMX | Information disclosure: whether the feature is on | Stock JMX authentication and authorisation, as above. The value says nothing beyond the switch | FREQ-BVER-013 |
| `BuildVersion` MBean, write of `Enabled` over JMX | Tampering: a client turns the feature on or off | Stock JMX authorisation. The change is in memory only and logged with the old and the new value, and a restart returns to the startup value | FREQ-BVER-009, FREQ-BVER-014 |
| `BuildVersion` MBean, write of `Enabled` over JMX | Repudiation: nobody can tell that the switch was changed | The INFO line records each accepted write. The identity of a JMX client is stock's concern | FREQ-BVER-014 |
| `BuildVersion` MBean | Spoofing and elevation of privilege | Not reachable: the MBean reads one string and flips one boolean, and runs nothing else | none |
| yaml setting `build_version_command_enabled` | Tampering: an edit of `cassandra.yaml` | The file's permissions, as for every stock setting. The setting only turns the feature on or off | FREQ-BVER-009 |
| Build property `chronitondb.release` | Tampering: a wrong release number baked into a build | A build given none writes `0`, a build given a value that is not a release number fails, and the release process verifies a candidate before it is promoted ([release.md](../../process/release.md#how-a-release-is-made)) | FREQ-BVER-002, FREQ-BVER-003 |

## 6. Compatibility

This feature changes no format, schema or protocol: the only new data is one entry inside `version.properties` on the class path, which stock code reads by key (`FBUtilities.java:465`) and never writes to disk or sends on the wire.

### 6.1 On-disk format changes

None.

### 6.2 Mixed-version cluster

Nodes never exchange the version, so a mixed cluster is a mix of nodetool and node builds only. A nodetool with this feature against a node without the MBean fails as nodetool fails on any missing MBean: nodetool turns the missing MBean into an `IllegalArgumentException` with the text `Server is not initialized yet, cannot run nodetool.` (`NodeTool.java:326` to `328`), thrown inside the catch block of `execute` and so left uncaught by it (`NodeTool.java:289` to `292`), which is why this one exception does not take the usage error path, and ends `main` (`NodeTool.java:85` to `87`) with the exception's stack trace on stderr and exit status 1. This feature leaves that as it is. A nodetool without this feature against a node with it refuses `chronitondbversion` through the stock usage error.

### 6.3 Upgrade path and prerequisites

No prerequisite for a node: it starts from any supported setup with the yaml key absent. On a cluster with JMX authorisation on, a role needs `SELECT` on the version MBean for `nodetool chronitondbversion` and `MODIFY` on it for the toggles, as for any MBean a role has no permission on (`AuthorizationProxy.java:422` to `427`).

### 6.4 Rollback path

Nothing to drop or rebuild. A rollback to a build without the feature removes the command and the MBean. An operator whose `cassandra.yaml` names `build_version_command_enabled` removes that key before the rollback, since a build without the feature refuses a yaml key it does not know (`YamlConfigurationLoader.java:422` to `423`). The reference page states this as a rollback prerequisite.

### 6.5 Runbook entries

One reference page for the feature, covering the command, the toggles, the setting, the MBean and the permissions it needs, the counters and the log line, under `docs/` at the path that the design record of the item the plan gives `nodetool chronitondbversion` names, since the line has no documentation layout yet ([conventions.md](../../process/conventions.md#where-things-live), rule 3). The page carries the rollback prerequisite above. The same item creates `NEWS-chronitondb.txt`, which the sandbox line does not have, with the feature's entry.

## 7. Dependencies

No new dependency. The commands use airline, which nodetool already ships (`NodeTool.java:61`), and the counters use the stock metrics registry (`CassandraMetricsRegistry.java:55` to `58`).

## 8. Risks

| Id | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| R1 | A build run by a target that skips `_createVersionPropFile` puts no `version.properties` on the class path, and the command prints `Unknown` | Medium | Low | FREQ-BVER-006 makes the case visible, and an in-JVM distributed test of a validation item reads `version.properties` from the class path of the build, where `_createVersionPropFile` writes it (`build.xml:108` to `109` and `:494` to `495`) |
| R2 | A wrong release number given to the build prints a wrong version on every node of that build | Low | Medium | FREQ-BVER-002 defaults to `0`, FREQ-BVER-003 fails the build on a value that is not a release number, and the release process verifies a candidate before it is promoted ([release.md](../../process/release.md#how-a-release-is-made)) |
| R3 | This line has no shared feature switch code yet, so `BuildVersion` carries the first one, which later features may replace | High | Low | `BuildVersion` is one class under `org.chronitondb.version` with no stock dependency beyond its `Config` field |
| R4 | The in-JVM distributed test framework runs nodetool through `InternalNodeProbe`, which opens no JMX connection (`test/distributed/org/apache/cassandra/distributed/mock/nodetool/InternalNodeProbe.java:63` to `64`), so the command cannot reach the MBean on that path | High | Medium | The in-JVM distributed tests of the validation items, one or several as the plan says, run the command against an instance through the connector its JMX feature starts (`test/distributed/org/apache/cassandra/distributed/impl/IsolatedJmx.java:127` to `128`), on instances started with the GOSSIP and JMX features (FREQ-BVER-023), the only place the lift exists, with `NodeTool` run in the test JVM against the instance's JMX host and port or `bin/nodetool` run as a process, as each validation item's design record decides. The unit tests of the items that build the code run only the tests of the switch off state and the switch off half of FREQ-BVER-022, against the unit test JVM through `ToolRunner.invokeNodetool`, which points `bin/nodetool` at the test JVM's JMX server (`test/unit/org/apache/cassandra/tools/ToolRunner.java:184` to `191`, `CQLTester.java:373` to `381` and `:541` to `551`). The switch on half of FREQ-BVER-022 runs as an in-JVM distributed test under the lift |
| R5 | An Apache import edits the same lines of nodetool's command list or of `initServer` as the hooks | Low | Low | The list entries, the one call and their imports, in two files with their delta entries, resolved at the import |
| R6 | While the gate field is false the switch refuses to turn on, so the tests of the switch on state depend on the lift | High | Medium | FREQ-BVER-015, FREQ-BVER-016 and FREQ-BVER-019 are designed together in the item the plan gives `BuildVersion` |
| R7 | The in-JVM framework shares a class between its instances when the class carries its `Shared` annotation or its default filter names it (`AbstractCluster.java:1161` to `1166` and `:1186` to `1197`). A shared `BuildVersion` would hold one gate field and one switch for every instance and the test JVM. The framework's default filter lives in the dtest api jar, which this workspace does not hold, so its list was not read | Low | Medium | `BuildVersion` carries no `Shared` annotation, and the design record of the item that builds it confirms, with the filter read from the jar, that `org.chronitondb` classes load per instance |

## 9. Decisions

1. [0002. The shape of the build version command](../../decisions/0002-build-version-command-shape.md): one line from the node over JMX, `ChronitonDBVersion: ` followed by the version in the form `<Apache version>-chronitondb<n>` of release.md, with `0` as the release number of a build given none. This spec adds what the record leaves implicit: a release candidate carries the version of the release it becomes, since a candidate is promoted unchanged ([release.md](../../process/release.md#how-a-release-is-made)), and the `~rc<k>` suffix of release.md is a package version and never part of the entry. The release process of release.md names no build property today, so giving a candidate build its release number through `chronitondb.release` is a change to that process, which is not in the scope of section 1 and is for the maintainers. The feature is complete without it: until the process passes the property, every build prints `0`.

## 10. Milestones outline

1. Milestone 1, the whole feature as section 1 scopes it: the version entry, `BuildVersion` with its switch, gate field and lift, the three commands, the counters and the log line. Its tests are JUnit tests and in-JVM distributed tests, since the line has no Cucumber runner for the scenarios of testing.md: in-JVM distributed tests over JMX against instances started with the GOSSIP and JMX features, with the switch on and with it off, and a JUnit test of the switch off half of FREQ-BVER-022, carried by the item that edits `NodeTool.java` and run first at that item's base commit, the line commit its branch starts from, where it passes too. Whether the one line change that sets the gate field is an item of this plan is the maintainers' open point of section 2.5. The milestone makes the command testable end to end. The delivery plan gives the items.

## 11. Prior art

1. Stock Apache Cassandra 5.0 on this line. `nodetool version` asks the node over JMX and prints `ReleaseVersion: ` plus the node's release version, with `-v` adding `GitSHA: ` (`Version.java:36` to `38`, `NodeProbe.java:859` to `862`, `StorageServiceMBean.java:108`, `StorageService.java:3985` to `3988`). The node reads both values from `version.properties`, with `Unknown` when the file is missing (`FBUtilities.java:117` and `:460` to `474`), and the build writes that file (`build.xml:492` to `499`). `bin/cassandra -v` prints the local installation's version instead (`bin/cassandra:237`, `src/java/org/apache/cassandra/tools/GetVersion.java:24`). Right: the node's own version, one line, one source for the build and the node. Missing: no ChronitonDB version anywhere. This feature follows the same shape with the same properties file.
2. Apache Cassandra `cassandra-6.0` and `trunk`, `src/java/org/apache/cassandra/tools/nodetool/Version.java` at blob `9b39e19b3a`, read through the GitHub API, lines 39 to 44: nodetool moved to picocli, and `nodetool version -v` grew `BuildDate` and JVM lines. Apache keeps one line by default and puts more behind `-v`. This feature keeps the one line and adds no `-v`.
3. The ChronitonDB version numbers ([release.md](../../process/release.md#version-numbers)) follow Ubuntu's pattern for packages taken from Debian. The command prints that package form, which says which build is installed. The string a node reports in `nodetool version`, `system.local` and gossip is a separate form for a separate purpose ([release.md](../../process/release.md#the-version-a-running-node-reports)), and this feature leaves it alone.
4. Elasticsearch and OpenSearch. Their root endpoint `GET /` returns the version number and build hash of the node asked, and their command line tools print their own version with `--version`. Taken from their public documentation, read before this run and not verified in it. Right: a client asks the node, as here. Different: they bundle the build hash with the version, which stock `nodetool version -v` already prints here.

These rules apply to every source:

1. Describe and cite behaviour, published designs, papers, public documentation and code under licences compatible with the Apache License 2.0.
2. Code or text under an incompatible licence, for example the Elastic License, SSPL, BUSL or a proprietary licence, MUST NOT be copied. The behaviour of such a system is taken only from its public documentation. Code under a compatible licence MAY be used only with credit. See [conventions.md](../../process/conventions.md#code-from-elsewhere).
3. Contributors working on the project's behalf MUST NOT search for or read patents for design work. Any patent concern goes to the maintainers.

## Glossary

| Term | Definition | Name in code, CQL and docs |
|---|---|---|
| Stock | Apache Cassandra as the line carries it, unchanged by ChronitonDB | none |
| Stock operation | Anything stock does for a user who runs no ChronitonDB command and sets no ChronitonDB key: every request path, the output of every stock command, every stock MBean, metric and virtual table row | none |
| Feature class | Purely additive or behaviour changing, as [branching-and-review.md](../../process/branching-and-review.md#feature-switches-and-defaults) defines the two: a purely additive feature is reached only through things stock does not have and changes no stock operation, a behaviour changing one changes something stock already does | none |
| Plan, delivery plan | The two documents of the second level of this feature, which list its items and order them in milestones ([additive.md](../../process/additive.md#level-2-the-plan-and-the-delivery-plan)) | `plan.md`, `delivery-plan.md` |
| Item | One unit of the plan, with its own design record and pull request | none |
| Milestone | An increment of the delivery plan that can be tested and shown. This feature has one | none |
| Milestone report | The architect's report on a finished milestone, whose merge by a maintainer is the milestone's gate ([additive.md](../../process/additive.md#milestone-gates)) | `milestones/milestone-1.md` |
| Delta entry | The file in the delta register that records one change ChronitonDB carries on top of stock, written by the item that makes the change ([docs/delta](../../delta/README.md)) | `docs/delta/<name>.md` |
| Base commit | The commit of the line an item's branch starts from | none |
| Unit test JVM | The JVM of a JUnit test that extends `CQLTester` and has started its services, which runs `initServer` and so holds the version MBean (`CQLTester.java:633` to `638`) | none |
| Node start | The call of `StorageService.initServer`: by `CassandraDaemon.setup` on a real node, by an in-JVM test instance started with the framework's GOSSIP feature (`Instance.java:704` and `:709`), and by the unit test JVM when a test starts its services. A requirement that says the node starts means this call | `StorageService.initServer` |
| ChronitonDB build version | The version of the ChronitonDB build a node runs, in the form `<Apache version>-chronitondb<n>` | The `ChronitonDBVersion` entry, the `BuildVersion` class, the output line `ChronitonDBVersion: ` |
| The node's version | What a node returns for its ChronitonDB build version: the trimmed value of the version entry when the node could read one, otherwise `Unknown` | The `Version` attribute |
| Apache version | The Apache Cassandra version a build contains, the `base.version` property of `build.xml`, `5.0.10` on this line | `base.version` |
| Release version | The string stock writes into `CassandraVersion` and a node reports in `nodetool version`: the `version` property, `5.0.10-SNAPSHOT` in a build without the `release` property and `5.0.10` with it | `CassandraVersion`, `ReleaseVersion: ` |
| Release number | The `n` of the version form, the count of ChronitonDB releases on the same Apache version: a string of ASCII digits, either `0` alone or a first digit from 1 to 9 followed by at most 8 more digits, after the white space around it is trimmed. The property unset, empty or made of white space only counts as `0` | The build property `chronitondb.release` |
| White space | The characters Java's `String.trim` removes, every character at or below U+0020, in the build and in the node alike | `String.trim` |
| Version entry | The `ChronitonDBVersion` key of `version.properties`, written by the build next to Apache's `CassandraVersion` | `ChronitonDBVersion` |
| Version command | The nodetool command that prints the build version of the node it connects to | `nodetool chronitondbversion` |
| Version MBean | The MBean in the `org.chronitondb` JMX domain that serves the version and carries the switch, implemented by the `BuildVersion` class | `org.chronitondb:type=BuildVersion`, attributes `Version` and `Enabled`, interface `BuildVersionMBean` |
| Switch | The one value that turns the feature on or off: the `Config` field, set to its yaml value by the yaml loader at startup, set off at startup while the gate field is false, and written by the toggles at runtime. `Enabled` reads and writes it, and `system_views.settings` shows it | `build_version_command_enabled` |
| Yaml value | What the stock yaml loader puts into the switch at startup: the value of the key in `cassandra.yaml` on a real node, the value in the instance configuration in an in-JVM test, and the default when the key is absent | none |
| Default | The yaml value the switch takes when the yaml key is absent, in every state: `true` on this line. It is the switch's startup value once the gate field is true | none |
| Startup value | The value the switch has at the end of startup, before any toggle: the yaml value while the gate field is true, off while it is false | none |
| Toggles | The two nodetool commands that write `Enabled` | `nodetool enablebuildversioncommand`, `nodetool disablebuildversioncommand` |
| Accepted write | A write of `Enabled` the node does not refuse. The gate refusal is the only refusal, so every write to off and every write to on while the gate field is true is accepted | none |
| Read refusal | The error a node returns for a version read while the switch is off. It names the setting and no toggle or other command | A nested class of `BuildVersion`, text in its design record |
| Gate refusal | The error a node returns for a write of `Enabled` to on while the gate field is false. It names no setting or toggle | A nested class of `BuildVersion`, text in its design record |
| Stock error path | How nodetool reports a throwable from a command: `error: ` and the message of the root cause, then the stack trace, on stderr, exit status 2 (`NodeTool.java:289` to `292` and `:329` to `332`) | `NodeTool.err` |
| Stock usage error | How nodetool reports an unknown command or option: `nodetool: ` and the parser's message, then a line pointing at `nodetool help`, on stdout, exit status 1 (`NodeTool.java:277` to `288` and `:318` to `321`) | `NodeTool.badUse` |
| Version counters | The counters of version reads served and refused, fields of `BuildVersion`, created through the stock metrics registry in the JMX domain `org.chronitondb` with no scope part in the name | The metric type `BuildVersion`, counters `ReadsServed` and `ReadsRefused`, MBeans `org.chronitondb:type=BuildVersion,name=ReadsServed` and `org.chronitondb:type=BuildVersion,name=ReadsRefused` |
| Final gate | The merge of the milestone report of milestone 1, a process event the code knows nothing of | none |
| Gate field | The code's record of the final gate: the non final static boolean of `BuildVersion`, read at run time, false in every build on this line until a one line code change sets it to true. The requirements of section 3 are written against it | `BuildVersion.finalGatePassed` |
| Instance initializer | The hook of the in-JVM distributed test framework, registered on a cluster's builder, that runs inside each instance's class loader before the instance starts, once per instance of the cluster (`test/distributed/org/apache/cassandra/distributed/impl/AbstractCluster.java:303` to `306`) | `IInstanceInitializer` |
| Lift | The test only path that sets the gate field to true, by reflection, before the instances of an in-JVM test cluster start: an instance initializer, the only test code that touches the field, nowhere in shipped code | The class `BuildVersionLift`, package `org.chronitondb.version` under `test/distributed/` |
| Validation item | An item of the plan that holds end to end in-JVM distributed tests of the feature ([additive.md](../../process/additive.md#validation-items)). The plan says how many there are | none |
