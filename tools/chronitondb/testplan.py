#!/usr/bin/env python3
#
# Copyright 2026 AxonOps Limited
# SPDX-License-Identifier: Apache-2.0
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
"""Reads what a pull request's tests need, for the CI workflow
chronitondb-changed-tests.yml.

    testplan.py impact --repo DIR --base REF
    testplan.py coverage --repo DIR --base REF --report FILE

impact reads each short record the pull request adds or changes,
docs/design/<issue>-<slug>/short-record.md, and in its section 4 the impact
analysis table: the table with a column Proving tests. Every test class
named in that column is looked up under test/unit and test/distributed, by
its full name or by its class name alone. It prints one line for each
class found, its kind and its full name, where the kind is unit,
distributed or upgrade (a class under a directory named upgrade). A name
that matches no class is an error, and so is a class name alone that
matches more than one class. A record with no such table names nothing.
Exit 0, or 1 on an error.

coverage reads the JaCoCo XML report FILE and the lines the pull request
adds or changes in the Java files under src/java, and prints a Markdown
table of the methods those lines fall in: line and branch coverage, the
cyclomatic complexity and, for a method under org/chronitondb, the CRAP
score, complexity squared times the uncovered share of its lines cubed,
plus its complexity. A score above 30 is marked. A changed line counts when
JaCoCo has code on it, and it falls in the method whose first line of code
is the nearest at or above it. Exit 0, or 2 when the report cannot be read.
"""

import argparse
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ElementTree

RECORDS = "docs/design/*/short-record.md"
TEST_ROOTS = ("test/unit", "test/distributed")
CLASS_NAME = re.compile(r"(?<![\w.])((?:[a-z_][a-z0-9_]*\.)*[A-Z][A-Za-z0-9_]*Test)(?![A-Za-z0-9_])")
HUNK = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@")
CRAP_LIMIT = 30


def git(repo, *args):
    done = subprocess.run(["git", "-C", repo] + list(args), capture_output=True, text=True, check=False)
    if done.returncode != 0:
        sys.stderr.write(done.stderr)
        return None
    return done.stdout


def changed_records(repo, base):
    listed = git(repo, "diff", "--name-only", "--diff-filter=ACMR", base + "...HEAD", "--", RECORDS)
    return [] if listed is None else [path for path in listed.splitlines() if path]


def section_four(text):
    """The lines of section 4 of a short record, its heading left out."""
    lines = text.split("\n")
    start = next((i for i, line in enumerate(lines) if re.match(r"^## 4\.", line)), None)
    if start is None:
        return []
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
    return lines[start + 1:end]


def cells(line):
    text = line.strip()
    if text.startswith("|"):
        text = text[1:]
    if text.endswith("|"):
        text = text[:-1]
    return [cell.strip() for cell in text.split("|")]


def proving_tests(text):
    """The class names in the Proving tests column of the impact analysis
    table of section 4, in the order they first appear."""
    names = []
    column = None
    for line in section_four(text):
        if not line.strip().startswith("|"):
            column = None
            continue
        row = cells(line)
        if column is None:
            headers = [cell.lower() for cell in row]
            column = next((i for i, header in enumerate(headers) if "proving tests" in header), -1)
            continue
        if column < 0 or column >= len(row) or re.fullmatch(r"[\s:|-]*", line):
            continue
        for name in CLASS_NAME.findall(row[column]):
            if name not in names:
                names.append(name)
    return names


def test_classes(repo):
    """Every test class file under the test roots, as paths from the repository root."""
    found = []
    for root in TEST_ROOTS:
        for folder, _, files in os.walk(os.path.join(repo, root)):
            for name in files:
                if name.endswith("Test.java"):
                    found.append(os.path.relpath(os.path.join(folder, name), repo).replace(os.sep, "/"))
    return sorted(found)


def kind_and_name(path):
    root = next(root for root in TEST_ROOTS if path.startswith(root + "/"))
    name = path[len(root) + 1:-len(".java")].replace("/", ".")
    if root == "test/unit":
        return "unit", name
    return ("upgrade" if "/upgrade/" in path else "distributed"), name


def resolve(name, paths):
    """The paths a name in a record stands for."""
    if "." in name:
        return [path for path in paths if kind_and_name(path)[1] == name]
    return [path for path in paths if path.rsplit("/", 1)[-1] == name + ".java"]


