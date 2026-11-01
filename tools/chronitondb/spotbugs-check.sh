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
# SpotBugs with the FindSecBugs plugin on the compiled org/chronitondb
# classes. Report only: findings are printed and never fail the check.
#
#   tools/chronitondb/spotbugs-check.sh [CLASSES]    analyse the org.chronitondb classes under CLASSES
#                                                    (default build/classes/main, run `ant jar` first)
#   tools/chronitondb/spotbugs-check.sh --self-test  compile and analyse the fixture under tools/chronitondb/test/spotbugs
#
# Apache classes are never analysed, they are only read to resolve types,
# with the jars under build/lib/jars.
#
# Tools: SpotBugs and FindSecBugs jars from Maven Central, pinned below by
# sha256, downloaded into build/chronitondb-shape/spotbugs on first use and
# refused unless the sha256 matches. Nothing is added to lib/ or build.xml
# and nothing is shipped. Needs a JDK (javac for --self-test).
#
# Output: SpotBugs text output, one line per finding
#   WARN priority category BUG_TYPE CODE: message  At File.java:[line N]
# then one summary line. Exit 0 when the analysis ran, with or without
# findings. The self-test exits 1 when a planted bug is missed. Exit 2 when
# the check itself could not run.
set -u

tool=spotbugs-check
# shellcheck source=lib.sh
. "$(dirname "${BASH_SOURCE[0]}")/lib.sh"

