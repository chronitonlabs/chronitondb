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
"""Checks the process documents of this repository the way docs/process/
on the line defines them, and the feature keys, libraries and settings the
process rules name. The CI workflow chronitondb-documents.yml runs it on
every pull request, and contributors and their tools run the same file
before they commit.

    doclint.py document --repo DIR --templates REF [--source SRC] PATH...
    doclint.py keys --repo DIR --base REF [--source SRC]
    doclint.py dependencies --repo DIR --base REF --line REF [--source SRC] FILE...
    doclint.py settings --repo DIR --base REF [--source SRC]
    doclint.py index [--write | --check] FILE...

SRC is where the documents are read: "index" (the default, the staged
version), "worktree", or a commit. REF is where the rules are read, the line
itself (origin/<line>), never the change being checked, so a pull request
cannot weaken its own check: the templates in docs/process/templates/, the
checklist of docs/process/quality-requirements.md and the decision record
template in docs/decisions/README.md. CI also takes this file from the line.

The type of each PATH comes from where it lives:

    docs/design/<dir>/feature-spec.md      feature spec
    docs/design/<dir>/plan.md              plan
    docs/design/<dir>/delivery-plan.md     delivery plan
    docs/design/<dir>/ac-coverage.md       coverage file
    docs/design/<dir>/milestones/*.md      milestone report
    docs/design/<dir>/*.md                 design record or fix record, by
                                           its first heading ("# Design:",
                                           "# Fix:")
    docs/imports/*.md                      import record
    docs/decisions/NNNN-<slug>.md          decision record
    docs/delta/<name>.md                   delta entry (README.md is the
                                           register)
    docs/releases/<line>-plan.md           line plan
    docs/releases/*.md                     release proposal

Any other path is not a document of the process and is passed over, except
that no file under docs/design/ may keep a clarification marker.

Every document is checked for:

  1. no clarification marker "[NEEDS CLARIFICATION" is left
  2. the document control table under the first heading holds every field
     of its template's table, each filled, and Status is one of the values
     the template allows (ISO/IEC/IEEE 15289)
  3. every numbered section of the template ("## 3. Title", "### 2.1
     Title") is there, in order, and no placeholder of the template, a
     "{...}" text in braces, is left
  4. when its template has a "## Contents" section, the document has one
     too, as its first section after the title: a nested list of links,
     one per heading below the title and in their order, each indented
     two spaces more than the nearest heading above it of a higher
     level, none for a "##", showing the heading's text and linking the
     heading's anchor, and nothing else. An anchor follows GitHub's
     rules: the text GitHub shows for the heading in lower case, every
     character that is not a letter, a digit, "_", "-" or a space
     removed, each space a hyphen, and a heading whose anchor is taken
     already gets "-1", then "-2". A decision record is asked for its
     index only when it is new, absent at REF: a merged record is never
     edited, docs/decisions/README.md rule 2, so one merged before its
     template had the section keeps none

A new decision record also takes the next number after the highest
record merged at REF, one number per new record and in order, so it
neither reuses a merged number nor leaves a gap (rule 1 of the README).

A feature spec is also checked for:

  1. its directory is docs/design/<KEY>-<slug>/
  2. its Feature class and switches section states the feature class
  3. its Feature requirements are FREQ-<KEY>-nnn lines, each with one EARS
     shape, one BCP 14 keyword, a source and no unmeasured word without a
     number
  4. its Quality requirements table has a row for every line of the
     quality checklist, each answered
  5. its Threat model has a STRIDE row or the statement "This feature adds
     no new entry point" with a reason
  6. its Compatibility section has its five parts or the statement "This
     feature changes no format, schema or protocol"
  7. its Dependencies section lists each library with ASF category A or B,
     or says "No new dependency"
  8. it has its Glossary
  9. its class (docs/process/classification.md), once the template has
     the rows: Risk, Size and Reach each the level, one of the levels of
     its family, a colon and a reason of three words or more, Touches the
     phrases of TOUCHES (public interface, stock behaviour, new input or
     privilege, new dependency, shared state, request path, new feature or
     switch) in any case, split at a comma, a semicolon or "and", or none,
     and a Low risk never touching a public
     interface or stock behaviour. A missing or malformed level counts as
     the strictest of its family: Critical, Byzantine, Cross-cutting
 10. its sections against the class: each section the class requires
     holds its content and never says Not applicable (at Critical risk the
     sections Normal risk requires by Touches too), every other section
     holds its content or the one line "Not applicable: <reason>", a
     section that says Not applicable covers its subsections, which may be
     left out, and the sections it covers are not checked further. "Not
     applicable" counts as such a line before any punctuation, at the end
     of the line, before because, since, as, here, now or yet, or before a
     qualifier such as "for this feature", and so does a leading N/A. Where
     problems could occur and its Test plan never say none, low or n/a,
     and never open with none, low, no risk, minimal or negligible

A decision record and a delta entry also have their unnumbered sections,
and a decision record keeps none of its template's <...> placeholders.

A plan, a milestone report, a design record and a fix record are also
checked for the form of their class rows, when their template has them. A
plan and a milestone report repeat the levels of the feature spec of their
feature directory. A fix record writes its Where problems could occur
section with its Test plan in full, and so does a design record, unless its
References row links a feature spec as a Markdown link to a feature-spec.md
the source holds, when it may say Not applicable with a reason that names
the spec's section 4.

A plan is also checked for: each item delivers FREQ ids its feature spec
defines, each acceptance criterion has one EARS shape and one BCP 14
keyword, and the traceability table maps every FREQ of the feature spec to
an item.

A milestone report is also checked for: each row of its Requirements
delivered table has the status delivered, not delivered, or delivered in
part, as planned, and the report of the feature's final milestone, the
highest milestone of the delivery plan, has no row delivered in part.

A delta entry is also checked for: the Header table holds the DEP-3 fields
of the template, each in its form (Origin, Bug, Bug-ChronitonDB, Forwarded,
dates YYYY-MM-DD), and the register's index has its row with the same
Forwarded, Added, Last update and Issue. It prints "issue N PATH" on stdout
for each Bug-ChronitonDB issue, which the caller checks exists.

keys is the feature key check of additive.md, Feature keys and requirement
ids, over the whole tree at SRC against the line at REF: every directory of
docs/design/ is <KEY>-<slug> (KEY 3 to 5 capital letters) or <issue>-<slug>,
each key names one directory on this line and on every other line the clone
has, no feature directory of REF is gone, every keyed id FREQ-<KEY>-nnn or
REQ-<KEY>-nnn uses a key that has a directory, each FREQ is defined once, in
its feature's feature spec, each REQ once, in the Requirements of one design
record, every id a document cites is defined, and every requirement tag on a
scenario under test/bdd names a defined id. It prints "new KEY DIR" on
stdout for each key directory REF does not have, for the caller's check
that no open pull request uses the key.

dependencies is the library check of compliance.md. FILE... are the
library files, with build.xml for the version properties. Each library
coordinate they declare at SRC, against the merge base REF, keyed by file
and name: Maven dependencies as elements or attributes with ${...} and Ant
@...@ versions resolved from the build's properties, pip pins, git
requirements by ref and unpinned names, pip install words in docker files,
every jar, zip or wheel under lib/, and the Accord submodule commit. A
coordinate added or moved to another version passes when a line of the
Dependencies section of a merged feature spec or design record on the line
(--line) names the library and the version, or when it is a patch-version
bump of the same library (same major and minor), which the pull request
states with its reason. It prints "patch NAME OLD NEW FILE" for each.

index prints the Contents section each FILE needs, read from the working
tree, whatever its type. With --write it puts that section in the file in
place of its old one, or before its first heading below the title when it
has none. A Contents section that holds anything but blank lines and
index entries is refused with its line, and the file is left unchanged.
With --check it reports what is wrong with the file's index, the check of
point 4 above, also for a template. Authors and their tools run it after
any heading changes, before the commit.

settings is the setting name check of release.md, The configuration file.
A setting name is a top level key of a yaml file, active ("name:") or
commented ("# name:" or "#name:"). Every setting of Apache's
conf/cassandra.yaml and conf/cassandra_latest.yaml at SRC is in ours,
conf/cassandra_chronitondb.yaml, active or commented, or left out with a
reason on a line "# Left out: <name>: <reason>". A setting Apache's two
files had at the merge base REF and have no more is gone from ours, or
flagged on a line "# Apache removed: <name>". Ours removed while the line
had it fails. With no file of ours on the line yet the check has nothing to
compare and says so.

Findings go to stderr as "PATH:LINE: reason", exit 1 when there is one.
A usage error exits 2.
"""

import html
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from markdown import Markdown, first_heading, first_table, outer_braces, table_cells  # noqa: E402

# The feature class line of the template section Feature class and switches,
# which the record parser reads too.
CLASS_LINE = re.compile(r"^Feature class: (purely additive|behaviour-changing), because \S.{2,}$")
MARKER = "[NEEDS CLARIFICATION"
KEY_DIR = re.compile(r"^docs/design/([A-Z]{3,5})-[a-z0-9]+(?:-[a-z0-9]+)*/")
FREQ_LINE = re.compile(r"^\s*(?:(?:[-*+]|[0-9]+[.)])\s+)?[*_`]*(FREQ-([A-Z]{3,5})-[0-9]{3})(?![0-9])[*_`]*\s*(\([^)]*\))?\s*:?\s*(.*)$")
KEYWORDS = re.compile(r"\b(MUST NOT|MUST|SHALL NOT|SHALL|SHOULD NOT|SHOULD|NOT RECOMMENDED|RECOMMENDED|MAY|REQUIRED|OPTIONAL)\b")
UNMEASURED = re.compile(r"\b(fast|faster|quick|quickly|slow|large|small|many|few|efficient|efficiently|reasonable|soon|high|low|scalable)\b", re.I)
EARS = ("The ", "When ", "While ", "Where ", "If ")
DATE = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$")
JIRA = re.compile(r"https://issues\.apache\.org/jira/browse/CASSANDRA-[0-9]+")
OUR_ISSUE = re.compile(r"^\[?#?([0-9]+)\]?\(https://github\.com/chronitonlabs/chronitondb/issues/([0-9]+)\)$|^https://github\.com/chronitonlabs/chronitondb/issues/([0-9]+)$")
NO_ENTRY_POINT = "This feature adds no new entry point"
NO_FORMAT_CHANGE = "This feature changes no format, schema or protocol"
NO_DEPENDENCY = "No new dependency"

# The class of a change (docs/process/classification.md): the Risk, Size,
# Reach and Touches rows of the document control table.
RISKS = ("Critical", "Normal", "Low")
SIZES = ("Low Hanging Fruit", "Normal", "Challenging", "Byzantine")
REACHES = ("One area", "Cross-cutting")
CLASS_ROWS = (("Risk", RISKS), ("Size", SIZES), ("Reach", REACHES))
# The last three name what a Normal risk code review adds a lens for: threads,
# pools or shared state, a read, write or query path, and a new feature or switch.
TOUCHES = ("public interface", "stock behaviour", "new input or privilege", "new dependency",
           "shared state", "request path", "new feature or switch")
