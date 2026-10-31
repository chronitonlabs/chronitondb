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

## Support lifetime

1. Each line is supported for 5 years from its first ChronitonDB release, whatever Apache Cassandra does with its major version.
2. The support end date of each line is published with its first release.
3. After Apache's own end of life for a major version, security fixes and critical fixes are carried back to the line from newer Apache Cassandra versions.

Supported versions are listed in the README of the repository.

## What a release may contain

1. Any release MAY ship fixes, imports from Apache Cassandra and security fixes.
2. A release MAY ship a finished feature that the operator can switch on with yaml or nodetool.
3. Within a line, a feature's default MUST stay off. Upgrading within a line never changes behaviour by itself.
4. A feature's default MAY be on only in a new line.

A feature becomes switchable at its final milestone gate. Before that, its switch refuses to turn on. See [additive.md](additive.md#milestone-gates) and [branching-and-review.md](branching-and-review.md#every-fork-feature-is-off-by-default).

## How a release is made

Every release takes two maintainer approvals, and each one is the merge of a pull request, like every approval in this project: the release proposal, before the candidate is built, and the promotion, after the soak and verification. The reviewer reviews both pull requests first.

1. **Proposal.** The release engineer opens a release proposal pull request that adds `docs/releases/<version>.md`: the version, the exact commit on the line it is built from, what goes in, from the commits on the line, the milestone gates passed and the security fixes due.
2. **First approval.** A maintainer merges the proposal pull request. Nothing is built, tagged or published before that merge.
3. **Release candidate.** A maintainer starts the release workflow by hand when the candidate is wanted, giving the version. Building and testing a candidate is expensive, so a maintainer chooses the moment. The workflow refuses to run unless that version's proposal is merged. The candidate tag is signed at the commit the proposal names, so anything merged later stays out. The pipeline then builds, tests and publishes the release candidate: a GitHub pre-release, and packages in a separate proposed package repository for Debian and Red Hat.
4. **Verification.** The release engineer verifies the candidate: signatures, installs, upgrade and rollback from the previous ChronitonDB release and from Apache Cassandra, and the parity suite.
5. **Soak.** The candidate stays in the proposed channel for 7 days.
6. **Second approval and promotion.** If the verification passed and no problem is reported during the soak, the release engineer opens a promotion pull request that adds the verification results to `docs/releases/<version>.md`. A maintainer merges it, and the candidate is then promoted unchanged to the official release.

A security release skips the soak once it is verified. It ships on the date the maintainers set. See [security.md](security.md).

## Freezes

1. There is no freeze on a line for its patch releases. The signed release candidate tag is the freeze.
2. A problem found during the soak is fixed on the line. A new candidate is then cut, and the soak starts again.
3. A feature freeze starts 4 weeks before the first release of a new line. After it, only fixes and imports go into that line until its first release.

## Version numbers

ChronitonDB versions follow the pattern Ubuntu uses for packages it takes from Debian.

| Form | Example | Meaning |
|---|---|---|
| `<Apache version>-chronitondb<n>` | `5.0.10-chronitondb1` | The first ChronitonDB release containing Apache Cassandra 5.0.10 |
| The same, `n` raised by one | `5.0.10-chronitondb2` | A further ChronitonDB release on the same Apache version |
| A new Apache version, `n` from 1 | `5.0.11-chronitondb1` | The first ChronitonDB release containing Apache Cassandra 5.0.11 |
| `<version>~rc<k>` | `5.0.10-chronitondb1~rc1` | The package version of a release candidate |
| `<version>-rc<k>` | `5.0.10-chronitondb1-rc1` | The git tag of a release candidate |
| Apache's development version | `6.0.0-alpha2-chronitondb1` | A build from Apache's branch before Apache's first release of that major version |

1. The git tag of a release is the version itself, for example `5.0.10-chronitondb1`, next to Apache's own `cassandra-5.0.10` tag. The git tag of a release candidate uses `-rc<k>` in place of `~rc<k>`, since git does not allow `~` in a tag name.
2. Release and release candidate tags are signed with the dedicated ChronitonDB release key, not with a person's key. Its public key is published so users can verify the tags.
3. Debian and Red Hat package tools order these versions correctly, release candidates before their release.
4. In strict Semantic Versioning the hyphen marks a pre-release. We accept that for packages and tags, as Ubuntu does.

### The version a running node reports

A running node reports a different string from its package version, in `nodetool version`, `system.local`, `system.peers_v2`, gossip and the drivers: `<Apache version>+chronitondb.<feature level>`, for example `5.0.10+chronitondb.1`.

1. Apache Cassandra and its drivers read a hyphen in a node's version as a pre-release, so `5.0.10-chronitondb1` would compare as older than Apache Cassandra 5.0.10. They read the part after `+` as build information, so `5.0.10+chronitondb.1` compares as 5.0.10.
2. The feature level is a number in the code, raised only when a release changes how nodes work together. Features that need every node to cooperate turn on once every node reports their level.
3. A node in Apache compatibility mode reports the plain Apache version, for example `5.0.10`.
4. The package version and the git tag say which build is installed. The node's version says which Apache version it carries and its feature level.

## Packaging

ChronitonDB is a fork, so it has its own packaging and its own names, separate from Apache's.

1. The Debian and Red Hat packaging lives in `packaging/debian/` and `packaging/redhat/`, with the tarball script in `packaging/`. The release pipeline builds from them. `packaging/` is a sensitive path with code owner review.
2. The package and its service are named `chronitondb`. Its versions follow [Version numbers](#version-numbers), for example `5.0.10-chronitondb1`.
3. A new install uses the configuration directory `/etc/chronitondb`, the data directory `/var/lib/chronitondb` and the system user `chronitondb`.
4. The package is declared as replacing Apache's `cassandra` package.
5. Apache's `debian/` and `redhat/` folders stay untouched, as the upstream reference.

### Switching a node from Apache's package

1. The operator drains and stops the node first, as in any rolling upgrade.
2. On a node with Apache's `cassandra` installation, the `chronitondb` package's install scripts detect it.
3. They copy the configuration to `/etc/chronitondb`.
4. They reuse the existing data directory in place. No data is copied or moved.
5. They report what else on the machine still refers to `cassandra`.

A runbook covers the order of nodes, the checks before and after each node, and the rollback to Apache's package.

## Release outputs

The release pipeline produces, for every release:

1. A git tag signed with the ChronitonDB release key.
2. The binary tarball.
3. Debian and Red Hat packages.
4. The software bill of materials in SPDX and in CycloneDX, published with the release.
5. The OpenVEX file, published with the release. See [security.md](security.md#vex-statements).
6. Release notes, generated from the commits and `NEWS-chronitondb.txt`. See [conventions.md](conventions.md#change-logs-and-release-notes).
7. SLSA Build Level 3 provenance for every artefact, through GitHub artifact attestations, once the release pipeline is built.
8. A verification pass: signatures, installs and upgrade tests.

Anything that installs or releases from a tag verifies its signature first.
