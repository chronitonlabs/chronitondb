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
"""A review record, docs/reviews/<work>.md, is checked against the review
record template once the line has it, and the record merged before the
template passes. Run from the repository root:

    python3 -m unittest discover -s tools/chronitondb/test/doclint
"""

import contextlib
import glob
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

TEMPLATE = os.path.join(ROOT, "docs", "process", "templates", "review-record.md")
RECORD = "docs/reviews/42-disk-check-design.md"


def run(*args):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = doclint.main(list(args))
    return rc, out.getvalue(), err.getvalue()


def template():
    with open(TEMPLATE, encoding="utf-8") as handle:
        return handle.read()


def opened_record():
    """The review record template on this branch as the author writes it
    when the pull request opens: no round yet, no decision."""
    text = template()
    text = text.replace("| Status | Open or Closed |", "| Status | Open |")
    # The paragraph on how the record is kept is the template's own.
    text = re.sub(r"\{How the record is kept\..*\}\n\n", "", text)
    # The two tables keep their header rows only.
    text = re.sub(r"\| \{n\} \| \{YYYY-MM-DD\}.*\n", "", text)
    text = re.sub(r"\| R\{round\}-\{n\} \|.*\n", "", text)
    # No decision: the one line, and no subsection.
    text = re.sub(r"## 3\. Decisions\n.*?(?=## 4\.)", "## 3. Decisions\n\nNo decisions.\n\n", text, flags=re.S)
    text = text.replace("  - [D{n}. {The question in one line}](#dn-the-question-in-one-line)\n", "")
    text = re.sub(r"## 4\. Limits\n.*?(?=## 5\.)", "## 4. Limits\n\nNone.\n\n", text, flags=re.S)
    text = re.sub(r"## 5\. Exit decision\n.*", "## 5. Exit decision\n\nOpen.\n", text, flags=re.S)
    text = text.replace("{the head commit the newest round read, by its short hash, or Not reviewed yet}", "Not reviewed yet")
    return re.sub(r"\{[^{}]*\}", "answered", text)


