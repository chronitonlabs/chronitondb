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
"""The delta register check, docs/delta/README.md, Keeping it current: a
change to a stock file needs an entry, each entry it adds or changes is in
its template's form with its index row, and no entry is renamed or
deleted. Run from the repository root:

    python3 -m unittest discover -s tools/chronitondb/test/doclint
"""

import contextlib
import io
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

TOOLS = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
ROOT = os.path.normpath(os.path.join(TOOLS, "..", ".."))
sys.path.insert(0, TOOLS)
import doclint  # noqa: E402

APACHE_HASH = "3f1593064cc89f3884e982dd74cb41b9d825bc1f"
FORK_HASH = "579e35ae6c12d0b5a1f4e3c2b7a8d9e0f1a2b3c4"
STOCK = "src/java/org/apache/cassandra/service/StorageService.java"
OURS = "src/java/org/chronitondb/startup/DiskCheck.java"

APACHE_ORIGIN = "Apache commit [`3f1593064c`](https://github.com/apache/cassandra/commit/%s), taken whole." % APACHE_HASH
FORK_ORIGIN = ("Another fork, rustyrazorblade/cassandra, commit [`579e35ae6c12`]"
               "(https://github.com/rustyrazorblade/cassandra/commit/%s)." % FORK_HASH)


def run(*args):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = doclint.main(list(args))
    return rc, out.getvalue(), err.getvalue()


def read(path):
    with open(os.path.join(ROOT, path), encoding="utf-8") as handle:
        return handle.read()


def entry(title="Storage service hook", origin="ChronitonDB.", bug="none",
          forwarded="Not needed. The hook only calls ChronitonDB code.",
          added="2026-11-01", updated="2026-11-01", area="Storage: `%s`." % STOCK,
          lines="`chronitondb-5.0` and `chronitondb-6.0`."):
    """A delta entry in the form of the template on this branch."""
    return "\n".join([
        "# Delta: %s" % title, "",
        "| Field | Value |", "|---|---|",
        "| Title | %s |" % title,
        "| Document type | Record (ISO/IEC/IEEE 15289) |",
        "| Status | Current |",
        "| Version | 1 |",
        "| Author | The maintainers |",
        "| Approver | The maintainer who merges the pull request |",
        "| References | The Origin, Bug, Bug-ChronitonDB and Pull requests fields below. |", "",
        "Change history: the git history of this file.", "",
        "## Contents", "",
        "- [Header](#header)", "- [What](#what)", "- [Why](#why)", "- [Area](#area)", "- [Lines](#lines)", "",
        "## Header", "",
        "| Field | Value |", "|---|---|",
        "| Description | %s. |" % title,
        "| Origin | %s |" % origin,
        "| Bug | %s |" % bug,
        "| Bug-ChronitonDB | none |",
        "| Forwarded | %s |" % forwarded,
        "| Added | %s |" % added,
        "| Last-Update | %s |" % updated,
        "| Pull requests | `chronitondb-5.0`: #1, commit `abcdef1234`. |", "",
        "## What", "", "What we carry.", "",
        "## Why", "", "Why we carry it.", "",
        "## Area", "", area, "",
        "## Lines", "", lines, ""])


def row(name, title="Storage service hook", area="Storage", lines="5.0, 6.0", forwarded="Not needed",
        added="2026-11-01", updated="2026-11-01"):
    return "| [%s](%s) | %s | %s | %s | %s | %s | none |" % (title, name, area, lines, forwarded, added, updated)


def step_env(workflow, name, context):
    """The environment the step NAME of a workflow file sets: each line of
    its "env:" block, with a value "${{ <name> }}" read from context. A
    value that is more than one such name cannot be worked out here and
    raises KeyError."""
    lines = read(workflow).split("\n")
    start = lines.index("      - name: %s" % name)
    index = next(i for i in range(start, len(lines)) if lines[i].strip() == "env:")
    found = {}
    for line in lines[index + 1:]:
        match = re.match(r"^\s+([A-Z_]+): \$\{\{ (.*) \}\}$", line)
        if not match:
            break
        found[match.group(1)] = context[match.group(2)]
    return found


def step_script(workflow, name):
    """The shell script of the step NAME of a workflow file: the lines of
    its "run: |" block, as the runner gives them to bash."""
    lines = read(workflow).split("\n")
    start = lines.index("      - name: %s" % name)
    index = next(i for i in range(start, len(lines)) if lines[i].strip() == "run: |")
    indent = len(lines[index]) - len(lines[index].lstrip()) + 2
    script = []
    for line in lines[index + 1:]:
        if line.strip() and len(line) - len(line.lstrip()) < indent:
            break
        script.append(line[indent:])
    return "\n".join(script) + "\n"