FLOOR = ("public interface", "stock behaviour")
# The strictest value of each family, which a missing or unreadable row counts as.
STRICTEST = {"Risk": "Critical", "Size": "Byzantine", "Reach": "Cross-cutting"}
NOT_APPLICABLE = re.compile(r"^Not applicable:\s*(\S.*)$")
# A section claims Not applicable when its own text starts with the words
# and then any punctuation, the end of the line, "because", "since" or "as",
# or a qualifier that points at the document itself, such as "here", "for
# this feature" or "in this case", and when it starts with "N/A" or "n/a",
# the slash written. Only a preposition that names something else makes
# content: "Not applicable to clusters without ..." and "Not applicable to
# this release line only ..." are content, and so is a word NA (P7, V1,
# V5, V7).
NOT_APPLICABLE_ANY = re.compile(
    r"^\W*(not\s+applicable\s*([^\w\s]|$|(because|since|as|here|now|yet)\b"
    r"|(for|in|on)\s+(this|these|the\s+(feature|change|item|fix|case|spec|record|document|section))\b)"
    r"|n/a\b)", re.I)
REASON_WORDS = 3
WPCO = "Where problems could occur"
TEST_PLAN = "Test plan"
EMPTY_RISK = re.compile(r"^\W*(none|low|n/?a|nothing|no risk|low risk|minimal|negligible)\W*$", re.I)
# A Where problems could occur text that opens by playing the risk down:
# "low risk", "no risk", "minimal risk" or "negligible risk", or "none",
# "low" or "nothing" with punctuation or the end of the text after it.
# "Low-level reads ..." and "Nothing in stock changes, but ..." name real
# problems (P11, V6). Ubuntu's rule is about that section, so the test plan
# is not held to it.
DISMISSIVE_RISK = re.compile(r"^\W*((low|no|minimal|negligible)\s+risk\b|(none|low|nothing)\s*([.,;:!]|$))", re.I)
# The Touches phrases are split at a comma, a semicolon or "and", and read
# in any case (P8).
TOUCHES_SPLIT = re.compile(r"\s*[,;]\s*(?:and\s+)?|\s+and\s+")
WPCO_WORDS = 5

TEMPLATES = {
    "feature-spec": "docs/process/templates/feature-spec.md",
    "plan": "docs/process/templates/plan.md",
    "delivery-plan": "docs/process/templates/delivery-plan.md",
    "milestone-report": "docs/process/templates/milestone-report.md",
    "design-record": "docs/process/templates/design-record.md",
    "fix-record": "docs/process/templates/fix-record.md",
    "line-plan": "docs/process/templates/line-plan.md",
    "import-record": "docs/process/templates/import-record.md",
    "delta-entry": "docs/process/templates/delta-entry.md",
    "release-proposal": "docs/process/templates/release-proposal.md",
    "ac-coverage": "docs/process/templates/ac-coverage.md",
    "decision": "docs/decisions/README.md",
}
# Unnumbered sections the type requires beside the numbered ones.
REQUIRED_PLAIN = {
    "feature-spec": ["Glossary"],
    "design-record": ["Planned file list"],
    "fix-record": ["Planned file list"],
    "decision": ["Context and problem statement", "Considered options", "Decision outcome"],
    "delta-entry": ["Header", "What", "Why", "Area", "Lines"],
}
# The types whose templates write placeholders in angle brackets.
ANGLE_PLACEHOLDERS = ("decision",)


class Source:
    """Reads files from the index, the working tree or a commit."""

    def __init__(self, repo, where):
        self.repo = repo
        self.where = where

    def read(self, path):
        if self.where == "worktree":
            try:
                with open(os.path.join(self.repo, path), encoding="utf-8") as handle:
                    return handle.read()
            except (OSError, UnicodeDecodeError):
                return None
        spec = ":" + path if self.where == "index" else "%s:%s" % (self.where, path)
        return git(self.repo, "show", spec)


def git(repo, *args):
    try:
        result = subprocess.run(["git", "-C", repo] + list(args), capture_output=True, check=False)
    except OSError:
        return None
    if result.returncode != 0:
        return None
    try:
        return result.stdout.decode("utf-8")
    except UnicodeDecodeError:
        return None


def doc_type(path, text):
    if path.startswith("docs/design/") and path.endswith(".md"):
        parts = path.split("/")
        if len(parts) == 4:
            name = parts[3]
            if name == "feature-spec.md":
                return "feature-spec"
            if name == "plan.md":
                return "plan"
            if name == "delivery-plan.md":
                return "delivery-plan"
            if name == "ac-coverage.md":
                return "ac-coverage"
            first = first_heading(text)
            if first.startswith("Design:"):
                return "design-record"
            if first.startswith("Fix:"):
                return "fix-record"
            return None
        if len(parts) == 5 and parts[3] == "milestones":
            return "milestone-report"
        return None
    if re.match(r"^docs/imports/[^/]+\.md$", path):
        return "import-record"
    if re.match(r"^docs/decisions/[0-9]{4}-[^/]+\.md$", path):
        return "decision"
    if re.match(r"^docs/delta/[^/]+\.md$", path) and path != "docs/delta/README.md":
        return "delta-entry"
    if re.match(r"^docs/releases/[^/]+-plan\.md$", path):
        return "line-plan"
    if re.match(r"^docs/releases/[^/]+\.md$", path):
        return "release-proposal"
    return None


def control_table(doc):
    """The field to (value, line) map of the document control table: the
    first table after the first heading, before the first section."""
    first = [h for h in doc.headings if h[0] == 1]
    if not first:
        return None, None
    start = first[0][2] + 1
    stop = len(doc.lines)
    for level, _, index in doc.headings:
        if index > start and level <= 2:
            stop = index
            break
    rows = first_table(doc, start, stop)
    if not rows:
        return None, None
    fields = {}
    for index, cells in rows:
        if len(cells) >= 2:
            fields[cells[0]] = (cells[1], index)
    return fields, rows[0][0]


def allowed_statuses(value):
    """The Status values a template allows: "Draft, Approved or Superseded",
    "Current or Dropped", "Proposed, Accepted, or Superseded by NNNN"."""
    words = re.split(r",\s*(?:or\s+)?|\s+or\s+", value.strip().rstrip("."))
    return [word.strip() for word in words if word.strip()]


def status_ok(value, allowed):
    for word in allowed:
        if "NNNN" in word:
            if re.match("^" + re.escape(word).replace("NNNN", "[0-9]{4}") + r"(\b|$)", value):
                return True
        elif value == word or (word == "Superseded" and value.startswith("Superseded")):
            return True
    return False


def numbered_sections(doc):
    """The numbered section headings of a document as (level, number,
    title, line): "## 3. Title" and "### 2.1 Title"."""
    found = []
    for level, text, index in doc.headings:
        match = re.match(r"^([0-9]+(?:\.[0-9]+)*)\.?\s+(.*)$", text)
        if match and level in (2, 3):
            found.append((level, match.group(1), match.group(2).strip(), index))
    return found


def section_span(doc, number):
    """The line range of the numbered section, None when it is missing."""
    for level, found, _, index in numbered_sections(doc):
        if found == number:
            return doc.span(level, index)
    return None


def plain_section_span(doc, title):
    for level, text, index in doc.headings:
        if level == 2 and text == title:
            return doc.span(level, index)
    return None


def text_lines(doc, span):
    start, end = span
    return [(index, doc.visible[index]) for index in range(start + 1, end)
            if index not in doc.fenced and index not in doc.commented]


def check_requirement(doc, index, rid, text, unit):
    """One EARS shape, one BCP 14 keyword, a source, no unmeasured word
    without a number."""
    # A code span is a word of the sentence: removed, a source that starts
    # with one reads as no source. It becomes "code", which no keyword,
    # shape or vague word check reads.
    body = re.sub(r"`[^`]*`", "code", text)
    if not body.startswith(EARS):
        doc.error(index, "%s is in none of the five EARS shapes (The, When, While, Where, If then)" % rid)
    elif body.startswith("If ") and ", then " not in body:
        doc.error(index, "%s starts with If and has no \", then\"" % rid)
    before_source = re.sub(r"Source:.*$", "", body)
    count = len(KEYWORDS.findall(before_source))
    if count != 1:
        doc.error(index, "%s has %d BCP 14 keywords, %s has exactly one (split it)" % (rid, count, unit))
    if unit != "an acceptance criterion" and not re.search(r"Source: [^<{\s]", body):
        doc.error(index, "%s has no source" % rid)
    if UNMEASURED.search(before_source) and not re.search(r"[0-9]", before_source):
        doc.error(index, "%s uses an unmeasured word without a number" % rid)


def check_common(doc, kind, template_text, path):
    for index, line in enumerate(doc.lines):
        if MARKER in line:
            doc.error(index, "a clarification marker is left: every [NEEDS CLARIFICATION: ...] is answered and removed before the document merges")
    template = Markdown(path + " template", template_text)
    # The document control table.
    wanted, _ = control_table(template)
    fields, table_line = control_table(doc)
    if wanted:
        if fields is None:
            doc.error(0, "no document control table under the first heading. The %s template starts with one: %s (ISO/IEC/IEEE 15289)" % (kind, ", ".join(wanted)))
        else:
            for field, (template_value, _) in wanted.items():
                if field not in fields:
                    doc.error(table_line, "the document control table has no '%s' row (ISO/IEC/IEEE 15289)" % field)
                    continue
                value, line = fields[field]
                # A template value in braces or angle brackets is a placeholder.
                # Any other value is the fixed text the template prescribes.
                if not value or outer_braces(value) or (re.search(r"<[^>]+>", template_value) and value == template_value):
                    doc.error(line, "the '%s' row of the document control table is not filled in" % field)
                    continue
                if field == "Status":
                    allowed = allowed_statuses(template_value)
                    if not status_ok(value, allowed):
                        doc.error(line, "Status is '%s', a %s is %s" % (value, kind.replace("-", " "), " or ".join(allowed)))
    # The numbered sections, in order.
    have = numbered_sections(doc)
    have_numbers = [(number, title) for _, number, title, _ in have]
    previous = -1
    compatibility = section_number(template, "Compatibility") if kind == "feature-spec" else None
    skip_parts = compatibility is not None and NO_FORMAT_CHANGE in section_text(doc, compatibility)
    # Where the class requires Compatibility in full, the statement stands in
    # for the on-disk format changes only (P3).
    only_formats = skip_parts and wanted and "Risk" in wanted and compatibility_in_full(*class_quietly(doc, fields))
    # A section that says Not applicable covers its subsections, which may
    # be left out, once the template carries the class (classification.md).
    covered = not_applicable_numbers(doc) if kind == "feature-spec" and wanted and "Risk" in wanted else set()
    for level, number, title, _ in numbered_sections(template):
        if "{" in title:
            continue
        if skip_parts and number.startswith(compatibility + ".") and (not only_formats or number == compatibility + ".1"):
            continue
        if "." in number and number.split(".")[0] in covered:
            continue
        if (number, title) not in have_numbers:
            doc.error(0, "no '%s %s%s %s' section. The %s template has it" % ("#" * level, number, "." if level == 2 else "", title, kind.replace("-", " ")))
            continue
        position = have_numbers.index((number, title))
        if position < previous:
            doc.error(have[position][3], "the section '%s %s' is out of the template's order" % (number, title))
        previous = max(previous, position)
    for title in REQUIRED_PLAIN.get(kind, []):
        if plain_section_span(doc, title) is None:
            doc.error(0, "no '## %s' section. The %s template has it" % (title, kind.replace("-", " ")))
    # No placeholder of the template is left.
    placeholders = set()
    for index, line in enumerate(template.lines):
        for group in outer_braces(line):
            if group not in ("{tags}", "{class}"):
                placeholders.add(group)
    if kind in ANGLE_PLACEHOLDERS:
        for line in template.lines:
            placeholders.update(re.findall(r"<[A-Za-z][^<>]*>", line))
    for index, line in enumerate(doc.lines):
        if index in doc.fenced:
            continue
        groups = outer_braces(line)
        if kind in ANGLE_PLACEHOLDERS:
            groups = groups + re.findall(r"<[A-Za-z][^<>]*>", line)
        for group in groups:
            if group in placeholders:
                doc.error(index, "a placeholder of the template is left: %s" % (group if len(group) <= 60 else group[:57] + "..." + group[-1]))


