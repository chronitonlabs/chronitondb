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

# 0008. The startup checks that always run take the names of Apache Cassandra 6.0

| Field | Value |
|---|---|
| Document type | Record (ISO/IEC/IEEE 15289), MADR |
| Status | Accepted |
| Date | 2026-11-15 |
| Deciders | The maintainers |
| References | Issue #117, the design record in `docs/design/SCV-startup-checks-view/` |

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in BCP 14 (RFC 2119, RFC 8174) when, and only when, they appear in all capitals, as shown here.

## Contents

- [Context and problem statement](#context-and-problem-statement)
- [Considered options](#considered-options)
- [Decision outcome](#decision-outcome)
  - [Consequences](#consequences)
- [More information](#more-information)

## Context and problem statement

The startup checks view has one row for each startup check a node runs, keyed by the name of the check. Four checks can be switched in `cassandra.yaml` and have a name there, such as `check_dc`. The other 15 always run and have no name on a 5.0 line: each is a Java field of the class `StartupChecks`. The row names are what an operator and a tool read, so the design had to know what the 15 are called. Apache Cassandra 6.0 gives every startup check a name. It names 14 of the 15, and it replaced the fifteenth, the check of the Sigar library, with a check named `process_environment` that gives the same warning.

## Considered options

1. The names Apache Cassandra 6.0 gives these checks, such as `jemalloc` and `data_dirs`. The Sigar check takes `process_environment`.
2. The names of Apache Cassandra 6.0 with `check_` in front, such as `check_jemalloc`, in the style of the four switchable names.
3. The Java field names of the 5.0 line, such as `checkJemalloc` and `initSigarLibrary`.

## Decision outcome

Chosen option: "The names Apache Cassandra 6.0 gives these checks", because a tool that reads the view then finds the same row names on a 6.0 line, where the names come from Apache Cassandra itself.

The rows of the 15 checks that always run MUST have these names:

| Field of `StartupChecks` on the 5.0 line | Row name |
|---|---|
| `checkKernelBug1057843` | `kernel_bug_1057843` |
| `checkJemalloc` | `jemalloc` |
| `checkLz4Native` | `lz4_native` |
| `checkValidLaunchDate` | `valid_launch_date` |
| `checkJMXPorts` | `jmx_ports` |
| `checkJMXProperties` | `jmx_properties` |
| `inspectJvmOptions` | `jvm_options` |
| `checkNativeLibraryInitialization` | `native_library_initialization` |
| `initSigarLibrary` | `process_environment` |
| `checkMaxMapCount` | `max_map_count` |
| `checkReadAheadKbSetting` | `read_ahead_kb_setting` |
| `checkDataDirs` | `data_dirs` |
| `checkSSTablesFormat` | `sstables_format` |
| `checkSystemKeyspaceState` | `system_keyspace_state` |
| `checkLegacyAuthTables` | `legacy_auth_tables` |

The rows of the checks that can be switched keep their names from `cassandra.yaml`.

### Consequences

- Good: the row names of a 5.0 line and of a 6.0 line are the same for the checks both lines run.
- Bad: the 15 names have no `check_` in front, so the view holds two styles of name.
- Bad: the names are a fixed list on a 5.0 line. A check that an import adds needs a name before the tests of the feature pass.

## More information

The design record in `docs/design/SCV-startup-checks-view/` applies this decision in section 1, in REQ-SCV-018 and in New terms. The names were read from Apache Cassandra `cassandra-6.0` at commit `84bca651ef`.