# The pins: sha256, Maven Central path, file name. The names are the ones in
# the Class-Path of the spotbugs.jar manifest, so `java -jar spotbugs.jar`
# finds the others next to it. The set is the lib/ directory of the SpotBugs
# 4.10.5 release (spotbugs-4.10.5.tgz, GitHub digest sha256:cce32449...007e),
# every jar there byte for byte equal to the Maven Central copy. Read on
# 2026-10-30. Each sha256 equals the .sha256 file Maven Central serves where
# one is published. Where only .sha1 is published (bcel, commons-io,
# commons-lang3, commons-text, jcip-annotations, jspecify, jsr305, the three
# log4j jars, findsecbugs-plugin), the sha256 is of the downloaded jar after
# its .sha1 matched, and for bcel, log4j-core and findsecbugs-plugin after
# the .asc signature verified.
maven="https://repo1.maven.org/maven2"
spotbugs_version="4.10.5"
spotbugs_jars="
8d0af71a88a5324fbe10909cc2ac4145a358c9af52fd6f796bdc0b0e42c7665f com/github/spotbugs/spotbugs/4.10.5/spotbugs-4.10.5.jar spotbugs.jar
2f28af17ad61a7daad0f3df070198c4a5807d3ffd98a5408f670cd19fc2dce84 com/github/spotbugs/spotbugs-annotations/4.10.5/spotbugs-annotations-4.10.5.jar spotbugs-annotations.jar
5fe3b469b8646e5bc53a897840952d63b712d4923d2a7a26aebc585f1fec7676 org/ow2/asm/asm/9.11/asm-9.11.jar asm-9.11.jar
a1421c20978ca0a330f241b17923a751a23fb1c9423fda1aba7591bb086b01d8 org/ow2/asm/asm-analysis/9.11/asm-analysis-9.11.jar asm-analysis-9.11.jar
fcff37e6a0227a9f5ee81a7c07f51249307fa15889b56a359ae6f773c164c22b org/ow2/asm/asm-commons/9.11/asm-commons-9.11.jar asm-commons-9.11.jar
da8ad24d0bf7efb0674a906f59a7d441692b641718371f3bce6762b191a169fd org/ow2/asm/asm-tree/9.11/asm-tree-9.11.jar asm-tree-9.11.jar
d5a23a677f31b8a7d2419895906e1fcbd9ac995beffb20944c8610c1bc377609 org/ow2/asm/asm-util/9.11/asm-util-9.11.jar asm-util-9.11.jar
a37a65752e861c07d313ca47bef0eb75bf7643152c82ca54c4f42d036850b4fb org/apache/bcel/bcel/6.13.0/bcel-6.13.0.jar bcel-6.13.0.jar
2b9a7b1f726fb86216dbd2c8321eabe0221dbd5b1be81c18e1cb53811b104758 commons-io/commons-io/2.22.0/commons-io-2.22.0.jar commons-io-2.22.0.jar
a2af247ec4db6eb8947e18e23e0433e4871a7c5d0a40e1f92e46ede54ae1defe org/apache/commons/commons-lang3/3.21.0/commons-lang3-3.21.0.jar commons-lang3-3.21.0.jar
58d2da30f058512a1e7f914e39241deca4dff5c27a085b4ed2faa9e7208067f6 org/apache/commons/commons-text/1.15.0/commons-text-1.15.0.jar commons-text-1.15.0.jar
3fae79e081096e1410645eb3557c63b79ca266d510ab479889511109becd1690 org/dom4j/dom4j/2.2.0/dom4j-2.2.0.jar dom4j-2.2.0.jar
b49c5c958316ed67a09c699dda9aa749caf434d51d863dea599ef36a49b9c855 com/google/errorprone/error_prone_annotations/2.48.0/error_prone_annotations-2.48.0.jar error_prone_annotations-2.48.0.jar
2cbd119bf1961c28788310963dc80ba65f58cdeec1dd139c8bdb1240faa2c36f com/google/code/gson/gson/2.14.0/gson-2.14.0.jar gson-2.14.0.jar
3e2a755b283fd492fa4be204294c7abb7cd63ac94fb366baab9c7bb9afb00b6d jaxen/jaxen/2.0.6/jaxen-2.0.6.jar jaxen-2.0.6.jar
4fccff8382aafc589962c4edb262f6aa595e34f1e11e61057d1c6a96e8fc7323 com/github/stephenc/jcip/jcip-annotations/1.0-1/jcip-annotations-1.0-1.jar jcip-annotations-1.0-1.jar
070d75f261fe4c5b8202508366715f7f2d4660f88c8ef7e6d3575e48c9683b66 org/jspecify/jspecify/1.0.1/jspecify-1.0.1.jar jspecify-1.0.1.jar
766ad2a0783f2687962c8ad74ceecc38a28b9f72a2d085ee438b7813e928d0c7 com/google/code/findbugs/jsr305/3.0.2/jsr305-3.0.2.jar jsr305-3.0.2.jar
f1810a4704ccce019d02bba029dc02a4f2ac0c997f647b465e7d409c1927f822 org/apache/logging/log4j/log4j-api/2.26.1/log4j-api-2.26.1.jar log4j-api-2.26.1.jar
2ec8c3bf5a6d7c89be8620116a2fc973f7dda1ad0261ad393c4d4726edfd3dcb org/apache/logging/log4j/log4j-core/2.26.1/log4j-core-2.26.1.jar log4j-core-2.26.1.jar
cbdfb4c2bcc10f0927c61036db54924250f3924ecd13ea913cefe4f99c08fa66 org/apache/logging/log4j/log4j-slf4j2-impl/2.26.1/log4j-slf4j2-impl-2.26.1.jar log4j-slf4j2-impl-2.26.1.jar
b571af282f25d7301059f788b9a149aab8b5cdc14ef3d212dc5425d3dcbb9a97 net/sf/saxon/Saxon-HE/12.10/Saxon-HE-12.10.jar Saxon-HE-12.10.jar
7e1446499b359675d8aabe6af2de86b85e72ae8a2a932c0b40d0e5ba57097439 org/slf4j/slf4j-api/2.0.20/slf4j-api-2.0.20.jar slf4j-api-2.0.20.jar
1fe4d5b92f708dcdb82dbce12919e0171e6b5ca62c6dca6220483625098feb5f org/xmlresolver/xmlresolver/5.3.3/xmlresolver-5.3.3.jar xmlresolver-5.3.3.jar
b0c487ad2f3e558be8d829c916d2458d10aca6a5bafa7a4d0524b70845e48a5c org/xmlresolver/xmlresolver/5.3.3/xmlresolver-5.3.3-data.jar xmlresolver-5.3.3-data.jar
"
findsecbugs_jar="6fa340344fa433ff46c2985dab1010e8bc739f9395c983594a5240095e92abc8 com/h3xstream/findsecbugs/findsecbugs-plugin/1.14.0/findsecbugs-plugin-1.14.0.jar findsecbugs-plugin-1.14.0.jar"
spotbugs_home="$work/spotbugs-$spotbugs_version"