def section_text(doc, number):
    span = section_span(doc, number)
    if span is None:
        return ""
    return "\n".join(line for _, line in text_lines(doc, span))


def freqs_of(doc):
    """The FREQ ids section 3 of a feature spec defines, with their lines."""
    found = {}
    span = section_span(doc, "3")
    if span is None:
        return found
    for index, line in text_lines(doc, span):
        match = FREQ_LINE.match(line)
        if match:
            found.setdefault(match.group(1), index)
    return found


def section_number(doc, title):
    """The number of the numbered section with this title, None when the
    document has none."""
    for _, number, found, _ in numbered_sections(doc):
        if found == title:
            return number
    return None


def own_lines(doc, index):
    """The text lines under the heading at index, up to the next heading of
    any level, comments left out, blank lines dropped."""
    end = len(doc.lines)
    for _, _, other in doc.headings:
        if other > index:
            end = other
            break
    return [(i, doc.visible[i]) for i in range(index + 1, end)
            if i not in doc.commented and i not in doc.fenced and doc.visible[i].strip()]


def not_applicable_of(doc, index):
    """For the heading at index: None when its own text is no Not applicable
    line, "" when it is one well formed line, or why it is not."""
    lines = own_lines(doc, index)
    hits = [(i, line.strip()) for i, line in lines if NOT_APPLICABLE_ANY.match(line.strip())]
    if not hits:
        return None
    line = hits[0][1]
    match = NOT_APPLICABLE.match(line)
    if not match:
        return "write it as the one line 'Not applicable: <reason>'"
    if len(re.findall(r"\w+", match.group(1))) < REASON_WORDS:
        return "its reason has fewer than %d words: 'Not applicable: <reason>' gives the reason" % REASON_WORDS
    if len(lines) > 1:
        return "it holds more than the one line 'Not applicable: <reason>'"
    return ""


def not_applicable_numbers(doc):
    """The numbers of the numbered sections whose own text is a Not
    applicable line, well formed or not."""
    return {number for _, number, _, index in numbered_sections(doc) if not_applicable_of(doc, index) is not None}


def class_of(doc, fields, kind, rows):
    """{row: level} of the class rows a document control table holds, each
    checked for its form, and the set of Touches phrases (None when the
    table has no Touches row). A missing or malformed level counts as the
    strictest of its family."""
    levels = {}
    for name, allowed in rows:
        value, line = fields.get(name, ("", 0))
        level = None
        for word in sorted(allowed, key=len, reverse=True):
            if value.startswith(word + ":"):
                level = word
                break
        if level is None:
            if value and not outer_braces(value):
                doc.error(line, "the '%s' row is '%s'. It is the level, one of %s, then a colon and the reason (classification.md)" % (name, value if len(value) <= 60 else value[:57] + "...", ", ".join(allowed)))
            levels[name] = STRICTEST[name]
            continue
        reason = value[len(level) + 1:]
        if len(re.findall(r"\w+", reason)) < REASON_WORDS:
            doc.error(line, "the '%s' row gives no reason after '%s:'. Write the level, a colon and a reason of %d words or more (classification.md)" % (name, level, REASON_WORDS))
        levels[name] = level
    touches = None
    if "Touches" in fields:
        value, line = fields["Touches"]
        touches = set()
        if value and not outer_braces(value):
            text = re.sub(r"\([^)]*\)", "", value).strip().rstrip(".")
            words = [w.strip().lower() for w in TOUCHES_SPLIT.split(text) if w.strip()]
            if words == ["none"]:
                pass
            else:
                for word in words:
                    if word in TOUCHES:
                        touches.add(word)
                    elif word == "none":
                        doc.error(line, "the 'Touches' row says none beside other phrases. It says none alone, or lists what the change touches")
                    else:
                        doc.error(line, "the 'Touches' row names '%s', which is none of: %s, or none (classification.md)" % (word, ", ".join(TOUCHES)))
            floor = sorted(touches & set(FLOOR))
            if floor and levels.get("Risk") == "Low" and fields.get("Risk", ("", 0))[0].startswith("Low:"):
                doc.error(fields["Risk"][1], "the risk is Low, and Touches names %s. A change that touches a public interface or stock behaviour is at least Normal risk (classification.md, The floor)" % " and ".join(floor))
    return levels, touches


def compatibility_in_full(levels, touches):
    """True when the class requires Compatibility in full: Critical risk,
    Challenging or Byzantine size, or Normal risk touching a public
    interface or stock behaviour. The statement "This feature changes no
    format, schema or protocol" then stands in for the on-disk format
    changes only, and the other parts stay (classification.md)."""
    risk, size = levels.get("Risk"), levels.get("Size")
    return risk == "Critical" or size in ("Challenging", "Byzantine") or \
        (risk == "Normal" and bool((touches or set()) & set(FLOOR)))


def class_quietly(doc, fields):
    """The class of a feature spec's control table, read with no finding:
    the levels and the Touches phrases, a missing or malformed level the
    strictest of its family, as class_of reads them."""
    levels = {}
    for row, allowed in CLASS_ROWS:
        value = (fields or {}).get(row, ("", 0))[0]
        word = value.split(":", 1)[0].strip()
        levels[row] = word if word in allowed else STRICTEST[row]
    touches = set()
    value = (fields or {}).get("Touches", ("", 0))[0]
    if value and not outer_braces(value):
        text = re.sub(r"\([^)]*\)", "", value).strip().rstrip(".")
        touches = {w.strip().lower() for w in TOUCHES_SPLIT.split(text) if w.strip().lower() in TOUCHES}
    return levels, touches


def required_sections(template, levels, touches):
    """{section: the class that requires it} of a feature spec, by the
    template's numbered sections and its Glossary."""
    size, reach, risk = levels.get("Size"), levels.get("Reach"), levels.get("Risk")
    touches = touches or set()
    numbers = {title: number for _, number, title, _ in numbered_sections(template) if "{" not in title}
    every = [n for _, n, t, _ in numbered_sections(template) if "{" not in t] + ["Glossary"]
    wanted = {}

    def need(names, why):
        for name in names:
            number = numbers.get(name, name if name == "Glossary" else None)
            if number is not None and number not in wanted:
                wanted[number] = why

    need(["Purpose and scope", "Architecture", "Feature class and switches", "Feature requirements", WPCO, TEST_PLAN, "Decisions", "Prior art"], "every class")
    if size in ("Challenging", "Byzantine"):
        for number in every:
            wanted.setdefault(number, "%s size" % size)
    if size == "Normal":
        need(["Context and scope", "Building blocks", "Package dependencies and hook points", "Milestones outline"], "Normal size")
    if reach == "Cross-cutting":
        need(["Dependencies", "Risks", "Milestones outline"], "Cross-cutting reach")
    if risk == "Critical":
        compatibility = numbers.get("Compatibility")
        need(["Threat model", "Compatibility"], "Critical risk")
        for number in every:
            if compatibility and number.startswith(compatibility + "."):
                wanted.setdefault(number, "Critical risk")
        if "new dependency" in touches:
            need(["Dependencies"], "Critical risk with a new dependency")
    if risk == "Normal":
        if "new input or privilege" in touches:
            need(["Threat model"], "Normal risk with new input or privilege")
        if touches & set(FLOOR):
            compatibility = numbers.get("Compatibility")
            need(["Compatibility"], "Normal risk touching %s" % " and ".join(sorted(touches & set(FLOOR))))
            for number in every:
                if compatibility and number.startswith(compatibility + "."):
                    wanted.setdefault(number, wanted[compatibility])
        if "new dependency" in touches:
            need(["Dependencies"], "Normal risk with a new dependency")
    return wanted


def check_risk_text(doc, index, what, opener=True):
    """The Where problems could occur section and its test plan name
    something: never none, low or a word or two. The section, not its test
    plan, never opens by playing the risk down (V6)."""
    lines = own_lines(doc, index)
    text = " ".join(line.strip() for _, line in lines)
    if lines and (EMPTY_RISK.match(text) or (opener and DISMISSIVE_RISK.match(text)) or len(re.findall(r"\w+", text)) < WPCO_WORDS):
        doc.error(index, "%s says only '%s'. It names what could break, how a user would see it and the tests that would catch it, never none or low (classification.md)" % (what, text if len(text) <= 40 else text[:37] + "..."))


def check_spec_class(doc, template, fields):
    """A feature spec against its class (classification.md): each section
    the class requires holds its content, never Not applicable, every other
    section its content or the one line 'Not applicable: <reason>', and the
    Where problems could occur section and its test plan name something."""
    levels, touches = class_of(doc, fields, "feature-spec", CLASS_ROWS)
    wanted = required_sections(template, levels, touches)
    headings = {number: (title, index) for _, number, title, index in numbered_sections(doc)}
    for level, text, index in doc.headings:
        if level == 2 and text == "Glossary":
            headings["Glossary"] = ("", index)
    compatibility = section_number(doc, "Compatibility")
    no_format = compatibility is not None and NO_FORMAT_CHANGE in section_text(doc, compatibility)
    only_formats = compatibility_in_full(levels, touches)
    covered = not_applicable_numbers(doc)
    for number, (title, index) in headings.items():
        name = ("%s %s" % (number, title)) if title else number
        if "." in number and number.split(".")[0] in covered:
            continue
        if no_format and compatibility and number.startswith(compatibility + ".") and (not only_formats or number == compatibility + ".1"):
            continue
        state = not_applicable_of(doc, index)
        if state:
            doc.error(index, "section %s says Not applicable, but %s" % (name, state))
            continue
        if state == "" and number in wanted:
            doc.error(index, "section %s says Not applicable, and the class requires it (%s). Write it in full (classification.md)" % (name, wanted[number]))
            continue
        if state is None:
            start, end = doc.span(level_of(doc, index), index)
            body = [i for i in range(start + 1, end) if i not in doc.commented and doc.visible[i].strip()
                    and not any(found == i for _, _, found in doc.headings)]
            if not body:
                doc.error(index, "section %s is empty. Write it, or the one line 'Not applicable: <reason>' when the class does not require it (classification.md)" % name)
    for title in (WPCO, TEST_PLAN):
        number = section_number(doc, title)
        if number is not None and not_applicable_of(doc, headings[number][1]) is None:
            if title == WPCO and not own_lines(doc, headings[number][1]):
                # Its test plan alone is not enough, as in a record (P1).
                doc.error(headings[number][1], "section %s %s is empty. It names what could break, how a user would see it and the tests that would catch it, and its test plan alone is not enough (classification.md)" % (number, title))
                continue
            check_risk_text(doc, headings[number][1], "section %s %s" % (number, title), opener=title == WPCO)
    check_non_goals(doc)
    return levels


def check_non_goals(doc):
    """The Non-goals of section 1, required at every class, never Not
    applicable (P9)."""
    purpose = section_number(doc, "Purpose and scope")
    span = section_span(doc, purpose) if purpose is not None else None
    index = None
    for level, text, found in doc.headings:
        if level == 3 and text == "Non-goals" and (span is None or span[0] < found < span[1]):
            index = found
            break
    if index is None:
        doc.error(0, "no '### Non-goals' section. The feature spec template has it")
        return
    state = not_applicable_of(doc, index)
    if state:
        doc.error(index, "section Non-goals says Not applicable, but %s" % state)
    elif state == "":
        doc.error(index, "section Non-goals says Not applicable, and the class requires it (every class). Write it in full (classification.md)")
    elif not own_lines(doc, index):
        doc.error(index, "section Non-goals is empty. It names what the feature will not do, each with a short reason, at every class (classification.md)")


