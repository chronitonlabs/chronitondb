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
    doclint.py history --repo DIR --templates REF [--write | --check] PATH...
    doclint.py indexes --repo DIR --templates REF [--source SRC] [--write]
    doclint.py delta --repo DIR --base REF [--source SRC] [--branch NAME] [--body FILE]
    doclint.py stock-tests --repo DIR --base REF [--source SRC] [--branch NAME] [--body FILE] [--issue STATE]
    doclint.py stock-tests-issue [--branch NAME] [--body FILE]

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
    docs/design/<dir>/decisions/*.md       decision record
    docs/decisions/*.md                    decision record (README.md is
                                           not one)
    docs/delta/<name>.md                   delta entry (README.md is the
                                           register)
    docs/releases/<line>-plan.md           line plan
    docs/releases/*.md                     release proposal
    docs/research/<issue>-<slug>.md        research report (README.md is
                                           not one)
    docs/reviews/<work>.md                 review record (README.md is
                                           not one)

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

A decision record new at REF is also checked for rule 1 of the README:
its name is its id and a slug, DEC-<KEY>-nnnn-<slug>.md, four digits or
more, under docs/design/<KEY>-<slug>/decisions/ with the key of that
directory (the issue number for a directory <issue>-<slug>), or under
docs/decisions/ with the key GOV, its title opens with its id, no other
record at SRC has that id, and its number is the next after the highest
merged at REF under its key, one number per new record and in order, so
it neither reuses a merged number nor leaves a gap. A record merged at
REF is never edited and is held to none of this: the records NNNN-<slug>.md
of docs/decisions/ were merged before the ids.

A document whose template at REF has the revision history, a table
Version, Date, Change, Decision record under the document control table,
is checked for it when the document is new at REF, has the table at REF or
at SRC, or is at another Version than at REF: one row for each version, in
order with no gap, each with a whole number, a YYYY-MM-DD date, what
changed and the id of a decision record or None, the last row the
document's Version, every row merged at REF unchanged, and under the table
the line "Full history in git: [commits of this file](ADDRESS)", ADDRESS
being https://github.com/<owner>/<repository>/commits/<line>/<path>: the
repository of the remote REF names (origin when REF names none), the line
REF names, and the document's own path. A document merged before its
template had the table keeps its old change history line until its next
version.

A feature spec is also checked for:

  1. its directory is docs/design/<KEY>-<slug>/
  2. its Feature class and switches section states the feature class
  3. its Feature requirements are FREQ-<KEY>-nnn lines, each with one EARS
     shape, one BCP 14 keyword and a source. A word of size or amount
     (large, small, many, few, reasonable, soon, high, low, scalable)
     needs a number on the line. A word of speed (fast, faster, quick,
     quickly, slow, efficient, efficiently) needs a number, or the
     mechanism that makes it so, named after the word in three words or
     more that follow "by", "because", "since" or "through" (the design
     record template, Requirement quality checklist, item 2). Whether the
     words name a mechanism is the reviewer's to judge
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
     switch, on-disk files, flush, compaction, streaming, repair) in any
     case, split at a comma, a semicolon or "and", or none,
     a public interface naming its area in brackets, one of FLOOR_AREAS
     (a phrase that names an area alone counts as a public interface and
     is refused), and a Low risk never touching a public
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

A review record is checked against the review record template once the
line has it. At a REF with no such template the record is passed over and
not counted: the first records were merged before the template was.

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

A research report is also checked for: its file name is
docs/research/<issue>-<slug>.md, the slug lower case words joined by
single hyphens, and its References row names that issue as #<issue>.

A delta entry is also checked for: the Header table holds the DEP-3 fields
of the template, each in its form (Origin, Bug, Bug-ChronitonDB, Forwarded,
dates YYYY-MM-DD), an Origin other than ChronitonDB links its commit (an
Apache one on github.com/apache/cassandra, another fork's on that fork,
never on chronitonlabs) and a hash it shows in backticks is the linked one,
and the register's index has its row with the same Forwarded, Added, Last
update and Issue, the Area the entry's Area section opens with, and the
lines its Lines section names as chronitondb-<x.y>. It prints "issue N
PATH" on stdout for each Bug-ChronitonDB issue, which the caller checks
exists.

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
states with its reason. It prints "patch NAME OLD NEW FILE" for each. No CI
workflow runs it yet.

index prints the Contents section each FILE needs, read from the working
tree, whatever its type. With --write it puts that section in the file in
place of its old one, or before its first heading below the title when it
has none. A Contents section that holds anything but blank lines and
index entries is refused with its line, and the file is left unchanged.
With --check it reports what is wrong with the file's index, the check of
point 4 above, also for a template. Authors and their tools run it after
any heading changes, before the commit.

history prints the history link each PATH needs, read from the working
tree. With --write it puts the link in place of the old one, or under the
revision history table, and in a document that still has the line "Change
history: the git history of this file." it puts the table in that line's
place, with one row for the document's Version and today's date, whose
change and decision record the author fills in. With --check it reports
what is wrong with the revision history and its link, whatever REF holds
of the document.

A document with an Areas row names one area or more of the list of
docs/process/areas.md at REF, joined by commas, each once, and one with a
Source row names one source of that page's list. A document merged at REF
without a row its template gained later, Areas, Supersedes or Source, keeps
none while it is at the Version it was merged at, a decision record for
good.

A document with an Exceptions row, a design record or a fix record, says
None there or names each principle it departs from by its id,
PRINCIPLE-nnn, joined by commas, each once and each a principle of
docs/process/principles.md at REF. A link whose text is the id counts as
the id. A document merged at REF without the row keeps none while it is at
the Version it was merged at, as for the rows above.

The supersede links of decision records hold both ways: each record a
Supersedes row names says "Superseded by" that record in its Status, and a
record whose Status says "Superseded by" another is named in that one's
Supersedes row, when it has the row.

indexes checks the generated indexes of the tree at SRC, and with --write
writes them into the working tree: docs/index/documents.md, every document
under docs/ whose document control table has a Document type row, by kind,
and once a record's Exceptions row names a principle a last section with
every such record under each principle it names,
docs/index/decisions.md, every decision record, docs/index/areas.md, the
same under each area of the areas page at REF, and INDEX.md in each
feature directory docs/design/<KEY>-<slug>/, its documents, the design
records that define its REQ ids and its decision records. A page that is
not what the documents give is a finding.

settings is the setting name check of release.md, The configuration file.
A setting name is a top level key of a yaml file, active ("name:") or
commented ("# name:" or "#name:"). Every setting of Apache's
conf/cassandra.yaml and conf/cassandra_latest.yaml at SRC is in ours,
conf/cassandra_chronitondb.yaml, active or commented, or left out with a
reason on a line "# Left out: <name>: <reason>". A setting Apache's two
files had at the merge base REF and have no more is gone from ours, or
flagged on a line "# Apache removed: <name>". Ours removed while the line
had it fails. With no file of ours on the line yet the check has nothing to
compare and says so. No CI workflow runs it yet: it becomes a check of
every pull request once the file exists.

delta is the delta register check of docs/delta/README.md, Keeping it
current, on the change at SRC since its merge base with REF. A file is
ChronitonDB's own when it falls under a path of the table Where things live
in docs/process/conventions.md at REF: a directory ("docs/"), a pattern
(".github/workflows/chronitondb-*.yml"), the directory before a "<...>"
placeholder, or one file. Every other file is a stock file, a file that
came from Apache Cassandra. A change that adds, edits, deletes or renames a
stock file adds or changes at least one entry docs/delta/<name>.md. It
passes without one when NAME, the pull request's branch, is an import of a
whole Apache release or of Apache's branch, import/cassandra-<...>, which
brings Apache Cassandra's own code. NAME is taken as given, so the caller
gives it only for a branch whose name it can trust: CI gives it for a
branch of the repository itself and never for the branch of a fork, whose
author chooses its name. It also passes without one when FILE, the pull
request's description, has a line "No delta entry: <reason>" with a reason
of three words or more. The line is for a feature's change that touches
only log lines Apache Cassandra writes. The check reads only that it is
there: the reviewer judges it against the change, and any other use of
it is a decision of the maintainers at review. Every entry the change adds or
changes passes the document rules of a delta entry above, against the
template at REF, and a changed entry has a Last-Update later than at REF,
or the same date when that is the date of the change, the date of the
commit SRC. No entry is renamed or deleted: its file name is its id, and a
change no longer carried keeps its entry with Status Dropped. It prints
"stock PATH" on stdout for each stock file, and the reason a change passes
without an entry.

stock-tests is the check of docs/process/testing.md, Policy 4, on the
change at SRC since its merge base with REF: a pre-existing test file of
Apache Cassandra changes in four ways only (principles.md, PRINCIPLE-013).
Such a file is one the line has at the merge base, in a directory named
test or with the name of a test (*Test.java, *Tests.java, test_*.py,
*_test.py), that is not the project's own by the table Where things live,
read as the delta check reads it. The permits are read at REF, the line,
never from the change, so a pull request cannot write its own. A changed
file passes by one of:

  1. NAME, the pull request's branch, is an import from Apache
     Cassandra: import/cassandra-<...>, a release or Apache's branch, or
     import/CASSANDRA-<n>, a single fix. Such an import brings Apache
     Cassandra's own test files, and the import history check holds what
     it brings. A commit of another project is no import from Apache
     Cassandra and takes one of the other ways. NAME is taken as given,
     as for delta
  2. the fix record of the pull request's issue at REF, a document under
     docs/design/ whose first heading opens "# Fix: #<issue>", lists the
     file in its Planned file list with the word test
  3. the design record or fix record of the pull request's issue at REF
     has a line "Pinned listing: <path>" with the file's path, and the
     change only adds lines of the listing to the file: any line in a
     file of plain data, one with no extension or a .txt, .json or .csv
     file, and in any other file only lines that are one quoted string,
     alone on the line but for a "+" or a ","
  4. a decision record at REF with the Status Accepted has a line
     "Approved stock test change: <path> for #<issue>, because
     <explanation>" with the file's path, the pull request's issue and a
     written explanation: eight different words or more, each of two
     letters or more, with no placeholder in it, such as TBD or todo

A record permits the change of its own issue only. The pull request's
issue is the issue of NAME when NAME is given: NAME is then a work branch,
<name>/<issue>-<slug>/<line>, and FILE, the pull request's description,
names that issue on a line "Fixes #<issue>" or "Part of #<issue>". With no
NAME, as for the branch of a fork, it is the one issue FILE names on such
a line. STATE is the answer of the GitHub API for that issue, and the
issue it shows is open and is no pull request. stock-tests-issue prints
the issue, so the caller can read its state first. A permit is used up
once a change to the file has reached REF, on its first parent history,
with the last change of the record or after it: a record permits the one
change it plans. A line of a record indented by four spaces or a tab is
code and permits nothing.

A record whose Status opens with Superseded permits nothing. A stock test
file that is deleted, renamed, binary, a symbolic link or changed in its
type passes only in an import. It prints "stock-test PATH: <way>" on
stdout for each file that passes, and "stock-tests N checked M failed".

Findings go to stderr as "PATH:LINE: reason", exit 1 when there is one.
A usage error exits 2.
"""

import fnmatch
import html
import json
import os
import re
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from markdown import Markdown, first_heading, first_table, outer_braces, table_cells  # noqa: E402

# The feature class line of the template section Feature class and switches,
# which the record parser reads too.
CLASS_LINE = re.compile(r"^Feature class: (purely additive|behaviour-changing), because \S.{2,}$")
MARKER = "[NEEDS CLARIFICATION"
KEY_DIR = re.compile(r"^docs/design/([A-Z]{3,5})-[a-z0-9]+(?:-[a-z0-9]+)*/")
FREQ_LINE = re.compile(r"^\s*(?:(?:[-*+]|[0-9]+[.)])\s+)?[*_`]*(FREQ-([A-Z]{3,5})-[0-9]{3})(?![0-9])[*_`]*\s*(\([^)]*\))?\s*:?\s*(.*)$")
KEYWORDS = re.compile(r"\b(MUST NOT|MUST|SHALL NOT|SHALL|SHOULD NOT|SHOULD|NOT RECOMMENDED|RECOMMENDED|MAY|REQUIRED|OPTIONAL)\b")
# A word of size or amount needs a number. A word of speed needs a number
# or the mechanism that makes it so, which the line names after the word
# (the design record template, Requirement quality checklist, item 2).
UNMEASURED = re.compile(r"\b(large|small|many|few|reasonable|soon|high|low|scalable)\b", re.I)
SPEED = re.compile(r"\b(fast|faster|quick|quickly|slow|efficient|efficiently)\b", re.I)
MECHANISM = re.compile(r"\b(?:by|because|since|through)\s+\S+(?:\s+\S+){2,}", re.I)
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
# Shared state, request path and new feature or switch name what a Normal risk
# code review adds a checklist for: threads, pools, caches or other state
# several requests share, any path whose cost grows with data or traffic, and
# a new feature or switch. The last five
# name what the code of a change does on the Critical floor, in Apache
# Cassandra's files or in ChronitonDB's own (classification.md, The Critical
# floor).
TOUCHES = ("public interface", "stock behaviour", "new input or privilege", "new dependency",
           "shared state", "request path", "new feature or switch",
           "on-disk files", "flush", "compaction", "streaming", "repair")