class ReviewRecord(unittest.TestCase):

    def setUp(self):
        self.repo = tempfile.mkdtemp()
        self.git("init", "-q")
        os.makedirs(os.path.join(self.repo, "docs", "process", "templates"))
        os.makedirs(os.path.join(self.repo, "docs", "reviews"))
        self.put("docs/process/README.md", "# Process\n")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "before the template")
        self.git("branch", "-f", "before")
        self.put("docs/process/templates/review-record.md", template())
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "line")
        self.git("branch", "-f", "line")

    def tearDown(self):
        shutil.rmtree(self.repo)

    def git(self, *args):
        subprocess.run(["git", "-C", self.repo, "-c", "user.name=t", "-c", "user.email=t@example.org",
                        "-c", "commit.gpgsign=false", "-c", "core.hooksPath=/dev/null"] + list(args),
                       check=True, capture_output=True)

    def put(self, path, text):
        with open(os.path.join(self.repo, path), "w", encoding="utf-8") as handle:
            handle.write(text)

    def document(self, path, ref="line"):
        return run("document", "--repo", self.repo, "--templates", ref, "--source", "worktree", path)

    def test_a_record_written_from_the_template_passes(self):
        self.put(RECORD, opened_record())
        rc, out, err = self.document(RECORD)
        self.assertEqual((rc, err), (0, ""))
        self.assertIn("documents 1 checked 0 failed", out)

    def test_a_record_with_a_decision_lists_it_in_its_index(self):
        text = opened_record().replace("No decisions.\n", "### D1. Which counter the warning names\n\n- **Raised by:** R1-1.\n- **Options:** A. The first. B. Both.\n- **Chosen:** B. Both.\n- **Reason:** An operator reads both.\n- **Decided by:** the maintainers, 2026-11-18.\n")
        self.put(RECORD, text)
        rc, _, err = self.document(RECORD)
        self.assertEqual(rc, 1)
        self.assertIn("is not in the index", err)
        text = text.replace("- [3. Decisions](#3-decisions)\n", "- [3. Decisions](#3-decisions)\n  - [D1. Which counter the warning names](#d1-which-counter-the-warning-names)\n")
        self.put(RECORD, text)
        rc, out, err = self.document(RECORD)
        self.assertEqual((rc, err), (0, ""))
        self.assertIn("documents 1 checked 0 failed", out)

    def test_a_status_the_template_does_not_allow_fails(self):
        self.put(RECORD, opened_record().replace("| Status | Open |", "| Status | Approved |"))
        rc, _, err = self.document(RECORD)
        self.assertEqual(rc, 1)
        self.assertIn("Status is 'Approved', a review record is Open or Closed", err)

    def test_a_record_missing_a_section_names_the_review_record_template(self):
        text = re.sub(r"## 4\. Limits\n.*?(?=## 5\.)", "", opened_record(), flags=re.S).replace("- [4. Limits](#4-limits)\n", "")
        self.put(RECORD, text)
        rc, _, err = self.document(RECORD)
        self.assertEqual(rc, 1)
        self.assertIn("no '## 4. Limits' section. The review record template has it", err)

    def test_a_record_missing_a_field_fails(self):
        self.put(RECORD, re.sub(r"\| Reviewer \|.*\n", "", opened_record()))
        rc, _, err = self.document(RECORD)
        self.assertEqual(rc, 1)
        self.assertIn("the document control table has no 'Reviewer' row", err)

    def test_a_placeholder_left_in_a_record_fails(self):
        left = re.search(r"## 4\. Limits\n\n(\{.*\})", template()).group(1)
        self.put(RECORD, opened_record().replace("## 4. Limits\n\nNone.", "## 4. Limits\n\n" + left))
        rc, _, err = self.document(RECORD)
        self.assertEqual(rc, 1)
        self.assertIn("a placeholder of the template is left", err)

    def test_a_record_without_its_contents_index_fails(self):
        text = re.sub(r"## Contents\n.*?(?=## 1\.)", "", opened_record(), flags=re.S)
        self.put(RECORD, text)
        rc, _, err = self.document(RECORD)
        self.assertEqual(rc, 1)
        self.assertIn("Contents", err)

    def test_a_line_with_no_template_yet_passes_the_record_over(self):
        self.put(RECORD, opened_record().replace("| Status | Open |", "| Status | Approved |"))
        rc, out, err = self.document(RECORD, ref="before")
        self.assertEqual((rc, err), (0, ""))
        self.assertIn("documents 0 checked 0 failed", out)

    def test_another_type_with_no_template_on_the_line_still_fails(self):
        os.makedirs(os.path.join(self.repo, "docs", "research"))
        self.put("docs/research/42-disk-check.md", "# Research report: #42 Disk check\n")
        rc, _, err = self.document("docs/research/42-disk-check.md")
        self.assertEqual(rc, 1)
        self.assertIn("no research report template", err)

    def test_the_reviews_readme_is_not_a_record(self):
        self.put("docs/reviews/README.md", "# Review records\n")
        rc, out, err = self.document("docs/reviews/README.md")
        self.assertEqual((rc, err), (0, ""))
        self.assertIn("documents 0 checked 0 failed", out)

    def test_the_template_has_its_own_index(self):
        rc, out, err = run("index", "--check", TEMPLATE)
        self.assertEqual((rc, err), (0, ""))

    def test_the_records_merged_in_this_repository_pass(self):
        records = sorted(glob.glob(os.path.join(ROOT, "docs", "reviews", "*.md")))
        for path in records:
            name = "docs/reviews/" + os.path.basename(path)
            with open(path, encoding="utf-8") as handle:
                self.put(name, handle.read())
            rc, _, err = self.document(name)
            self.assertEqual((rc, err), (0, ""), name)


if __name__ == "__main__":
    unittest.main()
