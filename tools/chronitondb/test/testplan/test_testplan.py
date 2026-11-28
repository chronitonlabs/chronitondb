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
"""Tests of testplan.py: the test classes the impact analysis of a short
record names, and the coverage of the methods a pull request changes. Run
from the repository root:

    python3 -m unittest discover -s tools/chronitondb/test/testplan
"""

import os
import shutil
import subprocess
import sys
import tempfile
import unittest

TOOLS = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
TOOL = os.path.join(TOOLS, "testplan.py")

RECORD = """# Short record

## 3. Decisions by the maintainers

| Proving tests | Not this table |
|---|---|
| `NotNamedTest` | none |

## 4. Test plan

The surface matrix rows.

| Area or surface reached | How the change reaches it | Proving tests | Existing or new |
|---|---|---|---|
| `observability` | the view | `org.chronitondb.virtual.WidgetTableTest.testRows` and `WidgetNodesTest` | Existing |
| system_views listing | one more table | `SystemViewsKeyspaceTest`, `WidgetTableTest` | Existing |
| The upgrade path | a new table on one node | `WidgetUpgradeTest` | New |

- TEST-1: `LeftOutTest.testList`, outside the table.

## 5. Where problems could occur

| Proving tests |
|---|
| `AlsoLeftOutTest` |
"""

REPORT = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<!DOCTYPE report PUBLIC "-//JACOCO//DTD Report 1.1//EN" "report.dtd">
<report name="r">
  <package name="org/chronitondb/virtual">
    <class name="org/chronitondb/virtual/Widget" sourcefilename="Widget.java">
      <method name="&lt;init&gt;" desc="()V" line="5">
        <counter type="LINE" missed="0" covered="1"/>
        <counter type="COMPLEXITY" missed="0" covered="1"/>
      </method>
      <method name="rows" desc="()I" line="10">
        <counter type="LINE" missed="2" covered="2"/>
        <counter type="BRANCH" missed="1" covered="3"/>
        <counter type="COMPLEXITY" missed="1" covered="2"/>
      </method>
      <method name="untouched" desc="()V" line="20">
        <counter type="LINE" missed="1" covered="0"/>
        <counter type="COMPLEXITY" missed="1" covered="0"/>
      </method>
    </class>
    <sourcefile name="Widget.java">
      <line nr="5" mi="0" ci="2" mb="0" cb="0"/>
      <line nr="10" mi="0" ci="2" mb="0" cb="0"/>
      <line nr="12" mi="3" ci="0" mb="1" cb="1"/>
      <line nr="20" mi="2" ci="0" mb="0" cb="0"/>
    </sourcefile>
  </package>
  <package name="org/apache/cassandra/db">
    <class name="org/apache/cassandra/db/Stock" sourcefilename="Stock.java">
      <method name="read" desc="()V" line="3">
        <counter type="LINE" missed="0" covered="4"/>
        <counter type="COMPLEXITY" missed="0" covered="1"/>
      </method>
    </class>
    <sourcefile name="Stock.java">
      <line nr="3" mi="0" ci="2" mb="0" cb="0"/>
    </sourcefile>
  </package>
