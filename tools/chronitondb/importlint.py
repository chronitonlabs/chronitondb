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
"""Checks the history of an import against docs/process/upstream.md, The
import history check: an import branch brings Apache Cassandra's own
history, or one commit taken unchanged, and nothing else of Apache
Cassandra's files. The CI workflow chronitondb-import.yml runs it on every
pull request from an import/ branch of this repository.

    importlint.py history --repo DIR --base REF --head REV --branch NAME [--body FILE] [--reviews FILE] [--github URL]

REF is the line, origin/<line>. REV is the head commit of the pull
request, never the merge commit CI builds of it. NAME is the head branch,
which gives the form of the import and what it brings:

    import/cassandra-<x.y.z>/<line>                 Apache's tag cassandra-<x.y.z>
    import/cassandra-<x.y>-<short hash>/<line>      the commit of Apache's branch
                                                    cassandra-<x.y> whose hash
                                                    opens with <short hash>
    import/CASSANDRA-<n>/<line>                     one commit of an Apache branch
    import/<owner>-<repo>-<12 character hash>/<line> one commit of a branch of
                                                    another project

NAME is taken as given, so the caller gives it only for a branch whose name
it can trust: CI runs the check only for a branch of the repository itself.

Apache Cassandra's tags and branches are read from the public repository
apache/cassandra, fetched by its address when the check runs, into refs of
the check's own under refs/import-check/. A tag or a branch the clone
already has is no proof, since anyone who can push to this repository can
create one. URL is the site the address starts with, https://github.com/
when not given. The unit tests give a directory.

The commits the branch adds to the line are those of REV that REF does not
have. They are held to:

  1. a release or a branch import has one merge commit on the branch's own
     line of commits, its first parent line from REV, and the second
     parent of that merge is the commit NAME gives: the commit of the
     tag, or a commit of the branch whose hash opens with the short hash
  2. every other commit of the branch's own line of commits is a merge of
     the line into the branch, or a commit of the project's own that
     changes none of Apache Cassandra's files, such as the import record.
     The project's own files are those of the table Where things live in
     docs/process/conventions.md at REF. What a merge brings beside that
     line is the line itself or the Apache history of point 1, nothing
     else
  3. a single fix has one commit that changes Apache Cassandra's files.
     Its message ends with the line "(cherry picked from commit <full
     hash>)", the hash is a commit of a branch of apache/cassandra whose
     message names the ticket of NAME, and the commit keeps the author,
     the author date and the message of that commit
  4. a commit of another project is held as a single fix is, against the
     repository the line "Origin: https://github.com/<owner>/<repo>/
     commit/<full hash>" of FILE, the pull request's description, names.
     NAME is that owner, repository and the first 12 characters of the
     hash. The repository is not apache/cassandra, whose commits come
     as a single fix. Its commit is the one git makes of the original
     commit, with no way round: a commit of another project comes in unchanged or
     not at all. Whether the maintainers approved the repository as a
     source is not something the check can read
  5. no merge commit has more than two parents

A conflict resolved by hand is what the check can see of a merge or of a
cherry-pick that git did not make alone. For a merge commit: its tree is
not the tree git gives when it merges the two parents again, with no
conflict. For the commit of a single fix: its tree is not the tree git
gives when it picks the original commit onto the same parent again, with
no conflict. So a line that sits in another place than git puts it, or
has other whitespace, is seen. The check prints "RESOLVED PATH" on
stdout for each file that differs, for the import's assessment, and
refuses the import until a maintainer has approved it: FILE of --reviews
holds the reviews of the pull request as the GitHub API gives them, one
list or the lists of its pages one after another, and
one whose state is APPROVED, by a maintainer of the table Maintainers in
docs/governance/committers.md at REF, at a commit of the branch that
holds the resolved commit, approves it. The latest review of each
maintainer counts.

It prints "import-history passed" with what the import brings, or
"import-history failed", on stdout. Findings go to stderr, one per line,
exit 1 when there is one. A usage error exits 2.
"""

import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from doclint import CONVENTIONS, is_own, own_paths, plain_section_span  # noqa: E402
from markdown import Markdown, first_table  # noqa: E402

