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
"""Checks commit subjects against the rules of docs/process/conventions.md,
Commit messages: a pull request's title, which becomes the subject of its
squash or merge commit on the line, and the subjects of the commits a push
brings to a line. The CI workflow chronitondb-subjects.yml runs it on every
pull request and on every push to a line.

    subjectlint.py title --repo DIR --rules REF [--commits RANGE] [--body FILE] TITLE
    subjectlint.py commits --repo DIR --rules REF RANGE

REF is where the rules are read, the line itself, never the change being
checked: the type list, the table under Types, and the length limit, the
rule "The subject is at most N characters", both in conventions.md.

A subject is checked for:

  1. the form "type(scope): description", with "!" after the scope for a
     breaking change, a type of the list and a scope
  2. at most N characters, not counting a trailing " (chronitondb-<line>)"
     that names the line, nor GitHub's " (#<number>)" at the end of a
     squash or merge commit subject. An import carries its original
     subject unchanged and has no length limit
  3. no file listed: no word in the description that is a path, such as
     ".build/run-ci", "docs/process/" or "Foo.java"
  4. "!" with a footer line "BREAKING CHANGE: <what breaks and what to
     do>", and the footer only with "!". The footer belongs in a commit
     message, since the squash commit on a line carries the messages of
     the pull request's commits, never its description. For a title it is
     read from the messages of the commits of RANGE, the pull request's
     commits. A footer only in FILE, the pull request's description, is
     refused with where to put it. For a commit on a line it is read from
     the commit message
  5. a subject of type import takes one of the import forms of
     conventions.md and upstream.md, and no "!":
       import(CASSANDRA-<n>): <original Apache subject>
       import(apache-<version>): merge Apache Cassandra <version>
       import(apache-<x.y>-branch): merge Apache cassandra-<x.y> at <short hash>
       import(<owner>/<repo>@<12 character hash>): <original subject>
     where <owner>/<repo> is neither apache/cassandra, whose commits come
     as import(CASSANDRA-<n>), nor a repository of chronitonlabs. Rule 3
     is not applied to an import, whose subject is someone else's

commits checks the subject of each commit of RANGE on the first parent
line, the squash and merge commits a line gets, not the commits an import
merge brings with it.

Findings go to stderr, one per line, exit 1 when there is one. A usage
error exits 2.
"""

import re
import subprocess
import sys

CONVENTIONS = "docs/process/conventions.md"
FORM = re.compile(r"^([A-Za-z]+)(?:\(([^()]*)\))?(!)?: (\S.*)$")
SCOPE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
GITHUB_NUMBER = re.compile(r" \(#[0-9]+\)$")
LINE_SUFFIX = re.compile(r" \(chronitondb-[A-Za-z0-9.]+\)$")
FOOTER = re.compile(r"^BREAKING CHANGE: \S")
FILE_NAME = re.compile(r"^[\w-]+\.(?:java|py|sh|ya?ml|xml|md|txt|g|json|cql|properties|html|cfg|conf|asc)$")
DOT_FILE = re.compile(r"^\.[A-Za-z][\w.-]*$")
CASSANDRA = re.compile(r"^CASSANDRA-[1-9][0-9]*$")
BRANCH = re.compile(r"^apache-([0-9]+\.[0-9]+)-branch$")
RELEASE = re.compile(r"^apache-([0-9]+\.[0-9]+(?:\.[0-9]+)?(?:-[a-z]+[0-9]+)?)$")
FORK = re.compile(r"^([A-Za-z0-9-]+)/([A-Za-z0-9._-]+)@([0-9a-f]{12})$")
IMPORT_FORMS = ("import(CASSANDRA-<n>), import(apache-<version>), import(apache-<x.y>-branch) "
                "or import(<owner>/<repo>@<12 character hash>)")


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


def rules_of(text):
    """The types and the length limit conventions.md sets: the types in
    backticks in the first column of the table under "### Types", and the
    number of "The subject is at most N characters"."""
    types, limit, inside = [], None, False
    for line in (text or "").splitlines():
        if line.startswith("#"):
            inside = line.strip() == "### Types"
            continue
        if inside:
            match = re.match(r"^\|\s*`([a-z]+)`\s*\|", line)
            if match:
                types.append(match.group(1))
        found = re.search(r"The subject is at most ([0-9]+) characters", line)
        if found:
            limit = int(found.group(1))
    return types, limit


