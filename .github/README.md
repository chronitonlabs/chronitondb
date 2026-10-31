<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://github.com/chronitonlabs/brand/raw/main/chronitondb/chronitondb-lockup-dark.svg">
    <img alt="ChronitonDB" src="https://github.com/chronitonlabs/brand/raw/main/chronitondb/chronitondb-lockup-light.svg" width="358">
  </picture>
</p>

<h3 align="center">Powered by <a href="https://cassandra.apache.org/">Apache Cassandra</a>®</h3>

> [!WARNING]
> **ChronitonDB is in early development and is being bootstrapped.** Nothing here is ready to use yet. Do not run it, build on it or depend on it. Expect branches, settings and history to change without notice.

ChronitonDB is an open source database built on [Apache Cassandra](https://cassandra.apache.org/). It adds features and fixes, and aims to stay compatible with Apache Cassandra. Find out more at [chronitonlabs.org](https://chronitonlabs.org/projects/chronitondb/).

## How the project is managed

[AxonOps](https://axonops.com) is the steward of ChronitonDB. A project needs someone to own its name, hold its contributor agreements, make its releases and stand behind them. AxonOps takes that role. ChronitonDB itself is open source and stays open source.

- **Apache License 2.0, always.** ChronitonDB is released under the Apache License 2.0 and will stay under it. There will be no license change and no proprietary edition with features held back.
- **Apache Cassandra comes first.** We aim to offer our fixes and features to the Apache Cassandra project and work to get them accepted there. Work we bring in from Apache Cassandra keeps its original authors.
- **A way back to Apache Cassandra.** We aim to keep a supported path from ChronitonDB back to Apache Cassandra, and we document any feature that makes going back harder.

## Branches

| Branch | Based on | Status |
|---|---|---|
| `chronitondb-5.0` (default) | Apache Cassandra 5.0 | in development |
| `chronitondb-6.0` | Apache Cassandra 6.0 (not yet released by Apache) | in development |

## Moving from Apache Cassandra

ChronitonDB is built on Apache Cassandra 5.0 and later. A cluster on an earlier version of Apache Cassandra must first be upgraded to Apache Cassandra 5.0, with the upgrade fully completed and the settings that upgrade requires in place, before it can move to ChronitonDB 5.0.

## Contributing

Contributions are made under the Chroniton Labs contributor agreements. Before your first pull request is merged, you sign the agreement through the CLA Assistant check on that pull request. The agreements, a plain English summary and how to sign are at https://github.com/chronitonlabs/contributor-agreements. Contribution guidelines are in [CONTRIBUTING.md](CONTRIBUTING.md).

## How we work

- [Development process](../docs/process/README.md): how a change goes from an idea to a merged commit.
- [Contributing](../docs/process/contributing.md): raising issues and contributing changes.
- [Security](../docs/process/security.md): reporting a vulnerability privately.
- [Governance](../docs/process/governance.md): maintainers, committers and commit rights.
- [Releases](../docs/process/release.md): release cadence, support lifetime and version numbers.

## License and notices

ChronitonDB is licensed under the [Apache License, Version 2.0](../LICENSE.txt).

ChronitonDB is a modified version of Apache Cassandra. Apache Cassandra is Copyright 2009 and later The Apache Software Foundation and is licensed under the Apache License, Version 2.0. The notices that come with Apache Cassandra are kept in [NOTICE.txt](../NOTICE.txt), and the original Apache Cassandra README is kept in [README.asc](../README.asc).

Changes made in ChronitonDB are Copyright 2026 AxonOps Limited and are licensed under the Apache License, Version 2.0.

## Trademarks

Apache®, Apache Cassandra®, Cassandra®, the Apache Cassandra Eye logo, Apache Lucene® and Lucene® are either registered trademarks or trademarks of the Apache Software Foundation in the United States and/or other countries. No endorsement by The Apache Software Foundation is implied by the use of these marks. ChronitonDB is not affiliated with, endorsed by or sponsored by The Apache Software Foundation.

ChronitonDB™ is a trademark of AxonOps Limited. AxonOps® is a registered trademark of AxonOps Limited.
