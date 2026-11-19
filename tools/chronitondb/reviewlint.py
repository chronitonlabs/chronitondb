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
"""Checks the review verdict of a pull request against
docs/process/branching-and-review.md, The review record: the newest review
of the project's review App on the pull request is a verdict, and it names
the commit the pull request is at now. The CI workflow
chronitondb-review-verdict.yml runs it on every pull request into a line.
The check only reads. It starts no review and asks for none.

    reviewlint.py verdict --app FILE --maintainers FILE --pull FILE --events FILE --reviews FILE --edits FILE

--app is tools/chronitondb/review-app.json as the line has it, never as the pull
request has it. It names the review App and the project's automation:

    app_id               the id of the GitHub App, a number above 0. No
                         answer of GitHub carries it on a review, so it
                         is kept for people and no check compares it
    app_slug             its name in addresses. Its reviews come from the
                         user <app_slug>[bot]
    bot_user_id          the id of that user, a number above 0
    automation_user_ids  the ids of the accounts the project's automation
                         writes pull requests as, one number or more

While a value is missing or is a placeholder, 0, "" or an empty list, the
check fails and says so: nothing can be held to names that are not given.

--maintainers is docs/governance/committers.md as the line has it. --pull
is the answer of the GitHub API for the pull request, --events its answer
for the events of the pull request as an issue, --reviews its answer for
the reviews of the pull request, each one list or the lists of its pages
one after another, and --edits the answer of the GraphQL API for the same
reviews, with fullDatabaseId, lastEditedAt and editor of each.

A review by the project's review roles runs on two kinds of pull request
only, so a verdict is due on those and on no other:

  a. the author of the pull request is one of automation_user_ids, by its
     id, never by a name
  b. the pull request carries the label triage:accepted, and the event
     that last set the label names a maintainer of the table Maintainers
     as its actor. A label set by anyone else accepts nothing

Any other pull request passes, with the line "no review verdict is due".
A maintainer's own review and the other checks still hold it. A pull
request that carries the label while no event says who set it fails: the
check cannot tell.

A review is the App's when its user has the type Bot, the login
<app_slug>[bot] and the id bot_user_id, all three. A login can be given up
and taken by another account, the id cannot. A review of any other account
counts for nothing, whatever its text says. GitHub's answers do not carry
the id of the App that posted a review, so the check holds a review to
the App's user, and app_id says which App that user belongs to.

Where a verdict is due, the newest review of the App, by the time it was
submitted, is held to:

  1. its state is COMMENTED: the App never approves and never asks for
     changes, a maintainer does
  2. its commit_id is the head commit of the pull request
  3. its text holds a verdict block, the last fenced json block that names
     "lenses", and the "head" of that block is the same commit
  4. nobody edited it after it was posted: --edits knows the review, and
     shows no edit and no editor

A pull request whose author is the App's user fails: the reviewer is never
the author. So does a pull request from a checkpoint branch of this
repository, agent/<issue>-<slug>/checkpoint/<line>, which never has a pull
request.

It prints "review-verdict passed" with the review it took, or
"review-verdict failed", on stdout. Findings go to stderr, one per line,
exit 1 when there is one. A usage error exits 2.
"""

import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from markdown import Markdown, first_table  # noqa: E402

LABEL = "triage:accepted"
USERNAME = re.compile(r"^`([A-Za-z0-9][A-Za-z0-9-]*)`$")
APP_FILE = "tools/chronitondb/review-app.json"
SLUG = re.compile(r"^[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$")
COMMIT = re.compile(r"^[0-9a-f]{40}$")
CHECKPOINT = re.compile(r"^agent/[^/]+/checkpoint/[^/]+$")
FENCE_OPEN = re.compile(r"^ {0,3}```json\s*$")
FENCE_CLOSE = re.compile(r"^ {0,3}```\s*$")
RULE = "docs/process/branching-and-review.md, The review record"


def is_id(value):
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def app_of(app):
    """(slug, bot user id, automation user ids) of the review App file,
    None while a value is missing or a placeholder."""
    if not isinstance(app, dict):
        return None
    slug, authors = app.get("app_slug"), app.get("automation_user_ids")
    if not is_id(app.get("app_id")) or not is_id(app.get("bot_user_id")) or not isinstance(slug, str) or not SLUG.match(slug):
        return None
    if not isinstance(authors, list) or not authors or not all(is_id(author) for author in authors) or app["bot_user_id"] in authors:
        return None
    return slug, app["bot_user_id"], authors