GITHUB = "https://github.com/"
APACHE = "apache/cassandra"
COMMITTERS = "docs/governance/committers.md"
REFS = "refs/import-check/"
BRANCH_IMPORT = re.compile(r"^import/cassandra-([0-9]+\.[0-9]+)-([0-9a-f]{7,40})/[^/]+$")
RELEASE_IMPORT = re.compile(r"^import/(cassandra-[0-9]+\.[0-9]+(?:\.[0-9]+)?(?:-[a-z]+[0-9]+)?)/[^/]+$")
FIX_IMPORT = re.compile(r"^import/CASSANDRA-([1-9][0-9]*)/[^/]+$")
OTHER_IMPORT = re.compile(r"^import/([A-Za-z0-9][A-Za-z0-9._-]*)-([0-9a-f]{12})/[^/]+$")
PICKED = re.compile(r"^\(cherry picked from commit ([0-9a-f]{40})\)$")
ORIGIN = re.compile(r"^Origin: https://github\.com/([A-Za-z0-9][A-Za-z0-9-]*)/([A-Za-z0-9._-]+)/commit/([0-9a-f]{40})$")
USERNAME = re.compile(r"^`([A-Za-z0-9][A-Za-z0-9-]*)`$")
SHOWN = 10
LISTED = 200
FORMS = ("import/cassandra-<x.y.z>/<line>, import/cassandra-<x.y>-<short hash>/<line>, import/CASSANDRA-<n>/<line> "
         "or import/<owner>-<repo>-<12 character hash>/<line>")


def git(repo, *args, data=None):
    """(exit code, output) of a git command, the output as text when it is
    UTF-8 and as bytes when it is not."""
    env = dict(os.environ, GIT_TERMINAL_PROMPT="0")
    try:
        done = subprocess.run(["git", "-C", repo] + list(args), capture_output=True, check=False, input=data, env=env)
    except OSError:
        return 127, ""
    try:
        return done.returncode, done.stdout.decode("utf-8")
    except UnicodeDecodeError:
        return done.returncode, done.stdout


def read(repo, *args):
    rc, out = git(repo, *args)
    return out.strip() if rc == 0 and isinstance(out, str) else None


def commit_of(repo, name):
    return read(repo, "rev-parse", "--verify", "--quiet", "%s^{commit}" % name)


def is_ancestor(repo, old, new):
    return git(repo, "merge-base", "--is-ancestor", old, new)[0] == 0


def fetch(repo, address, *refspecs):
    """Fetches refs of a public repository into the check's own refs.
    Nothing the clone already has under them is kept."""
    old = read(repo, "for-each-ref", "--format=%(refname)", REFS) or ""
    for name in old.split("\n"):
        if name:
            git(repo, "update-ref", "-d", name)
    return git(repo, "fetch", "--quiet", "--no-tags", "--force", address, *refspecs)[0] == 0


def maintainers_at(repo, base):
    """The GitHub usernames of the table Maintainers in the public record
    at REF, in lower case."""
    rc, text = git(repo, "show", "%s:%s" % (base, COMMITTERS))
    if rc != 0 or not isinstance(text, str):
        return []
    doc = Markdown(COMMITTERS, text)
    span = plain_section_span(doc, "Maintainers")
    if span is None:
        return []
    found = []
    for _, cells in first_table(doc, span[0], span[1]):
        for cell in cells:
            match = USERNAME.match(cell)
            if match:
                found.append(match.group(1).lower())
    return found


def approving_commits(reviews, maintainers):
    """The commits at which a maintainer's latest review approves the
    pull request."""
    latest = {}
    for review in reviews if isinstance(reviews, list) else []:
        if not isinstance(review, dict) or not isinstance(review.get("user"), dict):
            continue
        login = str(review["user"].get("login") or "").lower()
        state = str(review.get("state") or "")
        # A comment made as a review changes no earlier verdict.
        if login in maintainers and state in ("APPROVED", "CHANGES_REQUESTED", "DISMISSED"):
            latest[login] = (state, str(review.get("commit_id") or ""))
    return [commit for state, commit in latest.values() if state == "APPROVED" and re.match(r"^[0-9a-f]{40}$", commit)]


