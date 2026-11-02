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
"""Reads Markdown the way the process documents are written: headings,
fenced blocks and HTML comments, tables, and placeholders in braces.
doclint.py reads documents with it. It holds no project rule, so it can live wherever its readers live.
"""

import re

FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})")


def strip_comments(text):
    """The text with its HTML comments cut out, and whether a comment is
    still open at its end."""
    kept = ""
    while True:
        start = text.find("<!--")
        if start < 0:
            return kept + text, False
        kept += text[:start]
        end = text.find("-->", start + 4)
        if end < 0:
            return kept, True
        text = text[end + 3:]


class Markdown:
    """The lines of a Markdown document and its headings, outside fences and
    comments. fenced holds the lines of fenced blocks, their fences
    included, and fences the opening and closing fence lines. A fence
    closes only with the same character, at least as long and with no info
    string, as in CommonMark. visible holds each line with its HTML
    comments cut out, so a class after a comment on the same line still
    counts. commented holds the lines that are nothing but
    comment, which no list or table reads. doclint.py reads
    documents this way."""

    def __init__(self, name, text):
        self.name = name
        self.lines = text.split("\n")
        self.errors = []
        self.headings = []
        self.fenced = set()
        self.fences = set()
        self.commented = set()
        self.visible = list(self.lines)
        opening = None
        inside_comment = False
        for index, line in enumerate(self.lines):
            if inside_comment:
                end = line.find("-->")
                if end < 0:
                    self.commented.add(index)
                    self.visible[index] = ""
                    continue
                rest, inside_comment = strip_comments(line[end + 3:])
                self.visible[index] = rest
                if not rest.strip():
                    self.commented.add(index)
                continue
            match = FENCE.match(line)
            if opening is not None:
                self.fenced.add(index)
                if match and match.group(1)[0] == opening[0] and len(match.group(1)) >= len(opening) and not line[match.end():].strip():
                    self.fences.add(index)
                    opening = None
                continue
            if match:
                self.fenced.add(index)
                self.fences.add(index)
                opening = match.group(1)
                continue
            if "<!--" in line:
                line, inside_comment = strip_comments(line)
                self.visible[index] = line
                if not line.strip():
                    self.commented.add(index)
                    continue
            match = re.match(r"^(#{1,6}) +(.*?) *#*$", line)
            if match:
                self.headings.append((len(match.group(1)), match.group(2).strip(), index))

    def error(self, index, reason):
        self.errors.append("%s:%d: %s" % (self.name, index + 1, reason))

    def span(self, level, start):
        """The line range of the heading at index start, up to the next
        heading of the same or a higher level."""
        end = len(self.lines)
        for other_level, _, index in self.headings:
            if index > start and other_level <= level:
                end = index
                break
        return start, end


def table_cells(line):
    text = line.strip()
    if text.startswith("|"):
        text = text[1:]
    if text.endswith("|"):
        text = text[:-1]
    return [cell.strip() for cell in text.split("|")]


def first_heading(text):
    for line in text.split("\n"):
        match = re.match(r"^#\s+(.*?)\s*#*$", line)
        if match:
            return match.group(1)
    return ""


def outer_braces(text):
    """The outermost {...} groups of a text, nesting aware."""
    found, depth, start = [], 0, 0
    for position, char in enumerate(text):
        if char == "{":
            if depth == 0:
                start = position
            depth += 1
        elif char == "}" and depth > 0:
            depth -= 1
            if depth == 0:
                found.append(text[start:position + 1])
    return found


def first_table(doc, start=0, end=None):
    """The rows of the first table at or after line start, as lists of
    cells, header and separator left out, with the line index of each."""
    end = len(doc.lines) if end is None else end
    rows = []
    seen = False
    for index in range(start, end):
        if index in doc.fenced or index in doc.commented:
            if seen:
                break
            continue
        line = doc.visible[index].strip()
        if line.startswith("|"):
            if not seen:
                seen = True
                header = index
            if index == header or re.match(r"^\|[\s:|-]+\|?$", line):
                continue
            rows.append((index, table_cells(line)))
        elif seen:
            break
    return rows
