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
"""A short record, docs/design/<issue>-<slug>/short-record.md, is checked
against the short record template: its Tier row is the line the tier
command prints for the change, and the tests of section 4 trace to the
items of section 2. The tier command reads the paths of the Critical floor
from classification.md on the line. Run from the repository root:

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

PROCESS = os.path.join(ROOT, "docs", "process")
RECORD = "docs/design/42-widget-table/short-record.md"
FLOOR_FILE = "src/java/org/apache/cassandra/db/compaction/Widget.java"
OTHER_FILE = "src/java/org/apache/cassandra/db/virtual/WidgetTable.java"


def run(*args):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = doclint.main(list(args))
    return rc, out.getvalue(), err.getvalue()


def page(name):
    with open(os.path.join(PROCESS, name), encoding="utf-8") as handle:
        return handle.read()


SECTIONS = {
    "1. Impact": "Operators cannot list the widgets of a node without reading its files.",
    "2. What changes": "REQ-1: The widget table MUST have the columns name of type text and size of type int. Source: issue #42.\n\n"
                       "REQ-2: When a widget is removed, the widget table MUST drop its row. Source: issue #42.",
    "3. Decisions by the maintainers": "1. The table is named widgets, answered on 2026-11-20.",
    "4. Test plan": "TEST-1: WidgetTableTest.testColumns proves REQ-1.\n\nTEST-2: WidgetTableTest.testRemoved proves REQ-2.",
    "5. Where problems could occur": "A wrong size column would show operators a widget size that is not the real one, on a read of the table.",
}


def filled_record(tier=doclint.SHORT_TIER, sections=None):
    """The short record template on this branch with every placeholder
    answered, as the author writes it."""
    text = page("templates/short-record.md").replace("{issue}", "42").replace("{title}", "Widget table")
    text = text.replace("| Status | Draft, Approved or Superseded |", "| Status | Draft |")
    text = text.replace("| Version | {n} |", "| Version | 1 |")
    text = text.replace("| Author | {GitHub username} |", "| Author | octocat |")
    text = re.sub(r"\| Areas \| \{[^|]*\} \|", "| Areas | observability |", text)
    text = re.sub(r"\| Tier \| \{[^|]*\} \|", "| Tier | %s |" % tier, text)
    text = text.replace("{RFC 3339 date}", "2026-11-20").replace("{the id of the decision record behind this version, or None}", "None")
    text = text.replace("{the address `tools/chronitondb/doclint.py history --write` puts here}", "https://github.com/example/product/commits/line/" + RECORD)
    for title, body in dict(SECTIONS, **(sections or {})).items():
        text = re.sub(r"(## %s\n\n)\{.*?\}\n(?=\n## |$)" % re.escape(title), lambda match: match.group(1) + body + "\n", text, flags=re.S)
    return text


class ShortRecord(unittest.TestCase):

    def setUp(self):
        self.repo = tempfile.mkdtemp()
        self.git("init", "-q")
        for name in ("templates/short-record.md", "classification.md", "areas.md"):
            self.put("docs/process/" + name, page(name))
        self.put(OTHER_FILE.replace("WidgetTable", "Other"), "class Other {}\n")
        self.put(FLOOR_FILE.replace("Widget", "Old"), "class Old {}\n")
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
        full = os.path.join(self.repo, path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8") as handle:
            handle.write(text)

    def document(self):
        return run("document", "--repo", self.repo, "--templates", "line", "--source", "worktree", RECORD)

    def tier(self, *more):
        return run("tier", "--repo", self.repo, "--base", "line", "--source", "worktree", *more)

    def test_a_filled_record_passes(self):
        self.put(OTHER_FILE, "class WidgetTable {}\n")
        self.put(RECORD, filled_record())
        rc, out, err = self.document()
        self.assertEqual((rc, err), (0, ""))
        self.assertIn("documents 1 checked 0 failed", out)

    def test_a_tier_row_that_is_not_the_printed_line_fails(self):
        self.put(RECORD, filled_record(tier="Short: small"))
        rc, _, err = self.document()
        self.assertEqual(rc, 1)
        self.assertIn("It is the line 'doclint.py tier' prints for the change: '%s'" % doclint.SHORT_TIER, err)

    def test_a_record_of_a_change_on_the_floor_fails(self):
        self.put(FLOOR_FILE, "class Widget {}\n")
        self.put(RECORD, filled_record())
        rc, _, err = self.document()
        self.assertEqual(rc, 1)
        self.assertIn("the tier of the change is 'Full: 1 file the change touches is on the paths of the Critical floor' (%s)" % FLOOR_FILE, err)

    def test_a_record_missing_a_section_names_the_short_record_template(self):
        text = re.sub(r"## 4\. Test plan\n.*?(?=## 5\.)", "", filled_record(), flags=re.S)
        self.put(RECORD, text)
        rc, _, err = self.document()
        self.assertEqual(rc, 1)
        self.assertIn("no '## 4. Test plan' section. The short record template has it", err)

    def test_a_test_that_names_an_item_section_2_lacks_fails(self):
        self.put(RECORD, filled_record(sections={"4. Test plan": "TEST-1: WidgetTableTest.testColumns proves REQ-1 and REQ-2.\n\nTEST-2: WidgetTableTest.testOther proves REQ-3."}))
        rc, _, err = self.document()
        self.assertEqual(rc, 1)
        self.assertIn("TEST-2 names REQ-3, which section 2 does not define", err)

    def test_an_item_no_test_names_fails(self):
        self.put(RECORD, filled_record(sections={"4. Test plan": "TEST-1: WidgetTableTest.testColumns proves REQ-1."}))
        rc, _, err = self.document()
        self.assertEqual(rc, 1)
        self.assertIn("REQ-2 is named by no test of section 4", err)

    def test_a_test_that_names_no_item_fails(self):
        self.put(RECORD, filled_record(sections={"4. Test plan": "TEST-1: WidgetTableTest.testColumns proves REQ-1 and REQ-2.\n\nTEST-2: WidgetTableTest.testOther."}))
        rc, _, err = self.document()
        self.assertEqual(rc, 1)
        self.assertIn("TEST-2 names no REQ-n of section 2", err)

    def test_an_item_with_two_keywords_fails(self):
        self.put(RECORD, filled_record(sections={"2. What changes": "REQ-1: The widget table MUST have a name and MAY have a size. Source: issue #42.\n\nREQ-2: When a widget is removed, the widget table MUST drop its row. Source: issue #42."}))
        rc, _, err = self.document()
        self.assertEqual(rc, 1)
        self.assertIn("REQ-1 has 2 BCP 14 keywords", err)

    def test_where_problems_could_occur_saying_none_fails(self):
        self.put(RECORD, filled_record(sections={"5. Where problems could occur": "None."}))
        rc, _, err = self.document()
        self.assertEqual(rc, 1)
        self.assertIn("section 5 says only 'None.'", err)

    def test_the_tier_of_a_change_off_the_floor_is_short(self):
        self.put(OTHER_FILE, "class WidgetTable {}\n")
        rc, out, err = self.tier()
        self.assertEqual((rc, err, out), (0, "", doclint.SHORT_TIER + "\n"))

    def test_the_tier_of_a_change_on_the_floor_is_full_and_names_the_files(self):
        self.put(FLOOR_FILE, "class Widget {}\n")
        self.put(OTHER_FILE, "class WidgetTable {}\n")
        self.git("add", "-A")
        self.git("mv", FLOOR_FILE.replace("Widget", "Old"), "src/java/org/apache/cassandra/db/Old.java")
        rc, out, _ = self.tier("--source", "index")
        self.assertEqual(rc, 0)
        self.assertEqual(out.split("\n")[0], "Full: 2 files the change touches are on the paths of the Critical floor")
        self.assertIn("floor %s (Compaction)" % FLOOR_FILE, out)
        self.assertIn("floor %s (Compaction)" % FLOOR_FILE.replace("Widget", "Old"), out)
        self.assertNotIn(OTHER_FILE, out)

    def test_with_no_paths_on_the_line_the_tier_is_full(self):
        self.put("docs/process/classification.md", "# Classification of work\n")
        self.git("commit", "-q", "-a", "-m", "no paths")
        self.git("branch", "-f", "line")
        self.put(OTHER_FILE, "class WidgetTable {}\n")
        rc, out, _ = self.tier()
        self.assertEqual(rc, 0)
        self.assertTrue(out.startswith("Full: no paths of the Critical floor"), out)

    def test_a_change_that_removes_its_own_path_from_the_table_is_still_full(self):
        self.put(FLOOR_FILE, "class Widget {}\n")
        table = page("classification.md").replace("| `src/java/org/apache/cassandra/db/compaction/` | Compaction |\n", "")
        self.assertNotEqual(table, page("classification.md"))
        self.put("docs/process/classification.md", table)
        self.put(RECORD, filled_record())
        rc, out, _ = self.tier()
        self.assertEqual((rc, out.split("\n")[0]), (0, "Full: 1 file the change touches is on the paths of the Critical floor"))
        self.assertIn("floor %s (Compaction)" % FLOOR_FILE, out)
        rc, _, err = self.document()
        self.assertEqual(rc, 1)
        self.assertIn("the tier of the change is 'Full: 1 file", err)

    def test_a_pattern_of_the_table_matches_across_directories(self):
        self.put("src/java/org/chronitondb/widget/auth/Login.java", "class Login {}\n")
        rc, out, _ = self.tier()
        self.assertEqual(rc, 0)
        self.assertIn("floor src/java/org/chronitondb/widget/auth/Login.java (Authentication and authorisation)", out)

    def test_the_tier_without_a_base_is_a_usage_error(self):
        rc, _, _ = run("tier", "--repo", self.repo)
        self.assertEqual(rc, 2)


if __name__ == "__main__":
    unittest.main()
