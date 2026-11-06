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

# Security vulnerabilities

ChronitonDB handles vulnerabilities by ISO/IEC 30111 and discloses them by ISO/IEC 29147. This page adds the ChronitonDB rules to the [Chroniton Labs security policy](https://github.com/chronitonlabs/.github/blob/main/SECURITY.md), which applies to every Chroniton Labs project.

## Reporting

1. Report a vulnerability privately through GitHub: open the **Security** tab of the repository and choose **Report a vulnerability**.
2. Never report a vulnerability in a public issue, pull request, discussion or commit.
3. Include what you found, the line or version affected, and the steps to reproduce it.
4. If the vulnerability also affects Apache Cassandra, please also report it to the Apache Software Foundation security team, following [the Apache security process](https://www.apache.org/security/).

A report that arrives in public is handled privately. Nobody repeats its details in public.

## Private until disclosure

1. All work on a vulnerability happens in private until disclosure: in the GitHub security advisory and its temporary private fork.
2. Before disclosure, no public text names the vulnerability. Public text means issues, pull requests, review comments, commit messages, branch names, code comments, design and decision records, change logs, documentation and release notes.
3. Before disclosure, no public text carries a CVE id, an advisory id, exploit detail or the reporter's name.
4. A fix is described by its mechanics, for example "Bound the regex length before compile". A security fix uses the commit type `fix` until the advisory is public. The `security` type is used only after that.
5. The design or fix record of a vulnerability stays in the advisory until disclosure. The maintainers decide where it is published afterwards.
6. Anyone who finds a possible vulnerability during other work stops the public part of that work and tells the maintainers privately.

## The process

| Phase (ISO/IEC 30111) | What happens |
|---|---|
| Receipt | The report arrives through private vulnerability reporting. The maintainers acknowledge it. |
| Verification | The security engineer triages the report: it reproduces the fault, finds the affected lines and releases, proposes a CVSS severity and says whether stock Apache Cassandra code is affected. The maintainers decide whether it is valid and its severity. |
| Remediation | The fix follows the corrective order below, in the advisory's private fork. Apache is notified when stock code is affected. |
| Release | The release engineer prepares fixed releases on every affected supported line, in private. Each proposal names the commit in the advisory's private fork, and each release candidate is built and verified in private. The packages publish at the moment of disclosure, together with the advisory, on the date the maintainers set, as Debian and Ubuntu handle embargoed security updates. Security releases skip the release candidate soak once verified. The advisory is published. GitHub assigns the CVE as the CVE numbering authority. The security engineer updates the VEX statements. |
| Post release | The reporter is credited unless they ask not to be. The maintainers check that the fix reached every line. |

Only the maintainers decide validity, severity, the CVE, the disclosure date, the advisory text and publication. The security engineer proposes and drafts, and never decides any of these.

## The corrective order

A security fix follows the corrective path in [maintenance.md](maintenance.md), in private:

1. A fix record, with a test that reproduces the fault and fails before the fix. Its name and messages describe the mechanics, never the attack.
2. The fix, made against that test, on every affected supported line, each carrying the same test.
3. The fixed releases on all affected lines, prepared in private from the advisory's private fork and published together at disclosure. See [release.md](release.md#security-releases).

An urgent fix is an emergency and goes first in the queue. See [maintenance.md](maintenance.md#emergency-urgent-corrective-work). Only a security fix with a security advisory is private. Any other urgent fix, for example a data loss fault, takes the public corrective path.

## Response times

| Step | Target |
|---|---|
| Acknowledge the reporter | 2 business days |
| Triage with a CVSS score | 5 business days |
| Fix released, Critical | 14 days |
| Fix released, High | 30 days |
| Fix released, Medium | 90 days |
| Fix released, Low | The next regular release |
| Public disclosure | When the fix ships, at most 90 days after the report unless agreed with the reporter |

The CVSS version is not defined yet. Each line's support period is published with its first release: 5 years for a line designated long-term support, otherwise until 12 months after the next line's first release, see [release.md](release.md#support-lifetime). Supported versions are listed in the README of the repository. A line with no releases yet has no supported versions.

## When stock Apache Cassandra is affected

ChronitonDB follows the norm Linux distributions use with their upstream projects.

1. We fix the vulnerability privately at once.
2. We notify the Apache Cassandra security team at once, with the fix.
3. We release our fix at most 14 days after that notice.
4. We release sooner if the vulnerability becomes public or is exploited.
5. We release at once if it is already public.
6. If we learned of the vulnerability from Apache under their embargo, their embargo terms bind us.

Fixes that Apache publishes for its own advisories come into the lines by import. See [upstream.md](upstream.md).

## VEX statements

Every release ships an OpenVEX file for known vulnerabilities in its shipped components. Each statement has one status:

| Status | When | Required with it |
|---|---|---|
| `not_affected` | The vulnerable code is not shipped, not reachable, or needs a configuration we do not allow | An OpenVEX justification and an impact statement naming the evidence |
| `affected` | The release carries the vulnerability | An action statement: the fixed release to move to, or the workaround |
| `fixed` | The release carries the fix | The release |
| `under_investigation` | Triage is not done | Replaced within the triage time above |

Apache's own judgements on its dependencies are a starting point, never a copy. ChronitonDB ships components Apache does not, so each claim is checked against what ChronitonDB ships.

The security engineer keeps the VEX statements in the public repository [chronitonlabs/chronitondb-security-tracker](https://github.com/chronitonlabs/chronitondb-security-tracker), updated by pull request as findings change. Each release ships the OpenVEX file for its line from there. The SBOM and VEX files are public, published with each release. See [compliance.md](compliance.md) and [release.md](release.md#release-outputs).

## Watching shipped libraries and Apache

ChronitonDB inherits every Apache Cassandra vulnerability on its base and every vulnerability in the libraries it ships.

1. Every day the security engineer checks every library in the SBOM against OSV, the GitHub advisory database and NVD.
2. For each match it works out whether ChronitonDB is affected: whether the vulnerable code is shipped and reachable. It writes the VEX statement.
3. When a patch-version update of the library fixes it, the security engineer opens a corrective item, or an emergency item when the vulnerability is serious. The item goes straight to the developer with no fix record, as [maintenance.md](maintenance.md#dependency-patch-version-updates) describes. The security engineer names in the item the test classes that cover every use of the library in ChronitonDB, and those tests run before the update merges. Anything else goes to the maintainers as a decision.
4. Every library update goes through the security engineer, including one a maintainer asks for that is not a security fix. The security engineer checks the new version's licence, the new dependencies it brings in and its known vulnerabilities. It names the exact `NOTICE.txt` and `LICENSE.txt` text the update needs, which the developer writes and the reviewer checks, updates the VEX statements, and names the tests that cover every use of the library. See [maintenance.md](maintenance.md#dependency-patch-version-updates).
5. A library ChronitonDB ships but does not use at all is not updated. The security engineer opens an item to remove it.
6. The security engineer watches Apache Cassandra security announcements with the integrator. See [upstream.md](upstream.md).
