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
"""The rules of a feature spec, a plan and a milestone report that the
class tests do not reach, docs/process/additive.md and
quality-requirements.md: the feature requirements and their ids, the
feature class line, the quality checklist, the threat model and the
dependencies of a feature spec, the items, acceptance criteria and
traceability of a plan, the Requirements delivered table of a milestone
report, and the clarification marker no document keeps. Run from the
repository root:

    python3 -m unittest discover -s tools/chronitondb/test/doclint
"""

import os
import re
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from test_class import PLAN, REPORT, SPEC, Repo, filled, spec, template  # noqa: E402

DELIVERY_PLAN = "docs/design/ABC-test-feature/delivery-plan.md"
NOTES = "docs/design/ABC-test-feature/notes.md"
REQUIREMENT = "FREQ-ABC-001 (ubiquitous): The index MUST return every row whose text holds the word. Source: the issue."
SECOND = "FREQ-ABC-002 (event): When a row is deleted, the index MUST drop its words. Source: the issue."
CRITERION = "The index MUST return every row whose text holds the word."


def line_of(text, start):
    """The whole line of a template that starts with the given words."""
    return re.search(r"^%s.*$" % re.escape(start), text, re.M).group(0)


def quality_row(text, number):
    """The whole row of the quality table of a spec, counted from 0."""
    return [line for line in text.split("\n") if line.startswith("| Quality | ")][number]


