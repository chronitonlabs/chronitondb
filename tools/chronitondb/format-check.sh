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
# Format check for ChronitonDB code: Google Java Style, enforced with
# google-java-format on Java files under org/chronitondb, never on Apache
# code.
#
#   tools/chronitondb/format-check.sh [FILE...]        report the files that are not formatted
#   tools/chronitondb/format-check.sh                  same, on the staged files
#   tools/chronitondb/format-check.sh --base REF       same, on the files changed since the merge base with REF
#   tools/chronitondb/format-check.sh --fix [FILE...]  format the files in place (staged files when none)
#   tools/chronitondb/format-check.sh --self-test      run the fixtures under tools/chronitondb/test/format
#
# Production and test files alike, every unformatted file blocks: there is
# no legitimate exception to formatting. Only paths matching
# org/chronitondb/**/*.java are kept, the rest are ignored without a word.
#
# Tool: the google-java-format all-deps jar pinned below, downloaded into
# build/chronitondb-shape on first use and checked against its sha256.
# Nothing is added to lib/ or build.xml and nothing is shipped. It needs a
# Java 21 JDK (not a JRE) because it parses with jdk.compiler.
#
# Output: one line per file that needs formatting
#   ERROR path GoogleJavaFormat: not in Google Java Style, run tools/chronitondb/format-check.sh --fix path
# then one summary line. Exit 0 when every file is formatted, 1 when one is
# not, 2 when the check itself could not run.
set -u

tool=format-check
# shellcheck source=lib.sh
. "$(dirname "${BASH_SOURCE[0]}")/lib.sh"

# The pin, the same release on both lines so a change carried from 5.0 to 6.0
# keeps its formatting. google-java-format 1.29.0 and later need a Java 21 JDK
# to run, and still format code for any earlier Java level. The 5.0 line
# builds on Java 17, so the formatter runs on its own JDK: SHAPE_GJF_JAVA_HOME,
# or JAVA_HOME when that is already 21. The sha256 is the digest GitHub
# publishes for the release asset, equal to the .sha256 file Maven Central
# serves for the same artefact (both read on 2026-10-30).
gjf_version="1.37.0"
gjf_url="https://github.com/google/google-java-format/releases/download/v1.37.0/google-java-format-1.37.0-all-deps.jar"
gjf_sha256="834b2a0c38cb774953322a84b5ca3f2f40dd3156650b3cd44d3b744345962f7a"
gjf_java_bin="${SHAPE_GJF_JAVA_HOME:+$SHAPE_GJF_JAVA_HOME/bin/java}"
gjf_java_bin="${gjf_java_bin:-$java_bin}"

# google-java-format reads javac internals, these exports let it on every
# JDK from 21 on. SHAPE_GJF_JAR points at a jar already on disk instead.
gjf_java_opts="--add-exports=jdk.compiler/com.sun.tools.javac.api=ALL-UNNAMED
--add-exports=jdk.compiler/com.sun.tools.javac.code=ALL-UNNAMED
--add-exports=jdk.compiler/com.sun.tools.javac.file=ALL-UNNAMED
--add-exports=jdk.compiler/com.sun.tools.javac.parser=ALL-UNNAMED
--add-exports=jdk.compiler/com.sun.tools.javac.tree=ALL-UNNAMED
--add-exports=jdk.compiler/com.sun.tools.javac.util=ALL-UNNAMED"

gjf_jar()
{
  local jar="${SHAPE_GJF_JAR:-$work/google-java-format-$gjf_version-all-deps.jar}"
  if [ -n "${SHAPE_GJF_JAR:-}" ]
  then
    [ -f "$jar" ] || die "SHAPE_GJF_JAR=$jar is not a file"
  else
    download_verified "$gjf_url" "$gjf_sha256" "$jar"
  fi
  printf '%s' "$jar"
}

# run_gjf LIST ARGS...: google-java-format over the files listed in LIST.
# Prints its stdout, dies on anything written to stderr (a parse error, a
# missing JDK), returns its exit code otherwise.
run_gjf()
{
  local list="$1" jar err rc major
  shift
  major="$("$gjf_java_bin" -XshowSettings:properties -version 2>&1 \
    | sed -n -E 's/^ *java\.specification\.version = ([0-9]+).*/\1/p')"
  if [ "${major:-0}" -lt 21 ]
  then
    die "google-java-format $gjf_version needs Java 21 or later, $gjf_java_bin is Java ${major:-unknown}. Set SHAPE_GJF_JAVA_HOME to a Java 21 JDK"
  fi
  jar="$(gjf_jar)" || exit 2
  err="$work/gjf-stderr.txt"
  # shellcheck disable=SC2086
  xargs "$gjf_java_bin" $gjf_java_opts -jar "$jar" "$@" < "$list" 2> "$err"
  rc=$?
  if [ -s "$err" ]
  then
    cat "$err" >&2
    die "google-java-format failed (exit $rc)"
  fi
  return "$rc"
}