def level_of(doc, index):
    for level, _, found in doc.headings:
        if found == index:
            return level
    return 2


SPEC_LINK = re.compile(r"\[[^\]]*\]\(([^)\s]*feature-spec\.md)\)")


def spec_link_of(references, path, source):
    """The feature spec a design record's References row links, as a
    Markdown link to a feature-spec.md the source holds, or None (P10)."""
    for target in SPEC_LINK.findall(references or ""):
        if target.startswith("docs/"):
            resolved = target
        else:
            resolved = os.path.normpath(os.path.join(os.path.dirname(path or ""), target))
        if source is None or source.read(resolved) is not None:
            return resolved
    return None


def check_record_risk(doc, kind, template, path=None, source=None):
    """The Where problems could occur section of a design or fix record and
    its Test plan, when the record's template has them: always written in a
    fix record, and in a design record unless its References row links a
    feature spec the source holds, and its Not applicable reason names the
    spec's section 4 (P10)."""
    if template is None or plain_section_span(template, WPCO) is None:
        return
    span = plain_section_span(doc, WPCO)
    if span is None:
        doc.error(0, "no '## %s' section. The %s template has it" % (WPCO, kind.replace("-", " ")))
        return
    fields, _ = control_table(doc)
    references = (fields or {}).get("References", ("", 0))[0]
    linked = spec_link_of(references, path, source) if kind == "design-record" else None
    state = not_applicable_of(doc, span[0])
    reason = " ".join(line.strip() for _, line in own_lines(doc, span[0]))
    allowed = linked is not None and re.search(r"\bsection 4\b|Where problems could occur", reason.split(":", 1)[-1], re.I) is not None
    if state:
        doc.error(span[0], "section %s says Not applicable, but %s" % (WPCO, state))
        return
    if state == "":
        if not allowed:
            doc.error(span[0], "section %s says Not applicable. A %s writes it in full%s (classification.md)" % (WPCO, kind.replace("-", " "), "" if kind == "fix-record" else " unless its References row links the feature spec that covers it, as a Markdown link to its feature-spec.md, and the reason names that spec's section 4"))
        return
    if not own_lines(doc, span[0]):
        doc.error(span[0], "section %s is empty. It names what could break, how a user would see it and the tests that would catch it (classification.md)" % WPCO)
    else:
        check_risk_text(doc, span[0], "section %s" % WPCO)
    plan = None
    for level, text, index in doc.headings:
        if level == 3 and text == TEST_PLAN and span[0] < index < span[1]:
            plan = index
    if plan is None:
        doc.error(span[0], "section %s has no '### %s'. The %s template has it" % (WPCO, TEST_PLAN, kind.replace("-", " ")))
    elif not own_lines(doc, plan) or not_applicable_of(doc, plan) is not None:
        doc.error(plan, "the %s of section %s is empty or says Not applicable. It names the test that would catch each problem (classification.md)" % (TEST_PLAN, WPCO))
    else:
        check_risk_text(doc, plan, "the %s of section %s" % (TEST_PLAN, WPCO), opener=False)


def check_class_rows(doc, kind, path, template, source):
    """The class rows of a plan, milestone report, design record or fix
    record, when its template has them: their form, and for a plan and a
    milestone report the same levels as the feature spec of the directory."""
    wanted, _ = control_table(template)
    if not wanted or "Risk" not in wanted:
        return
    fields, _ = control_table(doc)
    if fields is None:
        return
    rows = tuple(row for row in CLASS_ROWS if row[0] in wanted)
    levels, _ = class_of(doc, {k: v for k, v in fields.items() if k in wanted}, kind, rows)
    if kind not in ("plan", "milestone-report"):
        return
    folder = os.path.dirname(path) if kind == "plan" else os.path.dirname(os.path.dirname(path))
    spec_path = os.path.join(folder, "feature-spec.md")
    spec_text = source.read(spec_path)
    if spec_text is None:
        return
    spec = Markdown(spec_path, spec_text)
    spec_fields, _ = control_table(spec)
    if not spec_fields or "Risk" not in spec_fields:
        return
    spec_levels, _ = class_of(Markdown(spec_path, spec_text), spec_fields, "feature-spec", CLASS_ROWS)
    for name, _ in rows:
        mine, line = levels.get(name), fields.get(name, ("", 0))[1]
        theirs = spec_levels.get(name)
        if name in fields and mine != theirs and not outer_braces(fields[name][0]):
            doc.error(line, "the %s is %s, and the feature spec %s says %s. The %s repeats the feature spec's class (classification.md)" % (name.lower(), mine, spec_path, theirs, kind.replace("-", " ")))


def check_feature_spec(doc, path, rules):
    key_match = KEY_DIR.match(path)
    key = key_match.group(1) if key_match else None
    if key is None:
        doc.error(0, "a feature spec lives in docs/design/<KEY>-<slug>/, KEY 3 to 5 capital letters and a lower case slug, found %s" % os.path.dirname(path))
    # 2.8 the feature class.
    span = section_span(doc, "2.8") if "2" not in not_applicable_numbers(doc) else None
    if span is not None and not any(CLASS_LINE.match(line.strip()) for _, line in text_lines(doc, span)):
        doc.error(span[0], "section 2.8 has no line 'Feature class: <purely additive or behaviour-changing>, because <reason>.'")
    # 3 the feature requirements.
    freqs = {}
    span = section_span(doc, "3")
    if span is not None:
        for index, line in text_lines(doc, span):
            match = FREQ_LINE.match(line)
            if not match:
                if re.search(r"\bFREQ-", line) and re.match(r"^\s*(?:[-*+]|[0-9]+[.)])?\s*[*_`]*FREQ-", line):
                    doc.error(index, "a requirement id is FREQ-<KEY>-nnn, the feature key and three digits")
                continue
            rid, rkey, text = match.group(1), match.group(2), match.group(4)
            if rid in freqs:
                doc.error(index, "%s is defined twice, first on line %d" % (rid, freqs[rid] + 1))
                continue
            freqs[rid] = index
            if key and rkey != key:
                doc.error(index, "%s uses the key %s, this feature's key is %s" % (rid, rkey, key))
            check_requirement(doc, index, rid, text.strip(), "a requirement")
        if not freqs:
            doc.error(span[0], "section 3 defines no feature requirement FREQ-<KEY>-nnn")
    covered = not_applicable_numbers(doc)
    # The quality checklist, every line answered.
    quality = section_number(doc, "Quality requirements")
    span = section_span(doc, quality) if quality and quality not in covered else None
    if span is not None and rules.get("quality"):
        rows = {}
        for index, cells in first_table(doc, span[0], span[1]):
            if len(cells) >= 3:
                rows[cells[1]] = (cells[2], index)
        for line_text in rules["quality"]:
            if line_text not in rows:
                doc.error(span[0], "the quality table has no row '%s' of quality-requirements.md" % line_text)
                continue
            answer, index = rows[line_text]
            if not answer or outer_braces(answer):
                doc.error(index, "the quality line '%s' has neither FREQ ids nor a reason it does not apply" % line_text)
                continue
            for rid in re.findall(r"FREQ-[A-Z]{3,5}-[0-9]{3}", answer):
                if rid not in freqs:
                    doc.error(index, "the quality line '%s' names %s, which section 3 does not define" % (line_text, rid))
    # The threat model.
    threat = section_number(doc, "Threat model")
    span = section_span(doc, threat) if threat and threat not in covered else None
    if span is not None:
        text = section_text(doc, threat)
        rows = [cells for _, cells in first_table(doc, span[0], span[1]) if any(cells)]
        statement = re.search(re.escape(NO_ENTRY_POINT) + r"\W+\S+", text)
        if not rows and not statement:
            doc.error(span[0], "the threat model has no STRIDE row and not the statement \"%s\" with its reason" % NO_ENTRY_POINT)
        for cells in rows:
            for rid in re.findall(r"FREQ-[A-Z]{3,5}-[0-9]{3}", " ".join(cells)):
                if rid not in freqs:
                    doc.error(span[0], "the threat model names %s, which section 3 does not define" % rid)
    # The dependencies.
    dependencies = section_number(doc, "Dependencies")
    span = section_span(doc, dependencies) if dependencies and dependencies not in covered else None
    if span is not None:
        rows = [(index, cells) for index, cells in first_table(doc, span[0], span[1]) if any(cells)]
        if not rows and NO_DEPENDENCY not in section_text(doc, dependencies):
            doc.error(span[0], "section %s lists no library and does not say \"%s\"" % (dependencies, NO_DEPENDENCY))
        for index, cells in rows:
            category = cells[2] if len(cells) > 2 else ""
            if re.match(r"^(Category\s+)?X\b", category):
                doc.error(index, "%s is ASF category X, which the project refuses (compliance.md)" % (cells[0] or "a library"))
            elif not re.match(r"^(Category\s+)?[AB]\b", category):
                doc.error(index, "%s has no ASF category A or B (compliance.md)" % (cells[0] or "a library"))
    return freqs


def check_plan(doc, path, source):
    spec_path = os.path.join(os.path.dirname(path), "feature-spec.md")
    spec_text = source.read(spec_path)
    freqs = {}
    if spec_text is None:
        doc.error(0, "no feature spec at %s to trace the plan to" % spec_path)
    else:
        spec = Markdown(spec_path, spec_text)
        freqs = freqs_of(spec)
    delivered = set()
    items = [(level, text, index) for level, text, index in doc.headings if level == 3 and re.match(r"^Item [0-9]+:", text)]
    if not items:
        doc.error(0, "the plan has no '### Item <n>: <title>' entry")
    for level, text, index in items:
        start, end = doc.span(level, index)
        lines = text_lines(doc, (start, end))
        delivers = [(i, line) for i, line in lines if re.match(r"^\s*[-*]\s+\*\*Delivers:\*\*", line)]
        if not delivers:
            doc.error(index, "%s has no '- **Delivers:**' line" % text)
        for i, line in delivers:
            ids = re.findall(r"FREQ-[A-Z]{3,5}-[0-9]{3}", line)
            if not ids:
                doc.error(i, "%s delivers no FREQ id" % text)
            for rid in ids:
                delivered.add(rid)
                if spec_text is not None and rid not in freqs:
                    doc.error(i, "%s delivers %s, which the feature spec does not define" % (text, rid))
        criteria = []
        lead = None
        collecting = False
        for i, line in lines:
            if re.match(r"^\s*[-*]\s+\*\*Acceptance criteria:\*\*", line):
                collecting = True
                rest = re.sub(r"^\s*[-*]\s+\*\*Acceptance criteria:\*\*\s*", "", line).strip()
                if rest and not rest.endswith(":"):
                    lead = (i, rest)
                continue
            if collecting:
                if re.match(r"^\s*[-*]\s+\*\*", line):
                    collecting = False
                    continue
                match = re.match(r"^\s*[0-9]+[.)]\s+(.*)$", line)
                if match:
                    criteria.append((i, match.group(1).strip()))
        if not criteria and lead is not None:
            criteria.append(lead)
        if not criteria:
            doc.error(index, "%s has no acceptance criteria" % text)
        for number, (i, criterion) in enumerate(criteria, 1):
            check_requirement(doc, i, "%s criterion %d" % (text.split(":")[0], number), criterion, "an acceptance criterion")
    span = section_span(doc, "3")
    if span is not None and spec_text is not None:
        traced = set()
        for index, cells in first_table(doc, span[0], span[1]):
            ids = re.findall(r"FREQ-[A-Z]{3,5}-[0-9]{3}", cells[0] if cells else "")
            if ids and len(cells) > 1 and cells[1].strip():
                traced.update(ids)
            for rid in ids:
                if rid not in freqs:
                    doc.error(index, "the traceability table names %s, which the feature spec does not define" % rid)
        for rid in sorted(freqs):
            if rid not in traced:
                doc.error(span[0], "%s of the feature spec maps to no item in the traceability table. A FREQ with no item blocks approval" % rid)


