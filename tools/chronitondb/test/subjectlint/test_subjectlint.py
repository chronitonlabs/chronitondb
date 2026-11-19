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
    "feat": "feat(compaction): count a skipped sstable once",
    "fix": "fix(compaction): keep the level of a moved sstable",
    "perf": "perf(compaction): read the index in blocks",
    "security": "security(transport): refuse an oversized frame",
    "refactor": "refactor(compaction): split the task planner",
    "test": "test(compaction): cover sstables across levels",
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


def check(title, messages="", pr_body=None):
    return subjectlint.check_subject(title, messages, TYPES, LIMIT, pr_body)


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
        errors = check("feature(compaction): count a skipped sstable once")
        self.assertIn("the type 'feature' is not one of", errors[0])

    def test_a_title_without_the_form_fails(self):
        for title in ("Count a skipped sstable once", "Update .build/run-ci", "feat(compaction) count a skipped sstable once",
                      "Merge pull request #37 from chronitonlabs/millerjp/build-scripts/chronitondb-5.0"):
            errors = check(title)
            self.assertTrue(any("the form 'type(scope): description'" in e for e in errors), title)

    def test_a_title_without_a_scope_fails(self):
        errors = check("docs: remove private references from public files")
        self.assertEqual(errors, ["the subject names its scope, the area of the change, as in 'docs(<scope>): remove private references from public files'"])

    def test_a_scope_that_is_not_one_word_fails(self):
        errors = check("fix(disk check): keep the limit")
        self.assertIn("the scope 'disk check' is one word", errors[0])

    def test_a_title_of_72_characters_passes_and_73_fails(self):
        title = "docs(process): " + "a" * (72 - len("docs(process): "))
        self.assertEqual(len(title), 72)
        self.assertEqual(check(title), [])
        errors = check(title + "b")
        self.assertEqual(errors, ["the subject has 73 characters, at most 72 are allowed, not counting a trailing ' (chronitondb-<line>)'"])

    def test_a_too_long_title_fails(self):
        errors = check("docs(process): describe how ChronitonDB is developed, maintained and released")
        self.assertEqual(errors, ["the subject has 77 characters, at most 72 are allowed, not counting a trailing ' (chronitondb-<line>)'"])

    def test_the_line_suffix_is_not_counted(self):
        title = "docs(process): fix records, kind labels, release rules and new templates"
        self.assertEqual(len(title), 72)
        for line in ("5.0", "6.0", "sandbox"):
            self.assertEqual(check("%s (chronitondb-%s)" % (title, line)), [], line)
        self.assertIn("73 characters", check(title.replace("fix", "fixe") + " (chronitondb-sandbox)")[0])

    def test_a_suffix_that_names_no_line_is_counted(self):
        title = "docs(process): fix records, kind labels, release rules and new templates (all lines)"
        self.assertIn("84 characters", check(title)[0])

    def test_a_title_listing_files_fails(self):
        for title, listed in (("fix(build): update .build/run-ci", ".build/run-ci"),
                              ("docs(process): edit docs/process/ pages", "docs/process/"),
                              ("fix(startup): change DiskCheck.java and build.xml", "DiskCheck.java, build.xml"),
                              ("chore(github): fix .editorconfig", ".editorconfig")):
            errors = check(title)
            self.assertEqual(errors, ["the subject lists files (%s). Say what the change does, not which files it touches" % listed], title)

    def test_words_with_a_slash_or_a_dot_that_are_no_files_pass(self):
        for title in ("fix(compaction): keep the read/write path apart", "build(java)!: require Java 17 on the 5.0 line",
                      "docs(process): rename to requirements analyst (chronitondb-6.0)"):
            body = "BREAKING CHANGE: the 5.0 line builds with Java 17 only." if "!" in title else ""
            self.assertEqual(check(title, body), [], title)