def maintainers_of(text):
    """The GitHub usernames of the table Maintainers of the public
    record, in lower case."""
    doc = Markdown("committers.md", text or "")
    found = []
    for level, title, index in doc.headings:
        if title == "Maintainers":
            start, end = doc.span(level, index)
            for _, cells in first_table(doc, start, end):
                for cell in cells:
                    match = USERNAME.match(cell)
                    if match:
                        found.append(match.group(1).lower())
            break
    return found


def accepted_by(pull, events):
    """Who last set the label triage:accepted on the pull request: the
    login of the actor in lower case, "" when the pull request carries
    the label and no event says who set it, None when it does not carry
    the label."""
    labels = pull.get("labels") if isinstance(pull.get("labels"), list) else []
    if not any(isinstance(label, dict) and label.get("name") == LABEL for label in labels):
        return None
    last = None
    for event in events:
        if (isinstance(event, dict) and event.get("event") in ("labeled", "unlabeled") and isinstance(event.get("label"), dict)
                and event["label"].get("name") == LABEL and isinstance(event.get("created_at"), str) and is_id(event.get("id"))):
            if last is None or (event["created_at"], event["id"]) > (last["created_at"], last["id"]):
                last = event
    if last is None or last["event"] != "labeled" or not isinstance(last.get("actor"), dict):
        return ""
    return str(last["actor"].get("login") or "").lower()


def pages_of(text):
    """The items of an answer of the GitHub API: one JSON list, or the
    lists of several pages one after another."""
    found, decoder, index = [], json.JSONDecoder(), 0
    while index < len(text):
        if text[index].isspace():
            index += 1
            continue
        value, index = decoder.raw_decode(text, index)
        found += value if isinstance(value, list) else [value]
    return found


def is_of_app(user, slug, bot):
    return (isinstance(user, dict) and user.get("type") == "Bot" and user.get("login") == slug + "[bot]"
            and is_id(user.get("id")) and user.get("id") == bot)


def verdict_block(body):
    """The verdict block of a review text: the object of its last fenced
    json block that names "lenses", None when there is none."""
    found, block = None, None
    for line in (body or "").split("\n"):
        if block is None:
            if FENCE_OPEN.match(line):
                block = []
        elif FENCE_CLOSE.match(line):
            try:
                value = json.loads("\n".join(block))
            except ValueError:
                value = None
            if isinstance(value, dict) and "lenses" in value:
                found = value
            block = None
        else:
            block.append(line)
    return found


def edits_of(answer):
    """The reviews of the GraphQL answer, by their database id."""
    found = {}

    def walk(value):
        if isinstance(value, dict):
            if "fullDatabaseId" in value:
                found[str(value["fullDatabaseId"])] = value
            for inner in value.values():
                walk(inner)
        elif isinstance(value, list):
            for inner in value:
                walk(inner)

    walk(answer)
    return found


