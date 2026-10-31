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

# Governance

This page says who makes decisions on ChronitonDB and how someone gains or loses the right to merge. It follows the model Ubuntu uses for upload rights.

Governance is separate from the contributor agreements. Every contributor signs an agreement before their first pull request is merged. Signing one gives no rights to merge. See [contributing.md](contributing.md#before-you-start).

## Two levels

| Level | Rights | Appointed by |
|---|---|---|
| Committer | Merges pull requests in an area, a set of paths in `.github/CODEOWNERS`, or for a whole line | The maintainers |
| Maintainer | Merges across the project, approves releases, decides security disclosures, commit rights and changes to the process | AxonOps Limited, as copyright owner |

1. The maintainers decide scope, priority, releases and security disclosure. They approve every step of the process by merging its pull request. See [roles.md](roles.md#maintainer).
2. Only maintainers and committers merge into the lines, each within their rights, and only after the reviewer's review is posted.

## Becoming a committer

1. **Nomination.** A maintainer MAY nominate a contributor with a public track record, for example several merged pull requests over some months.
2. **Decision.** The maintainers decide on the nomination, and the area or line it covers. AxonOps Limited, as copyright owner, keeps the final say on every grant and removal of rights.
3. **Record.** The grant is recorded in the public record below.

## Staying active

1. A committer or maintainer is active with at least one merged pull request, review or merge in their area within the last 12 months.
2. Rights of someone who is not active lapse quietly, with thanks.
3. Lapsed rights are restored on request.

## Removal

Rights are removed for a breach of the [code of conduct](contributing.md#code-of-conduct).

## Public record

1. [docs/governance/committers.md](../governance/committers.md) lists each committer and maintainer, the area or line of their rights, and the date since when they hold them.
2. Each grant, lapse, restoration or removal has a [decision record](../decisions/README.md) with its reason.

## Changes to this page

Changes to the governance and the process are decided by the maintainers and follow the documentation only path in [maintenance.md](maintenance.md#documentation-only-changes). `.github/CODEOWNERS` assigns `docs/process/` and `docs/governance/` to the maintainers team, so a change there needs a maintainer's review.
