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
# Shape check for ChronitonDB code: the measured limits in
# docs/process/conventions.md on Java files under org/chronitondb, never on
# Apache code.
#
#   tools/chronitondb/shape-check.sh [FILE...]   check these files
#   tools/chronitondb/shape-check.sh             check the staged files
#   tools/chronitondb/shape-check.sh --base REF  check the files changed since the merge base with REF
#   tools/chronitondb/shape-check.sh --self-test run the fixtures under tools/chronitondb/test
#
# Only paths matching org/chronitondb/**/*.java are kept, the rest are
# ignored without a word. A file under a test/ directory (test/unit,
# test/distributed, test/microbench, test/burn) gets the test limits and
# every finding is a warning. Every other file is production code and every
# finding blocks.
#
# Tools: checkstyle from the build's own test classpath (build/test/lib/jars,
# filled by `ant resolver-retrieve-build` or any build) and PMD, downloaded
# into build/chronitondb-shape on first use and checked against the sha256
# pinned in pmd-ruleset.xml. Nothing is added to lib/ or build.xml and
# nothing is shipped.
#
# Output: one line per finding
#   SEVERITY path:line Rule value=N limit=M: message
# then one summary line. Exit 0 when nothing blocks (test warnings allowed),
# 1 on a production finding, 2 when the check itself could not run.
set -u

tool=shape-check
# shellcheck source=lib.sh
. "$(dirname "${BASH_SOURCE[0]}")/lib.sh"

ruleset="$here/pmd-ruleset.xml"
prod_config="$here/checkstyle-shape.xml"
test_config="$here/checkstyle-shape-tests.xml"
findings=""

# One setting from the key = value block in pmd-ruleset.xml.
setting()
{
  local value
  value="$(sed -n -E "s/^[[:space:]]*$1[[:space:]]*=[[:space:]]*([^[:space:]]+)[[:space:]]*$/\1/p" "$ruleset" | head -n 1)"
  [ -n "$value" ] || die "$1 is not set in $(display "$ruleset")"
  printf '%s' "$value"
}

severity_of()
{
  if [ "$(classify "$1")" = test ]
  then
    printf 'WARN'
  else
    printf 'ERROR'
  fi
}

checkstyle_classpath()
{
  local jars="$root/build/test/lib/jars"
  ls "$jars"/checkstyle-*.jar >/dev/null 2>&1 \
    || die "no checkstyle jar under $(display "$jars"), run 'ant resolver-retrieve-build' first"
  printf '%s/*' "$jars"
}

# Prints the PMD home, downloading and unpacking the pinned release into
# build/ when it is not there yet. SHAPE_PMD_HOME points at an unpacked
# release instead.
pmd_home()
{
  local version home
  version="$(setting pmd.version)"
  home="${SHAPE_PMD_HOME:-$work/pmd-bin-$version}"
  if [ -x "$home/bin/pmd" ]
  then
    printf '%s' "$home"
    return 0
  fi
  [ -z "${SHAPE_PMD_HOME:-}" ] || die "SHAPE_PMD_HOME=$SHAPE_PMD_HOME has no bin/pmd"
  download_verified "$(setting pmd.url)" "$(setting pmd.sha256)" "$work/pmd-dist-$version-bin.zip"
  rm -rf "$home"
  unzip -q -o "$work/pmd-dist-$version-bin.zip" -d "$work" || die "cannot unpack PMD $version"
  [ -x "$home/bin/pmd" ] || die "unpacked PMD has no bin/pmd under $(display "$home")"
  printf '%s' "$home"
}

# Prints "value limit" read out of a checkstyle or PMD message, "? ?" when
# the message has another shape.
value_and_limit()
{
  local msg="$1" is_max='is ([0-9,]+)( lines)? \(max allowed is ([0-9,]+)\)'
  local params='More than ([0-9]+) parameters \(found ([0-9]+)\)'
  local cognitive='cognitive complexity of ([0-9]+), current threshold is ([0-9]+)'
  local cpd='\(([0-9]+) tokens, minimum ([0-9]+)\)'
  if [[ $msg =~ $is_max ]]
  then
    printf '%s %s' "${BASH_REMATCH[1]//,/}" "${BASH_REMATCH[3]//,/}"
  elif [[ $msg =~ $params ]]
  then
    printf '%s %s' "${BASH_REMATCH[2]}" "${BASH_REMATCH[1]}"
  elif [[ $msg =~ $cognitive ]]
  then
    # PMD reports at or above reportLevel, the limit is one below it.
    printf '%s %s' "${BASH_REMATCH[1]}" "$((BASH_REMATCH[2] - 1))"
  elif [[ $msg =~ $cpd ]]
  then
    printf '%s %s' "${BASH_REMATCH[1]}" "${BASH_REMATCH[2]}"
  else
    printf '? ?'
  fi
}

