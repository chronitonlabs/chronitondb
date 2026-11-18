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
"""The stock test check, docs/process/testing.md, Policy 4: a pre-existing
test file of Apache Cassandra changes in four ways only, and the records
that permit a change are read on the line, never from the change. Run from
the repository root:

    python3 -m unittest discover -s tools/chronitondb/test/doclint
"""

import os
import shutil
import subprocess
import sys
import tempfile
import unittest

TOOLS = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import test_delta  # noqa: E402
from test_delta import read, run, step_env, step_script  # noqa: E402

STOCK_TEST = "test/unit/org/apache/cassandra/tools/nodetool/VersionTest.java"
LISTING = "test/resources/nodetool/help/version"
OTHER_TEST = "pylib/cqlshlib/test/test_cqlsh_output.py"
BINARY = "test/data/legacy-sstables/oa/nb-1-big-Data.db"
OWN_TEST = "test/unit/org/chronitondb/startup/DiskCheckTest.java"
FIX_RECORD = "docs/design/142-keep-the-level/fix-record.md"
DESIGN_RECORD = "docs/design/VER-release-version/design-record.md"
DECISION = "docs/decisions/DEC-GOV-0002-version-test-expects-the-release-version.md"
IMPORT = "import/cassandra-5.0.8/chronitondb-5.0"


def record(heading, status="Draft", planned=(), lines=()):
    """A design record or fix record with what the check reads of it."""
    return "\n".join(["# %s" % heading, "",
                      "| Field | Value |", "|---|---|",
                      "| Title | A title |",
                      "| Status | %s |" % status, "",
                      "## 14. Testing", ""] + list(lines) + ["",
                      "## Planned file list", "", "```"] + list(planned) + ["```", ""])


def decision(*lines, status="Accepted"):
    return "\n".join(["# DEC-GOV-0002. The version test expects the release version", "",
                      "| Field | Value |", "|---|---|",
                      "| Document type | Record (ISO/IEC/IEEE 15289), MADR |",
                      "| Status | %s |" % status, "",
                      "## Decision outcome", ""] + list(lines) + [""])


APPROVAL = "Stock test change: %s for #142, because the test compares the first line of the output" % STOCK_TEST