def check_delta(doc, path, source, rules):
    span = plain_section_span(doc, "Header")
    template = rules.get("delta-template")
    if span is None:
        doc.error(0, "no '## Header' section with the DEP-3 fields")
        return
    fields = {}
    for index, cells in first_table(doc, span[0], span[1]):
        if len(cells) >= 2:
            fields[cells[0]] = (cells[1], index)
    wanted = []
    if template is not None:
        tspan = plain_section_span(template, "Header")
        if tspan is not None:
            wanted = [cells[0] for _, cells in first_table(template, tspan[0], tspan[1]) if cells]
    for field in wanted:
        if field not in fields or not fields[field][0] or outer_braces(fields[field][0]):
            doc.error(span[0], "the Header table has no filled '%s' row (DEP-3)" % field)
    def value(name):
        return fields.get(name, ("", span[0]))
    origin, line = value("Origin")
    if origin and not re.match(r"^(ChronitonDB\b|Apache commit\b|Backport of Apache commit\b|Another fork\b|[A-Za-z0-9 ._-]+ fork\b)", origin):
        doc.error(line, "Origin is ChronitonDB, Apache commit <hash>, Backport of Apache commit <hash>, or another fork with its link")
    if origin and re.match(r"^(Apache commit|Backport of Apache commit)", origin) and not re.search(r"[0-9a-f]{7,40}", origin):
        doc.error(line, "an Apache Origin names the commit hash")
    bug, line = value("Bug")
    if bug and bug.lower() != "none" and not JIRA.search(bug):
        doc.error(line, "Bug is the Apache JIRA as a link, https://issues.apache.org/jira/browse/CASSANDRA-<n>, or none")
    ours, line = value("Bug-ChronitonDB")
    issue = None
    if ours and ours.lower() != "none":
        match = OUR_ISSUE.match(ours.strip())
        if not match:
            doc.error(line, "Bug-ChronitonDB is a link to our issue, https://github.com/chronitonlabs/chronitondb/issues/<n>, or none")
        else:
            issue = match.group(2) or match.group(3)
            if match.group(1) and match.group(1) != issue:
                doc.error(line, "Bug-ChronitonDB shows #%s and links issue %s" % (match.group(1), issue))
            sys.stdout.write("issue %s %s\n" % (issue, path))
    forwarded, line = value("Forwarded")
    if forwarded:
        if not re.match(r"^(Offered|Declined|Not needed)\b", forwarded):
            doc.error(line, "Forwarded is Offered, Declined or Not needed")
        elif re.match(r"^(Offered|Declined)\b", forwarded) and not re.search(r"CASSANDRA-[0-9]+", forwarded):
            doc.error(line, "Forwarded %s names the Apache JIRA" % forwarded.split()[0])
        elif forwarded.startswith("Declined") and not re.search(r"CASSANDRA-[0-9]+\S*\W+\w+", forwarded):
            doc.error(line, "Forwarded Declined gives a one line reason")
        elif forwarded.startswith("Not needed") and not re.search(r"^Not needed\W+\w+", forwarded):
            doc.error(line, "Forwarded Not needed gives the reason")
    for name in ("Added", "Last-Update"):
        date, line = value(name)
        if date and not DATE.match(date):
            doc.error(line, "%s is a date YYYY-MM-DD" % name)
    added, _ = value("Added")
    updated, line = value("Last-Update")
    if DATE.match(added or "") and DATE.match(updated or "") and updated < added:
        doc.error(line, "Last-Update %s is before Added %s" % (updated, added))
    # The register's index row.
    register = source.read("docs/delta/README.md")
    name = os.path.basename(path)
    if register is None:
        doc.error(0, "no register docs/delta/README.md to hold this entry's index row")
        return
    index_doc = Markdown("docs/delta/README.md", register)
    rows = []
    span_index = plain_section_span(index_doc, "Index")
    if span_index is not None:
        for index, cells in first_table(index_doc, span_index[0], span_index[1]):
            if re.search(r"\]\((\./)?" + re.escape(name) + r"\)", cells[0] if cells else ""):
                rows.append((index, cells))
    if len(rows) != 1:
        doc.error(0, "the register's Index has %d rows for %s, it has exactly one" % (len(rows), name))
        return
    index, cells = rows[0]
    columns = ["Entry", "Area", "Lines", "Forwarded", "Added", "Last update", "Issue"]
    if len(cells) != len(columns):
        doc.error(0, "the register's Index row for %s has %d columns, the Index has %s" % (name, len(cells), ", ".join(columns)))
        return
    row = dict(zip(columns, cells))
    if forwarded and not row["Forwarded"].startswith(forwarded.split(".")[0].split(",")[0].strip()[:10]):
        doc.error(0, "the register's Index row for %s says Forwarded '%s', the entry says '%s'" % (name, row["Forwarded"], forwarded))
    if added and row["Added"] != added:
        doc.error(0, "the register's Index row for %s says Added %s, the entry says %s" % (name, row["Added"], added))
    if updated and row["Last update"] != updated:
        doc.error(0, "the register's Index row for %s says Last update %s, the entry says %s" % (name, row["Last update"], updated))
    shown = row["Issue"].strip()
    if issue is None and shown.lower() != "none":
        doc.error(0, "the register's Index row for %s names the issue %s, the entry's Bug-ChronitonDB is none" % (name, shown))
    if issue is not None and not re.search(r"#?\b%s\b" % issue, shown):
        doc.error(0, "the register's Index row for %s does not name issue #%s" % (name, issue))


MILESTONE_STATUSES = ("delivered", "not delivered", "delivered in part, as planned")
IN_PART = "delivered in part, as planned"


def milestone_number(path, text):
    match = re.search(r"milestone\s+([0-9]+)", first_heading(text), re.I)
    if match:
        return int(match.group(1))
    match = re.search(r"milestone-([0-9]+)\.md$", path)
    return int(match.group(1)) if match else None


def check_milestone(doc, path, source):
    """The Requirements delivered table: each status is one the template
    allows, and the feature's final milestone, the highest milestone of the
    delivery plan, delivers no requirement in part."""
    span = None
    for level, number, title, index in numbered_sections(doc):
        if level == 2 and title == "Requirements delivered":
            span = doc.span(level, index)
    if span is None:
        return
    in_part = []
    for index, cells in first_table(doc, span[0], span[1]):
        if len(cells) < 4 or not any(cells):
            continue
        status = cells[-1].strip().lower()
        if status not in MILESTONE_STATUSES:
            doc.error(index, "the status of %s is '%s', it is delivered, not delivered, or delivered in part, as planned" % (cells[0] or "a requirement", cells[-1]))
        elif status == IN_PART:
            in_part.append((index, cells[0]))
    if not in_part:
        return
    plan_path = os.path.join(os.path.dirname(os.path.dirname(path)), "delivery-plan.md")
    plan = source.read(plan_path)
    if plan is None:
        doc.error(in_part[0][0], "a requirement is delivered in part, and there is no delivery plan at %s to tell whether this is the feature's final milestone" % plan_path)
        return
    numbers = [int(n) for n in re.findall(r"^###\s+Milestone\s+([0-9]+)\b", plan, re.M)]
    own = milestone_number(path, doc.lines and "\n".join(doc.lines) or "")
    if not numbers or own is None:
        doc.error(in_part[0][0], "a requirement is delivered in part, and the milestone's number or the delivery plan's milestones cannot be read to tell whether this is the final milestone")
        return
    if own >= max(numbers):
        for index, rid in in_part:
            doc.error(index, "%s is delivered in part in milestone %d, the feature's final milestone in %s. The final milestone delivers each requirement or reports it not delivered with its reason in Deviations" % (rid or "a requirement", own, plan_path))

CONTENTS = "Contents"
INDEX_ENTRY = re.compile(r"^( *)[-*+] +\[(.*)\]\(#([^()\s]*)\)\s*$")
HTML_TAG = re.compile(r"</?[A-Za-z][A-Za-z0-9-]*(?:\s[^<>]*)?/?>")
ESCAPE_OR_CODE = re.compile(r"\\([!-/:-@\[-`{-~])|(`+)(.+?)(?<!`)\2(?!`)")
LINK = re.compile(r"(?<!!)\[([^\]]*)\](?:\([^)]*\)|\[[^\]]*\])")
IMAGE = re.compile(r"!\[[^\]]*\](?:\([^)]*\)|\[[^\]]*\])")
UNDERSCORES = re.compile(r"(?<!\w)(_+)(?!\s)(.+?)(?<!\s)\1(?!\w)")


def protect(text):
    """The text with each backslash escape and code span replaced by a
    placeholder, which no later rule reads, and what each stood for: an
    escape its character, a code span its source and its content."""
    kept = []

    def keep(match):
        if match.group(1) is not None:
            kept.append((match.group(0), match.group(1)))
        else:
            content = match.group(3)
            if len(content) > 2 and content[0] == " " and content[-1] == " " and content.strip():
                content = content[1:-1]
            kept.append((match.group(0), content))
        return "\0%d\0" % (len(kept) - 1)
    return ESCAPE_OR_CODE.sub(keep, text), kept


def restore(text, kept, which):
    """The text with each placeholder back: which is 0 for the source as
    written, 1 for what GitHub shows."""
    return re.sub("\0([0-9]+)\0", lambda m: kept[int(m.group(1))][which], text)


def rendered(text):
    """The text GitHub shows for a heading, from which it makes the
    anchor: a backslash escape as its character, a code span as its
    content, an inline or reference link as its text, an image as
    nothing, HTML tags and emphasis marks dropped, a "_" kept unless it
    opens and closes emphasis, HTML entities decoded."""
    text, kept = protect(text)
    text = IMAGE.sub("", text)
    text = LINK.sub(r"\1", text)
    text = HTML_TAG.sub("", text)
    text = text.replace("*", "")
    previous = None
    while previous != text:
        previous = text
        text = UNDERSCORES.sub(r"\2", text)
    text = html.unescape(text)
    return restore(text, kept, 1)


def slug(text):
    """GitHub's anchor for a heading: its text in lower case, every
    character that is not a letter, a digit, "_", "-" or a space removed,
    each space a hyphen."""
    return re.sub(r"[^\w\- ]", "", rendered(text).lower()).replace(" ", "-")


def anchors(doc):
    """(level, text, line, anchor) of each heading, in order. A heading
    whose anchor is taken already gets "-1", then "-2", the next number
    whose anchor is free, as GitHub numbers them."""
    seen = {}
    found = []
    for level, text, index in doc.headings:
        base = slug(text)
        anchor = base
        while anchor in seen:
            seen[base] += 1
            anchor = "%s-%d" % (base, seen[base])
        seen[anchor] = 0
        found.append((level, text, index, anchor))
    return found


def link_text(text):
    """A heading's text as an index entry shows it: its links reduced to
    their text and any other bracket outside a code span escaped, so the
    entry stays one link and a code span shows as written."""
    text, kept = protect(text)
    text = LINK.sub(r"\1", text)
    text = re.sub(r"([\[\]])", r"\\\1", text)
    return restore(text, kept, 0)