# Appends one finding line to the findings file.
emit()
{
  local file="$1" line="$2" rule="$3" msg="$4" value limit
  read -r value limit <<EOF
$(value_and_limit "$msg")
EOF
  printf '%s %s:%s %s value=%s limit=%s: %s\n' \
    "$(severity_of "$file")" "$(display "$file")" "$line" "$rule" "$value" "$limit" "$msg" >> "$findings"
}

# Runs checkstyle with one config over the files listed in $2 (one per line).
run_checkstyle()
{
  local config="$1" list="$2" out rc sev file line msg rule parsed="$work/checkstyle-parsed.txt"
  [ -s "$list" ] || return 0
  out="$(xargs "$java_bin" -Duser.language=en -Duser.country=US \
    -cp "$(checkstyle_classpath)" com.puppycrawl.tools.checkstyle.Main \
    -c "$config" -f plain < "$list" 2>&1)"
  rc=$?
  if ! printf '%s\n' "$out" | grep -q '^Audit done\.'
  then
    printf '%s\n' "$out" >&2
    die "checkstyle did not finish (exit $rc) with $(display "$config")"
  fi
  printf '%s\n' "$out" \
    | sed -n -E 's/^\[(ERROR|WARN)\] (.*):([0-9]+)(:[0-9]+)?: (.*) \[([A-Za-z]+)\]$/\1|\2|\3|\5|\6/p' > "$parsed"
  while IFS='|' read -r sev file line msg rule
  do
    [ -n "$file" ] || continue
    emit "$file" "$line" "$rule" "$msg"
  done < "$parsed"
}

# PMD cognitive complexity over the files listed in $1.
run_pmd()
{
  local list="$1" home out rc file line rule msg parsed="$work/pmd-parsed.txt"
  [ -s "$list" ] || return 0
  home="$(pmd_home)" || exit 2
  out="$("$home/bin/pmd" check --file-list "$list" -R "$ruleset" -f text \
    --no-cache --no-progress --no-fail-on-violation 2>&1)"
  rc=$?
  if [ "$rc" -ne 0 ]
  then
    printf '%s\n' "$out" >&2
    die "pmd check failed (exit $rc)"
  fi
  printf '%s\n' "$out" \
    | sed -n -E 's/^(.*):([0-9]+):[[:space:]]+([A-Za-z]+):[[:space:]]+(.*)$/\1|\2|\3|\4/p' > "$parsed"
  while IFS='|' read -r file line rule msg
  do
    [ -n "$file" ] || continue
    emit "$file" "$line" "$rule" "$msg"
  done < "$parsed"
}

# Turns the text report of pmd cpd into one record per occurrence:
# tokens|lines|file|line|the other occurrences
cpd_records()
{
  awk -v root="$root/" '
    function flush(   i, j, f, others, sep)
    {
      for (i = 1; i <= n; i++)
      {
        others = ""
        sep = ""
        for (j = 1; j <= n; j++)
        {
          if (j == i) continue
          f = files[j]
          sub("^" root, "", f)
          others = others sep f ":" lines[j]
          sep = ", "
        }
        print tokens "|" span "|" files[i] "|" lines[i] "|" others
      }
      n = 0
    }
    /^Found a [0-9]+ line \([0-9]+ tokens\) duplication/ {
      if (n > 0) flush()
      span = $3
      tokens = $5
      sub("\\(", "", tokens)
      n = 0
      next
    }
    /^Starting at line [0-9]+ of / {
      n++
      lines[n] = $4
      files[n] = $0
      sub("^Starting at line [0-9]+ of ", "", files[n])
      next
    }
    { if (n > 0) flush() }
    END { if (n > 0) flush() }'
}

# Duplication over the given files plus every org/chronitondb Java file in
# the tree, reported only where a given file takes part.
run_cpd()
{
  local list="$1" home corpus out rc tokens span file line others minimum dir
  local parsed="$work/cpd-parsed.txt"
  [ -s "$list" ] || return 0
  home="$(pmd_home)" || exit 2
  minimum="$(setting cpd.minimum-tokens)"
  corpus="$work/cpd-corpus.txt"
  {
    cat "$list"
    for dir in "$root/src" "$root/test"
    do
      [ -d "$dir" ] && find "$dir" -path '*/org/chronitondb/*' -name '*.java' -type f
    done
  } | awk '!seen[$0]++' > "$corpus"
  out="$("$home/bin/pmd" cpd --file-list "$corpus" --language java \
    --minimum-tokens "$minimum" --format text --no-fail-on-violation 2>&1)"
  rc=$?
  if [ "$rc" -ne 0 ]
  then
    printf '%s\n' "$out" >&2
    die "pmd cpd failed (exit $rc)"
  fi
  printf '%s\n' "$out" | cpd_records > "$parsed"
  while IFS='|' read -r tokens span file line others
  do
    [ -n "$file" ] || continue
    grep -q -x -F "$file" "$list" || continue
    emit "$file" "$line" "CPD" \
      "duplicated block of $span lines ($tokens tokens, minimum $minimum), also at $others"
  done < "$parsed"
}

