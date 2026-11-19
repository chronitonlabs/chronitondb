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
"""The requirement line check of doclint.py: a code span is a word of the
sentence, never nothing, a word of size needs a number, and a word of
speed needs a number or the mechanism that makes it so. Run from the
repository root:

    python3 -m unittest discover -s tools/chronitondb/test/doclint
"""

import os
import sys
import unittest

TOOLS = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, TOOLS)
import doclint  # noqa: E402
from markdown import Markdown  # noqa: E402


def check(text, unit="a requirement"):
    doc = Markdown("docs/design/BVER-versions/feature-spec.md", text)
    doclint.check_requirement(doc, 0, "FREQ-BVER-023", text, unit)
    return doc.errors


class CodeSpans(unittest.TestCase):

    def test_a_source_that_starts_with_a_code_span_is_a_source(self):
        errors = check("When a flush runs, the index MUST write one segment. Source: `Instance.java:704` and `:709`, where the node starts.")
        self.assertEqual(errors, [])

    def test_a_keyword_inside_a_code_span_is_not_counted(self):
        errors = check("When `nodetool flush` runs, the index MUST write one segment, never `MUST NOT` text. Source: issue #42.")
        self.assertEqual(errors, [])

    def test_a_sentence_that_starts_with_a_code_span_is_in_no_ears_shape(self):
        errors = check("`nodetool flush` MUST write one segment. Source: issue #42.")
        self.assertEqual(len(errors), 1)
        self.assertIn("FREQ-BVER-023 is in none of the five EARS shapes", errors[0])

    def test_a_source_that_is_only_a_placeholder_is_still_no_source(self):
        errors = check("When a flush runs, the index MUST write one segment. Source: {the issue}.")
        self.assertEqual(len(errors), 1)
        self.assertIn("FREQ-BVER-023 has no source", errors[0])


class UnmeasuredWords(unittest.TestCase):

    def test_a_speed_word_with_its_mechanism_passes(self):
        errors = check("When a row is read, the reader MUST find its block fast, by one lookup in the block map held in memory. Source: issue #42.")
        self.assertEqual(errors, [])

    def test_a_speed_word_with_a_number_passes(self):
        errors = check("When a row is read, the reader MUST find its block fast, in at most 2 disk reads. Source: issue #42.")
        self.assertEqual(errors, [])

    def test_a_speed_word_alone_is_refused(self):
        errors = check("When a row is read, the reader MUST find its block fast. Source: issue #42.")
        self.assertEqual(len(errors), 1)
        self.assertIn("FREQ-BVER-023 says 'fast' without a number or the mechanism that makes it so", errors[0])

    def test_a_mechanism_of_fewer_than_three_words_is_refused(self):
        errors = check("When a row is read, the reader MUST find its block quickly by design. Source: issue #42.")
        self.assertEqual(len(errors), 1)
        self.assertIn("says 'quickly' without a number or the mechanism", errors[0])

    def test_a_mechanism_named_before_the_speed_word_does_not_count(self):
        errors = check("When a row is read by a client of the node, the reader MUST be efficient. Source: issue #42.")
        self.assertEqual(len(errors), 1)
        self.assertIn("says 'efficient' without a number or the mechanism", errors[0])

    def test_a_mechanism_in_the_source_does_not_count(self):
        errors = check("When a row is read, the reader MUST be fast. Source: issue #42, raised by an operator of a cluster.")
        self.assertEqual(len(errors), 1)
        self.assertIn("says 'fast' without a number or the mechanism", errors[0])

    def test_a_size_word_still_needs_a_number_whatever_mechanism_follows(self):
        errors = check("When a file is large, the writer MUST split it, since one file holds one range. Source: issue #42.")
        self.assertEqual(len(errors), 1)
        self.assertIn("FREQ-BVER-023 uses an unmeasured word without a number", errors[0])

    def test_a_size_word_with_a_number_passes(self):
        errors = check("When a file is large, above 64 MiB, the writer MUST split it. Source: issue #42.")
        self.assertEqual(errors, [])

    def test_an_acceptance_criterion_is_held_to_the_same_words(self):
        errors = check("When a row is read, the reader MUST answer quickly.", unit="an acceptance criterion")
        self.assertEqual(len(errors), 1)
        self.assertIn("says 'quickly' without a number or the mechanism", errors[0])


if __name__ == "__main__":
    unittest.main()
