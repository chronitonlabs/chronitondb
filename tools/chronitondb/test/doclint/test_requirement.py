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
sentence, never nothing. Run from the repository root:

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


if __name__ == "__main__":
    unittest.main()