class FeatureSpec(Repo):

    def text_errors(self, text):
        self.put(SPEC, text)
        rc, _, err = self.document(SPEC)
        return rc, err

    def requirement_errors(self, *requirements):
        return self.spec_errors(bodies={"Feature requirements": "\n".join(requirements)})

    # The feature requirements and their ids.

    def test_a_requirement_with_two_key_words_fails(self):
        rc, err = self.requirement_errors("FREQ-ABC-001 (ubiquitous): The index MUST return every row and SHOULD log the query. Source: the issue.")
        self.assertEqual(rc, 1)
        self.assertIn("FREQ-ABC-001 has 2 BCP 14 keywords, a requirement has exactly one (split it)", err)

    def test_a_requirement_with_no_key_word_no_shape_or_no_source_fails(self):
        rc, err = self.requirement_errors("FREQ-ABC-001 (ubiquitous): The index returns every row whose text holds the word. Source: the issue.")
        self.assertIn("FREQ-ABC-001 has 0 BCP 14 keywords, a requirement has exactly one (split it)", err)
        rc, err = self.requirement_errors("FREQ-ABC-001 (ubiquitous): Every row whose text holds the word MUST be returned. Source: the issue.")
        self.assertIn("FREQ-ABC-001 is in none of the five EARS shapes (The, When, While, Where, If then)", err)
        rc, err = self.requirement_errors("FREQ-ABC-001 (ubiquitous): The index MUST return every row whose text holds the word.")
        self.assertIn("FREQ-ABC-001 has no source", err)

    def test_a_requirement_id_carries_the_key_of_its_feature(self):
        rc, err = self.requirement_errors(REQUIREMENT.replace("FREQ-ABC-001", "FREQ-XYZ-001"))
        self.assertEqual(rc, 1)
        self.assertIn("FREQ-XYZ-001 uses the key XYZ, this feature's key is ABC", err)

    def test_a_requirement_id_has_three_digits(self):
        rc, err = self.requirement_errors(REQUIREMENT, SECOND.replace("FREQ-ABC-002", "FREQ-ABC-2"))
        self.assertEqual(rc, 1)
        self.assertIn("a requirement id is FREQ-<KEY>-nnn, the feature key and three digits", err)

    def test_a_requirement_id_is_defined_once(self):
        rc, err = self.requirement_errors(REQUIREMENT, "", SECOND.replace("FREQ-ABC-002", "FREQ-ABC-001"))
        self.assertEqual(rc, 1)
        self.assertRegex(err, r"FREQ-ABC-001 is defined twice, first on line [0-9]+")

    def test_a_spec_defines_a_requirement(self):
        rc, err = self.requirement_errors("The index returns every row whose text holds the word.")
        self.assertEqual(rc, 1)
        self.assertIn("section 3 defines no feature requirement FREQ-<KEY>-nnn", err)

    def test_two_good_requirements_pass(self):
        self.assertEqual(self.requirement_errors(REQUIREMENT, "", SECOND), (0, ""))

    # The feature class line.

    def test_section_2_8_gives_the_feature_class(self):
        for body in ("The feature is additive.", "Feature class: additive, because only new index types reach it.",
                     "Feature class: purely additive."):
            rc, err = self.spec_errors(bodies={"Feature class and switches": body})
            self.assertEqual(rc, 1, body)
            self.assertIn("section 2.8 has no line 'Feature class: <purely additive or behaviour-changing>, because <reason>.'", err)
        body = "Feature class: behaviour-changing, because a stock query returns other rows."
        self.assertEqual(self.spec_errors(bodies={"Feature class and switches": body}), (0, ""))

    # The quality checklist.

    def test_a_missing_quality_row_fails(self):
        good = spec()
        row = quality_row(good, 0)
        line = row.split(" | ")[1]
        rc, err = self.text_errors(good.replace(row + "\n", ""))
        self.assertEqual(rc, 1)
        self.assertIn("the quality table has no row '%s' of quality-requirements.md" % line, err)

    def test_every_quality_row_of_the_page_is_asked_for(self):
        good = spec()
        rows = [line for line in good.split("\n") if line.startswith("| Quality | ")]
        self.assertGreater(len(rows), 3)
        for row in rows:
            rc, err = self.text_errors(good.replace(row + "\n", ""))
            self.assertIn("the quality table has no row '%s' of quality-requirements.md" % row.split(" | ")[1], err)

    def test_a_quality_row_with_no_answer_fails(self):
        good = spec()
        row = quality_row(good, 1)
        line = row.split(" | ")[1]
        for answer in ("", "{FREQ ids, or the reason it does not apply}"):
            rc, err = self.text_errors(good.replace(row, "| Quality | %s | %s |" % (line, answer)))
            self.assertEqual(rc, 1, answer)
            self.assertIn("the quality line '%s' has neither FREQ ids nor a reason it does not apply" % line, err)

    def test_a_quality_row_names_requirements_the_spec_defines(self):
        good = spec()
        row = quality_row(good, 2)
        line = row.split(" | ")[1]
        rc, err = self.text_errors(good.replace(row, "| Quality | %s | FREQ-ABC-001, FREQ-ABC-009 |" % line))
        self.assertEqual(rc, 1)
        self.assertIn("the quality line '%s' names FREQ-ABC-009, which section 3 does not define" % line, err)
        self.assertNotIn("names FREQ-ABC-001", err)
        self.assertEqual(self.text_errors(good.replace(row, "| Quality | %s | FREQ-ABC-001 |" % line)), (0, ""))

    # The threat model and the dependencies.

    def test_the_threat_model_has_a_row_or_the_no_entry_point_statement(self):
        rc, err = self.spec_errors(bodies={"Threat model": "Only new index options reach the feature."})
        self.assertEqual(rc, 1)
        self.assertIn("the threat model has no STRIDE row and not the statement \"This feature adds no new entry point\" with its reason", err)
        table = "| Threat | Entry point | Mitigation |\n|---|---|---|\n| Tampering | The index option | FREQ-ABC-007 |"
        rc, err = self.spec_errors(bodies={"Threat model": table})
        self.assertIn("the threat model names FREQ-ABC-007, which section 3 does not define", err)

    def test_the_dependencies_say_none_or_give_each_library_its_category(self):
        rc, err = self.spec_errors(bodies={"Dependencies": "One library is added."})
        self.assertEqual(rc, 1)
        self.assertRegex(err, r"section [0-9]+ lists no library and does not say \"No new dependency\"")
        head = "| Library | Version | ASF category | Why |\n|---|---|---|---|\n"
        rc, err = self.spec_errors(bodies={"Dependencies": head + "| somelib | 1.2.3 | Category X | It parses text |"})
        self.assertIn("somelib is ASF category X, which the project refuses (compliance.md)", err)
        rc, err = self.spec_errors(bodies={"Dependencies": head + "| somelib | 1.2.3 | unknown | It parses text |"})
        self.assertIn("somelib has no ASF category A or B (compliance.md)", err)
        self.assertEqual(self.spec_errors(bodies={"Dependencies": head + "| somelib | 1.2.3 | Category A | It parses text |"}), (0, ""))

    def test_a_spec_lives_in_a_directory_named_for_its_key(self):
        path = "docs/design/test-feature/feature-spec.md"
        self.put(path, spec())
        _, _, err = self.document(path)
        self.assertIn("a feature spec lives in docs/design/<KEY>-<slug>/, KEY 3 to 5 capital letters and a lower case slug, found docs/design/test-feature", err)