def check_verdict(app, maintainers, pull, events, reviews, edits):
    """Returns the findings and, when there is none, the note on the
    review that carries the verdict or on why none is due."""
    named = app_of(app)
    if named is None:
        return ["the review App is not named yet: %s on the line holds a placeholder or lacks a value. A maintainer fills app_id, "
                "app_slug, bot_user_id and automation_user_ids there, and until then the check cannot tell where a verdict is due "
                "or who gave one (%s)" % (APP_FILE, RULE)], None
    slug, bot, authors = named
    login = slug + "[bot]"
    head = pull.get("head") if isinstance(pull, dict) else None
    sha = head.get("sha") if isinstance(head, dict) else None
    author = pull.get("user") if isinstance(pull, dict) else None
    if not isinstance(sha, str) or not COMMIT.match(sha) or not isinstance(author, dict) or not is_id(author.get("id")):
        return ["the head commit or the author of the pull request cannot be read from the answer of the API"], None
    errors = []
    if author["id"] == bot:
        errors.append("the author of the pull request is %s, the review App. The reviewer is never the author (%s)" % (login, RULE))
    elif author["id"] not in authors:
        # Not the automation's own work: a verdict is due only once a
        # maintainer accepted the pull request for review.
        accepted = accepted_by(pull, events)
        if accepted is None:
            return [], ("no review verdict is due: the project's automation did not write this pull request and no maintainer has "
                        "accepted it for review with the label %s" % LABEL)
        if accepted == "":
            return ["the pull request carries the label %s and no event of the pull request says who set it, so the check cannot "
                    "tell whether a maintainer accepted it for review" % LABEL], None
        if accepted not in maintainers:
            return [], ("no review verdict is due: the label %s was set by %s, who is no maintainer of docs/governance/committers.md "
                        "on the line, so no maintainer has accepted this pull request for review" % (LABEL, accepted))
    here = (pull.get("base") or {}).get("repo") if isinstance(pull.get("base"), dict) else None
    there = head.get("repo")
    if (isinstance(here, dict) and isinstance(there, dict) and here.get("full_name") and here.get("full_name") == there.get("full_name")
            and CHECKPOINT.match(str(head.get("ref") or ""))):
        errors.append("the head branch %s is a checkpoint branch, which never has a pull request "
                      "(docs/process/branching-and-review.md, Work branches)" % head.get("ref"))
    ours = [review for review in reviews
            if isinstance(review, dict) and is_of_app(review.get("user"), slug, bot) and isinstance(review.get("submitted_at"), str)
            and is_id(review.get("id"))]
    if not ours:
        errors.append("the pull request has no review of %s, the review App, so it has no review verdict. A review of any other "
                      "account is no verdict. The check passes when it is run again after the verdict is posted (%s)" % (login, RULE))
        return errors, None
    newest = max(ours, key=lambda review: (review["submitted_at"], review["id"]))
    what = "the newest review of %s, %d" % (login, newest["id"])
    if newest.get("state") != "COMMENTED":
        errors.append("%s, has the state %s. A verdict is a review that comments: the App never approves and never asks for changes"
                      % (what, newest.get("state")))
    commit = newest.get("commit_id")
    if commit != sha:
        errors.append("%s, is a review of the commit %s, and the pull request is at %s now. The verdict names the commit it read, "
                      "so a later commit needs a new verdict" % (what, commit, sha))
    block = verdict_block(newest.get("body") if isinstance(newest.get("body"), str) else "")
    if block is None:
        errors.append("%s, holds no verdict block: a fenced json block that names \"lenses\"" % what)
    elif block.get("head") != commit or not isinstance(commit, str) or not COMMIT.match(commit):
        errors.append("%s, has a verdict block whose \"head\" is %s, and the review is of the commit %s. The two are the same commit"
                      % (what, block.get("head"), commit))
    edit = edits_of(edits).get(str(newest["id"]))
    if edit is None:
        errors.append("%s, is not in the answer of the GraphQL API, so the check cannot tell whether it was edited" % what)
    elif edit.get("lastEditedAt") is not None or edit.get("editor") is not None:
        editor = edit.get("editor") if isinstance(edit.get("editor"), dict) else {}
        errors.append("%s, was edited after it was posted%s. An edited verdict does not count: the App posts a new one"
                      % (what, ", by %s" % editor.get("login") if editor.get("login") else ""))
    if errors:
        return errors, None
    return [], "the review %d of %s is the verdict on the commit %s" % (newest["id"], login, sha)


def main(argv):
    names = ("--app", "--maintainers", "--pull", "--events", "--reviews", "--edits")
    found = {}
    args = argv[1:]
    index = 0
    while index < len(args):
        if args[index] in names and index + 1 < len(args):
            found[args[index]] = args[index + 1]
            index += 2
            continue
        break
    if not argv or argv[0] != "verdict" or index < len(args) or any(name not in found for name in names):
        sys.stderr.write(__doc__)
        return 2
    read = {}
    for name in names:
        try:
            with open(found[name], encoding="utf-8") as handle:
                text = handle.read()
            if name == "--maintainers":
                read[name] = maintainers_of(text)
            else:
                read[name] = pages_of(text) if name in ("--reviews", "--events") else json.loads(text)
        except (OSError, ValueError):
            # A file that cannot be read holds nothing.
            read[name] = [] if name in ("--reviews", "--events", "--maintainers") else None
    errors, note = check_verdict(read["--app"], read["--maintainers"], read["--pull"], read["--events"], read["--reviews"], read["--edits"])
    for error in errors:
        sys.stderr.write(error + "\n")
    if note:
        print(note)
    print("review-verdict %s" % ("failed" if errors else "passed"))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