FLOOR = ("public interface", "stock behaviour")
# The floor's public interfaces: the areas of compatibility the Cassandra
# Enhancement Proposals page lists under Compatibility Concerns, plus
# virtual tables, ChronitonDB's one addition (classification.md, The floor).
# A Touches row names public interface with its area in brackets, such as
# "public interface (configuration)", and each area is found by its words.
FLOOR_AREAS = (
    ("native protocol and CQL", r"native\s+protocol|protocol\s+version|\bcql\b"),
    ("gossip and the messaging service", r"\bgossip|messaging|internode|\bverbs?\b"),
    ("pluggable components (SPIs) such as authorisation and triggers",
     r"\bspis?\b|pluggable|\bplug-?ins?\b|authori[sz]|authenticat|\btriggers?\b"),
    ("commitlog, hint log and cache files", r"commit\s*log|hint\s*log|\bhints?\b|cache\s+files?|saved\s+caches?"),
    ("sstable components", r"\bsstables?\b"),
    ("configuration", r"configuration|\bconfig\b|\byaml\b|system\s+propert"),
    ("JMX MBeans including metrics", r"\bjmx\b|\bmbeans?\b|\bmetrics?\b"),
    ("monitoring", r"\bmonitoring\b"),
    ("client tool classes", r"client\s+tool"),
    ("command line tools and arguments", r"command\s+line|\bnodetool\b|\bcqlsh\b|\btools?\b|\barguments?\b"),
    ("operational routines", r"operational\s+routines?|\broutines?\b|\brunbooks?\b"),
    ("virtual tables", r"virtual\s+tables?|\bsystem_views\b"),
)
# The words of an on-disk format, which the CEP list names by its files.
ON_DISK = re.compile(r"on.?disk|\bformats?\b|\bfiles?\b", re.I)
# Text in brackets, which may itself hold one pair of brackets, as the area
# "pluggable components (SPIs) such as authorisation and triggers" does.
BRACKETS = r"\(((?:[^()]|\([^()]*\))*)\)"
PUBLIC_INTERFACE = re.compile(r"public\s+interface\b(\s*" + BRACKETS + r")?", re.I)
# The strictest value of each family, which a missing or unreadable row counts as.
STRICTEST = {"Risk": "Critical", "Size": "Byzantine", "Reach": "Cross-cutting"}
NOT_APPLICABLE = re.compile(r"^Not applicable:\s*(\S.*)$")
# A section claims Not applicable when its own text starts with the words
# and then any punctuation, the end of the line, "because", "since" or "as",
# or a qualifier that points at the document itself, such as "here", "for
# this feature" or "in this case", and when it starts with "N/A" or "n/a",
# the slash written. Only a preposition that names something else makes
# content: "Not applicable to clusters without ..." and "Not applicable to
# this release line only ..." are content, and so is a word NA.
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
# problems. Ubuntu's rule is about that section, so the test plan
# is not held to it.
DISMISSIVE_RISK = re.compile(r"^\W*((low|no|minimal|negligible)\s+risk\b|(none|low|nothing)\s*([.,;:!]|$))", re.I)
# The Touches phrases are split at a comma, a semicolon or "and", and read
# in any case. An area in brackets is cut out first, so its own commas and
# "and" split nothing.
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
    "research-report": "docs/process/templates/research-report.md",
    "review-record": "docs/process/templates/review-record.md",
    "decision": "docs/decisions/README.md",
}
# The types whose first documents were merged before their template. Such a
# document is passed over at a rules ref that has no template for it.
LATE_TEMPLATES = ("review-record",)
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
        if len(parts) == 5 and parts[3] == "decisions":
            return "decision"
        return None
    if re.match(r"^docs/imports/[^/]+\.md$", path):
        return "import-record"
    if re.match(r"^docs/decisions/[^/]+\.md$", path) and path != "docs/decisions/README.md":
        return "decision"
    if re.match(r"^docs/delta/[^/]+\.md$", path) and path != "docs/delta/README.md":
        return "delta-entry"
    if re.match(r"^docs/releases/[^/]+-plan\.md$", path):
        return "line-plan"
    if re.match(r"^docs/releases/[^/]+\.md$", path):
        return "release-proposal"
    if re.match(r"^docs/research/[^/]+\.md$", path) and path != "docs/research/README.md":
        return "research-report"
    if re.match(r"^docs/reviews/[^/]+\.md$", path) and path != "docs/reviews/README.md":
        return "review-record"
    return None


RESEARCH_NAME = re.compile(r"^docs/research/([0-9]+)-[a-z0-9]+(?:-[a-z0-9]+)*\.md$")


def check_research(doc, path):
    """A research report's file name is docs/research/<issue>-<slug>.md,
    and its References row names that issue (additive.md, Work intake)."""
    match = RESEARCH_NAME.match(path)
    if not match:
        doc.error(0, "a research report is docs/research/<issue>-<slug>.md, the issue number of its spike and a slug of lower case words joined by single hyphens")
        return
    fields, _ = control_table(doc)
    if not fields or "References" not in fields:
        return
    value, line = fields["References"]
    if not re.search(r"(?<![0-9A-Za-z])#%s(?![0-9])" % match.group(1), value):
        doc.error(line, "the References row names the spike's issue as #%s, the number in the file name" % match.group(1))


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


# The id of a decision record: DEC, the feature key, the reserved key GOV
# for a decision of the whole project, or the issue number of a design
# directory that has no key, then four digits or more.
DECISION_ID = r"DEC-(?:[A-Z]{3,5}|[0-9]+)-[0-9]{4,}"
DECISION_WORD = "DEC-<KEY>-nnnn"
GOV_KEY = "GOV"


def allowed_statuses(value):
    """The Status values a template allows: "Draft, Approved or Superseded",
    "Current or Dropped", "Proposed, Accepted, or Superseded by NNNN"."""
    words = re.split(r",\s*(?:or\s+)?|\s+or\s+", value.strip().rstrip("."))
    return [word.strip() for word in words if word.strip()]


def status_ok(value, allowed):
    for word in allowed:
        # A record is superseded by a record named by its id, or by its
        # number when the record that replaces it is one merged before the
        # ids (docs/decisions/README.md, rule 1).
        if "NNNN" in word or DECISION_WORD in word:
            stem = word.replace("NNNN", "").replace(DECISION_WORD, "")
            if re.match("^" + re.escape(stem) + r"(?:" + DECISION_ID + r"|[0-9]{4})(?![0-9A-Za-z])", value):
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
    """One EARS shape, one BCP 14 keyword, a source, no word of size or
    amount without a number, and no word of speed without a number or the
    mechanism that makes it so."""
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
    if not re.search(r"[0-9]", before_source):
        if UNMEASURED.search(before_source):
            doc.error(index, "%s uses an unmeasured word without a number" % rid)
        speed = SPEED.search(before_source)
        if speed and not MECHANISM.search(before_source, speed.end()):
            doc.error(index, "%s says '%s' without a number or the mechanism that makes it so, named after by, because, since or through" % (rid, speed.group(1)))


def check_common(doc, kind, template_text, path, late=()):
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
                    if field not in late:
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
    # for the on-disk format changes only.
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


def floor_areas(text):
    """The floor areas a text names, in the order of FLOOR_AREAS."""
    return [name for name, words in FLOOR_AREAS if re.search(words, text, re.I)]


def touch_of(word):
    """The Touches phrase a word of the row is: one of TOUCHES, public
    interface when it names a floor area without saying so, or None."""
    if word in TOUCHES:
        return word
    return "public interface" if floor_areas(word) else None


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
            areas = ", ".join(name for name, _ in FLOOR_AREAS)
            for match in PUBLIC_INTERFACE.finditer(value):
                if match.group(1) is None:
                    doc.error(line, "the 'Touches' row names public interface without its area. Name it in brackets, such as public interface (configuration), from: %s (classification.md, The floor)" % areas)
                elif not floor_areas(match.group(2)):
                    hint = ""
                    if ON_DISK.search(match.group(2)):
                        hint = ". An on-disk file is named by its area: sstable components, or commitlog, hint log and cache files"
                    doc.error(line, "the 'Touches' row names public interface (%s), which names none of the compatibility areas: %s%s (classification.md, The floor)" % (match.group(2).strip(), areas, hint))
            text = re.sub(BRACKETS, "", value).strip().rstrip(".")
            words = [w.strip().lower() for w in TOUCHES_SPLIT.split(text) if w.strip()]
            if words == ["none"]:
                pass
            else:
                for word in words:
                    touch = touch_of(word)
                    if word in TOUCHES:
                        touches.add(word)
                    elif word == "none":
                        doc.error(line, "the 'Touches' row says none beside other phrases. It says none alone, or lists what the change touches")
                    elif touch:
                        # Counted as a public interface, so the floor and the
                        # sections it requires apply while the row is fixed.
                        touches.add(touch)
                        doc.error(line, "the 'Touches' row names '%s', which is a compatibility area of %s. Write it as public interface (%s) (classification.md, The floor)" % (word, " and ".join(floor_areas(word)), word))
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
        touches = {touch_of(w.strip().lower()) for w in TOUCHES_SPLIT.split(text) if w.strip()} - {None}
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
    plan, never opens by playing the risk down."""
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
                # Its test plan alone is not enough, as in a record.
                doc.error(headings[number][1], "section %s %s is empty. It names what could break, how a user would see it and the tests that would catch it, and its test plan alone is not enough (classification.md)" % (number, title))
                continue
            check_risk_text(doc, headings[number][1], "section %s %s" % (number, title), opener=title == WPCO)
    check_non_goals(doc)
    return levels


def check_non_goals(doc):
    """The Non-goals of section 1, required at every class, never Not
    applicable."""
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
    Markdown link to a feature-spec.md the source holds, or None."""
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
    spec's section 4."""
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
    elif origin and re.match(r"^(Apache commit|Backport of Apache commit)", origin) and not re.search(r"[0-9a-f]{7,40}", origin):
        doc.error(line, "an Apache Origin names the commit hash")
    elif origin:
        check_origin_link(doc, line, origin)
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
    check_area_and_lines(doc, name, row)