def register(*rows):
    return "\n".join(["# The delta register", "", "## Index", "",
                      "| Entry | Area | Lines | Forwarded | Added | Last update | Issue |",
                      "|---|---|---|---|---|---|---|"] + list(rows)) + "\n"


class Delta(unittest.TestCase):

    def setUp(self):
        self.repo = tempfile.mkdtemp()
        self.git("init", "-q")
        self.put("docs/process/templates/delta-entry.md", read("docs/process/templates/delta-entry.md"))
        self.put("docs/process/conventions.md", read("docs/process/conventions.md"))
        self.put("docs/delta/README.md", register())
        self.put(STOCK, "class StorageService {}\n")
        self.put(OURS, "class DiskCheck {}\n")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "line")
        self.git("branch", "-f", "line")
        self.git("checkout", "-q", "-b", "change")

    def tearDown(self):
        shutil.rmtree(self.repo)

    def git(self, *args):
        return subprocess.run(["git", "-C", self.repo, "-c", "user.name=t", "-c", "user.email=t@example.org",
                               "-c", "commit.gpgsign=false", "-c", "core.hooksPath=/dev/null"] + list(args),
                              check=True, capture_output=True, text=True).stdout

    def put(self, path, text):
        full = os.path.join(self.repo, path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8") as handle:
            handle.write(text)

    def commit(self, date=None):
        self.git("add", "-A")
        env = dict(os.environ)
        if date:
            env["GIT_COMMITTER_DATE"] = date + "T12:00:00Z"
        subprocess.run(["git", "-C", self.repo, "-c", "user.name=t", "-c", "user.email=t@example.org",
                        "-c", "commit.gpgsign=false", "-c", "core.hooksPath=/dev/null", "commit", "-q", "-m", "change"],
                       check=True, capture_output=True, env=env)

    def delta(self, branch=None, body=None):
        args = ["delta", "--repo", self.repo, "--base", "line", "--source", "HEAD"]
        if branch:
            args += ["--branch", branch]
        if body is not None:
            path = os.path.join(self.repo, ".git", "body.txt")
            with open(path, "w", encoding="utf-8") as handle:
                handle.write(body)
            args += ["--body", path]
        return run(*args)

    def stock_change_with(self, name, text, index_row):
        self.put(STOCK, "class StorageService { void hook() {} }\n")
        self.put("docs/delta/" + name, text)
        self.put("docs/delta/README.md", register(index_row))
        self.commit()
        return self.delta()

    # Entries of each Origin.

    def test_an_apache_commit_taken_whole_passes(self):
        rc, out, err = self.stock_change_with(
            "run-ci-routing.md",
            entry(origin=APACHE_ORIGIN, bug="[CASSANDRA-21319](https://issues.apache.org/jira/browse/CASSANDRA-21319)",
                  forwarded="Not needed. Apache has it on its 6.0 branch."),
            row("run-ci-routing.md"))
        self.assertEqual((rc, err), (0, ""))
        self.assertIn("stock %s" % STOCK, out)
        self.assertIn("delta 1 stock files 1 entries passed", out)

    def test_a_fork_import_naming_the_forks_commit_passes(self):
        rc, out, err = self.stock_change_with("fork-change.md", entry(origin=FORK_ORIGIN), row("fork-change.md"))
        self.assertEqual((rc, err), (0, ""))

    def test_a_chronitondb_original_passes(self):
        rc, out, err = self.stock_change_with("storage-hook.md", entry(), row("storage-hook.md"))
        self.assertEqual((rc, err), (0, ""))

    def test_a_backport_of_part_of_an_apache_commit_passes(self):
        origin = "Backport of Apache commit [`3f1593064c`](https://github.com/apache/cassandra/commit/%s). Only one file is taken." % APACHE_HASH
        rc, out, err = self.stock_change_with("backport.md", entry(origin=origin), row("backport.md"))
        self.assertEqual((rc, err), (0, ""))

    # A missing entry.

    def test_a_stock_change_without_an_entry_fails(self):
        self.put(STOCK, "class StorageService { void hook() {} }\n")
        self.commit()
        rc, out, err = self.delta()
        self.assertEqual(rc, 1)
        self.assertIn("touches 1 stock file(s), %s, and adds or updates no entry" % STOCK, err)
        self.assertIn("No delta entry: <reason>", err)
        self.assertIn("delta 1 stock files 0 entries failed", out)

    def test_a_deleted_stock_file_is_a_stock_change(self):
        os.remove(os.path.join(self.repo, STOCK))
        self.commit()
        rc, _, err = self.delta()
        self.assertEqual(rc, 1)
        self.assertIn(STOCK, err)

    def test_a_change_to_our_own_files_needs_no_entry(self):
        self.put(OURS, "class DiskCheck { void check() {} }\n")
        self.put(".github/workflows/chronitondb-new.yml", "name: new\n")
        self.put("tools/chronitondb/new.sh", "true\n")
        self.put("docs/design/VER-release-version/notes.md", "# Notes\n")
        self.put(".github/CODEOWNERS", "* @owner\n")
        self.commit()
        rc, out, err = self.delta()
        self.assertEqual((rc, err), (0, ""))
        self.assertIn("delta 0 stock files 0 entries passed", out)

    def test_an_apache_workflow_is_a_stock_file(self):
        self.put(".github/workflows/code-check.yaml", "name: Code Check\n")
        self.commit()
        rc, _, err = self.delta()
        self.assertEqual(rc, 1)
        self.assertIn(".github/workflows/code-check.yaml", err)

    def test_the_waiver_line_with_a_reason_passes(self):
        self.put(STOCK, "class StorageService { void hook() {} }\n")
        self.commit()
        rc, out, err = self.delta(body="## What and why\n\nNo delta entry: the line restores Apache's own text.\n")
        self.assertEqual((rc, err), (0, ""))
        self.assertIn("no delta entry, as the pull request says: the line restores Apache's own text.", out)

    def test_the_waiver_line_passes_a_switch_check_round_stock_log_lines(self):
        # A feature that changes what Apache Cassandra logs works behind a
        # switch, so its change holds the switch check round the stock log
        # lines. The check reads only the line, not the change, so the switch
        # check passes as the log lines do.
        self.git("checkout", "-q", "line")
        self.put(STOCK, "class StorageService {\n    void drain() {\n        logger.info(\"Draining {}\", keyspace);\n    }\n}\n")
        self.commit()
        self.git("checkout", "-q", "change")
        self.git("reset", "-q", "--hard", "line")
        self.put(STOCK, "class StorageService {\n    void drain() {\n        if (Switches.REDACT_LOGS.get())\n"
                        "            logger.info(\"Draining a keyspace\");\n        else\n"
                        "            logger.info(\"Draining {}\", keyspace);\n    }\n}\n")
        self.commit()
        self.assertEqual(self.delta()[0], 1)
        rc, out, err = self.delta(body="No delta entry: the redaction feature changes only stock log lines behind its switch.\n")
        self.assertEqual((rc, err), (0, ""))
        self.assertIn("no delta entry, as the pull request says: the redaction feature changes only stock log lines behind its switch.", out)

    def test_the_waiver_line_without_a_reason_fails(self):
        self.put(STOCK, "class StorageService { void hook() {} }\n")
        self.commit()
        rc, _, err = self.delta(body="No delta entry: none\n")
        self.assertEqual(rc, 1)
        self.assertIn("gives no reason", err)

    def test_an_import_of_a_whole_apache_release_needs_no_entry(self):
        self.put(STOCK, "class StorageService { void apacheFix() {} }\n")
        self.commit()
        for branch in ("import/cassandra-5.0.8/chronitondb-5.0", "import/cassandra-6.0-1a2b3c4d5e/chronitondb-6.0"):
            rc, out, err = self.delta(branch=branch)
            self.assertEqual((rc, err), (0, ""))
            self.assertIn("brings Apache Cassandra's own code", out)

    def test_a_single_fix_or_fork_import_needs_its_entry(self):
        self.put(STOCK, "class StorageService { void apacheFix() {} }\n")
        self.commit()
        for branch in ("import/CASSANDRA-21319/chronitondb-5.0", "import/rustyrazorblade-cassandra-579e35ae6c12/chronitondb-5.0"):
            rc, _, err = self.delta(branch=branch)
            self.assertEqual(rc, 1)
            self.assertIn("adds or updates no entry", err)

    # A wrong Origin.

    def test_an_origin_of_no_allowed_kind_fails(self):
        rc, _, err = self.stock_change_with("x.md", entry(origin="Upstream."), row("x.md"))
        self.assertEqual(rc, 1)
        self.assertIn("Origin is ChronitonDB, Apache commit <hash>", err)

    def test_an_apache_origin_without_its_link_fails(self):
        rc, _, err = self.stock_change_with("x.md", entry(origin="Apache commit `3f1593064c`, taken whole."), row("x.md"))
        self.assertEqual(rc, 1)
        self.assertIn("an Apache Origin links its commit", err)

    def test_a_fork_origin_without_a_commit_link_fails(self):
        origin = "Another fork, rustyrazorblade/cassandra, [its branch](https://github.com/rustyrazorblade/cassandra/tree/main)."
        rc, _, err = self.stock_change_with("x.md", entry(origin=origin), row("x.md"))
        self.assertEqual(rc, 1)
        self.assertIn("a fork Origin links the fork's commit", err)

    def test_a_fork_origin_linking_an_apache_commit_fails(self):
        origin = "Another fork, [`3f1593064c`](https://github.com/apache/cassandra/commit/%s)." % APACHE_HASH
        rc, _, err = self.stock_change_with("x.md", entry(origin=origin), row("x.md"))
        self.assertEqual(rc, 1)
        self.assertIn("a fork Origin links an Apache commit", err)

    def test_a_fork_origin_linking_our_own_organisation_fails(self):
        origin = "Another fork, [`579e35ae6c12`](https://github.com/chronitonlabs/chronitondb-upstream/commit/%s)." % FORK_HASH
        rc, _, err = self.stock_change_with("x.md", entry(origin=origin), row("x.md"))
        self.assertEqual(rc, 1)
        self.assertIn("links a chronitonlabs repository", err)

    def test_a_shown_hash_that_is_not_the_linked_one_fails(self):
        origin = "Apache commit [`deadbeef12`](https://github.com/apache/cassandra/commit/%s), taken whole." % APACHE_HASH
        rc, _, err = self.stock_change_with("x.md", entry(origin=origin), row("x.md"))
        self.assertEqual(rc, 1)
        self.assertIn("Origin shows the commit `deadbeef12`", err)

    # The index row.

    def test_a_missing_index_row_fails(self):
        rc, _, err = self.stock_change_with("storage-hook.md", entry(), row("other.md"))
        self.assertEqual(rc, 1)
        self.assertIn("the register's Index has 0 rows for storage-hook.md, it has exactly one", err)

    def test_an_index_row_with_another_area_fails(self):
        rc, _, err = self.stock_change_with("storage-hook.md", entry(), row("storage-hook.md", area="Build"))
        self.assertEqual(rc, 1)
        self.assertIn("the Area section opens with 'Storage', the register's Index row for storage-hook.md says Area 'Build'", err)

    def test_an_index_row_with_other_lines_fails(self):
        rc, _, err = self.stock_change_with("storage-hook.md", entry(), row("storage-hook.md", lines="5.0"))
        self.assertEqual(rc, 1)
        self.assertIn("the Lines section names 5.0, 6.0, the register's Index row for storage-hook.md says Lines 5.0", err)

    def test_a_last_update_unlike_the_index_row_fails(self):
        rc, _, err = self.stock_change_with("storage-hook.md", entry(updated="2026-11-02"), row("storage-hook.md"))
        self.assertEqual(rc, 1)
        self.assertIn("says Last update 2026-11-01, the entry says 2026-11-02", err)

    # Updates, renames and deletions.

    def merged_entry(self):
        self.put("docs/delta/storage-hook.md", entry())
        self.put("docs/delta/README.md", register(row("storage-hook.md")))
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "entry")
        self.git("branch", "-f", "line")

    def test_an_update_with_a_new_last_update_passes(self):
        self.merged_entry()
        self.put(STOCK, "class StorageService { void hook2() {} }\n")
        self.put("docs/delta/storage-hook.md", entry(updated="2026-11-10").replace("What we carry.", "What we carry now."))
        self.put("docs/delta/README.md", register(row("storage-hook.md", updated="2026-11-10")))
        self.commit("2026-11-10")
        rc, out, err = self.delta()
        self.assertEqual((rc, err), (0, ""))
        self.assertIn("delta 1 stock files 1 entries passed", out)

    def test_an_update_that_keeps_an_old_last_update_fails(self):
        self.merged_entry()
        self.put("docs/delta/storage-hook.md", entry().replace("What we carry.", "What we carry now."))
        self.commit("2026-11-10")
        rc, _, err = self.delta()
        self.assertEqual(rc, 1)
        self.assertIn("its Last-Update stays 2026-11-01, as on the line. Set it to the date of this change, 2026-11-10", err)

    def test_a_second_update_on_the_same_day_passes(self):
        self.merged_entry()
        self.put("docs/delta/storage-hook.md", entry().replace("What we carry.", "What we carry now."))
        self.commit("2026-11-01")
        rc, _, err = self.delta()
        self.assertEqual((rc, err), (0, ""))

    def test_a_renamed_entry_fails(self):
        self.merged_entry()
        self.git("mv", "docs/delta/storage-hook.md", "docs/delta/storage-service-hook.md")
        self.put("docs/delta/README.md", register(row("storage-service-hook.md")))
        self.commit()
        rc, _, err = self.delta()
        self.assertEqual(rc, 1)
        self.assertIn("docs/delta/storage-hook.md: the entry is renamed to docs/delta/storage-service-hook.md", err)

    def test_a_deleted_entry_fails(self):
        self.merged_entry()
        os.remove(os.path.join(self.repo, "docs/delta/storage-hook.md"))
        self.put("docs/delta/README.md", register())
        self.commit()
        rc, _, err = self.delta()
        self.assertEqual(rc, 1)
        self.assertIn("the entry is deleted", err)
        self.assertIn("Status Dropped", err)

    def test_an_entry_in_the_worktree_is_checked(self):
        self.put("docs/delta/storage-hook.md", entry(origin="Upstream."))
        self.put("docs/delta/README.md", register(row("storage-hook.md")))
        rc, _, err = run("delta", "--repo", self.repo, "--base", "line", "--source", "worktree")
        self.assertEqual(rc, 1)
        self.assertIn("Origin is ChronitonDB", err)

    def test_usage(self):
        rc, _, _ = run("delta", "--repo", self.repo)
        self.assertEqual(rc, 2)


