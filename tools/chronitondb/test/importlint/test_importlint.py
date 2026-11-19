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
"""The import history check, docs/process/upstream.md: an import branch
brings Apache Cassandra's own history, or one commit taken unchanged, and
nothing else of Apache Cassandra's files. Each test builds a stand-in for
the public repositories in a directory and an import branch in a clone.
Run from the repository root:

    python3 -m unittest discover -s tools/chronitondb/test/importlint
"""

import contextlib
import io
import json
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
import importlint  # noqa: E402

STOCK = "src/java/org/apache/cassandra/service/StorageService.java"
STOCK_TEST = "test/unit/org/apache/cassandra/service/StorageServiceTest.java"
RECORD = "docs/imports/5.0.8.md"
RELEASE = "import/cassandra-5.0.8/chronitondb-5.0"
FIX = "import/CASSANDRA-100/chronitondb-5.0"
FIX_MESSAGE = "Keep the level of a moved sstable\n\npatch by A Committer for CASSANDRA-100"
WORKFLOW = ".github/workflows/chronitondb-import.yml"


def read(path):
    with open(os.path.join(ROOT, path), encoding="utf-8") as handle:
        return handle.read()


# The maintainers of the public record on this branch.
MAINTAINERS = re.findall(r"\| `([A-Za-z0-9-]+)` \|", read("docs/governance/committers.md").split("## Committers")[0])
MAINTAINER = MAINTAINERS[0]


def run(*args):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = importlint.main(list(args))
    return rc, out.getvalue(), err.getvalue()


def step_env(workflow, name, context):
    """The environment the step NAME of a workflow file sets, each value
    "${{ <name> }}" read from context."""
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
    """The shell script of the step NAME of a workflow file."""
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


