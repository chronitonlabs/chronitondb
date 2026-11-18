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
"""Decision records, docs/decisions/README.md rule 1: a record new to the
line is named by its id in the place its key gives it, and a document that
can change carries its revision history with a link to its commits. Run
from the repository root:

    python3 -m unittest discover -s tools/chronitondb/test/doclint
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
import doclint  # noqa: E402
from markdown import Markdown  # noqa: E402

RECORD = """# %s. A decision

| Field | Value |
|---|---|
| Document type | Record (ISO/IEC/IEEE 15289), MADR |
| Status | Accepted |
| Date | 2026-11-17 |
| Deciders | The maintainers |
| References | Issue 61 |
| Areas | %s |
| Supersedes | %s |

## Context and problem statement

A question.

## Considered options

1. One
2. Two

## Decision outcome

Chosen option: "One", because it is first.

### Consequences

- Good: it is decided
- Bad: nothing

## More information

None.
"""

PLAN = """# Line plan: chronitondb-5.0

| Field | Value |
|---|---|
| Title | Line plan |
| Status | Draft |
| Version | %s |

%s

## Contents

- [1. Dates](#1-dates)

## 1. Dates

Not set.
"""

TEMPLATE = PLAN % ("{n}", """Revision history, one row for each version:

| Version | Date | Change | Decision record |
|---|---|---|---|
| 1 | {RFC 3339 date} | First version | {the id of the decision record behind this version, or None} |

Full history in git: [commits of this file]({the address})""")
TEMPLATE = TEMPLATE.replace("| Status | Draft |", "| Status | Draft, Approved or Superseded |")
OLD_LINE = "Change history: the git history of this file."
PATH = "docs/releases/chronitondb-5.0-plan.md"
LINK = "Full history in git: [commits of this file](https://github.com/example/product/commits/line/%s)" % PATH


def history(*rows):
    return "\n".join(["Revision history, one row for each version:", "", "| Version | Date | Change | Decision record |", "|---|---|---|---|"]
                     + ["| %s |" % " | ".join(row) for row in rows] + ["", LINK])


def run(*args):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = doclint.main(list(args))
    return rc, out.getvalue(), err.getvalue()


class Repo(unittest.TestCase):

    def setUp(self):
        self.repo = tempfile.mkdtemp()
        self.git("init", "-q")
        with open(os.path.join(ROOT, "docs", "decisions", "README.md"), encoding="utf-8") as handle:
            self.put("docs/decisions/README.md", handle.read())
        self.put("docs/process/templates/line-plan.md", TEMPLATE)
        with open(os.path.join(ROOT, "docs", "process", "areas.md"), encoding="utf-8") as handle:
            self.put("docs/process/areas.md", handle.read())

    def tearDown(self):
        shutil.rmtree(self.repo)

    def git(self, *args):
        subprocess.run(["git", "-C", self.repo, "-c", "user.name=t", "-c", "user.email=t@example.org",
                        "-c", "commit.gpgsign=false", "-c", "core.hooksPath=/dev/null"] + list(args),
                       check=True, capture_output=True)

    def put(self, path, text):
        full = os.path.join(self.repo, path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8") as handle:
            handle.write(text)

    def record(self, path, name=None, areas="project", supersedes="None"):
        own = os.path.basename(path)[:len("DEC-") + path.split("DEC-")[1].index("-", path.split("DEC-")[1].index("-") + 1)]
        self.put(path, RECORD % (name or own, areas, supersedes))
        run("index", "--write", os.path.join(self.repo, path))

    def line(self):
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "line")
        self.git("branch", "-f", "line")

    def document(self, *paths):
        return run("document", "--repo", self.repo, "--templates", "line", "--source", "worktree", *paths)


class Records(Repo):

    def test_where_a_record_lives_gives_its_type(self):
        for path in ("docs/design/VER-release-version/decisions/DEC-VER-0001-a-choice.md", "docs/design/42-a-fix/decisions/DEC-42-0001-a-choice.md",
                     "docs/decisions/DEC-GOV-0001-a-rule.md", "docs/decisions/0001-initial-maintainers.md"):
            self.assertEqual(doclint.doc_type(path, ""), "decision", path)
        self.assertIsNone(doclint.doc_type("docs/decisions/README.md", ""))

    def test_a_feature_record_in_its_feature_passes(self):
        self.line()
        path = "docs/design/VER-release-version/decisions/DEC-VER-0001-what-version-prints.md"
        self.record(path)
        self.assertEqual(self.document(path)[::2], (0, ""))

    def test_a_record_of_work_with_no_key_takes_its_issue_number(self):
        self.line()
        path = "docs/design/42-a-fix/decisions/DEC-42-0001-which-error.md"
        self.record(path)
        self.assertEqual(self.document(path)[::2], (0, ""))

    def test_a_number_of_more_than_four_digits_passes(self):
        self.record("docs/design/VER-release-version/decisions/DEC-VER-9999-the-last-of-four.md")
        self.line()
        path = "docs/design/VER-release-version/decisions/DEC-VER-10000-the-next.md"
        self.record(path)
        self.assertEqual(self.document(path)[::2], (0, ""))

    def test_a_record_under_another_features_key_fails(self):
        self.line()
        path = "docs/design/VER-release-version/decisions/DEC-CLD-0001-a-choice.md"
        self.record(path)
        rc, _, err = self.document(path)
        self.assertEqual(rc, 1)
        self.assertIn("with the key of its directory", err)

    def test_a_feature_record_in_the_project_folder_fails(self):
        self.line()
        path = "docs/decisions/DEC-VER-0001-a-choice.md"
        self.record(path)
        rc, _, err = self.document(path)
        self.assertEqual(rc, 1)
        self.assertIn("docs/decisions/DEC-GOV-nnnn-<slug>.md for a decision of the whole project", err)

    def test_the_title_opens_with_the_id(self):
        self.line()
        path = "docs/design/VER-release-version/decisions/DEC-VER-0001-a-choice.md"
        self.record(path, "DEC-VER-0002")
        rc, _, err = self.document(path)
        self.assertEqual(rc, 1)
        self.assertIn("the title of this record opens with its id: '# DEC-VER-0001. <Short title of the decision>'", err)

    def test_an_id_two_records_share_fails(self):
        self.line()
        paths = ["docs/design/VER-release-version/decisions/DEC-VER-0001-a-choice.md", "docs/design/VER-release-version/decisions/DEC-VER-0001-another-choice.md"]
        for path in paths:
            self.record(path)
        rc, _, err = self.document(*paths)
        self.assertEqual(rc, 1)
        self.assertIn("%s:1: the id DEC-VER-0001 is also the id of %s" % (paths[0], paths[1]), err)

    def test_numbers_are_counted_under_each_key(self):
        self.record("docs/design/VER-release-version/decisions/DEC-VER-0001-first.md")
        self.record("docs/design/VER-release-version/decisions/DEC-VER-0002-second.md")
        self.line()
        new = ["docs/design/VER-release-version/decisions/DEC-VER-0003-third.md", "docs/design/CLD-commitlog-disk-check/decisions/DEC-CLD-0001-first.md",
               "docs/decisions/DEC-GOV-0001-first.md"]
        for path in new:
            self.record(path)
        self.assertEqual(self.document(*new)[::2], (0, ""))

    def test_a_number_merged_under_the_key_is_not_taken_again(self):
        self.record("docs/design/VER-release-version/decisions/DEC-VER-0001-first.md")
        self.line()
        path = "docs/design/VER-release-version/decisions/DEC-VER-0003-third.md"
        self.record(path)
        rc, _, err = self.document(path)
        self.assertEqual(rc, 1)
        self.assertIn("after the highest merged one, DEC-VER-0001, DEC-VER-0002 here, and this one is DEC-VER-0003", err)

    def test_a_merged_record_is_held_to_no_later_rule(self):
        with open(os.path.join(ROOT, "docs", "decisions", "0001-initial-maintainers.md"), encoding="utf-8") as handle:
            self.put("docs/decisions/0001-initial-maintainers.md", handle.read())
        self.line()
        self.assertEqual(self.document("docs/decisions/0001-initial-maintainers.md")[::2], (0, ""))

    def test_a_record_is_superseded_by_an_id_or_an_old_number(self):
        allowed = doclint.allowed_statuses("Proposed, Accepted, or Superseded by DEC-<KEY>-nnnn")
        for value in ("Accepted", "Superseded by DEC-VER-0007", "Superseded by DEC-GOV-12345", "Superseded by DEC-42-0002", "Superseded by 0005"):
            self.assertTrue(doclint.status_ok(value, allowed), value)
        for value in ("Superseded", "Superseded by VER-7", "Superseded by DEC-VER-07"):
            self.assertFalse(doclint.status_ok(value, allowed), value)
        self.assertTrue(doclint.status_ok("Superseded by 0005", doclint.allowed_statuses("Proposed, Accepted, or Superseded by NNNN")))

    def test_no_feature_takes_the_key_of_the_project(self):
        self.put("docs/design/GOV-governance-view/feature-spec.md", "# Feature spec: x\n")
        self.line()
        errors = doclint.check_keys(self.repo, "line", "worktree")
        self.assertTrue(any("the key GOV is kept for the decision records of the whole project" in error for error in errors), errors)


class Revisions(Repo):

    def plan(self, version, block):
        self.put(PATH, PLAN % (version, block))

    def errors(self):
        return self.document(PATH)[::2]

    def test_a_new_document_with_its_history_passes(self):
        self.line()
        self.plan("1", history(("1", "2026-11-17", "First version", "None")))
        self.assertEqual(self.errors(), (0, ""))

    def test_a_new_document_without_it_fails(self):
        self.line()
        self.plan("1", OLD_LINE)
        rc, err = self.errors()
        self.assertEqual(rc, 1)
        self.assertIn("%s:1: no revision history table under the document control table" % PATH, err)

    def test_a_document_merged_before_the_table_keeps_its_old_line(self):
        self.plan("1", OLD_LINE)
        self.line()
        self.put(PATH, (PLAN % ("1", OLD_LINE)).replace("Not set.", "Set now."))
        self.assertEqual(self.errors(), (0, ""))

    def test_its_next_version_adds_the_table(self):
        self.plan("1", OLD_LINE)
        self.line()
        self.plan("2", OLD_LINE)
        rc, err = self.errors()
        self.assertEqual(rc, 1)
        self.assertIn("no revision history table", err)
        self.plan("2", history(("2", "2026-11-17", "The dates are set", "DEC-GOV-0001")))
        self.assertEqual(self.errors(), (0, ""))

    def test_a_template_without_the_table_asks_for_none(self):
        self.put("docs/process/templates/line-plan.md", TEMPLATE.split("Revision history")[0] + OLD_LINE + "\n\n## Contents" + TEMPLATE.split("## Contents")[1])
        self.line()
        self.plan("1", OLD_LINE)
        self.assertEqual(self.errors(), (0, ""))

    def test_rows_in_order_and_the_last_is_the_version(self):
        self.line()
        self.plan("3", history(("1", "2026-11-01", "First version", "None"), ("3", "2026-11-17", "The dates moved", "DEC-GOV-0002")))
        rc, err = self.errors()
        self.assertEqual(rc, 1)
        self.assertIn("in order with no gap: version 2 follows version 1", err)
        self.plan("3", history(("1", "2026-11-01", "First version", "None"), ("2", "2026-11-17", "The dates moved", "DEC-GOV-0002")))
        rc, err = self.errors()
        self.assertEqual(rc, 1)
        self.assertIn("the Version row says 3 and the last row of the revision history is version 2", err)

    def test_each_cell_of_a_row(self):
        self.line()
        self.plan("1", history(("one", "17 November", "{what changed in this version}", "see the task")))
        rc, err = self.errors()
        self.assertEqual(rc, 1)
        for reason in ("the Version of a revision history row is a whole number", "the Date of a revision history row is an RFC 3339 date",
                       "the Change of a revision history row says what changed", "the Decision record of a revision history row names the record"):
            self.assertIn(reason, err)

    def test_the_decision_record_cell(self):
        for cell in ("None", "DEC-VER-0003", "DEC-VER-0003, DEC-GOV-0001", "[DEC-VER-0003](decisions/DEC-VER-0003-a-choice.md)", "0005", "DEC-42-0001 and DEC-VER-12345"):
            self.assertTrue(doclint.RECORD_CELL.match(cell), cell)
        for cell in ("", "none yet", "DEC-VER-3", "the owner"):
            self.assertFalse(doclint.RECORD_CELL.match(cell), cell)

    def test_a_merged_row_is_never_changed(self):
        self.plan("1", history(("1", "2026-11-01", "First version", "None")))
        self.line()
        self.plan("2", history(("1", "2026-11-02", "First version, said better", "None"), ("2", "2026-11-17", "The dates moved", "DEC-GOV-0002")))
        rc, err = self.errors()
        self.assertEqual(rc, 1)
        self.assertIn("the revision history row of version 1 on the line is changed or gone", err)

    def test_the_link_is_the_file_on_its_line_in_the_lines_repository(self):
        self.git("remote", "add", "origin", "git@github.com:someone/renamed-product.git")
        self.line()
        self.git("update-ref", "refs/remotes/origin/chronitondb-5.0", "line")
        self.plan("1", history(("1", "2026-11-17", "First version", "None")))
        rc, _, err = run("document", "--repo", self.repo, "--templates", "origin/chronitondb-5.0", "--source", "worktree", PATH)
        self.assertEqual(rc, 1)
        self.assertIn("the history link is not the commits of this file on its line: 'Full history in git: [commits of this file](https://github.com/someone/renamed-product/commits/chronitondb-5.0/%s)'" % PATH, err)
        rc, out, _ = run("history", "--repo", self.repo, "--templates", "origin/chronitondb-5.0", "--write", PATH)
        self.assertEqual((rc, out), (0, "history %s written\n" % PATH))
        self.assertEqual(run("document", "--repo", self.repo, "--templates", "origin/chronitondb-5.0", "--source", "worktree", PATH)[::2], (0, ""))
        self.assertEqual(run("history", "--repo", self.repo, "--templates", "origin/chronitondb-5.0", "--write", PATH)[1], "history %s current\n" % PATH)

    def test_a_link_to_another_file_fails_with_no_remote_to_read(self):
        self.line()
        self.plan("1", history(("1", "2026-11-17", "First version", "None")).replace(PATH, "docs/releases/another-plan.md"))
        rc, err = self.errors()
        self.assertEqual(rc, 1)
        self.assertIn("the history link is not the commits of this file on GitHub", err)

    def test_history_write_starts_the_table_of_an_old_document(self):
        self.git("remote", "add", "origin", "https://github.com/someone/product.git")
        self.plan("2", OLD_LINE)
        self.line()
        rc, out, _ = run("history", "--repo", self.repo, "--templates", "line", "--write", PATH)
        self.assertEqual((rc, out), (0, "history %s written\n" % PATH))
        with open(os.path.join(self.repo, PATH), encoding="utf-8") as handle:
            text = handle.read()
        self.assertNotIn(OLD_LINE, text)
        self.assertRegex(text, r"\| 2 \| [0-9]{4}-[0-9]{2}-[0-9]{2} \| \{what changed in this version\} \| \{the id of the decision record behind it, or None\} \|")
        self.assertIn("Full history in git: [commits of this file](https://github.com/someone/product/commits/line/%s)" % PATH, text)
        rc, _, err = run("history", "--repo", self.repo, "--templates", "line", "--check", PATH)
        self.assertEqual(rc, 1)
        self.assertIn("the Change of a revision history row says what changed", err)

    def test_history_write_refuses_a_clone_with_no_remote(self):
        self.line()
        self.plan("1", history(("1", "2026-11-17", "First version", "None")))
        rc, _, err = run("history", "--repo", self.repo, "--templates", "line", "--write", PATH)
        self.assertEqual(rc, 1)
        self.assertIn("the clone has no GitHub remote for line to build the link from", err)
        self.plan("1", history(("1", "2026-11-17", "First version", "None")).replace("example/product", "<owner>/<repository>"))
        self.assertIn("the history link is not the commits of this file on GitHub", self.errors()[1])

    def test_history_write_refuses_a_document_with_nothing_to_start_from(self):
        self.git("remote", "add", "origin", "https://github.com/someone/product.git")
        self.line()
        self.plan("1", "No history line here.")
        rc, _, err = run("history", "--repo", self.repo, "--templates", "line", "--write", PATH)
        self.assertEqual(rc, 1)
        self.assertIn("so there is nothing to write", err)

    def test_every_template_with_a_version_has_the_history(self):
        templates = os.path.join(ROOT, "docs", "process", "templates")
        for name in sorted(os.listdir(templates)):
            with open(os.path.join(templates, name), encoding="utf-8") as handle:
                text = handle.read()
            doc = Markdown(name, text)
            fields, _ = doclint.control_table(doc)
            with self.subTest(template=name):
                self.assertEqual(bool(fields and "Version" in fields), doclint.revision_rows(doc)[0] is not None)
                self.assertNotIn(OLD_LINE, text)
                if fields and "Version" in fields:
                    self.assertEqual(doclint.history_line(doc)[0] is not None, True)

    def test_the_decision_record_template_has_no_version(self):
        with open(os.path.join(ROOT, "docs", "decisions", "README.md"), encoding="utf-8") as handle:
            template = doclint.decision_template(handle.read())
        fields, _ = doclint.control_table(Markdown("record", template))
        self.assertNotIn("Version", fields)
        self.assertIsNone(doclint.revision_rows(Markdown("record", template))[0])


class Areas(Repo):

    VER = "docs/design/VER-release-version/decisions/DEC-VER-%s.md"

    def test_the_areas_and_sources_are_read_from_the_page(self):
        self.line()
        areas = doclint.areas_at(self.repo, "line")
        self.assertIn("search", areas)
        self.assertIn("project", areas)
        self.assertEqual(len(areas), len(set(areas)))
        self.assertEqual(doclint.names_at(self.repo, "line", "The sources"), ["original", "apache-cherry-pick", "apache-merge", "third-party"])

    def test_a_word_that_is_no_area_fails(self):
        self.line()
        path = self.VER % "0001-a-choice"
        self.record(path, areas="storage, performance")
        rc, _, err = self.document(path)
        self.assertEqual(rc, 1)
        self.assertIn("'performance' is not an area. The Areas row names one or more of cql, client-protocol", err)

    def test_several_areas_pass_and_one_twice_fails(self):
        self.line()
        path = self.VER % "0001-a-choice"
        self.record(path, areas="storage, `observability`")
        self.assertEqual(self.document(path)[::2], (0, ""))
        self.record(path, areas="storage, storage")
        self.assertIn("names an area twice", self.document(path)[2])

    def test_a_new_record_without_the_row_fails_and_a_merged_one_keeps_none(self):
        text = (RECORD % ("DEC-VER-0001", "x", "y")).replace("| Areas | x |\n| Supersedes | y |\n", "")
        merged, new = self.VER % "0001-merged", self.VER % "0002-new"
        self.put(merged, text)
        run("index", "--write", os.path.join(self.repo, merged))
        self.line()
        self.put(merged, open(os.path.join(self.repo, merged), encoding="utf-8").read().replace("| Status | Accepted |", "| Status | Superseded by DEC-VER-0002 |"))
        self.record(new, supersedes="DEC-VER-0001")
        self.assertEqual(self.document(merged, new)[::2], (0, ""))
        self.put(new, text.replace("DEC-VER-0001", "DEC-VER-0002"))
        run("index", "--write", os.path.join(self.repo, new))
        rc, _, err = self.document(new)
        self.assertEqual(rc, 1)
        self.assertIn("the document control table has no 'Areas' row", err)
        self.assertIn("the document control table has no 'Supersedes' row", err)

    def test_a_document_keeps_no_late_row_until_its_next_version(self):
        template = TEMPLATE.replace("| Version | {n} |", "| Version | {n} |\n| Areas | {areas} |")
        self.put(PATH, PLAN % ("1", history(("1", "2026-11-01", "First version", "None"))))
        self.put("docs/process/templates/line-plan.md", template)
        self.line()
        self.assertEqual(self.document(PATH)[::2], (0, ""))
        self.put(PATH, PLAN % ("2", history(("1", "2026-11-01", "First version", "None"), ("2", "2026-11-17", "The dates moved", "None"))))
        rc, _, err = self.document(PATH)
        self.assertEqual(rc, 1)
        self.assertIn("the document control table has no 'Areas' row", err)

    def test_a_source_that_is_not_on_the_list_fails(self):
        template = TEMPLATE.replace("| Version | {n} |", "| Version | {n} |\n| Source | {source} |")
        self.put("docs/process/templates/line-plan.md", template)
        self.line()
        good = (PLAN % ("1", history(("1", "2026-11-17", "First version", "None")))).replace("| Version | 1 |", "| Version | 1 |\n| Source | apache-merge |")
        self.put(PATH, good)
        self.assertEqual(self.document(PATH)[::2], (0, ""))
        self.put(PATH, good.replace("apache-merge", "backport"))
        rc, _, err = self.document(PATH)
        self.assertEqual(rc, 1)
        self.assertIn("'backport' is not a source. The Source row names one of original, apache-cherry-pick, apache-merge, third-party", err)


class Exceptions(Repo):
    """The Exceptions row of a design record or fix record: None, or the
    ids of the principles the record departs from, each one a principle of
    the page on the line."""

    ROW = "| Version | 1 |\n| Exceptions | %s |"

    def setUp(self):
        super().setUp()
        with open(os.path.join(ROOT, "docs", "process", "principles.md"), encoding="utf-8") as handle:
            self.put("docs/process/principles.md", handle.read())
        self.put("docs/process/templates/line-plan.md", TEMPLATE.replace("| Version | {n} |", "| Version | {n} |\n| Exceptions | {None, or ids} |"))
        self.line()

    def plan(self, value):
        self.put(PATH, (PLAN % ("1", history(("1", "2026-11-18", "First version", "None")))).replace("| Version | 1 |", self.ROW % value))
        return self.document(PATH)

    def test_the_principles_are_read_from_the_page(self):
        known = doclint.principles_at(self.repo, "line")
        self.assertIn("PRINCIPLE-001", known)
        self.assertIn("PRINCIPLE-081", known)
        self.assertEqual(len(known), len(set(known)))

    def test_none_and_ids_of_the_page_pass(self):
        self.assertEqual(self.plan("None")[::2], (0, ""))
        self.assertEqual(self.plan("PRINCIPLE-016")[::2], (0, ""))
        self.assertEqual(self.plan("PRINCIPLE-016, `PRINCIPLE-051`")[::2], (0, ""))
        self.assertEqual(self.plan("[PRINCIPLE-016](../process/principles.md#principle-016), PRINCIPLE-051")[::2], (0, ""))

    def test_an_id_the_page_does_not_state_fails(self):
        for name in ("PRINCIPLE-999", "PRINCIPLE-038"):
            rc, _, err = self.plan("PRINCIPLE-016, %s" % name)
            self.assertEqual(rc, 1)
            self.assertIn("%s is not a principle of docs/process/principles.md on line" % name, err)
            self.assertNotIn("PRINCIPLE-016 is not", err)

    def test_a_word_that_is_no_id_fails(self):
        for word in ("none", "Yes", "16", "PRINCIPLE-16", "DEC-GOV-0001"):
            rc, _, err = self.plan(word)
            self.assertEqual(rc, 1, word)
            self.assertIn("'%s' is not the id of a principle. The Exceptions row names each principle this record departs from by its id, such as PRINCIPLE-016, joined by commas, or says None" % word, err)
        rc, _, err = self.plan("None, PRINCIPLE-016")
        self.assertEqual(rc, 1)
        self.assertIn("'None' is not the id of a principle", err)

    def test_a_principle_named_twice_fails(self):
        rc, _, err = self.plan("PRINCIPLE-016, PRINCIPLE-016")
        self.assertEqual(rc, 1)
        self.assertIn("the Exceptions row names a principle twice", err)

    def test_an_empty_row_fails(self):
        rc, _, err = self.plan("{None, or ids}")
        self.assertEqual(rc, 1)
        self.assertIn("the 'Exceptions' row of the document control table is not filled in", err)

    def test_a_line_with_no_principles_page_cannot_check_an_id(self):
        os.remove(os.path.join(self.repo, "docs/process/principles.md"))
        self.line()
        self.assertEqual(self.plan("None")[::2], (0, ""))
        rc, _, err = self.plan("PRINCIPLE-016")
        self.assertEqual(rc, 1)
        self.assertIn("no principles at docs/process/principles.md on line, so the Exceptions row cannot be checked", err)

    def test_a_document_merged_before_the_row_keeps_none_until_its_next_version(self):
        self.put(PATH, PLAN % ("1", history(("1", "2026-11-01", "First version", "None"))))
        self.line()
        self.assertEqual(self.document(PATH)[::2], (0, ""))
        self.put(PATH, PLAN % ("2", history(("1", "2026-11-01", "First version", "None"), ("2", "2026-11-18", "The dates moved", "None"))))
        rc, _, err = self.document(PATH)
        self.assertEqual(rc, 1)
        self.assertIn("the document control table has no 'Exceptions' row", err)

    def test_a_new_document_without_the_row_fails(self):
        self.put(PATH, PLAN % ("1", history(("1", "2026-11-18", "First version", "None"))))
        rc, _, err = self.document(PATH)
        self.assertEqual(rc, 1)
        self.assertIn("the document control table has no 'Exceptions' row", err)

    def test_the_record_templates_carry_the_row(self):
        for name in ("design-record.md", "fix-record.md"):
            with open(os.path.join(ROOT, "docs", "process", "templates", name), encoding="utf-8") as handle:
                fields, _ = doclint.control_table(Markdown(name, handle.read()))
            with self.subTest(template=name):
                self.assertIn("Exceptions", fields)
                self.assertTrue(fields["Exceptions"][0].startswith("{None, or"))


class Supersedes(Repo):

    OLD = "docs/design/VER-release-version/decisions/DEC-VER-0001-first.md"
    NEW = "docs/design/VER-release-version/decisions/DEC-VER-0002-second.md"

    def merged_first(self):
        self.record(self.OLD)
        self.line()

    def status(self, path, value):
        full = os.path.join(self.repo, path)
        with open(full, encoding="utf-8") as handle:
            text = handle.read()
        self.put(path, text.replace("| Status | Accepted |", "| Status | %s |" % value))

    def test_both_links_in_one_change_pass(self):
        self.merged_first()
        self.record(self.NEW, supersedes="DEC-VER-0001")
        self.status(self.OLD, "Superseded by DEC-VER-0002")
        self.assertEqual(self.document(self.OLD, self.NEW)[::2], (0, ""))

    def test_a_new_record_whose_old_one_does_not_say_so_fails(self):
        self.merged_first()
        self.record(self.NEW, supersedes="DEC-VER-0001")
        rc, _, err = self.document(self.NEW)
        self.assertEqual(rc, 1)
        self.assertIn("this record supersedes DEC-VER-0001, and the Status of %s is 'Accepted'. It becomes 'Superseded by DEC-VER-0002' in the same pull request" % self.OLD, err)

    def test_an_old_record_whose_new_one_does_not_name_it_fails(self):
        self.merged_first()
        self.record(self.NEW)
        self.status(self.OLD, "Superseded by DEC-VER-0002")
        rc, _, err = self.document(self.OLD)
        self.assertEqual(rc, 1)
        self.assertIn("the Status says this record is superseded by DEC-VER-0002, and the Supersedes row of %s does not name DEC-VER-0001" % self.NEW, err)

    def test_a_record_that_is_not_there_fails_both_ways(self):
        self.merged_first()
        self.record(self.NEW, supersedes="DEC-VER-0007")
        self.assertIn("this record supersedes DEC-VER-0007, and there is no such record", self.document(self.NEW)[2])
        self.status(self.OLD, "Superseded by DEC-VER-0009")
        self.assertIn("the Status names DEC-VER-0009, and there is no such record", self.document(self.OLD)[2])

    def test_a_record_merged_before_ids_is_superseded_by_its_number(self):
        with open(os.path.join(ROOT, "docs", "decisions", "0001-initial-maintainers.md"), encoding="utf-8") as handle:
            self.put("docs/decisions/0001-initial-maintainers.md", handle.read())
        self.line()
        new = "docs/decisions/DEC-GOV-0001-new-maintainers.md"
        self.record(new, supersedes="0001")
        self.status("docs/decisions/0001-initial-maintainers.md", "Superseded by DEC-GOV-0001")
        self.assertEqual(self.document("docs/decisions/0001-initial-maintainers.md", new)[::2], (0, ""))

    def test_the_row_says_none_or_ids(self):
        self.merged_first()
        self.record(self.NEW, supersedes="the earlier one")
        self.assertIn("the Supersedes row names each record this one replaces by its id", self.document(self.NEW)[2])


class Indexes(Repo):

    SPEC = """# Feature spec: Release version

| Field | Value |
|---|---|
| Title | Release version |
| Document type | Specification and description (ISO/IEC/IEEE 15289) |
| Status | Approved |
| Version | 2 |
| Areas | tools, observability |
"""
    IMPORT = """# Import: CASSANDRA-19999 into chronitondb-5.0

| Field | Value |
|---|---|
| Title | Import of CASSANDRA-19999 into chronitondb-5.0 |
| Document type | Record (ISO/IEC/IEEE 15289) |
| Status | Approved |
| Version | 1 |
| References | Issue #9. Apache commit `0123456789ab`, CASSANDRA-19998. |
| Areas | storage |
| Source | apache-cherry-pick |
"""
    DESIGN = """# Design: #70 The reader

| Field | Value |
|---|---|
| Title | The reader |
| Document type | Specification and description at item level (ISO/IEC/IEEE 15289) |
| Status | Draft |
| Version | 1 |
| Areas | tools |

## Requirements

- REQ-VER-001: The reader MUST read the key. Source: issue.
"""

    def tree(self):
        self.put("docs/design/VER-release-version/feature-spec.md", self.SPEC)
        self.put("docs/design/70-the-reader/design-record.md", self.DESIGN)
        self.put("docs/imports/cassandra-19999.md", self.IMPORT)
        self.put("docs/notes.md", "# Notes\n\nNo header here.\n")
        self.record("docs/design/VER-release-version/decisions/DEC-VER-0001-first.md", areas="tools")
        self.record("docs/decisions/DEC-GOV-0001-a-rule.md")
        self.line()

    def indexes(self, *more):
        return run("indexes", "--repo", self.repo, "--templates", "line", "--source", "worktree", *more)

    def read(self, path):
        with open(os.path.join(self.repo, path), encoding="utf-8") as handle:
            return handle.read()

    def test_missing_indexes_fail_and_write_puts_them_in(self):
        self.tree()
        rc, out, err = self.indexes()
        self.assertEqual(rc, 1)
        self.assertIn("docs/index/areas.md:0: is not the index the documents give now", err)
        self.assertIn("indexes 4 pages 4 stale", out)
        rc, out, _ = self.indexes("--write")
        self.assertEqual(rc, 0)
        self.assertIn("indexes 4 pages 4 written", out)
        self.assertEqual(self.indexes()[::2], (0, ""))
        self.assertIn("indexes 4 pages 0 written", self.indexes("--write")[1])

    def test_every_kind_is_listed_from_its_header(self):
        self.tree()
        self.indexes("--write")
        documents = self.read("docs/index/documents.md")
        self.assertIn("## Feature spec\n\n| Document | Status | Version | Areas |\n|---|---|---|---|\n| [Release version](../design/VER-release-version/feature-spec.md) | Approved | 2 | `tools`, `observability` |", documents)
        self.assertIn("| [CASSANDRA-19999 into chronitondb-5.0](../imports/cassandra-19999.md) | chronitondb-5.0 | apache-cherry-pick | CASSANDRA-19998, CASSANDRA-19999 | `0123456789ab` | Approved | 1 | `storage` |", documents)
        self.assertNotIn("notes.md", documents)
        self.assertLess(documents.index("## Feature spec"), documents.index("## Design record"))
        self.assertLess(documents.index("## Design record"), documents.index("## Import record"))

    def test_the_decisions_page_lists_every_record_by_key_and_number(self):
        self.tree()
        self.indexes("--write")
        decisions = self.read("docs/index/decisions.md")
        self.assertIn("| [DEC-GOV-0001](../decisions/DEC-GOV-0001-a-rule.md) | A decision |  | Accepted | 2026-11-17 | `project` | None |", decisions)
        self.assertIn("| [DEC-VER-0001](../design/VER-release-version/decisions/DEC-VER-0001-first.md) | A decision | `VER-release-version` | Accepted | 2026-11-17 | `tools` | None |", decisions)
        self.assertLess(decisions.index("DEC-GOV-0001"), decisions.index("DEC-VER-0001"))

    def test_the_area_page_lists_a_document_under_each_of_its_areas(self):
        self.tree()
        self.indexes("--write")
        areas = self.read("docs/index/areas.md")
        tools = areas[areas.index("## `tools`"):areas.index("## `build-and-test`")]
        for name in ("feature-spec.md", "design-record.md", "DEC-VER-0001-first.md"):
            self.assertIn(name, tools)
        self.assertNotIn("cassandra-19999.md", tools)
        self.assertIn("feature-spec.md", areas[areas.index("## `observability`"):areas.index("## `configuration`")])
        self.assertIn("## `cql`\n\nNone.", areas)
        self.assertIn("## Documents with no Areas row", areas)

    def test_a_feature_page_lists_its_documents_its_items_and_its_records(self):
        self.tree()
        self.indexes("--write")
        feature = self.read("docs/design/VER-release-version/INDEX.md")
        self.assertIn("| [Release version](feature-spec.md) | Feature spec | Approved | 2 | `tools`, `observability` |", feature)
        self.assertIn("| [#70 The reader](../70-the-reader/design-record.md) | Design record | Draft | 1 | `tools` |", feature)
        self.assertIn("| [DEC-VER-0001](decisions/DEC-VER-0001-first.md) | A decision | Accepted | 2026-11-17 | `tools` | None |", feature)
        self.assertFalse(os.path.exists(os.path.join(self.repo, "docs/design/70-the-reader/INDEX.md")))

    def test_a_changed_header_makes_the_index_stale(self):
        self.tree()
        self.indexes("--write")
        self.put("docs/design/VER-release-version/feature-spec.md", self.SPEC.replace("| Version | 2 |", "| Version | 3 |"))
        rc, _, err = self.indexes()
        self.assertEqual(rc, 1)
        self.assertIn("docs/index/documents.md:0: is not the index the documents give now", err)
        self.assertIn("docs/design/VER-release-version/INDEX.md:0:", err)

    def test_a_record_with_an_exception_is_listed_under_each_principle(self):
        self.tree()
        self.indexes("--write")
        self.assertNotIn("Exceptions to principles", self.read("docs/index/documents.md"))
        self.put("docs/design/70-the-reader/design-record.md", self.DESIGN.replace("| Areas | tools |", "| Areas | tools |\n| Exceptions | PRINCIPLE-051, [PRINCIPLE-016](../../process/principles.md#principle-016) |"))
        self.put("docs/design/71-the-writer/design-record.md", self.DESIGN.replace("#70 The reader", "#71 The writer").replace("REQ-VER-001", "REQ-VER-002").replace("| Areas | tools |", "| Areas | tools |\n| Exceptions | None |"))
        self.put("docs/design/72-the-fault/fix-record.md", self.DESIGN.replace("# Design: #70 The reader", "# Fix: #72 The fault").replace("REQ-VER-001", "REQ-1").replace("| Areas | tools |", "| Areas | tools |\n| Exceptions | PRINCIPLE-016 |"))
        rc, _, err = self.indexes()
        self.assertEqual(rc, 1)
        self.assertIn("docs/index/documents.md:0: is not the index the documents give now", err)
        self.indexes("--write")
        documents = self.read("docs/index/documents.md")
        section = documents[documents.index("## Exceptions to principles"):]
        self.assertIn("| Principle | Record | Kind | Status | Version |\n|---|---|---|---|---|\n"
                      "| [PRINCIPLE-016](../process/principles.md#principle-016) | [#70 The reader](../design/70-the-reader/design-record.md) | Design record | Draft | 1 |\n"
                      "| [PRINCIPLE-016](../process/principles.md#principle-016) | [#72 The fault](../design/72-the-fault/fix-record.md) | Fix record | Draft | 1 |\n"
                      "| [PRINCIPLE-051](../process/principles.md#principle-051) | [#70 The reader](../design/70-the-reader/design-record.md) | Design record | Draft | 1 |\n", section)
        self.assertNotIn("The writer", section)
        self.assertLess(documents.index("## Fix record"), documents.index("## Exceptions to principles"))
        self.assertEqual(self.indexes()[::2], (0, ""))

    def test_an_index_page_is_no_document(self):
        self.tree()
        self.indexes("--write")
        for path in ("docs/index/areas.md", "docs/design/VER-release-version/INDEX.md"):
            self.assertIsNone(doclint.doc_type(path, self.read(path)))
        self.assertNotIn("INDEX.md", self.read("docs/index/documents.md"))


if __name__ == "__main__":
    unittest.main()
