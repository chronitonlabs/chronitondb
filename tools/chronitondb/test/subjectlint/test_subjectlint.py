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
"""The subject check of docs/process/conventions.md, Commit messages, on
pull request titles and on the commits a push brings to a line. Run from
the repository root:

    python3 -m unittest discover -s tools/chronitondb/test/subjectlint
"""

import contextlib
import io
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

TOOLS = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
ROOT = os.path.normpath(os.path.join(TOOLS, "..", ".."))
sys.path.insert(0, TOOLS)
import subjectlint  # noqa: E402

with open(os.path.join(ROOT, "docs", "process", "conventions.md"), encoding="utf-8") as _handle:
    CONVENTIONS = _handle.read()
TYPES, LIMIT = subjectlint.rules_of(CONVENTIONS)

# One title per type of the Types table, each as a maintainer writes it.
TITLES = {
    "feat": "feat(fulltext): add the phrase operator",
    "fix": "fix(fulltext): keep the slop of a phrase query",
    "perf": "perf(fulltext): read postings in blocks",
    "security": "security(transport): refuse an oversized frame",
    "refactor": "refactor(fulltext): split the query planner",
    "test": "test(fulltext): cover phrases across segments",
    "docs": "docs(process): add the product manager role (chronitondb-5.0)",
    "build": "build(tools): check the delta register (chronitondb-sandbox)",
    "ci": "ci(github): run every class label check (chronitondb-5.0)",
    "chore": "chore(github): tidy the issue labels",
}
IMPORTS = (
    "import(CASSANDRA-21319): Route 6.0 versions to the cassandra-6.0 job",
    "import(apache-5.0.8): merge Apache Cassandra 5.0.8",
    "import(apache-6.0-alpha2): merge Apache Cassandra 6.0-alpha2",
    "import(apache-6.0-branch): merge Apache cassandra-6.0 at 1a2b3c4d5e",
    "import(rustyrazorblade/cassandra@579e35ae6c12): Add a lab profile",
)


def check(title, body=""):
    return subjectlint.check_subject(title, body, TYPES, LIMIT)


def run(*args):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = subjectlint.main(list(args))
    return rc, out.getvalue(), err.getvalue()


class Rules(unittest.TestCase):

    def test_the_rules_come_from_conventions(self):
        self.assertEqual(LIMIT, 72)
        self.assertEqual(sorted(TYPES), sorted(list(TITLES) + ["import"]))

    def test_a_type_the_table_does_not_list_is_refused(self):
        types = [kind for kind in TYPES if kind != "perf"]
        errors = subjectlint.check_subject(TITLES["perf"], "", types, LIMIT)
        self.assertEqual(len(errors), 1)
        self.assertIn("the type 'perf' is not one of", errors[0])


class Titles(unittest.TestCase):

    def test_each_type_passes(self):
        for kind, title in TITLES.items():
            self.assertEqual(check(title), [], kind)

    def test_each_import_form_passes(self):
        for title in IMPORTS:
            self.assertEqual(check(title), [], title)

    def test_an_unknown_type_fails(self):
        errors = check("feature(fulltext): add the phrase operator")
        self.assertIn("the type 'feature' is not one of", errors[0])

    def test_a_title_without_the_form_fails(self):
        for title in ("Add the phrase operator", "Update .build/run-ci", "feat(fulltext) add the phrase operator",
                      "Merge pull request #37 from chronitonlabs/millerjp/build-scripts/chronitondb-5.0"):
            errors = check(title)
            self.assertTrue(any("the form 'type(scope): description'" in e for e in errors), title)

    def test_a_title_without_a_scope_fails(self):
        errors = check("docs: remove private references from public files")
        self.assertEqual(errors, ["the subject names its scope, the area of the change, as in 'docs(<scope>): remove private references from public files'"])

    def test_a_scope_that_is_not_one_word_fails(self):
        errors = check("fix(full text): keep the slop")
        self.assertIn("the scope 'full text' is one word", errors[0])

    def test_a_title_of_72_characters_passes_and_73_fails(self):
        title = "docs(process): " + "a" * (72 - len("docs(process): "))
        self.assertEqual(len(title), 72)
        self.assertEqual(check(title), [])
        errors = check(title + "b")
        self.assertEqual(errors, ["the subject has 73 characters, at most 72 are allowed"])

    def test_a_too_long_title_fails(self):
        errors = check("docs(process): fix records, kind labels, release rules and new templates (chronitondb-5.0)")
        self.assertIn("the subject has 90 characters, at most 72 are allowed", errors)

    def test_a_title_listing_files_fails(self):
        for title, listed in (("fix(build): update .build/run-ci", ".build/run-ci"),
                              ("docs(process): edit docs/process/ pages", "docs/process/"),
                              ("fix(fulltext): change Phrase.java and build.xml", "Phrase.java, build.xml"),
                              ("chore(github): fix .editorconfig", ".editorconfig")):
            errors = check(title)
            self.assertEqual(errors, ["the subject lists files (%s). Say what the change does, not which files it touches" % listed], title)

    def test_words_with_a_slash_or_a_dot_that_are_no_files_pass(self):
        for title in ("fix(fulltext): keep the read/write path apart", "build(java)!: require Java 17 on the 5.0 line",
                      "docs(process): rename to requirements analyst (chronitondb-6.0)"):
            body = "BREAKING CHANGE: the 5.0 line builds with Java 17 only." if "!" in title else ""
            self.assertEqual(check(title, body), [], title)


