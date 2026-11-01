<!--
#
# Copyright 2026 AxonOps Limited
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
-->

# Contributing to ChronitonDB

Thank you for your interest in ChronitonDB. Start with the [Chroniton Labs contributing guide](https://github.com/chronitonlabs/.github/blob/main/CONTRIBUTING.md): the contributor agreement, pull requests, commit messages and AI-assisted contributions work the same way in every Chroniton Labs project. This page adds what is specific to ChronitonDB.

For building, testing and code style, ChronitonDB follows Apache Cassandra. The Apache Cassandra guide in [CONTRIBUTING.md](../CONTRIBUTING.md) at the root of this repository applies, except where this page says otherwise. Issues live on [GitHub Issues](https://github.com/chronitonlabs/chronitondb/issues), not the Apache Cassandra JIRA.

## Branches

| Branch | Use it for |
|---|---|
| `chronitondb-5.0` (default) | Work on the ChronitonDB 5.0 line |
| `chronitondb-6.0` | Work on the ChronitonDB 6.0 line |

Open your pull request against the line your change is for. If a change belongs on both lines, open it against the oldest line, `chronitondb-5.0`, and say so in the pull request. A maintainer carries it forward to the newer line in a pull request of its own.

## Changing Apache Cassandra files

Do not change Apache Cassandra files beyond what your change needs. Every extra difference makes future imports from Apache Cassandra harder.

## Changes from Apache Cassandra

ChronitonDB brings in fixes and features from Apache Cassandra. Maintainers handle these imports. If you need an Apache Cassandra change in ChronitonDB, open an issue naming the Apache commit or the CASSANDRA ticket.

ChronitonDB aims to offer its own fixes and features to the Apache Cassandra project. If your change fixes a problem that also exists in Apache Cassandra, consider contributing it there as well, following the Apache Cassandra guide.

## Security issues

Do not report security vulnerabilities in public issues or pull requests. See the [Chroniton Labs security policy](https://github.com/chronitonlabs/.github/blob/main/SECURITY.md).