def impact(repo, base):
    paths = test_classes(repo)
    errors = []
    found = []
    for record in changed_records(repo, base):
        with open(os.path.join(repo, record), encoding="utf-8") as handle:
            names = proving_tests(handle.read())
        if not names:
            sys.stderr.write("%s names no test class in an impact analysis table\n" % record)
        for name in names:
            matches = resolve(name, paths)
            if not matches:
                errors.append("%s names %s, and no test class under test/unit or test/distributed has that name" % (record, name))
            elif len(matches) > 1:
                errors.append("%s names %s, which is the name of %s. Give the full name" % (record, name, " and ".join(matches)))
            elif kind_and_name(matches[0]) not in found:
                found.append(kind_and_name(matches[0]))
    for error in errors:
        sys.stderr.write("%s\n" % error)
    for kind, name in found:
        print("%s %s" % (kind, name))
    return 1 if errors else 0


def changed_lines(repo, base):
    """The lines each Java file under src/java gains or changes, by path."""
    diff = git(repo, "diff", "-U0", "--diff-filter=AMR", base + "...HEAD", "--", "src/java/*.java")
    lines = {}
    path = None
    for line in (diff or "").splitlines():
        if line.startswith("+++ "):
            path = line[6:] if line.startswith("+++ b/") else None
            continue
        match = HUNK.match(line)
        if match and path:
            start, count = int(match.group(1)), int(match.group(2) or "1")
            lines.setdefault(path, set()).update(range(start, start + count))
    return lines


def counter(element, kind):
    for item in element.findall("counter"):
        if item.get("type") == kind:
            return int(item.get("covered")), int(item.get("missed"))
    return 0, 0


def share(covered, missed):
    return covered / (covered + missed) if covered + missed else 1.0


def crap(complexity, covered_share):
    return complexity * complexity * (1 - covered_share) ** 3 + complexity


def methods_of(package, source):
    """The methods of the classes compiled from one source file, by their first line of code."""
    found = []
    for item in package.findall("class"):
        if item.get("sourcefilename") != source:
            continue
        for method in item.findall("method"):
            if method.get("line"):
                found.append((int(method.get("line")), item.get("name"), method))
    return sorted(found, key=lambda entry: entry[0])


def coverage_rows(report, changed):
    rows = []
    missing = []
    packages = {package.get("name"): package for package in report.iter("package")}
    for path in sorted(changed):
        folder, source = path[len("src/java/"):].rsplit("/", 1)
        package = packages.get(folder)
        code = set()
        if package is not None:
            for item in package.findall("sourcefile"):
                if item.get("name") == source:
                    code = {int(line.get("nr")) for line in item.findall("line")}
        touched = sorted(changed[path] & code)
        methods = methods_of(package, source) if package is not None else []
        if not methods or not touched:
            missing.append(path)
            continue
        hit = []
        for number in touched:
            above = [entry for entry in methods if entry[0] <= number]
            if above and above[-1] not in hit:
                hit.append(above[-1])
        for _, owner, method in hit:
            lines = counter(method, "LINE")
            branches = counter(method, "BRANCH")
            complexity = sum(counter(method, "COMPLEXITY"))
            score = ""
            if owner.startswith("org/chronitondb/"):
                value = crap(complexity, share(*lines))
                score = "%.1f%s" % (value, " (above %d)" % CRAP_LIMIT if value > CRAP_LIMIT else "")
            rows.append("| `%s.%s` | %d of %d | %d of %d | %d | %s |" % (owner.replace("/", "."), method.get("name"), lines[0], sum(lines),
                                                                        branches[0], sum(branches), complexity, score or "stock method"))
    return rows, missing


def coverage(repo, base, report_path):
    try:
        report = ElementTree.parse(report_path).getroot()
    except (OSError, ElementTree.ParseError) as error:
        sys.stderr.write("the JaCoCo report %s cannot be read: %s\n" % (report_path, error))
        return 2
    changed = changed_lines(repo, base)
    print("## Coverage of the changed methods")
    print()
    if not changed:
        print("The pull request changes no Java file under src/java.")
        return 0
    rows, missing = coverage_rows(report, changed)
    if rows:
        print("| Method | Lines covered | Branches covered | Complexity | CRAP |")
        print("|---|---|---|---|---|")
        for row in rows:
            print(row)
    for path in missing:
        print()
        print("%s: no changed line of code in the report, so no method of it is listed." % path)
    return 0


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", choices=("impact", "coverage"))
    parser.add_argument("--repo", required=True)
    parser.add_argument("--base", required=True)
    parser.add_argument("--report")
    found = parser.parse_args(argv)
    if found.command == "impact":
        return impact(found.repo, found.base)
    if not found.report:
        parser.error("coverage needs --report")
    return coverage(found.repo, found.base, found.report)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