class Workflow(unittest.TestCase):
    """The step of the CI workflow that runs the check, run here as the
    shell script it is, with the environment the workflow gives it and a
    stand-in for gh. The author of a pull request from a fork chooses its
    branch name, so the name of an import branch counts only for a branch
    of the repository itself."""

    WORKFLOW = ".github/workflows/chronitondb-delta.yml"
    REPO = "example/product"
    IMPORT = "import/cassandra-5.0.8/chronitondb-5.0"
    # The repository of the Delta tests, without their test methods.
    setUp, tearDown, git, put, commit = Delta.setUp, Delta.tearDown, Delta.git, Delta.put, Delta.commit

    def step(self, head_repo, head_ref, body=""):
        temp = tempfile.mkdtemp()
        try:
            os.makedirs(os.path.join(temp, "doclint"))
            for name in ("doclint.py", "markdown.py"):
                shutil.copy(os.path.join(TOOLS, name), os.path.join(temp, "doclint", name))
            os.makedirs(os.path.join(temp, "bin"))
            gh = os.path.join(temp, "bin", "gh")
            with open(gh, "w", encoding="utf-8") as handle:
                handle.write("#!/bin/sh\nprintf '%s' \"$PR_BODY\"\n")
            os.chmod(gh, 0o755)
            self.git("update-ref", "refs/remotes/origin/line", "line")
            context = {"github.base_ref": "line", "github.head_ref": head_ref, "github.repository": self.REPO,
                       "github.event.pull_request.head.repo.full_name": head_repo,
                       "github.event.pull_request.number": "7", "github.token": "none"}
            env = dict(os.environ, PATH=os.path.join(temp, "bin") + os.pathsep + os.environ.get("PATH", ""),
                       RUNNER_TEMP=temp, PR_BODY=body)
            env.update(step_env(self.WORKFLOW, "Delta register", context))
            done = subprocess.run(["bash", "-e", "-c", step_script(self.WORKFLOW, "Delta register")],
                                  cwd=self.repo, env=env, capture_output=True, text=True, check=False)
            return done.returncode, done.stdout, done.stderr
        finally:
            shutil.rmtree(temp)

    def stock_change(self):
        self.put(STOCK, "class StorageService { void apacheFix() {} }\n")
        self.commit()

    def test_an_import_branch_of_the_repository_needs_no_entry(self):
        self.stock_change()
        rc, out, err = self.step(self.REPO, self.IMPORT)
        self.assertEqual((rc, err), (0, ""))
        self.assertIn("the branch %s imports a whole Apache release" % self.IMPORT, out)

    def test_a_fork_branch_named_as_an_import_needs_its_entry(self):
        self.stock_change()
        for head_repo in ("someone/product", "someone/" + self.REPO.split("/")[1], self.REPO + "-fork", ""):
            rc, out, err = self.step(head_repo, self.IMPORT)
            self.assertEqual(rc, 1, head_repo)
            self.assertIn("adds or updates no entry", err)
            self.assertNotIn("imports a whole Apache release", out)

    def test_a_fork_still_passes_with_its_entry_or_the_waiver_line(self):
        self.stock_change()
        rc, out, err = self.step("someone/product", "a-fix", body="No delta entry: the line restores Apache's own text.\n")
        self.assertEqual((rc, err), (0, ""))
        self.assertIn("no delta entry, as the pull request says", out)

    def test_the_branch_name_reaches_the_checker_only_through_that_test(self):
        text = read(self.WORKFLOW)
        self.assertNotIn("pull_request_target", text)
        self.assertEqual([line.strip() for line in text.split("\n") if "github.head_ref" in line],
                         ["HEAD_REF: ${{ github.head_ref }}"])
        self.assertIn("HEAD_REPO: ${{ github.event.pull_request.head.repo.full_name }}", text)
        self.assertEqual(text.count("$HEAD_REF"), 1)
        script = step_script(self.WORKFLOW, "Delta register")
        self.assertIn('if [ "$HEAD_REPO" = "$REPO" ]\nthen\n  BRANCH="$HEAD_REF"\nfi\n', script)


