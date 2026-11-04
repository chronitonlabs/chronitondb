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
"""The class of a change, docs/process/classification.md: the Risk, Size,
Reach and Touches rows of a document, the sections of a feature spec its
class requires, the Not applicable line, the Where problems could occur
section, and the class rows of the plan, the milestone report and the
records. Run from the repository root:

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
SPEC = "docs/design/ABC-test-feature/feature-spec.md"
PLAN = "docs/design/ABC-test-feature/plan.md"
REPORT = "docs/design/ABC-test-feature/milestones/milestone-1.md"
FIX = "docs/design/42-a-fault/fix-record.md"
DESIGN = "docs/design/43-an-item/design-record.md"

# The text each section of a filled spec holds, by title.
BODIES = {
    "Purpose and scope": "The feature finds rows by the words they hold, for application developers.",
    "Non-goals": "- Ranking across tables, which no user asked for.",
    "Architecture": "One new index type on the replica, read through the stock query path.",
    "Context and scope": "Clients send CQL, the coordinator sends reads to replicas.",
    "Building blocks": "The index writer, the index reader and the query planner hook.",
    "Runtime view": "A replica read asks the index for row ids, then reads the rows.",
    "Data and formats": "One new sstable component per index.",
    "Cross cutting concepts": "Each limit has a setting and a metric.",
    "Deployment": "One new setting in the yaml file.",
    "Package dependencies and hook points": "The index package imports only the stock index interfaces.",
    "Feature class and switches": "Feature class: purely additive, because only new index types reach it.",
    "Feature requirements": "FREQ-ABC-001 (ubiquitous): The index MUST return every row whose text holds the word. Source: the issue.",
    "Where problems could occur": "A missed row would give a client a wrong result on a replica read, from the index reader.",
    "Test plan": "A scenario compares every query with stock filtering over the same rows, on each read path.",
    "Threat model": "This feature adds no new entry point, because only new index options reach it.",
    "Compatibility": "This feature changes no format, schema or protocol, because the component is new.",
    "On-disk format changes": "One new component, which an older reader leaves alone.",
    "Mixed-version cluster": "An older replica answers with stock filtering.",
    "Upgrade path and prerequisites": "Any 5.0 release, with no setting changed first.",
    "Rollback path": "Drop the index, then roll back the binaries.",
    "Runbook entries": "The index page of the operator runbook.",
    "Dependencies": "No new dependency.",
    "Risks": "| Id | Risk | Likelihood | Impact | Mitigation |\n|---|---|---|---|---|\n| R1 | A missed row | Low | High | The comparison scenario |",
    "Decisions": "- [0001](../../decisions/0001-initial-maintainers.md): who decides.",
    "Milestones outline": "1. The index answers one word queries.",
    "Prior art": "Stock Apache Cassandra 5.0 answers these queries with filtering, which we keep as the reference.",
    "Glossary": "| Term | Definition | Name in code, CQL and docs |\n|---|---|---|\n| Word | One token of a text | word |",
}
NOT_APPLICABLE = "Not applicable: this feature has no such part."


def run(*args):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = doclint.main(list(args))
    return rc, out.getvalue(), err.getvalue()


def template(name):
    with open(os.path.join(TEMPLATES, name), encoding="utf-8") as handle:
        return handle.read()


def quality_table():
    with open(os.path.join(ROOT, "docs", "process", "quality-requirements.md"), encoding="utf-8") as handle:
        lines = doclint.quality_lines(handle.read())
    rows = ["| Area | Line | Answer |", "|---|---|---|"]
    rows += ["| Quality | %s | Not relevant here, because the feature reads only |" % line for line in lines]
    return "\n".join(rows)


def spec(risk="Normal: a slow use case at worst, no floor applied",
         size="Normal: one index type on one read path",
         reach="One area: the index package only",
         touches="none", na=(), drop=(), bodies=None):
    """A feature spec in the template's headings, each section filled, or
    the Not applicable line for the titles in na, or left out for the
    titles in drop."""
    bodies = dict(BODIES, **(bodies or {}))
    bodies["Quality requirements"] = quality_table()
    lines = ["# Feature spec: Test feature", "", "| Field | Value |", "|---|---|"]
    values = {"Title": "Test feature", "Document type": "Specification and description (ISO/IEC/IEEE 15289)",
              "Status": "Draft", "Version": "1", "Author": "Architect: millerjp",
              "Approver": "The maintainer who merges the pull request", "References": "Issue 61",
              "Risk": risk, "Size": size, "Reach": reach, "Touches": touches}
    for field, value in values.items():
        lines.append("| %s | %s |" % (field, value))
    lines += ["", "## Contents", ""]
    for raw in template("feature-spec.md").split("\n"):
        match = re.match(r"^(#{2,3}) (.*)$", raw)
        if not match or match.group(2) == "Contents":
            continue
        heading = match.group(2)
        title = re.sub(r"^[0-9.]+\s+", "", heading)
        if title in drop:
            continue
        lines += ["", raw, ""]
        lines.append(NOT_APPLICABLE if title in na else bodies[title])
    return "\n".join(lines) + "\n"


class Repo(unittest.TestCase):

    def setUp(self):
        self.repo = tempfile.mkdtemp()
        self.git("init", "-q")
        os.makedirs(os.path.join(self.repo, "docs", "process", "templates"))
        for name in os.listdir(TEMPLATES):
            self.put("docs/process/templates/" + name, template(name))
        with open(os.path.join(ROOT, "docs", "process", "quality-requirements.md"), encoding="utf-8") as handle:
            self.put("docs/process/quality-requirements.md", handle.read())
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
        if path.startswith("docs/design/"):
            run("index", "--write", full)

    def document(self, path):
        return run("document", "--repo", self.repo, "--templates", "line", "--source", "worktree", path)

    def spec_errors(self, **kwargs):
        self.put(SPEC, spec(**kwargs))
        rc, out, err = self.document(SPEC)
        return rc, err


class SpecClass(Repo):

    def test_a_normal_spec_with_every_section_passes(self):
        self.assertEqual(self.spec_errors(), (0, ""))

    def test_a_normal_spec_may_say_not_applicable_where_its_class_allows(self):
        na = ("Runtime view", "Data and formats", "Cross cutting concepts", "Deployment",
              "Quality requirements", "Threat model", "Dependencies", "Risks", "Glossary")
        self.assertEqual(self.spec_errors(na=na), (0, ""))

    def test_a_parent_that_says_not_applicable_covers_its_left_out_subsections(self):
        drop = ("On-disk format changes", "Mixed-version cluster", "Upgrade path and prerequisites",
                "Rollback path", "Runbook entries")
        rc, err = self.spec_errors(na=("Compatibility",), drop=drop)
        self.assertEqual((rc, err), (0, ""))

    def test_a_required_section_may_not_say_not_applicable(self):
        rc, err = self.spec_errors(na=("Building blocks",))
        self.assertEqual(rc, 1)
        self.assertIn("section 2.2 Building blocks says Not applicable, and the class requires it (Normal size). Write it in full (classification.md)", err)

    def test_where_problems_could_occur_is_never_not_applicable(self):
        rc, err = self.spec_errors(na=("Where problems could occur",))
        self.assertEqual(rc, 1)
        self.assertIn("section 4 Where problems could occur says Not applicable, and the class requires it (every class)", err)

    def test_where_problems_could_occur_is_never_none_or_low(self):
        for text in ("None.", "Low", "n/a"):
            rc, err = self.spec_errors(bodies={"Where problems could occur": text})
            self.assertEqual(rc, 1, text)
            self.assertIn("section 4 Where problems could occur says only '%s'. It names what could break" % text, err)
        rc, err = self.spec_errors(bodies={"Test plan": "Low risk."})
        self.assertEqual(rc, 1)
        self.assertIn("section 4.1 Test plan says only 'Low risk.'", err)

    def test_where_problems_could_occur_needs_its_own_text(self):
        rc, err = self.spec_errors(bodies={"Where problems could occur": ""})
        self.assertEqual(rc, 1)
        self.assertIn("section 4 Where problems could occur is empty. It names what could break, how a user would see it and the tests that would catch it, and its test plan alone is not enough (classification.md)", err)

    def test_non_goals_are_required_at_every_size(self):
        na = ("Context and scope", "Building blocks", "Runtime view", "Data and formats", "Cross cutting concepts",
              "Deployment", "Package dependencies and hook points", "Quality requirements", "Threat model",
              "Compatibility", "Dependencies", "Risks", "Milestones outline", "Glossary")
        drop = ("On-disk format changes", "Mixed-version cluster", "Upgrade path and prerequisites",
                "Rollback path", "Runbook entries")
        size = "Low Hanging Fruit: one option on one class"
        rc, err = self.spec_errors(size=size, na=na + ("Non-goals",), drop=drop)
        self.assertEqual(rc, 1)
        self.assertIn("section Non-goals says Not applicable, and the class requires it (every class). Write it in full (classification.md)", err)
        rc, err = self.spec_errors(size=size, na=na, drop=drop, bodies={"Non-goals": ""})
        self.assertEqual(rc, 1)
        self.assertIn("section Non-goals is empty. It names what the feature will not do, each with a short reason, at every class (classification.md)", err)
        rc, err = self.spec_errors(size=size, na=na, drop=drop + ("Non-goals",))
        self.assertEqual(rc, 1)
        self.assertIn("no '### Non-goals' section. The feature spec template has it", err)

    def test_the_no_format_statement_replaces_only_on_disk_formats_where_compatibility_is_required(self):
        drop = ("On-disk format changes", "Mixed-version cluster", "Upgrade path and prerequisites",
                "Rollback path", "Runbook entries")
        rc, err = self.spec_errors(risk="Critical: a wrong result, Correctness", drop=drop)
        self.assertEqual(rc, 1)
        self.assertNotIn("no '### 7.1 On-disk format changes' section", err)
        self.assertIn("no '### 7.2 Mixed-version cluster' section. The feature spec template has it", err)
        self.assertIn("no '### 7.4 Rollback path' section. The feature spec template has it", err)
        rc, err = self.spec_errors(touches="stock behaviour", drop=drop)
        self.assertEqual(rc, 1)
        self.assertIn("no '### 7.2 Mixed-version cluster' section", err)
        self.assertEqual(self.spec_errors(risk="Critical: a wrong result, Correctness", drop=("On-disk format changes",)), (0, ""))
        self.assertEqual(self.spec_errors(drop=drop), (0, ""))

    def test_every_form_of_not_applicable_is_a_claim(self):
        # V1: a comma, a full stop, a dash, a colon, the end of the line or
        # because, since or as after the words make a claim, in every
        # section the class requires.
        forms = ("Not applicable, the change is internal only.",
                 "Not applicable. The change is internal only.",
                 "Not applicable - the change is internal only",
                 "Not applicable because the change is internal only.",
                 "Not applicable since the change is internal only.",
                 "Not applicable as the change is internal only.",
                 "Not applicable")
        sections = (("Where problems could occur", "section 4 Where problems could occur says Not applicable"),
                    ("Decisions", "section 10 Decisions says Not applicable"),
                    ("Building blocks", "section 2.2 Building blocks says Not applicable"),
                    ("Non-goals", "section Non-goals says Not applicable"))
        for form in forms:
            for section, finding in sections:
                rc, err = self.spec_errors(bodies={section: form})
                self.assertEqual(rc, 1, (section, form))
                self.assertIn(finding, err, (section, form))
        rc, err = self.spec_errors(bodies={"Glossary": "Not applicable, no terms beyond stock ones."})
        self.assertEqual(rc, 1)
        self.assertIn("section Glossary says Not applicable, but write it as the one line 'Not applicable: <reason>'", err)

    def test_text_that_only_starts_with_not_applicable_is_content(self):
        rc, err = self.spec_errors(bodies={"Deployment": "Not applicable to clusters without the index: they see no change, and operators set nothing."})
        self.assertEqual((rc, err), (0, ""))
        rc, err = self.spec_errors(bodies={"Deployment": "The tool prints this when the index is off:\n\n```\nNot applicable: the index is off\n```"})
        self.assertEqual((rc, err), (0, ""))

    def test_challenging_size_requires_every_section(self):
        rc, err = self.spec_errors(size="Challenging: three read paths and a new format", na=("Glossary", "Runtime view"))
        self.assertEqual(rc, 1)
        self.assertIn("section Glossary says Not applicable, and the class requires it (Challenging size)", err)
        self.assertIn("section 2.3 Runtime view says Not applicable, and the class requires it (Challenging size)", err)

    def test_low_hanging_fruit_needs_only_the_sections_every_class_has(self):
        na = ("Context and scope", "Building blocks", "Runtime view", "Data and formats", "Cross cutting concepts",
              "Deployment", "Package dependencies and hook points", "Quality requirements", "Threat model",
              "Compatibility", "Dependencies", "Risks", "Milestones outline", "Glossary")
        drop = ("On-disk format changes", "Mixed-version cluster", "Upgrade path and prerequisites",
                "Rollback path", "Runbook entries")
        self.assertEqual(self.spec_errors(size="Low Hanging Fruit: one option on one class", na=na, drop=drop), (0, ""))

    def test_cross_cutting_reach_requires_dependencies_risks_and_milestones(self):
        rc, err = self.spec_errors(reach="Cross-cutting: the index, the planner and streaming", na=("Risks",))
        self.assertEqual(rc, 1)
        self.assertIn("section 9 Risks says Not applicable, and the class requires it (Cross-cutting reach)", err)

    def test_critical_risk_requires_the_threat_model_and_compatibility(self):
        rc, err = self.spec_errors(risk="Critical: a wrong result, Correctness", na=("Threat model",))
        self.assertEqual(rc, 1)
        self.assertIn("section 6 Threat model says Not applicable, and the class requires it (Critical risk)", err)

    def test_critical_risk_requires_dependencies_for_a_new_dependency(self):
        rc, err = self.spec_errors(risk="Critical: a wrong result, Correctness", touches="new dependency", na=("Dependencies",))
        self.assertEqual(rc, 1)
        self.assertIn("section 8 Dependencies says Not applicable, and the class requires it (Critical risk with a new dependency). Write it in full (classification.md)", err)
        self.assertEqual(self.spec_errors(risk="Critical: a wrong result, Correctness", na=("Dependencies",)), (0, ""))

    def test_normal_risk_requires_what_touches_names(self):
        rc, err = self.spec_errors(touches="public interface (CQL), new input or privilege, new dependency",
                                   na=("Threat model", "Compatibility", "Dependencies"),
                                   drop=("On-disk format changes", "Mixed-version cluster", "Upgrade path and prerequisites",
                                         "Rollback path", "Runbook entries"))
        self.assertEqual(rc, 1)
        self.assertIn("section 6 Threat model says Not applicable, and the class requires it (Normal risk with new input or privilege)", err)
        self.assertIn("section 7 Compatibility says Not applicable, and the class requires it (Normal risk touching public interface)", err)
        self.assertIn("section 8 Dependencies says Not applicable, and the class requires it (Normal risk with a new dependency)", err)

    def test_a_not_applicable_line_gives_a_reason(self):
        rc, err = self.spec_errors(bodies={"Glossary": "Not applicable: none"}, na=())
        self.assertEqual(rc, 1)
        self.assertIn("section Glossary says Not applicable, but its reason has fewer than 3 words", err)
        rc, err = self.spec_errors(bodies={"Glossary": "Not applicable"})
        self.assertEqual(rc, 1)
        self.assertIn("section Glossary says Not applicable, but write it as the one line 'Not applicable: <reason>'", err)

    def test_an_empty_section_is_refused(self):
        rc, err = self.spec_errors(bodies={"Deployment": ""})
        self.assertEqual(rc, 1)
        self.assertIn("section 2.6 Deployment is empty. Write it, or the one line 'Not applicable: <reason>'", err)

    def test_the_class_rows_have_their_form(self):
        rc, err = self.spec_errors(risk="Medium: a slow query", size="Normal", reach="Everywhere: all of it")
        self.assertEqual(rc, 1)
        self.assertIn("the 'Risk' row is 'Medium: a slow query'. It is the level, one of Critical, Normal, Low, then a colon and the reason (classification.md)", err)
        self.assertIn("the 'Size' row is 'Normal'. It is the level", err)
        self.assertIn("the 'Reach' row is 'Everywhere: all of it'. It is the level, one of One area, Cross-cutting", err)

    def test_a_level_needs_its_reason(self):
        rc, err = self.spec_errors(risk="Normal: slow")
        self.assertEqual(rc, 1)
        self.assertIn("the 'Risk' row gives no reason after 'Normal:'. Write the level, a colon and a reason of 3 words or more (classification.md)", err)

    def test_an_unreadable_class_counts_as_the_strictest(self):
        rc, err = self.spec_errors(size="Huge: very big indeed", na=("Glossary",))
        self.assertEqual(rc, 1)
        self.assertIn("section Glossary says Not applicable, and the class requires it (Byzantine size)", err)

    def test_touches_names_only_the_seven_phrases_or_none(self):
        rc, err = self.spec_errors(touches="the planner")
        self.assertEqual(rc, 1)
        self.assertIn("the 'Touches' row names 'the planner', which is none of: public interface, stock behaviour, new input or privilege, new dependency, shared state, request path, new feature or switch, or none (classification.md)", err)

    def test_touches_names_what_a_code_review_adds_a_lens_for(self):
        rc, err = self.spec_errors(touches="shared state, request path and new feature or switch")
        self.assertNotIn("the 'Touches' row", err)

    def test_the_floor_keeps_a_public_interface_off_low_risk(self):
        rc, err = self.spec_errors(risk="Low: documentation only change", touches="public interface (yaml)",
                                   na=("Compatibility",),
                                   drop=("On-disk format changes", "Mixed-version cluster", "Upgrade path and prerequisites",
                                         "Rollback path", "Runbook entries"))
        self.assertEqual(rc, 1)
        self.assertIn("the risk is Low, and Touches names public interface. A change that touches a public interface or stock behaviour is at least Normal risk (classification.md, The floor)", err)

    def test_a_missing_class_row_is_refused(self):
        text = spec().replace("| Touches | none |\n", "")
        self.put(SPEC, text)
        rc, _, err = self.document(SPEC)
        self.assertEqual(rc, 1)
        self.assertIn("the document control table has no 'Touches' row", err)


def filled(name, replacements):
    """A template with its class rows set and every other placeholder
    answered."""
    text = template(name)
    for old, new in replacements:
        text = text.replace(old, new)
    text = re.sub(r"^\| Risk \|.*\|$", "| Risk | Normal: a slow use case at worst |", text, flags=re.M)
    text = re.sub(r"^\| Size \|.*\|$", "| Size | Normal: one index type only |", text, flags=re.M)
    text = re.sub(r"^\| Reach \|.*\|$", "| Reach | One area: the index package only |", text, flags=re.M)
    text = re.sub(r"^\| Touches \|.*\|$", "| Touches | none |", text, flags=re.M)
    text = text.replace("| Status | Draft, Approved or Superseded |", "| Status | Draft |")
    return re.sub(r"\{[^{}]*\}", "a value written by the author for the test", text)


class OtherDocuments(Repo):

    def class_errors(self, path, text):
        self.put(path, text)
        _, _, err = self.document(path)
        return [line for line in err.splitlines() if "Risk" in line or "risk" in line or "class" in line
                or "Where problems" in line or "Test plan" in line or "Touches" in line]

    def test_a_plan_repeats_the_feature_spec_class(self):
        self.put(SPEC, spec())
        self.assertEqual(self.class_errors(PLAN, filled("plan.md", [])), [])
        text = filled("plan.md", []).replace("| Risk | Normal: a slow use case at worst |", "| Risk | Critical: a wrong result could reach clients |")
        errors = self.class_errors(PLAN, text)
        self.assertTrue(any("the risk is Critical, and the feature spec %s says Normal. The plan repeats the feature spec's class (classification.md)" % SPEC in e for e in errors), errors)

    def test_a_milestone_report_repeats_the_feature_spec_class(self):
        self.put(SPEC, spec())
        text = filled("milestone-report.md", []).replace("| Reach | One area: the index package only |", "| Reach | Cross-cutting: three subsystems at once |")
        errors = self.class_errors(REPORT, text)
        self.assertTrue(any("the reach is Cross-cutting, and the feature spec %s says One area. The milestone report repeats" % SPEC in e for e in errors), errors)

    def test_a_fix_record_writes_where_problems_could_occur(self):
        good = filled("fix-record.md", [])
        self.assertEqual(self.class_errors(FIX, good), [])
        text = re.sub(r"(## Where problems could occur\n\n)[^\n]*", r"\1Not applicable: the fix is a small one.", good)
        errors = self.class_errors(FIX, text)
        self.assertTrue(any("section Where problems could occur says Not applicable. A fix record writes it in full (classification.md)" in e for e in errors), errors)
        for form in ("Not applicable, the fix is a small one.", "Not applicable. The fix is small.",
                     "Not applicable - the fix is small", "Not applicable because the fix is small."):
            text = re.sub(r"(## Where problems could occur\n\n)[^\n]*", lambda m: m.group(1) + form, good)
            errors = self.class_errors(FIX, text)
            self.assertTrue(any("section Where problems could occur says Not applicable" in e for e in errors), (form, errors))
        text = re.sub(r"(## Where problems could occur\n\n)[^\n]*", r"\1None.", good)
        errors = self.class_errors(FIX, text)
        self.assertTrue(any("section Where problems could occur says only 'None.'" in e for e in errors), errors)

    def test_a_design_record_of_a_spec_item_may_point_to_the_spec(self):
        good = filled("design-record.md", [])
        text = re.sub(r"(## Where problems could occur\n\n)[^\n]*\n\n### Test plan\n\n[^\n]*\n", r"\1Not applicable: section 4 of the feature spec covers this item.\n", good)
        errors = self.class_errors(DESIGN, text)
        self.assertTrue(any("unless its References row links the feature spec that covers it" in e for e in errors), errors)
        text = re.sub(r"^\| References \|.*\|$", "| References | Issue #43. Feature spec docs/design/ABC-test-feature/feature-spec.md |", text, flags=re.M)
        self.assertEqual(self.class_errors(DESIGN, text), [])

    def test_the_floor_applies_to_a_record(self):
        text = filled("fix-record.md", []).replace("| Risk | Normal: a slow use case at worst |", "| Risk | Low: a test only change |")
        text = text.replace("| Touches | none |", "| Touches | stock behaviour |")
        errors = self.class_errors(FIX, text)
        self.assertTrue(any("the risk is Low, and Touches names stock behaviour" in e for e in errors), errors)


if __name__ == "__main__":
    unittest.main()
