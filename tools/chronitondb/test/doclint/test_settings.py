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
"""The two checks of doclint.py that read the build and the configuration
and not a document: settings, the setting names of
conf/cassandra_chronitondb.yaml against Apache's two yaml files
(docs/process/release.md, The configuration file), and dependencies, the
libraries a change adds or moves (docs/process/compliance.md, Declaring
dependencies). Run from the repository root:

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
sys.path.insert(0, TOOLS)
import doclint  # noqa: E402

APACHE = "conf/cassandra.yaml"
LATEST = "conf/cassandra_latest.yaml"
OURS = "conf/cassandra_chronitondb.yaml"
PINS = "requirements.txt"
POM = ".build/parent-pom-template.xml"
SPEC = "docs/design/ABC-test-feature/feature-spec.md"


def run(*args):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = doclint.main(list(args))
    return rc, out.getvalue(), err.getvalue()


class Repo(unittest.TestCase):
    """A repository whose first commit is the line. Each test changes the
    working tree, commits, and checks the commit against the line."""

    FILES = {}

    def setUp(self):
        self.repo = tempfile.mkdtemp()
        self.git("init", "-q")
        for path, text in self.FILES.items():
            self.put(path, text)
        self.put("README.md", "A line.\n")
        self.commit()
        self.git("branch", "-f", "line")
        self.git("checkout", "-q", "-b", "change")

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

    def commit(self):
        self.git("add", "-A")
        self.git("commit", "-q", "--allow-empty", "-m", "change")


class Settings(Repo):

    FILES = {APACHE: "cluster_name: 'Test Cluster'\nnum_tokens: 16\n# hints_compression:\n#   - class_name: LZ4Compressor\n",
             LATEST: "cluster_name: 'Test Cluster'\nnum_tokens: 16\nsstable:\n  selected_format: bti\n",
             OURS: "cluster_name: 'Test Cluster'\n# num_tokens: 16\n#hints_compression:\nsstable:\n  selected_format: bti\n"}

    def settings(self):
        self.commit()
        return run("settings", "--repo", self.repo, "--base", "line", "--source", "HEAD")

    def test_a_file_that_holds_every_apache_setting_passes(self):
        # Active, commented with a space and commented without one all count.
        self.assertEqual(self.settings(), (0, "settings 4\n", ""))

    def test_an_apache_setting_missing_from_ours_fails(self):
        self.put(APACHE, self.FILES[APACHE] + "concurrent_reads: 32\n")
        rc, out, err = self.settings()
        self.assertEqual((rc, out), (1, "settings 5\n"))
        self.assertEqual(err, "%s:5: Apache's setting concurrent_reads is not in %s, active or commented, and not left out with a reason "
                              "on a line '# Left out: concurrent_reads: <reason>'\n" % (APACHE, OURS))

    def test_a_setting_only_in_the_latest_file_is_asked_for_too(self):
        self.put(LATEST, self.FILES[LATEST] + "default_compaction:\n  class_name: UnifiedCompactionStrategy\n")
        rc, _, err = self.settings()
        self.assertEqual(rc, 1)
        self.assertIn("%s:5: Apache's setting default_compaction is not in %s" % (LATEST, OURS), err)

    def test_a_setting_left_out_with_a_reason_passes(self):
        self.put(APACHE, self.FILES[APACHE] + "concurrent_reads: 32\n")
        self.put(OURS, self.FILES[OURS] + "# Left out: concurrent_reads: the default is right for every disk we support\n")
        self.assertEqual(self.settings(), (0, "settings 5\n", ""))
        # The line needs its reason.
        self.put(OURS, self.FILES[OURS] + "# Left out: concurrent_reads:\n")
        self.assertEqual(self.settings()[0], 1)

    def test_a_nested_key_is_not_a_setting(self):
        self.put(APACHE, self.FILES[APACHE] + "seed_provider:\n  - class_name: SimpleSeedProvider\n    parameters:\n      - seeds: '127.0.0.1'\n")
        rc, _, err = self.settings()
        self.assertEqual(rc, 1)
        self.assertIn("Apache's setting seed_provider is not in", err)
        self.assertNotIn("class_name", err)
        self.assertNotIn("seeds", err)

    def test_a_setting_apache_removed_is_removed_or_flagged(self):
        for path in (APACHE, LATEST):
            self.put(path, self.FILES[path].replace("num_tokens: 16\n", ""))
        rc, out, err = self.settings()
        self.assertEqual((rc, out), (1, "settings 3\n"))
        self.assertEqual(err, "%s:2: Apache removed the setting num_tokens from %s. Remove it from ours or flag it on a line "
                              "'# Apache removed: num_tokens'\n" % (OURS, APACHE))
        self.put(OURS, self.FILES[OURS] + "# Apache removed: num_tokens\n")
        self.assertEqual(self.settings(), (0, "settings 3\n", ""))
        self.put(OURS, self.FILES[OURS].replace("# num_tokens: 16\n", ""))
        self.assertEqual(self.settings(), (0, "settings 3\n", ""))

    def test_a_setting_of_our_own_is_not_asked_of_apache(self):
        self.put(OURS, self.FILES[OURS] + "our_own_setting: true\n")
        self.assertEqual(self.settings(), (0, "settings 4\n", ""))

    def test_our_file_removed_while_the_line_has_it_fails(self):
        os.remove(os.path.join(self.repo, OURS))
        rc, out, err = self.settings()
        self.assertEqual((rc, out), (1, "settings 0\n"))
        self.assertIn("%s:0: our yaml is removed, and the line has it" % OURS, err)

    def test_usage(self):
        self.assertEqual(run("settings", "--repo", self.repo)[0], 2)
        self.assertEqual(run("settings", "--repo", self.repo, "--base", "line", "--other", "x")[0], 2)


class NoFileOfOurs(Repo):

    FILES = {APACHE: "cluster_name: 'Test Cluster'\n"}

    def test_a_line_with_no_file_of_ours_has_nothing_to_compare(self):
        self.put(APACHE, "cluster_name: 'Test Cluster'\nconcurrent_reads: 32\n")
        self.commit()
        self.assertEqual(run("settings", "--repo", self.repo, "--base", "line", "--source", "HEAD"), (0, "settings none\n", ""))


def spec(*lines):
    return "\n".join(["# Feature spec: Test feature", "", "## 9. Dependencies", ""] + list(lines)) + "\n"


def pom(version):
    return ("<project>\n <dependencies>\n  <dependency>\n   <groupId>org.example</groupId>\n   <artifactId>somelib</artifactId>\n"
            "   <version>%s</version>\n  </dependency>\n </dependencies>\n</project>\n" % version)


class Dependencies(Repo):

    FILES = {PINS: "otherlib==2.0.1\n", POM: pom("1.2.3"), "build.xml": "<project>\n <property name=\"somelib.version\" value=\"1.2.3\" />\n</project>\n"}

    def dependencies(self, *files):
        self.commit()
        return run("dependencies", "--repo", self.repo, "--base", "line", "--line", "line", "--source", "HEAD", *(files or (PINS, POM, "build.xml")))

    def declare(self, *lines):
        """Puts a feature spec with these Dependencies lines on the line."""
        self.git("checkout", "-q", "line")
        self.put(SPEC, spec(*lines))
        self.commit()
        self.git("checkout", "-q", "change")
        self.git("rebase", "-q", "line")

    def test_no_change_passes(self):
        self.assertEqual(self.dependencies(), (0, "", ""))

    def test_a_new_library_nobody_declared_fails(self):
        self.put(PINS, self.FILES[PINS] + "newlib==0.4.0\n")
        rc, out, err = self.dependencies()
        self.assertEqual((rc, out), (1, ""))
        self.assertEqual(err, "%s:0: pypi:newlib is added at 0.4.0, and no Dependencies section of a merged feature spec or design record on line "
                              "names it at that version. A new library or a minor or major version change is declared there first, only a "
                              "patch-version bump goes without\n" % PINS)

    def test_a_new_library_with_no_version_cannot_be_declared(self):
        self.put(PINS, self.FILES[PINS] + "newlib\n")
        rc, _, err = self.dependencies()
        self.assertEqual(rc, 1)
        self.assertIn("pypi:newlib is added with no version pinned, so it cannot be declared at a version", err)

    def test_a_patch_bump_passes_and_is_printed(self):
        self.put(PINS, "otherlib==2.0.2\n")
        self.put(POM, pom("1.2.9"))
        rc, out, err = self.dependencies()
        self.assertEqual((rc, err), (0, ""))
        self.assertEqual(sorted(out.splitlines()), ["patch org.example:somelib 1.2.3 1.2.9 %s" % POM, "patch pypi:otherlib 2.0.1 2.0.2 %s" % PINS])

    def test_a_minor_or_major_move_nobody_declared_fails(self):
        for version in ("2.1.0", "3.0.0", "2.0.0"):
            self.put(PINS, "otherlib==%s\n" % version)
            rc, _, err = self.dependencies()
            self.assertEqual(rc, 1, version)
            self.assertIn("pypi:otherlib moves from 2.0.1 to %s, and no Dependencies section" % version, err)

    def test_a_library_declared_at_its_version_on_the_line_passes(self):
        self.declare("| Library | Version | ASF category | Why |", "|---|---|---|---|",
                     "| newlib | 0.4.0 | Category A | It parses text |", "| org.example:somelib | 1.3.0 | Category A | A fix we need |")
        self.put(PINS, self.FILES[PINS] + "newlib==0.4.0\n")
        self.put(POM, pom("1.3.0"))
        self.assertEqual(self.dependencies(), (0, "", ""))

    def test_a_library_declared_at_another_version_fails(self):
        self.declare("The feature adds newlib 0.4.0, ASF category A.")
        self.put(PINS, self.FILES[PINS] + "newlib==0.5.0\n")
        rc, _, err = self.dependencies()
        self.assertEqual(rc, 1)
        self.assertIn("pypi:newlib is added at 0.5.0", err)

    def test_a_version_given_by_a_build_property_is_resolved(self):
        self.put(POM, pom("${somelib.version}"))
        self.assertEqual(self.dependencies(), (0, "", ""))
        self.put("build.xml", self.FILES["build.xml"].replace("1.2.3", "1.4.0"))
        rc, _, err = self.dependencies()
        self.assertEqual(rc, 1)
        self.assertIn("%s:0: org.example:somelib moves from 1.2.3 to 1.4.0" % POM, err)

    def test_a_declaration_only_on_the_change_does_not_count(self):
        # The declaration is merged on the line first. One the change
        # itself brings is not yet approved.
        self.put(SPEC, spec("The feature adds newlib 0.4.0, ASF category A."))
        self.put(PINS, self.FILES[PINS] + "newlib==0.4.0\n")
        rc, _, err = self.dependencies()
        self.assertEqual(rc, 1)
        self.assertIn("pypi:newlib is added at 0.4.0", err)

    def test_usage(self):
        self.assertEqual(run("dependencies", "--repo", self.repo, "--base", "line")[0], 2)
        self.assertEqual(run("dependencies", "--repo", self.repo, "--base", "line", "--line", "line", "--other", PINS)[0], 2)


if __name__ == "__main__":
    unittest.main()