class BreakingChanges(unittest.TestCase):

    TITLE = "feat(nodetool)!: rename the version option"
    COMMIT = "feat(nodetool)!: rename the version option\n\nBREAKING CHANGE: the option release is now version. Rename it in each script.\n"
    DESCRIPTION = "## What and why\n\nRenames it.\n\nBREAKING CHANGE: the option release is now version. Rename it in each script.\n"
    WHERE = "Put the line 'BREAKING CHANGE: <what breaks and what to do>' in a commit message of the pull request, which the squash commit on the line carries"

    def test_a_title_with_the_footer_in_a_commit_passes(self):
        self.assertEqual(check(self.TITLE, self.COMMIT, pr_body="## What and why\n\nRenames it.\n"), [])

    def test_a_title_with_the_footer_in_a_commit_and_the_description_passes(self):
        self.assertEqual(check(self.TITLE, self.COMMIT, pr_body=self.DESCRIPTION), [])

    def test_a_title_with_the_footer_only_in_the_description_fails(self):
        errors = check(self.TITLE, "feat(nodetool)!: rename the version option\n", pr_body=self.DESCRIPTION)
        self.assertEqual(errors, ["the 'BREAKING CHANGE:' footer is only in the pull request description, which never reaches the line. " + self.WHERE])

    def test_a_title_without_any_footer_fails(self):
        errors = check(self.TITLE, "feat(nodetool)!: rename the version option\n", pr_body="Renames it.\n")
        self.assertEqual(errors, ["a breaking change with '!' also takes a footer. " + self.WHERE])

    def test_a_footer_only_in_the_description_without_the_bang_fails(self):
        errors = check("feat(nodetool): rename the version option", "", pr_body=self.DESCRIPTION)
        self.assertEqual(errors, ["the pull request description has a 'BREAKING CHANGE:' footer. A breaking change takes '!' after the scope, and the footer goes in a commit message of the pull request"])

    def test_a_commit_with_its_footer_passes(self):
        self.assertEqual(check(self.TITLE, "\nBREAKING CHANGE: rename it in each script.\n"), [])

    def test_a_commit_without_its_footer_fails(self):
        errors = check(self.TITLE, "\nRenames it.\n")
        self.assertEqual(errors, ["a breaking change with '!' also takes a footer line 'BREAKING CHANGE: <what breaks and what to do>' in its commit message"])

    def test_a_footer_without_the_bang_fails(self):
        errors = check("feat(nodetool): rename the version option", "BREAKING CHANGE: rename it in each script.\n")
        self.assertEqual(errors, ["a 'BREAKING CHANGE:' footer also takes '!' after the scope, as in 'feat(nodetool)!: rename the version option'"])

    def test_a_footer_inside_a_line_does_not_count(self):
        errors = check(self.TITLE, "See the BREAKING CHANGE: section.\n")
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

    def test_an_import_keeps_a_long_original_subject(self):
        for title in ("import(CASSANDRA-21319): Fix the token allocation of a new node when the keyspace uses NetworkTopologyStrategy",
                      "import(rustyrazorblade/cassandra@579e35ae6c12): Add the easy-cass-lab profile for local clusters"):
            self.assertGreater(len(title), 72)
            self.assertEqual(check(title), [], title)

    def test_a_long_import_still_takes_its_exact_form(self):
        title = "import(apache-5.0.8): merge Apache Cassandra 5.0.8 with the fixes of the month and more words"
        self.assertEqual(check(title), ["an import of an Apache release reads 'import(apache-5.0.8): merge Apache Cassandra 5.0.8'"])

    def test_an_import_without_its_scope_fails(self):
        self.assertIn("an import takes one of the import forms", check("import: bring in a fix")[0])

    def test_an_import_title_from_an_import_branch_passes(self):
        for title, branch in zip(IMPORTS, ("import/CASSANDRA-21319/chronitondb-6.0", "import/cassandra-5.0.8/chronitondb-5.0",
                                           "import/cassandra-6.0-alpha2/chronitondb-6.0", "import/cassandra-6.0-1a2b3c4d5e/chronitondb-6.0",
                                           "import/rustyrazorblade-cassandra-579e35ae6c12/chronitondb-5.0")):
            self.assertEqual(subjectlint.check_subject(title, "", TYPES, LIMIT, "", branch), [], title)

    def test_an_import_title_from_another_branch_is_refused(self):
        # The import type lifts the length rule and the file rule, so a
        # change that is no import may not take it to pass them.
        title = "import(CASSANDRA-1): change DiskCheck.java, build.xml and every other file this long subject can name"
        self.assertEqual(check(title), [])
        errors = subjectlint.check_subject(title, "", TYPES, LIMIT, "", "agent/42-disk-check/chronitondb-5.0")
        self.assertEqual(errors, ["the type 'import' is only for an import, a pull request from an import/ branch of this repository. "
                                  "This pull request comes from the branch 'agent/42-disk-check/chronitondb-5.0'. Use the type of the change it makes"])

    def test_an_import_title_with_no_branch_that_counts_is_refused(self):
        # CI gives an empty name for the branch of a fork.
        errors = subjectlint.check_subject(IMPORTS[0], "", TYPES, LIMIT, "", "")
        self.assertEqual(len(errors), 1)
        self.assertIn("This pull request comes from a branch of a fork or one with no name given", errors[0])

    def test_the_branch_is_not_asked_of_another_type(self):
        self.assertEqual(subjectlint.check_subject(TITLES["feat"], "", TYPES, LIMIT, "", ""), [])
        self.assertEqual(subjectlint.check_subject(TITLES["feat"], "", TYPES, LIMIT, "", "agent/42-disk-check/chronitondb-5.0"), [])