def paths_in(description):
    """The words of a description that are paths: a word with "/" that
    starts with ".", ends with "/" or ends in a file name with an
    extension, a file name with a source or text extension, or a dot
    file such as ".editorconfig"."""
    found = []
    for word in description.split():
        word = word.strip("`'\"()[],;:").rstrip(".")
        if "/" in word:
            last = word.rstrip("/").rsplit("/", 1)[-1]
            if word.startswith(".") or word.endswith("/") or re.search(r"\.[A-Za-z0-9]+$", last):
                found.append(word)
        elif FILE_NAME.match(word) or DOT_FILE.match(word):
            found.append(word)
    return found


def check_import(scope, description, bang):
    if bang:
        return ["an import takes no '!'. Its subject is one of the import forms: %s" % IMPORT_FORMS]
    if CASSANDRA.match(scope):
        return []
    match = BRANCH.match(scope)
    if match:
        wanted = re.compile(r"^merge Apache cassandra-%s at [0-9a-f]{7,40}$" % re.escape(match.group(1)))
        if not wanted.match(description):
            return ["an import of Apache's branch reads 'import(%s): merge Apache cassandra-%s at <short hash>'" % (scope, match.group(1))]
        return []
    match = RELEASE.match(scope)
    if match:
        if description != "merge Apache Cassandra %s" % match.group(1):
            return ["an import of an Apache release reads 'import(%s): merge Apache Cassandra %s'" % (scope, match.group(1))]
        return []
    match = FORK.match(scope)
    if match:
        owner, repo = match.group(1).lower(), match.group(2).lower()
        if (owner, repo) == ("apache", "cassandra"):
            return ["an Apache commit is imported as import(CASSANDRA-<n>), never as a commit from another project"]
        if owner == "chronitonlabs":
            return ["a repository of chronitonlabs is never a source of an import. Its work is ours"]
        return []
    return ["the import scope '%s' is not one of the import forms: %s" % (scope, IMPORT_FORMS)]


def has_footer(text):
    return any(FOOTER.match(line) for line in (text or "").splitlines())


def check_length(subject, limit):
    counted = LINE_SUFFIX.sub("", GITHUB_NUMBER.sub("", subject))
    if limit is not None and len(counted) > limit:
        return ["the subject has %d characters, at most %d are allowed, not counting a trailing ' (chronitondb-<line>)'" % (len(counted), limit)]
    return []


def check_footer(kind, scope, bang, description, messages, pr_body):
    """The footer of a breaking change, read from messages, the commit
    messages the commit on the line carries. pr_body is the pull request
    description, None for a commit, where a footer never reaches the
    line."""
    footer = has_footer(messages)
    stray = pr_body is not None and has_footer(pr_body) and not footer
    where = "Put the line 'BREAKING CHANGE: <what breaks and what to do>' in a commit message of the pull request, which the squash commit on the line carries"
    if bang and not footer:
        if stray:
            return ["the 'BREAKING CHANGE:' footer is only in the pull request description, which never reaches the line. " + where]
        if pr_body is not None:
            return ["a breaking change with '!' also takes a footer. " + where]
        return ["a breaking change with '!' also takes a footer line 'BREAKING CHANGE: <what breaks and what to do>' in its commit message"]
    if footer and not bang:
        return ["a 'BREAKING CHANGE:' footer also takes '!' after the scope, as in '%s(%s)!: %s'" % (kind, scope, description)]
    if stray:
        return ["the pull request description has a 'BREAKING CHANGE:' footer. A breaking change takes '!' after the scope, and the footer goes in a commit message of the pull request"]
    return []


