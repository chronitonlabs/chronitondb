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

# Acceptance coverage for #{issue}

Location: next to its design or fix record, in `docs/design/<issue>-<slug>/`, or in `docs/design/<KEY>-<slug>/` for a fork feature that fits one item. Process: [testing.md](../testing.md).

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in BCP 14 (RFC 2119, RFC 8174) when, and only when, they appear in all capitals, as shown here.

{One row per requirement of the record that a scenario does not prove: a requirement proven by another test names that test, and one deliberately not tested gives the decision that excluded it. A requirement proven by a scenario carrying its tag needs no row. Each requirement has at most one row. Tooling reads this table, so keep its columns.}

| Id | Source | Requirement | Covering scenario | Test | Status |
|---|---|---|---|---|---|
| {REQ-n or REQ-<KEY>-nnn} | {issue, risk or plan criterion} | {the requirement as the record states it} | {the scenario in one line, or none} | {the fully qualified test class and method} | {Covered, or Excluded: the decision record or issue comment that excluded it, stated cleanly} |