class BreakingChanges(unittest.TestCase):

    def test_a_breaking_change_with_its_footer_passes(self):
        body = "## What and why\n\nRenames it.\n\nBREAKING CHANGE: the option analyzer is now tokenizer. Rename it in each index.\n"
        self.assertEqual(check("feat(fulltext)!: rename the analyzer option", body), [])

    def test_a_breaking_change_without_its_footer_fails(self):
        errors = check("feat(fulltext)!: rename the analyzer option", "## What and why\n\nRenames it.\n")
        self.assertEqual(errors, ["a breaking change with '!' also takes a footer line 'BREAKING CHANGE: <what breaks and what to do>'"])

    def test_a_footer_without_the_bang_fails(self):
        errors = check("feat(fulltext): rename the analyzer option", "BREAKING CHANGE: rename it in each index.\n")
        self.assertEqual(errors, ["a 'BREAKING CHANGE:' footer also takes '!' after the scope, as in 'feat(fulltext)!: rename the analyzer option'"])

    def test_a_footer_inside_a_line_does_not_count(self):
        errors = check("feat(fulltext)!: rename the analyzer option", "See the BREAKING CHANGE: section.\n")
        self.assertIn("a breaking change with '!' also takes a footer line", errors[0])


class Imports(unittest.TestCase):

    def test_a_fork_import_passes(self):
        self.assertEqual(check("import(rustyrazorblade/cassandra@579e35ae6c12): Add a lab profile"), [])

    def test_a_fork_import_with_a_short_hash_fails(self):
        errors = check("import(rustyrazorblade/cassandra@579e35a): Add a lab profile")
        self.assertIn("is not one of the import forms", errors[0])

    def test_an_apache_commit_through_the_fork_form_fails(self):
        errors = check("import(apache/cassandra@3f1593064cc8): Route 6.0 versions")
        self.assertEqual(errors, ["an Apache commit is imported as import(CASSANDRA-<n>), never as a commit from another project"])

    def test_our_own_organisation_is_never_a_source(self):
        errors = check("import(chronitonlabs/chronitondb-upstream@579e35ae6c12): Fix it")
        self.assertEqual(errors, ["a repository of chronitonlabs is never a source of an import. Its work is ours"])

    def test_a_release_import_names_its_version_twice(self):
        errors = check("import(apache-5.0.8): merge Apache Cassandra 5.0.9")
        self.assertEqual(errors, ["an import of an Apache release reads 'import(apache-5.0.8): merge Apache Cassandra 5.0.8'"])

    def test_a_branch_import_names_its_branch_and_hash(self):
        errors = check("import(apache-6.0-branch): merge the Apache branch")
        self.assertEqual(errors, ["an import of Apache's branch reads 'import(apache-6.0-branch): merge Apache cassandra-6.0 at <short hash>'"])

    def test_another_import_scope_fails(self):
        errors = check("import(datastax): bring in the vector search")
        self.assertIn("the import scope 'datastax' is not one of the import forms", errors[0])

    def test_an_import_takes_no_bang(self):
        errors = check("import(CASSANDRA-21319)!: Route 6.0 versions")
        self.assertIn("an import takes no '!'", errors[0])

    def test_an_import_keeps_file_names_of_the_original_subject(self):
        self.assertEqual(check("import(CASSANDRA-21319): Fix NPE in StorageService.java"), [])

    def test_an_import_too_long_fails(self):
        title = "import(CASSANDRA-21319): " + "Fix " * 15
        self.assertIn("at most 72 are allowed", check(title.strip())[0])


