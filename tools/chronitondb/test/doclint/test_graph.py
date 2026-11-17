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
"""The graph of the documents, docgraph.py: derived from the headers the
indexes read, written as JSON-LD, the same bytes for the same tree. Run
from the repository root:

    python3 -m unittest discover -s tools/chronitondb/test/doclint
"""

import contextlib
import io
import json
import os
import sys
import unittest

TOOLS = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
ROOT = os.path.normpath(os.path.join(TOOLS, "..", ".."))
sys.path.insert(0, TOOLS)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import docgraph  # noqa: E402
import doclint  # noqa: E402
from test_records import Indexes, history  # noqa: E402

LINKS = ("areas", "isPartOf", "replaces", "references", "elaborates", "wasDerivedFrom", "inScheme")


def run(*args):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = docgraph.main(list(args))
    return rc, out.getvalue(), err.getvalue()


class Graph(Indexes):

    def setUp(self):
        super().setUp()
        with open(os.path.join(ROOT, "docs", "index", "context.json"), encoding="utf-8") as handle:
            self.put("docs/index/context.json", handle.read())
        self.tree()
        self.record("docs/design/VER-release-version/decisions/DEC-VER-0002-second.md", areas="tools", supersedes="DEC-VER-0001")
        self.put("docs/design/VER-release-version/feature-spec.md", self.SPEC + "\n" + history(("1", "2026-11-01", "First version", "None"), ("2", "2026-11-17", "The key moved", "DEC-VER-0002")) + "\n")
        self.put("docs/design/70-the-reader/design-record.md", self.DESIGN.replace("| Areas | tools |", "| References | Issue #70. Line `chronitondb-5.0`. [Feature spec](../VER-release-version/feature-spec.md). |\n| Areas | tools |"))

    def graph(self, *more):
        return run("--repo", self.repo, "--templates", "line", "--source", "worktree", *more)

    def nodes(self):
        self.graph("--write")
        data = json.loads(self.read("docs/index/graph.json"))
        return data, {node["@id"]: node for node in data["@graph"]}

    def test_write_then_check_and_the_same_bytes_twice(self):
        rc, _, err = self.graph()
        self.assertEqual(rc, 1)
        self.assertIn("docs/index/graph.json:0: is not the graph the documents give now", err)
        self.assertEqual(self.graph("--write")[:2], (0, "graph docs/index/graph.json written\n"))
        first = self.read("docs/index/graph.json")
        self.assertEqual(self.graph()[::2], (0, ""))
        self.assertEqual(self.graph("--write")[1], "graph docs/index/graph.json current\n")
        self.assertEqual(self.read("docs/index/graph.json"), first)
        self.assertNotIn(self.repo, first)

    def test_it_parses_and_every_link_points_at_a_node(self):
        data, nodes = self.nodes()
        self.assertEqual(data["@context"], "context.json")
        self.assertIn("Never edited by hand", data["description"])
        self.assertEqual([node["@id"] for node in data["@graph"]], sorted(nodes))
        count = 0
        for node in data["@graph"]:
            for key in LINKS:
                targets = node.get(key, [])
                for target in [targets] if isinstance(targets, str) else targets:
                    count += 1
                    if key == "inScheme":
                        continue
                    self.assertIn(target, nodes, "%s of %s" % (key, node["@id"]))
        self.assertGreater(count, 8)

    def test_each_link_a_header_states(self):
        _, nodes = self.nodes()
        spec = nodes["../design/VER-release-version/feature-spec.md"]
        self.assertEqual(spec["areas"], ["../process/areas.md#observability", "../process/areas.md#tools"])
        self.assertEqual(spec["isPartOf"], ["../design/VER-release-version/"])
        self.assertEqual(spec["references"], ["../design/VER-release-version/decisions/DEC-VER-0002-second.md"])
        self.assertEqual((spec["status"], spec["version"], spec["type"]), ("Approved", "2", "Feature spec"))
        self.assertIn("oslc_rm:RequirementCollection", spec["@type"])
        design = nodes["../design/70-the-reader/design-record.md"]
        self.assertEqual(design["elaborates"], ["../design/VER-release-version/feature-spec.md"])
        self.assertEqual(design["isPartOf"], ["../design/VER-release-version/"])
        self.assertEqual(design["line"], "chronitondb-5.0")
        second = nodes["../design/VER-release-version/decisions/DEC-VER-0002-second.md"]
        self.assertEqual(second["replaces"], ["../design/VER-release-version/decisions/DEC-VER-0001-first.md"])
        self.assertEqual(second["identifier"], "DEC-VER-0002")
        imported = nodes["../imports/cassandra-19999.md"]
        self.assertEqual(imported["wasDerivedFrom"], ["https://github.com/apache/cassandra/commit/0123456789ab", "https://issues.apache.org/jira/browse/CASSANDRA-19998",
                                                      "https://issues.apache.org/jira/browse/CASSANDRA-19999"])
        self.assertEqual((imported["source"], imported["line"]), ("apache-cherry-pick", "chronitondb-5.0"))
        self.assertEqual(nodes["../design/VER-release-version/"]["@type"], ["Feature"])
        self.assertEqual(nodes["../process/areas.md#tools"]["prefLabel"], "tools")

    def test_no_link_is_guessed_from_prose(self):
        self.put("docs/design/70-the-reader/design-record.md", self.DESIGN + "\nThis record follows DEC-VER-0001 and the feature spec of VER.\n")
        _, nodes = self.nodes()
        design = nodes["../design/70-the-reader/design-record.md"]
        self.assertNotIn("references", design)
        self.assertNotIn("elaborates", design)

    def test_a_commit_of_another_project_is_named_and_not_linked(self):
        self.put("docs/imports/other-project-0123456789ab.md", self.IMPORT.replace("apache-cherry-pick", "third-party"))
        _, nodes = self.nodes()
        imported = nodes["../imports/other-project-0123456789ab.md"]
        self.assertEqual(imported["upstreamRevision"], ["0123456789ab"])
        self.assertNotIn("https://github.com/apache/cassandra/commit/0123456789ab", imported.get("wasDerivedFrom", []))

    def test_a_missing_context_fails(self):
        os.remove(os.path.join(self.repo, "docs/index/context.json"))
        rc, _, err = self.graph("--write")
        self.assertEqual(rc, 1)
        self.assertIn("docs/index/context.json:0: the context of the graph is not there", err)

    def test_the_context_parses_and_keeps_our_terms_relative(self):
        with open(os.path.join(ROOT, "docs", "index", "context.json"), encoding="utf-8") as handle:
            text = handle.read()
        context = json.loads(text)["@context"]
        self.assertEqual(context["@vocab"], "context.json#")
        self.assertNotIn("chronitonlabs", text)
        for term in ("line", "source", "upstreamRevision", "Feature"):
            self.assertNotIn(term, context)

    def test_the_graph_on_this_line_is_current(self):
        with open(os.path.join(ROOT, "docs", "index", "graph.json"), encoding="utf-8") as handle:
            data = json.load(handle)
        ids = {node["@id"] for node in data["@graph"]}
        self.assertEqual(len(ids), len(data["@graph"]))


if __name__ == "__main__":
    unittest.main()
