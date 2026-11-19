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
"""The review verdict check, docs/process/branching-and-review.md, The
review record: the newest review of the project's review App is a verdict
on the commit the pull request is at. The files under shapes/ are the
answers of the GitHub API the check reads, recorded from a review that a
GitHub App posted on a public pull request, with the names and ids
replaced: reviews.json from GET /repos/{owner}/{repo}/pulls/{number}/reviews,
edits.json from the GraphQL query of the workflow, pull.json from GET
/repos/{owner}/{repo}/pulls/{number} with the fields the check reads and
events.json from GET /repos/{owner}/{repo}/issues/{number}/events. In
the REST answer the login of an App's user ends in [bot] and its type is
Bot. A review nobody edited has lastEditedAt and editor null in the
GraphQL answer. Run from the repository root:

    python3 -m unittest discover -s tools/chronitondb/test/reviewlint
"""

import contextlib
import copy
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.normpath(os.path.join(HERE, "..", ".."))
ROOT = os.path.normpath(os.path.join(TOOLS, "..", ".."))
sys.path.insert(0, TOOLS)
import reviewlint  # noqa: E402

WORKFLOW = ".github/workflows/chronitondb-review-verdict.yml"
APP_FILE = "tools/chronitondb/review-app.json"
APP = {"app_id": 1000001, "app_slug": "example-review", "bot_user_id": 175728472, "automation_user_ids": [583231]}
COMMITTERS = "docs/governance/committers.md"
OTHER = "8f6787959e001c2d50696ef0f9df3e9c85ac36c8"


def read(path):
    with open(os.path.join(ROOT, path), encoding="utf-8") as handle:
        return handle.read()


def shape(name):
    with open(os.path.join(HERE, "shapes", name), encoding="utf-8") as handle:
        return json.load(handle)


def step_env(workflow, name, context):
    """The environment the step NAME of a workflow file sets, each value
    "${{ <name> }}" read from context."""
    lines = read(workflow).split("\n")
    start = lines.index("      - name: %s" % name)
    index = next(i for i in range(start, len(lines)) if lines[i].strip() == "env:")
    found = {}
    for line in lines[index + 1:]:
        match = re.match(r"^\s+([A-Z_]+): \$\{\{ (.*) \}\}$", line)
        if not match:
            break
        found[match.group(1)] = context[match.group(2)]
    return found


def step_script(workflow, name):
    """The shell script of the step NAME of a workflow file."""
    lines = read(workflow).split("\n")
    start = lines.index("      - name: %s" % name)
    index = next(i for i in range(start, len(lines)) if lines[i].strip() == "run: |")
    indent = len(lines[index]) - len(lines[index].lstrip()) + 2
    script = []
    for line in lines[index + 1:]:
        if line.strip() and len(line) - len(line.lstrip()) < indent:
            break
        script.append(line[indent:])
    return "\n".join(script) + "\n"


MAINTAINERS = reviewlint.maintainers_of(read(COMMITTERS))
MAINTAINER = MAINTAINERS[0]