# Reads the selected files from stdin, reports the ones not formatted.
check_files()
{
  local list="$work/format-files.txt" out="$work/format-output.txt" n_files n_bad path
  mkdir -p "$work" || die "cannot create $(display "$work")"
  cat > "$list"
  n_files="$(grep -c . "$list")"
  if [ "$n_files" -eq 0 ]
  then
    printf '%s: no org/chronitondb Java files to check\n' "$tool"
    return 0
  fi
  run_gjf "$list" --dry-run --set-exit-if-changed > "$out"
  n_bad=0
  while IFS= read -r path
  do
    [ -n "$path" ] || continue
    printf 'ERROR %s GoogleJavaFormat: not in Google Java Style, run tools/chronitondb/format-check.sh --fix %s\n' \
      "$(display "$path")" "$(display "$path")"
    n_bad=$((n_bad + 1))
  done < "$out"
  printf '%s: %s file(s) not in Google Java Style, %s file(s) checked\n' "$tool" "$n_bad" "$n_files"
  [ "$n_bad" -eq 0 ]
}

# Reads the selected files from stdin, formats them in place.
fix_files()
{
  local list="$work/format-files.txt" n_files path
  mkdir -p "$work" || die "cannot create $(display "$work")"
  cat > "$list"
  n_files="$(grep -c . "$list")"
  if [ "$n_files" -eq 0 ]
  then
    printf '%s: no org/chronitondb Java files to format\n' "$tool"
    return 0
  fi
  run_gjf "$list" --replace || die "google-java-format --replace failed"
  while IFS= read -r path
  do
    printf 'formatted %s\n' "$(display "$path")"
  done < "$list"
}

# Stages the format fixtures as production and as test files, checks that
# the unformatted one is reported in both places, the formatted one in
# neither, that --fix repairs them and that fixtures given by their own path
# are skipped.
self_test()
{
  local stage out rc failed=0
  stage="$work/format-selftest"
  rm -rf "$stage"
  mkdir -p "$stage/src/java/org/chronitondb/shape" "$stage/test/unit/org/chronitondb/shape" \
    || die "cannot create $(display "$stage")"
  cp "$fixtures/format/"*.java "$stage/src/java/org/chronitondb/shape/"
  cp "$fixtures/format/Unformatted.java" "$stage/test/unit/org/chronitondb/shape/"
  out="$work/format-selftest-output.txt"

  find "$stage" -name '*.java' -type f | sort | run_on_list > "$out" 2>&1
  rc=$?
  cat "$out"
  if [ "$rc" -ne 1 ]
  then
    printf 'self-test: FAIL exit %s on the fixtures, expected 1\n' "$rc"
    failed=$((failed + 1))
  fi
  if ! grep -q '^ERROR build/chronitondb-shape/format-selftest/src/java/org/chronitondb/shape/Unformatted.java ' "$out"
  then
    printf 'self-test: FAIL the unformatted production fixture was not reported\n'
    failed=$((failed + 1))
  fi
  if ! grep -q '^ERROR build/chronitondb-shape/format-selftest/test/unit/org/chronitondb/shape/Unformatted.java ' "$out"
  then
    printf 'self-test: FAIL the unformatted test fixture was not reported, formatting blocks tests too\n'
    failed=$((failed + 1))
  fi
  if grep 'Formatted.java ' "$out" | grep -q -v Unformatted
  then
    printf 'self-test: FAIL the formatted fixture was reported\n'
    failed=$((failed + 1))
  fi

  find "$stage" -name '*.java' -type f | sort | run_on_list --fix > "$out" 2>&1
  rc=$?
  if [ "$rc" -ne 0 ]
  then
    cat "$out"
    printf 'self-test: FAIL --fix exit %s, expected 0\n' "$rc"
    failed=$((failed + 1))
  fi
  find "$stage" -name '*.java' -type f | sort | run_on_list > "$out" 2>&1
  rc=$?
  if [ "$rc" -ne 0 ] || grep -q '^ERROR ' "$out"
  then
    cat "$out"
    printf 'self-test: FAIL exit %s after --fix, expected 0 without findings\n' "$rc"
    failed=$((failed + 1))
  fi

  find "$fixtures/format" -name '*.java' -type f | sort | run_on_list > "$out" 2>&1
  rc=$?
  if [ "$rc" -ne 0 ] || grep -q '^ERROR ' "$out"
  then
    cat "$out"
    printf 'self-test: FAIL fixtures given by their own path exit %s, expected to be skipped\n' "$rc"
    failed=$((failed + 1))
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
    files_for base "$2" | check_files
    ;;
  --fix)
    shift
    if [ $# -gt 0 ]
    then
      files_for files "$@" | fix_files
    else
      files_for staged | fix_files
    fi
    ;;
  --help|-h)
    usage "Format check"
    ;;
  --*)
    die "unknown option $1"
    ;;
  "")
    files_for staged | check_files
    ;;
  *)
    files_for files "$@" | check_files
    ;;
esac
