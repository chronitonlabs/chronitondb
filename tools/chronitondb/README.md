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

# ChronitonDB code checks

Two checks for the Java files under `org/chronitondb` that a change adds or modifies, and one for the process documents, `doclint.py`. Apache code is never checked by either. Both run on the staged files before each commit, and in the CI workflow `.github/workflows/chronitondb-shape.yml` on every pull request into a `chronitondb-*` branch. The rules are in [conventions.md](../../docs/process/conventions.md#shape-limits).

## Shape limits: `shape-check.sh`

Measured limits on production code, every finding blocks:

| Limit | Value | Tool |
| --- | --- | --- |
| Cyclomatic complexity per method (a `switch` counts once) | 10 | checkstyle CyclomaticComplexity |
| NPath complexity per method | 200 | checkstyle NPathComplexity |
| Boolean expression complexity | 3 operators | checkstyle BooleanExpressionComplexity |
| Method length (blank and comment lines included) | 80 lines | checkstyle MethodLength |
| Parameters per method | 7 | checkstyle ParameterNumber |
| Nested `if` depth | 3 | checkstyle NestedIfDepth |
| Nested loop depth (`for` loops, checkstyle has no module for `while`) | 2 | checkstyle NestedForDepth |
| Class fan out | 20 classes | checkstyle ClassFanOutComplexity |
| File length | 1,000 lines | checkstyle FileLength |
| Cognitive complexity per method | 15 | PMD CognitiveComplexity |
| Duplicated block | 50 tokens | PMD CPD |

Tests and benchmarks (any path with a `test/` directory before `org/chronitondb`: `test/unit`, `test/distributed`, `test/microbench`, `test/burn`) are measured with looser limits and every finding is a warning, never a failure: cyclomatic complexity 5, method length 150, file length 1,000, cognitive complexity 15, duplication 50 tokens. Testing a database is complicated, long setup is not a finding.

The rules live in `checkstyle-shape.xml` (production), `checkstyle-shape-tests.xml` (tests) and `pmd-ruleset.xml` (cognitive complexity, plus the CPD setting and the PMD pin). Changing a limit is a one line change there.

Output, one line per finding, then a summary:

    ERROR src/java/org/chronitondb/index/Foo.java:42:5 CyclomaticComplexity value=12 limit=10: Cyclomatic Complexity is 12 (max allowed is 10).
    WARN test/unit/org/chronitondb/index/FooTest.java:88:5 MethodLength value=162 limit=150: Method verify length is 162 lines (max allowed is 150).
    shape-check: 1 production finding(s) that block, 1 test warning(s), 1 production and 1 test file(s) checked

Exit 0 when nothing blocks, 1 on a production finding, 2 when the check could not run.

## Google Java Style: `format-check.sh`

ChronitonDB code follows Google Java Style, enforced with google-java-format. Production and test files alike, every unformatted file blocks, formatting has no legitimate exceptions.

    tools/chronitondb/format-check.sh src/java/org/chronitondb/index/Foo.java   report
    tools/chronitondb/format-check.sh --fix src/java/org/chronitondb/index/Foo.java   format in place

The `.editorconfig` at the repository root carries the matching editor settings (2 space indent, 100 columns) for `src/java/org/chronitondb/**` and `test/**/org/chronitondb/**` only. Other paths are not affected.

Apache's own checkstyle (`.build/checkstyle.xml`) runs over the whole tree. On the 5.0 line none of its rules touches layout or import order (banned APIs, unused and redundant imports, illegal types), so Google style needs no suppression there. The 6.0 line enforces `ImportOrder` with Cassandra's groups and static imports at the bottom, which Google style contradicts (one ASCII sorted block, static imports first), so the 6.0 port needs one `ImportOrder` suppression for `org/chronitondb` in `.build/checkstyle_suppressions.xml`, with a comment giving the reason.

## Running

    tools/chronitondb/shape-check.sh FILE...            these files
    tools/chronitondb/shape-check.sh                    the staged files (what runs before a commit)
    tools/chronitondb/shape-check.sh --base origin/chronitondb-5.0   the files changed since the merge base (what CI does)
    tools/chronitondb/shape-check.sh --self-test        the fixtures under test/
    tools/chronitondb/format-check.sh ...               same options, plus --fix

Paths that are not `org/chronitondb/**/*.java` are ignored. Checkstyle comes from the build's own test classpath, `build/test/lib/jars`, so run `ant resolver-retrieve-build` (or any build) once. PMD and google-java-format are downloaded into `build/chronitondb-shape` on first use and refused unless their sha256 matches the pin. Nothing is added to `lib/` or `build.xml`, nothing is shipped, `build/` is not committed. `SHAPE_PMD_HOME` and `SHAPE_GJF_JAR` point at copies already on disk, for offline use.

Pins:

- checkstyle 10.26.1, the version Apache's build declares in `.build/parent-pom-template.xml`.
- PMD 7.29.0, `pmd-dist-7.29.0-bin.zip` from the PMD GitHub release, sha256 recorded in `pmd-ruleset.xml` after the release signature verified against the PMD release signing key.
- google-java-format 1.37.0 all-deps jar from its GitHub release, sha256 recorded in `format-check.sh`, the same release on both lines. It needs a Java 21 JDK to run. On the 5.0 line, which builds on Java 17, set `SHAPE_GJF_JAVA_HOME` to a Java 21 JDK for `format-check.sh`.

## Tests

`test/src` and `test/test` hold one fixture per limit that breaks it and a few that pass (a 15 case `switch` with cyclomatic complexity 2, a method at cognitive complexity 15 exactly, a 100 line test method). `test/expected.txt` lists the finding each fixture must produce. `test/format` holds one formatted and one unformatted class. `--self-test` stages them as `src/java` and `test/unit` files, runs the real tools and compares. The fixtures are skipped when given to the checks by their own path, so staging them never fails a commit. CI runs both self-tests before the checks.

## Waivers

A production limit can be exceeded only with a waiver recorded in the design record of the change and approved with it, naming the method, the rule and why the shape is right there. A suppression comment in the code is not a waiver and the rules files have no suppression filter. The maintainability review lens reads the check output next to the design record and treats a broken limit without a recorded waiver as a major finding.

## Security checks

Two more checks. CI runs them on every pull request into a `chronitondb-*` branch, in `.github/workflows/chronitondb-semgrep.yml` and `chronitondb-spotbugs.yml`, each after its self-test. Both are required checks on every line, see [branching-and-review.md](../../docs/process/branching-and-review.md#required-checks).

### Semgrep: `semgrep-check.sh`

Semgrep CE from its container image, pinned by digest in the script, run with docker without network. The rules are in `semgrep/`, one file per topic:

| File | Finds | Paths |
| --- | --- | --- |
| `banned-apis.yml` | the APIs `.build/checkstyle.xml` bans in main code | `src/java/org/chronitondb` |
| `non-ascii-identifiers.yml` | a non-ASCII character outside strings and comments | any `org/chronitondb` path |
| `process-exec.yml` | `Runtime.exec` and `ProcessBuilder` with a command that is not a string literal | every Java file |
| `deserialization.yml` | `ObjectInputStream` | every Java file |
| `bidi.yml` | Unicode bidirectional control characters | every file |

    tools/chronitondb/semgrep-check.sh FILE...          these files
    tools/chronitondb/semgrep-check.sh                  the staged files
    tools/chronitondb/semgrep-check.sh --base origin/chronitondb-5.0   the files changed since the merge base, without the findings already there (what CI does)
    tools/chronitondb/semgrep-check.sh --self-test      the fixtures under test/semgrep

Semgrep runs with `--disable-nosem`, so a `nosemgrep` comment hides nothing, and a checkstyle `permit` comment does not hide a banned API from Semgrep. Needs docker and jq. `--self-test` runs `semgrep --test` on `test/semgrep` (each `ruleid` line must be reported, each `ok` line must not) and then checks the path scoping, which `--test` ignores. The bidi fixture is written at test time, so no committed file carries a bidi control character.

### SpotBugs: `spotbugs-check.sh`

SpotBugs 4.10.5 with the FindSecBugs 1.14.0 plugin on the compiled `org.chronitondb` classes, report only: findings are printed and never fail the check. Apache classes are read to resolve types and never analysed.

    tools/chronitondb/spotbugs-check.sh                 the classes under build/classes/main (run ant jar first)
    tools/chronitondb/spotbugs-check.sh CLASSES         the classes under another directory
    tools/chronitondb/spotbugs-check.sh --self-test     compile test/spotbugs and expect COMMAND_INJECTION and OBJECT_DESERIALIZATION

The jars come from Maven Central into `build/chronitondb-shape/spotbugs-4.10.5`, each refused unless its sha256 matches the pin in the script. The set is the `lib/` of the SpotBugs release, so `java -jar spotbugs.jar` finds them through its manifest.

## Process documents: `doclint.py`

Checks the process documents under `docs/` against their templates on the line, and the rules [docs/process/](../../docs/process/README.md) sets for them: the document control table, every numbered section in order, the Contents index, no template placeholder and no `[NEEDS CLARIFICATION` marker left, and per document type the feature spec, plan, milestone report, decision record and delta entry rules. It also checks the feature keys and requirement ids of [additive.md](../../docs/process/additive.md#feature-keys-and-requirement-ids) across the lines, the library declarations of [compliance.md](../../docs/process/compliance.md), and that `conf/cassandra_chronitondb.yaml` holds every setting of Apache's two yaml files ([release.md](../../docs/process/release.md#the-configuration-file)). `markdown.py` beside it is its Markdown reader. Python 3 only, no other dependency.

    tools/chronitondb/doclint.py document --repo . --templates origin/chronitondb-5.0 --source index docs/design/LUC-fulltext-search/feature-spec.md
    tools/chronitondb/doclint.py keys --repo . --base origin/chronitondb-5.0 --source index
    tools/chronitondb/doclint.py index --write docs/design/LUC-fulltext-search/feature-spec.md

The rules are read from the ref given with `--templates` or `--base`, the line, never from the change being checked. The CI workflow `.github/workflows/chronitondb-documents.yml` runs `document` on the process documents a pull request changes, and `keys` when it changes `docs/design/` or `test/bdd/`, with this file taken from the base branch. It also checks that a delta entry's issue exists and that a new feature key is not in use by another open pull request. Run `doclint.py` without arguments for every subcommand and option.

Findings, one per line, then a summary:

    docs/design/LUC-fulltext-search/feature-spec.md:45: FREQ-LUC-002 has 2 BCP 14 keywords, a requirement has exactly one (split it)
    documents 1 checked 1 failed

Exit 0 when nothing is found, 1 on a finding, 2 on a usage error.

### The Contents index

When a document's template on the line has a `## Contents` section, the document must have one too, as [conventions.md](../../docs/process/conventions.md#contents-index-of-process-documents) sets out: the first section after the title, a nested list with one link per heading below the title, in order, each entry two spaces deeper than the nearest heading above it of a higher level (a `##` not indented), each showing its heading's text and linking its GitHub anchor. Duplicate headings link `-1`, `-2` as GitHub numbers them. A decision record is asked for its index only when its number is above the highest record merged on the line, since a merged record is never edited. The check refuses a missing or misplaced section, a heading left out, an entry out of order or at the wrong depth, a link no heading of the file answers, and any other text in the section.

    tools/chronitondb/doclint.py index FILE              print the Contents section FILE needs
    tools/chronitondb/doclint.py index --write FILE...   put it in the file, in place of the old one, refused when that one holds other text
    tools/chronitondb/doclint.py index --check FILE...   report what is wrong with the index, also for a template

`index` reads the working tree and works on any Markdown file. Authors and agents run `index --write` after any heading changes and before each commit of a document.

A coverage file, `ac-coverage.md` in a design directory, is checked against the coverage file template.

### Tests

`test/doclint/` holds the checker's unit tests, Python's `unittest`, no other dependency. They include a test that every template in `docs/process/templates/` carries a correct index. The CI workflow runs them in a job of its own, apart from the job that checks the documents with the line's checker.

    python3 -m unittest discover -s tools/chronitondb/test/doclint