class Verdict(unittest.TestCase):
    """A pull request the project's automation wrote, at one commit, with
    one review of the App on that commit that carries a verdict block and
    was never edited."""

    def setUp(self):
        self.app = dict(APP)
        self.maintainers = list(MAINTAINERS)
        self.pull = shape("pull.json")
        self.events = shape("events.json")
        self.reviews = shape("reviews.json")
        self.edits = shape("edits.json")
        self.head = self.pull["head"]["sha"]

    def check(self):
        return reviewlint.check_verdict(self.app, self.maintainers, self.pull, self.events, self.reviews, self.edits)

    def not_due(self, text):
        errors, note = self.check()
        self.assertEqual(errors, [])
        self.assertTrue(note.startswith("no review verdict is due: "), note)
        self.assertIn(text, note)

    def label(self, event="labeled", login=MAINTAINER, name="triage:accepted", **more):
        """One more event of the pull request, a minute after the last."""
        self.events.append(dict({"id": 20000000010 + len(self.events), "event": event, "label": {"name": name},
                                 "actor": {"login": login, "id": 1000002, "type": "User"},
                                 "created_at": "2026-11-19T07:%02d:00Z" % len(self.events)}, **more))

    def by_someone_else(self):
        """The pull request of an account that is not the automation's."""
        self.pull["user"] = {"login": "someone", "id": 424242, "type": "User"}
        self.reviews = []

    # Where a verdict is due.

    def test_the_automations_own_pull_request_needs_a_verdict(self):
        self.reviews = []
        self.refused("the pull request has no review of example-review[bot]")
        # The id tells the automation, never the name.
        self.pull["user"] = {"login": "octocat", "id": 424242, "type": "User"}
        self.not_due("the project's automation did not write this pull request and no maintainer has accepted it for review with the label triage:accepted")

    def test_any_other_pull_request_passes_until_a_maintainer_accepts_it(self):
        self.by_someone_else()
        self.not_due("no maintainer has accepted it for review with the label triage:accepted")
        self.pull["labels"] = [{"name": "kind:corrective"}, {"name": "triage:accepted-later"}]
        self.not_due("no maintainer has accepted it")

    def test_a_pull_request_a_maintainer_accepted_needs_a_verdict(self):
        self.by_someone_else()
        self.pull["labels"] = [{"name": "triage:accepted"}]
        self.label()
        self.refused("the pull request has no review of example-review[bot], the review App, so it has no review verdict")
        self.review()
        self.passes()
        # A commit after the verdict needs a new one.
        self.pull["head"]["sha"] = OTHER
        self.refused("and the pull request is at %s now" % OTHER)

    def test_a_label_set_by_anyone_else_accepts_nothing(self):
        self.by_someone_else()
        self.pull["labels"] = [{"name": "triage:accepted"}]
        self.label(login="someone")
        self.not_due("the label triage:accepted was set by someone, who is no maintainer")
        # The one who set it last counts.
        self.label("unlabeled", login="someone")
        self.label(login=MAINTAINER.upper())
        self.refused("the pull request has no review of example-review[bot]")
        self.label("unlabeled")
        self.label(login="someone")
        self.not_due("was set by someone")
        # The list of maintainers is the one given, the line's.
        self.maintainers = ["someone"]
        self.refused("the pull request has no review of example-review[bot]")

    def test_the_last_event_is_told_by_its_time(self):
        self.by_someone_else()
        self.pull["labels"] = [{"name": "triage:accepted"}]
        self.label()
        self.label(login="someone")
        self.events.reverse()
        self.not_due("was set by someone")

    def test_a_label_nobody_is_seen_to_set_fails(self):
        self.by_someone_else()
        self.pull["labels"] = [{"name": "triage:accepted"}]
        for events in ([], [None, "labeled"], shape("events.json")):
            self.events = events
            self.refused("carries the label triage:accepted and no event of the pull request says who set it")
        # Another label's event, an event with no actor and a label taken off say nothing.
        self.events = []
        self.label(name="kind:corrective")
        self.refused("no event of the pull request says who set it")
        self.label(actor=None)
        self.refused("no event of the pull request says who set it")
        self.label()
        self.label("unlabeled")
        self.refused("no event of the pull request says who set it")

    def test_the_maintainers_are_read_from_the_public_record(self):
        self.assertEqual(reviewlint.maintainers_of("# Committers\n\n## Maintainers\n\n| Name | GitHub username |\n|---|---|\n| A | `Ann-1` |\n| B | `bob` |\n\n"
                                                   "## Committers\n\n| Name | GitHub username |\n|---|---|\n| C | `carol` |\n"), ["ann-1", "bob"])
        self.assertEqual(reviewlint.maintainers_of("## Committers\n\n| Name | GitHub username |\n|---|---|\n| C | `carol` |\n"), [])
        self.assertEqual(reviewlint.maintainers_of(""), [])
        self.assertGreater(len(MAINTAINERS), 0)

    def passes(self):
        errors, note = self.check()
        self.assertEqual(errors, [])
        return note

    def refused(self, text):
        errors, note = self.check()
        self.assertIsNone(note)
        self.assertTrue(any(text in error for error in errors), errors)

    def review(self, **changes):
        """One more review, like the recorded one but for the changes. A
        key with a dot changes a field of the user."""
        review = copy.deepcopy(shape("reviews.json")[0])
        review["id"] += len(self.reviews)
        review["submitted_at"] = "2026-11-19T07:%02d:00Z" % len(self.reviews)
        for key, value in changes.items():
            if key.startswith("user_"):
                review["user"][key[5:]] = value
            else:
                review[key] = value
        self.reviews.append(review)
        self.edits["data"]["repository"]["pullRequest"]["reviews"]["nodes"].append(
            {"fullDatabaseId": str(review["id"]), "lastEditedAt": None, "editor": None})
        return review

    def body(self, head, text="Round 3.", lenses=True):
        block = {"head": head, "approve": True, "ready": True}
        if lenses:
            block["lenses"] = ["correctness"]
        return "%s\n\n```json\n%s\n```\n" % (text, json.dumps(block))

    def test_the_verdict_of_the_app_on_the_head_passes(self):
        self.assertEqual(self.passes(), "the review 5970525038 of example-review[bot] is the verdict on the commit " + self.head)

    def test_a_verdict_with_findings_passes_too(self):
        # The check holds who gave the verdict and on which commit. What a
        # maintainer does with its findings is the maintainer's.
        self.reviews[0]["body"] = "Round 1. 2 blocker.\n\n```json\n%s\n```\n" % json.dumps(
            {"head": self.head, "approve": False, "ready": False, "lenses": ["security"]})
        self.passes()

    # The App is named on the line.

    def test_the_placeholders_fail_with_the_file_to_fill(self):
        for app in ({"app_id": 0, "app_slug": "", "bot_user_id": 0, "automation_user_ids": []}, {}, None, [], "example-review",
                    dict(APP, automation_user_ids=[]), dict(APP, automation_user_ids=[0]), dict(APP, automation_user_ids=["583231"]),
                    dict(APP, automation_user_ids=583231), dict(APP, automation_user_ids=[583231, True]),
                    dict(APP, automation_user_ids=[175728472]), {k: v for k, v in APP.items() if k != "automation_user_ids"},
                    dict(APP, app_id=0), dict(APP, bot_user_id=0), dict(APP, app_slug=""), dict(APP, app_id="1000001"),
                    dict(APP, bot_user_id="175728472"), dict(APP, bot_user_id=True), dict(APP, app_id=-1), dict(APP, bot_user_id=1.5),
                    dict(APP, app_slug="Example Review"), dict(APP, app_slug="example-review[bot]"), dict(APP, app_slug=None),
                    {"app_slug": "example-review", "bot_user_id": 175728472}, {"app_id": 1000001, "app_slug": "example-review"}):
            self.app = app
            errors, note = self.check()
            self.assertIsNone(note)
            self.assertEqual(len(errors), 1, app)
            self.assertIn("the review App is not named yet: tools/chronitondb/review-app.json on the line holds a placeholder or lacks a value. "
                          "A maintainer fills app_id, app_slug, bot_user_id and automation_user_ids there", errors[0])

    def test_the_file_of_this_tree_has_the_three_values_or_its_placeholders(self):
        app = json.loads(read(APP_FILE))
        self.assertEqual(sorted(app), ["app_id", "app_slug", "automation_user_ids", "bot_user_id"])
        if reviewlint.app_of(app) is None:
            self.assertEqual(app, {"app_id": 0, "app_slug": "", "bot_user_id": 0, "automation_user_ids": []})

    # Only the App's user gives a verdict.

    def test_a_review_of_any_other_account_counts_for_nothing(self):
        mine = self.reviews.pop()
        for changes in ({"user_id": 583231, "user_login": "octocat", "user_type": "User"},
                        # The login of the App with another id, as after the name was given up and taken.
                        {"user_id": 583231},
                        {"user_id": 583231, "user_type": "User"},
                        # The id of the App's user under another login or type.
                        {"user_login": "example-review"},
                        {"user_login": "other-review[bot]"},
                        {"user_type": "User"},
                        {"user_type": "Organization"},
                        {"user_id": "175728472"},
                        {"user_id": True},
                        {"user": None},
                        {"user": "example-review[bot]"}):
            self.reviews = []
            self.review(**changes)
            self.refused("the pull request has no review of example-review[bot], the review App, so it has no review verdict")
        self.reviews = [mine]
        self.passes()

    def test_a_later_review_of_another_account_does_not_hide_the_verdict(self):
        self.review(user_id=583231, user_login="octocat", user_type="User", commit_id=OTHER, body=self.body(OTHER))
        self.passes()

    def test_no_review_at_all_is_refused(self):
        self.reviews = []
        self.refused("the pull request has no review of example-review[bot]")
        self.reviews = [None, "review", {"id": 1}]
        self.refused("the pull request has no review of example-review[bot]")

    def test_a_review_not_yet_submitted_is_no_verdict(self):
        del self.reviews[0]["submitted_at"]
        self.reviews[0]["state"] = "PENDING"
        self.refused("the pull request has no review of example-review[bot]")

    # The newest review of the App names the head.

    def test_the_newest_review_of_the_app_counts(self):
        # An earlier verdict on the head, then a review of another commit.
        self.review(commit_id=OTHER, body=self.body(OTHER))
        self.refused("is a review of the commit %s, and the pull request is at %s now" % (OTHER, self.head))
        # A verdict on the head after it passes again.
        self.review()
        self.passes()

    def test_the_newest_is_told_by_the_time_it_was_submitted(self):
        late = self.review(commit_id=OTHER, body=self.body(OTHER))
        self.reviews.reverse()
        self.refused("the newest review of example-review[bot], %d, is a review of the commit %s" % (late["id"], OTHER))
        late["submitted_at"] = "2026-11-19T06:00:00Z"
        self.passes()

    def test_a_verdict_on_an_earlier_head_is_refused(self):
        self.pull["head"]["sha"] = OTHER
        self.refused("is a review of the commit %s, and the pull request is at %s now. The verdict names the commit it read" % (self.head, OTHER))

    def test_a_head_that_cannot_be_read_is_refused(self):
        user = {"login": "octocat", "id": 583231}
        for pull in (None, {}, [], {"head": {}, "user": user}, {"head": {"sha": "34103ea"}, "user": user},
                     {"head": {"sha": self.head.upper()}, "user": user}, {"head": {"sha": None}, "user": user},
                     {"head": {"sha": self.head}}, {"head": {"sha": self.head}, "user": {"login": "octocat"}},
                     {"head": {"sha": self.head}, "user": {"login": "octocat", "id": "583231"}}):
            self.pull = pull
            self.refused("the head commit or the author of the pull request cannot be read")

    def test_a_review_that_approves_or_asks_for_changes_is_no_verdict(self):
        for state in ("APPROVED", "CHANGES_REQUESTED", "DISMISSED", "PENDING", None):
            self.reviews[0]["state"] = state
            self.refused("has the state %s. A verdict is a review that comments" % state)

    # The verdict block.

    def test_a_review_without_a_verdict_block_is_refused(self):
        for body in ("Round 2. Clean.", "", None, self.body(self.head, lenses=False), "```json\nnot json\n```\n",
                     "```\n%s\n```\n" % json.dumps({"head": self.head, "lenses": []}),
                     "```json\n%s\n" % json.dumps({"head": self.head, "lenses": []}),
                     "```json\n%s\n```\n" % json.dumps([{"head": self.head, "lenses": []}]),
                     "    ```json\n    %s\n    ```\n" % json.dumps({"head": self.head, "lenses": []})):
            self.reviews[0]["body"] = body
            self.refused("holds no verdict block: a fenced json block that names \"lenses\"")

    def test_the_block_names_the_commit_of_the_review(self):
        for head in (OTHER, self.head[:12], self.head.upper(), "", None, 7):
            self.reviews[0]["body"] = self.body(head)
            self.refused("has a verdict block whose \"head\" is %s, and the review is of the commit %s" % (head, self.head))

    def test_the_last_block_that_names_lenses_is_the_verdict(self):
        earlier, last = self.body(OTHER, "The round before said:"), self.body(self.head, "Round 2.")
        self.reviews[0]["body"] = earlier + "\n" + last + "\n```json\n{\"note\": \"no verdict\"}\n```\n"
        self.passes()
        self.reviews[0]["body"] = last + "\n" + earlier
        self.refused("has a verdict block whose \"head\" is %s" % OTHER)

    # Nobody edited the verdict.

    def edit(self):
        return self.edits["data"]["repository"]["pullRequest"]["reviews"]["nodes"][0]

    def test_an_edited_verdict_is_refused(self):
        self.edit().update(lastEditedAt="2026-11-19T06:50:00Z", editor={"login": "octocat"})
        self.refused("was edited after it was posted, by octocat. An edited verdict does not count")
        self.edit().update(lastEditedAt="2026-11-19T06:50:00Z", editor=None)
        self.refused("was edited after it was posted. An edited verdict does not count")
        self.edit().update(lastEditedAt=None, editor={"login": "example-review"})
        self.refused("was edited after it was posted, by example-review")

    def test_a_review_the_edits_do_not_know_is_refused(self):
        for edits in ({"data": {"repository": {"pullRequest": {"reviews": {"nodes": []}}}}}, {}, None, [], {"errors": [{"message": "x"}]},
                      {"data": {"repository": {"pullRequest": {"reviews": {"nodes": [{"fullDatabaseId": "1", "lastEditedAt": None, "editor": None}]}}}}}):
            self.edits = edits
            self.refused("is not in the answer of the GraphQL API, so the check cannot tell whether it was edited")

    def test_the_database_id_is_read_as_text_or_number(self):
        self.edit()["fullDatabaseId"] = 5970525038
        self.passes()

    # Who and where.

    def test_the_reviewer_is_never_the_author(self):
        self.pull["user"] = {"login": "example-review[bot]", "id": 175728472, "type": "Bot"}
        self.pull["labels"] = []
        self.refused("the author of the pull request is example-review[bot], the review App. The reviewer is never the author")

    def test_a_checkpoint_branch_of_the_repository_is_refused(self):
        self.pull["head"]["ref"] = "agent/42-disk-check/checkpoint/chronitondb-5.0"
        self.refused("the head branch agent/42-disk-check/checkpoint/chronitondb-5.0 is a checkpoint branch, which never has a pull request")
        # The author of a fork names its branches as it likes.
        self.pull["head"]["repo"]["full_name"] = "someone/product"
        self.passes()


