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
"""A research report, docs/research/<issue>-<slug>.md, is checked against
the research report template, and its file name and References row name
the spike's issue. Run from the repository root:

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

TEMPLATES = os.path.join(ROOT, "docs", "process", "templates")
REPORT = "docs/research/42-compaction-throttle.md"


def run(*args):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = doclint.main(list(args))
    return rc, out.getvalue(), err.getvalue()


def template(name):
    with open(os.path.join(TEMPLATES, name), encoding="utf-8") as handle:
        return handle.read()


def filled_report(issue="42"):
    """The research report template on this branch with every placeholder
    answered, as the architect writes it."""
    text = template("research-report.md").replace("{issue}", issue)
    text = text.replace("| Status | Draft, Approved or Superseded |", "| Status | Draft |")
    text = text.replace("| Version | {n} |", "| Version | 1 |")
    text = text.replace("| Author | Architect: {GitHub username} |", "| Author | Architect: millerjp |")
    return re.sub(r"\{[^{}]*\}", "answered", text)


class ResearchReport(unittest.TestCase):

    def setUp(self):
        self.repo = tempfile.mkdtemp()
        self.git("init", "-q")
        os.makedirs(os.path.join(self.repo, "docs", "process", "templates"))
        os.makedirs(os.path.join(self.repo, "docs", "research"))
        self.put("docs/process/templates/research-report.md", template("research-report.md"))
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

    def document(self, path):
        return run("document", "--repo", self.repo, "--templates", "line", "--source", "worktree", path)

    def test_a_filled_report_passes(self):
        self.put(REPORT, filled_report())
        rc, out, err = self.document(REPORT)
        self.assertEqual((rc, err), (0, ""))
        self.assertIn("documents 1 checked 0 failed", out)

    def test_a_report_missing_a_section_names_the_research_report_template(self):
        text = re.sub(r"## 5\. Effort\n.*?(?=## 6\.)", "", filled_report(), flags=re.S)
        self.put(REPORT, text)
        rc, _, err = self.document(REPORT)
        self.assertEqual(rc, 1)
        self.assertIn("no '## 5. Effort' section. The research report template has it", err)

    def test_a_placeholder_left_in_a_report_fails(self):
        left = re.search(r"## 7\. Options\n\n(\{[^{}]*\})", template("research-report.md")).group(1)
        self.put(REPORT, filled_report().replace("## 7. Options\n\nanswered", "## 7. Options\n\n" + left))
        rc, _, err = self.document(REPORT)
        self.assertEqual(rc, 1)
        self.assertIn(REPORT, err)

    def test_a_report_without_its_contents_index_fails(self):
        text = re.sub(r"## Contents\n.*?(?=## 1\.)", "", filled_report(), flags=re.S)
        self.put(REPORT, text)
        rc, _, err = self.document(REPORT)
        self.assertEqual(rc, 1)
        self.assertIn("Contents", err)

    def test_a_report_named_without_its_issue_fails(self):
        self.put("docs/research/compaction-throttle.md", filled_report())
        rc, _, err = self.document("docs/research/compaction-throttle.md")
        self.assertEqual(rc, 1)
        self.assertIn("a research report is docs/research/<issue>-<slug>.md", err)

    def test_a_report_whose_references_name_another_issue_fails(self):
        self.put(REPORT, filled_report(issue="41"))
        rc, _, err = self.document(REPORT)
        self.assertEqual(rc, 1)
        self.assertIn("names the spike's issue as #42", err)

    def test_the_research_readme_is_not_a_report(self):
        self.put("docs/research/README.md", "# Research reports\n")
        rc, out, err = self.document("docs/research/README.md")
        self.assertEqual((rc, err), (0, ""))
        self.assertIn("documents 0 checked 0 failed", out)


if __name__ == "__main__":
    unittest.main()
