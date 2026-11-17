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

    def record(self, path, name=None):
        self.put(path, RECORD % (name or os.path.basename(path)[:len("DEC-") + path.split("DEC-")[1].index("-", path.split("DEC-")[1].index("-") + 1)]))
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

    def test_history_write_refuses_a_document_with_nothing_to_start_from(self):
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


if __name__ == "__main__":
    unittest.main()