APACHE_REPO = ("apache", "cassandra")
COMMIT_LINK = re.compile(r"https://github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)/commit/([0-9a-f]{7,40})(?![0-9A-Za-z])")
SHOWN_HASH = re.compile(r"`([0-9a-f]{7,40})`")
LINE_NAME = re.compile(r"\bchronitondb-([0-9]+\.[0-9]+|sandbox)\b")


def check_origin_link(doc, line, origin):
    """An Origin other than ChronitonDB links the commit it came from: an
    Apache commit on github.com/apache/cassandra, another fork's commit on
    the fork's own repository, never Apache's and never one of
    chronitonlabs, whose work is ours (upstream.md, Commits from other
    projects). A hash shown in backticks is the start of the linked one."""
    if origin.startswith("ChronitonDB"):
        return
    links = COMMIT_LINK.findall(origin)
    if origin.startswith(("Apache commit", "Backport of Apache commit")):
        wanted = [link for link in links if link[:2] == APACHE_REPO]
        if not wanted:
            doc.error(line, "an Apache Origin links its commit, https://github.com/apache/cassandra/commit/<hash>")
            return
    else:
        wanted = [link for link in links if link[:2] != APACHE_REPO and link[0].lower() != "chronitonlabs"]
        if not wanted:
            if any(link[:2] == APACHE_REPO for link in links):
                doc.error(line, "a fork Origin links an Apache commit. An Apache commit is Origin Apache commit or Backport of Apache commit, even when a fork holds it")
            elif any(link[0].lower() == "chronitonlabs" for link in links):
                doc.error(line, "a fork Origin links a chronitonlabs repository. The work of our own organisation is Origin ChronitonDB")
            else:
                doc.error(line, "a fork Origin links the fork's commit, https://github.com/<owner>/<repo>/commit/<hash>")
            return
    for shown in SHOWN_HASH.findall(origin):
        if not any(link[2].startswith(shown) or shown.startswith(link[2]) for link in wanted):
            doc.error(line, "Origin shows the commit `%s` and links %s" % (shown, ", ".join(link[2] for link in wanted)))


def check_area_and_lines(doc, name, row):
    """The entry's Area section opens with the register's Area for it,
    then a colon or a full stop, and its Lines section names, as
    chronitondb-<x.y>, the same lines as the register's Lines column."""
    span = plain_section_span(doc, "Area")
    if span is not None:
        text = [line for _, line in text_lines(doc, span) if line.strip()]
        opening = text[0].split(":", 1)[0].strip().rstrip(".") if text else ""
        if opening != row["Area"].strip():
            doc.error(span[0], "the Area section opens with '%s', the register's Index row for %s says Area '%s'. Open the section with the same area, then a colon and the files" % (opening, name, row["Area"].strip()))
    span = plain_section_span(doc, "Lines")
    if span is not None:
        named = set()
        for _, line in text_lines(doc, span):
            named.update(LINE_NAME.findall(line))
        listed = set(part.strip() for part in re.split(r",|\band\b", row["Lines"]) if part.strip())
        if not named:
            doc.error(span[0], "the Lines section names no line. Name each one as `chronitondb-<x.y>`")
        elif named != listed:
            doc.error(span[0], "the Lines section names %s, the register's Index row for %s says Lines %s" % (", ".join(sorted(named)), name, ", ".join(sorted(listed))))


# The delta register check: the page that says which files are
# ChronitonDB's own, the line of a pull request description that waives
# the entry, and the import branches that bring Apache's own code.
CONVENTIONS = "docs/process/conventions.md"
WAIVER = re.compile(r"^No delta entry:\s*(.*?)\s*$")
WHOLE_IMPORT = re.compile(r"^import/cassandra-[0-9]")
ENTRY = re.compile(r"^docs/delta/[^/]+\.md$")


def own_paths(text):
    """The paths of ChronitonDB's own files: every path in backticks in
    the table of conventions.md, Where things live. A path ending in "/"
    is a directory, a path with "*" a pattern, a path with a "<...>"
    placeholder the directory before it, any other path one file."""
    doc = Markdown(CONVENTIONS, text)
    span = plain_section_span(doc, "Where things live")
    if span is None:
        return []
    paths = []
    for _, cells in first_table(doc, span[0], span[1]):
        for token in re.findall(r"`([^`]+)`", cells[1] if len(cells) > 1 else ""):
            if "<" in token:
                token = token[:token.index("<")]
                token = token[:token.rfind("/") + 1]
            if token and token not in paths:
                paths.append(token)
    return paths


def is_own(path, paths):
    for own in paths:
        if own.endswith("/"):
            if path.startswith(own):
                return True
        elif "*" in own:
            if fnmatch.fnmatchcase(path, own):
                return True
        elif path == own:
            return True
    return False


def is_entry(path):
    return bool(path) and bool(ENTRY.match(path)) and path != "docs/delta/README.md"


def changes(repo, base, where):
    """(status, path, old path) of each file changed at SRC since its merge
    base with REF, with renames found, or None when there is no merge
    base. The worktree also counts its untracked files as added."""
    head = "HEAD" if where in ("index", "worktree") else where
    merge_base = git(repo, "merge-base", base, head)
    if merge_base is None:
        return None
    args = ["diff", "--name-status", "-z", "-M"]
    if where == "index":
        args.append("--cached")
    args.append(merge_base.strip())
    if where not in ("index", "worktree"):
        args.append(where)
    out = git(repo, *args)
    if out is None:
        return None
    words = out.split("\0")
    found = []
    index = 0
    while index + 1 < len(words) and words[index]:
        status = words[index]
        if status[0] in "RC":
            found.append((status[0], words[index + 2], words[index + 1]))
            index += 3
        else:
            found.append((status[0], words[index + 1], None))
            index += 2
    if where == "worktree":
        others = git(repo, "ls-files", "--others", "--exclude-standard", "-z") or ""
        found += [("A", path, None) for path in others.split("\0") if path]
    return found


def change_date(repo, where):
    """The date of the change, YYYY-MM-DD in UTC: the date of the commit
    SRC, or today for the index and the worktree."""
    if where not in ("index", "worktree"):
        date = git(repo, "log", "-1", "--no-show-signature", "--format=%ct", where)
        if date and date.strip().isdigit():
            return time.strftime("%Y-%m-%d", time.gmtime(int(date.strip())))
    return time.strftime("%Y-%m-%d", time.gmtime())


def header_value(text, field):
    doc = Markdown("entry", text)
    span = plain_section_span(doc, "Header")
    if span is None:
        return None
    for _, cells in first_table(doc, span[0], span[1]):
        if len(cells) >= 2 and cells[0] == field:
            return cells[1]
    return None


def check_entry(repo, base, source, path, status, template_text, today):
    """An added or changed entry: the document rules of its template, its
    Contents index, its DEP-3 header and its Index row, and for a changed
    entry a Last-Update later than the line's, or the line's when that is
    already the date of the change."""
    text = source.read(path) or ""
    doc = Markdown(path, text)
    check_common(doc, "delta-entry", template_text, path)
    if has_contents(Markdown(TEMPLATES["delta-entry"], template_text)):
        check_index(doc, path)
    check_delta(doc, path, source, {"delta-template": Markdown("delta-entry.md", template_text)})
    if status == "M":
        before = git(repo, "show", "%s:%s" % (base, path))
        old = header_value(before, "Last-Update") if before else None
        new = header_value(text, "Last-Update")
        if old and new and DATE.match(old) and DATE.match(new):
            if new < old:
                doc.error(0, "Last-Update %s is before the line's %s" % (new, old))
            elif new == old and old != today:
                doc.error(0, "the entry changes and its Last-Update stays %s, as on the line. Set it to the date of this change, %s, in the entry and in its Index row" % (old, today))
    return doc.errors


def waiver_of(body):
    """The reason on the line "No delta entry: <reason>" of a pull request
    description, "" when the line gives none, None when there is no such
    line."""
    for line in (body or "").splitlines():
        match = WAIVER.match(line.strip())
        if match:
            return match.group(1)
    return None


def check_register(repo, base, where, branch, body):
    """The delta register check. Returns the findings, the stock files the
    change touches, the number of entries it adds or changes, and the note
    on what lets it pass without an entry."""
    conventions = git(repo, "show", "%s:%s" % (base, CONVENTIONS))
    paths = own_paths(conventions) if conventions else []
    if not paths:
        return ["%s on %s has no Where things live table, so ChronitonDB's own files cannot be told from stock files" % (CONVENTIONS, base)], [], 0, None
    changed = changes(repo, base, where)
    if changed is None:
        return ["no merge base of %s and %s, so the change cannot be read. Fetch the line first" % (base, where)], [], 0, None
    template_text = git(repo, "show", "%s:%s" % (base, TEMPLATES["delta-entry"]))
    source = Source(repo, where)
    today = change_date(repo, where)
    errors, stock, entries = [], [], 0
    for status, path, old in changed:
        for name in (old, path):
            if name and not is_own(name, paths) and name not in stock:
                stock.append(name)
        if status == "R" and is_entry(old):
            errors.append("%s: the entry is renamed to %s. An entry's file name is its id and never changes (docs/delta/README.md, Entries). Keep the old name" % (old, path))
        elif status == "D" and is_entry(path):
            errors.append("%s: the entry is deleted. An entry's file name is its id and stays. A change no longer carried keeps its entry, with Status Dropped" % path)
        elif is_entry(path):
            entries += 1
            if template_text is None:
                errors.append("%s: no delta entry template at %s on %s, so the entry cannot be checked" % (path, TEMPLATES["delta-entry"], base))
            else:
                errors += check_entry(repo, base, source, path, "A" if status in "AC" else "M", template_text, today)
    note = None
    waiver = waiver_of(body)
    if waiver is not None and len(waiver.split()) < REASON_WORDS:
        errors.append("the pull request's line 'No delta entry:' gives no reason. Write the reason after the colon, in %d words or more" % REASON_WORDS)
    elif stock and not entries:
        if branch and WHOLE_IMPORT.match(branch):
            note = "the branch %s imports a whole Apache release or Apache's branch, which brings Apache Cassandra's own code and needs no entry" % branch
        elif waiver is not None:
            note = "no delta entry, as the pull request says: %s" % waiver
        else:
            shown = ", ".join(stock[:10]) + (" and %d more" % (len(stock) - 10) if len(stock) > 10 else "")
            errors.append("the change touches %d stock file(s), %s, and adds or updates no entry in docs/delta/. Add its entry from docs/process/templates/delta-entry.md with its row in the Index of docs/delta/README.md, or update the entry of the change it extends, with a new Last-Update. A feature's change that touches only log lines Apache Cassandra writes needs no entry and says so in the pull request description on a line 'No delta entry: <reason>'. Any other use of that line is a decision of the maintainers at review (docs/process/principles.md, PRINCIPLE-011)" % (len(stock), shown))
    return errors, stock, entries, note


