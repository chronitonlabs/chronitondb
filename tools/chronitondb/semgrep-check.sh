#!/usr/bin/env bash
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
#
# Semgrep check for ChronitonDB: the house rules in tools/chronitondb/semgrep.
#
#   tools/chronitondb/semgrep-check.sh [FILE...]     scan these files
#   tools/chronitondb/semgrep-check.sh               scan the staged files
#   tools/chronitondb/semgrep-check.sh --base REF    scan the files changed since the merge base with REF,
#                                                    without the findings already on the merge base
#   tools/chronitondb/semgrep-check.sh --self-test   run the rules on the fixtures under tools/chronitondb/test/semgrep
#
# Each rule file says which paths it covers: the banned APIs on
# src/java/org/chronitondb, non-ASCII identifiers on any org/chronitondb
# path, process starts and ObjectInputStream on every Java file, bidi
# control characters on every file. The fixtures under tools/chronitondb/test
# are never scanned as changes. Semgrep runs with --disable-nosem, so a
# "nosemgrep" comment hides nothing.
#
# Tool: the Semgrep CE container image pinned by digest below, run with
# docker, without network, as the calling user. Nothing is installed and
# nothing is shipped. jq formats the output.
#
# Output: one line per finding
#   ERROR path:line:col rule: message
# then one summary line. Exit 0 without findings, 1 on a finding, 2 when the
# check itself could not run.
set -u

tool=semgrep-check
# shellcheck source=lib.sh
. "$(dirname "${BASH_SOURCE[0]}")/lib.sh"

# The pin. The digest is the multi-platform index of semgrep/semgrep:1.182.1
# on Docker Hub, read with `docker buildx imagetools inspect` on 2026-10-30.
# The tag is for the reader, docker pulls by the digest.
semgrep_image="semgrep/semgrep:1.182.1@sha256:451b3d875c00dac7ed5db5293e584a07de11449a409c10b3c2d2652f429630b6"
rules="$here/semgrep"
semgrep_work="$work/semgrep"

# run_semgrep MOUNT WORKDIR ARGS...: semgrep in the pinned image, with MOUNT
# (a host directory) at /src and the rules read only at /rules.
run_semgrep()
{
  local mount="$1" workdir="$2"
  shift 2
  command -v docker >/dev/null 2>&1 || die "docker is needed to run the pinned Semgrep image"
  docker run --rm --network none --user "$(id -u):$(id -g)" \
    -e HOME=/tmp -e SEMGREP_ENABLE_VERSION_CHECK=0 -e SEMGREP_SEND_METRICS=off \
    -e GIT_CONFIG_COUNT=1 -e GIT_CONFIG_KEY_0=safe.directory -e GIT_CONFIG_VALUE_0=/src \
    -v "$mount:/src" -v "$rules:/rules:ro" -w "$workdir" \
    "$semgrep_image" semgrep "$@"
}