class Fixture(unittest.TestCase):
    """A directory that stands for the site of the public repositories,
    with apache/cassandra.git in it, and a clone that stands for this
    repository. Apache has the tags cassandra-5.0.7 and cassandra-5.0.8,
    the branch cassandra-5.0 one commit after the second tag, and trunk.
    The line was cut at cassandra-5.0.7 and holds the project's own files
    and one change to a stock file."""

    def setUp(self):
        self.site = tempfile.mkdtemp()
        self.apache = os.path.join(self.site, "apache", "cassandra.git")
        os.makedirs(self.apache)
        self.repo = self.apache
        self.git("init", "-q", "-b", "cassandra-5.0")
        self.put(STOCK, "class StorageService {\n  void start() {}\n\n\n\n  void stop() {}\n}\n")
        self.put(STOCK_TEST, "class StorageServiceTest {}\n")
        self.put("CHANGES.txt", "5.0.7\n * Start\n")
        self.commit("Start")
        self.git("tag", "cassandra-5.0.7")
        self.put(STOCK, "class StorageService {\n  void start() {}\n\n\n\n  void stop() { level() }\n}\n")
        self.put(STOCK_TEST, "class StorageServiceTest { void level() {} }\n")
        self.put("CHANGES.txt", "5.0.8\n * Keep the level of a moved sstable (CASSANDRA-100)\n5.0.7\n * Start\n")
        self.fix = self.commit(FIX_MESSAGE, author="A Committer <a@apache.example>")
        self.put("NEWS.txt", "5.0.8\n")
        self.release = self.commit("Prepare for 5.0.8")
        self.git("tag", "-a", "-m", "5.0.8", "cassandra-5.0.8")
        self.put("NEWS.txt", "5.0.8\n5.0.9\n")
        self.after = self.commit("Next for CASSANDRA-101")
        self.git("branch", "trunk")

        self.repo = os.path.join(self.site, "clone")
        subprocess.run(["git", "clone", "-q", self.apache, self.repo], check=True, capture_output=True)
        self.git("checkout", "-q", "-b", "line", "cassandra-5.0.7")
        self.put("docs/process/conventions.md", read("docs/process/conventions.md"))
        self.put("docs/governance/committers.md", read("docs/governance/committers.md"))
        self.put(STOCK, "class StorageService {\n  void start() { hook() }\n\n\n\n  void stop() {}\n}\n")
        self.commit("feat(startup): call the disk check")
        self.git("update-ref", "refs/remotes/origin/line", "line")

    def tearDown(self):
        shutil.rmtree(self.site)

    def git(self, *args, **env):
        return subprocess.run(["git", "-C", self.repo, "-c", "user.name=t", "-c", "user.email=t@example.org",
                               "-c", "commit.gpgsign=false", "-c", "tag.gpgsign=false", "-c", "core.hooksPath=/dev/null"] + list(args),
                              check=True, capture_output=True, text=True, env=dict(os.environ, **env)).stdout.strip()

    def put(self, path, text):
        full = os.path.join(self.repo, path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8") as handle:
            handle.write(text)

    def commit(self, message, author=None):
        self.git("add", "-A")
        self.git(*(["commit", "-q", "--allow-empty", "-m", message] + (["--author", author] if author else [])))
        return self.git("rev-parse", "HEAD")

    def branch(self, name):
        self.git("checkout", "-q", "-b", name, "line")

    def merge(self, what, message="import(apache-5.0.8): merge Apache Cassandra 5.0.8"):
        self.git("merge", "-q", "--no-ff", "-m", message, what)
        return self.git("rev-parse", "HEAD")

    def check(self, branch, body=None, reviews=None, head="HEAD"):
        args = ["history", "--repo", self.repo, "--base", "origin/line", "--head", head, "--branch", branch, "--github", self.site + os.sep]
        for option, text in (("--body", body), ("--reviews", None if reviews is None else json.dumps(reviews))):
            if text is not None:
                path = os.path.join(self.repo, ".git", option.strip("-") + ".txt")
                with open(path, "w", encoding="utf-8") as handle:
                    handle.write(text)
                args += [option, path]
        return run(*args)

    def passes(self, done, note=None):
        rc, out, err = done
        self.assertEqual((rc, err), (0, ""))
        self.assertTrue(out.endswith("import-history passed\n"), out)
        if note:
            self.assertIn(note, out)

    def refused(self, done, text):
        rc, out, err = done
        self.assertEqual(rc, 1, out)
        self.assertIn(text, err)
        self.assertTrue(out.endswith("import-history failed\n"), out)

    def review(self, state="APPROVED", login=MAINTAINER, at=None):
        return {"user": {"login": login}, "state": state, "commit_id": at or self.git("rev-parse", "HEAD")}


class Release(Fixture):
    """import/cassandra-<x.y.z>/<line>: one merge of Apache's tag."""

    def test_the_merge_of_the_tag_passes(self):
        self.branch(RELEASE)
        merge = self.merge("cassandra-5.0.8")
        self.passes(self.check(RELEASE), "%s merges the commit %s of Apache Cassandra's tag cassandra-5.0.8\n" % (merge[:10], self.release))

    def test_the_projects_own_files_may_come_with_it(self):
        self.branch(RELEASE)
        self.put("docs/delta/README.md", "# The delta register\n")
        self.commit("docs(delta): drop an entry Apache Cassandra fixed")
        self.merge("cassandra-5.0.8")
        self.put(RECORD, "# Import: Apache Cassandra 5.0.8\n")
        self.commit("docs(imports): add the import record")
        self.passes(self.check(RELEASE))

    def test_a_commit_that_changes_a_stock_file_is_refused(self):
        self.branch(RELEASE)
        self.merge("cassandra-5.0.8")
        self.put(STOCK_TEST, "class StorageServiceTest { void level() { skip() } }\n")
        self.put(RECORD, "# Import: Apache Cassandra 5.0.8\n")
        bad = self.commit("docs(imports): add the import record")
        self.refused(self.check(RELEASE), "%s docs(imports): add the import record: the commit changes 1 file(s) of Apache Cassandra, %s. "
                                          "An import brings Apache Cassandra's history through its merge commit" % (bad[:10], STOCK_TEST))

    def test_many_such_commits_are_counted(self):
        self.branch(RELEASE)
        self.merge("cassandra-5.0.8")
        for number in range(12):
            self.put(STOCK_TEST, "class StorageServiceTest { void level%d() {} }\n" % number)
            self.commit("test(service): change %d" % number)
        rc, _, err = self.check(RELEASE)
        self.assertEqual(rc, 1)
        self.assertEqual(err.count("the commit changes 1 file(s) of Apache Cassandra"), 10)
        self.assertIn("\n2 more such commits\n", err)

    def test_a_stock_change_before_the_merge_is_refused(self):
        self.branch(RELEASE)
        self.put(STOCK_TEST, "class StorageServiceTest { void skipped() {} }\n")
        self.commit("test(service): skip a test")
        self.git("merge", "-q", "--no-ff", "-X", "theirs", "-m", "import(apache-5.0.8): merge Apache Cassandra 5.0.8", "cassandra-5.0.8")
        self.refused(self.check(RELEASE), "the commit changes 1 file(s) of Apache Cassandra")

    def test_another_commit_than_the_tag_is_refused(self):
        for what in (self.fix, self.after):
            self.git("checkout", "-q", "line")
            self.git("branch", "-D", RELEASE, "-q") if self.git("branch", "--list", RELEASE) else None
            self.branch(RELEASE)
            self.merge(what)
            self.refused(self.check(RELEASE), "the merge brings the commit %s, and Apache Cassandra's tag cassandra-5.0.8 is the commit %s"
                         % (what, self.release))

    def test_a_tag_of_the_clone_is_no_proof(self):
        self.git("checkout", "-q", "-b", "forged", "cassandra-5.0.8")
        self.put(STOCK_TEST, "class StorageServiceTest {}\n")
        forged = self.commit("Prepare for 5.0.9")
        self.git("tag", "cassandra-5.0.9")
        self.git("tag", "-f", "cassandra-5.0.8")
        self.git("update-ref", "refs/import-check/apache/tags/cassandra-5.0.9", forged)
        self.git("update-ref", "refs/import-check/apache/tags/cassandra-5.0.8", forged)
        self.branch("import/cassandra-5.0.9/chronitondb-5.0")
        self.merge(forged)
        self.refused(self.check("import/cassandra-5.0.9/chronitondb-5.0"), "Apache Cassandra has no tag cassandra-5.0.9 at ")
        self.refused(self.check(RELEASE), "the merge brings the commit %s, and Apache Cassandra's tag cassandra-5.0.8 is the commit %s"
                     % (forged, self.release))

    def test_a_commit_on_top_of_the_tag_is_refused(self):
        self.git("checkout", "-q", "-b", "side", "cassandra-5.0.8")
        self.put(STOCK_TEST, "class StorageServiceTest {}\n")
        side = self.commit("Weaken a test")
        self.branch(RELEASE)
        self.merge(side)
        self.refused(self.check(RELEASE), "the merge brings the commit %s, and Apache Cassandra's tag" % side)

    def test_a_branch_without_the_merge_is_refused(self):
        self.branch(RELEASE)
        self.git("cherry-pick", self.fix, "-X", "theirs")
        self.refused(self.check(RELEASE), "the branch has 0 merge commits that bring history from outside the line, "
                                          "and an import of Apache Cassandra's tag cassandra-5.0.8 has one")
        self.git("checkout", "-q", "-B", RELEASE, "cassandra-5.0.8")
        self.refused(self.check(RELEASE), "the branch has 0 merge commits that bring history from outside the line")

    def test_a_second_merge_is_refused(self):
        self.git("checkout", "-q", "-b", "side", "line")
        self.put(STOCK_TEST, "class StorageServiceTest { void other() {} }\n")
        self.commit("test(service): another change")
        self.branch(RELEASE)
        self.merge("cassandra-5.0.8")
        self.git("merge", "-q", "--no-ff", "-X", "ours", "-m", "Merge side", "side")
        self.refused(self.check(RELEASE), "the branch has 2 merge commits that bring history from outside the line")

    def test_a_merge_of_three_parents_is_refused(self):
        self.git("checkout", "-q", "-b", "side", "line")
        self.put("docs/reference/page.md", "# Page\n")
        self.commit("docs(reference): add a page")
        self.branch(RELEASE)
        self.git("merge", "-q", "--no-ff", "-m", "import(apache-5.0.8): merge Apache Cassandra 5.0.8", "cassandra-5.0.8", "side")
        self.refused(self.check(RELEASE), "the merge has 3 parents")

    def test_the_line_merged_into_the_branch_passes(self):
        self.branch(RELEASE)
        self.merge("cassandra-5.0.8")
        self.git("checkout", "-q", "line")
        self.put("docs/reference/page.md", "# Page\n")
        self.commit("docs(reference): add a page")
        self.git("update-ref", "refs/remotes/origin/line", "line")
        self.git("checkout", "-q", RELEASE)
        self.git("merge", "-q", "--no-ff", "-m", "Merge branch 'line' into the import", "line")
        self.passes(self.check(RELEASE))

    def test_a_change_hidden_in_a_merge_of_the_line_is_refused(self):
        self.branch(RELEASE)
        self.merge("cassandra-5.0.8")
        self.git("checkout", "-q", "line")
        self.put("docs/reference/page.md", "# Page\n")
        self.commit("docs(reference): add a page")
        self.git("update-ref", "refs/remotes/origin/line", "line")
        self.git("checkout", "-q", RELEASE)
        self.git("merge", "-q", "--no-ff", "--no-commit", "line")
        self.put(STOCK_TEST, "class StorageServiceTest {}\n")
        self.commit("Merge branch 'line' into the import")
        rc, out, err = self.check(RELEASE)
        self.assertEqual(rc, 1)
        self.assertIn("RESOLVED %s\n" % STOCK_TEST, out)
        self.assertIn("the merge commit is not the merge git makes of its two parents, in 1 file(s)", err)

    def test_the_rules_come_from_the_line(self):
        self.branch(RELEASE)
        self.merge("cassandra-5.0.8")
        text = read("docs/process/conventions.md").replace("| `tools/chronitondb/` |", "| `tools/chronitondb/`, `test/` |")
        self.assertIn("`test/` |", text)
        self.put("docs/process/conventions.md", text)
        self.put(STOCK_TEST, "class StorageServiceTest {}\n")
        self.commit("docs(process): call the tests our own")
        self.refused(self.check(RELEASE), "the commit changes 1 file(s) of Apache Cassandra, " + STOCK_TEST)


class ByHand(Fixture):
    """A merge commit that is not the merge git makes of its parents: a
    conflict resolved by hand, as far as the check can tell."""

    def by_hand(self):
        self.branch(RELEASE)
        self.git("merge", "-q", "--no-ff", "--no-commit", "cassandra-5.0.8")
        self.put(STOCK, "class StorageService {\n  void start() { hook() }\n\n\n\n  void stop() { level() again() }\n}\n")
        return self.commit("import(apache-5.0.8): merge Apache Cassandra 5.0.8")

    def test_a_merge_changed_by_hand_is_reported_and_refused(self):
        merge = self.by_hand()
        rc, out, err = self.check(RELEASE)
        self.assertEqual(rc, 1)
        self.assertEqual(out, "RESOLVED %s\nimport-history failed\n" % STOCK)
        self.assertIn("%s import(apache-5.0.8): merge Apache Cassandra 5.0.8: the merge commit is not the merge git makes of its two parents, "
                      "in 1 file(s), listed above on the RESOLVED lines" % merge[:10], err)
        self.assertIn("A maintainer approves with an approving review of this pull request", err)

    def test_a_real_conflict_resolved_by_hand_is_reported_and_refused(self):
        self.git("checkout", "-q", "line")
        self.put(STOCK, "class StorageService {\n  void start() { hook() }\n\n\n\n  void stop() { ours() }\n}\n")
        self.commit("fix(service): stop our own way")
        self.git("update-ref", "refs/remotes/origin/line", "line")
        self.branch(RELEASE)
        with self.assertRaises(subprocess.CalledProcessError):
            self.git("merge", "-q", "--no-ff", "-m", "import", "cassandra-5.0.8")
        self.put(STOCK, "class StorageService {\n  void start() { hook() }\n\n\n\n  void stop() { ours() level() }\n}\n")
        self.commit("import(apache-5.0.8): merge Apache Cassandra 5.0.8")
        rc, out, err = self.check(RELEASE)
        self.assertEqual(rc, 1)
        self.assertIn("RESOLVED %s\n" % STOCK, out)
        self.assertIn("the merge commit is not the merge git makes of its two parents", err)
        self.passes(self.check(RELEASE, reviews=[self.review()]), "and a maintainer approved it")

    def test_a_maintainers_approving_review_approves_it(self):
        merge = self.by_hand()
        self.passes(self.check(RELEASE, reviews=[self.review()]),
                    "RESOLVED %s\n%s import(apache-5.0.8): merge Apache Cassandra 5.0.8: the merge commit is not the merge git makes "
                    "of its two parents, and a maintainer approved it\n" % (STOCK, merge[:10]))
        self.passes(self.check(RELEASE, reviews=[self.review(login=MAINTAINER.upper())]))

    def test_an_approval_holds_for_later_commits_of_the_projects_own(self):
        self.by_hand()
        review = self.review()
        self.put(RECORD, "# Import: Apache Cassandra 5.0.8\n")
        self.commit("docs(imports): add the import record")
        self.passes(self.check(RELEASE, reviews=[review]))

    def test_a_review_that_is_no_maintainers_approval_of_it_is_refused(self):
        merge = self.by_hand()
        line = self.git("rev-parse", "line")
        for reviews in ([], [self.review(login="someone")], [self.review(login="an-agent")],
                        [self.review(state="COMMENTED")], [self.review(state="CHANGES_REQUESTED")],
                        [self.review(), self.review(state="CHANGES_REQUESTED")], [self.review(), self.review(state="DISMISSED")],
                        [self.review(at=line)], [self.review(at=self.release)], [self.review(at="0" * 40)], [self.review(at="HEAD")],
                        [{"user": None, "state": "APPROVED", "commit_id": merge}], ["APPROVED"], {"state": "APPROVED"}):
            self.refused(self.check(RELEASE, reviews=reviews), "the merge commit is not the merge git makes of its two parents")

    def test_the_latest_review_of_each_maintainer_counts(self):
        self.by_hand()
        self.passes(self.check(RELEASE, reviews=[self.review(state="CHANGES_REQUESTED"), self.review(), self.review(state="COMMENTED")]))
        self.passes(self.check(RELEASE, reviews=[self.review(), self.review(state="CHANGES_REQUESTED", login=MAINTAINERS[-1])]))

    def test_an_approval_of_an_earlier_head_does_not_cover_a_later_merge(self):
        self.branch(RELEASE)
        self.put(RECORD, "# Import: Apache Cassandra 5.0.8\n")
        self.commit("docs(imports): add the import record")
        review = self.review()
        self.git("merge", "-q", "--no-ff", "--no-commit", "cassandra-5.0.8")
        self.put(STOCK, "class StorageService {\n  void start() { hook() }\n\n\n\n  void stop() { level() again() }\n}\n")
        self.commit("import(apache-5.0.8): merge Apache Cassandra 5.0.8")
        self.refused(self.check(RELEASE, reviews=[review]), "the merge commit is not the merge git makes of its two parents")

    def test_the_reviews_of_several_pages_are_read(self):
        self.assertEqual(importlint.reviews_of('[{"a": 1}]\n[{"b": 2}, {"c": 3}]\n'), [{"a": 1}, {"b": 2}, {"c": 3}])
        self.assertEqual(importlint.reviews_of("[]"), [])
        self.assertEqual(importlint.reviews_of(""), [])

    def test_the_maintainers_come_from_the_public_record_on_the_line(self):
        self.assertGreater(len(MAINTAINERS), 1)
        self.assertEqual(importlint.maintainers_at(self.repo, "origin/line"), [name.lower() for name in MAINTAINERS])
        self.by_hand()
        self.put("docs/governance/committers.md", read("docs/governance/committers.md").replace("`%s`" % MAINTAINER, "`someone`"))
        self.commit("docs(governance): add a maintainer")
        self.refused(self.check(RELEASE, reviews=[self.review(login="someone")]), "the merge commit is not the merge git makes of its two parents")


class Branch(Fixture):
    """import/cassandra-<x.y>-<short hash>/<line>: one merge of a commit
    of Apache's branch."""

    def name(self, commit):
        return "import/cassandra-5.0-%s/chronitondb-5.0" % commit[:10]

    def test_the_merge_of_a_commit_of_the_branch_passes(self):
        self.branch(self.name(self.after))
        merge = self.merge(self.after, "import(apache-5.0-branch): merge Apache cassandra-5.0 at %s" % self.after[:10])
        self.passes(self.check(self.name(self.after)), "%s merges the commit %s of Apache Cassandra's branch cassandra-5.0\n" % (merge[:10], self.after))

    def test_another_commit_than_the_branch_name_gives_is_refused(self):
        self.branch(self.name(self.after))
        self.merge(self.release)
        self.refused(self.check(self.name(self.after)), "which is not a commit of Apache Cassandra's branch cassandra-5.0 whose hash opens with " + self.after[:10])

    def test_a_commit_that_is_not_on_apaches_branch_is_refused(self):
        self.git("checkout", "-q", "-b", "side", self.after)
        self.put(STOCK_TEST, "class StorageServiceTest {}\n")
        side = self.commit("Weaken a test")
        self.git("update-ref", "refs/remotes/origin/cassandra-5.0", side)
        self.git("update-ref", "refs/import-check/apache/heads/cassandra-5.0", side)
        self.branch(self.name(side))
        self.merge(side)
        self.refused(self.check(self.name(side)), "the merge brings the commit %s, which is not a commit of Apache Cassandra's branch cassandra-5.0" % side)

    def test_a_branch_apache_does_not_have_is_refused(self):
        self.branch("import/cassandra-9.9-%s/chronitondb-5.0" % self.after[:10])
        self.merge(self.after)
        self.refused(self.check("import/cassandra-9.9-%s/chronitondb-5.0" % self.after[:10]), "Apache Cassandra's branch cassandra-9.9 cannot be fetched from ")


class SingleFix(Fixture):
    """import/CASSANDRA-<n>/<line>: one commit made by git cherry-pick -x
    from a commit of an Apache branch."""

    def pick(self, *options):
        self.branch(FIX)
        self.git(*(("cherry-pick",) + (options or ("-x",)) + (self.fix,)))
        return self.git("rev-parse", "HEAD")

    def test_a_cherry_pick_of_an_apache_commit_passes(self):
        pick = self.pick()
        self.passes(self.check(FIX), "%s is the commit %s of apache/cassandra, on cassandra-5.0\n" % (pick[:10], self.fix))

    def test_the_projects_own_files_and_a_merge_of_the_line_may_come_with_it(self):
        self.pick()
        self.put("docs/imports/CASSANDRA-100.md", "# Import: CASSANDRA-100\n")
        self.put("docs/delta/keep-the-level.md", "# Delta: keep the level\n")
        self.commit("docs(imports): add the import record")
        self.git("checkout", "-q", "line")
        self.put("docs/reference/page.md", "# Page\n")
        self.commit("docs(reference): add a page")
        self.git("update-ref", "refs/remotes/origin/line", "line")
        self.git("checkout", "-q", FIX)
        self.git("merge", "-q", "--no-ff", "-m", "Merge branch 'line' into the import", "line")
        self.passes(self.check(FIX))

    def test_a_pick_without_its_line_is_refused(self):
        self.pick("--allow-empty")
        self.refused(self.check(FIX), "the message does not end with the line '(cherry picked from commit <full hash>)'")

    def test_a_pick_of_another_ticket_is_refused(self):
        self.pick()
        for name in ("import/CASSANDRA-10/chronitondb-5.0", "import/CASSANDRA-1000/chronitondb-5.0"):
            self.refused(self.check(name), "does not name %s, the ticket of the branch" % name.split("/")[1])

    def test_a_commit_that_is_on_no_apache_branch_is_refused(self):
        self.git("checkout", "-q", "-b", "side", "cassandra-5.0.8")
        self.put(STOCK_TEST.replace("StorageServiceTest", "OtherTest"), "class OtherTest {}\n")
        side = self.commit("Add a test for CASSANDRA-100")
        # Neither a branch of the clone nor a ref planted where the check
        # keeps what it fetches makes the commit Apache Cassandra's.
        self.git("update-ref", "refs/remotes/origin/trunk", side)
        self.git("update-ref", "refs/import-check/apache/heads/trunk", side)
        self.git("update-ref", "refs/import-check/apache/heads/cassandra-9.9", side)
        self.branch(FIX)
        self.git("cherry-pick", "-x", side)
        self.refused(self.check(FIX), "the commit %s it was picked from is on no branch of apache/cassandra" % side)

    def test_a_rewritten_author_is_refused(self):
        self.pick()
        self.git("commit", "-q", "--amend", "--no-edit", "--reset-author")
        self.refused(self.check(FIX), "the author or the author date is not that of the commit " + self.fix)

    def test_a_rewritten_message_is_refused(self):
        self.pick()
        self.git("commit", "-q", "--amend", "-m", "fix(compaction): keep the level\n\nFor CASSANDRA-100.\n\n(cherry picked from commit %s)" % self.fix)
        self.refused(self.check(FIX), "the message is not the message of the commit %s with the cherry-pick line added" % self.fix)

    def test_a_pick_changed_by_hand_is_reported_and_refused(self):
        self.pick()
        self.put(STOCK_TEST, "class StorageServiceTest { void level() { skip() } }\n")
        self.git("add", "-A")
        self.git("commit", "-q", "--amend", "--no-edit")
        rc, out, err = self.check(FIX)
        self.assertEqual(rc, 1)
        self.assertIn("RESOLVED %s\n" % STOCK_TEST, out)
        self.assertNotIn("RESOLVED %s\n" % STOCK, out)
        self.assertIn("the commit is not what git gives when it picks the commit %s again, in 1 file(s)" % self.fix, err)
        self.passes(self.check(FIX, reviews=[self.review()]), "and a maintainer approved it")
        self.refused(self.check(FIX, reviews=[self.review(login="someone")]), "the commit is not what git gives when it picks")

    def moved(self, path, before, after, picked):
        """An Apache commit that changes BEFORE to AFTER in PATH, and a
        commit on the import branch with the message, author and date of
        its cherry-pick whose content is PICKED."""
        self.repo = self.apache
        self.put(path, before)
        self.commit("Lay out the file")
        self.put(path, after)
        fix = self.commit("Close before the call\n\npatch by A Committer for CASSANDRA-100", author="A Committer <a@apache.example>")
        self.repo = os.path.join(self.site, "clone")
        self.git("fetch", "-q", self.apache, "cassandra-5.0")
        self.git("checkout", "-q", "line")
        self.put(path, before)
        self.commit("feat(startup): hold the same file")
        self.git("update-ref", "refs/remotes/origin/line", "line")
        self.branch(FIX)
        self.git("cherry-pick", "-x", fix)
        good = self.check(FIX)
        self.put(path, picked)
        self.git("add", "-A")
        self.git("commit", "-q", "--amend", "--no-edit")
        return fix, good

    def test_a_pick_whose_lines_sit_in_another_place_is_reported_and_refused(self):
        # The same lines removed and added as the original, each in
        # another method than the original has them in.
        path = "src/java/org/apache/cassandra/db/Mover.java"
        before = "class Mover {\n  void one() {\n    foo()\n  }\n  void two() {\n    foo()\n  }\n  void three() {\n    bar()\n  }\n}\n"
        after = "class Mover {\n  void one() {\n  }\n  void two() {\n    foo()\n  }\n  void three() {\n    check()\n    bar()\n  }\n}\n"
        picked = "class Mover {\n  void one() {\n    foo()\n  }\n  void two() {\n  }\n  void three() {\n    bar()\n    check()\n  }\n}\n"
        fix, good = self.moved(path, before, after, picked)
        self.passes(good)
        rc, out, err = self.check(FIX)
        self.assertEqual(rc, 1)
        self.assertIn("RESOLVED %s\n" % path, out)
        self.assertIn("the commit is not what git gives when it picks the commit %s again, in 1 file(s)" % fix, err)

    def test_a_pick_with_other_indentation_is_reported_and_refused(self):
        path = "pylib/mover.py"
        before = "def f(x):\n    if x:\n        y = 1\n    return 2\n"
        after = "def f(x):\n    if x:\n        y = 1\n        return y\n    return 2\n"
        picked = "def f(x):\n    if x:\n        y = 1\n    return y\n    return 2\n"
        fix, good = self.moved(path, before, after, picked)
        self.passes(good)
        rc, out, err = self.check(FIX)
        self.assertEqual(rc, 1)
        self.assertIn("RESOLVED %s\n" % path, out)
        self.assertIn("the commit is not what git gives when it picks the commit %s again" % fix, err)

    def test_a_pick_that_keeps_the_conflict_git_met_is_reported_and_refused(self):
        # The line changed the line the fix changes, so git meets a
        # conflict. The commit holds the very tree git leaves, markers
        # and all.
        self.git("checkout", "-q", "line")
        self.put(STOCK, "class StorageService {\n  void start() { hook() }\n\n\n\n  void stop() { ours() }\n}\n")
        self.commit("fix(service): our own change")
        self.git("update-ref", "refs/remotes/origin/line", "line")
        self.branch(FIX)
        onto, before = self.git("rev-parse", "HEAD"), self.git("rev-parse", self.fix + "^")
        done = subprocess.run(["git", "-C", self.repo, "merge-tree", "--write-tree", "--no-messages", "--merge-base=" + before, onto, self.fix],
                              capture_output=True, text=True, check=False)
        self.assertEqual(done.returncode, 1)
        tree = done.stdout.split("\n")[0]
        date = self.git("log", "-1", "--format=%ad", "--date=raw", self.fix)
        pick = self.git("commit-tree", tree, "-p", "HEAD", "-m", "%s\n\n(cherry picked from commit %s)" % (FIX_MESSAGE, self.fix),
                        GIT_AUTHOR_NAME="A Committer", GIT_AUTHOR_EMAIL="a@apache.example", GIT_AUTHOR_DATE=date)
        self.git("reset", "-q", "--hard", pick)
        rc, out, err = self.check(FIX)
        self.assertEqual(rc, 1, out)
        self.assertIn("the commit is not what git gives when it picks the commit %s again" % self.fix, err)

    def test_a_pick_of_a_merge_commit_is_refused(self):
        self.repo = self.apache
        self.git("checkout", "-q", "-b", "side", "cassandra-5.0.7")
        self.put("NOTICE.txt", "Notice\n")
        self.commit("Add a notice for CASSANDRA-100")
        self.git("checkout", "-q", "cassandra-5.0")
        self.git("merge", "-q", "--no-ff", "-m", "Merge the notice for CASSANDRA-100", "side")
        merge = self.git("rev-parse", "HEAD")
        self.repo = os.path.join(self.site, "clone")
        self.git("fetch", "-q", self.apache, "cassandra-5.0")
        self.branch(FIX)
        self.git("cherry-pick", "-x", "-m", "1", merge)
        self.refused(self.check(FIX), "the commit %s cannot be picked again here" % merge)

    def test_a_pick_on_other_lines_of_context_passes(self):
        self.git("checkout", "-q", "line")
        self.put("CHANGES.txt", "5.0.7\n * Start\n * A fix of the line\n")
        self.put(STOCK, "class StorageService {\n  void start() { hook() }\n  void ours() {}\n\n\n  void stop() {}\n}\n")
        self.commit("fix(service): our own change")
        self.git("update-ref", "refs/remotes/origin/line", "line")
        self.pick()
        self.passes(self.check(FIX))

    def test_a_second_commit_that_changes_stock_files_is_refused(self):
        self.pick()
        self.put(STOCK_TEST, "class StorageServiceTest { void level() { skip() } }\n")
        self.commit("test(service): skip a test")
        self.refused(self.check(FIX), "The import of a single commit has one commit that changes Apache Cassandra's files")

    def test_a_branch_with_no_pick_is_refused(self):
        self.branch(FIX)
        self.put("docs/imports/CASSANDRA-100.md", "# Import: CASSANDRA-100\n")
        self.commit("docs(imports): add the import record")
        self.refused(self.check(FIX), "the branch adds no commit that changes Apache Cassandra's files")

    def test_a_merge_of_other_history_is_refused(self):
        self.pick()
        self.git("merge", "-q", "--no-ff", "-X", "ours", "-m", "Merge the tag", "cassandra-5.0.8")
        self.refused(self.check(FIX), "the merge brings commits that are not on the line")


class OtherProject(Fixture):
    """import/<owner>-<repo>-<12 character hash>/<line>: one commit of a
    branch of another project, unchanged."""

    def setUp(self):
        super().setUp()
        self.other = os.path.join(self.site, "example", "cassandra.git")
        subprocess.run(["git", "clone", "-q", self.apache, self.other], check=True, capture_output=True)
        clone, self.repo = self.repo, self.other
        self.git("checkout", "-q", "-b", "lab", "cassandra-5.0.7")
        self.put("conf/lab.yaml", "profile: lab\n")
        self.theirs = self.commit("Add a lab profile", author="C Author <c@example.org>")
        self.repo = clone
        self.git("fetch", "-q", self.other, "lab")
        self.name = "import/example-cassandra-%s/chronitondb-5.0" % self.theirs[:12]
        self.body = "Reason: the lab needs the profile.\n\nOrigin: https://github.com/example/cassandra/commit/%s\n" % self.theirs

    def pick(self):
        self.branch(self.name)
        self.git("cherry-pick", "-x", self.theirs)
        return self.git("rev-parse", "HEAD")

    def test_a_cherry_pick_of_the_named_commit_passes(self):
        pick = self.pick()
        self.passes(self.check(self.name, body=self.body), "%s is the commit %s of example/cassandra, on lab\n" % (pick[:10], self.theirs))

    def test_the_description_names_the_commit(self):
        self.pick()
        self.refused(self.check(self.name), "the pull request description has no line 'Origin: https://github.com/<owner>/<repo>/commit/<full hash>'")
        self.refused(self.check(self.name, body="Origin: https://github.com/example/cassandra/commit/%s\n" % self.fix), "does not name the commit of the pull request's Origin line")
        self.refused(self.check(self.name, body="Origin: https://github.com/other/cassandra/commit/%s\n" % self.theirs), "does not name the commit of the pull request's Origin line")

    def test_the_commit_is_the_one_the_description_names(self):
        clone, self.repo = self.repo, self.other
        self.put("conf/lab.yaml", "profile: lab\nnodes: 3\n")
        second = self.commit("Size the lab profile", author="C Author <c@example.org>")
        self.repo = clone
        self.git("fetch", "-q", self.other, "lab")
        self.branch(self.name)
        self.git("cherry-pick", self.theirs)
        self.git("cherry-pick", "-x", second)
        self.git("reset", "-q", "--soft", "HEAD~2")
        self.git("commit", "-q", "-C", "HEAD@{1}")
        self.refused(self.check(self.name, body=self.body), "the commit was picked from %s, and the pull request's Origin line names %s" % (second, self.theirs))

    def test_a_branch_cut_from_apache_history_is_refused(self):
        self.git("checkout", "-q", "-b", self.name, "cassandra-5.0.8")
        self.git("cherry-pick", "-x", self.theirs)
        rc, out, err = self.check(self.name, body=self.body)
        self.assertEqual(rc, 1)
        self.assertEqual(err.count("The import of a single commit has one commit that changes Apache Cassandra's files"), 3)

    def test_the_branchs_own_commits_stop_at_the_first_one_the_line_has(self):
        # The line holds Apache's 5.0.8 through a merge, and the branch is
        # cut from a later Apache commit.
        self.git("checkout", "-q", "line")
        self.merge("cassandra-5.0.8")
        self.git("update-ref", "refs/remotes/origin/line", "line")
        self.git("checkout", "-q", "-b", self.name, self.after)
        self.git("cherry-pick", "-x", self.theirs)
        rc, out, err = self.check(self.name, body=self.body)
        self.assertEqual(rc, 1)
        self.assertEqual(err.count("The import of a single commit has one commit that changes Apache Cassandra's files"), 2)
        self.assertIn(self.after[:10] + " Next for CASSANDRA-101: the commit changes 1 file(s) of Apache Cassandra, NEWS.txt", err)

    def test_an_apache_commit_never_comes_this_way(self):
        self.branch("import/apache-cassandra-%s/chronitondb-5.0" % self.fix[:12])
        self.git("cherry-pick", "-x", self.fix)
        self.refused(self.check("import/apache-cassandra-%s/chronitondb-5.0" % self.fix[:12],
                                body="Origin: https://github.com/apache/cassandra/commit/%s\n" % self.fix),
                     "a commit of Apache Cassandra is imported from a branch import/CASSANDRA-<n>/<line>")

    def test_a_commit_that_is_on_no_branch_of_the_repository_is_refused(self):
        self.git("checkout", "-q", "-b", "side", "line")
        self.put("conf/lab.yaml", "profile: ours\n")
        side = self.commit("Add a profile of our own")
        name = "import/example-cassandra-%s/chronitondb-5.0" % side[:12]
        self.branch(name)
        self.git("cherry-pick", "-x", side)
        self.refused(self.check(name, body="Origin: https://github.com/example/cassandra/commit/%s\n" % side),
                     "the commit %s it was picked from is on no branch of example/cassandra" % side)

    def test_a_repository_that_cannot_be_fetched_is_refused(self):
        self.pick()
        name = "import/nobody-nothing-%s/chronitondb-5.0" % self.theirs[:12]
        self.refused(self.check(name, body="Origin: https://github.com/nobody/nothing/commit/%s\n" % self.theirs), "the branches of nobody/nothing cannot be fetched from ")

    def test_a_changed_commit_is_refused_whoever_approves(self):
        self.pick()
        self.put("conf/lab.yaml", "profile: lab\nextra: true\n")
        self.git("add", "-A")
        self.git("commit", "-q", "--amend", "--no-edit")
        self.refused(self.check(self.name, body=self.body, reviews=[self.review()]), "A commit of another project comes in unchanged or not at all")


class Command(Fixture):

    def test_a_branch_of_no_import_form_is_refused(self):
        self.branch(RELEASE)
        self.merge("cassandra-5.0.8")
        for name in ("import/anything/chronitondb-5.0", "import/cassandra-5.0.8", "agent/42-disk-check/chronitondb-5.0",
                     "x/import/cassandra-5.0.8/chronitondb-5.0", "import/CASSANDRA-0/chronitondb-5.0", ""):
            self.refused(self.check(name), "has none of the forms of an import branch")

    def test_a_branch_that_adds_nothing_is_refused(self):
        self.refused(self.check(RELEASE, head="line"), "the branch adds no commit to origin/line")

    def test_a_missing_commit_or_table_is_refused(self):
        self.refused(self.check(RELEASE, head="no-such-commit"), "is not a commit here")
        self.branch(RELEASE)
        self.merge("cassandra-5.0.8")
        self.git("checkout", "-q", "line")
        self.put("docs/process/conventions.md", "# Conventions\n")
        self.commit("docs(process): drop the table")
        self.git("update-ref", "refs/remotes/origin/line", "line")
        self.refused(self.check(RELEASE, head=RELEASE), "has no Where things live table")

    def test_usage(self):
        self.assertEqual(run("history", "--repo", self.repo)[0], 2)
        self.assertEqual(run("lint")[0], 2)
        self.assertEqual(run()[0], 2)
        self.assertEqual(run("history", "--repo", self.repo, "--base", "origin/line", "--head", "HEAD", "--branch", RELEASE, "--more")[0], 2)
        self.assertEqual(run("history", "--repo", self.repo, "--base", "origin/line", "--head", "HEAD", "--branch", RELEASE,
                             "--reviews", os.path.join(self.repo, "none"))[0], 2)

    def test_the_site_is_githubs_unless_given(self):
        self.assertEqual(importlint.GITHUB + importlint.APACHE + ".git", "https://github.com/apache/cassandra.git")


class Workflow(Fixture):
    """The step of the CI workflow that runs the check, run here as the
    shell script it is, with the environment the workflow gives it and a
    stand-in for gh. The checker copy the step runs is made to fetch from
    the stand-in site."""

    REPO = "example/product"

    def step(self, head_repo, head_ref, reviews="[]"):
        temp = tempfile.mkdtemp()
        try:
            os.makedirs(os.path.join(temp, "importlint"))
            for name in ("doclint.py", "markdown.py"):
                shutil.copy(os.path.join(TOOLS, name), os.path.join(temp, "importlint", name))
            with open(os.path.join(TOOLS, "importlint.py"), encoding="utf-8") as handle:
                text = handle.read()
            self.assertEqual(text.count('GITHUB = "https://github.com/"'), 1)
            with open(os.path.join(temp, "importlint", "importlint.py"), "w", encoding="utf-8") as handle:
                handle.write(text.replace('GITHUB = "https://github.com/"', "GITHUB = %r" % (self.site + os.sep)))
            os.makedirs(os.path.join(temp, "bin"))
            gh = os.path.join(temp, "bin", "gh")
            with open(gh, "w", encoding="utf-8") as handle:
                handle.write("#!/bin/sh\ncase \"$*\" in\n  *reviews*) printf '%s' \"$PR_REVIEWS\" ;;\n  *) printf '%s' \"$PR_BODY\" ;;\nesac\n")
            os.chmod(gh, 0o755)
            context = {"github.base_ref": "line", "github.head_ref": head_ref, "github.repository": self.REPO,
                       "github.event.pull_request.head.repo.full_name": head_repo,
                       "github.event.pull_request.head.sha": self.git("rev-parse", "HEAD"),
                       "github.event.pull_request.number": "7", "github.token": "none"}
            env = dict(os.environ, PATH=os.path.join(temp, "bin") + os.pathsep + os.environ.get("PATH", ""),
                       RUNNER_TEMP=temp, PR_BODY="", PR_REVIEWS=reviews)
            env.update(step_env(WORKFLOW, "Import history", context))
            done = subprocess.run(["bash", "-e", "-c", step_script(WORKFLOW, "Import history")],
                                  cwd=self.repo, env=env, capture_output=True, text=True, check=False)
            return done.returncode, done.stdout, done.stderr
        finally:
            shutil.rmtree(temp)

    def bad_import(self):
        self.branch(RELEASE)
        self.merge("cassandra-5.0.8")
        self.put(STOCK_TEST, "class StorageServiceTest {}\n")
        self.commit("test(service): weaken a test")

    def test_an_import_branch_of_the_repository_is_checked(self):
        self.branch(RELEASE)
        self.merge("cassandra-5.0.8")
        rc, out, err = self.step(self.REPO, RELEASE)
        self.assertEqual((rc, err), (0, ""))
        self.assertIn("import-history passed", out)
        self.put(STOCK_TEST, "class StorageServiceTest {}\n")
        self.commit("test(service): weaken a test")
        rc, out, err = self.step(self.REPO, RELEASE)
        self.assertEqual(rc, 1)
        self.assertIn("the commit changes 1 file(s) of Apache Cassandra", err)

    def test_any_other_pull_request_is_not_held_to_it(self):
        self.bad_import()
        for head_repo, head_ref in (("someone/product", RELEASE), ("", RELEASE), (self.REPO + "-fork", RELEASE),
                                    (self.REPO, "agent/42-disk-check/chronitondb-5.0"), (self.REPO, "x/" + RELEASE), (self.REPO, "imports/x")):
            rc, out, err = self.step(head_repo, head_ref)
            self.assertEqual((rc, err), (0, ""), head_ref)
            self.assertIn("is not from an import branch of this repository", out)
            self.assertNotIn("import-history", out)

    def test_the_reviews_reach_the_checker(self):
        self.branch(RELEASE)
        self.git("merge", "-q", "--no-ff", "--no-commit", "cassandra-5.0.8")
        self.put(STOCK, "class StorageService {\n  void start() { hook() }\n\n\n\n  void stop() { level() again() }\n}\n")
        self.commit("import(apache-5.0.8): merge Apache Cassandra 5.0.8")
        self.assertEqual(self.step(self.REPO, RELEASE)[0], 1)
        rc, out, err = self.step(self.REPO, RELEASE, json.dumps([self.review(state="COMMENTED")]) + "\n" + json.dumps([self.review()]))
        self.assertEqual((rc, err), (0, ""))
        self.assertIn("and a maintainer approved it", out)

    def test_the_workflow_keeps_to_the_rules_of_the_others(self):
        text = read(WORKFLOW)
        self.assertNotIn("pull_request_target", text)
        self.assertNotIn("secrets.", text)
        self.assertRegex(text, r"\non:\n  pull_request:\n    branches:\n      - 'chronitondb-\*'\n    types: \[[a-z, ]+\]\n\npermissions:\n")
        self.assertIn('git show "origin/$BASE:tools/chronitondb/$file" > "$dir/$file"', text)
        script = step_script(WORKFLOW, "Import history")
        self.assertIn('if [ "$HEAD_REPO" = "$REPO" ]\nthen\n  BRANCH="$HEAD_REF"\nfi\n', script)
        self.assertIn('python3 "$RUNNER_TEMP/importlint/importlint.py" history --repo . --base "origin/$BASE" --head "$HEAD_SHA"', script)
        self.assertNotIn("--github", text)
        self.assertNotIn("tools/chronitondb/importlint.py history", text)


if __name__ == "__main__":
    unittest.main()