class OwnPaths(unittest.TestCase):
    """The table Where things live of conventions.md on this branch is the
    rule for ChronitonDB's own files."""

    def setUp(self):
        self.paths = doclint.own_paths(read("docs/process/conventions.md"))

    def test_the_table_gives_directories_patterns_and_files(self):
        for path in ("src/java/org/chronitondb/", "test/unit/org/chronitondb/", "tools/chronitondb/", "docs/",
                     "docs/decisions/", ".github/workflows/chronitondb-*.yml", ".github/README.md",
                     "CHANGES-chronitondb.txt", "packaging/"):
            self.assertIn(path, self.paths)

    def test_our_files_are_our_own(self):
        for path in ("src/java/org/chronitondb/startup/DiskCheck.java", "test/distributed/org/chronitondb/X.java",
                     "docs/delta/README.md", ".github/workflows/chronitondb-delta.yml", ".github/CODEOWNERS",
                     ".editorconfig", "conf/cassandra_chronitondb.yaml", "NEWS-chronitondb.txt"):
            self.assertTrue(doclint.is_own(path, self.paths), path)

    def test_apache_files_are_stock(self):
        for path in ("src/java/org/apache/cassandra/service/StorageService.java", "build.xml", ".build/run-ci",
                     ".github/workflows/code-check.yaml", "conf/cassandra.yaml", "CHANGES.txt", "doc/README.md",
                     "debian/control", "test/unit/org/apache/cassandra/db/CellTest.java"):
            self.assertFalse(doclint.is_own(path, self.paths), path)