# Reads the selected files from stdin, runs every tool, prints the findings.
check_files()
{
  local prod_list test_list all_list path n_prod n_test n_err n_warn
  prod_list="$work/prod-files.txt"
  test_list="$work/test-files.txt"
  all_list="$work/all-files.txt"
  mkdir -p "$work" || die "cannot create $(display "$work")"
  : > "$prod_list"
  : > "$test_list"
  cat > "$all_list"
  while IFS= read -r path
  do
    [ -n "$path" ] || continue
    if [ "$(classify "$path")" = test ]
    then
      printf '%s\n' "$path" >> "$test_list"
    else
      printf '%s\n' "$path" >> "$prod_list"
    fi
  done < "$all_list"
  n_prod="$(grep -c . "$prod_list")"
  n_test="$(grep -c . "$test_list")"
  if [ "$((n_prod + n_test))" -eq 0 ]
  then
    printf '%s: no org/chronitondb Java files to check\n' "$tool"
    return 0
  fi
  findings="$work/findings.txt"
  : > "$findings"
  run_checkstyle "$prod_config" "$prod_list"
  run_checkstyle "$test_config" "$test_list"
  run_pmd "$all_list"
  run_cpd "$all_list"
  sort -u "$findings"
  n_err="$(grep -c '^ERROR ' "$findings")"
  n_warn="$(grep -c '^WARN ' "$findings")"
  printf '%s: %s production finding(s) that block, %s test warning(s), %s production and %s test file(s) checked\n' \
    "$tool" "$n_err" "$n_warn" "$n_prod" "$n_test"
  [ "$n_err" -eq 0 ]
}

# Copies the fixtures into a staging tree shaped like the repository, runs the
# check on them and compares the findings with tools/chronitondb/test/expected.txt.
self_test()
{
  local stage out expected actual rc failed=0
  stage="$work/selftest"
  rm -rf "$stage"
  mkdir -p "$stage/src/java" "$stage/test/unit" || die "cannot create $(display "$stage")"
  cp -R "$fixtures/src/." "$stage/src/java/"
  cp -R "$fixtures/test/." "$stage/test/unit/"
  out="$work/selftest-output.txt"
  expected="$work/selftest-expected.txt"
  actual="$work/selftest-actual.txt"

  find "$stage" -name '*.java' -type f | sort | run_on_list > "$out" 2>&1
  rc=$?
  cat "$out"
  if [ "$rc" -ne 1 ]
  then
    printf 'self-test: FAIL all fixtures exit %s, expected 1\n' "$rc"
    failed=$((failed + 1))
  fi
  grep -v -E '^[[:space:]]*(#|$)' "$fixtures/expected.txt" | sort -u > "$expected"
  {
    sed -n -E "s#^(ERROR|WARN) build/chronitondb-shape/selftest/([^:]+):[0-9]+(:[0-9]+)? ([A-Za-z]+) .*#\2 \1 \4#p" "$out"
    find "$stage" -name '*.java' -type f | while IFS= read -r path
    do
      path="${path#"$stage"/}"
      grep -q -F "build/chronitondb-shape/selftest/$path:" "$out" || printf '%s none\n' "$path"
    done
  } | sort -u > "$actual"
  if ! diff -u "$expected" "$actual"
  then
    printf 'self-test: FAIL findings differ from %s (above, - expected, + actual)\n' "$(display "$fixtures/expected.txt")"
    failed=$((failed + 1))
  fi

  find "$stage/test" -name '*.java' -type f | sort | run_on_list > "$out" 2>&1
  rc=$?
  if [ "$rc" -ne 0 ] || grep -q '^ERROR ' "$out" || ! grep -q '^WARN ' "$out"
  then
    cat "$out"
    printf 'self-test: FAIL test fixtures exit %s, expected 0 with warnings only\n' "$rc"
    failed=$((failed + 1))
  fi

  grep ' none$' "$expected" | awk -v stage="$stage/" '/^src\// { print stage $1 }' | run_on_list > "$out" 2>&1
  rc=$?
  if [ "$rc" -ne 0 ] || grep -q -E '^(ERROR|WARN) ' "$out"
  then
    cat "$out"
    printf 'self-test: FAIL clean production fixtures exit %s, expected 0 without findings\n' "$rc"
    failed=$((failed + 1))
  fi

  find "$fixtures/src" -name '*.java' -type f | sort | run_on_list > "$out" 2>&1
  rc=$?
  if [ "$rc" -ne 0 ] || grep -q -E '^(ERROR|WARN) ' "$out"
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
  --help|-h)
    usage "Shape check"
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
