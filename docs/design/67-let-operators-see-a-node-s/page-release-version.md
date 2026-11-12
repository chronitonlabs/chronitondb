---
title: Release version
description: What nodetool version shows on a ChronitonDB node, the switch that controls it, and the MBean and metric behind it.
---
<!--
Copyright 2026 AxonOps Limited

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

SPDX-License-Identifier: Apache-2.0
-->

# Release version

Skeleton of the reference page `docs/reference/release-version.md`. The developer fills each placeholder in angle brackets and moves the file to that path in the code pull request. The page is a reference page: facts only, no steps, no background.

A ChronitonDB™ node reports its release version, `<line>-chronitondb<n>`, through `nodetool version`. Apache Cassandra® reports its own version string everywhere else.

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in BCP 14 [RFC 2119] [RFC 8174] when, and only when, they appear in all capitals, as shown here.

## nodetool version

With the switch on, the default:

```
$ nodetool version
ReleaseVersion: <release version, for example 5.0-chronitondb3>
$ nodetool version --verbose
ReleaseVersion: <release version>
GitSHA: <git SHA of the build>
```

With the switch off, or against a node that runs Apache Cassandra or an older ChronitonDB build, the output is Apache Cassandra's: `ReleaseVersion: <Apache version>` and with `--verbose` the `GitSHA:` line.

A build made without a release version shows `5.0-chronitondb-SNAPSHOT`. A build whose value is missing shows `Unknown`.

## Setting

| Key | Type | Default | Change at runtime |
|---|---|---|---|
| `nodetool_release_version_enabled` | boolean | `true` | `nodetool enablereleaseversion`, `nodetool disablereleaseversion`, in memory only, the yaml value returns at restart |

## nodetool commands

| Command | What it changes | Output |
|---|---|---|
| `nodetool enablereleaseversion` | sets `nodetool_release_version_enabled` to `true` on the node, in memory | nothing on success |
| `nodetool disablereleaseversion` | sets it to `false` on the node, in memory | nothing on success |

Against a node without the MBean below, both end with status 1 and print `nodetool: enablereleaseversion: the node has no ChronitonDB release version reporter. It runs Apache Cassandra or an older ChronitonDB build, or the reporter failed to register at start.` on standard output, or the same line with `disablereleaseversion` in its place, followed by the usual `See 'nodetool help'` line. Under the authorization proxy, `cassandra.jmx.authorizer`, a role that lacks `DESCRIBE` or `MODIFY` on the MBean gets `error: Access Denied`, as from any stock command without a grant. Under the JDK access file, a `readonly` user gets `error: Access Denied` too, and a `readwrite` user runs both. On the stock default, local JMX with authentication off, no access control applies.

## JMX

| ObjectName | Attribute | Type | Meaning |
|---|---|---|---|
| `org.chronitondb:type=ReleaseVersion` | `ReleaseVersion` | String, read only | the release version of the build, returned whatever the switch says |
| `org.chronitondb:type=ReleaseVersion` | `Enabled` | boolean, read and write | the switch |

A ChronitonDB node applies the JMX access mode Apache Cassandra configures, one of three. On the stock default, local JMX with authentication off, no access control applies to this MBean or to any other. Under the JDK access file, `com.sun.management.jmxremote.access.file`, a `readonly` user reads both attributes and a `readwrite` user also writes `Enabled`. Under the authorization proxy, `cassandra.jmx.authorizer`, a role needs `DESCRIBE` and `SELECT` on `org.chronitondb:type=ReleaseVersion` to see the release version with `nodetool version`, and `DESCRIBE` and `MODIFY` on `org.chronitondb:type=ReleaseVersion` to run the two commands. A role without them sees Apache Cassandra's output from `nodetool version`.

## Metric

| ObjectName | Type | Unit | What increments it | Alert threshold |
|---|---|---|---|---|
| `org.chronitondb.metrics:type=ReleaseVersion,name=Reported` | counter | reads | each read of the `ReleaseVersion` attribute, by nodetool or any JMX client | none |

## Build

The release pipeline passes `-Dchronitondb.version=<release version>` to the build. The build writes it as the key `ReleaseVersion` of `org/apache/cassandra/config/version.properties` inside the jar, next to Apache Cassandra's own `CassandraVersion` and `GitSHA` keys. Without the property the value is `5.0-chronitondb-SNAPSHOT`. The build writes what it is given. A unit test fails a blank or malformed value, the release pipeline passes the value, and the release verification checks it on the installed candidate. The git SHA is Apache Cassandra's own, from the same build.

## Failure behaviour

| Case | What happens |
|---|---|
| the properties file is missing, cannot be loaded, lacks the key `ReleaseVersion` or holds it blank | the node reports `Unknown` and, for a file that cannot be loaded, logs one WARN line |
| the JMX role may not read the MBean, under the authorization proxy | `nodetool version` prints Apache Cassandra's output and nothing else, the toggles fail with `error: Access Denied` as any stock command without a grant |
| the JMX user may read but not write, a `readonly` user of the JDK access file | `nodetool version` prints the release version, the toggles fail with `error: Access Denied` |
| the JMX connection fails in another way | `nodetool version` fails with `error:` and exit code 2, as it does for Apache Cassandra's own calls |
| nodetool runs with no JMX connection, as inside the in-JVM test framework | `nodetool version` prints Apache Cassandra's output, the two commands end with status 1 and `nodetool: enablereleaseversion needs a JMX connection`, or the same for `disablereleaseversion` |
| the node asked has no MBean | `nodetool version` prints Apache Cassandra's output, the toggles end with status 1 and the line above |
| the switch is off | `nodetool version` prints Apache Cassandra's output |

Timeouts, missing replicas and limits do not apply: the command reads one value from one node over JMX.

## Known limitations

These keep Apache Cassandra's version string on a ChronitonDB node: `cassandra -v`, the start log line `Cassandra version:`, the cqlsh banner, `nodetool describecluster` and `nodetool gossipinfo`, which show the versions gossip carries, and `nodetool version` run from an Apache Cassandra nodetool or a ChronitonDB nodetool older than this feature, because the choice is made in the nodetool process. Check a rolling upgrade with the new nodetool.

Every release candidate of a release prints the release version itself, for example `5.0-chronitondb3`, not the candidate's package version `5.0-chronitondb3~rc1`. `nodetool version --verbose` tells two candidates apart by their git SHA.

## Rollback to Apache Cassandra

Before a node runs an Apache Cassandra binary, or a ChronitonDB build older than this feature, `cassandra.yaml` MUST NOT contain `nodetool_release_version_enabled`. Apache Cassandra, and an older ChronitonDB build, refuse to start on a yaml with a key they do not know.