def indexed(doc):
    """The headings the index lists: every heading below the title but
    the Contents heading, as (level, text, line, anchor)."""
    return [entry for entry in anchors(doc) if entry[0] >= 2 and not (entry[0] == 2 and entry[1] == CONTENTS)]


def indents(entries):
    """The indent of each index entry: none for a heading with no heading
    of a higher level above it, otherwise two spaces more than the
    nearest such heading. A heading that skips a level is one step below
    its parent, never more, so the list stays nested."""
    parents = []
    found = []
    for level, _, _, _ in entries:
        while parents and parents[-1][0] >= level:
            parents.pop()
        indent = parents[-1][1] + 2 if parents else 0
        parents.append((level, indent))
        found.append(indent)
    return found


def index_section(doc):
    """The lines of the Contents section the document needs."""
    lines = ["## " + CONTENTS, ""]
    entries = indexed(doc)
    for (level, text, _, anchor), indent in zip(entries, indents(entries)):
        lines.append("%s- [%s](#%s)" % (" " * indent, link_text(text), anchor))
    return lines


def has_contents(doc):
    return any(level == 2 and text == CONTENTS for level, text, _ in doc.headings)


def contents_line_ok(doc, index):
    """True for a line a Contents section may hold: blank, or one index
    entry with nothing else on the line."""
    if index in doc.fenced:
        return False
    line = doc.lines[index]
    return not line.strip() or bool(INDEX_ENTRY.match(line))


def check_index(doc, path):
    """The Contents section of point 4 of the module text."""
    hint = "Regenerate it with tools/chronitondb/doclint.py index --write %s" % path
    sections = [(level, text, index) for level, text, index in doc.headings if level == 2]
    contents = [index for level, text, index in sections if text == CONTENTS]
    if not contents:
        doc.error(0, "no '## %s' section, the index of the document's headings with a link to each, as its template has. %s" % (CONTENTS, hint))
        return
    start = contents[0]
    for index in contents[1:]:
        doc.error(index, "a second '## %s' section. A document has one index" % CONTENTS)
    if sections[0][2] != start:
        doc.error(start, "the '## %s' section comes after '## %s'. It is the first section after the title" % (CONTENTS, sections[0][1]))
    wanted = indexed(doc)
    every = dict((anchor, (level, text, index)) for level, text, index, anchor in anchors(doc))
    by_anchor = dict((anchor, (level, text, index)) for level, text, index, anchor in wanted)
    expected_indent = dict((entry[3], indent) for entry, indent in zip(wanted, indents(wanted)))
    _, end = doc.span(2, start)
    listed = []
    for index in range(start + 1, end):
        if not doc.lines[index].strip() and index not in doc.fenced:
            continue
        if not contents_line_ok(doc, index):
            doc.error(index, "the Contents section holds only its list of links to the headings, one per line, and this line is not one. Move it out of the section. %s" % hint)
            continue
        match = INDEX_ENTRY.match(doc.lines[index])
        indent, shown, anchor = len(match.group(1)), match.group(2), match.group(3)
        if anchor not in every:
            doc.error(index, "the index links #%s, and no heading of this file has that anchor. %s" % (anchor, hint))
            continue
        if anchor not in by_anchor:
            doc.error(index, "the index links #%s, the %s, which the index leaves out" % (anchor, "title" if every[anchor][0] == 1 else "Contents heading"))
            continue
        if anchor in [a for _, a in listed]:
            doc.error(index, "the index lists #%s twice" % anchor)
            continue
        listed.append((index, anchor))
        level, text, _ = by_anchor[anchor]
        if indent != expected_indent[anchor]:
            doc.error(index, "the index entry for '%s' is indented %d spaces. It is indented %d, two spaces more than the nearest heading above it of a higher level. %s" % (text, indent, expected_indent[anchor], hint))
        if shown != link_text(text):
            doc.error(index, "the index entry #%s shows '%s', its heading reads '%s'. %s" % (anchor, shown, text, hint))
    shown_anchors = [anchor for _, anchor in listed]
    for level, text, index, anchor in wanted:
        if anchor not in shown_anchors:
            doc.error(start, "the heading '%s' on line %d is not in the index, as [%s](#%s). %s" % (text, index + 1, link_text(text), anchor, hint))
    order = [anchor for _, _, _, anchor in wanted if anchor in shown_anchors]
    for (index, anchor), expected in zip(listed, order):
        if anchor != expected:
            doc.error(index, "the index lists #%s out of the headings' order. %s" % (anchor, hint))
            break


def write_index(doc):
    """(lines, None): the lines of the document with its Contents section
    in place of the old one, or before its first heading below the title
    when it has none, built from the headings that remain. (None, line):
    a Contents section holds a line that is neither blank nor an index
    entry, so nothing is removed and the file stays as it is. (None, None):
    no heading below the title is left to index."""
    drop = set()
    for level, text, index in doc.headings:
        if level == 2 and text == CONTENTS:
            start, end = doc.span(2, index)
            for line in range(start + 1, end):
                if not contents_line_ok(doc, line):
                    return None, line
            drop.update(range(start, end))
    kept = [line for index, line in enumerate(doc.lines) if index not in drop]
    rest = Markdown(doc.name, "\n".join(kept))
    first = [index for level, text, index in rest.headings if level >= 2]
    if not first:
        return None, None
    before = kept[:first[0]]
    while before and not before[-1].strip():
        before.pop()
    return before + [""] + index_section(rest) + [""] + kept[first[0]:], None


def run_index(args):
    mode = None
    files = []
    for word in args:
        if word in ("--write", "--check") and mode is None:
            mode = word
        elif word.startswith("--"):
            sys.stderr.write(__doc__)
            return 2
        else:
            files.append(word)
    if not files:
        sys.stderr.write(__doc__)
        return 2
    failed = 0
    for path in files:
        try:
            with open(path, encoding="utf-8") as handle:
                text = handle.read()
        except (OSError, UnicodeDecodeError):
            sys.stderr.write("%s:0: cannot be read\n" % path)
            failed += 1
            continue
        doc = Markdown(path, text)
        if not indexed(doc):
            sys.stderr.write("%s:0: has no heading below its title, so there is nothing to index\n" % path)
            failed += 1
            continue
        if mode == "--check":
            check_index(doc, path)
            for error in doc.errors:
                sys.stderr.write(error + "\n")
            failed += 1 if doc.errors else 0
        elif mode == "--write":
            new, stray = write_index(doc)
            if stray is not None:
                sys.stderr.write("%s:%d: the Contents section holds other text on this line. Move it out of the section, then run again. The file is unchanged\n" % (path, stray + 1))
                failed += 1
            elif new is None:
                sys.stderr.write("%s:0: has no heading below its title outside its Contents section, so there is nothing to index\n" % path)
                failed += 1
            elif new != doc.lines:
                with open(path, "w", encoding="utf-8") as handle:
                    handle.write("\n".join(new))
                print("index %s written" % path)
            else:
                print("index %s current" % path)
        else:
            if len(files) > 1:
                print("==> %s <==" % path)
            print("\n".join(index_section(doc)))
    if mode == "--check":
        print("index %d checked %d failed" % (len(files), failed))
    return 1 if failed else 0


RECORD = re.compile(r"^docs/decisions/([0-9]{4})-[^/]+\.md$")


def records_at(repo, where):
    """The decision record paths of docs/decisions/ at where: "index",
    "worktree" or a commit."""
    if where == "index":
        listing = git(repo, "ls-files", "--", "docs/decisions/")
    elif where == "worktree":
        listing = git(repo, "ls-files", "--cached", "--others", "--exclude-standard", "--", "docs/decisions/")
    else:
        listing = git(repo, "ls-tree", "-r", "--name-only", where, "--", "docs/decisions/")
    return [line for line in (listing or "").split("\n") if RECORD.match(line)]


def record_rules(repo, templates, where, rules):
    """The decision records merged at the rules ref, and the numbers the
    new ones may take: the next numbers after the highest merged one, one
    each, in order (docs/decisions/README.md, rule 1)."""
    if "records" not in rules:
        merged = set(records_at(repo, templates))
        numbers = [int(RECORD.match(path).group(1)) for path in merged]
        last = max(numbers) if numbers else 0
        new = [path for path in records_at(repo, where) if path not in merged]
        rules["records"] = (merged, last, set(range(last + 1, last + 1 + len(new))))
    return rules["records"]


def needs_index(kind, path, repo, templates, where, rules):
    """True when the document is asked for its index: every templated
    kind, and a decision record only when it is new, absent at the rules
    ref. A merged record is never edited (docs/decisions/README.md, rule
    2), so one merged before its template had the section keeps none."""
    if kind != "decision":
        return True
    merged, _, _ = record_rules(repo, templates, where, rules)
    return path not in merged


def check_record_number(doc, path, repo, templates, where, rules):
    """A new decision record takes the next number after the highest
    record merged at the rules ref, so it neither reuses a merged number
    nor leaves a gap (docs/decisions/README.md, rule 1)."""
    merged, last, allowed = record_rules(repo, templates, where, rules)
    match = RECORD.match(path)
    if path in merged or not match:
        return
    number = int(match.group(1))
    if number not in allowed:
        span = "%04d" % (last + 1) if len(allowed) == 1 else "%04d to %04d" % (last + 1, last + len(allowed))
        doc.error(0, "a new decision record takes a number after the highest merged one, %04d, in order with no gap: %s here, and this one is %04d (docs/decisions/README.md, rule 1)" % (last, span, number))


def decision_template(text):
    """The decision record template: the fenced markdown block of
    docs/decisions/README.md under its Template heading."""
    match = re.search(r"## Template\s*\n+```markdown\n(.*?)\n```", text, re.S)
    return match.group(1) if match else None


def quality_lines(text):
    doc = Markdown("quality-requirements.md", text)
    span = plain_section_span(doc, "The checklist")
    if span is None:
        return []
    return [cells[1] for _, cells in first_table(doc, span[0], span[1]) if len(cells) >= 2 and cells[1]]


DIR_FORM = re.compile(r"^(?:([A-Z]{3,5})|[0-9]+)-[a-z0-9]+(?:-[a-z0-9]+)*$")
ANY_ID = re.compile(r"\b(FREQ|REQ)-([A-Z]{3,5})-([0-9]{3})(?![0-9])")
TAG_ID = re.compile(r"(?<![\w-])@((?:FREQ|REQ)-[A-Z]{3,5}-[0-9]{3})(?![\w-])")


def tree_files(repo, where):
    if where == "index":
        listing = git(repo, "ls-files", "--", "docs/design", "test/bdd")
    elif where == "worktree":
        listing = git(repo, "ls-files", "--cached", "--others", "--exclude-standard", "--", "docs/design", "test/bdd")
    else:
        listing = git(repo, "ls-tree", "-r", "--name-only", where, "--", "docs/design", "test/bdd")
    return [line for line in (listing or "").split("\n") if line]


def requirement_definitions(doc, pattern):
    """The ids matching pattern that start a line, a bullet or a numbered
    item inside a section titled "Requirements" or "N. Feature requirements",
    with their lines."""
    found = []
    for level, text, index in doc.headings:
        title = re.sub(r"^[0-9]+\.\s+", "", text)
        if level >= 2 and title in ("Requirements", "Feature requirements"):
            start, end = doc.span(level, index)
            for line_index in range(start + 1, end):
                if line_index in doc.fenced or line_index in doc.commented:
                    continue
                match = re.match(r"^\s*(?:(?:[-*+]|[0-9]+[.)])\s+)?[*_`]*(" + pattern + r")(?![0-9])", doc.visible[line_index])
                if match:
                    found.append((match.group(1), line_index))
    return found


