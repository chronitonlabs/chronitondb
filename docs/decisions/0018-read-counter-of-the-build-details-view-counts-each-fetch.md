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

# 0018. The read counter of the build details view counts each fetch

| Field | Value |
|---|---|
| Document type | Record (ISO/IEC/IEEE 15289), MADR |
| Status | Accepted |
| Date | 2026-11-16 |
| Deciders | The maintainers |
| References | Issue #141, the feature spec in `docs/design/BUILD-build-details-view/`, decision record 0014 |

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in BCP 14 (RFC 2119, RFC 8174) when, and only when, they appear in all capitals, as shown here.

## Contents

- [Context and problem statement](#context-and-problem-statement)
- [Considered options](#considered-options)
- [Decision outcome](#decision-outcome)
  - [Consequences](#consequences)
- [More information](#more-information)

## Context and problem statement

A node that shows the build details view counts the reads of the view (decision record 0014). That record does not say what one read is when a client fetches a statement in pages. The view holds one row. With a page size of one row, that row fills the first page, and a page is the last one only when it holds fewer rows than the page size (`DataLimits.isExhausted`, `src/java/org/apache/cassandra/db/filter/DataLimits.java:139`, ChronitonDB chronitondb-sandbox at `17e0b84a36`, whose `src/` equals its Apache base, Apache Cassandra cassandra-5.0 at `76550e9314`. Apache Cassandra now was not read for this line). So Apache Cassandra offers a second page, and the fetch of it is a new read of the same table, which asks the view for its data again (`PartitionRangeQueryPager.nextPageReadQuery`, `src/java/org/apache/cassandra/service/pager/PartitionRangeQueryPager.java:77`, the same tree). The feature had to know whether such a statement counts once or twice.

## Considered options

1. The counter rises each time Apache Cassandra asks the view for its data.
2. The counter rises once for a statement, however many pages the client fetches.

## Decision outcome

Chosen option: "The counter rises each time Apache Cassandra asks the view for its data", because it is one exact rule that needs one increment in the read method of the view and no code that tells a later page from a first read.

The view MUST raise its read counter by one each time Apache Cassandra's read path asks the view for its data. The counter counts those requests and not statements. A `SELECT` with no key filter that a client fetches to the end in pages of one row therefore counts twice. The view MUST NOT hold code that tells a later page from a first read. The reference page MUST say what the counter counts.

### Consequences

- Good: the rule is exact and a test can state the value of the counter after each statement.
- Good: the view has one increment and no paging logic.
- Bad: the counter is no count of statements. A statement fetched in pages of one row counts more than once.
- Bad: an operator who compares the counter with a count of statements made elsewhere can find a higher value.

## More information

The feature spec in `docs/design/BUILD-build-details-view/feature-spec.md` applies this decision in FREQ-BUILD-030 and FREQ-BUILD-038 and in its section 2.2, with the code fact C20 of its section 12.