# The stock test check: the directory name that marks a test file, the
# lines of a pull request description that name its issue, the heading of
# a record of one issue, and the lines of the records that permit a change
# to a stock test file.
TEST_DIR = re.compile(r"(?:^|/)test/")
TEST_NAME = re.compile(r"(?:^|/)(?:[^/]*Tests?\.java|test_[^/]*\.py|[^/]*_test\.py)$")
WORK_BRANCH = re.compile(r"^[^/]+/([0-9]+)-[^/]+/[^/]+$")
LISTING_DATA = re.compile(r"(?:^|/)(?:[^/.]+|[^/]+\.(?:txt|json|csv))$")
LISTING_STRING = re.compile(r"""^\s*(?:\+\s*)?(?:"(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*')\s*[,+]?\s*$""")
ISSUE_LINE = re.compile(r"^(?:Fixes|Part of) #([0-9]+)\.?$")
RECORD_OF = re.compile(r"^(Fix|Design): #([0-9]+)(?![0-9])")
PLANNED = re.compile(r"^(\S+) (new|edit|test|stock)$")
PINNED = re.compile(r"^Pinned listing: ([^\s{}`]+)$")
TEST_CHANGE = re.compile(r"^Approved stock test change: ([^\s{}`]+) for #([0-9]+), because (\S.*)$")
EXPLANATION_WORDS = 8
PLACEHOLDER = re.compile(r"(?i:\b(?:tbd|todo|fixme|xxx|lorem)\b)|\.\.\.|\u2026|<[a-z][a-z ,.'-]*>|\{[^{}]*\}")
APACHE_IMPORT = re.compile(r"^import/(?:cassandra-[0-9]|CASSANDRA-[1-9])")
SYMLINK = "120000"
FOUR_WAYS = ("A pre-existing test file of Apache Cassandra changes in four ways only (docs/process/principles.md, PRINCIPLE-013): "
             "in an import from Apache Cassandra, in a fix to stock whose merged fix record lists the file as 'test' in its Planned file list, "
             "by lines added to a listing that the merged design record or fix record names on a line 'Pinned listing: <path>', "
             "or with an accepted decision record that has the line 'Approved stock test change: <path> for #<issue>, because <explanation>', the explanation in eight different words of two letters or more, with no placeholder such as TBD. "
             "The record merges first, in its own pull request, and this pull request names its issue on a line 'Fixes #<issue>' "
             "or 'Part of #<issue>'. A record permits the change of its own issue only: the issue of the work branch, "
             "<name>/<issue>-<slug>/<line>, for a branch of this repository, and the one issue the description names for a fork. "
             "The issue is open, and a permit is used up once a change to the file has reached the line after the record. "
             "A fork feature puts its tests in its own files (docs/process/conventions.md, Where things live)")


def is_explained(text):
    """Whether the explanation of an approval is written: eight different
    words or more, each of two letters or more with the case of letters
    ignored, and no placeholder in it. A placeholder is one of the words
    TBD, TODO, FIXME, XXX and lorem in any case of letters, three full
    stops or an ellipsis, a text in braces or lower case words in angle
    brackets."""
    words = set(word.lower() for word in re.findall(r"[^\W\d_]{2,}", text))
    return len(words) >= EXPLANATION_WORDS and not PLACEHOLDER.search(text)


def is_stock_test(path, paths):
    return bool(TEST_DIR.search(path) or TEST_NAME.search(path)) and not is_own(path, paths)


def diff_since(repo, merge_base, where, *options):
    args = ["diff", "-z", "-M"] + list(options)
    if where == "index":
        args.append("--cached")
    args.append(merge_base)
    if where not in ("index", "worktree"):
        args.append(where)
    return git(repo, *args)


def file_changes(repo, merge_base, where):
    """Each file changed at SRC since the merge base, by its path there:
    (status, path at the merge base, mode before, mode after, lines
    added, lines removed), the two counts None for a binary file. None
    when the change cannot be read."""
    raw = diff_since(repo, merge_base, where, "--raw", "--abbrev=40")
    counts = diff_since(repo, merge_base, where, "--numstat")
    if raw is None or counts is None:
        return None
    lines = {}
    words = counts.split("\0")
    index = 0
    while index < len(words) and words[index]:
        added, removed, path = words[index].split("\t", 2)
        if path:
            index += 1
        else:
            path = words[index + 2]
            index += 3
        lines[path] = (None, None) if added == "-" else (int(added), int(removed))
    found = {}
    words = raw.split("\0")
    index = 0
    while index + 1 < len(words) and words[index]:
        before, after, _, _, status = words[index].lstrip(":").split(" ")
        if status[0] in "RC":
            old, path = words[index + 1], words[index + 2]
            index += 3
        else:
            old = path = words[index + 1]
            index += 2
        found[path] = (status[0], old, before, after) + lines.get(path, (None, None))
    return found


def issues_of(body):
    """The issues a pull request description names on its lines "Fixes
    #<issue>" and "Part of #<issue>"."""
    found = []
    for line in (body or "").splitlines():
        match = ISSUE_LINE.match(line.strip())
        if match and match.group(1) not in found:
            found.append(match.group(1))
    return found


def plain_lines(doc):
    """The lines of a document outside fences and comments. A line
    indented by four spaces or a tab is left out: Markdown shows such a
    line as code."""
    return [doc.visible[index].strip() for index in range(len(doc.lines))
            if index not in doc.fenced and index not in doc.commented and not re.match(r"^(?: {4}| {0,3}\t)", doc.visible[index])]


def own_issue(branch, body):
    """The issue a pull request is the work of, and when there is none
    the reason. For a branch of the repository it is the issue of its
    work branch, <name>/<issue>-<slug>/<line>, which the description
    names too. With no branch name, as for a fork, whose author chooses
    the name, it is the one issue the description names."""
    named = issues_of(body)
    if branch:
        match = WORK_BRANCH.match(branch)
        if not match:
            return None, "the head branch %s is not the work branch of an issue, <name>/<issue>-<slug>/<line>" % branch
        if match.group(1) not in named:
            return None, ("the pull request description does not name #%s, the issue of the branch %s, on a line 'Fixes #%s' or 'Part of #%s'"
                          % (match.group(1), branch, match.group(1), match.group(1)))
        return match.group(1), None
    if not named:
        return None, "the pull request description names no issue"
    if len(named) > 1:
        return None, "the pull request description names more than one issue, %s, and a pull request is the work of one" % " and ".join("#" + issue for issue in named)
    return named[0], None


def issue_closed(state, issue):
    """Why the answer of the GitHub API for an issue does not show the
    issue open, None when it does. A pull request has a number too and
    is no issue."""
    if not isinstance(state, dict) or str(state.get("number")) != issue:
        return "the state of #%s cannot be read" % issue
    if "pull_request" in state:
        return "#%s is a pull request, not an issue" % issue
    if state.get("state") != "open":
        return "the issue #%s is not open" % issue
    return None


def first_parents(repo, base):
    out = git(repo, "rev-list", "--first-parent", base)
    return out.split() if out else []


def is_unused(repo, base, line, record, path):
    """Whether the permit a record gives for a file is still unused: no
    change to the file reached the line with the last change of the
    record or after it. line is the first parent history of REF, newest
    first."""
    def last(name):
        return (git(repo, "log", "-1", "--first-parent", "--no-show-signature", "--format=%H", base, "--", name) or "").strip()
    permit, change = last(record), last(path)
    if permit not in line:
        return False
    return change not in line or line.index(change) > line.index(permit)


def added_lines(repo, merge_base, where, path):
    """The lines a change adds to a file, None when they cannot be read."""
    args = ["diff", "-U0", "--no-color", "--no-ext-diff", "--no-textconv", "--no-renames"]
    if where == "index":
        args.append("--cached")
    args.append(merge_base)
    if where not in ("index", "worktree"):
        args.append(where)
    out = git(repo, *(args + ["--", path]))
    if out is None:
        return None
    return [line[1:] for line in out.split("\n") if line.startswith("+") and not line.startswith("+++ ")]


def test_permits(repo, base):
    """What the records at REF permit, as three lists: (issue, path,
    record) for each file a fix record plans as test, the same for each
    Pinned listing line of a design record or fix record, and for each
    Approved stock test change line of an accepted decision record, when
    its explanation is written."""
    planned, pinned, approved = [], [], []
    listing = git(repo, "ls-tree", "-r", "--name-only", base, "--", "docs/design/", "docs/decisions/") or ""
    for path in listing.split("\n"):
        kind = doc_type(path, "") if path.endswith(".md") else None
        if kind != "decision" and len(path.split("/")) != 4:
            continue
        text = git(repo, "show", "%s:%s" % (base, path))
        if text is None:
            continue
        doc = Markdown(path, text)
        fields, _ = control_table(doc)
        status = fields["Status"][0] if fields and "Status" in fields else ""
        if kind == "decision":
            if status != "Accepted":
                continue
            for line in plain_lines(doc):
                match = TEST_CHANGE.match(line)
                if match and is_explained(match.group(3)):
                    approved.append((match.group(2), match.group(1), path))
            continue
        heading = RECORD_OF.match(first_heading(text))
        if not heading or status.startswith("Superseded"):
            continue
        issue = heading.group(2)
        for line in plain_lines(doc):
            match = PINNED.match(line)
            if match:
                pinned.append((issue, match.group(1), path))
        span = plain_section_span(doc, "Planned file list")
        if heading.group(1) == "Fix" and span is not None:
            for index in range(span[0] + 1, span[1]):
                if index in doc.fenced and index not in doc.fences:
                    match = PLANNED.match(doc.lines[index].strip())
                    if match and match.group(2) == "test":
                        planned.append((issue, match.group(1), path))
    return planned, pinned, approved