class Register(unittest.TestCase):
    """Every entry of the register on this branch passes the entry rules."""

    def test_every_entry_on_this_branch_passes(self):
        names = sorted(name for name in os.listdir(os.path.join(ROOT, "docs", "delta"))
                       if name.endswith(".md") and name != "README.md")
        repo = tempfile.mkdtemp()
        try:
            for path in ["docs/process/templates/delta-entry.md", "docs/delta/README.md"] + ["docs/delta/" + n for n in names]:
                full = os.path.join(repo, path)
                os.makedirs(os.path.dirname(full), exist_ok=True)
                with open(full, "w", encoding="utf-8") as handle:
                    handle.write(read(path))
            subprocess.run(["git", "-C", repo, "init", "-q"], check=True)
            subprocess.run(["git", "-C", repo, "add", "-A"], check=True)
            subprocess.run(["git", "-C", repo, "-c", "user.name=t", "-c", "user.email=t@example.org", "-c", "commit.gpgsign=false",
                            "-c", "core.hooksPath=/dev/null", "commit", "-q", "-m", "register"], check=True)
            rc, out, err = run("document", "--repo", repo, "--templates", "HEAD", "--source", "HEAD",
                               *["docs/delta/" + n for n in names])
            self.assertEqual((rc, err), (0, ""))
            self.assertIn("documents %d checked 0 failed" % len(names), out)
        finally:
            shutil.rmtree(repo)


if __name__ == "__main__":
    unittest.main()