# Reads repository relative paths from stdin. Keeps the files that exist,
# drops the fixtures under tools/chronitondb/test, removes duplicates.
select_targets()
{
  local path
  while IFS= read -r path
  do
    [ -n "$path" ] || continue
    case "$path" in
      tools/chronitondb/test/*) continue ;;
    esac
    [ -f "$root/$path" ] || continue
    printf '%s\n' "$path"
  done | awk '!seen[$0]++'
}

# relative PATH: the path relative to the repository, or nothing when it is
# outside it.
relative()
{
  local abs
  abs="$(absolute "$1")"
  case "$abs" in
    "$root"/*) printf '%s' "${abs#"$root"/}" ;;
  esac
}

# scan BASELINE: scans the targets on stdin, all of them repository
# relative. BASELINE is a commit whose findings are not reported, or empty.
scan()
{
  local baseline="$1" list="$semgrep_work/targets.txt" out="$semgrep_work/results.json" n_files n_found rc path
  local targets=()
  mkdir -p "$semgrep_work" || die "cannot create $(display "$semgrep_work")"
  command -v jq >/dev/null 2>&1 || die "jq is needed to format the Semgrep output"
  select_targets > "$list"
  n_files="$(grep -c . "$list")"
  if [ "$n_files" -eq 0 ]
  then
    printf '%s: no files to scan\n' "$tool"
    return 0
  fi
  while IFS= read -r path
  do
    targets+=("$path")
  done < "$list"
  if [ -n "$baseline" ]
  then
    run_semgrep "$root" /src scan --metrics=off --disable-nosem --error --quiet --json \
      --config /rules --baseline-commit "$baseline" "${targets[@]}" > "$out"
  else
    run_semgrep "$root" /src scan --metrics=off --disable-nosem --error --quiet --json \
      --config /rules "${targets[@]}" > "$out"
  fi
  rc=$?
  if [ "$rc" -gt 1 ] || ! jq -e . "$out" >/dev/null 2>&1
  then
    die "semgrep failed (exit $rc)"
  fi
  jq -r '.errors[]? | "semgrep: \(.type | if type == "array" then .[0] else (. // "error") end): \(.message // "" | gsub("\n"; " "))"' "$out" >&2
  # The line itself is not printed: a bidi control character in it would
  # reorder the terminal display of the report that is meant to expose it.
  jq -r '.results[] | "ERROR \(.path):\(.start.line):\(.start.col) \(.check_id | split(".") | last): \(.extra.message | gsub("\n"; " "))"' "$out"
  n_found="$(jq '.results | length' "$out")"
  printf '%s: %s finding(s), %s file(s) scanned\n' "$tool" "$n_found" "$n_files"
  [ "$n_found" -eq 0 ]
}

# Writes the bidi fixture. It is generated, so that no committed file
# carries a bidi control character: RIGHT-TO-LEFT OVERRIDE (U+202E) and
# LEFT-TO-RIGHT ISOLATE (U+2066) on line 2, RIGHT-TO-LEFT MARK (U+200F) on
# line 6, in UTF-8.
write_bidi_fixture()
{
  printf '%s\n' \
    '// ruleid: chronitondb-bidi-control-character' \
    "String access = \"user$(printf '\342\200\256') $(printf '\342\201\246')// admin\";" \
    '// ok: chronitondb-bidi-control-character' \
    'String plain = "user";' \
    '# ruleid: chronitondb-bidi-control-character' \
    "echo \"$(printf '\342\200\217')\"" > "$1"
}

# Runs every rule on its fixture with semgrep --test (each "ruleid" line
# must be reported, each "ok" line must not), then checks the path scoping
# that --test ignores: the banned API fixture staged as production, test and
# Apache code, the non-ASCII fixture as test and Apache code.
self_test()
{
  local stage out rc failed=0 expected actual
  stage="$semgrep_work/selftest"
  rm -rf "$stage"
  mkdir -p "$stage/fixtures" \
    "$stage/scope/src/java/org/chronitondb/selftest" \
    "$stage/scope/test/unit/org/chronitondb/selftest" \
    "$stage/scope/src/java/org/apache/cassandra/selftest" \
    || die "cannot create $(display "$stage")"
  cp "$fixtures/semgrep/"* "$stage/fixtures/"
  write_bidi_fixture "$stage/fixtures/bidi.txt"
  out="$semgrep_work/selftest-output.txt"

  run_semgrep "$stage" /src --test --metrics=off --config /rules /src/fixtures > "$out" 2>&1
  rc=$?
  if [ "$rc" -ne 0 ] || ! grep -q 'All tests passed' "$out"
  then
    cat "$out"
    printf 'self-test: FAIL semgrep --test exit %s, a rule missed a ruleid line or hit an ok line\n' "$rc"
    failed=$((failed + 1))
  else
    grep -E 'tests? passed' "$out"
  fi

  cp "$fixtures/semgrep/banned-apis.java" "$stage/scope/src/java/org/chronitondb/selftest/BannedApis.java"
  cp "$fixtures/semgrep/banned-apis.java" "$stage/scope/test/unit/org/chronitondb/selftest/BannedApisTest.java"
  cp "$fixtures/semgrep/banned-apis.java" "$stage/scope/src/java/org/apache/cassandra/selftest/BannedApis.java"
  cp "$fixtures/semgrep/non-ascii-identifiers.java" "$stage/scope/test/unit/org/chronitondb/selftest/NonAscii.java"
  cp "$fixtures/semgrep/non-ascii-identifiers.java" "$stage/scope/src/java/org/apache/cassandra/selftest/NonAscii.java"
  run_semgrep "$stage/scope" /src scan --metrics=off --disable-nosem --quiet --json --config /rules \
    src/java/org/chronitondb/selftest/BannedApis.java \
    test/unit/org/chronitondb/selftest/BannedApisTest.java \
    src/java/org/apache/cassandra/selftest/BannedApis.java \
    test/unit/org/chronitondb/selftest/NonAscii.java \
    src/java/org/apache/cassandra/selftest/NonAscii.java > "$out"
  rc=$?
  expected="src/java/org/chronitondb/selftest/BannedApis.java test/unit/org/chronitondb/selftest/NonAscii.java"
  actual="$(jq -r '[.results[].path] | unique | join(" ")' "$out" 2>/dev/null)"
  if [ "$rc" -ne 0 ] || [ "$actual" != "$expected" ]
  then
    printf 'self-test: FAIL path scoping, findings in [%s], expected in [%s] (exit %s)\n' "$actual" "$expected" "$rc"
    failed=$((failed + 1))
  else
    printf 'self-test: path scoping as expected, findings only in %s\n' "$expected"
  fi

  if [ "$failed" -eq 0 ]
  then
    printf 'self-test: PASS\n'
    return 0
  fi
  printf 'self-test: %s check(s) failed\n' "$failed"
  return 1
}

case "${1:-}" in
  --self-test)
    self_test
    ;;
  --base)
    [ -n "${2:-}" ] || die "--base needs a ref"
    base="$(git -C "$root" merge-base "$2" HEAD)" || die "no merge base between $2 and HEAD"
    git -C "$root" diff --name-only --diff-filter=ACMR "$base" HEAD | scan "$base"
    ;;
  --help|-h)
    usage "Semgrep check"
    ;;
  --*)
    die "unknown option $1"
    ;;
  "")
    git -C "$root" diff --cached --name-only --diff-filter=ACMR | scan ""
    ;;
  *)
    for path in "$@"
    do
      rel="$(relative "$path")"
      [ -n "$rel" ] || die "$path is outside the repository"
      printf '%s\n' "$rel"
    done | scan ""
    ;;
esac