def check_keys(repo, base, where):
    source = Source(repo, where)
    files = tree_files(repo, where)
    base_files = tree_files(repo, base)
    errors = []
    dirs = sorted({f.split("/")[2] for f in files if f.startswith("docs/design/") and f.count("/") >= 3})
    base_dirs = sorted({f.split("/")[2] for f in base_files if f.startswith("docs/design/") and f.count("/") >= 3})
    keys = {}
    for name in dirs:
        match = DIR_FORM.match(name)
        if not match:
            errors.append("docs/design/%s:0: a design directory is <KEY>-<slug> for a feature, KEY 3 to 5 capital letters, or <issue>-<slug>, the slug lower case words joined by single hyphens" % name)
            continue
        if match.group(1):
            keys.setdefault(match.group(1), []).append(name)
    for key, names in sorted(keys.items()):
        if len(names) > 1:
            errors.append("docs/design/%s:0: the key %s names %d directories, %s. A key names one feature" % (names[1], key, len(names), ", ".join(names)))
    for name in base_dirs:
        match = DIR_FORM.match(name)
        if match and match.group(1) and name not in dirs:
            errors.append("docs/design/%s:0: the feature directory on the line is removed or renamed. A key is never reused and a withdrawn feature keeps its directory" % name)
    base_keys = {DIR_FORM.match(n).group(1) for n in base_dirs if DIR_FORM.match(n) and DIR_FORM.match(n).group(1)}
    # A key is the project's, not one line's: the other lines, as this
    # clone has them, may not hold the same key for another feature. The
    # same directory on two lines is one feature carried on both.
    other_refs = [ref for ref in (git(repo, "for-each-ref", "--format=%(refname:short)", "refs/remotes/origin/chronitondb-*") or "").split() if ref != base]
    if not other_refs:
        for key in sorted(keys):
            if key not in base_keys:
                errors.append("docs/design/%s:0: the new key %s is not checked against the other lines, since this clone has no other line's ref. Fetch every line, then check again" % (keys[key][0], key))
    for ref in other_refs:
        if ref == base:
            continue
        for name in sorted({f.split("/")[2] for f in tree_files(repo, ref) if f.startswith("docs/design/") and f.count("/") >= 3}):
            match = DIR_FORM.match(name)
            if not match or not match.group(1) or match.group(1) not in keys:
                continue
            for own in keys[match.group(1)]:
                if own != name:
                    errors.append("docs/design/%s:0: the key %s is taken on %s by docs/design/%s, another feature. A key names one feature on every line" % (own, match.group(1), ref, name))
    defined = {}
    cited = []
    for path in files:
        if not (path.startswith("docs/design/") and path.endswith(".md")):
            continue
        text = source.read(path)
        if text is None:
            continue
        doc = Markdown(path, text)
        first = first_heading(text)
        name = os.path.basename(path)
        if name == "feature-spec.md":
            for rid, index in requirement_definitions(doc, r"FREQ-[A-Z]{3,5}-[0-9]{3}"):
                defined.setdefault(rid, []).append((path, index))
                key = rid.split("-")[1]
                own = path.split("/")[2]
                if not own.startswith(key + "-"):
                    errors.append("%s:%d: %s is defined in the feature spec of %s, a FREQ is defined in its own feature's spec" % (path, index + 1, rid, own))
        elif first.startswith("Design:"):
            for rid, index in requirement_definitions(doc, r"REQ-[A-Z]{3,5}-[0-9]{3}"):
                defined.setdefault(rid, []).append((path, index))
        for index, line in enumerate(doc.lines):
            for match in ANY_ID.finditer(line):
                cited.append(("%s-%s-%s" % match.groups(), path, index))
    for rid, places in sorted(defined.items()):
        if len(places) > 1:
            errors.append("%s:%d: %s is defined %d times, also at %s. Each id is defined exactly once" % (places[1][0], places[1][1] + 1, rid, len(places), ", ".join("%s:%d" % (p, i + 1) for p, i in places if (p, i) != places[1])))
    for rid, path, index in cited:
        key = rid.split("-")[1]
        if key not in keys:
            errors.append("%s:%d: %s uses the key %s, which no docs/design/%s-<slug>/ directory reserves" % (path, index + 1, rid, key, key))
        elif rid not in defined:
            errors.append("%s:%d: %s is cited and defined nowhere: a FREQ in its feature spec, a REQ in one design record of its feature" % (path, index + 1, rid))
    for path in files:
        if not (path.startswith("test/bdd/") and path.endswith(".feature")):
            continue
        text = source.read(path) or ""
        for index, line in enumerate(text.split("\n")):
            stripped = line.strip()
            if not stripped.startswith("@"):
                continue
            for match in TAG_ID.finditer(stripped.split(" #")[0]):
                if match.group(1) not in defined:
                    errors.append("%s:%d: the tag @%s names no defined requirement" % (path, index + 1, match.group(1)))
    for key in sorted(keys):
        if key not in base_keys:
            sys.stdout.write("new %s %s\n" % (key, keys[key][0]))
    return errors


XML_BLOCK = re.compile(r"<dependency>(.*?)</dependency>", re.S)
XML_ATTRS = re.compile(r"<dependency\b([^>]*?)/?>")
PIP_SPEC = re.compile(r"^([A-Za-z0-9][A-Za-z0-9_.-]*)(?:\[[^\]]*\])?\s*(?:(==|===|>=|<=|~=|!=|>|<)\s*([^\s;#,]+))?")
PIP_GIT = re.compile(r"git\+\S+?/([A-Za-z0-9_.-]+?)(?:\.git)?@([^#\s]+)(?:#egg=([A-Za-z0-9_.-]+))?")
LIB_FILE = re.compile(r"^lib/(?:[^/]+/)*([A-Za-z0-9_.+-]+?)-([0-9][A-Za-z0-9_.+-]*?)\.(jar|zip|tar\.gz|tgz|whl)$")
UNPINNED = "unpinned"


def properties_of(texts):
    """Ant properties (name and value attributes) and Maven properties of
    the given build files, the first definition of a name kept."""
    found = {}
    for text in texts:
        for name, value in re.findall(r"<property\s+name=\"([^\"]+)\"\s+value=\"([^\"]*)\"", text):
            found.setdefault(name, value)
        block = re.search(r"<properties>(.*?)</properties>", text, re.S)
        if block:
            for name, value in re.findall(r"<([A-Za-z0-9_.-]+)>([^<]*)</\1>", block.group(1)):
                if value.strip() != "@%s@" % name:
                    found.setdefault(name, value.strip())
    return found


def resolve(value, props):
    """A version with its ${name} and Ant filter @name@ tokens replaced by
    the build's properties."""
    for _ in range(5):
        new = re.sub(r"\$\{([^}]+)\}", lambda m: props.get(m.group(1), m.group(0)), value)
        new = re.sub(r"@([A-Za-z0-9_.-]+)@", lambda m: props.get(m.group(1), m.group(0)), new)
        if new == value:
            break
        value = new
    return value


def pip_lines(text):
    """The logical lines of a pip file, continuations joined, comments cut."""
    joined = re.sub(r"\\\n", " ", text)
    for raw in joined.split("\n"):
        line = re.sub(r"(^|\s)#.*$", "", raw).strip()
        if line:
            yield line


def pip_coordinates(path, text):
    """{name: version} of a pip requirements file or of the pip install
    commands of a docker file. A git requirement's version is its ref, a
    name with no pin is unpinned."""
    found = {}
    if path.endswith(".docker"):
        for line in pip_lines(text):
            for command in re.findall(r"pip3?(?:\.[0-9]+)? install ([^&|;]*)", line):
                for word in command.split():
                    word = word.strip("\\\"'")
                    if not word or word.startswith("-") or "/" in word:
                        continue
                    match = PIP_SPEC.match(word)
                    if match:
                        found.setdefault(match.group(1).lower(), set()).add(match.group(3) or UNPINNED)
        # A name a docker file installs in several places, at several pins,
        # is one coordinate holding all of them, so a change to any shows.
        return {name: ",".join(sorted(versions)) for name, versions in found.items()}
    for line in pip_lines(text):
        git_match = PIP_GIT.search(line)
        if git_match:
            name = (git_match.group(3) or git_match.group(1)).lower()
            found[name] = git_match.group(2)
            continue
        if line.startswith("-"):
            continue
        match = PIP_SPEC.match(line)
        if match:
            found[match.group(1).lower()] = match.group(3) or UNPINNED
    return found


def coordinates(repo, where, files):
    """{(file, library): version} of the library files at where, "index"
    (the staged tree, also for "worktree") or a commit. A library is keyed
    per file, so the same name pinned in two files is two coordinates.
    Maven libraries are group:artifact with :classifier, pip libraries
    pypi:name, files under lib/ lib:name, the Accord submodule accord."""
    source = Source(repo, where if where != "worktree" else "index")
    texts = {}
    for path in files:
        if path == "lib" or path.startswith("lib/") or path == "modules/accord":
            continue
        text = source.read(path)
        if text is not None:
            texts[path] = text
    # build.xml first: the pom templates define their versions as @name@
    # filter tokens that the build fills from build.xml's properties.
    ordered = sorted((p for p in texts if p.endswith(".xml")), key=lambda p: (p != "build.xml", p))
    props = properties_of([texts[p] for p in ordered])
    found = {}
    for path, text in texts.items():
        if path.endswith(".xml"):
            for block in XML_BLOCK.findall(text):
                def tag(name):
                    match = re.search(r"<%s>\s*([^<]*?)\s*</%s>" % (name, name), block)
                    return match.group(1) if match else ""
                group, artifact, version = tag("groupId"), tag("artifactId"), tag("version")
                if artifact and version:
                    key = "%s:%s%s" % (group, artifact, ":" + tag("classifier") if tag("classifier") else "")
                    found[(path, key)] = resolve(version, props)
            for attrs in XML_ATTRS.findall(text):
                values = dict(re.findall(r"(\w+)=\"([^\"]*)\"", attrs))
                if values.get("artifactId") and values.get("version"):
                    key = "%s:%s" % (values.get("groupId", ""), values["artifactId"])
                    found[(path, key)] = resolve(values["version"], props)
        elif path.endswith(".txt") or path.endswith(".docker"):
            for name, version in pip_coordinates(path, text).items():
                found[(path, "pypi:%s" % name)] = version
    if where in ("index", "worktree"):
        listing = git(repo, "ls-files", "-s", "--", "lib", "modules/accord") or ""
        sha_field = 1
    else:
        listing = git(repo, "ls-tree", "-r", where, "--", "lib", "modules/accord") or ""
        sha_field = 2
    for line in listing.split("\n"):
        if not line:
            continue
        meta, _, path = line.partition("\t")
        parts = meta.split()
        if path == "modules/accord" and len(parts) > sha_field:
            found[(path, "accord")] = parts[sha_field]
            continue
        match = LIB_FILE.match(path)
        if match:
            found[(os.path.dirname(path) or "lib", "lib:%s" % match.group(1))] = match.group(2)
    return found


def patch_bump(old, new):
    """True when new is a patch-version bump of old: the same major and
    minor, a higher patch. Several pins of one name compare one by one."""
    olds, news = (old or "").split(","), (new or "").split(",")
    if len(olds) > 1 or len(news) > 1:
        if len(olds) != len(news):
            return False
        pairs = list(zip(olds, news))
        return all(a == b or one_patch_bump(a, b) for a, b in pairs) and any(a != b for a, b in pairs)
    return one_patch_bump(old, new)