class Command(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.mkdtemp()
        for name in ("pull.json", "events.json", "reviews.json", "edits.json"):
            shutil.copy(os.path.join(HERE, "shapes", name), os.path.join(self.temp, name))
        self.put("app.json", json.dumps(APP))
        self.put("maintainers.json", read(COMMITTERS))

    def tearDown(self):
        shutil.rmtree(self.temp)

    def put(self, name, text):
        with open(os.path.join(self.temp, name), "w", encoding="utf-8") as handle:
            handle.write(text)

    def run_check(self, *args):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = reviewlint.main(list(args))
        return rc, out.getvalue(), err.getvalue()

    def verdict(self, **names):
        args = ["verdict"]
        for option in ("app", "maintainers", "pull", "events", "reviews", "edits"):
            args += ["--" + option, os.path.join(self.temp, names.get(option, option + ".json"))]
        return self.run_check(*args)

    def test_the_command_passes_and_says_which_review(self):
        rc, out, err = self.verdict()
        self.assertEqual((rc, err), (0, ""))
        self.assertTrue(out.endswith("review-verdict passed\n"))
        self.assertIn("the review 5970525038 of example-review[bot] is the verdict on the commit", out)

    def test_the_command_fails_with_its_findings(self):
        self.put("app.json", read(APP_FILE) if reviewlint.app_of(json.loads(read(APP_FILE))) is None else '{"app_id": 0}')
        rc, out, err = self.verdict()
        self.assertEqual((rc, out), (1, "review-verdict failed\n"))
        self.assertIn("the review App is not named yet", err)

    def test_the_pages_of_the_reviews_are_read(self):
        other = dict(json.loads(read("tools/chronitondb/test/reviewlint/shapes/reviews.json"))[0], id=1, submitted_at="2026-11-18T06:00:00Z", commit_id=OTHER)
        with open(os.path.join(self.temp, "reviews.json"), encoding="utf-8") as handle:
            page = handle.read()
        self.put("reviews.json", json.dumps([other]) + "\n" + page)
        self.assertEqual(self.verdict()[0], 0)
        other["submitted_at"] = "2026-11-20T06:00:00Z"
        self.put("reviews.json", page + json.dumps([other]))
        self.assertEqual(self.verdict()[0], 1)

    def test_an_answer_that_cannot_be_read_fails(self):
        for name, text in (("app", "the review App is not named yet"), ("pull", "the head commit or the author of the pull request cannot be read"),
                           ("reviews", "the pull request has no review of"), ("edits", "is not in the answer of the GraphQL API")):
            for content in ("", "not json", None):
                if content is None:
                    names = {name: "none.json"}
                else:
                    self.put("bad.json", content)
                    names = {name: "bad.json"}
                rc, out, err = self.verdict(**names)
                self.assertEqual((rc, out), (1, "review-verdict failed\n"), (name, content))
                self.assertIn(text, err)

    def test_a_pull_request_with_no_verdict_due_passes_and_says_so(self):
        with open(os.path.join(self.temp, "pull.json"), encoding="utf-8") as handle:
            pull = json.load(handle)
        pull["user"] = {"login": "someone", "id": 424242, "type": "User"}
        self.put("pull.json", json.dumps(pull))
        self.put("reviews.json", "[]")
        rc, out, err = self.verdict()
        self.assertEqual((rc, err), (0, ""))
        self.assertEqual(out, "no review verdict is due: the project's automation did not write this pull request and no maintainer has "
                              "accepted it for review with the label triage:accepted\nreview-verdict passed\n")
        # The label a maintainer set, read from the pages of the events.
        pull["labels"] = [{"name": "triage:accepted"}]
        self.put("pull.json", json.dumps(pull))
        event = {"id": 20000000009, "event": "labeled", "label": {"name": "triage:accepted"}, "actor": {"login": MAINTAINER},
                 "created_at": "2026-11-19T08:00:00Z"}
        with open(os.path.join(self.temp, "events.json"), encoding="utf-8") as handle:
            page = handle.read()
        self.put("events.json", page + json.dumps([event]))
        rc, out, err = self.verdict()
        self.assertEqual(rc, 1)
        self.assertIn("the pull request has no review of example-review[bot]", err)
        # A list of maintainers or events that cannot be read accepts nothing and proves nothing.
        self.assertIn("no review verdict is due: the label triage:accepted was set by %s, who is no maintainer" % MAINTAINER.lower(),
                      self.verdict(maintainers="none.json")[1])
        self.assertIn("no event of the pull request says who set it", self.verdict(events="none.json")[2])

    def test_usage(self):
        self.assertEqual(self.run_check()[0], 2)
        self.assertEqual(self.run_check("lint")[0], 2)
        self.assertEqual(self.run_check("verdict", "--app", "x", "--pull", "x", "--reviews", "x", "--edits", "x")[0], 2)
        self.assertEqual(self.run_check("verdict", "--app", "x", "--maintainers", "x", "--pull", "x", "--events", "x", "--reviews", "x",
                                        "--edits", "x", "--more")[0], 2)


class Workflow(unittest.TestCase):
    """The steps of the CI workflow, run here as the shell scripts they
    are, with the environment the workflow gives them and a stand-in for
    gh. The base branch of a small repository holds the checker and the
    file that names the App."""

    REPO = "example/product"

    def setUp(self):
        self.temp = tempfile.mkdtemp()
        self.repo = os.path.join(self.temp, "repo")
        os.makedirs(self.repo)
        self.git("init", "-q")
        for path in ("tools/chronitondb/reviewlint.py", "tools/chronitondb/markdown.py", COMMITTERS):
            self.put(path, read(path))
        self.put(APP_FILE, json.dumps(APP))
        self.commit()
        self.git("update-ref", "refs/remotes/origin/chronitondb-5.0", "HEAD")
        self.answers = os.path.join(self.temp, "answers")
        os.makedirs(self.answers)
        for name in ("pull.json", "events.json", "reviews.json", "edits.json"):
            shutil.copy(os.path.join(HERE, "shapes", name), os.path.join(self.answers, name))
        os.makedirs(os.path.join(self.temp, "bin"))
        gh = os.path.join(self.temp, "bin", "gh")
        with open(gh, "w", encoding="utf-8") as handle:
            handle.write('#!/bin/sh\n[ "$1" = api ] || exit 2\nshift\n[ "$1" = --paginate ] && shift\ncase "$1" in\n'
                         '  repos/example/product/pulls/7) name=pull.json ;;\n'
                         '  "repos/example/product/pulls/7/reviews?per_page=100") name=reviews.json ;;\n'
                         '  "repos/example/product/issues/7/events?per_page=100") name=events.json ;;\n'
                         '  graphql) name=edits.json\n    case "$*" in *"owner=example "*"name=product "*"number=7 "*) ;; *) exit 2 ;; esac ;;\n'
                         '  *) exit 2 ;;\nesac\n[ -f "$ANSWERS/$name" ] || exit 1\ncat "$ANSWERS/$name"\n')
        os.chmod(gh, 0o755)

    def tearDown(self):
        shutil.rmtree(self.temp)

    def git(self, *args):
        return subprocess.run(["git", "-C", self.repo, "-c", "user.name=t", "-c", "user.email=t@example.org", "-c", "commit.gpgsign=false",
                               "-c", "core.hooksPath=/dev/null"] + list(args), check=True, capture_output=True, text=True).stdout.strip()

    def put(self, path, text):
        full = os.path.join(self.repo, path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8") as handle:
            handle.write(text)

    def commit(self):
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "change")

    def steps(self):
        runner = os.path.join(self.temp, "runner")
        shutil.rmtree(runner, ignore_errors=True)
        os.makedirs(runner)
        output = os.path.join(runner, "output")
        context = {"github.event.pull_request.base.ref": "chronitondb-5.0", "github.repository": self.REPO,
                   "github.event.pull_request.number": "7", "github.token": "none"}
        env = dict(os.environ, PATH=os.path.join(self.temp, "bin") + os.pathsep + os.environ.get("PATH", ""),
                   RUNNER_TEMP=runner, GITHUB_OUTPUT=output, ANSWERS=self.answers)
        first = subprocess.run(["bash", "-e", "-c", step_script(WORKFLOW, "The checker from the base branch")], cwd=self.repo,
                               env=dict(env, **step_env(WORKFLOW, "The checker from the base branch", context)),
                               capture_output=True, text=True, check=False)
        with open(output, encoding="utf-8") as handle:
            present = handle.read()
        if first.returncode != 0 or present != "present=yes\n":
            return first.returncode, first.stdout, first.stderr, present
        done = subprocess.run(["bash", "-e", "-c", step_script(WORKFLOW, "Review verdict")], cwd=self.repo,
                              env=dict(env, **step_env(WORKFLOW, "Review verdict", context)), capture_output=True, text=True, check=False)
        return done.returncode, done.stdout, done.stderr, present

    def test_a_verdict_of_the_app_on_the_head_passes(self):
        rc, out, err, _ = self.steps()
        self.assertEqual((rc, err), (0, ""))
        self.assertTrue(out.endswith("review-verdict passed\n"), out)

    def test_the_app_and_the_checker_come_from_the_base_branch(self):
        # The pull request names another App and brings a checker that
        # passes everything. Neither is read.
        self.git("checkout", "-q", "-b", "change")
        self.put(APP_FILE, json.dumps({"app_id": 2, "app_slug": "octocat-review", "bot_user_id": 424242, "automation_user_ids": [1]}))
        self.put("tools/chronitondb/reviewlint.py", "print('review-verdict passed')\n")
        self.put(COMMITTERS, "## Maintainers\n\n| Name | GitHub username |\n|---|---|\n| S | `someone` |\n")
        self.commit()
        with open(os.path.join(self.answers, "reviews.json"), encoding="utf-8") as handle:
            reviews = json.load(handle)
        reviews[0]["user"].update(login="octocat-review[bot]", id=424242)
        with open(os.path.join(self.answers, "reviews.json"), "w", encoding="utf-8") as handle:
            json.dump(reviews, handle)
        rc, out, err, _ = self.steps()
        self.assertEqual(rc, 1)
        self.assertIn("the pull request has no review of example-review[bot], the review App", err)

    def test_the_placeholders_on_the_base_fail(self):
        self.put(APP_FILE, read(APP_FILE) if reviewlint.app_of(json.loads(read(APP_FILE))) is None else '{"app_id": 0}')
        self.commit()
        self.git("update-ref", "refs/remotes/origin/chronitondb-5.0", "HEAD")
        rc, out, err, _ = self.steps()
        self.assertEqual((rc, out), (1, "review-verdict failed\n"))
        self.assertIn("the review App is not named yet: tools/chronitondb/review-app.json on the line holds a placeholder", err)

    def test_before_the_check_is_on_the_line_it_says_so_and_passes(self):
        for path in ("tools/chronitondb/reviewlint.py", "tools/chronitondb/markdown.py", APP_FILE, COMMITTERS):
            self.git("checkout", "-q", "--detach", "HEAD")
            self.git("rm", "-q", path)
            self.commit()
            self.git("update-ref", "refs/remotes/origin/chronitondb-5.0", "HEAD")
            rc, out, err, present = self.steps()
            self.assertEqual((rc, present), (0, "present=no\n"))
            self.assertIn("%s is not on chronitondb-5.0 yet, so there is no checker to run. The check starts once it is merged." % path, out)
            self.git("reset", "-q", "--hard", "HEAD~1")

    def test_an_answer_the_api_does_not_give_fails(self):
        for name, text in (("pull.json", "the head commit or the author of the pull request cannot be read"),
                           ("reviews.json", "the pull request has no review of"), ("edits.json", "is not in the answer of the GraphQL API")):
            os.rename(os.path.join(self.answers, name), os.path.join(self.answers, name + ".away"))
            rc, out, err, _ = self.steps()
            self.assertEqual(rc, 1, name)
            self.assertIn(text, err)
            os.rename(os.path.join(self.answers, name + ".away"), os.path.join(self.answers, name))

    def test_a_label_counts_only_from_a_maintainer_of_the_base_branch(self):
        with open(os.path.join(self.answers, "pull.json"), encoding="utf-8") as handle:
            pull = json.load(handle)
        pull["user"] = {"login": "someone", "id": 424242, "type": "User"}
        pull["labels"] = [{"name": "triage:accepted"}]
        with open(os.path.join(self.answers, "pull.json"), "w", encoding="utf-8") as handle:
            json.dump(pull, handle)
        with open(os.path.join(self.answers, "reviews.json"), "w", encoding="utf-8") as handle:
            handle.write("[]")
        # The pull request adds its author to the maintainers. The list of the base branch is read.
        self.git("checkout", "-q", "-b", "change")
        self.put(COMMITTERS, "## Maintainers\n\n| Name | GitHub username |\n|---|---|\n| S | `someone` |\n")
        self.commit()
        for login, due in (("someone", False), (MAINTAINER, True)):
            with open(os.path.join(self.answers, "events.json"), "w", encoding="utf-8") as handle:
                json.dump([{"id": 20000000009, "event": "labeled", "label": {"name": "triage:accepted"}, "actor": {"login": login},
                            "created_at": "2026-11-19T08:00:00Z"}], handle)
            rc, out, err, _ = self.steps()
            if due:
                self.assertEqual(rc, 1)
                self.assertIn("the pull request has no review of example-review[bot]", err)
            else:
                self.assertEqual((rc, err), (0, ""))
                self.assertIn("no review verdict is due: the label triage:accepted was set by someone, who is no maintainer", out)

    def test_the_workflow_keeps_to_the_rules_of_the_others(self):
        text = read(WORKFLOW)
        self.assertIn("\non:\n  pull_request:\n    branches:\n      - 'chronitondb-*'\n    types: [opened, reopened, synchronize, labeled, unlabeled]\n"
                      "  pull_request_review:\n    types: [submitted, edited, dismissed]\n", text)
        self.assertIn("\npermissions:\n  contents: read\n  pull-requests: read\n\njobs:\n  review-verdict:\n"
                      "    if: startsWith(github.event.pull_request.base.ref, 'chronitondb-')\n", text)
        self.assertEqual(text.count("persist-credentials: false"), text.count("uses: actions/checkout@"))
        for word in ("pull_request_target", "workflow_run", "secrets.", ": write"):
            self.assertNotIn(word, text)
        for line in text.split("\n"):
            if "uses:" in line:
                self.assertRegex(line, r"uses: [a-z-]+/[a-z-]+@[0-9a-f]{40} # v[0-9.]+$")
        # No value of the event is written into a script.
        for name in ("The checker from the base branch", "Review verdict"):
            self.assertNotIn("${{", step_script(WORKFLOW, name))
        self.assertIn('git show "origin/$BASE:$file" > "$dir/${file##*/}"', text)
        self.assertNotIn("tools/chronitondb/reviewlint.py verdict", text)
        self.assertIn("  reviewlint-tests:\n    if: github.event_name == 'pull_request'\n", text)
        self.assertIn("python3 -m unittest discover -s tools/chronitondb/test/reviewlint -v", text)


if __name__ == "__main__":
    unittest.main()