class StockTests(unittest.TestCase):
    """The line holds a stock test class, a stock listing, a stock test of
    another test directory, a binary stock test data file, a test of the
    project's own, the fix record of #142 that plans the stock test class,
    and the design record of #150 that names the listing as pinned."""

    # The repository helpers of the delta tests, without their test methods.
    tearDown, git, put, commit = test_delta.Delta.tearDown, test_delta.Delta.git, test_delta.Delta.put, test_delta.Delta.commit

    def setUp(self):
        self.repo = tempfile.mkdtemp()
        self.git("init", "-q")
        self.put("docs/process/conventions.md", read("docs/process/conventions.md"))
        self.put(STOCK_TEST, "class VersionTest {\n  void testVersion() {}\n}\n")
        self.put(LISTING, "NAME\n  nodetool version\nOPTIONS\n  -v, --verbose\n")
        self.put(OTHER_TEST, "def test_output():\n    pass\n")
        self.put(OWN_TEST, "class DiskCheckTest {}\n")
        with open(os.path.join(self.repo, self.dirs(BINARY)), "wb") as handle:
            handle.write(b"\x00\x01\x02\x00sstable")
        self.put(FIX_RECORD, record("Fix: #142 Keep the level of a moved sstable",
                                    planned=["src/java/org/apache/cassandra/tools/nodetool/Version.java stock", STOCK_TEST + " test"]))
        self.put(DESIGN_RECORD, record("Design: #150 Print the release version", lines=["Pinned listing: " + LISTING],
                                       planned=["src/java/org/chronitondb/tools/ReleaseVersion.java new", LISTING + " test"]))
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "line")
        self.git("branch", "-f", "line")
        self.git("checkout", "-q", "-b", "change")

    def dirs(self, path):
        os.makedirs(os.path.dirname(os.path.join(self.repo, path)), exist_ok=True)
        return path

    def on_the_line(self, path, text):
        """Merges a file into the line, then takes the line into the
        change, as a record merged by its own pull request."""
        self.git("checkout", "-q", "line")
        self.put(path, text)
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "record")
        self.git("checkout", "-q", "change")
        self.git("merge", "-q", "line")

    def check(self, body=None, branch=None, source="HEAD"):
        args = ["stock-tests", "--repo", self.repo, "--base", "line", "--source", source]
        if branch is not None:
            args += ["--branch", branch]
        if body is not None:
            path = os.path.join(self.repo, ".git", "body.txt")
            with open(path, "w", encoding="utf-8") as handle:
                handle.write(body)
            args += ["--body", path]
        return run(*args)

    def change_the_test(self):
        self.put(STOCK_TEST, "class VersionTest {\n  void testVersion() { check() }\n}\n")
        self.commit()

    def extend_the_listing(self):
        self.put(LISTING, "NAME\n  nodetool version\nOPTIONS\n  -v, --verbose\n  --release\n")
        self.commit()

    def refused(self, done, text, path=STOCK_TEST):
        rc, out, err = done
        self.assertEqual(rc, 1, err)
        self.assertIn(path + ": ", err)
        self.assertIn(text, err)
        self.assertIn("changes in four ways only (docs/process/principles.md, PRINCIPLE-013)", err)
        self.assertIn(" checked 1 failed\n", out)

    # What the check reads as a stock test file.

    def test_a_change_to_other_files_passes(self):
        self.put(OWN_TEST, "class DiskCheckTest { void check() {} }\n")
        self.put("tools/chronitondb/test/doclint/test_new.py", "pass\n")
        self.put("src/java/org/apache/cassandra/tools/nodetool/Version.java", "class Version {}\n")
        self.commit()
        self.assertEqual(self.check(), (0, "stock-tests 0 checked 0 failed\n", ""))

    def test_a_new_file_beside_the_stock_tests_is_not_a_pre_existing_one(self):
        self.put("test/unit/org/apache/cassandra/tools/nodetool/VersionReproducerTest.java", "class VersionReproducerTest {}\n")
        self.commit()
        self.assertEqual(self.check(), (0, "stock-tests 0 checked 0 failed\n", ""))

    def test_a_stock_test_of_any_test_directory_counts(self):
        for path in (OTHER_TEST, LISTING, STOCK_TEST):
            self.assertTrue(self.is_stock(path), path)
        for path in (OWN_TEST, "tools/chronitondb/test/doclint/test_delta.py", "test/bdd/steps/common.py",
                     "src/java/org/apache/cassandra/service/StorageService.java", "docs/process/testing.md"):
            self.assertFalse(self.is_stock(path), path)
        self.put(OTHER_TEST, "def test_output():\n    return 1\n")
        self.commit()
        self.refused(self.check("Fixes #142\n"), "no record on line of #142 permits the change", OTHER_TEST)

    def is_stock(self, path):
        import doclint
        return doclint.is_stock_test(path, doclint.own_paths(read("docs/process/conventions.md")))

    def test_the_table_of_the_change_does_not_make_a_file_its_own(self):
        text = read("docs/process/conventions.md").replace("| `tools/chronitondb/` |", "| `tools/chronitondb/`, `test/` |")
        self.assertIn("`test/` |", text)
        self.put("docs/process/conventions.md", text)
        self.change_the_test()
        self.refused(self.check(), "the pull request description names no issue")

    # The first way: an import.

    def test_an_import_passes(self):
        self.change_the_test()
        rc, out, err = self.check(branch=IMPORT)
        self.assertEqual((rc, err), (0, ""))
        self.assertIn("stock-test %s: the branch %s is an import from Apache Cassandra" % (STOCK_TEST, IMPORT), out)
        self.assertIn("stock-tests 1 checked 0 failed\n", out)
        for branch in ("import/CASSANDRA-21319/chronitondb-5.0", "import/cassandra-6.0-1a2b3c4d5e/chronitondb-6.0"):
            self.assertEqual(self.check(branch=branch)[0], 0, branch)

    def test_another_branch_name_is_no_import_from_apache_cassandra(self):
        self.change_the_test()
        for branch in ("", "agent/42-disk-check/chronitondb-5.0", "x/import/cassandra-5.0.8", "imports/cassandra-5.0.8",
                       "import/rustyrazorblade-cassandra-579e35ae6c12/chronitondb-5.0", "import/cassandra-fork-579e35ae6c12/chronitondb-5.0",
                       "import/142-keep-the-level/chronitondb-5.0", "import/CASSANDRA-x/chronitondb-5.0"):
            self.assertEqual(self.check(branch=branch)[0], 1, branch)

    # The second way: the fix record of the issue plans the file as test.

    def test_the_fix_record_of_the_named_issue_permits_the_change(self):
        self.change_the_test()
        for body in ("Fixes #142\n", "What and why.\n\nPart of #142\n", "  Fixes #142.  \nFixes #7\n"):
            rc, out, err = self.check(body)
            self.assertEqual((rc, err), (0, ""), body)
            self.assertEqual(out, "stock-test %s: the fix record %s plans it as test\nstock-tests 1 checked 0 failed\n" % (STOCK_TEST, FIX_RECORD))

    def test_no_issue_named_is_refused(self):
        self.change_the_test()
        for body in (None, "", "This fixes #142 for good.\n", "fixes #142\n", "Fixes 142\n", "Fixes #142 and #150\n"):
            self.refused(self.check(body), "the pull request description names no issue, so no record on line can permit the change")

    def test_another_issue_is_refused(self):
        self.change_the_test()
        self.refused(self.check("Fixes #150\nPart of #1420\n"), "no record on line of #150 or #1420 permits the change")

    def test_a_fix_record_the_change_brings_is_no_permit(self):
        self.put("docs/design/160-print-the-sha/fix-record.md", record("Fix: #160 Print the SHA", planned=[STOCK_TEST + " test"]))
        self.put(FIX_RECORD, record("Fix: #142 Keep the level of a moved sstable", planned=[OTHER_TEST + " test"]))
        self.put(OTHER_TEST, "def test_output():\n    return 1\n")
        self.change_the_test()
        rc, out, err = self.check("Fixes #160\nFixes #142\n")
        self.assertEqual(rc, 1)
        self.assertIn(OTHER_TEST + ": the file is a pre-existing test file", err)
        self.assertNotIn(STOCK_TEST + ": ", err)
        self.assertIn("stock-tests 2 checked 1 failed\n", out)
        rc, out, err = self.check("Fixes #160\n")
        self.assertEqual((rc, out), (1, "stock-tests 2 checked 2 failed\n"))
        self.assertIn(STOCK_TEST + ": the file is a pre-existing test file of Apache Cassandra and no record on line of #160 permits the change", err)

    def test_a_file_planned_under_another_word_is_refused(self):
        self.on_the_line(FIX_RECORD, record("Fix: #142 Keep the level of a moved sstable", planned=[STOCK_TEST + " stock"]))
        self.change_the_test()
        self.refused(self.check("Fixes #142\n"), "no record on line of #142 permits the change")

    def test_a_planned_file_outside_the_list_is_refused(self):
        self.on_the_line(FIX_RECORD, record("Fix: #142 Keep the level of a moved sstable", lines=["```", STOCK_TEST + " test", "```"]))
        self.change_the_test()
        self.refused(self.check("Fixes #142\n"), "no record on line of #142 permits the change")

    def test_a_design_record_that_plans_the_file_is_refused(self):
        self.on_the_line(DESIGN_RECORD, record("Design: #150 Print the release version", planned=[STOCK_TEST + " test"]))
        self.change_the_test()
        self.refused(self.check("Fixes #150\n"), "no record on line of #150 permits the change")

    def test_a_superseded_record_permits_nothing(self):
        self.on_the_line(FIX_RECORD, record("Fix: #142 Keep the level of a moved sstable", status="Superseded",
                                            planned=[STOCK_TEST + " test"]))
        self.change_the_test()
        self.refused(self.check("Fixes #142\n"), "no record on line of #142 permits the change")

    # The third way: lines added to a pinned listing.

    def test_lines_added_to_a_pinned_listing_pass(self):
        self.extend_the_listing()
        rc, out, err = self.check("Fixes #150\n")
        self.assertEqual((rc, err), (0, ""))
        self.assertIn("stock-test %s: %s names it as a pinned listing and the change only adds lines\n" % (LISTING, DESIGN_RECORD), out)

    def test_a_pinned_listing_with_a_line_altered_or_removed_is_refused(self):
        for text in ("NAME\n  nodetool version\nOPTIONS\n  -v, --verbose, --release\n", "NAME\n  nodetool version\nOPTIONS\n"):
            self.put(LISTING, text)
            self.commit()
            self.refused(self.check("Fixes #150\n"), "names the file as a pinned listing, and the change removes or alters 1 line(s) of it", LISTING)

    def test_a_pinned_listing_of_another_issue_or_file_is_refused(self):
        self.extend_the_listing()
        self.refused(self.check("Fixes #142\n"), "no record on line of #142 permits the change", LISTING)
        self.change_the_test()
        rc, _, err = self.check("Fixes #150\n")
        self.assertEqual(rc, 1)
        self.assertIn(STOCK_TEST + ": the file is a pre-existing test file", err)
        self.assertNotIn(LISTING + ": ", err)

    def test_a_pinned_listing_line_in_a_fix_record_counts(self):
        self.on_the_line(FIX_RECORD, record("Fix: #142 Keep the level of a moved sstable", lines=["Pinned listing: " + LISTING]))
        self.extend_the_listing()
        self.assertEqual(self.check("Fixes #142\n")[0], 0)

    def test_a_pinned_listing_line_in_another_form_is_refused(self):
        self.extend_the_listing()
        for line in ("Pinned listing: `%s`" % LISTING, "Pinned listing: {the file's path from the repository root}",
                     "The pinned listing: " + LISTING, "```\nPinned listing: %s\n```" % LISTING, "<!-- Pinned listing: %s -->" % LISTING,
                     "<!--\nPinned listing: %s\n-->" % LISTING):
            self.on_the_line(DESIGN_RECORD, record("Design: #150 Print the release version", lines=line.split("\n")))
            self.refused(self.check("Fixes #150\n"), "no record on line of #150 permits the change", LISTING)
        self.on_the_line(DESIGN_RECORD, record("Design: #150 Print the release version", lines=["  Pinned listing: %s  " % LISTING]))
        self.assertEqual(self.check("Fixes #150\n")[0], 0)

    # The fourth way: an accepted decision record.

    def test_an_accepted_decision_record_permits_the_change(self):
        self.on_the_line(DECISION, decision(APPROVAL))
        self.on_the_line(FIX_RECORD, record("Fix: #142 Keep the level of a moved sstable"))
        self.change_the_test()
        rc, out, err = self.check("Part of #142\n")
        self.assertEqual((rc, err), (0, ""))
        self.assertIn("stock-test %s: the decision record %s approves the change\n" % (STOCK_TEST, DECISION), out)

    def test_a_decision_record_of_a_feature_counts(self):
        self.on_the_line("docs/design/VER-release-version/decisions/DEC-VER-0001-version-test.md",
                         decision(APPROVAL.replace("#142", "#150")))
        self.change_the_test()
        self.assertEqual(self.check("Fixes #150\n")[0], 0)

    def test_a_decision_record_that_does_not_approve_this_change_is_refused(self):
        self.on_the_line(FIX_RECORD, record("Fix: #142 Keep the level of a moved sstable"))
        self.change_the_test()
        for text in (decision(APPROVAL, status="Proposed"),
                     decision(APPROVAL, status="Superseded by DEC-GOV-0003"),
                     decision(APPROVAL.replace("#142", "#143")),
                     decision(APPROVAL.replace(STOCK_TEST, OTHER_TEST)),
                     decision("Stock test change: %s for #142, because it must" % STOCK_TEST),
                     decision("Stock test change: %s for #142" % STOCK_TEST),
                     decision("```", APPROVAL, "```"),
                     decision("<!--", APPROVAL, "-->"),
                     decision("The test `%s` changes for #142." % STOCK_TEST)):
            self.on_the_line(DECISION, text)
            self.refused(self.check("Fixes #142\n"), "no record on line of #142 permits the change")
        self.on_the_line(DECISION, decision(APPROVAL))
        self.assertEqual(self.check("Fixes #142\n")[0], 0)

    def test_a_decision_record_the_change_brings_is_no_permit(self):
        self.put(DECISION, decision(APPROVAL))
        self.change_the_test()
        self.refused(self.check("Fixes #142\n".replace("142", "143")), "no record on line of #143 permits the change")
        self.on_the_line(FIX_RECORD, record("Fix: #142 Keep the level of a moved sstable"))
        self.refused(self.check("Fixes #142\n"), "no record on line of #142 permits the change")

    # Changes only an import makes.

    def test_a_deleted_renamed_linked_or_binary_file_is_refused_with_a_permit(self):
        self.on_the_line(DECISION, decision(APPROVAL, APPROVAL.replace(STOCK_TEST, BINARY)))
        self.git("rm", "-q", STOCK_TEST)
        self.commit()
        self.refused(self.check("Fixes #142\n"), "the file is deleted. A pre-existing test file of Apache Cassandra is deleted, renamed")
        self.git("reset", "-q", "--hard", "HEAD~1")
        self.git("mv", STOCK_TEST, STOCK_TEST.replace("VersionTest", "ReleaseVersionTest"))
        self.commit()
        self.refused(self.check("Fixes #142\n"), "the file is renamed to " + STOCK_TEST.replace("VersionTest", "ReleaseVersionTest"))
        self.git("reset", "-q", "--hard", "HEAD~1")
        os.remove(os.path.join(self.repo, STOCK_TEST))
        os.symlink("../../../../../../../../" + OWN_TEST, os.path.join(self.repo, STOCK_TEST))
        self.commit()
        self.refused(self.check("Fixes #142\n"), "the file is or becomes a symbolic link or another type of file")
        self.git("reset", "-q", "--hard", "HEAD~1")
        with open(os.path.join(self.repo, BINARY), "wb") as handle:
            handle.write(b"\x00\x01\x02\x00another sstable")
        self.commit()
        self.refused(self.check("Fixes #142\n"), "the file is a binary file", BINARY)

    def test_an_import_deletes_renames_and_changes_binary_files(self):
        self.git("rm", "-q", STOCK_TEST)
        self.git("mv", OTHER_TEST, OTHER_TEST.replace("test_cqlsh_output", "test_output"))
        with open(os.path.join(self.repo, BINARY), "wb") as handle:
            handle.write(b"\x00\x01\x02\x00another sstable")
        self.commit()
        rc, out, err = self.check(branch=IMPORT)
        self.assertEqual((rc, err), (0, ""))
        self.assertIn("stock-tests 3 checked 0 failed\n", out)
        self.assertEqual(self.check("Fixes #142\n")[0], 1)

    # The sources and the command.

    def test_the_index_and_the_worktree_are_checked(self):
        self.put(STOCK_TEST, "class VersionTest {\n  void testVersion() { check() }\n}\n")
        self.assertEqual(self.check(source="index")[0], 0)
        self.refused(self.check(source="worktree"), "the pull request description names no issue")
        self.git("add", "-A")
        self.refused(self.check(source="index"), "the pull request description names no issue")
        self.assertEqual(self.check("Fixes #142\n", source="index")[0], 0)

    def test_a_line_without_the_table_fails(self):
        self.on_the_line("docs/process/conventions.md", "# Conventions\n")
        self.change_the_test()
        rc, _, err = self.check("Fixes #142\n")
        self.assertEqual(rc, 1)
        self.assertIn("has no Where things live table", err)

    def test_no_merge_base_fails(self):
        self.git("checkout", "-q", "--orphan", "other")
        self.git("commit", "-q", "--allow-empty", "-m", "other")
        rc, _, err = self.check()
        self.assertEqual(rc, 1)
        self.assertIn("no merge base of line and HEAD", err)

    def test_usage(self):
        self.assertEqual(run("stock-tests", "--repo", self.repo)[0], 2)
        self.assertEqual(run("stock-tests", "--repo", self.repo, "--base", "line", "--body", os.path.join(self.repo, "none"))[0], 2)