def one_patch_bump(old, new):
    a = re.match(r"^([0-9]+)\.([0-9]+)(?:\.([0-9]+))?", old or "")
    b = re.match(r"^([0-9]+)\.([0-9]+)(?:\.([0-9]+))?", new or "")
    if not a or not b:
        return False
    if a.group(1) != b.group(1) or a.group(2) != b.group(2):
        return False
    return int(b.group(3) or 0) > int(a.group(3) or 0)


def library_names(key):
    """The names a Dependencies section may give a library by."""
    if key == "accord":
        return ["accord", "cassandra-accord"]
    kind, _, name = key.partition(":")
    if kind in ("pypi", "lib"):
        return [name]
    parts = key.split(":")
    return [":".join(parts[:2]), parts[1]] if len(parts) >= 2 else [key]


def declared(repo, line, key, version):
    """True when the Dependencies section of a merged feature spec or design
    record on the line names the library and the version on one line: a
    table row or a sentence. A library is named by its Maven group:artifact
    or artifact, its pip name, its file name under lib/ without the version,
    or accord for the Accord submodule, whose version is its commit hash or
    the first 10 or more characters of it."""
    listing = git(repo, "ls-tree", "-r", "--name-only", line, "--", "docs/design") or ""
    names = library_names(key)
    for path in listing.split("\n"):
        if not path.endswith(".md"):
            continue
        text = git(repo, "show", "%s:%s" % (line, path))
        if not text:
            continue
        if os.path.basename(path) != "feature-spec.md" and not first_heading(text).startswith("Design:"):
            continue
        doc = Markdown(path, text)
        for level, title, index in doc.headings:
            if level != 2 or re.sub(r"^[0-9]+\.\s+", "", title) != "Dependencies":
                continue
            start, end = doc.span(level, index)
            for line_index in range(start + 1, end):
                if line_index in doc.fenced or line_index in doc.commented:
                    continue
                words = set(w.lower() for w in re.findall(r"[A-Za-z0-9_.:+-]+", doc.visible[line_index].replace("`", " ")))
                if not any(name.lower() in words for name in names):
                    continue
                wanted = [v for v in version.split(",") if v != UNPINNED]
                if wanted and all(v.lower() in words or (len(v) == 40 and any(len(w) >= 10 and v.startswith(w) for w in words)) for v in wanted):
                    return True
    return False


def check_dependencies(repo, base, line, where, files):
    before = coordinates(repo, base, files)
    after = coordinates(repo, where, files)
    errors = []
    for (path, key), version in sorted(after.items()):
        old = before.get((path, key))
        if old == version:
            continue
        if old is not None and old != UNPINNED and patch_bump(old, version):
            sys.stdout.write("patch %s %s %s %s\n" % (key, old, version, path))
            continue
        if declared(repo, line, key, version):
            continue
        if old is None:
            what = "is added at %s" % version if version != UNPINNED else "is added with no version pinned, so it cannot be declared at a version"
        else:
            what = "moves from %s to %s" % (old, version)
        errors.append("%s:0: %s %s, and no Dependencies section of a merged feature spec or design record on %s names it at that version. A new library or a minor or major version change is declared there first, only a patch-version bump goes without" % (path, key, what, line))
    return errors


SETTING = re.compile(r"^#? ?([a-z_][a-z0-9_]*):(?:\s|$)")
LEFT_OUT = re.compile(r"^#\s*Left out:\s*([a-z_][a-z0-9_]*):\s*(\S.*)$")
APACHE_REMOVED = re.compile(r"^#\s*Apache removed:\s*([a-z_][a-z0-9_]*)\b")
APACHE_YAML = ("conf/cassandra.yaml", "conf/cassandra_latest.yaml")
OUR_YAML = "conf/cassandra_chronitondb.yaml"


def setting_names(text):
    names = {}
    for index, line in enumerate((text or "").split("\n")):
        match = SETTING.match(line)
        if match:
            names.setdefault(match.group(1), index)
    return names


def check_settings(repo, base, where):
    source = Source(repo, where)
    errors = []
    ours = source.read(OUR_YAML)
    if ours is None:
        if git(repo, "show", "%s:%s" % (base, OUR_YAML)) is not None:
            errors.append("%s:0: our yaml is removed, and the line has it. ChronitonDB ships its own full yaml" % OUR_YAML)
            return errors, 0
        return errors, None
    lines = ours.split("\n")
    own = setting_names(ours)
    left = {}
    removed_flags = set()
    for index, line in enumerate(lines):
        match = LEFT_OUT.match(line)
        if match:
            left[match.group(1)] = index
        match = APACHE_REMOVED.match(line)
        if match:
            removed_flags.add(match.group(1))
    apache_now = {}
    apache_then = {}
    for path in APACHE_YAML:
        for name, index in setting_names(source.read(path)).items():
            apache_now.setdefault(name, (path, index))
        for name in setting_names(git(repo, "show", "%s:%s" % (base, path))):
            apache_then.setdefault(name, path)
    for name, (path, index) in sorted(apache_now.items()):
        if name in own or name in left:
            continue
        errors.append("%s:%d: Apache's setting %s is not in %s, active or commented, and not left out with a reason on a line '# Left out: %s: <reason>'" % (path, index + 1, name, OUR_YAML, name))
    for name, path in sorted(apache_then.items()):
        if name in apache_now:
            continue
        if name in own and name not in removed_flags and name not in left:
            errors.append("%s:%d: Apache removed the setting %s from %s. Remove it from ours or flag it on a line '# Apache removed: %s'" % (OUR_YAML, own[name] + 1, name, path, name))
    return errors, len(apache_now)


def main(argv):
    if argv and argv[0] == "index":
        return run_index(argv[1:])
    if argv and argv[0] == "settings":
        repo, base, where = None, None, "index"
        args = argv[1:]
        index = 0
        while index < len(args):
            if args[index] in ("--repo", "--base", "--source") and index + 1 < len(args):
                if args[index] == "--repo":
                    repo = args[index + 1]
                elif args[index] == "--base":
                    base = args[index + 1]
                else:
                    where = args[index + 1]
                index += 2
                continue
            sys.stderr.write(__doc__)
            return 2
        if not repo or not base:
            sys.stderr.write(__doc__)
            return 2
        errors, count = check_settings(repo, base, where)
        for error in errors:
            sys.stderr.write(error + "\n")
        print("settings %s" % ("none" if count is None else count))
        return 1 if errors else 0
    if argv and argv[0] == "dependencies":
        repo, base, line, where, files = None, None, None, "index", []
        args = argv[1:]
        index = 0
        while index < len(args):
            if args[index] in ("--repo", "--base", "--line", "--source") and index + 1 < len(args):
                value = args[index + 1]
                if args[index] == "--repo":
                    repo = value
                elif args[index] == "--base":
                    base = value
                elif args[index] == "--line":
                    line = value
                else:
                    where = value
                index += 2
                continue
            if args[index].startswith("--"):
                sys.stderr.write(__doc__)
                return 2
            files.append(args[index])
            index += 1
        if not repo or not base or not line:
            sys.stderr.write(__doc__)
            return 2
        errors = check_dependencies(repo, base, line, where, files)
        for error in errors:
            sys.stderr.write(error + "\n")
        return 1 if errors else 0
    if argv and argv[0] == "keys":
        repo, base, where = None, None, "index"
        args = argv[1:]
        index = 0
        while index < len(args):
            if args[index] in ("--repo", "--base", "--source") and index + 1 < len(args):
                if args[index] == "--repo":
                    repo = args[index + 1]
                elif args[index] == "--base":
                    base = args[index + 1]
                else:
                    where = args[index + 1]
                index += 2
                continue
            sys.stderr.write(__doc__)
            return 2
        if not repo or not base:
            sys.stderr.write(__doc__)
            return 2
        errors = check_keys(repo, base, where)
        for error in errors:
            sys.stderr.write(error + "\n")
        return 1 if errors else 0
    if not argv or argv[0] != "document":
        sys.stderr.write(__doc__)
        return 2
    repo, templates, where, paths = None, None, "index", []
    args = argv[1:]
    index = 0
    while index < len(args):
        word = args[index]
        if word in ("--repo", "--templates", "--source") and index + 1 < len(args):
            value = args[index + 1]
            if word == "--repo":
                repo = value
            elif word == "--templates":
                templates = value
            else:
                where = value
            index += 2
            continue
        if word.startswith("--"):
            sys.stderr.write(__doc__)
            return 2
        paths.append(word)
        index += 1
    if not repo or not templates:
        sys.stderr.write(__doc__)
        return 2
    source = Source(repo, where)
    if git(repo, "rev-parse", "--verify", "--quiet", "%s^{commit}" % templates) is None:
        sys.stderr.write("the rules ref %s does not exist here, so no document can be checked. Fetch the line first\n" % templates)
        print("documents 0 checked 0 failed")
        return 1
    rules = {}
    cache = {}
    failed = 0
    checked = 0
    for path in paths:
        text = source.read(path)
        if text is None:
            continue
        kind = doc_type(path, text)
        if kind is None:
            if path.startswith("docs/design/") and MARKER in text:
                doc = Markdown(path, text)
                for i, line in enumerate(doc.lines):
                    if MARKER in line:
                        doc.error(i, "a clarification marker is left: every [NEEDS CLARIFICATION: ...] is answered and removed before the document merges")
                for error in doc.errors:
                    sys.stderr.write(error + "\n")
                failed += 1
            continue
        checked += 1
        doc = Markdown(path, text)
        template_path = TEMPLATES[kind]
        if template_path not in cache:
            cache[template_path] = git(repo, "show", "%s:%s" % (templates, template_path))
        template_text = cache[template_path]
        if template_text is not None and kind == "decision":
            template_text = decision_template(template_text)
        if template_text is None:
            doc.error(0, "no %s template at %s on %s, so this document cannot be checked against it" % (kind.replace("-", " "), template_path, templates))
        else:
            check_common(doc, kind, template_text, path)
            if has_contents(Markdown(template_path, template_text)) and needs_index(kind, path, repo, templates, where, rules):
                check_index(doc, path)
            if kind == "decision":
                check_record_number(doc, path, repo, templates, where, rules)
            template_doc = Markdown(template_path, template_text)
            template_fields, _ = control_table(template_doc)
            if kind == "feature-spec" and template_fields and "Risk" in template_fields:
                fields, _ = control_table(doc)
                if fields is not None:
                    check_spec_class(doc, template_doc, fields)
            elif kind in ("plan", "milestone-report", "design-record", "fix-record"):
                check_class_rows(doc, kind, path, template_doc, source)
            if kind in ("design-record", "fix-record"):
                check_record_risk(doc, kind, template_doc, path, source)
            if kind == "feature-spec":
                if "quality" not in rules:
                    quality = git(repo, "show", "%s:docs/process/quality-requirements.md" % templates)
                    rules["quality"] = quality_lines(quality) if quality else []
                if not rules["quality"]:
                    doc.error(0, "no quality checklist in docs/process/quality-requirements.md on %s, so the Quality requirements section cannot be checked" % templates)
                check_feature_spec(doc, path, rules)
            elif kind == "plan":
                check_plan(doc, path, source)
            elif kind == "milestone-report":
                check_milestone(doc, path, source)
            elif kind == "delta-entry":
                if "delta-template" not in rules:
                    rules["delta-template"] = Markdown("delta-entry.md", template_text)
                check_delta(doc, path, source, rules)
        for error in doc.errors:
            sys.stderr.write(error + "\n")
        if doc.errors:
            failed += 1
    print("documents %d checked %d failed" % (checked, failed))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
