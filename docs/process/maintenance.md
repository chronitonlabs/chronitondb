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

# Maintenance

This page covers corrective, emergency, preventive, adaptive and perfective changes, the categories of ISO/IEC/IEEE 14764:2022 other than additive. New features are in [additive.md](additive.md). Changes that come from Apache Cassandra are in [upstream.md](upstream.md).

Every change is one item with one public GitHub issue. A security fix has no public issue until disclosure. It is tracked in its private advisory. A maintainer approves an item's design record or fix record, and later its pull request, by merging. The reviewer reviews each of those pull requests first.

## Corrective: fixing a fault

1. **Fix record with its reproducing test.** The designer reproduces the fault and writes a test that fails on the line before the fix. With it, the designer writes a short fix record in `docs/design/<issue>-<slug>/`, like a design record, from [templates/fix-record.md](templates/fix-record.md): the symptom, the root cause with file and line, the fix, the reproducing test, the compatibility impact, and the requirements in EARS shape. A maintainer approves it by merging.
2. **Fix against the test.** The developer fixes the fault against that test. The test MUST pass after the fix. See [testing.md](testing.md).
3. **One item, one pull request per affected line.** A fault on several lines is one item that carries every affected line. Each affected line gets its own pull request. The oldest affected line goes first, and the fix is carried forward to the newer lines. The item is done only when every one of those pull requests is merged.
4. **Stock faults.** A fault that also exists in Apache Cassandra is fixed here the same way, tests first. The integrator drafts an Apache JIRA for it, and the maintainers file it. The commit message names the `CASSANDRA-<n>` ticket. The fix gets a [delta entry](../delta/README.md) with its upstream status.

## Emergency: urgent corrective work

Emergency changes follow the corrective order, ahead of the queue.

1. **Security fixes** follow [security.md](security.md). They are worked on in private until disclosure and released on every affected supported line together.
2. **Other urgent fixes,** such as a data loss fault, take the corrective path above, first in the queue. They are released once merged on every affected line.

## Preventive, adaptive and perfective

Preventive work fixes a latent fault before it causes a failure. Adaptive work keeps ChronitonDB working in a changed environment, such as a new JDK or operating system. Perfective work improves performance, maintainability, usability or documentation. All three take the one-item path.

### The one-item path

1. **One item, one design record.** The designer writes the design record in `docs/design/<issue>-<slug>/` from [templates/design-record.md](templates/design-record.md). It carries the feature spec's mandatory sections in small form: quality requirements, threat model, compatibility and dependencies. Each section is filled, or marked "does not apply, because" with the reason.
2. **Size check.** If the designer finds the change needs several items, or a design decision across components, the designer stops and asks the maintainers. The change then moves to the three levels in [additive.md](additive.md) and keeps its maintenance category.
3. **Lines.** A change that belongs on every line follows the corrective pattern: one pull request per line, oldest line first. An adaptive change specific to one line touches only that line.
4. **Approval.** A maintainer approves the design record by merging. Implementation starts after that merge. A maintainer merges the code pull request after review.

An additive feature small enough for one item takes this same path.

### Documentation only changes

A change to documentation only is perfective. It needs no design record. The reviewer checks the pull request against the documentation rules in [conventions.md](conventions.md).

## Dependency patch-version updates

A patch-version update of an approved library, under the same licence, for a bug fix or a security fix:

1. Needs no fix record and no design record.
2. MAY be made inside the item that needs it, or as an item of its own.
3. MUST give its reason in the pull request description. The SBOM and the VEX statements of the next release record the change.
4. Inside an item of a feature, it is also recorded in the feature spec's Dependencies section in the same pull request.
5. MUST keep the library's licence category and NOTICE lines correct. See [compliance.md](compliance.md).

When a vulnerability in a shipped library is fixed by a patch-version update, the security engineer opens a corrective item, or an emergency item when the vulnerability is serious. The item goes straight to the developer, with no fix record. See [security.md](security.md#watching-shipped-libraries-and-apache).

Any other dependency change, a new library or a minor or major version change, needs approval in a feature spec or a design record before use.
