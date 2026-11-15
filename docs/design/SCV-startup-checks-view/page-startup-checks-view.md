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

# Startup checks view

Skeleton of the reference page `docs/reference/startup-checks-view.md`. The developer fills each placeholder in angle brackets and moves the file to that path in the code pull request. The page is a reference page: facts only, no steps, no background.

A ChronitonDB™ node can show over CQL which startup checks it runs, whether each one is on, and where that value came from. The view is off by default. Apache Cassandra® has no such view.

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in BCP 14 [RFC 2119] [RFC 8174] when, and only when, they appear in all capitals, as shown here.

## Setting

| Setting in `cassandra.yaml` | Type | Default | Change at runtime |
|---|---|---|---|
| `startup_checks_view_enabled` | boolean | `false` | `nodetool enablestartupchecksview` and `nodetool disablestartupchecksview`, in memory only. A restart returns to the yaml value |

## The view

The view is the table `system_views.startup_checks`.

<Its three columns `name`, `enabled` and `source` with their types, and the example of section 1 of the design record.>

## Where a value comes from

| `source` | Meaning |
|---|---|
| `always_on` | <the check always runs and has no switch> |
| `system_property` | <a start option set the value: `cassandra.ignore_dc`, `cassandra.ignore_rack` or `cassandra.enable_fs_ownership_check`> |
| `yaml` | <`cassandra.yaml` has an entry for the check under `startup_checks`> |
| `default` | <none of the above, so the check has its default> |

<The order in which the node decides between them.>

## Rows

<One line for each row name, with what the check does. The four checks that can be switched: `check_data_resurrection`, `check_dc`, `check_filesystem_ownership` and `check_rack`. The 15 checks that always run: `data_dirs`, `jemalloc`, `jmx_ports`, `jmx_properties`, `jvm_options`, `kernel_bug_1057843`, `legacy_auth_tables`, `lz4_native`, `max_map_count`, `native_library_initialization`, `process_environment`, `read_ahead_kb_setting`, `sstables_format`, `system_keyspace_state` and `valid_launch_date`.>

## Who may read the view

<On a node with authorisation on, a role needs `SELECT` granted on the table or on the keyspace `system_views`. What a role without it gets.>

## Errors, log lines and metrics

<The refusal text of a read while the view is off. The INFO line of a change by nodetool. The WARN line of a failed switch, and the exit status of the nodetool command then. The line a nodetool command prints against a node without the view.>

| Metric | Counts |
|---|---|
| `org.chronitondb.metrics:type=StartupChecksView,name=Reads` | <reads the view served> |
| `org.chronitondb.metrics:type=StartupChecksView,name=RefusedReads` | <reads refused because the view is off> |
| `org.chronitondb.metrics:type=StartupChecksView,name=FailedSwitches` | <switches of the view that failed> |

## Known limitations

<A row says whether a check is on, not what it found. The two checks that do nothing on a platform other than Linux. The start option `cassandra.ignore_kernel_bug_1057843_check`. A yaml entry without the key `enabled` shows `yaml`. A read of the view at the moment it is switched on can fail once. The view is local to the node that answers.>

## Rollback

Before a node runs an Apache Cassandra binary, or a ChronitonDB build older than this feature, remove startup_checks_view_enabled from its cassandra.yaml.