class History:
    """The commits an import branch adds to its line, and the findings on
    them."""

    def __init__(self, repo, base, head, reviews):
        self.repo = repo
        self.base = base
        self.head = head
        self.errors = []
        self.notes = []
        self.resolved = []
        rc, conventions = git(repo, "show", "%s:%s" % (base, CONVENTIONS))
        self.own = own_paths(conventions) if rc == 0 and isinstance(conventions, str) else []
        self.approved = approving_commits(reviews, maintainers_at(repo, base))
        self.added = (read(repo, "rev-list", head, "^" + base) or "").split()
        # The branch's own line of commits, newest first: the first parents
        # from REV down to the first commit the line already has.
        self.spine = (read(repo, "rev-list", "--first-parent", head, "^" + base) or "").split()

    def error(self, text):
        self.errors.append(text)

    def parents(self, commit):
        return (read(self.repo, "rev-list", "--parents", "-n", "1", commit) or "").split()[1:]

    def subject(self, commit):
        return "%s %s" % (commit[:10], read(self.repo, "log", "-1", "--no-show-signature", "--format=%s", commit) or "")

    def stock_files(self, commit):
        """Apache Cassandra's files a commit changes against its first
        parent, None when the change cannot be read."""
        rc, out = git(self.repo, "diff", "--name-only", "-z", "--no-renames", commit + "^1", commit)
        if rc != 0 or not isinstance(out, str):
            return None
        return [path for path in out.split("\0") if path and not is_own(path, self.own)]

    def is_approved(self, commit):
        return any(commit_of(self.repo, at) and is_ancestor(self.repo, commit, at) and is_ancestor(self.repo, at, self.head)
                   for at in self.approved)

    def by_hand(self, commit, what, files):
        """A commit git did not make alone: reported, and refused until a
        maintainer has approved it."""
        self.resolved += files[:LISTED]
        if len(files) > LISTED:
            self.resolved.append("and %d more files of %s" % (len(files) - LISTED, commit[:10]))
        if self.is_approved(commit):
            self.notes.append("%s: %s, and a maintainer approved it" % (self.subject(commit), what))
            return
        self.error("%s: %s, in %d file(s), listed above on the RESOLVED lines. The check cannot tell a conflict resolved by hand from "
                   "another change, so a maintainer decides (docs/process/principles.md, PRINCIPLE-074). List each file in the import "
                   "record with how it was resolved. A maintainer approves with an approving review of this pull request, and the "
                   "check passes when it is run again" % (self.subject(commit), what, len(files)))

    def check_merge(self, commit, parents):
        """A merge commit is what git gives when it merges the two parents
        again, or it is a conflict resolved by hand."""
        rc, out = git(self.repo, "merge-tree", "--write-tree", "--no-messages", parents[0], parents[1])
        tree = out.split("\n", 1)[0].strip() if isinstance(out, str) else ""
        if rc not in (0, 1) or not re.match(r"^[0-9a-f]{40,64}$", tree):
            self.error("%s: the merge cannot be made again here, so it cannot be checked. The check needs git 2.38 or later" % self.subject(commit))
            return
        if rc == 0 and tree == read(self.repo, "rev-parse", commit + "^{tree}"):
            return
        _, names = git(self.repo, "diff", "--name-only", "-z", "--no-renames", tree, commit)
        files = [path for path in names.split("\0") if path] if isinstance(names, str) else []
        self.by_hand(commit, "the merge commit is not the merge git makes of its two parents", files or ["(the tree)"])

    def check_spine(self, is_import_merge):
        """Each commit of the branch's own line: a merge the form allows,
        a merge of the line, or a commit that changes none of Apache
        Cassandra's files. Returns the import merges and the commits that
        change Apache Cassandra's files."""
        merges, picks = [], []
        for commit in reversed(self.spine):
            parents = self.parents(commit)
            if len(parents) > 2:
                self.error("%s: the merge has %d parents. An import has merges of two parents only" % (self.subject(commit), len(parents)))
            elif len(parents) == 2:
                if is_ancestor(self.repo, parents[1], self.base):
                    self.check_merge(commit, parents)
                elif is_import_merge:
                    merges.append((commit, parents))
                else:
                    self.error("%s: the merge brings commits that are not on the line. A single commit is imported with "
                               "'git cherry-pick -x', and the branch merges nothing but its line" % self.subject(commit))
            elif len(parents) == 1:
                stock = self.stock_files(commit)
                if stock is None:
                    self.error("%s: the change of the commit cannot be read" % self.subject(commit))
                elif stock:
                    picks.append((commit, stock))
            else:
                self.error("%s: the commit has no parent. An import branch is cut from its line" % self.subject(commit))
        return merges, picks

    def refuse_stock_changes(self, picks, what):
        for commit, stock in picks[:SHOWN]:
            shown = ", ".join(stock[:5]) + (" and %d more" % (len(stock) - 5) if len(stock) > 5 else "")
            self.error("%s: the commit changes %d file(s) of Apache Cassandra, %s. %s" % (self.subject(commit), len(stock), shown, what))
        if len(picks) > SHOWN:
            self.error("%d more such commits" % (len(picks) - SHOWN))

    def merge_form(self, name, wanted, on_branch=None):
        """A release or a branch import. wanted is the commit of the tag,
        or the short hash for a branch import, where on_branch is the head
        of Apache's branch."""
        merges, picks = self.check_spine(True)
        self.refuse_stock_changes(picks, "An import brings Apache Cassandra's history through its merge commit and changes no other file "
                                         "of Apache Cassandra. A change the merge needs is part of the merge commit, where the check shows "
                                         "it to the maintainers. Any other change has its own pull request")
        if len(merges) != 1:
            self.error("the branch has %d merge commits that bring history from outside the line, and an import of Apache Cassandra's %s "
                       "has one: the merge of it into the branch" % (len(merges), name))
            return
        commit, parents = merges[0]
        brought = parents[1]
        if on_branch is None and brought != wanted:
            self.error("%s: the merge brings the commit %s, and Apache Cassandra's %s is the commit %s. The second parent of an "
                       "import's merge commit is the commit of the tag its branch names" % (self.subject(commit), brought, name, wanted))
            return
        if on_branch is not None and not (brought.startswith(wanted) and is_ancestor(self.repo, brought, on_branch)):
            self.error("%s: the merge brings the commit %s, which is not a commit of Apache Cassandra's %s whose hash opens with %s. "
                       "The second parent of an import's merge commit is the commit its branch names"
                       % (self.subject(commit), brought, name, wanted))
            return
        self.check_merge(commit, parents)
        self.notes.append("%s merges the commit %s of Apache Cassandra's %s" % (commit[:10], brought, name))

    def message(self, commit):
        return read(self.repo, "log", "-1", "--no-show-signature", "--format=%B", commit) or ""

    def picked_again(self, commit, original):
        """What git gives when it picks the original commit onto the parent
        of the pick again: (the tree, whether git made it with no
        conflict), or None when it cannot be made here. The pick is held
        to that tree, so a line in another place, with other whitespace
        or in another file is seen."""
        before, onto = self.parents(original), self.parents(commit)
        if len(before) != 1 or len(onto) != 1:
            return None
        rc, out = git(self.repo, "merge-tree", "--write-tree", "--no-messages", "--merge-base=" + before[0], onto[0], original)
        tree = out.split("\n", 1)[0].strip() if isinstance(out, str) else ""
        if rc not in (0, 1) or not re.match(r"^[0-9a-f]{40,64}$", tree):
            return None
        return tree, rc == 0

    def pick_form(self, source, heads, ticket=None, wanted=None, unchanged_only=False):
        """One commit taken with git cherry-pick -x. heads is where the
        fetched branches of the source are, ticket the Apache ticket the
        original names, wanted the hash the description names."""
        merges, picks = self.check_spine(False)
        if len(picks) != 1:
            self.refuse_stock_changes(picks if len(picks) > 1 else [], "The import of a single commit has one commit that changes "
                                                                       "Apache Cassandra's files, the commit 'git cherry-pick -x' makes")
            if not picks:
                self.error("the branch adds no commit that changes Apache Cassandra's files, and the import of a single commit has one, "
                           "the commit 'git cherry-pick -x' makes")
            return
        commit, _ = picks[0]
        lines = self.message(commit).rstrip().split("\n")
        match = PICKED.match(lines[-1].strip()) if lines else None
        if not match:
            self.error("%s: the message does not end with the line '(cherry picked from commit <full hash>)', which "
                       "'git cherry-pick -x' adds. The commit names where it came from (docs/process/principles.md, PRINCIPLE-075)"
                       % self.subject(commit))
            return
        original = match.group(1)
        if wanted and original != wanted:
            self.error("%s: the commit was picked from %s, and the pull request's Origin line names %s" % (self.subject(commit), original, wanted))
            return
        holds = read(self.repo, "for-each-ref", "--contains", original, "--format=%(refname)", heads) if commit_of(self.repo, original) else None
        if not holds:
            self.error("%s: the commit %s it was picked from is on no branch of %s. A commit is imported from a branch of the "
                       "repository the import names" % (self.subject(commit), original, source))
            return
        was = self.message(original)
        if ticket and not re.search(r"(?<![A-Za-z0-9-])%s(?![0-9])" % re.escape(ticket), was):
            self.error("%s: the message of the commit %s it was picked from does not name %s, the ticket of the branch"
                       % (self.subject(commit), original, ticket))
        if "\n".join(lines[:-1]).rstrip() != was.rstrip():
            self.error("%s: the message is not the message of the commit %s with the cherry-pick line added. An imported commit "
                       "keeps its message (docs/process/principles.md, PRINCIPLE-075)" % (self.subject(commit), original))
        form = "--format=%an%x00%ae%x00%ad"
        if read(self.repo, "log", "-1", "--no-show-signature", "--date=raw", form, commit) != read(
                self.repo, "log", "-1", "--no-show-signature", "--date=raw", form, original):
            self.error("%s: the author or the author date is not that of the commit %s. An imported commit keeps its author, "
                       "and the author is never rewritten (docs/process/principles.md, PRINCIPLE-075)" % (self.subject(commit), original))
        again = self.picked_again(commit, original)
        if again is None:
            self.error("%s: the commit %s cannot be picked again here, so the pick cannot be checked. The original has one parent, "
                       "and the check needs git 2.40 or later" % (self.subject(commit), original))
            return
        tree, clean = again
        if not clean or tree != read(self.repo, "rev-parse", commit + "^{tree}"):
            _, names = git(self.repo, "diff", "--name-only", "-z", "--no-renames", tree, commit)
            files = [path for path in names.split("\0") if path] if isinstance(names, str) else []
            files = files or ["(the change)"]
            if unchanged_only:
                self.error("%s: the commit is not what git gives when it picks the commit %s again. A commit of another project comes "
                           "in unchanged or not at all. A maintainer ports it instead, as the project's own change that credits its "
                           "authors (docs/process/upstream.md, Commits from other projects)" % (self.subject(commit), original))
            else:
                self.by_hand(commit, "the commit is not what git gives when it picks the commit %s again" % original, files)
        self.notes.append("%s is the commit %s of %s, on %s" % (commit[:10], original, source, holds.split("\n")[0][len(heads):]))