def check_stock_tests(repo, base, where, branch, body, state=None):
    """The stock test check. Returns the findings, for each stock test
    file the change touches that passes the file and the way it passes,
    and the number of stock test files the change touches. state is the
    answer of the GitHub API for the issue of the pull request, None when
    the caller has none."""
    conventions = git(repo, "show", "%s:%s" % (base, CONVENTIONS))
    paths = own_paths(conventions) if conventions else []
    if not paths:
        return ["%s on %s has no Where things live table, so the project's own files cannot be told from stock files" % (CONVENTIONS, base)], [], 0
    head = "HEAD" if where in ("index", "worktree") else where
    merge_base = (git(repo, "merge-base", base, head) or "").strip()
    changed = file_changes(repo, merge_base, where) if merge_base else None
    if changed is None:
        return ["no merge base of %s and %s, so the change cannot be read. Fetch the line first" % (base, where)], [], 0
    touched = []
    for path in sorted(changed):
        status, old, before, after, added, removed = changed[path]
        # A file the change adds is not a pre-existing one. A renamed file
        # is, by the name the line has it under.
        if status != "A" and is_stock_test(old, paths) and git(repo, "cat-file", "-e", "%s:%s" % (merge_base, old)) is not None:
            touched.append((old, path, status, before, after, added, removed))
    if not touched:
        return [], [], 0
    if branch and APACHE_IMPORT.match(branch):
        way = "the branch %s is an import from Apache Cassandra, which brings its own test files. The import history check holds what it brings" % branch
        return [], [(old, way) for old, _, _, _, _, _, _ in touched], len(touched)
    issue, no_issue = own_issue(branch, body)
    if issue and state is not None:
        no_issue = issue_closed(state, issue)
        issue = None if no_issue else issue
    planned, pinned, approved = test_permits(repo, base)
    line = first_parents(repo, base)
    errors, passed = [], []

    def permit(found, old):
        """The record that permits the change of a file for the issue of
        the pull request, and whether its permit is used up."""
        record = next((record for of, name, record in found if name == old and of == issue), None)
        return record, bool(record) and not is_unused(repo, base, line, record, old)

    for old, path, status, before, after, added, removed in touched:
        refused = None
        if status == "D":
            refused = "is deleted"
        elif status in "RC":
            refused = "is renamed to %s" % path
        elif status == "T" or SYMLINK in (before, after):
            refused = "is or becomes a symbolic link or another type of file"
        elif added is None:
            refused = "is a binary file"
        if refused:
            errors.append("%s: the file %s. A pre-existing test file of Apache Cassandra is deleted, renamed, replaced by a link "
                          "or changed as a binary file only by an import from Apache Cassandra" % (old, refused))
            continue
        used = None
        record, spent = permit(planned, old)
        if record and not spent:
            passed.append((old, "the fix record %s plans it as test" % record))
            continue
        used = record or used
        record, spent = permit(approved, old)
        if record and not spent:
            passed.append((old, "the decision record %s approves the change" % record))
            continue
        used = record or used
        record, spent = permit(pinned, old)
        if record and not spent:
            lines = [] if LISTING_DATA.search(old) else added_lines(repo, merge_base, where, old)
            other = None if lines is None else [text for text in lines if not LISTING_STRING.match(text)]
            if removed:
                errors.append("%s: %s names the file as a pinned listing, and the change removes or alters %d line(s) of it. "
                              "A pinned listing only gains lines. A change to an existing line needs an accepted decision record with the line "
                              "'Approved stock test change: %s for #<issue>, because <explanation>'" % (old, record, removed, old))
            elif other is None or other:
                errors.append("%s: %s names the file as a pinned listing, and the change adds %s that no listing holds. "
                              "A file of plain data, one with no extension or a .txt, .json or .csv file, gains any line. In any other file, "
                              "such as a test class, a pinned listing gains only lines that are one quoted string, alone on the line but for a "
                              "'+' or a ','. Any other added line needs an accepted decision record with the line "
                              "'Approved stock test change: %s for #<issue>, because <explanation>'"
                              % (old, record, "lines that cannot be read" if other is None else "%d line(s)" % len(other), old))
            else:
                passed.append((old, "%s names it as a pinned listing and the change only adds lines of the listing" % record))
            continue
        used = record or used
        if used and not line:
            errors.append("%s: the history of %s cannot be read here, so the permit of %s cannot be told unused. Fetch the whole line first" % (old, base, used))
        elif used:
            errors.append("%s: the permit of %s is used up: a change to the file reached %s with that record or after it. "
                          "A record permits the one change it plans. A further change needs its own record" % (old, used, base))
        elif not issue:
            errors.append("%s: the file is a pre-existing test file of Apache Cassandra and %s, so no record on %s can permit the change"
                          % (old, no_issue, base))
        else:
            errors.append("%s: the file is a pre-existing test file of Apache Cassandra and no record on %s of #%s permits the change"
                          % (old, base, issue))
    if errors:
        errors.append(FOUR_WAYS)
    return errors, passed, len(touched)


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


OLD_RECORD = re.compile(r"^docs/decisions/([0-9]{4})-[^/]+\.md$")
SLUG = r"[a-z0-9]+(?:-[a-z0-9]+)*"
GOV_RECORD = re.compile(r"^docs/decisions/(DEC-(GOV)-([0-9]{4,}))-" + SLUG + r"\.md$")
FEATURE_RECORD = re.compile(r"^docs/design/((?:([A-Z]{3,5})|([0-9]+))-" + SLUG + r")/decisions/(DEC-([A-Z]{3,5}|[0-9]+)-([0-9]{4,}))-" + SLUG + r"\.md$")
RECORD_FORM = ("a decision record is DEC-<KEY>-nnnn-<slug>.md, four digits or more and a slug of lower case words joined by single hyphens: "
               "docs/design/<KEY>-<slug>/decisions/ for a decision of one feature, with the key of its directory (the issue number where the directory has no key), "
               "or docs/decisions/DEC-GOV-nnnn-<slug>.md for a decision of the whole project (docs/decisions/README.md, rule 1)")


def record_id(path):
    """(id, key, number) of a decision record named in the form of rule 1,
    None for any other path. The key is the feature key, GOV, or the issue
    number of a design directory that has no key."""
    match = GOV_RECORD.match(path)
    if match:
        return match.group(1), match.group(2), int(match.group(3))
    match = FEATURE_RECORD.match(path)
    if match and match.group(5) == (match.group(2) or match.group(3)) and match.group(5) != GOV_KEY:
        return match.group(4), match.group(5), int(match.group(6))
    return None


def records_at(repo, where):
    """The decision record paths at where, "index", "worktree" or a
    commit: every file of docs/decisions/ but its README, and every file
    of a decisions/ directory of a design directory."""
    places = ("docs/decisions/", "docs/design/")
    if where == "index":
        listing = git(repo, "ls-files", "--", *places)
    elif where == "worktree":
        listing = git(repo, "ls-files", "--cached", "--others", "--exclude-standard", "--", *places)
    else:
        listing = git(repo, "ls-tree", "-r", "--name-only", where, "--", *places)
    return [line for line in (listing or "").split("\n") if doc_type(line, "") == "decision"]


def record_rules(repo, templates, where, rules):
    """The decision records merged at the rules ref, the highest number
    merged under each key, and the numbers the new records of each key may
    take: the next ones after the highest merged, one each, in order
    (docs/decisions/README.md, rule 1)."""
    if "records" not in rules:
        merged = set(records_at(repo, templates))
        last = {}
        for path in merged:
            found = record_id(path)
            if found:
                last[found[1]] = max(last.get(found[1], 0), found[2])
        count = {}
        here = records_at(repo, where)
        for path in here:
            found = record_id(path)
            if found and path not in merged:
                count[found[1]] = count.get(found[1], 0) + 1
        allowed = {key: set(range(last.get(key, 0) + 1, last.get(key, 0) + 1 + n)) for key, n in count.items()}
        ids = {}
        for path in here:
            found = record_id(path)
            if found:
                ids.setdefault(found[0], []).append(path)
        rules["records"] = (merged, last, allowed, ids)
    return rules["records"]


def needs_index(kind, path, repo, templates, where, rules):
    """True when the document is asked for its index: every templated
    kind, and a decision record only when it is new, absent at the rules
    ref. A merged record is never edited (docs/decisions/README.md, rule
    2), so one merged before its template had the section keeps none."""
    if kind != "decision":
        return True
    return path not in record_rules(repo, templates, where, rules)[0]


def check_record(doc, path, repo, templates, where, rules):
    """A new decision record is named in the form of rule 1 and lives where
    its key puts it, its title opens with its id, its id is no other
    record's, and its number is the next after the highest merged under its
    key, so it neither reuses a merged number nor leaves a gap. A record
    merged at the rules ref is never edited (rule 2) and is not held to
    this: the records numbered NNNN in docs/decisions/ were merged before
    the ids."""
    merged, last, allowed, ids = record_rules(repo, templates, where, rules)
    if path in merged:
        return
    found = record_id(path)
    if not found:
        if OLD_RECORD.match(path):
            doc.error(0, "a new decision record takes an id, not a number alone: " + RECORD_FORM)
        else:
            doc.error(0, RECORD_FORM)
        return
    name, key, number = found
    title = doc.headings[0][1] if doc.headings and doc.headings[0][0] == 1 else ""
    if not title.startswith(name + ". "):
        doc.error(doc.headings[0][2] if doc.headings else 0, "the title of this record opens with its id: '# %s. <Short title of the decision>'" % name)
    others = [other for other in ids.get(name, []) if other != path]
    if others:
        doc.error(0, "the id %s is also the id of %s. Each decision record has an id of its own (docs/decisions/README.md, rule 1)" % (name, ", ".join(sorted(others))))
    numbers = allowed.get(key, set())
    if number not in numbers:
        first = last.get(key, 0) + 1
        span = "%s-%s-%04d" % ("DEC", key, first) if len(numbers) <= 1 else "DEC-%s-%04d to DEC-%s-%04d" % (key, first, key, first + len(numbers) - 1)
        before = "the highest merged one, DEC-%s-%04d" % (key, last[key]) if key in last else "none merged under the key %s yet" % key
        doc.error(0, "a new decision record takes the next number of its key, in order with no gap: after %s, %s here, and this one is %s (docs/decisions/README.md, rule 1)" % (before, span, name))


AREAS_PAGE = "docs/process/areas.md"
AREA_NAME = re.compile(r"^`([a-z][a-z0-9]*(?:-[a-z0-9]+)*)`$")
# The rows a template gained after documents were merged from it. A
# document merged without one keeps none until it is at another version
# than on the line, a decision record, which has no version, for good.
LATE_ROWS = ("Areas", "Supersedes", "Source", "Exceptions")


def names_at(repo, ref, section, rules=None):
    """The names of one closed list of docs/process/areas.md at ref, in the
    page's order: the names in backticks in the first column of the table
    of the section. None when the page or the table is not there."""
    if rules is not None and ("names", section) in rules:
        return rules[("names", section)]
    found = None
    text = git(repo, "show", "%s:%s" % (ref, AREAS_PAGE))
    if text is not None:
        doc = Markdown(AREAS_PAGE, text)
        span = plain_section_span(doc, section)
        if span is not None:
            names = [AREA_NAME.match(cells[0]) for _, cells in first_table(doc, span[0], span[1]) if cells]
            found = [match.group(1) for match in names if match] or None
    if rules is not None:
        rules[("names", section)] = found
    return found


def areas_at(repo, ref, rules=None):
    return names_at(repo, ref, "The areas", rules)


def late_rows(doc, path, kind, repo, templates):
    """The rows of LATE_ROWS this document may lack: the ones it lacked
    when it was merged at the rules ref, while it is the version it was
    merged at. A decision record is never edited (README rule 2), so it
    keeps the rows it was merged with."""
    merged = git(repo, "show", "%s:%s" % (templates, path))
    if merged is None:
        return ()
    old_fields, _ = control_table(Markdown(path, merged))
    fields, _ = control_table(doc)
    if not old_fields or not fields:
        return ()
    if kind != "decision" and old_fields.get("Version", ("",))[0] != fields.get("Version", ("",))[0]:
        return ()
    return tuple(row for row in LATE_ROWS if row not in old_fields and row not in fields)


