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

# Areas and sources

Every feature spec, design record, fix record, plan, delivery plan, milestone report, import record and decision record names the areas of ChronitonDB it is about, in the `Areas` row of its document control table. The areas group the documents in the [generated indexes](conventions.md#generated-indexes) and name the `area:<name>` labels of issues and pull requests.

The list is closed. A document names one area or more from it, joined by commas, and no other word. A new area, a renamed one or a removed one is a change to this page, which the maintainers approve by merging it.

## The areas

The list follows the top level of Apache Cassandra's own JIRA component list, read on 2026-11-17 from the CASSANDRA project, so that a change here and the Apache ticket behind it are named alike. `search` gathers Apache's index components with any index feature of ChronitonDB's own. `project` has no Apache component: it is ChronitonDB's own. `dependencies` takes Apache's Dependencies and Jamm components, a library the server ships, apart from the build that pulls them in.

| Area | What it covers | Apache Cassandra components |
|---|---|---|
| `cql` | The CQL language and the data model it gives: syntax, semantics, types, functions, prepared statements, counters, constraints and materialized views | CQL, Feature/Constraints, Feature/Counters, Feature/Materialized Views, Feature/Prepared Statements, Feature/Super Columns, Feature/UDA, Feature/UDF, Feature/UDT, Legacy/CQL |
| `client-protocol` | The native protocol, client connections and what a driver sees | Messaging/Client, Messaging/Thrift, Client |
| `cluster` | Membership, gossip, schema agreement, cluster metadata and the messages between nodes | Cluster, Transactional Cluster Metadata, Messaging/Internode, Feature/Virtual Nodes, Legacy/Distributed Metadata |
| `consistency` | Coordination of reads and writes, hints, repair, streaming, bootstrap and decommission, lightweight transactions and Accord | Consistency, Accord, Feature/Lightweight Transactions, Feature/Repair, Feature/Streaming, Feature/Transient Replication, Legacy/Coordination, Legacy/Streaming and Messaging |
| `storage` | The local write and read paths: commit log, memtables, sstables, compaction, compression, caches, snapshots and change data capture | Local/Caching, Local/Commit Log, Local/Compaction, Local/Memtable, Local/SSTable, Local/Snapshots, Local/Other, Feature/Compression, Feature/Change Data Capture, Legacy/Core, Legacy/Local Write-Read Paths |
| `search` | Secondary indexes, storage attached indexes, vector search and the index features ChronitonDB adds | Feature/2i Index, Feature/SAI, Feature/SASI, Feature/Vector Search |
| `security` | Authentication, authorisation, encryption, key management, data masking and the audit log | Feature/Authentication, Feature/Authorization, Feature/Encryption, Feature/KMS Vault, Feature/Dynamic Data Masking, Tool/auditlogging |
| `observability` | Metrics, JMX, logging, tracing and virtual tables | Observability, Virtual Tables, Feature/Virtual Tables, Legacy/Observability |
| `configuration` | Settings and their defaults, startup and shutdown, startup checks, guardrails and rate limits | Local/Config, Local/Startup and Shutdown, Local/Scripts, Feature/Startup Checks, Feature/Guardrails, Feature/Rate Limiting |
| `tools` | nodetool, cqlsh, the sstable tools, stress, bulk loading and the tools shipped beside the server | Tool, Sidecar, Analytics Library, Legacy/Tools |
| `build-and-test` | The build, continuous integration, the test suites and harnesses, and packaging | Build, CI, Test, Packaging, Legacy/Testing |
| `dependencies` | A change that adds, removes or updates a library or another third party component the build pulls in | Dependencies, Jamm |
| `documentation` | User and operator documentation, NEWS and the website | Documentation, Legacy/Documentation and Website |
| `project` | ChronitonDB's own process, governance, release management and its relation to Apache Cassandra | None |

## The sources

How a change came into a line is its source. An import record names it in its `Source` row, and the issue and the pull requests of a change carry the one label `source:<name>`. A delta entry gives the same fact in more detail in its Origin field, so it has no `Source` row.

| Source | What it means |
|---|---|
| `original` | Written for ChronitonDB, in this repository |
| `apache-cherry-pick` | One or more commits of Apache Cassandra, picked onto the line one by one |
| `apache-merge` | A release tag or a branch of Apache Cassandra, merged into the line whole |
| `third-party` | A commit from the repository of another project |

## Rules

1. A document names the areas its content is about, not every area its code happens to touch. A feature usually has one or two.
2. An import record names the areas of what the import brings. The import of a whole Apache release names the areas its assessment found changes in.
3. A document merged before its template had the `Areas` row keeps none until its next version, which adds the row. A decision record merged before the row keeps none, since a merged record is never edited.
4. The issue of a piece of work carries one label `area:<name>` for each area, and its pull requests carry the same labels.
5. The process document check refuses a document whose `Areas` row names a word that is not on the list of areas, or whose `Source` row names a word that is not on the list of sources, as the lists stand on the line.
6. Labels of different families go together: one issue carries its kind, its class, its line, its areas and its source, so that work can be filtered by any mix of them.