</report>
"""


def widget(lines):
    return "\n".join("// line %d" % number for number in range(1, lines + 1)) + "\n"


class Repository(unittest.TestCase):

    def setUp(self):
        self.repo = tempfile.mkdtemp()
        self.put("README", "line\n")
        self.put("test/unit/org/chronitondb/virtual/WidgetTableTest.java", "class WidgetTableTest {}\n")
        self.put("test/unit/org/apache/cassandra/db/virtual/SystemViewsKeyspaceTest.java", "class SystemViewsKeyspaceTest {}\n")
        self.put("test/distributed/org/chronitondb/virtual/test/WidgetNodesTest.java", "class WidgetNodesTest {}\n")
        self.put("test/unit/org/apache/cassandra/LeftOutTest.java", "class LeftOutTest {}\n")
        self.put("src/java/org/chronitondb/virtual/Widget.java", widget(25))
        self.put("src/java/org/apache/cassandra/db/Stock.java", widget(5))
        for args in (["init", "-q"], ["add", "-A"], ["commit", "-q", "-m", "line"], ["update-ref", "refs/remotes/origin/line", "HEAD"]):
            self.git(*args)

    def tearDown(self):
        shutil.rmtree(self.repo)

    def put(self, path, text):
        full = os.path.join(self.repo, path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8") as handle:
            handle.write(text)

    def git(self, *args):
        subprocess.run(["git", "-C", self.repo, "-c", "user.name=t", "-c", "user.email=t@example.org", "-c", "commit.gpgsign=false",
                        "-c", "core.hooksPath=/dev/null"] + list(args), check=True, capture_output=True)

    def commit(self):
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "change")

    def run_tool(self, *args):
        done = subprocess.run([sys.executable, TOOL] + list(args) + ["--repo", self.repo, "--base", "origin/line"],
                              capture_output=True, text=True, check=False)
        return done.returncode, done.stdout, done.stderr


class Impact(Repository):

    def test_the_proving_tests_of_the_impact_table_are_found_by_full_name_and_by_class_name(self):
        self.put("test/distributed/org/chronitondb/virtual/upgrade/WidgetUpgradeTest.java", "class WidgetUpgradeTest {}\n")
        self.put("docs/design/7-widget/short-record.md", RECORD)
        self.commit()
        rc, out, err = self.run_tool("impact")
        self.assertEqual(rc, 0, err)
        self.assertEqual(out.splitlines(), ["unit org.chronitondb.virtual.WidgetTableTest",
                                            "distributed org.chronitondb.virtual.test.WidgetNodesTest",
                                            "unit org.apache.cassandra.db.virtual.SystemViewsKeyspaceTest",
                                            "upgrade org.chronitondb.virtual.upgrade.WidgetUpgradeTest"])

    def test_a_name_with_no_class_is_an_error(self):
        self.put("docs/design/7-widget/short-record.md", RECORD)
        self.commit()
        rc, out, err = self.run_tool("impact")
        self.assertEqual(rc, 1)
        self.assertIn("names WidgetUpgradeTest, and no test class", err)
        self.assertIn("unit org.chronitondb.virtual.WidgetTableTest", out)

    def test_a_class_name_of_two_classes_is_an_error(self):
        self.put("test/distributed/org/chronitondb/virtual/upgrade/WidgetUpgradeTest.java", "class WidgetUpgradeTest {}\n")
        self.put("test/distributed/org/chronitondb/other/test/WidgetNodesTest.java", "class WidgetNodesTest {}\n")
        self.put("docs/design/7-widget/short-record.md", RECORD)
        self.commit()
        rc, _, err = self.run_tool("impact")
        self.assertEqual(rc, 1)
        self.assertIn("names WidgetNodesTest, which is the name of", err)

    def test_a_record_the_pull_request_does_not_touch_is_not_read(self):
        self.put("docs/design/7-widget/short-record.md", RECORD)
        self.commit()
        self.git("update-ref", "refs/remotes/origin/line", "HEAD")
        self.put("README", "changed\n")
        self.commit()
        self.assertEqual(self.run_tool("impact"), (0, "", ""))

    def test_a_record_of_the_old_form_names_nothing(self):
        self.put("docs/design/7-widget/short-record.md", "## 4. Test plan\n\n- TEST-1: `WidgetTableTest.testRows` proves REQ-1.\n")
        self.commit()
        rc, out, err = self.run_tool("impact")
        self.assertEqual((rc, out), (0, ""))
        self.assertIn("names no test class in an impact analysis table", err)


class Coverage(Repository):

    def test_the_methods_with_changed_lines_of_code_are_listed(self):
        changed = widget(25).replace("// line 12\n", "// line 12 changed\n").replace("// line 1\n", "// line 1 changed\n")
        self.put("src/java/org/chronitondb/virtual/Widget.java", changed)
        self.put("src/java/org/apache/cassandra/db/Stock.java", widget(5).replace("// line 3\n", "// line 3 changed\n"))
        self.commit()
        self.put("report.xml", REPORT)
        rc, out, err = self.run_tool("coverage", "--report", os.path.join(self.repo, "report.xml"))
        self.assertEqual((rc, err), (0, ""))
        self.assertIn("| `org.chronitondb.virtual.Widget.rows` | 2 of 4 | 3 of 4 | 3 | 4.1 |", out)
        self.assertIn("| `org.apache.cassandra.db.Stock.read` | 4 of 4 | 0 of 0 | 1 | stock method |", out)
        self.assertNotIn("untouched", out)
        self.assertNotIn("init", out)

    def test_a_high_score_is_marked(self):
        report = REPORT.replace('<counter type="COMPLEXITY" missed="1" covered="2"/>', '<counter type="COMPLEXITY" missed="4" covered="4"/>')
        report = report.replace('<counter type="LINE" missed="2" covered="2"/>', '<counter type="LINE" missed="4" covered="0"/>')
        self.put("src/java/org/chronitondb/virtual/Widget.java", widget(25).replace("// line 10\n", "// line 10 changed\n"))
        self.commit()
        self.put("report.xml", report)
        _, out, _ = self.run_tool("coverage", "--report", os.path.join(self.repo, "report.xml"))
        self.assertIn("| 8 | 72.0 (above 30) |", out)

    def test_no_changed_java_file_is_said(self):
        self.put("README", "changed\n")
        self.commit()
        self.put("report.xml", REPORT)
        rc, out, _ = self.run_tool("coverage", "--report", os.path.join(self.repo, "report.xml"))
        self.assertEqual(rc, 0)
        self.assertIn("changes no Java file under src/java", out)

    def test_a_report_that_cannot_be_read_fails(self):
        rc, _, err = self.run_tool("coverage", "--report", os.path.join(self.repo, "missing.xml"))
        self.assertEqual(rc, 2)
        self.assertIn("cannot be read", err)


if __name__ == "__main__":
    unittest.main()