class Plan(Repo):
    """A plan in the template's form, with one item that delivers the one
    requirement of the feature spec."""

    WORDS = ("Item", "FREQ", "acceptance", "criterion", "traceability", "feature spec at")

    def plan(self, title="### Item 1: The index reader", delivers="- **Delivers:** FREQ-ABC-001",
             criteria=(CRITERION,), traced=("| FREQ-ABC-001 | Item 1 | Item 2 |",)):
        text = template("plan.md")
        table = line_of(text, "| FREQ |")
        accepted = "- **Acceptance criteria:**" + "".join("\n  %d. %s" % (number, criterion) for number, criterion in enumerate(criteria, 1))
        return filled("plan.md", [(line_of(text, "### Item "), title),
                                  (line_of(text, "- **Delivers:**"), delivers),
                                  (line_of(text, "- **Acceptance criteria:**"), accepted),
                                  (table + "\n|---|---|---|", "\n".join((table, "|---|---|---|") + tuple(traced)))])

    def plan_errors(self, text, with_spec=True):
        if with_spec:
            self.put(SPEC, spec())
        self.put(PLAN, text)
        _, _, err = self.document(PLAN)
        return [line for line in err.splitlines() if any(word in line for word in self.WORDS)]

    def test_a_plan_that_traces_every_requirement_passes(self):
        self.assertEqual(self.plan_errors(self.plan()), [])

    def test_a_plan_has_an_item(self):
        errors = self.plan_errors(self.plan(title="### The index reader"))
        self.assertTrue(any("the plan has no '### Item <n>: <title>' entry" in e for e in errors), errors)

    def test_an_item_delivers_a_requirement_of_the_spec(self):
        errors = self.plan_errors(self.plan(delivers="- **Depends on:** none"))
        self.assertTrue(any("Item 1: The index reader has no '- **Delivers:**' line" in e for e in errors), errors)
        errors = self.plan_errors(self.plan(delivers="- **Delivers:** the reader"))
        self.assertTrue(any("Item 1: The index reader delivers no FREQ id" in e for e in errors), errors)
        errors = self.plan_errors(self.plan(delivers="- **Delivers:** FREQ-ABC-001, FREQ-ABC-004"))
        self.assertTrue(any("Item 1: The index reader delivers FREQ-ABC-004, which the feature spec does not define" in e for e in errors), errors)

    def test_an_item_has_acceptance_criteria_each_one_requirement(self):
        errors = self.plan_errors(self.plan(criteria=()))
        self.assertTrue(any("Item 1: The index reader has no acceptance criteria" in e for e in errors), errors)
        errors = self.plan_errors(self.plan(criteria=(CRITERION, "The index MUST return every row and SHOULD log the query.")))
        self.assertTrue(any("Item 1 criterion 2 has 2 BCP 14 keywords, an acceptance criterion has exactly one (split it)" in e for e in errors), errors)
        self.assertFalse(any("Item 1 criterion 1" in e for e in errors), errors)

    def test_every_requirement_maps_to_an_item(self):
        errors = self.plan_errors(self.plan(traced=()))
        self.assertTrue(any("FREQ-ABC-001 of the feature spec maps to no item in the traceability table. A FREQ with no item blocks approval" in e for e in errors), errors)
        errors = self.plan_errors(self.plan(traced=("| FREQ-ABC-001 |  | Item 2 |",)))
        self.assertTrue(any("FREQ-ABC-001 of the feature spec maps to no item" in e for e in errors), errors)

    def test_the_traceability_table_names_requirements_of_the_spec(self):
        errors = self.plan_errors(self.plan(traced=("| FREQ-ABC-001 | Item 1 | Item 2 |", "| FREQ-ABC-005 | Item 1 | Item 2 |")))
        self.assertTrue(any("the traceability table names FREQ-ABC-005, which the feature spec does not define" in e for e in errors), errors)

    def test_a_plan_needs_its_feature_spec(self):
        errors = self.plan_errors(self.plan(), with_spec=False)
        self.assertTrue(any("no feature spec at %s to trace the plan to" % SPEC in e for e in errors), errors)


