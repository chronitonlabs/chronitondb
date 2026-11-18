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
# Shared by the check scripts of this folder, sourced, never run. The
# caller sets $tool (its own name) before sourcing. Defines:
#   $here      tools/chronitondb
#   $root      the repository this script is in
#   $tree      the tree whose files are checked: $root, or the directory
#              given with --tree. The scripts, the rules, the tools and
#              the scratch files stay those of $root
#   $fixtures  tools/chronitondb/test, skipped by every check, used by --self-test
#   $work      build/chronitondb-shape, downloads and scratch, never committed
#   $java_bin  java from JAVA_HOME when set, else from PATH

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
root="$(cd "$here/../.." && pwd -P)"
fixtures="$here/test"
work="$root/build/chronitondb-shape"
tree="$root"
java_bin="${JAVA_HOME:+$JAVA_HOME/bin/}java"

die()
{
  printf '%s: %s\n' "$tool" "$*" >&2
  exit 2
}

note()
{
  printf '%s: %s\n' "$tool" "$*" >&2
}

# Runs this script once on the files listed on stdin, one per line, and returns
# its exit code. GNU xargs would turn an exit code of 1 into 123.
run_on_list()
{
  local path files=()
  while IFS= read -r path
  do
    files+=("$path")
  done
  "$0" "$@" ${files[@]+"${files[@]}"}
}

# use_tree DIR: checks the files of DIR, another checkout of the
# repository, with the scripts and rules of this one. CI runs the checks of
# the line on the files of a pull request this way, so a pull request
# cannot bring its own rules.
use_tree()
{
  [ -n "${1:-}" ] || die "--tree needs a directory"
  [ -d "$1" ] || die "--tree $1 is not a directory"
  tree="$(cd "$1" && pwd -P)"
}

# Path for output: relative to the checked tree when inside it, else to the
# repository when inside it.
display()
{
  case "$1" in
    "$tree"/*) printf '%s' "$1" | awk -v r="$tree/" '{ print substr($0, length(r) + 1) }' ;;
    "$root"/*) printf '%s' "$1" | awk -v r="$root/" '{ print substr($0, length(r) + 1) }' ;;
    *) printf '%s' "$1" ;;
  esac
}

absolute()
{
  case "$1" in
    /*) printf '%s' "$1" ;;
    *) printf '%s/%s' "$tree" "$1" ;;
  esac
}

# "test" for a file under a test/ directory before org/chronitondb, else "prod".
classify()
{
  local rel prefix
  rel="$(display "$1")"
  prefix="${rel%%org/chronitondb/*}"
  case "/$prefix" in
    */test/*) printf 'test' ;;
    *) printf 'prod' ;;
  esac
}

# Reads paths from stdin. Keeps the org/chronitondb Java files that exist,
# drops the fixtures under tools/chronitondb/test of this repository and of
# the checked tree, removes duplicates. One absolute path per line.
select_files()
{
  local path abs
  while IFS= read -r path
  do
    [ -n "$path" ] || continue
    printf '%s\n' "$path" | grep -q -E '(^|/)org/chronitondb/.*\.java$' || continue
    abs="$(absolute "$path")"
    case "$abs" in
      "$fixtures"/*|"$tree/tools/chronitondb/test"/*)
        note "skipping fixture $(display "$abs"), fixtures are checked by --self-test"
        continue
        ;;
    esac
    [ -f "$abs" ] || continue
    printf '%s\n' "$abs"
  done | awk '!seen[$0]++'
}

# The files to check for the given mode, one absolute path per line.
#   files_for files FILE...   the given files
#   files_for staged          the files staged in git
#   files_for base REF        the files changed since the merge base with REF
files_for()
{
  local mode="$1"
  shift
  case "$mode" in
    files) printf '%s\n' "$@" ;;
    staged) git -C "$tree" diff --cached --name-only --diff-filter=ACMR ;;
    base) git -C "$tree" diff --name-only --diff-filter=ACMR --merge-base "$1" HEAD ;;
  esac | select_files
}

sha256_of()
{
  if command -v sha256sum >/dev/null 2>&1
  then
    sha256sum "$1" | awk '{ print $1 }'
  else
    shasum -a 256 "$1" | awk '{ print $1 }'
  fi
}

# download_verified URL SHA256 DEST: fetches URL into DEST under build/ unless
# a copy with the pinned sha256 is there already. Refuses anything else.
download_verified()
{
  local url="$1" sha256="$2" dest="$3" actual
  mkdir -p "$(dirname "$dest")" || die "cannot create $(dirname "$dest")"
  if [ ! -f "$dest" ] || [ "$(sha256_of "$dest")" != "$sha256" ]
  then
    note "downloading $(basename "$dest") into $(display "$(dirname "$dest")")"
    curl -fsSL --retry 3 -o "$dest" "$url" || die "download of $url failed"
  fi
  actual="$(sha256_of "$dest")"
  if [ "$actual" != "$sha256" ]
  then
    rm -f "$dest"
    die "$(basename "$dest") does not match the pinned sha256 ($actual, expected $sha256)"
  fi
}

# Prints the comment block at the top of the calling script as usage: from
# the comment line starting with $1 down to the line before "set -u". The
# comment marker is spelled as octal 043 so that lint tools do not read this
# awk program as a comment.
usage()
{
  awk -v start="$1" '
    index($0, "\043 " start) == 1 { on = 1 }
    /^set -u/ { exit }
    on { sub("^\043 ?", ""); print }' "$0"
}
