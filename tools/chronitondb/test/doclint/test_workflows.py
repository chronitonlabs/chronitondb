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
"""The steps of the CI workflows that decide what a pull request is checked
with, run here as the shell scripts they are, with the environment each
workflow gives its step. A pull request controls its branch name, its
title and every file it brings, so the checks run the scripts and rules of
the base branch, and the name of an import branch counts only for a branch
of the repository itself. The delta register step is tested in
test_delta.py. Run from the repository root:

    python3 -m unittest discover -s tools/chronitondb/test/doclint
"""

import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

TOOLS = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
ROOT = os.path.normpath(os.path.join(TOOLS, "..", ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from test_delta import read, step_env, step_script  # noqa: E402

WORKFLOWS = os.path.join(ROOT, ".github", "workflows")
OURS = sorted(name for name in os.listdir(WORKFLOWS) if name.startswith("chronitondb-"))
REPO = "example/product"
IMPORT = "import/cassandra-5.0.8/chronitondb-5.0"
# A stand-in for a check script: it says which copy ran and with what.
STAND_IN = "#!/bin/sh\necho \"%s $*\"\n"


class Steps(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.mkdtemp()
        self.workspace = os.path.join(self.temp, "workspace")
        os.makedirs(self.workspace)

    def tearDown(self):
        shutil.rmtree(self.temp)

    def put(self, path, text, mode=0o644):
        full = os.path.join(self.temp, path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8") as handle:
            handle.write(text)
        os.chmod(full, mode)

    def step(self, workflow, name, head_repo=REPO, head_ref="agent/42-disk-check/chronitondb-5.0", more=None):
        path = ".github/workflows/" + workflow
        context = {"github.base_ref": "line", "github.head_ref": head_ref, "github.repository": REPO,
                   "github.event.pull_request.head.repo.full_name": head_repo,
                   "github.event.pull_request.number": "7", "github.token": "none"}
        env = dict(os.environ, PATH=os.path.join(self.temp, "bin") + os.pathsep + os.environ.get("PATH", ""),
                   RUNNER_TEMP=self.temp, GITHUB_WORKSPACE=self.workspace, **(more or {}))
        env.update(step_env(path, name, context))
        done = subprocess.run(["bash", "-e", "-c", step_script(path, name)], cwd=self.workspace, env=env,
                              capture_output=True, text=True, check=False)
        return done.returncode, done.stdout, done.stderr


class CodeChecks(Steps):
    """The shape, Semgrep and SpotBugs steps run the script of the base
    branch, in its own tree, on the files of the pull request."""

    def scripts(self, name):
        self.put("line/tools/chronitondb/" + name, STAND_IN % "line", 0o755)
        self.put("workspace/tools/chronitondb/" + name, STAND_IN % "head", 0o755)

    def test_the_shape_check_is_the_one_of_the_base_branch(self):
        self.scripts("shape-check.sh")
        rc, out, err = self.step("chronitondb-shape.yml", "Shape limits on the changed org/chronitondb files")
        self.assertEqual((rc, out, err), (0, "line --tree %s --base origin/line\n" % self.workspace, ""))
        rc, out, _ = self.step("chronitondb-shape.yml", "Self-test the check of the line")
        self.assertEqual((rc, out), (0, "line --self-test\n"))

    def test_the_semgrep_rules_are_the_ones_of_the_base_branch(self):
        self.scripts("semgrep-check.sh")
        rc, out, err = self.step("chronitondb-semgrep.yml", "Semgrep on the changed files")
        self.assertEqual((rc, out, err), (0, "line --tree %s --base origin/line\n" % self.workspace, ""))
        rc, out, _ = self.step("chronitondb-semgrep.yml", "Self-test the rules of the line")
        self.assertEqual((rc, out), (0, "line --self-test\n"))

    def test_the_spotbugs_script_is_the_one_of_the_base_branch(self):
        self.scripts("spotbugs-check.sh")
        rc, out, err = self.step("chronitondb-spotbugs.yml", "SpotBugs on the org/chronitondb classes (report only)")
        self.assertEqual((rc, out, err), (0, "line --tree %s\n" % self.workspace, ""))
        rc, out, _ = self.step("chronitondb-spotbugs.yml", "Self-test SpotBugs and FindSecBugs with the script of the line")
        self.assertEqual((rc, out), (0, "line --self-test\n"))

    def test_a_finding_in_imported_code_is_reported_only_on_an_import_branch_of_the_repository(self):
        self.scripts("semgrep-check.sh")
        step = "Semgrep on the changed files"
        rc, out, _ = self.step("chronitondb-semgrep.yml", step, head_ref=IMPORT)
        self.assertEqual((rc, out), (0, "line --tree %s --imported --base origin/line\n" % self.workspace))
        for head_ref in ("import/CASSANDRA-21319/chronitondb-5.0", "import/rustyrazorblade-cassandra-579e35ae6c12/chronitondb-5.0"):
            self.assertIn(" --imported ", self.step("chronitondb-semgrep.yml", step, head_ref=head_ref)[1], head_ref)
        # A fork's branch has any name its author likes, so it never counts.
        for head_repo in ("someone/product", REPO + "-fork", ""):
            rc, out, _ = self.step("chronitondb-semgrep.yml", step, head_repo=head_repo, head_ref=IMPORT)
            self.assertEqual((rc, out), (0, "line --tree %s --base origin/line\n" % self.workspace), head_repo)
        for head_ref in ("agent/42-disk-check/chronitondb-5.0", "x/import/cassandra-5.0.8", "imports/cassandra-5.0.8"):
            self.assertNotIn("--imported", self.step("chronitondb-semgrep.yml", step, head_ref=head_ref)[1], head_ref)


class Title(Steps):
    """The title step: the import type, which lifts the length rule and the
    file rule, is taken only from an import branch of the repository."""

    TITLE = "import(CASSANDRA-1): change DiskCheck.java, build.xml and every other file this long subject can name"

    def setUp(self):
        super().setUp()
        shutil.copy(os.path.join(TOOLS, "subjectlint.py"), self.path("subjectlint", "subjectlint.py"))
        self.put("bin/gh", "#!/bin/sh\ncase \"$*\" in\n  *.title*) printf '%s\\n' \"$PR_TITLE\" ;;\n  *) printf '%s' \"$PR_BODY\" ;;\nesac\n", 0o755)
        self.put("workspace/docs/process/conventions.md", read("docs/process/conventions.md"))
        for args in (["init", "-q"], ["add", "-A"], ["commit", "-q", "-m", "line"], ["update-ref", "refs/remotes/origin/line", "HEAD"]):
            subprocess.run(["git", "-C", self.workspace, "-c", "user.name=t", "-c", "user.email=t@example.org", "-c", "commit.gpgsign=false",
                            "-c", "core.hooksPath=/dev/null"] + args, check=True, capture_output=True)

    def path(self, *parts):
        full = os.path.join(self.temp, *parts)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        return full

    def title(self, title, body="", **where):
        return self.step("chronitondb-subjects.yml", "Pull request title", more={"PR_TITLE": title, "PR_BODY": body}, **where)

    def test_the_step_checks_the_attribution_of_the_commits_and_the_description(self):
        git = ["git", "-C", self.workspace, "-c", "user.name=t", "-c", "user.email=t@example.org", "-c", "commit.gpgsign=false",
               "-c", "core.hooksPath=/dev/null"]
        subprocess.run(git + ["commit", "-q", "--allow-empty", "-m", "keep the limit\n\nCo-authored-by: Example Model 4 <noreply@anthropic.com>"],
                       check=True, capture_output=True)
        rc, out, err = self.title("fix(startup): keep the disk check limit", body="What and why.\n\nhttps://claude.ai/code/session_01ABC\n")
        self.assertEqual(rc, 1)
        self.assertIn("names an AI tool or model as a co-author", err)
        self.assertIn("description: the line 'https://claude.ai/code/session_01ABC' links a session of an AI tool", err)
        self.assertIn("title failed", out)

    def test_an_import_title_passes_from_an_import_branch_of_the_repository(self):
        rc, out, err = self.title(self.TITLE, head_ref="import/CASSANDRA-1/chronitondb-5.0")
        self.assertEqual((rc, err), (0, ""))
        self.assertIn("title passed", out)

    def test_an_import_title_is_refused_from_any_other_branch(self):
        for where in ({"head_ref": "agent/42-disk-check/chronitondb-5.0"},
                      {"head_repo": "someone/product", "head_ref": "import/CASSANDRA-1/chronitondb-5.0"},
                      {"head_repo": "", "head_ref": "import/CASSANDRA-1/chronitondb-5.0"}):
            rc, out, err = self.title(self.TITLE, **where)
            self.assertEqual(rc, 1, where)
            self.assertIn("title: the type 'import' is only for an import", err)
            self.assertIn("title failed", out)

    def test_another_type_passes_from_any_branch(self):
        for where in ({}, {"head_repo": "someone/product", "head_ref": "a-fix"}):
            rc, out, err = self.title("fix(startup): keep the disk check limit", **where)
            self.assertEqual((rc, err), (0, ""), where)

    def test_a_checker_on_the_line_without_the_option_is_not_given_it(self):
        with open(self.path("subjectlint", "subjectlint.py"), encoding="utf-8") as handle:
            text = handle.read()
        old = text.replace("[--branch NAME] ", "").replace('"--commits", "--branch")', '"--commits")')
        self.assertNotIn("--branch NAME", old)
        self.put("subjectlint/subjectlint.py", old)
        rc, out, err = self.title("fix(startup): keep the disk check limit")
        self.assertEqual((rc, err), (0, ""))
        self.assertIn("title passed", out)


class Workflows(unittest.TestCase):
    """What every workflow of the project keeps to, so that code a pull
    request brings never runs with more than a read only token."""

    def test_no_workflow_runs_with_the_base_repository_token_on_a_pull_request(self):
        for name in OURS:
            text = read(".github/workflows/" + name)
            self.assertNotIn("pull_request_target", text, name)
            self.assertNotIn("workflow_run", text, name)
            self.assertNotIn("secrets.", text, name)

    def test_every_workflow_asks_for_read_access_only(self):
        for name in OURS:
            text = read(".github/workflows/" + name)
            block = re.search(r"^permissions:\n((?:  \S.*\n)+)", text, re.M)
            self.assertIsNotNone(block, name)
            for line in block.group(1).splitlines():
                self.assertRegex(line, r"^  [a-z-]+: read$", name)
            self.assertEqual(len(re.findall(r"^\s*permissions:", text, re.M)), 1, name)

    def test_no_checkout_keeps_its_credentials(self):
        for name in OURS:
            lines = read(".github/workflows/" + name).split("\n")
            for index, line in enumerate(lines):
                if "uses: actions/checkout@" in line:
                    self.assertIn("persist-credentials: false", "\n".join(lines[index:index + 5]), "%s:%d" % (name, index + 1))

    def test_the_head_branch_name_is_never_used_without_the_head_repository(self):
        for name in OURS:
            text = read(".github/workflows/" + name)
            if "github.head_ref" not in text:
                continue
            self.assertEqual(text.count("github.head_ref"), 1, name)
            self.assertIn("HEAD_REF: ${{ github.head_ref }}", text, name)
            self.assertIn("HEAD_REPO: ${{ github.event.pull_request.head.repo.full_name }}", text, name)
            self.assertIn('if [ "$HEAD_REPO" = "$REPO" ]', text, name)


if __name__ == "__main__":
    unittest.main()
