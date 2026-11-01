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

Two checks for the Java files under `org/chronitondb` that a change adds or modifies. Apache code is never checked by either. Both run on the staged files before each commit, and in the CI workflow `.github/workflows/chronitondb-shape.yml` on every pull request into a `chronitondb-*` branch. The rules are in [conventions.md](../../docs/process/conventions.md#shape-limits).

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

Apache's own checkstyle (`.build/checkstyle.xml` and `.build/checkstyle_test.xml`) runs over the whole tree. The 6.0 line enforces `ImportOrder` with Cassandra's groups and static imports at the bottom, which Google style contradicts (one ASCII sorted block, static imports first). So `.build/checkstyle_suppressions.xml`, which both configs read, carries one `ImportOrder` suppression for `org/chronitondb` paths, with a comment giving the reason. `AvoidStarImport` stays on for ChronitonDB code, Google style forbids wildcard imports too. The 5.0 line has no `ImportOrder` rule and needs no suppression.

## Running

    tools/chronitondb/shape-check.sh FILE...            these files
    tools/chronitondb/shape-check.sh                    the staged files (what runs before a commit)
    tools/chronitondb/shape-check.sh --base origin/chronitondb-6.0   the files changed since the merge base (what CI does)
    tools/chronitondb/shape-check.sh --self-test        the fixtures under test/
    tools/chronitondb/format-check.sh ...               same options, plus --fix

Paths that are not `org/chronitondb/**/*.java` are ignored. Checkstyle comes from the build's own test classpath, `build/test/lib/jars`, so run `ant resolver-retrieve-build` (or any build) once. On 6.0 that target also builds the `modules/accord` submodule, so run `git submodule update --init` first. PMD and google-java-format are downloaded into `build/chronitondb-shape` on first use and refused unless their sha256 matches the pin. Nothing is added to `lib/` or `build.xml`, nothing is shipped, `build/` is not committed. `SHAPE_PMD_HOME` and `SHAPE_GJF_JAR` point at copies already on disk, for offline use.

Pins:

- checkstyle 10.26.1, the version Apache's build declares in `.build/parent-maven-pom.xml` on the 6.0 line.
- PMD 7.29.0, `pmd-dist-7.29.0-bin.zip` from the PMD GitHub release, sha256 recorded in `pmd-ruleset.xml` after the release signature verified against the PMD release signing key.
- google-java-format 1.37.0 all-deps jar from its GitHub release, sha256 recorded in `format-check.sh`, equal to the digest GitHub publishes for the asset and to Maven Central's `.sha256`. It needs a Java 21 JDK, so run `format-check.sh` with `JAVA_HOME` at 21, or `SHAPE_GJF_JAVA_HOME` pointing at a Java 21 JDK, even when the build uses 11 or 17 (`build.xml` supports 11, 17 and 21 on this line). The CI workflow runs on Temurin 21. The 5.0 line pins the same release.

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
