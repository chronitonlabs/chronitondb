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

# Releases

This page says when ChronitonDB releases, what a release may contain, how long each line is supported, how a release is tested before it ships, and how versions are numbered. It follows the transition process of ISO/IEC/IEEE 12207 and the release model Ubuntu uses.

The release engineer proposes each release and verifies its candidate. A maintainer approves every release and starts each candidate run. See [roles.md](roles.md#release-engineer).

## Cadence

Each line releases on its own rhythm:

1. A release follows each Apache Cassandra patch release of the line's major version, once it is imported and tested. See [upstream.md](upstream.md).
2. Otherwise, a release ships monthly when our own changes are waiting.
3. Security fixes and urgent fixes are released whenever they are ready, outside both rhythms.

The release engineer's daily check finds each release that is due on a line under these rules. It then opens the release's public issue itself and writes the proposal. The maintainers still decide by merging the proposal and by starting the candidate run.

## Support lifetime

1. The maintainers designate a line as long-term support (LTS) when its first release ships, in the line's plan file (see [Freezes](#freezes)). An LTS line is supported for 5 years from its first ChronitonDB release, whatever Apache Cassandra does with its major version. This follows the default support period of the EU Cyber Resilience Act.
2. A line that is not designated LTS is supported until 12 months after the next line's first release.
3. The support period of each line, whether it is LTS, and for an LTS line its end date, are published with its first release. A line's first release also states the end date of each earlier standard line it ends.
4. After Apache's own end of life for a major version, security fixes and critical fixes are carried back to a supported line from newer Apache Cassandra versions.

Supported versions are listed in the README of the repository.

## What a release may contain

1. Any release MAY ship fixes, imports from Apache Cassandra and security fixes.
2. A release MAY ship a finished feature behind its feature switch, which the operator sets with yaml or nodetool.
3. Within a line, a feature's default MUST NOT change. Upgrading within a line never changes behaviour by itself.
4. A purely additive feature's default MAY be on from a line's first release. A behaviour-changing feature's default MUST be off on every line, with one exception the maintainers made: `nodetool version` showing the release version and the git SHA is on by default, see [What nodetool version shows](#what-nodetool-version-shows). No other behaviour-changing feature is on by default. That feature ships before each line's first release, `5.0-chronitondb1` and `6.0-chronitondb1`: it blocks a line's first release until it is in. So it is in every release of a line from the first, and no release within a line changes what `nodetool version` shows.
5. A feature finished after its line's first release ships with its default off on that line.

A feature becomes switchable at its final milestone gate. Before that, its switch refuses to turn on, whatever its default. See [additive.md](additive.md#milestone-gates) and [branching-and-review.md](branching-and-review.md#feature-switches-and-defaults).

## How a release is made

Every release takes two maintainer approvals, and each one is the merge of a pull request, like every approval in this project: the release proposal, before the candidate is built, and the promotion, after the soak and verification. The reviewer reviews both pull requests first.

1. **Proposal.** When a release is due, the release engineer opens its issue and a release proposal pull request that adds `docs/releases/<version>.md` from [the release proposal template](templates/release-proposal.md): the version, the exact commit on the line it is built from, what goes in, from the commits on the line, the milestone gates passed and the security fixes due.
2. **First approval.** A maintainer merges the proposal pull request. Nothing is built, tagged or published before that merge.
3. **Release candidate.** A maintainer starts the release workflow by hand when the candidate is wanted, giving the version. Building and testing a candidate is expensive, so a maintainer chooses the moment. The workflow refuses to run unless that version's proposal is merged. The candidate tag is signed at the commit the proposal names, so anything merged later stays out. The pipeline then builds, tests and publishes the release candidate: a GitHub pre-release, and packages in a separate proposed package repository for Debian and Red Hat.
4. **Verification.** The release engineer verifies the candidate: signatures, installs, upgrade and rollback from the previous ChronitonDB release and from Apache Cassandra, the parity suite, and that the release outputs are present and signed: the SBOM in SPDX and CycloneDX, the OpenVEX statements, the release notes and the provenance.
5. **Soak.** The candidate stays in the proposed channel for 7 days.
6. **Second approval and promotion.** If the verification passed and no problem is reported during the soak, the release engineer opens a promotion pull request that fills the verification results section of `docs/releases/<version>.md`. A maintainer merges it, and the candidate is then promoted unchanged to the official release.

### Security releases

A security release is prepared in private, after the practice Debian and Ubuntu follow for embargoed security updates:

1. Its proposal names the commit in the security advisory's private fork, not a commit on the public line. The proposal and its review stay private until disclosure.
2. Its release candidate is built and verified in private.
3. It skips the soak once it is verified.
4. Its packages publish at the moment of disclosure, together with the advisory, on the date the maintainers set. The fix reaches the public line at the same time.

Every other release names one commit on the public line. See [security.md](security.md).

## Freezes

1. There is no freeze on a line for its patch releases. The signed release candidate tag is the freeze.
2. A problem found during the soak is fixed on the line. A new candidate is then cut, and the soak starts again.
3. A feature freeze starts 4 weeks before the first release of a new line. After it, only fixes and imports go into that line until its first release.

Each line has a plan file, `docs/releases/<line>-plan.md`, from [the line plan template](templates/line-plan.md). It holds the line's planned first release date, the date its feature freeze starts and whether the maintainers designated it LTS. It changes only by a pull request a maintainer merges. The release engineer and the reviewers read it: the release engineer for the releases that are due and the freeze, the reviewers to hold a feature pull request back during the freeze.

## Version numbers

A ChronitonDB release version is the line followed by ChronitonDB's own release number on that line: `<line>-chronitondb<n>`. Here `<line>` is the line's Apache Cassandra major version, `5.0` for `chronitondb-5.0` and `6.0` for `chronitondb-6.0`. `n` starts at 1 on each line and goes up by one with each release on it.

A release version never carries an Apache patch number. A line leads Apache: it can carry Apache fixes taken early and Apache branch commits that no Apache release holds yet. A version such as `5.0.10-chronitondb1` would claim Apache Cassandra 5.0.10 where the release carries more or less than that. The form `<line>-chronitondb<n>` cannot be mistaken for an Apache version.

| Form | Example | Meaning |
|---|---|---|
| `<line>-chronitondb<n>` | `5.0-chronitondb1` | The first ChronitonDB release on the 5.0 line |
| The same, `n` raised by one | `5.0-chronitondb2` | The next release on the 5.0 line |
| Another line, `n` from 1 | `6.0-chronitondb1` | The first ChronitonDB release on the 6.0 line |
| `<version>~rc<k>` | `5.0-chronitondb3~rc1` | The package version of the first release candidate of `5.0-chronitondb3` |
| `<version>-rc<k>` | `5.0-chronitondb3-rc1` | The git tag of that release candidate |

1. `n` goes up by one for every release, whatever it carries: an Apache release import, fixes taken early, security fixes or our own changes.
2. A release candidate cut again after a problem in the soak keeps its version and raises `k`, for example `5.0-chronitondb3~rc2`.
3. A line taken from Apache's branch before Apache's first release of that major version is numbered the same way. The 6.0 line's first release is `6.0-chronitondb1`, even while Apache's own build file says a development version such as `6.0-alpha3`. Apache's development version never appears in a ChronitonDB release version.
4. The git tag of a release is the version itself, for example `5.0-chronitondb3`. It cannot clash with Apache's own tags, which start with `cassandra-`. The git tag of a release candidate uses `-rc<k>` in place of `~rc<k>`, since git does not allow `~` in a tag name.
5. Release and release candidate tags are signed with the dedicated ChronitonDB release key, not with a person's key. Its public key is published so users can verify the tags.
6. These versions are not Semantic Versioning, which needs three numbers and reads a hyphen as a pre-release. Package tools and git do not need it.

### How package tools order the versions

Debian and Red Hat package tools order every release and release candidate of a line correctly:

1. Both split the version at its hyphen. Debian reads `5.0` as the upstream version and `chronitondb3` as the Debian revision. Red Hat reads `5.0` as the Version and `chronitondb3` as the Release, since a Red Hat Version allows no hyphen.
2. Both compare runs of digits as numbers, so `5.0-chronitondb9` comes before `5.0-chronitondb10`.
3. Both sort `~` before anything, even the end of the version. So `5.0-chronitondb3~rc1` comes before `5.0-chronitondb3~rc2`, and both come before `5.0-chronitondb3`.
4. The release candidate of the next release comes after the current release: `5.0-chronitondb2` comes before `5.0-chronitondb3~rc1`.
5. A line's versions come before the next line's: `5.0-chronitondb99` comes before `6.0-chronitondb1`.

Each of these orders was checked with `dpkg --compare-versions` on Debian 13 and with rpm's version comparison in rpm 4.14 and rpm 6.1. Red Hat tools sort `~` this way from rpm 4.10.

### What a release contains

The release version does not say which Apache content a release carries, so its release notes and its release proposal state it:

1. The newest Apache Cassandra release the line fully contains, for example Apache Cassandra 5.0.9. On a line before Apache's first release of its major version, the newest Apache pre-release of that major version the line contains, for example Apache Cassandra 6.0-alpha2.
2. When the line carries Apache branch commits after that release, the last Apache commit merged, by its full hash.
3. Every change cherry-picked on top of that release: an Apache fix by its Apache JIRA and full Apache commit hash, a change from another project by its source repository and full commit hash, found by the `import(<owner>/<repo>@<12 character hash>)` subject of its import merge commit.
4. Our own changes, from the commits on the line and `NEWS-chronitondb.txt`.

The release engineer takes the first three from the line's git history: the Apache release tags it contains, Apache's branch, and its import commits. See [upstream.md](upstream.md) and [conventions.md](conventions.md#change-logs-and-release-notes).

### The version a running node reports

A running node reports a different string from its release version to other nodes and to drivers, in gossip, `system.local`, `system.peers_v2` and the drivers. This is the node version: `<Apache version>+chronitondb.<feature level>`, for example `5.0.10+chronitondb.1`.

1. Its Apache part is the version in the line's build file, the string stock Apache Cassandra reports for a release build of the same code: `5.0.10` on the 5.0 line today, `6.0-alpha3` on the 6.0 line. The version checks in Apache's code are written against that version. It can differ from the Apache release the release notes name.
2. It exists so that Apache Cassandra and its drivers compare a ChronitonDB node correctly. They read the part after `+` as build information, so `5.0.10+chronitondb.1` compares just after Apache Cassandra 5.0.10 and before 5.0.11. They read a hyphen as a pre-release, so the release version `5.0-chronitondb3` would compare as a pre-release of 5.0.0, older than every Apache Cassandra 5.0 release.
3. It is never shown as the release version. Packages, tags, release notes and our documentation name a release by its release version only.
4. The feature level is a number in the code, raised only when a release changes how nodes work together. Features that need every node to cooperate turn on once every node reports their level, so they need the ChronitonDB form on every node.
5. The ChronitonDB form is a behaviour-changing feature with its own switch, off by default. With it off, a node reports the build file's version as stock does, for example `5.0.10`, and the features that need a feature level stay off. Its feature spec sets the switch's name and the driver tests that prove each setting.
6. Apache compatibility mode, `apache_compatibility_mode`, comes first. A node in Apache compatibility mode reports the plain Apache version whatever the switch says. With compatibility mode off, the switch decides.
7. The switch never changes `nodetool version`. Until the feature of [What nodetool version shows](#what-nodetool-version-shows) ships, `nodetool version` prints Apache's own string, and the node version MUST NOT appear there.

### What nodetool version shows

`nodetool version` shows what is installed: the release version, for example `5.0-chronitondb3`, and the git SHA of the build. It shows no Apache release line.

1. It is the one exception to the rule that a behaviour-changing feature is off by default, see [What a release may contain](#what-a-release-may-contain). A ChronitonDB node is a different database and binary, and an operator needs to know which release is installed.
2. It has a switch, like every feature, and it is on by default.
3. It is required for a line's first release and blocks that release until it is in. The version and the git SHA it shows are read from the build, never written into the code, and its tests prove both on a built package.
4. The feature is not built yet. Until it is, `nodetool version` prints Apache's output, and the release version of an installed node is the version of its `chronitondb` package.
5. `bin/cassandra -v`, the startup log line `Cassandra version:` and the cqlsh banner stay as they are today. Any change to them is decided in their own feature spec.

## Packaging

ChronitonDB is a fork, so it has its own packaging and its own names, separate from Apache's.

1. The Debian and Red Hat packaging lives in `packaging/debian/` and `packaging/redhat/`, with the tarball script in `packaging/`. The release pipeline builds from them. `packaging/` is a sensitive path: a change to it requests a review from the code owners. The pull request that creates it adds it to `.github/CODEOWNERS`.
2. The package and its service are named `chronitondb`. Its versions follow [Version numbers](#version-numbers), for example `5.0-chronitondb1`.
3. A new install uses the configuration directory `/etc/chronitondb`, the data directory `/var/lib/chronitondb` and the system user `chronitondb`.
4. The package is declared as replacing Apache's `cassandra` package.
5. Apache's `debian/` and `redhat/` folders stay untouched, as the upstream reference.

### The configuration file

1. ChronitonDB ships its own configuration file, `conf/cassandra_chronitondb.yaml`. It started from Apache's `conf/cassandra_latest.yaml` and carries ChronitonDB's own settings and values.
2. A fresh install gets it as its `cassandra.yaml`, in `/etc/chronitondb`.
3. Apache's `conf/cassandra.yaml` and `conf/cassandra_latest.yaml` stay untouched, as the upstream reference.
4. A node switched from Apache Cassandra keeps the operator's own file.
5. Each line's upgrade runbook states the minimum setup an existing Apache Cassandra cluster MUST reach before it switches. The list is published with the line's first release.
6. A node checks the minimum setup at every start. It refuses to start when the setup is not met, and names each unmet setting and the runbook step that sets it.

Our file holds every setting of Apache's two files, active or commented, or leaves one out on a line `# Left out: <setting>: <reason>`. A setting Apache removes is removed from our file too, or flagged on a line `# Apache removed: <setting>`. A pull request check will enforce both once it exists.

How Apache's configuration changes reach our file is in [upstream.md](upstream.md#configuration-changes).

### Switching a node from Apache's package

1. The operator drains and stops the node first, as in any rolling upgrade.
2. On a node with Apache's `cassandra` installation, the `chronitondb` package's install scripts detect it.
3. They copy the configuration to `/etc/chronitondb`.
4. They reuse the existing data directory in place. No data is copied or moved.
5. They report what else on the machine still refers to `cassandra`.

A runbook covers the minimum setup to reach first, the order of nodes, the checks before and after each node, and the rollback to Apache's package.

## Release outputs

The release pipeline produces, for every release:

1. A git tag signed with the ChronitonDB release key.
2. The binary tarball.
3. Debian and Red Hat packages.
4. The software bill of materials in SPDX and in CycloneDX, published with the release.
5. The OpenVEX file, taken from [chronitonlabs/chronitondb-security-tracker](https://github.com/chronitonlabs/chronitondb-security-tracker) and published with the release. See [security.md](security.md#vex-statements).
6. Release notes, generated from the commits and `NEWS-chronitondb.txt`, naming the Apache content as [What a release contains](#what-a-release-contains) says. See [conventions.md](conventions.md#change-logs-and-release-notes).
7. SLSA Build Level 3 provenance for every artefact, through GitHub artifact attestations, once the release pipeline is built.
8. A verification pass: signatures, installs and upgrade tests.

Anything that installs or releases from a tag verifies its signature first.