def areas_of(value):
    return [word.strip().strip("`") for word in value.split(",") if word.strip()]


def check_areas(doc, repo, templates, rules):
    """The Areas row names one area or more of docs/process/areas.md on the
    line, joined by commas, and nothing else."""
    fields, _ = control_table(doc)
    if not fields or "Areas" not in fields:
        return
    value, line = fields["Areas"]
    if not value or outer_braces(value) or re.search(r"<[^>]+>", value):
        return
    known = areas_at(repo, templates, rules)
    if known is None:
        doc.error(line, "no list of areas at %s on %s, so the Areas row cannot be checked" % (AREAS_PAGE, templates))
        return
    named = areas_of(value)
    for name in named:
        if name not in known:
            doc.error(line, "'%s' is not an area. The Areas row names one or more of %s, joined by commas (%s). A new area is a change to that page" % (name, ", ".join(known), AREAS_PAGE))
    if len(set(named)) != len(named):
        doc.error(line, "the Areas row names an area twice")


def check_source(doc, repo, templates, rules):
    """The Source row names one source of the list on the areas page: how
    the change came into the line."""
    fields, _ = control_table(doc)
    if not fields or "Source" not in fields:
        return
    value, line = fields["Source"]
    if not value or outer_braces(value):
        return
    known = names_at(repo, templates, "The sources", rules)
    if known is None:
        doc.error(line, "no list of sources at %s on %s, so the Source row cannot be checked" % (AREAS_PAGE, templates))
    elif value.strip("`") not in known:
        doc.error(line, "'%s' is not a source. The Source row names one of %s (%s)" % (value, ", ".join(known), AREAS_PAGE))


PRINCIPLES_PAGE = "docs/process/principles.md"
PRINCIPLE_ID = re.compile(r"^PRINCIPLE-[0-9]{3}$")
NO_EXCEPTION = "None"


def principles_at(repo, ref, rules=None):
    """The ids of the principles page at ref: each heading that is an id
    PRINCIPLE-nnn. None when the page is not there or holds no principle."""
    if rules is not None and "principles" in rules:
        return rules["principles"]
    found = None
    text = git(repo, "show", "%s:%s" % (ref, PRINCIPLES_PAGE))
    if text is not None:
        found = [title for _, title, _ in Markdown(PRINCIPLES_PAGE, text).headings if PRINCIPLE_ID.match(title)] or None
    if rules is not None:
        rules["principles"] = found
    return found


def exceptions_of(value):
    """The words an Exceptions row names, a link read as its text. None
    names nothing."""
    plain = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", value).strip()
    if plain == NO_EXCEPTION:
        return []
    return [word.strip().strip("`") for word in plain.split(",") if word.strip()]


def check_exceptions(doc, repo, templates, rules):
    """The Exceptions row marks a record that departs from a principle
    (docs/process/principles.md, How to read and cite a principle): it
    says None, or names each principle the record departs from by its id,
    joined by commas, each one a principle of the page on the line."""
    fields, _ = control_table(doc)
    if not fields or "Exceptions" not in fields:
        return
    value, line = fields["Exceptions"]
    if not value or outer_braces(value):
        return
    named = exceptions_of(value)
    if not named:
        if value.strip() != NO_EXCEPTION:
            doc.error(line, "the Exceptions row names each principle this record departs from by its id, such as PRINCIPLE-016, joined by commas, or says None")
        return
    known = principles_at(repo, templates, rules)
    if known is None:
        doc.error(line, "no principles at %s on %s, so the Exceptions row cannot be checked" % (PRINCIPLES_PAGE, templates))
    for name in named:
        if not PRINCIPLE_ID.match(name):
            doc.error(line, "'%s' is not the id of a principle. The Exceptions row names each principle this record departs from by its id, such as PRINCIPLE-016, joined by commas, or says None" % name)
        elif known is not None and name not in known:
            doc.error(line, "%s is not a principle of %s on %s. The Exceptions row names a principle the page states" % (name, PRINCIPLES_PAGE, templates))
    if len(set(named)) != len(named):
        doc.error(line, "the Exceptions row names a principle twice")


RECORD_REF = re.compile(r"(?<![0-9A-Za-z-])(" + DECISION_ID + r"|[0-9]{4})(?![0-9A-Za-z])")


def own_record_name(path):
    """The id a decision record is cited by: its id, or its number for a
    record merged before the ids."""
    found = record_id(path)
    if found:
        return found[0]
    match = OLD_RECORD.match(path)
    return match.group(1) if match else None


def check_supersedes(doc, path, source, repo, where):
    """Supersede links hold both ways (README rule 2): each record this
    one's Supersedes row names says "Superseded by" this one in its Status,
    and a record whose Status says "Superseded by" another is named in that
    one's Supersedes row. A record merged before the Supersedes row has
    none, and is not asked for it."""
    own = own_record_name(path)
    fields, _ = control_table(doc)
    if own is None or not fields:
        return
    by_name = {}
    for other in records_at(repo, where):
        name = own_record_name(other)
        if name:
            by_name.setdefault(name, other)

    def fields_of(name):
        other = by_name.get(name)
        text = source.read(other) if other else None
        if text is None:
            return other, None
        return other, control_table(Markdown(other, text))[0] or {}

    if "Supersedes" in fields:
        value, line = fields["Supersedes"]
        names = RECORD_REF.findall(re.sub(r"\\([^)]*\\)", "", value))
        if value != "None" and not names and not re.search(r"<[^>]+>", value):
            doc.error(line, "the Supersedes row names each record this one replaces by its id, such as DEC-VER-0003, or says None")
        for name in names:
            if name == own:
                doc.error(line, "a record does not supersede itself")
                continue
            other, theirs = fields_of(name)
            if theirs is None:
                doc.error(line, "this record supersedes %s, and there is no such record" % name)
            elif theirs.get("Status", ("",))[0] != "Superseded by %s" % own:
                doc.error(line, "this record supersedes %s, and the Status of %s is '%s'. It becomes 'Superseded by %s' in the same pull request (docs/decisions/README.md, rule 2)" % (name, other, theirs.get("Status", ("",))[0], own))
    status, line = fields.get("Status", ("", 0))
    match = re.match(r"^Superseded by (" + DECISION_ID + r"|[0-9]{4})$", status)
    if match:
        other, theirs = fields_of(match.group(1))
        if theirs is None:
            doc.error(line, "the Status names %s, and there is no such record" % match.group(1))
        elif "Supersedes" in theirs and own not in RECORD_REF.findall(re.sub(r"\\([^)]*\\)", "", theirs["Supersedes"][0])):
            doc.error(line, "the Status says this record is superseded by %s, and the Supersedes row of %s does not name %s (docs/decisions/README.md, rule 2)" % (match.group(1), other, own))


REVISION_HEAD = ["Version", "Date", "Change", "Decision record"]
REVISION_INTRO = "Revision history, one row for each version:"
OLD_HISTORY = "Change history: the git history of this file."
HISTORY_LABEL = "Full history in git: "
HISTORY_LINE = re.compile(r"^Full history in git: \[commits of this file\]\((\S+)\)$")
RECORD_CELL = re.compile(r"^(?:None|(?:\[?(?:" + DECISION_ID + r"|[0-9]{4})\]?(?:\([^)\s]+\))?)(?:(?:, | and )\[?(?:" + DECISION_ID + r"|[0-9]{4})\]?(?:\([^)\s]+\))?)*)$")
GITHUB_REMOTE = re.compile(r"github\.com[:/]([^/\s]+)/([^/\s]+?)(?:\.git)?/?\s*$")


def preamble(doc):
    """The line range between the title and the first section."""
    first = [h for h in doc.headings if h[0] == 1]
    start = first[0][2] + 1 if first else 0
    stop = len(doc.lines)
    for level, _, index in doc.headings:
        if index >= start and level >= 2:
            stop = index
            break
    return start, stop


def revision_rows(doc):
    """(header line, rows) of the revision history table of a document:
    the table of its preamble whose header is Version, Date, Change,
    Decision record. (None, []) when it has none."""
    start, stop = preamble(doc)
    for index in range(start, stop):
        if index in doc.fenced or index in doc.commented:
            continue
        line = doc.visible[index].strip()
        if line.startswith("|") and table_cells(line) == REVISION_HEAD:
            return index, first_table(doc, index, stop)
    return None, []


def history_url(repo, ref, path):
    """The address of the commits of path on its line on GitHub: the
    repository is the one the rules ref is fetched from, so the link
    follows a move or a rename of the repository, and the line is the
    branch the rules ref names. None when the clone has no GitHub remote
    to read it from."""
    remote, _, line = ref.partition("/")
    url = git(repo, "remote", "get-url", remote) if line else None
    if url is None:
        url = git(repo, "remote", "get-url", "origin")
        line = ref
    match = GITHUB_REMOTE.search(url or "")
    if not match or not re.match(r"^[A-Za-z0-9._-]+$", line):
        return None
    return "https://github.com/%s/%s/commits/%s/%s" % (match.group(1), match.group(2), line, path)


def history_line(doc):
    """(line index, address) of the history link of the preamble."""
    start, stop = preamble(doc)
    for index in range(start, stop):
        if index in doc.fenced or index in doc.commented:
            continue
        if doc.visible[index].startswith(HISTORY_LABEL):
            match = HISTORY_LINE.match(doc.visible[index].rstrip())
            return index, match.group(1) if match else ""
    return None, None


def held_to_revision(doc, path, repo, templates, template_text):
    """True when the document carries its revision history: its template
    on the line has the table, and the document is new, or already has the
    table on the line, or is at another version than on the line. A
    document merged before its template had the table keeps the old line
    until its next version, which adds the table with that version's
    row."""
    if revision_rows(Markdown("template", template_text))[0] is None:
        return False
    merged = git(repo, "show", "%s:%s" % (templates, path))
    if merged is None:
        return True
    old = Markdown(path, merged)
    if revision_rows(old)[0] is not None or revision_rows(doc)[0] is not None:
        return True
    old_fields, _ = control_table(old)
    fields, _ = control_table(doc)
    return bool(old_fields and fields and "Version" in old_fields and "Version" in fields and old_fields["Version"][0] != fields["Version"][0])