AI_CO_AUTHOR = "Co-authored-by: Example Model 4 <noreply@anthropic.com>"
SESSION_TRAILER = "Example-Session: https://sessions.example.org/01ABC"
SESSION_LINK = "https://claude.ai/code/session_01ABC"
BANNER = "Generated with [Example Tool](https://tool.example.org)"
ALLOWED = (
    "Assisted-by: Example Tool:example-model-4",
    "Requested-by: octocat 583231+octocat@users.noreply.github.com",
    "Co-authored-by: Stefan Example <stefan@example.org>",
)


class Attribution(unittest.TestCase):
    """conventions.md, Trailers: no AI tool or model as a co-author, no
    link to a session of an AI tool and no line that says a tool generated
    the text, in a commit message or a pull request description."""

    def findings(self, *lines):
        return subjectlint.check_attribution("fix the count\n\nThe cause and the fix.\n\n" + "\n".join(lines) + "\n")

    def test_a_clean_message_passes(self):
        self.assertEqual(self.findings("Fixes #42"), [])
        self.assertEqual(subjectlint.check_attribution(""), [])
        self.assertEqual(subjectlint.check_attribution(None), [])

    def test_the_allowed_trailers_pass(self):
        self.assertEqual(self.findings(*ALLOWED), [])

    def test_a_person_as_co_author_passes(self):
        # First names that are also the names of tools.
        for person in ("Claude Dupont <claude.dupont@example.org>", "Ai Tanaka <ai@example.org>", "Devin Jones <devin@example.org>",
                       "Cody Smith <cody@example.org>", "Gemini Rossi <g@example.org>", "Jane Roe <jane@openai.com>",
                       "Stefan Miklosovic <smiklosovic@apache.org>"):
            self.assertEqual(self.findings("Co-authored-by: " + person), [], person)

    def test_an_ai_tool_or_model_as_co_author_is_refused(self):
        for tool in ("Claude <noreply@anthropic.com>", "Claude Opus 4.1 <noreply@anthropic.com>", "Someone <noreply@anthropic.com>",
                     "Copilot <175728472+Copilot@users.noreply.github.com>", "Cursor Agent <cursoragent@cursor.com>",
                     "aider (gpt-4o) <aider@example.org>", "Devin AI <devin@example.org>", "GPT-5 <model@example.org>",
                     "Gemini <gemini@example.org>", "ChatGPT <chat@example.org>", "An AI assistant <a@example.org>"):
            for name in ("Co-authored-by", "Co-Authored-By", "co-authored-by"):
                errors = self.findings("%s: %s" % (name, tool))
                self.assertEqual(len(errors), 1, tool)
                self.assertIn("names an AI tool or model as a co-author", errors[0])
                self.assertIn("'Assisted-by: <tool>:<model>'", errors[0])

    def test_punctuation_round_a_tools_name_does_not_hide_it(self):
        for tool in ("Claude. <claude@example.org>", "Claude \U0001F916 <claude@example.org>", "\"Claude\" <claude@example.org>",
                     "[Copilot] <c@example.org>", "*Gemini* <g@example.org>", "claude_ <c@example.org>"):
            self.assertEqual(len(self.findings("Co-authored-by: " + tool)), 1, tool)
        for person in ("Claude Dupont, PhD <claude.dupont@example.org>", "J. R. Roe <jr@example.org>", "Anne-Marie O'Neil <a@example.org>"):
            self.assertEqual(self.findings("Co-authored-by: " + person), [], person)

    def test_a_session_address_without_its_scheme_is_refused(self):
        for line in ("See claude.ai/code/session_01ABC", "claude.ai/share/abc", "Written at chatgpt.com/share/abc.", "(www.github.com/copilot/c/1)"):
            errors = self.findings(line)
            self.assertEqual(len(errors), 1, line)
            self.assertIn("links a session of an AI tool", errors[0])
        for line in ("The site claude.ai is down.", "Mail to someone@claude.ai/x", "See docs.example.org/claude.ai/notes", "notclaude.ai/x"):
            self.assertEqual(self.findings(line), [], line)

    def test_a_banner_in_other_words_or_over_two_lines_is_refused(self):
        for lines in (("Generated using Claude Code",), ("Written by Claude",), ("Created with ChatGPT",), ("Authored by GitHub Copilot",),
                      ("\U0001F916 Generated", "with Claude Code"), ("This change was generated by", "Claude Opus 4")):
            errors = self.findings(*lines)
            self.assertEqual(len(errors), 1, lines)
            self.assertIn("says a tool generated the text", errors[0])
        for lines in (("Written by Claude Dupont",), ("The table is created with the stock statement",), ("The index is generated", "with the script of the build"),
                      ("Authored by the maintainers",)):
            self.assertEqual(self.findings(*lines), [], lines)

    def test_a_link_to_a_session_is_refused(self):
        for line in (SESSION_LINK, SESSION_TRAILER, "Claude-Session: 01ABC", "See https://chatgpt.com/share/abc for the chat.",
                     "[the session](https://gemini.google.com/app/abc)", "https://github.com/copilot/c/abc",
                     "Assisted-by: Example Tool:example-model-4 https://claude.ai/chat/abc"):
            errors = self.findings(line)
            self.assertEqual(len(errors), 1, line)
            self.assertIn("links a session of an AI tool", errors[0])

    def test_another_link_or_the_word_session_passes(self):
        for line in ("See https://docs.github.com/copilot for the rules.", "https://github.com/copilot-extensions/example",
                     "Session: the client session is closed first.", "The session of the client is closed first.",
                     "https://claude.ai.example.org/code", "https://issues.apache.org/jira/browse/CASSANDRA-21319"):
            self.assertEqual(self.findings(line), [], line)

    def test_a_banner_is_refused(self):
        for line in (BANNER, "Generated by Example Tool", "> generated with ChatGPT", "\U0001F916 Generated with [Claude Code](https://claude.com/claude-code)",
                     "This text was generated by an AI assistant.", "The tests were generated with Copilot.", "Co-generated with Example Tool"):
            errors = self.findings(line)
            self.assertEqual(len(errors), 1, line)
            self.assertIn("says a tool generated the text", errors[0])

    def test_a_sentence_about_a_generated_file_passes(self):
        for line in ("The indexes are generated by doclint from each header.", "docs/index/graph.json is generated by docgraph.py.",
                     "It reads the generated indexes.", "A file generated by the build is not measured."):
            self.assertEqual(self.findings(line), [], line)

    def test_each_line_is_reported_once_and_shown_short(self):
        errors = subjectlint.check_attribution((AI_CO_AUTHOR + "\n") * 3 + "Generated by " + "x" * 300 + "\n")
        self.assertEqual(len(errors), 2)
        self.assertIn("x..." , errors[1])
        self.assertLess(len(errors[1]), 400)


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

    def test_the_branch_option_keeps_the_import_type_for_import_branches(self):
        args = ["title", "--repo", self.repo, "--rules", "line"]
        self.assertEqual(run(*(args + [IMPORTS[1]]))[0], 0)
        self.assertEqual(run(*(args + ["--branch", "import/cassandra-5.0.8/chronitondb-5.0", IMPORTS[1]]))[0], 0)
        for branch in ("", "agent/42-disk-check/chronitondb-5.0"):
            rc, out, err = run(*(args + ["--branch", branch, IMPORTS[1]]))
            self.assertEqual((rc, out), (1, "title failed\n"), branch)
            self.assertIn("title: the type 'import' is only for an import", err)

    def test_a_bad_title_fails(self):
        rc, out, err = self.title("Update build.xml")
        self.assertEqual(rc, 1)
        self.assertIn("title: the subject has the form", err)
        self.assertEqual(out, "title failed\n")

    def test_the_footer_is_read_from_the_pull_requests_commits(self):
        self.git("checkout", "-q", "-b", "work")
        self.commit("rename the version option\n\nBREAKING CHANGE: rename it in each script.")
        self.commit("answer the review")
        rc, _, err = run("title", "--repo", self.repo, "--rules", "line", "--commits", "line..work",
                         "feat(nodetool)!: rename the version option")
        self.assertEqual((rc, err), (0, ""))

    def test_a_footer_only_in_the_description_is_refused(self):
        self.git("checkout", "-q", "-b", "work")
        self.commit("rename the version option")
        path = os.path.join(self.repo, ".git", "body.txt")
        with open(path, "w", encoding="utf-8") as handle:
            handle.write("BREAKING CHANGE: rename it in each script.\n")
        rc, out, err = run("title", "--repo", self.repo, "--rules", "line", "--commits", "line..work", "--body", path,
                           "feat(nodetool)!: rename the version option")
        self.assertEqual(rc, 1)
        self.assertIn("title: the 'BREAKING CHANGE:' footer is only in the pull request description", err)
        self.assertIn("in a commit message of the pull request", err)

    def test_line_suffix_and_number_are_not_counted_on_the_line(self):
        start = self.git("rev-parse", "HEAD")
        self.commit("docs(process): fix records, kind labels, release rules and new templates (chronitondb-5.0) (#74)")
        rc, _, err = run("commits", "--repo", self.repo, "--rules", "line", "%s..line" % start)
        self.assertEqual((rc, err), (0, ""))

    def test_squash_and_merge_subjects_on_the_line(self):
        start = self.git("rev-parse", "HEAD")
        self.commit("feat(compaction): count a skipped sstable once (#121)")
        self.commit("feat(nodetool)!: rename the version option (#122)\n\nBREAKING CHANGE: rename it in each script.")
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
        bad = self.commit("Skipped sstable count (#124)")
        rc, out, err = run("commits", "--repo", self.repo, "--rules", "line", "%s..line" % start)
        self.assertEqual(rc, 1)
        self.assertIn("%s Skipped sstable count (#124): the subject has the form" % bad[:10], err)
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

    # Attribution, through the command.

    def work(self, *messages):
        self.git("checkout", "-q", "-b", "work")
        return [self.commit(message) for message in messages]

    def test_an_ai_co_author_in_a_commit_of_the_pull_request_is_refused(self):
        _, bad = self.work("count a skipped sstable once", "answer the review\n\n" + AI_CO_AUTHOR)
        rc, out, err = run("title", "--repo", self.repo, "--rules", "line", "--commits", "line..work", TITLES["feat"])
        self.assertEqual((rc, out), (1, "title failed\n"))
        self.assertEqual(err.count("\n"), 1)
        self.assertIn("commit %s: the line '%s' names an AI tool or model as a co-author" % (bad[:10], AI_CO_AUTHOR), err)

    def test_a_session_link_and_a_banner_in_the_description_are_refused(self):
        self.work("count a skipped sstable once")
        rc, out, err = self.title_with("What and why.\n\n" + BANNER + "\n\n" + SESSION_LINK + "\n")
        self.assertEqual((rc, out), (1, "title failed\n"))
        self.assertIn("description: the line '%s' says a tool generated the text" % BANNER, err)
        self.assertIn("description: the line '%s' links a session of an AI tool" % SESSION_LINK, err)

    def title_with(self, body, title=None, branch=None):
        path = os.path.join(self.repo, ".git", "body.txt")
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(body)
        more = ["--branch", branch] if branch is not None else []
        return run(*(["title", "--repo", self.repo, "--rules", "line", "--commits", "line..work", "--body", path] + more
                     + [title or TITLES["feat"]]))

    def test_the_allowed_trailers_pass(self):
        self.work("count a skipped sstable once\n\n" + "\n".join(ALLOWED))
        rc, out, err = self.title_with("What and why.\n\n" + "\n".join(ALLOWED) + "\n")
        self.assertEqual((rc, err, out), (0, "", "title passed\n"))

    def test_the_commits_of_an_import_keep_their_messages(self):
        self.work("Route 6.0 versions to the cassandra-6.0 job\n\npatch by someone for CASSANDRA-21319\n\n" + AI_CO_AUTHOR)
        rc, out, err = self.title_with("Reason: the line needs the fix now.\n", IMPORTS[0], "import/CASSANDRA-21319/chronitondb-5.0")
        self.assertEqual((rc, err), (0, ""))
        # The description of an import is the project's own text.
        rc, out, err = self.title_with(SESSION_LINK + "\n", IMPORTS[0], "import/CASSANDRA-21319/chronitondb-5.0")
        self.assertEqual(rc, 1)
        self.assertIn("description: the line", err)
        # The type import from any other branch is refused, so it lifts nothing.
        rc, out, err = self.title_with("Reason: none.\n", IMPORTS[0], "agent/42-disk-check/chronitondb-5.0")
        self.assertEqual(rc, 1)

    def test_a_commit_on_the_line_is_checked_for_attribution(self):
        start = self.git("rev-parse", "HEAD")
        bad = self.commit("feat(compaction): count a skipped sstable once (#121)\n\n* count it once\n\n" + SESSION_TRAILER)
        self.commit("import(apache-5.0.8): merge Apache Cassandra 5.0.8 (#122)\n\n" + BANNER)
        rc, out, err = run("commits", "--repo", self.repo, "--rules", "line", "%s..line" % start)
        self.assertEqual((rc, out), (1, "subjects 2 checked 2 failed\n"))
        self.assertIn("%s feat(compaction): count a skipped sstable once (#121): the line '%s' links a session" % (bad[:10], SESSION_TRAILER), err)
        self.assertIn("says a tool generated the text", err)

    def test_usage(self):
        self.assertEqual(run("title", "--repo", self.repo)[0], 2)
        self.assertEqual(run("lint")[0], 2)

    def test_missing_rules_fail(self):
        rc, _, err = run("title", "--repo", self.repo, "--rules", "no-such-ref", TITLES["feat"])
        self.assertEqual(rc, 1)
        self.assertIn("the subject rules cannot be read", err)


if __name__ == "__main__":
    unittest.main()