def check_subject(subject, messages, types, limit, pr_body=None):
    """The findings for one subject. messages is the text where the footer
    of a breaking change is read: the pull request's commit messages for
    a title, the commit message after the subject for a commit. pr_body is
    the pull request description for a title, None for a commit."""
    match = FORM.match(subject)
    if not match:
        return check_length(subject, limit) + ["the subject has the form 'type(scope): description', for example 'feat(fulltext): add the phrase operator'"]
    kind, scope, bang, description = match.groups()
    if kind not in types:
        return check_length(subject, limit) + ["the type '%s' is not one of %s" % (kind, ", ".join(types))]
    if kind == "import":
        if not scope:
            return ["an import takes one of the import forms: %s" % IMPORT_FORMS]
        errors = check_import(scope, description, bang)
        if has_footer(messages):
            errors.append("an import carries no 'BREAKING CHANGE:' footer")
        return errors
    errors = check_length(subject, limit)
    if not scope:
        errors.append("the subject names its scope, the area of the change, as in '%s(<scope>): %s'" % (kind, description))
        return errors
    if not SCOPE.match(scope):
        errors.append("the scope '%s' is one word naming the area, for example fulltext, build or github" % scope)
    listed = paths_in(LINE_SUFFIX.sub("", description))
    if listed:
        errors.append("the subject lists files (%s). Say what the change does, not which files it touches" % ", ".join(listed))
    return errors + check_footer(kind, scope, bang, description, messages, pr_body)


def load_rules(repo, ref):
    text = git(repo, "show", "%s:%s" % (ref, CONVENTIONS))
    if text is None:
        sys.stderr.write("no %s on %s, so the subject rules cannot be read. Fetch the line first\n" % (CONVENTIONS, ref))
        return None, None
    types, limit = rules_of(text)
    if not types or limit is None:
        sys.stderr.write("%s on %s has no Types table or no length rule, so the subject rules cannot be read\n" % (CONVENTIONS, ref))
        return None, None
    return types, limit


def options(args, names):
    found, rest = {}, []
    index = 0
    while index < len(args):
        if args[index] in names and index + 1 < len(args):
            found[args[index]] = args[index + 1]
            index += 2
        elif args[index].startswith("--"):
            return None, None
        else:
            rest.append(args[index])
            index += 1
    return found, rest


def main(argv):
    if not argv or argv[0] not in ("title", "commits"):
        sys.stderr.write(__doc__)
        return 2
    found, rest = options(argv[1:], ("--repo", "--rules", "--body", "--commits"))
    if found is None or "--repo" not in found or "--rules" not in found or len(rest) != 1:
        sys.stderr.write(__doc__)
        return 2
    repo, ref = found["--repo"], found["--rules"]
    types, limit = load_rules(repo, ref)
    if types is None:
        return 1
    if argv[0] == "title":
        body = ""
        if "--body" in found:
            try:
                with open(found["--body"], encoding="utf-8") as handle:
                    body = handle.read()
            except (OSError, UnicodeDecodeError):
                sys.stderr.write("the pull request description %s cannot be read\n" % found["--body"])
                return 2
        messages = ""
        if "--commits" in found:
            messages = git(repo, "log", "--no-show-signature", "--format=%B", found["--commits"])
            if messages is None:
                sys.stderr.write("the range %s cannot be read. Fetch it first\n" % found["--commits"])
                return 2
        errors = check_subject(rest[0], messages, types, limit, body)
        for error in errors:
            sys.stderr.write("title: %s\n" % error)
        print("title %s" % ("failed" if errors else "passed"))
        return 1 if errors else 0
    listed = git(repo, "rev-list", "--first-parent", "--reverse", rest[0])
    if listed is None:
        sys.stderr.write("the range %s cannot be read. Fetch it first\n" % rest[0])
        return 2
    checked = failed = 0
    for commit in listed.split():
        message = git(repo, "log", "-1", "--no-show-signature", "--format=%B", commit) or ""
        subject, _, body = message.partition("\n")
        errors = check_subject(GITHUB_NUMBER.sub("", subject), body, types, limit)
        checked += 1
        for error in errors:
            sys.stderr.write("%s %s: %s\n" % (commit[:10], subject, error))
        if errors:
            failed += 1
    print("subjects %d checked %d failed" % (checked, failed))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