def check_revision_table(doc, path, repo, templates):
    """The revision history table and the history link of a document."""
    head, rows = revision_rows(doc)
    if head is None:
        doc.error(0, "no revision history table under the document control table: a table Version, Date, Change, Decision record with one row for each version, and under it the link to the commits of this file. doclint.py history --write puts both in")
        return
    fields, _ = control_table(doc)
    if not rows:
        doc.error(head, "the revision history has no row. Each version has one: its number, its date, what changed and the decision record behind it")
    previous = None
    for index, cells in rows:
        cells = cells + [""] * (4 - len(cells))
        version, date, change, record = cells[:4]
        if not re.match(r"^[1-9][0-9]*$", version):
            doc.error(index, "the Version of a revision history row is a whole number, 1 for the first version")
        else:
            if previous is not None and int(version) != previous + 1:
                doc.error(index, "the revision history rows are in order with no gap: version %d follows version %d" % (previous + 1, previous))
            previous = int(version)
        if not DATE.match(date):
            doc.error(index, "the Date of a revision history row is an RFC 3339 date, YYYY-MM-DD")
        if not change or outer_braces(change):
            doc.error(index, "the Change of a revision history row says what changed in that version")
        if not RECORD_CELL.match(record):
            doc.error(index, "the Decision record of a revision history row names the record behind the change by its id, such as DEC-VER-0003, several joined by commas, or says None")
    if previous is not None and fields and "Version" in fields:
        value, line = fields["Version"]
        if re.match(r"^[1-9][0-9]*$", value) and int(value) != previous:
            doc.error(line, "the Version row says %s and the last row of the revision history is version %d. A new version adds its row" % (value, previous))
    # A version that is merged keeps its row as it was merged.
    merged = git(repo, "show", "%s:%s" % (templates, path))
    if merged is not None:
        for index, cells in revision_rows(Markdown(path, merged))[1]:
            if cells not in [found for _, found in rows]:
                doc.error(head, "the revision history row of version %s on the line is changed or gone. A merged version keeps its row" % (cells[0] if cells else "?"))
    line, address = history_line(doc)
    wanted = history_url(repo, templates, path)
    if line is None:
        doc.error(head, "no link to the commits of this file under the revision history: '%s[commits of this file](%s)'. doclint.py history --write puts it in" % (HISTORY_LABEL, wanted or "https://github.com/<owner>/<repository>/commits/<line>/" + path))
    elif wanted is not None and address != wanted:
        doc.error(line, "the history link is not the commits of this file on its line: '%s[commits of this file](%s)'. doclint.py history --write puts it right" % (HISTORY_LABEL, wanted))
    elif wanted is None and not re.match(r"^https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/commits/[A-Za-z0-9._-]+/" + re.escape(path) + "$", address):
        doc.error(line, "the history link is not the commits of this file on GitHub: https://github.com/<owner>/<repository>/commits/<line>/%s" % path)


def check_revision(doc, path, repo, templates, template_text):
    if held_to_revision(doc, path, repo, templates, template_text):
        check_revision_table(doc, path, repo, templates)


def with_history(doc, path, repo, templates, today):
    """The lines of the document with its revision history as doclint
    writes it: the old change history line becomes the table with the row
    of the document's version, which the author fills in, and the history
    link is the one of this file on its line. None when the document has
    neither the old line nor the table to start from, False when the clone
    has no GitHub remote to build the link from."""
    lines = list(doc.lines)
    start, stop = preamble(doc)
    head, _ = revision_rows(doc)
    wanted = history_url(repo, templates, path)
    if wanted is None:
        return False
    link = "%s[commits of this file](%s)" % (HISTORY_LABEL, wanted)
    if head is None:
        old = [index for index in range(start, stop) if lines[index].strip() == OLD_HISTORY]
        if not old:
            return None
        fields, _ = control_table(doc)
        version = fields["Version"][0] if fields and "Version" in fields and re.match(r"^[1-9][0-9]*$", fields["Version"][0]) else "1"
        block = [REVISION_INTRO, "", "| " + " | ".join(REVISION_HEAD) + " |", "|---|---|---|---|",
                 "| %s | %s | {what changed in this version} | {the id of the decision record behind it, or None} |" % (version, today), "", link]
        return lines[:old[0]] + block + lines[old[0] + 1:]
    line, _ = history_line(doc)
    if line is not None:
        lines[line] = link
        return lines
    end = head
    while end + 1 < stop and lines[end + 1].strip().startswith("|"):
        end += 1
    return lines[:end + 1] + ["", link] + lines[end + 1:]


def run_history(args):
    repo, templates, mode, paths = None, None, None, []
    index = 0
    while index < len(args):
        word = args[index]
        if word in ("--repo", "--templates") and index + 1 < len(args):
            if word == "--repo":
                repo = args[index + 1]
            else:
                templates = args[index + 1]
            index += 2
            continue
        if word in ("--write", "--check") and mode is None:
            mode = word
        elif word.startswith("--"):
            sys.stderr.write(__doc__)
            return 2
        else:
            paths.append(word)
        index += 1
    if not repo or not templates or not paths:
        sys.stderr.write(__doc__)
        return 2
    failed = 0
    for path in paths:
        text = Source(repo, "worktree").read(path)
        if text is None:
            sys.stderr.write("%s:0: cannot be read\n" % path)
            failed += 1
            continue
        doc = Markdown(path, text)
        if mode == "--check":
            check_revision_table(doc, path, repo, templates)
            for error in doc.errors:
                sys.stderr.write(error + "\n")
            failed += 1 if doc.errors else 0
        elif mode == "--write":
            new = with_history(doc, path, repo, templates, time.strftime("%Y-%m-%d", time.gmtime()))
            if new is False:
                sys.stderr.write("%s:0: the clone has no GitHub remote for %s to build the link from, so nothing is written. Add the remote the line is fetched from\n" % (path, templates))
                failed += 1
            elif new is None:
                sys.stderr.write("%s:0: has neither a revision history table nor the line '%s' under its document control table, so there is nothing to write\n" % (path, OLD_HISTORY))
                failed += 1
            elif new != doc.lines:
                with open(os.path.join(repo, path), "w", encoding="utf-8") as handle:
                    handle.write("\n".join(new))
                print("history %s written" % path)
            else:
                print("history %s current" % path)
        else:
            print("%s[commits of this file](%s)" % (HISTORY_LABEL, history_url(repo, templates, path) or "https://github.com/<owner>/<repository>/commits/<line>/" + path))
    if mode == "--check":
        print("history %d checked %d failed" % (len(paths), failed))
    return 1 if failed else 0


INDEX_DIR = "docs/index"
INDEX_PAGES = {"documents": INDEX_DIR + "/documents.md", "decisions": INDEX_DIR + "/decisions.md", "areas": INDEX_DIR + "/areas.md"}
FEATURE_INDEX = "INDEX.md"
INDEX_LICENCE = """<!--
Copyright 2026 AxonOps Limited
SPDX-License-Identifier: Apache-2.0

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
-->
"""
INDEX_NOTE = "This page is generated by `tools/chronitondb/doclint.py indexes --write` from the document control table of each document. It is never edited by hand."
# The kind of a document is the word before the colon of its title, as its
# template writes it. These read better with their noun.
KIND_NAMES = {"Design": "Design record", "Fix": "Fix record", "Import": "Import record", "Release": "Release proposal", "Delta": "Delta entry"}
KIND_ORDER = ("Feature spec", "Plan", "Delivery plan", "Milestone report", "Design record", "Fix record", "Import record",
              "Research report", "Line plan", "Release proposal", "Delta entry", "Review record")
NO_AREA = "Documents with no Areas row"
EXCEPTIONS_SECTION = "Exceptions to principles"
JIRA_ID = re.compile(r"\bCASSANDRA-[0-9]+\b")
UPSTREAM = re.compile(r"`([0-9a-f]{7,40}|cassandra-[0-9][0-9A-Za-z.-]*)`|\b(cassandra-[0-9]+\.[0-9]+(?:\.[0-9]+)?(?:-[a-z0-9]+)?)\b")


def docs_at(repo, where):
    if where == "index":
        listing = git(repo, "ls-files", "--", "docs/")
    elif where == "worktree":
        listing = git(repo, "ls-files", "--cached", "--others", "--exclude-standard", "--", "docs/")
    else:
        listing = git(repo, "ls-tree", "-r", "--name-only", where, "--", "docs/")
    return sorted(line for line in (listing or "").split("\n") if line.endswith(".md"))


def cell(text):
    return re.sub(r"\s+", " ", text).replace("|", "\\|").strip()


def indexed_documents(repo, where):
    """Every document of docs/ at where that carries the common header: a
    document control table with a Document type row. A template, a generated
    index and a page with no such table are not documents. Each is a dict
    of its path, kind, title, status, version, areas and, by kind, what
    its header says more."""
    source = Source(repo, where)
    found = []
    for path in docs_at(repo, where):
        if path.startswith("docs/process/templates/") or path.startswith(INDEX_DIR + "/") or os.path.basename(path) == FEATURE_INDEX:
            continue
        text = source.read(path)
        if text is None:
            continue
        doc = Markdown(path, text)
        fields, _ = control_table(doc)
        if not fields or "Document type" not in fields:
            continue
        heading = first_heading(text)
        value = lambda name: fields[name][0] if name in fields else ""
        entry = {"path": path, "heading": heading, "status": value("Status"), "version": value("Version"),
                 "areas": areas_of(value("Areas")) if "Areas" in fields else None, "references": value("References"),
                 "title": value("Title") or heading,
                 "exceptions": [name for name in exceptions_of(value("Exceptions")) if PRINCIPLE_ID.match(name)]}
        if doc_type(path, text) == "decision":
            entry["kind"] = "Decision record"
            entry["id"] = own_record_name(path) or ""
            entry["title"] = re.sub(r"^\S+\.\s+", "", heading)
            entry["date"] = value("Date")
            entry["supersedes"] = value("Supersedes") if "Supersedes" in fields else ""
            entry["feature"] = path.split("/")[2] if path.startswith("docs/design/") else ""
        else:
            word = heading.split(":")[0].strip() if ":" in heading else ""
            entry["kind"] = KIND_NAMES.get(word, word) or "Other document"
            entry["title"] = heading.split(":", 1)[1].strip() if ":" in heading else heading
        if entry["kind"] == "Import record":
            both = heading + " " + entry["references"]
            line = re.search(r" into (\S+)\s*$", heading)
            entry["line"] = line.group(1) if line else ""
            entry["source"] = value("Source")
            entry["jira"] = sorted(set(JIRA_ID.findall(both)), key=lambda name: int(name.split("-")[1]))
            entry["upstream"] = []
            for match in UPSTREAM.finditer(both):
                name = match.group(1) or match.group(2)
                if name not in entry["upstream"]:
                    entry["upstream"].append(name)
        found.append(entry)
    return found


def link(entry, page, text=None):
    return "[%s](%s)" % (cell(text or entry["title"]), os.path.relpath(entry["path"], os.path.dirname(page)).replace(os.sep, "/"))


def kind_key(kind):
    return (KIND_ORDER.index(kind) if kind in KIND_ORDER else len(KIND_ORDER), kind)


def record_key(entry):
    found = record_id(entry["path"])
    return (0, "", int(entry["id"])) if not found else (1, found[1], found[2])


def table(head, rows):
    return ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)] + ["| " + " | ".join(row) + " |" for row in rows]


def areas_cell(entry):
    return ", ".join("`%s`" % name for name in entry["areas"]) if entry["areas"] else ""