class Milestone(Repo):
    """A milestone report in the template's form, with one row in its
    Requirements delivered table."""

    WORDS = ("delivered", "status of", "final milestone")

    def report(self, status):
        text = template("milestone-report.md")
        row = "| FREQ-ABC-001 | Item 1, pull request 12 | The reader scenarios | %s |" % status
        return filled("milestone-report.md", [(line_of(text, "| {FREQ-<KEY>-nnn}"), row)])

    def delivery_plan(self, *numbers):
        return "# Delivery plan: Test feature\n\n## 1. Milestones\n\n" + "".join("### Milestone %d: A step\n\nIts items.\n\n" % n for n in numbers)

    def report_errors(self, status, milestones=(1,)):
        if milestones:
            self.put(DELIVERY_PLAN, self.delivery_plan(*milestones))
        self.put(REPORT, self.report(status))
        _, _, err = self.document(REPORT)
        return [line for line in err.splitlines() if any(word in line for word in self.WORDS)]

    def test_each_allowed_status_passes_before_the_final_milestone(self):
        for status in ("delivered", "not delivered", "delivered in part, as planned", "Delivered"):
            self.assertEqual(self.report_errors(status, milestones=(1, 2)), [], status)

    def test_another_status_fails(self):
        for status in ("done", "delivered in part", "mostly delivered"):
            errors = self.report_errors(status, milestones=(1, 2))
            self.assertTrue(any("the status of FREQ-ABC-001 is '%s', it is delivered, not delivered, or delivered in part, as planned" % status in e for e in errors), (status, errors))

    def test_the_final_milestone_delivers_nothing_in_part(self):
        errors = self.report_errors("delivered in part, as planned", milestones=(1,))
        self.assertTrue(any("FREQ-ABC-001 is delivered in part in milestone 1, the feature's final milestone in %s. The final milestone delivers each requirement or reports it not delivered with its reason in Deviations" % DELIVERY_PLAN in e for e in errors), errors)
        for status in ("delivered", "not delivered"):
            self.assertEqual(self.report_errors(status, milestones=(1,)), [], status)

    def test_delivered_in_part_needs_the_delivery_plan_to_tell_the_final_milestone(self):
        errors = self.report_errors("delivered in part, as planned", milestones=())
        self.assertTrue(any("a requirement is delivered in part, and there is no delivery plan at %s to tell whether this is the feature's final milestone" % DELIVERY_PLAN in e for e in errors), errors)
        self.put(DELIVERY_PLAN, "# Delivery plan: Test feature\n\n## 1. Milestones\n\nNone yet.\n")
        self.put(REPORT, self.report("delivered in part, as planned"))
        _, _, err = self.document(REPORT)
        self.assertIn("the milestone's number or the delivery plan's milestones cannot be read to tell whether this is the final milestone", err)


class Marker(Repo):
    """No document merges with a clarification marker left in it."""

    MESSAGE = "a clarification marker is left: every [NEEDS CLARIFICATION: ...] is answered and removed before the document merges"

    def test_a_marker_in_a_document_of_a_template_fails(self):
        body = "The index reader [NEEDS CLARIFICATION: which read path] and the query planner hook."
        rc, err = self.spec_errors(bodies={"Building blocks": body})
        self.assertEqual(rc, 1)
        self.assertIn(self.MESSAGE, err)
        self.assertEqual(self.spec_errors(bodies={"Building blocks": body.replace(" [NEEDS CLARIFICATION: which read path]", "")}), (0, ""))

    def test_a_marker_in_any_other_file_of_a_design_directory_fails(self):
        self.put(NOTES, "# Notes\n\nThe reader keeps one cache.\n\nIts size is [NEEDS CLARIFICATION: per table or per node].\n")
        rc, out, err = self.document(NOTES)
        self.assertEqual((rc, out), (1, "documents 0 checked 1 failed\n"))
        self.assertEqual(err, "%s:5: %s\n" % (NOTES, self.MESSAGE))

    def test_a_file_of_a_design_directory_without_a_marker_passes(self):
        self.put(NOTES, "# Notes\n\nThe reader keeps one cache, sized per table.\n")
        self.assertEqual(self.document(NOTES), (0, "documents 0 checked 0 failed\n", ""))


if __name__ == "__main__":
    unittest.main()