def reviews_of(text):
    """The reviews of a pull request, from the GitHub API's answer: one
    JSON list, or the lists of several pages one after another."""
    found, decoder, index = [], json.JSONDecoder(), 0
    while index < len(text):
        if text[index].isspace():
            index += 1
            continue
        value, index = decoder.raw_decode(text, index)
        found += value if isinstance(value, list) else [value]
    return found


def origin_of(body):
    found = None
    for line in (body or "").splitlines():
        match = ORIGIN.match(line.strip())
        if match:
            found = match.groups()
    return found


def check_history(repo, base, head, branch, body, reviews, github):
    """Returns the findings, the notes on what the import brings and the
    files resolved by hand."""
    if commit_of(repo, base) is None or commit_of(repo, head) is None:
        return ["%s or %s is not a commit here, so the import cannot be read. Fetch both first" % (base, head)], [], []
    head = commit_of(repo, head)
    history = History(repo, base, head, reviews)
    if not history.own:
        return ["%s on %s has no Where things live table, so the project's own files cannot be told from Apache Cassandra's" % (CONVENTIONS, base)], [], []
    if not history.added:
        return ["the branch adds no commit to %s" % base], [], []
    apache = github + APACHE + ".git"
    heads = REFS + "apache/heads/"
    match = BRANCH_IMPORT.match(branch)
    if match:
        name = "cassandra-" + match.group(1)
        if not fetch(repo, apache, "+refs/heads/%s:%s%s" % (name, heads, name)):
            return ["Apache Cassandra's branch %s cannot be fetched from %s, so the import cannot be checked against it" % (name, apache)], [], []
        history.merge_form("branch " + name, match.group(2), commit_of(repo, heads + name))
        return history.errors, history.notes, history.resolved
    match = RELEASE_IMPORT.match(branch)
    if match:
        name = match.group(1)
        if not fetch(repo, apache, "+refs/tags/%s:%sapache/tags/%s" % (name, REFS, name)):
            return ["Apache Cassandra has no tag %s at %s, or it cannot be fetched, so the import cannot be checked against it. "
                    "The branch of a release import is named after the Apache release tag" % (name, apache)], [], []
        history.merge_form("tag " + name, commit_of(repo, "%sapache/tags/%s" % (REFS, name)))
        return history.errors, history.notes, history.resolved
    match = FIX_IMPORT.match(branch)
    if match:
        if not fetch(repo, apache, "+refs/heads/cassandra-*:%scassandra-*" % heads, "+refs/heads/trunk:%strunk" % heads):
            return ["Apache Cassandra's branches cannot be fetched from %s, so the import cannot be checked against them" % apache], [], []
        history.pick_form(APACHE, heads, ticket="CASSANDRA-" + match.group(1))
        return history.errors, history.notes, history.resolved
    match = OTHER_IMPORT.match(branch)
    if match:
        origin = origin_of(body)
        if origin is None:
            return ["the pull request description has no line 'Origin: https://github.com/<owner>/<repo>/commit/<full hash>', "
                    "which names the commit this import takes (docs/process/upstream.md, Commits from other projects)"], [], []
        owner, name, wanted = origin
        if "%s-%s" % (owner, name) != match.group(1) or not wanted.startswith(match.group(2)):
            return ["the branch %s does not name the commit of the pull request's Origin line. For that commit the branch is "
                    "import/%s-%s-%s/<line>" % (branch, owner, name, wanted[:12])], [], []
        if (owner.lower(), name.lower()) == tuple(APACHE.split("/")):
            return ["a commit of Apache Cassandra is imported from a branch import/CASSANDRA-<n>/<line>, never as a commit of another project"], [], []
        source = "%s/%s" % (owner, name)
        heads = REFS + "other/heads/"
        if not fetch(repo, github + source + ".git", "+refs/heads/*:%s*" % heads):
            return ["the branches of %s cannot be fetched from %s, so the import cannot be checked against them" % (source, github + source + ".git")], [], []
        history.pick_form(source, heads, wanted=wanted, unchanged_only=True)
        return history.errors, history.notes, history.resolved
    return ["the branch %s has none of the forms of an import branch: %s" % (branch, FORMS)], [], []


