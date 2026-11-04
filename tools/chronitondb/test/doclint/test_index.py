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
"""The Contents index of doclint.py: GitHub's anchors, the index check of
the document subcommand, and the index subcommand that prints, writes and
checks it. Run from the repository root:

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

TEMPLATE = """# Delta: {short name}

| Field | Value |
|---|---|
| Title | {short name} |
| Status | Current or Dropped |

Change history: the git history of this file.

## Contents

- [Header](#header)
- [What](#what)

## Header

{The fields.}

## What

{What we carry.}
"""

GOOD = """# Delta: Actions pinned

| Field | Value |
|---|---|
| Title | Actions pinned |
| Status | Current |

Change history: the git history of this file.

## Contents

- [Header](#header)
  - [Fields](#fields)
- [What](#what)

## Header

The fields.

### Fields

None.

## What

Every action is pinned.
"""


def check(text, path="docs/x.md"):
    doc = Markdown(path, text)
    doclint.check_index(doc, path)
    return doc.errors


def run(*args):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = doclint.main(list(args))
    return rc, out.getvalue(), err.getvalue()


class Anchors(unittest.TestCase):

    def anchors_of(self, text):
        return [anchor for _, _, _, anchor in doclint.anchors(Markdown("x.md", text))]

    def test_lower_case_and_spaces_to_hyphens(self):
        self.assertEqual(doclint.slug("Stock hook points"), "stock-hook-points")

    def test_punctuation_removed_hyphens_kept(self):
        self.assertEqual(doclint.slug("2.1 Context and scope"), "21-context-and-scope")
        self.assertEqual(doclint.slug("Requirement quality checklist (ISO/IEC/IEEE 29148)"), "requirement-quality-checklist-isoiecieee-29148")
        self.assertEqual(doclint.slug("6.1 On-disk format changes"), "61-on-disk-format-changes")
        self.assertEqual(doclint.slug("Item {n}: {title}"), "item-n-title")

    def test_each_space_is_a_hyphen(self):
        self.assertEqual(doclint.slug("a  b - c"), "a--b---c")

    def test_inline_markup_is_read_as_text(self):
        self.assertEqual(doclint.slug("Process documents: `doclint.py`"), "process-documents-doclintpy")
        self.assertEqual(doclint.slug("The **bold** and _soft_ words"), "the-bold-and-soft-words")
        self.assertEqual(doclint.slug("See [the register](README.md)"), "see-the-register")
        self.assertEqual(doclint.slug("Keep `snake_case` names"), "keep-snake_case-names")

    def test_escaped_and_bare_underscores_are_kept(self):
        # GitHub shows max_threads, _private, "Use _ as a placeholder" and
        # chronitondb_ as written: none of these underscores is emphasis.
        self.assertEqual(doclint.slug("max\\_threads"), "max_threads")
        self.assertEqual(doclint.slug("_private"), "_private")
        self.assertEqual(doclint.slug("Use _ as a placeholder"), "use-_-as-a-placeholder")
        self.assertEqual(doclint.slug("The prefix chronitondb_ and more"), "the-prefix-chronitondb_-and-more")
        self.assertEqual(doclint.slug("A lone _"), "a-lone-_")

    def test_other_escapes_are_their_character(self):
        self.assertEqual(doclint.rendered("Escaped \\`tick\\` and \\*star\\*"), "Escaped `tick` and *star*")
        self.assertEqual(doclint.slug("Escaped \\`tick\\` and \\*star\\*"), "escaped-tick-and-star")

    def test_a_reference_link_is_its_text(self):
        self.assertEqual(doclint.slug("See [x][ref]"), "see-x")
        self.assertEqual(doclint.slug("See [x][]"), "see-x")

    def test_an_html_entity_is_its_character(self):
        self.assertEqual(doclint.rendered("Q&amp;A"), "Q&A")
        self.assertEqual(doclint.slug("Q&amp;A"), "qa")
        self.assertEqual(doclint.slug("Keep `&amp;` literal"), "keep-amp-literal")

    def test_an_image_shows_no_text(self):
        self.assertEqual(doclint.slug("Link [a](http://x) and ![img](y.png)"), "link-a-and-")

    def test_brackets_in_a_code_span(self):
        self.assertEqual(doclint.slug("The `a[0]` value"), "the-a0-value")
        self.assertEqual(doclint.link_text("The `a[0]` value"), "The `a[0]` value")
        self.assertEqual(doclint.link_text("The [a] and `b[1]`"), "The \\[a\\] and `b[1]`")
        self.assertEqual(doclint.link_text("See [x](y) and [z][ref]"), "See x and z")

    def test_duplicates_are_numbered(self):
        text = "# T\n\n## Notes\n\n## Notes\n\n### Notes\n"
        self.assertEqual(self.anchors_of(text), ["t", "notes", "notes-1", "notes-2"])

    def test_a_numbered_anchor_already_taken_is_skipped(self):
        text = "# T\n\n## A\n\n## A 1\n\n## A\n"
        self.assertEqual(self.anchors_of(text), ["t", "a", "a-1", "a-2"])

    def test_headings_in_fences_and_comments_have_no_anchor(self):
        text = "# T\n\n```\n## Not a heading\n```\n\n<!--\n## Hidden\n-->\n\n## Real\n"
        self.assertEqual(self.anchors_of(text), ["t", "real"])


class IndexCheck(unittest.TestCase):

    def test_a_correct_index_passes(self):
        self.assertEqual(check(GOOD), [])

    def test_no_contents_section_fails(self):
        text = GOOD.replace("## Contents\n\n- [Header](#header)\n  - [Fields](#fields)\n- [What](#what)\n\n", "")
        errors = check(text)
        self.assertEqual(len(errors), 1)
        self.assertIn("no '## Contents' section", errors[0])
        self.assertIn("doclint.py index --write docs/x.md", errors[0])

    def test_a_heading_missing_from_the_index_fails(self):
        errors = check(GOOD.replace("  - [Fields](#fields)\n", ""))
        self.assertEqual(len(errors), 1)
        self.assertIn("the heading 'Fields' on line 19 is not in the index, as [Fields](#fields)", errors[0])

    def test_a_link_to_no_heading_fails(self):
        errors = check(GOOD.replace("- [What](#what)", "- [What](#what)\n- [Why](#why)"))
        self.assertEqual(len(errors), 1)
        self.assertIn("the index links #why, and no heading of this file has that anchor", errors[0])

    def test_a_stale_anchor_after_a_rename_fails(self):
        errors = check(GOOD.replace("## What\n", "## What we carry\n"))
        self.assertTrue(any("links #what, and no heading" in e for e in errors), errors)
        self.assertTrue(any("'What we carry' on line 24 is not in the index" in e for e in errors), errors)

    def test_the_title_listed_fails(self):
        errors = check(GOOD.replace("- [Header](#header)", "- [Delta: Actions pinned](#delta-actions-pinned)\n- [Header](#header)"))
        self.assertEqual(len(errors), 1)
        self.assertIn("links #delta-actions-pinned, the title, which the index leaves out", errors[0])

    def test_a_heading_listed_twice_fails(self):
        errors = check(GOOD.replace("- [What](#what)", "- [What](#what)\n- [What](#what)"))
        self.assertEqual(len(errors), 1)
        self.assertIn("lists #what twice", errors[0])

    def test_wrong_depth_fails(self):
        errors = check(GOOD.replace("  - [Fields](#fields)", "- [Fields](#fields)"))
        self.assertEqual(len(errors), 1)
        self.assertIn("'Fields' is indented 0 spaces. It is indented 2, two spaces more than the nearest heading above it of a higher level", errors[0])

    def test_a_skipped_level_is_one_step_below_its_parent(self):
        text = "# T\n\n## Contents\n\n- [A](#a)\n  - [Deep](#deep)\n    - [Deeper](#deeper)\n  - [B](#b)\n- [C](#c)\n\n## A\n\n##### Deep\n\n###### Deeper\n\n### B\n\n## C\n"
        self.assertEqual(check(text), [])
        errors = check(text.replace("  - [Deep](#deep)", "      - [Deep](#deep)"))
        self.assertEqual(len(errors), 1)
        self.assertIn("'Deep' is indented 6 spaces. It is indented 2", errors[0])
        doc = Markdown("x.md", text)
        self.assertEqual(doclint.index_section(doc)[2:], ["- [A](#a)", "  - [Deep](#deep)", "    - [Deeper](#deeper)", "  - [B](#b)", "- [C](#c)"])

    def test_out_of_order_fails(self):
        text = GOOD.replace("- [Header](#header)\n  - [Fields](#fields)\n- [What](#what)", "- [What](#what)\n- [Header](#header)\n  - [Fields](#fields)")
        errors = check(text)
        self.assertEqual(len(errors), 1)
        self.assertIn("lists #what out of the headings' order", errors[0])

    def test_text_that_is_not_the_heading_fails(self):
        errors = check(GOOD.replace("- [What](#what)", "- [The change](#what)"))
        self.assertEqual(len(errors), 1)
        self.assertIn("#what shows 'The change', its heading reads 'What'", errors[0])

    def test_other_text_in_the_section_fails(self):
        errors = check(GOOD.replace("## Contents\n\n", "## Contents\n\nThe sections:\n\n"))
        self.assertEqual(len(errors), 1)
        self.assertIn("holds only its list of links", errors[0])

    def test_contents_after_another_section_fails(self):
        text = GOOD.replace("## Contents\n\n- [Header](#header)\n  - [Fields](#fields)\n- [What](#what)\n\n", "")
        text = text.replace("## What\n", "## Contents\n\n- [Header](#header)\n  - [Fields](#fields)\n- [What](#what)\n\n## What\n")
        errors = check(text)
        self.assertEqual(len(errors), 1)
        self.assertIn("the '## Contents' section comes after '## Header'", errors[0])

    def test_duplicate_headings_link_their_numbered_anchors(self):
        text = "# T\n\n## Contents\n\n- [Notes](#notes)\n- [Notes](#notes-1)\n\n## Notes\n\n## Notes\n"
        self.assertEqual(check(text), [])
        errors = check(text.replace("(#notes-1)", "(#notes)"))
        self.assertTrue(any("lists #notes twice" in e for e in errors), errors)
        self.assertTrue(any("is not in the index, as [Notes](#notes-1)" in e for e in errors), errors)


class IndexCommand(unittest.TestCase):

    def setUp(self):
        self.dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.dir)

    def write(self, name, text):
        path = os.path.join(self.dir, name)
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(text)
        return path

    def read(self, path):
        with open(path, encoding="utf-8") as handle:
            return handle.read()

    def without_contents(self):
        return GOOD.replace("## Contents\n\n- [Header](#header)\n  - [Fields](#fields)\n- [What](#what)\n\n", "")

    def test_print(self):
        path = self.write("a.md", self.without_contents())
        rc, out, _ = run("index", path)
        self.assertEqual(rc, 0)
        self.assertEqual(out, "## Contents\n\n- [Header](#header)\n  - [Fields](#fields)\n- [What](#what)\n")

    def test_write_inserts_before_the_first_section(self):
        path = self.write("a.md", self.without_contents())
        rc, out, _ = run("index", "--write", path)
        self.assertEqual(rc, 0)
        self.assertIn("written", out)
        self.assertEqual(self.read(path), GOOD)

    def test_write_replaces_a_stale_index_and_is_stable(self):
        path = self.write("a.md", GOOD.replace("## What\n", "## What we carry\n"))
        run("index", "--write", path)
        text = self.read(path)
        self.assertIn("- [What we carry](#what-we-carry)", text)
        self.assertNotIn("(#what)", text)
        self.assertEqual(check(text, path), [])
        rc, out, _ = run("index", "--write", path)
        self.assertEqual(rc, 0)
        self.assertIn("current", out)
        self.assertEqual(self.read(path), text)

    def test_write_moves_a_misplaced_index_first(self):
        text = self.without_contents().replace("## What\n", "## Contents\n\n- [Header](#header)\n\n## What\n")
        path = self.write("a.md", text)
        run("index", "--write", path)
        self.assertEqual(self.read(path), GOOD)

    def test_write_refuses_a_subsection_under_contents(self):
        text = "# T\n\n## 1. Problem\n\nIntro.\n\n## Contents\n\n- [x](#x)\n\n### Requirements\n\nREQ-ABC-001 The node MUST do it.\n\n## 2. Next\n"
        path = self.write("a.md", text)
        rc, out, err = run("index", "--write", path)
        self.assertEqual(rc, 1)
        self.assertIn(path + ":11: the Contents section holds other text on this line", err)
        self.assertIn("The file is unchanged", err)
        self.assertEqual(self.read(path), text)

    def test_write_refuses_a_paragraph_in_contents(self):
        text = GOOD.replace("- [What](#what)\n", "- [What](#what)\n\nNote: keep me.\n")
        path = self.write("a.md", text)
        rc, _, err = run("index", "--write", path)
        self.assertEqual(rc, 1)
        self.assertIn(path + ":16: the Contents section holds other text on this line", err)
        self.assertEqual(self.read(path), text)
        self.assertTrue(any("holds only its list of links" in e for e in check(text, path)))

    def test_write_builds_the_index_from_the_headings_that_remain(self):
        text = self.without_contents().replace("## What\n", "## Contents\n\n- [Gone](#gone)\n\n## What\n")
        path = self.write("a.md", text)
        rc, _, _ = run("index", "--write", path)
        self.assertEqual(rc, 0)
        self.assertEqual(self.read(path), GOOD)

    def test_check(self):
        good = self.write("good.md", GOOD)
        bad = self.write("bad.md", GOOD.replace("  - [Fields](#fields)\n", ""))
        rc, out, err = run("index", "--check", good, bad)
        self.assertEqual(rc, 1)
        self.assertIn("index 2 checked 1 failed", out)
        self.assertIn(bad + ":10: the heading 'Fields'", err)
        self.assertNotIn(good, err)

    def test_nothing_to_index(self):
        path = self.write("a.md", "# Title\n\nText only.\n")
        rc, _, err = run("index", "--write", path)
        self.assertEqual(rc, 1)
        self.assertIn("has no heading below its title", err)
        self.assertEqual(self.read(path), "# Title\n\nText only.\n")

    def test_usage(self):
        self.assertEqual(run("index")[0], 2)
        self.assertEqual(run("index", "--fix", "a.md")[0], 2)


class Templates(unittest.TestCase):
    """Every template on this branch carries a correct index."""

    def test_every_template_has_its_index(self):
        folder = os.path.join(ROOT, "docs", "process", "templates")
        names = sorted(name for name in os.listdir(folder) if name.endswith(".md"))
        self.assertTrue(names)
        for name in names:
            path = os.path.join(folder, name)
            with open(path, encoding="utf-8") as handle:
                text = handle.read()
            with self.subTest(template=name):
                self.assertEqual(check(text, path), [])


class DocumentCheck(unittest.TestCase):
    """The document subcommand requires the index when the template on the
    line has a Contents section, and only then."""

    def setUp(self):
        self.repo = tempfile.mkdtemp()
        self.git("init", "-q")
        os.makedirs(os.path.join(self.repo, "docs", "process", "templates"))
        os.makedirs(os.path.join(self.repo, "docs", "delta"))
        os.makedirs(os.path.join(self.repo, "docs", "releases"))
        os.makedirs(os.path.join(self.repo, "docs", "design", "42-a-fix"))

    def tearDown(self):
        shutil.rmtree(self.repo)

    def git(self, *args):
        subprocess.run(["git", "-C", self.repo, "-c", "user.name=t", "-c", "user.email=t@example.org",
                        "-c", "commit.gpgsign=false", "-c", "core.hooksPath=/dev/null"] + list(args),
                       check=True, capture_output=True)

    def put(self, path, text):
        with open(os.path.join(self.repo, path), "w", encoding="utf-8") as handle:
            handle.write(text)

    def line(self, template):
        self.put("docs/process/templates/delta-entry.md", template)
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "line")
        self.git("branch", "-f", "line")

    def document(self, path):
        return run("document", "--repo", self.repo, "--templates", "line", "--source", "worktree", path)

    def test_required_when_the_template_has_contents(self):
        self.line(TEMPLATE)
        self.put("docs/delta/README.md", "# Register\n")
        self.put("docs/delta/pinned.md", GOOD.replace("## Contents\n\n- [Header](#header)\n  - [Fields](#fields)\n- [What](#what)\n\n", ""))
        rc, out, err = self.document("docs/delta/pinned.md")
        self.assertEqual(rc, 1)
        self.assertIn("docs/delta/pinned.md:1: no '## Contents' section", err)

    def test_a_correct_index_passes_the_index_check(self):
        self.line(TEMPLATE)
        self.put("docs/delta/pinned.md", GOOD)
        _, _, err = self.document("docs/delta/pinned.md")
        self.assertNotIn("Contents", err)
        self.assertNotIn("doclint.py index", err)

    def test_not_required_when_the_template_has_none(self):
        self.line(TEMPLATE.replace("## Contents\n\n- [Header](#header)\n- [What](#what)\n\n", ""))
        self.put("docs/delta/pinned.md", GOOD.replace("## Contents\n\n- [Header](#header)\n  - [Fields](#fields)\n- [What](#what)\n\n", ""))
        _, _, err = self.document("docs/delta/pinned.md")
        self.assertNotIn("Contents", err)

    def decisions_on_the_line(self):
        """The line's decision README, whose record template has a Contents
        section, and its merged record 0001, which has none."""
        os.makedirs(os.path.join(self.repo, "docs", "decisions"))
        for name in ("README.md", "0001-initial-maintainers.md"):
            with open(os.path.join(ROOT, "docs", "decisions", name), encoding="utf-8") as handle:
                self.put("docs/decisions/" + name, handle.read())
        self.line(TEMPLATE)
        with open(os.path.join(ROOT, "docs", "decisions", "0001-initial-maintainers.md"), encoding="utf-8") as handle:
            old = handle.read()
        self.assertNotIn("## Contents", old)
        return old.replace("# 0001. The first maintainers", "# 0002. A later decision")

    def test_a_merged_record_without_an_index_passes(self):
        self.decisions_on_the_line()
        rc, out, err = self.document("docs/decisions/0001-initial-maintainers.md")
        self.assertEqual((rc, err), (0, ""))
        self.assertIn("documents 1 checked 0 failed", out)

    def test_a_new_record_without_an_index_fails(self):
        self.put("docs/decisions/0002-a-later-decision.md", self.decisions_on_the_line())
        rc, _, err = self.document("docs/decisions/0002-a-later-decision.md")
        self.assertEqual(rc, 1)
        self.assertIn("docs/decisions/0002-a-later-decision.md:1: no '## Contents' section", err)

    def test_a_new_record_with_its_index_passes(self):
        self.put("docs/decisions/0002-a-later-decision.md", self.decisions_on_the_line())
        run("index", "--write", os.path.join(self.repo, "docs/decisions/0002-a-later-decision.md"))
        rc, out, err = self.document("docs/decisions/0002-a-later-decision.md")
        self.assertEqual((rc, err), (0, ""))
        self.assertIn("documents 1 checked 0 failed", out)

    def test_a_new_record_reusing_a_merged_number_fails(self):
        self.put("docs/decisions/0001-another.md", self.decisions_on_the_line().replace("# 0002.", "# 0001."))
        rc, _, err = self.document("docs/decisions/0001-another.md")
        self.assertEqual(rc, 1)
        self.assertIn("docs/decisions/0001-another.md:1: no '## Contents' section", err)
        self.assertIn("a new decision record takes a number after the highest merged one, 0001, in order with no gap: 0002 here, and this one is 0001", err)

    def test_a_new_record_leaving_a_gap_fails(self):
        path = "docs/decisions/0003-gap.md"
        self.put(path, self.decisions_on_the_line().replace("# 0002.", "# 0003."))
        run("index", "--write", os.path.join(self.repo, path))
        rc, _, err = self.document(path)
        self.assertEqual(rc, 1)
        self.assertNotIn("Contents", err)
        self.assertIn("after the highest merged one, 0001, in order with no gap: 0002 here, and this one is 0003", err)

    def test_two_new_records_in_order_pass(self):
        text = self.decisions_on_the_line()
        paths = ["docs/decisions/0002-a-later-decision.md", "docs/decisions/0003-another-decision.md"]
        self.put(paths[0], text)
        self.put(paths[1], text.replace("# 0002.", "# 0003."))
        for path in paths:
            run("index", "--write", os.path.join(self.repo, path))
        rc, out, err = run("document", "--repo", self.repo, "--templates", "line", "--source", "worktree", *paths)
        self.assertEqual((rc, err), (0, ""))
        self.assertIn("documents 2 checked 0 failed", out)

    def test_a_coverage_file_is_a_document(self):
        self.assertEqual(doclint.doc_type("docs/design/42-a-fix/ac-coverage.md", "# Acceptance coverage for #42\n"), "ac-coverage")
        template = self.read_template("ac-coverage.md")
        self.put("docs/process/templates/ac-coverage.md", template)
        self.line(TEMPLATE)
        self.put("docs/design/42-a-fix/ac-coverage.md", "# Acceptance coverage for #42\n\n## Coverage\n\n| Id | Source | Requirement | Covering scenario | Test | Status |\n|---|---|---|---|---|---|\n")
        rc, _, err = self.document("docs/design/42-a-fix/ac-coverage.md")
        self.assertEqual(rc, 1)
        self.assertIn("no '## Contents' section", err)
        run("index", "--write", os.path.join(self.repo, "docs/design/42-a-fix/ac-coverage.md"))
        rc, out, err = self.document("docs/design/42-a-fix/ac-coverage.md")
        self.assertEqual((rc, err), (0, ""))
        self.assertIn("documents 1 checked 0 failed", out)

    def read_template(self, name):
        with open(os.path.join(ROOT, "docs", "process", "templates", name), encoding="utf-8") as handle:
            return handle.read()


if __name__ == "__main__":
    unittest.main()
