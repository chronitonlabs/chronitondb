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
"""A line plan, docs/releases/<line>-plan.md, is checked against the line
plan template, never the release proposal template. Run from the
repository root:

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


def run(*args):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = doclint.main(list(args))
    return rc, out.getvalue(), err.getvalue()


def template(name):
    with open(os.path.join(TEMPLATES, name), encoding="utf-8") as handle:
        return handle.read()


def filled_line_plan():
    """The line plan template on this branch with every placeholder
    answered, as a maintainer writes it."""
    text = template("line-plan.md").replace("{line}", "chronitondb-5.0")
    text = text.replace("| Status | Draft, Approved or Superseded |", "| Status | Draft |")
    text = text.replace("| Version | {n} |", "| Version | 1 |")
    text = text.replace("| Author | {GitHub username} |", "| Author | millerjp |")
    return re.sub(r"\{[^{}]*\}", "not set", text)


class LinePlan(unittest.TestCase):

    def setUp(self):
        self.repo = tempfile.mkdtemp()
        self.git("init", "-q")
        os.makedirs(os.path.join(self.repo, "docs", "process", "templates"))
        os.makedirs(os.path.join(self.repo, "docs", "releases"))
        for name in ("line-plan.md", "release-proposal.md"):
            self.put("docs/process/templates/" + name, template(name))
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

    def test_a_filled_line_plan_passes(self):
        self.put("docs/releases/chronitondb-5.0-plan.md", filled_line_plan())
        rc, out, err = self.document("docs/releases/chronitondb-5.0-plan.md")
        self.assertEqual((rc, err), (0, ""))
        self.assertIn("documents 1 checked 0 failed", out)

    def test_a_line_plan_missing_a_section_names_the_line_plan_template(self):
        text = re.sub(r"## 2\. Feature freeze\n.*?(?=## 3\.)", "", filled_line_plan(), flags=re.S)
        self.put("docs/releases/chronitondb-5.0-plan.md", text)
        rc, _, err = self.document("docs/releases/chronitondb-5.0-plan.md")
        self.assertEqual(rc, 1)
        self.assertIn("no '## 2. Feature freeze' section. The line plan template has it", err)
        self.assertNotIn("release proposal", err)

    def test_a_release_proposal_is_still_checked_against_its_template(self):
        self.put("docs/releases/5.0.10-chronitondb1.md", filled_line_plan())
        rc, _, err = self.document("docs/releases/5.0.10-chronitondb1.md")
        self.assertEqual(rc, 1)
        self.assertIn("The release proposal template has it", err)


if __name__ == "__main__":
    unittest.main()