class Command(unittest.TestCase):

    def setUp(self):
        self.repo = tempfile.mkdtemp()
        self.git("init", "-q", "-b", "line")
        os.makedirs(os.path.join(self.repo, "docs", "process"))
        with open(os.path.join(self.repo, "docs", "process", "conventions.md"), "w", encoding="utf-8") as handle:
            handle.write(CONVENTIONS)
        self.git("add", "-A")
        self.commit("docs(process): add the conventions")

    def tearDown(self):
        shutil.rmtree(self.repo)

    def git(self, *args):
        return subprocess.run(["git", "-C", self.repo, "-c", "user.name=t", "-c", "user.email=t@example.org",
                               "-c", "commit.gpgsign=false", "-c", "core.hooksPath=/dev/null"] + list(args),
                              check=True, capture_output=True, text=True).stdout.strip()

    def commit(self, message):
        self.git("commit", "-q", "--allow-empty", "-m", message)
        return self.git("rev-parse", "HEAD")

    def title(self, title, body=None):
        args = ["title", "--repo", self.repo, "--rules", "line"]
        if body is not None:
            path = os.path.join(self.repo, ".git", "body.txt")
            with open(path, "w", encoding="utf-8") as handle:
                handle.write(body)
            args += ["--body", path]
        return run(*(args + [title]))

    def test_a_good_title_passes(self):
        rc, out, err = self.title(TITLES["feat"])
        self.assertEqual((rc, err, out), (0, "", "title passed\n"))

    def test_a_bad_title_fails(self):
        rc, out, err = self.title("Update build.xml")
        self.assertEqual(rc, 1)
        self.assertIn("title: the subject has the form", err)
        self.assertEqual(out, "title failed\n")

    def test_the_footer_is_read_from_the_description(self):
        rc, _, err = self.title("feat(fulltext)!: rename the analyzer option", "BREAKING CHANGE: rename it in each index.\n")
        self.assertEqual((rc, err), (0, ""))

    def test_squash_and_merge_subjects_on_the_line(self):
        start = self.git("rev-parse", "HEAD")
        self.commit("feat(fulltext): add the phrase operator (#121)")
        self.commit("feat(fulltext)!: rename the analyzer option (#122)\n\nBREAKING CHANGE: rename it in each index.")
        rc, out, err = run("commits", "--repo", self.repo, "--rules", "line", "%s..line" % start)
        self.assertEqual((rc, err), (0, ""))
        self.assertEqual(out, "subjects 2 checked 0 failed\n")

    def test_the_github_number_is_not_counted(self):
        start = self.git("rev-parse", "HEAD")
        title = "docs(process): " + "a" * (72 - len("docs(process): "))
        self.commit(title + " (#123)")
        rc, _, err = run("commits", "--repo", self.repo, "--rules", "line", "%s..line" % start)
        self.assertEqual((rc, err), (0, ""))

    def test_a_subject_edited_in_the_merge_dialog_fails(self):
        start = self.git("rev-parse", "HEAD")
        bad = self.commit("Phrase operator (#124)")
        rc, out, err = run("commits", "--repo", self.repo, "--rules", "line", "%s..line" % start)
        self.assertEqual(rc, 1)
        self.assertIn("%s Phrase operator (#124): the subject has the form" % bad[:10], err)
        self.assertEqual(out, "subjects 1 checked 1 failed\n")

    def test_the_commits_an_import_merge_brings_are_not_checked(self):
        start = self.git("rev-parse", "HEAD")
        self.git("checkout", "-q", "-b", "apache")
        self.commit("Route 6.0 versions to the cassandra-6.0 job\n\npatch by someone for CASSANDRA-21319")
        self.git("checkout", "-q", "line")
        self.git("merge", "-q", "--no-ff", "-m", "import(CASSANDRA-21319): Route 6.0 versions to the cassandra-6.0 job (#125)", "apache")
        rc, out, err = run("commits", "--repo", self.repo, "--rules", "line", "%s..line" % start)
        self.assertEqual((rc, err), (0, ""))
        self.assertEqual(out, "subjects 1 checked 0 failed\n")

    def test_usage(self):
        self.assertEqual(run("title", "--repo", self.repo)[0], 2)
        self.assertEqual(run("lint")[0], 2)

    def test_missing_rules_fail(self):
        rc, _, err = run("title", "--repo", self.repo, "--rules", "no-such-ref", TITLES["feat"])
        self.assertEqual(rc, 1)
        self.assertIn("the subject rules cannot be read", err)


if __name__ == "__main__":
    unittest.main()