# Fetches every pinned jar into $spotbugs_home, checking each sha256.
fetch_jars()
{
  local sha256 path name
  printf '%s\n%s\n' "$spotbugs_jars" "$findsecbugs_jar" | while read -r sha256 path name
  do
    [ -n "$sha256" ] || continue
    download_verified "$maven/$path" "$sha256" "$spotbugs_home/$name"
  done || exit 2
}

# run_spotbugs CLASSES AUXLIST OUT: FindSecBugs and the SpotBugs detectors on
# the org.chronitondb classes under CLASSES, findings written to OUT.
run_spotbugs()
{
  local classes="$1" auxlist="$2" output="$3"
  fetch_jars
  "$java_bin" -jar "$spotbugs_home/spotbugs.jar" -textui -effort:max -longBugCodes \
    -pluginList "$spotbugs_home/findsecbugs-plugin-1.14.0.jar" \
    -onlyAnalyze 'org.chronitondb.-' \
    -auxclasspathFromFile "$auxlist" \
    -output "$output" "$classes" || die "spotbugs failed on $(display "$classes")"
}

# analyse CLASSES: report only, the findings never fail the check.
analyse()
{
  local classes auxlist="$work/spotbugs-auxclasspath.txt" out="$work/spotbugs-output.txt" n_found
  classes="$(absolute "$1")"
  [ -d "$classes" ] || die "$(display "$classes") is not a directory, run 'ant jar' first"
  if [ ! -d "$classes/org/chronitondb" ]
  then
    printf '%s: no org/chronitondb classes under %s\n' "$tool" "$(display "$classes")"
    return 0
  fi
  mkdir -p "$work" || die "cannot create $(display "$work")"
  find "$root/build/lib/jars" -name '*.jar' -type f 2>/dev/null | sort > "$auxlist"
  run_spotbugs "$classes" "$auxlist" "$out"
  sed 's/^/WARN /' "$out"
  n_found="$(grep -c . "$out")"
  printf '%s: %s finding(s) in the org/chronitondb classes under %s, report only\n' \
    "$tool" "$n_found" "$(display "$classes")"
}

# Compiles the fixture and checks that FindSecBugs reports both planted bugs.
self_test()
{
  local stage="$work/spotbugs-selftest" out failed=0 javac_bin bug
  javac_bin="${JAVA_HOME:+$JAVA_HOME/bin/}javac"
  rm -rf "$stage"
  mkdir -p "$stage/classes" || die "cannot create $(display "$stage")"
  "$javac_bin" -d "$stage/classes" "$fixtures/spotbugs/org/chronitondb/selftest/SpotBugsFixture.java" \
    || die "cannot compile the fixture with $javac_bin"
  : > "$stage/auxclasspath.txt"
  out="$stage/output.txt"
  run_spotbugs "$stage/classes" "$stage/auxclasspath.txt" "$out"
  cat "$out"
  for bug in COMMAND_INJECTION OBJECT_DESERIALIZATION
  do
    if ! grep -q " $bug " "$out"
    then
      printf 'self-test: FAIL %s was not reported on the fixture\n' "$bug"
      failed=$((failed + 1))
    fi
  done
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
  --help|-h)
    usage "SpotBugs with"
    ;;
  --*)
    die "unknown option $1"
    ;;
  "")
    analyse "build/classes/main"
    ;;
  *)
    analyse "$1"
    ;;
esac