def main(argv):
    names = ("--repo", "--base", "--head", "--branch", "--body", "--reviews", "--github")
    found = {}
    args = argv[1:]
    index = 0
    while index < len(args):
        if args[index] in names and index + 1 < len(args):
            found[args[index]] = args[index + 1]
            index += 2
            continue
        break
    if not argv or argv[0] != "history" or index < len(args) or any(name not in found for name in names[:4]):
        sys.stderr.write(__doc__)
        return 2
    body, reviews = "", []
    try:
        if "--body" in found:
            with open(found["--body"], encoding="utf-8") as handle:
                body = handle.read()
        if "--reviews" in found:
            with open(found["--reviews"], encoding="utf-8") as handle:
                reviews = reviews_of(handle.read())
    except (OSError, ValueError):
        sys.stderr.write("the pull request description or its reviews cannot be read\n")
        return 2
    errors, notes, resolved = check_history(found["--repo"], found["--base"], found["--head"], found["--branch"], body, reviews,
                                            found.get("--github", GITHUB))
    for path in resolved:
        print("RESOLVED %s" % path)
    # What the import brings is said only of an import that passes.
    for note in notes if not errors else []:
        print(note)
    for error in errors:
        sys.stderr.write(error + "\n")
    print("import-history %s" % ("failed" if errors else "passed"))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
