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

# Open source compliance

ChronitonDB runs its open source compliance as an OpenChain programme: ISO/IEC 5230 for licence compliance and ISO/IEC 18974 for security assurance. This page says what the programme covers.

## Programme

1. **Contact.** The compliance contact is the Chroniton Labs Legal mailbox, chronitonlabs-legal@axonops.com. Security vulnerabilities are not reported there: use the private reporting in [security.md](security.md).
2. **Licence.** ChronitonDB is released under the Apache License 2.0. Changes made in ChronitonDB are licensed under the same licence.
3. **Contributions.** Contributions are made under the Chroniton Labs contributor agreements, signed through the agreement check on each pull request. See [contributing.md](contributing.md).
4. **Known vulnerabilities.** The vulnerability process in [security.md](security.md) and the VEX statements below cover the security assurance side. The security engineer checks every shipped library daily against OSV, the GitHub advisory database and NVD, and writes the VEX statements. See [roles.md](roles.md#security-engineer).
5. **Self-certification.** OpenChain self-certification for both standards is planned before the first release.

## Third party licences

Every third party component is checked against the Apache Software Foundation licence categories, as Apache Cassandra does.

| Category | Meaning here | Examples |
|---|---|---|
| A | MAY be included in source and binary form | Apache License 2.0, MIT, BSD |
| B | MAY be included in binary form only, with the conditions the ASF policy sets | EPL, MPL, CDDL |
| X | MUST NOT be included | GPL, LGPL, AGPL |

## Declaring dependencies

1. Every new dependency, and every version change of an existing one, MUST be declared before use. For a feature it goes in the feature spec's Dependencies section. For a one-item change it goes in the design record's Dependencies section.
2. Each declaration gives the library and version, its ASF licence category, the NOTICE and credit lines it needs, its known vulnerabilities and why it is needed.
3. The maintainers approve the declaration by merging the document. A library that no merged document declares is refused at review.
4. `build.xml`, `lib/`, `packaging/` and the other build inputs are sensitive paths with code owner review. See [branching-and-review.md](branching-and-review.md#sensitive-paths).
5. A patch-version update of an approved library, under the same licence, for a bug or security fix, MAY be made without a fix record or design record. The pull request description gives the reason, and the SBOM and VEX record the change. See [maintenance.md](maintenance.md#dependency-patch-version-updates).

## NOTICE and credits

1. `NOTICE.txt` keeps every notice that comes with Apache Cassandra. Each new dependency adds the NOTICE text its licence asks for.
2. Code taken from Apache Cassandra keeps its original author, its Apache headers and a citation of its Apache ticket and commit.
3. Code taken from another project keeps its authors and headers. Adapted work credits its authors with `Co-authored-by:` and adds a NOTICE entry where the licence asks for one.
4. An idea taken from elsewhere and written fresh is credited in the commit message.
5. The details are in [conventions.md](conventions.md#code-from-elsewhere).

## SBOM, VEX and provenance

1. Each release ships its software bill of materials in SPDX (ISO/IEC 5962) and in CycloneDX (ECMA-424).
2. Each release ships an OpenVEX file for the known vulnerabilities in its shipped components, kept by the security engineer. See [security.md](security.md#vex-statements).
3. With the release pipeline, each release artefact will carry SLSA Build Level 3 provenance through GitHub artifact attestations.
4. With the release pipeline, the repository will run OpenSSF Scorecard weekly with public results.

The SBOM and VEX files are public. The release pipeline publishes them with each release. See [release.md](release.md#release-outputs).