class Workflow(unittest.TestCase):
    """The step of the CI workflow that runs the check, run here as the
    shell script it is, with the environment the workflow gives it and a
    stand-in for gh."""

    WORKFLOW = ".github/workflows/chronitondb-stock-tests.yml"
    REPO = "example/product"
    setUp, tearDown, git, put, commit = StockTests.setUp, StockTests.tearDown, StockTests.git, StockTests.put, StockTests.commit
    dirs, change_the_test = StockTests.dirs, StockTests.change_the_test

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
            env.update(step_env(self.WORKFLOW, "Stock test files", context))
            done = subprocess.run(["bash", "-e", "-c", step_script(self.WORKFLOW, "Stock test files")],
                                  cwd=self.repo, env=env, capture_output=True, text=True, check=False)
            return done.returncode, done.stdout, done.stderr
        finally:
            shutil.rmtree(temp)

    def test_the_description_names_the_issue(self):
        self.change_the_test()
        rc, out, err = self.step("someone/product", "a-fix", body="What and why.\n\nFixes #142\n")
        self.assertEqual((rc, err), (0, ""))
        self.assertIn("the fix record %s plans it as test" % FIX_RECORD, out)
        rc, out, err = self.step(self.REPO, "agent/142-keep-the-level/chronitondb-5.0", body="What and why.\n")
        self.assertEqual(rc, 1)
        self.assertIn("names no issue", err)

    def test_an_import_branch_of_the_repository_passes(self):
        self.change_the_test()
        rc, out, err = self.step(self.REPO, IMPORT)
        self.assertEqual((rc, err), (0, ""))
        self.assertIn("the branch %s is an import from Apache Cassandra" % IMPORT, out)

    def test_a_fork_branch_named_as_an_import_is_refused(self):
        self.change_the_test()
        for head_repo in ("someone/product", "someone/" + self.REPO.split("/")[1], self.REPO + "-fork", ""):
            rc, out, err = self.step(head_repo, IMPORT)
            self.assertEqual(rc, 1, head_repo)
            self.assertIn("names no issue", err)
            self.assertNotIn("is an import", out)

    def test_the_checker_and_the_permits_come_from_the_base_branch(self):
        text = read(self.WORKFLOW)
        self.assertIn('git show "origin/$BASE:tools/chronitondb/$file" > "$dir/$file"', text)
        script = step_script(self.WORKFLOW, "Stock test files")
        self.assertIn('if [ "$HEAD_REPO" = "$REPO" ]\nthen\n  BRANCH="$HEAD_REF"\nfi\n', script)
        self.assertIn('python3 "$RUNNER_TEMP/doclint/doclint.py" stock-tests --repo . --base "origin/$BASE" --source HEAD', script)
        self.assertEqual(text.count("$HEAD_REF"), 1)
        self.assertNotIn("tools/chronitondb/doclint.py stock-tests", text)


if __name__ == "__main__":
    unittest.main()