def index_pages(repo, where, rules_ref):
    """The generated indexes of the tree at where, as a path to text map:
    every document by kind, every decision record, every document by area,
    and the documents of each feature in its own directory. The areas and
    their order come from the areas page at rules_ref, the line."""
    entries = indexed_documents(repo, where)
    records = sorted((entry for entry in entries if entry["kind"] == "Decision record"), key=record_key)
    others = [entry for entry in entries if entry["kind"] != "Decision record"]
    pages = {}

    def page(path, title, body):
        pages[path] = "\n".join([INDEX_LICENCE, "# " + title, "", INDEX_NOTE, ""] + body).rstrip("\n") + "\n"

    # Every document, by kind.
    here = INDEX_PAGES["documents"]
    body = ["Every document under `docs/` that carries the common header, by kind. The decision records are in [decisions.md](decisions.md), and the same documents by area in [areas.md](areas.md).", ""]
    for kind in sorted({entry["kind"] for entry in others}, key=kind_key):
        body += ["## %s" % kind, ""]
        rows = sorted((entry for entry in others if entry["kind"] == kind), key=lambda entry: entry["path"])
        if kind == "Import record":
            body += table(["Import", "Line", "Source", "Apache JIRA", "Release or commit", "Status", "Version", "Areas"],
                          [[link(entry, here), cell(entry["line"]), cell(entry["source"]), ", ".join(entry["jira"]), ", ".join("`%s`" % name for name in entry["upstream"]),
                            cell(entry["status"]), cell(entry["version"]), areas_cell(entry)] for entry in rows])
        else:
            body += table(["Document", "Status", "Version", "Areas"],
                          [[link(entry, here), cell(entry["status"]), cell(entry["version"]), areas_cell(entry)] for entry in rows])
        body += [""]
    # The records that carry an exception to a principle, by principle. The
    # section is written once a record names one.
    marked = sorted(((name, entry) for entry in others for name in sorted(set(entry["exceptions"]))), key=lambda pair: (pair[0], pair[1]["path"]))
    if marked:
        principles = os.path.relpath(PRINCIPLES_PAGE, os.path.dirname(here)).replace(os.sep, "/")
        body += ["## %s" % EXCEPTIONS_SECTION, "",
                 "Every record whose `Exceptions` row names a principle of [principles.md](%s), under each principle it departs from. The record gives the reason." % principles, ""]
        body += table(["Principle", "Record", "Kind", "Status", "Version"],
                      [["[%s](%s#%s)" % (name, principles, name.lower()), link(entry, here), entry["kind"], cell(entry["status"]), cell(entry["version"])] for name, entry in marked])
        body += [""]
    page(here, "Documents", body)

    # Every decision record.
    here = INDEX_PAGES["decisions"]
    body = ["Every decision record of the project and of its features, by key and number. The records named by a number alone were merged before records had ids.", ""]
    body += table(["Id", "Decision", "Feature", "Status", "Date", "Areas", "Supersedes"],
                  [[link(entry, here, entry["id"]), cell(entry["title"]), "`%s`" % entry["feature"] if entry["feature"] else "", cell(entry["status"]),
                    cell(entry["date"]), areas_cell(entry), cell(entry["supersedes"])] for entry in records])
    page(here, "Decision records", body)

    # Every document, by area.
    here = INDEX_PAGES["areas"]
    names = areas_at(repo, rules_ref) or []
    extra = sorted({name for entry in entries for name in (entry["areas"] or []) if name not in names})
    body = ["Every document and decision record under each of [the areas](../process/areas.md) its `Areas` row names. A document that names several areas is listed under each.", ""]
    for name in names + extra + [None]:
        rows = [entry for entry in entries if (name in (entry["areas"] or []) if name else not entry["areas"])]
        rows.sort(key=lambda entry: (kind_key(entry["kind"]), record_key(entry) if entry["kind"] == "Decision record" else (), entry["path"]))
        body += ["## %s" % ("`%s`" % name if name else NO_AREA), ""]
        if not name:
            body += ["Documents of a kind that has no `Areas` row, and documents merged before the row.", ""]
        if rows:
            body += table(["Document", "Kind", "Status", "Version"],
                          [[link(entry, here, "%s. %s" % (entry["id"], entry["title"]) if entry["kind"] == "Decision record" else None),
                            entry["kind"], cell(entry["status"]), cell(entry.get("version", ""))] for entry in rows])
        else:
            body += ["None."]
        body += [""]
    page(here, "Documents by area", body)

    # The documents of each feature, in its directory.
    source = Source(repo, where)
    owners = {}
    for entry in others:
        if entry["kind"] in ("Design record", "Fix record"):
            text = source.read(entry["path"]) or ""
            for rid, _ in requirement_definitions(Markdown(entry["path"], text), r"REQ-[A-Z]{3,5}-[0-9]{3}"):
                owners.setdefault(rid.split("-")[1], set()).add(entry["path"])
    features = sorted({path.split("/")[2] for path in docs_at(repo, where) if path.startswith("docs/design/") and path.count("/") >= 3})
    for name in features:
        match = DIR_FORM.match(name)
        if not match or not match.group(1):
            continue
        key = match.group(1)
        here = "docs/design/%s/%s" % (name, FEATURE_INDEX)
        own = [entry for entry in others if entry["path"].startswith("docs/design/%s/" % name) or entry["path"] in owners.get(key, ())]
        own.sort(key=lambda entry: (kind_key(entry["kind"]), entry["path"]))
        body = ["The documents of the feature `%s`: those of this directory, and the design records of its items, which define its `REQ-%s-nnn` requirements." % (key, key), ""]
        body += table(["Document", "Kind", "Status", "Version", "Areas"],
                      [[link(entry, here), entry["kind"], cell(entry["status"]), cell(entry["version"]), areas_cell(entry)] for entry in own]) if own else ["None."]
        body += ["", "## Decision records", ""]
        mine = [entry for entry in records if entry["feature"] == name]
        body += table(["Id", "Decision", "Status", "Date", "Areas", "Supersedes"],
                      [[link(entry, here, entry["id"]), cell(entry["title"]), cell(entry["status"]), cell(entry["date"]), areas_cell(entry), cell(entry["supersedes"])]
                       for entry in mine]) if mine else ["None."]
        page(here, "%s: documents of this feature" % key, body)
    return pages


def run_indexes(args):
    repo, rules_ref, where, write = None, None, "index", False
    index = 0
    while index < len(args):
        word = args[index]
        if word in ("--repo", "--templates", "--source") and index + 1 < len(args):
            if word == "--repo":
                repo = args[index + 1]
            elif word == "--templates":
                rules_ref = args[index + 1]
            else:
                where = args[index + 1]
            index += 2
            continue
        if word == "--write":
            write = True
            index += 1
            continue
        sys.stderr.write(__doc__)
        return 2
    if not repo or not rules_ref:
        sys.stderr.write(__doc__)
        return 2
    if write:
        where = "worktree"
    pages = index_pages(repo, where, rules_ref)
    source = Source(repo, where)
    stale = [path for path in sorted(pages) if source.read(path) != pages[path]]
    gone = [path for path in docs_at(repo, where)
            if (path.startswith(INDEX_DIR + "/") or (path.startswith("docs/design/") and os.path.basename(path) == FEATURE_INDEX)) and path not in pages]
    if write:
        for path in stale:
            full = os.path.join(repo, path)
            os.makedirs(os.path.dirname(full), exist_ok=True)
            with open(full, "w", encoding="utf-8") as handle:
                handle.write(pages[path])
            print("index %s written" % path)
        for path in gone:
            os.remove(os.path.join(repo, path))
            print("index %s removed" % path)
        print("indexes %d pages %d written" % (len(pages), len(stale)))
        return 0
    for path in stale:
        sys.stderr.write("%s:0: is not the index the documents give now. doclint.py indexes --write regenerates it, then commit it with the change\n" % path)
    for path in gone:
        sys.stderr.write("%s:0: is an index of nothing: no feature directory or index page of this name is generated. doclint.py indexes --write removes it\n" % path)
    print("indexes %d pages %d stale" % (len(pages), len(stale) + len(gone)))
    return 1 if stale or gone else 0


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
        if match.group(1) == GOV_KEY:
            errors.append("docs/design/%s:0: the key GOV is kept for the decision records of the whole project, docs/decisions/DEC-GOV-nnnn-<slug>.md. A feature takes another key" % name)
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


def run_delta(args, stock_tests=False, issue_only=False):
    repo, base, where, branch, body, issue = None, None, "index", None, None, None
    index = 0
    while index < len(args):
        if args[index] in ("--repo", "--base", "--source", "--branch", "--body") + (("--issue",) if stock_tests else ()) and index + 1 < len(args):
            value = args[index + 1]
            if args[index] == "--repo":
                repo = value
            elif args[index] == "--base":
                base = value
            elif args[index] == "--source":
                where = value
            elif args[index] == "--branch":
                branch = value
            elif args[index] == "--issue":
                issue = value
            else:
                body = value
            index += 2
            continue
        sys.stderr.write(__doc__)
        return 2
    if not issue_only and (not repo or not base):
        sys.stderr.write(__doc__)
        return 2
    text = None
    if body:
        try:
            with open(body, encoding="utf-8") as handle:
                text = handle.read()
        except (OSError, UnicodeDecodeError):
            sys.stderr.write("the pull request description %s cannot be read\n" % body)
            return 2
    if issue_only:
        # The issue whose state the caller reads before the check.
        print(own_issue(branch, text)[0] or "")
        return 0
    if stock_tests:
        state = None
        if issue:
            # An answer that cannot be read is the state of no issue.
            state = {}
            try:
                with open(issue, encoding="utf-8") as handle:
                    state = json.load(handle)
            except (OSError, ValueError):
                pass
        errors, passed, checked = check_stock_tests(repo, base, where, branch, text, state)
        for path, way in passed:
            print("stock-test %s: %s" % (path, way))
        for error in errors:
            sys.stderr.write(error + "\n")
        print("stock-tests %d checked %d failed" % (checked, checked - len(passed) if checked else len(errors)))
        return 1 if errors else 0
    errors, stock, entries, note = check_register(repo, base, where, branch, text)
    for path in stock:
        print("stock %s" % path)
    if note:
        print(note)
    for error in errors:
        sys.stderr.write(error + "\n")
    print("delta %d stock files %d entries %s" % (len(stock), entries, "failed" if errors else "passed"))
    return 1 if errors else 0


def main(argv):
    if argv and argv[0] == "index":
        return run_index(argv[1:])
    if argv and argv[0] == "delta":
        return run_delta(argv[1:])
    if argv and argv[0] == "stock-tests":
        return run_delta(argv[1:], stock_tests=True)
    if argv and argv[0] == "stock-tests-issue":
        return run_delta(argv[1:], issue_only=True)
    if argv and argv[0] == "history":
        return run_history(argv[1:])
    if argv and argv[0] == "indexes":
        return run_indexes(argv[1:])
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
        if template_text is None and kind in LATE_TEMPLATES:
            checked -= 1
            continue
        if template_text is None:
            doc.error(0, "no %s template at %s on %s, so this document cannot be checked against it" % (kind.replace("-", " "), template_path, templates))
        else:
            check_common(doc, kind, template_text, path, late_rows(doc, path, kind, repo, templates))
            check_areas(doc, repo, templates, rules)
            check_source(doc, repo, templates, rules)
            check_exceptions(doc, repo, templates, rules)
            if has_contents(Markdown(template_path, template_text)) and needs_index(kind, path, repo, templates, where, rules):
                check_index(doc, path)
            if kind == "decision":
                check_record(doc, path, repo, templates, where, rules)
                check_supersedes(doc, path, source, repo, where)
            check_revision(doc, path, repo, templates, template_text)
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
            elif kind == "research-report":
                check_research(doc, path)
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
