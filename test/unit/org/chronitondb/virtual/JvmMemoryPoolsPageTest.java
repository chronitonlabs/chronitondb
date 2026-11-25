/*
 * Copyright 2026 AxonOps Limited
 * SPDX-License-Identifier: Apache-2.0
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package org.chronitondb.virtual;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import org.junit.BeforeClass;
import org.junit.Test;

import com.datastax.driver.core.Row;
import org.apache.cassandra.cql3.CQLTester;
import org.apache.cassandra.service.CassandraDaemon;

import static org.assertj.core.api.Assertions.assertThat;

/**
 * The reference page of the view against a test node, and the statements the page must make.
 */
public class JvmMemoryPoolsPageTest extends CQLTester
{
    private static final Path PAGE = Paths.get("docs", "reference", "virtual-tables", "jvm-memory-pools.md");
    private static final Pattern COLUMN_ROW = Pattern.compile("^\\| `([a-z_]+)` \\| `([a-z]+)` \\| ([a-z ]+) \\| (.*) \\|$", Pattern.MULTILINE);
    /**
     * A commit the page names for code it was read in: the project, its branch and the commit, in any wording round it.
     */
    private static final Pattern COMMIT = Pattern.compile("(ChronitonDB|Apache Cassandra)\\S* `[a-z0-9.-]+` at `([0-9a-f]{7,40})`");
    private static final String OUT_OF_MEMORY = "the node's own handling of an out of memory error, as on any request";

    private static String page;

    @BeforeClass
    public static void setUpClass()
    {
        CQLTester.setUpClass();
        requireNetwork();
        CassandraDaemon.getInstanceForTesting().setupVirtualKeyspaces();
    }

    private static String page() throws IOException
    {
        if (page == null)
            page = new String(Files.readAllBytes(PAGE), StandardCharsets.UTF_8);
        return page;
    }

    @Test
    public void testPageNamesEveryColumnWithItsTypeAndKind() throws IOException
    {
        assertThat(page()).startsWith("---\ntitle: ").contains("\ndescription: ").contains("\n---\n<!--").contains("# system_views.jvm_memory_pools\n");

        Map<String, String> onPage = new HashMap<>();
        Matcher row = COLUMN_ROW.matcher(page());
        while (row.find())
        {
            assertThat(row.group(4).trim()).as("the meaning of column %s", row.group(1)).hasSizeGreaterThan(20);
            onPage.put(row.group(1), row.group(2) + ' ' + row.group(3).replace(' ', '_'));
        }

        Map<String, String> onNode = new HashMap<>();
        for (Row column : executeNet("SELECT column_name, type, kind FROM system_virtual_schema.columns " +
                                     "WHERE keyspace_name = 'system_views' AND table_name = ?", JvmMemoryPoolsTable.TABLE_NAME))
            onNode.put(column.getString("column_name"), column.getString("type") + ' ' + column.getString("kind"));

        assertThat(onNode).hasSize(5);
        assertThat(onPage).isEqualTo(onNode);
    }

    @Test
    public void testPageGivesTheValuesOfTypeAndTheMeaningOfMinusOneAndNull() throws IOException
    {
        String columns = section("## Columns");
        Matcher type = Pattern.compile("^\\| `type` \\|.*$", Pattern.MULTILINE).matcher(columns);
        assertThat(type.find()).as("the row of the type column").isTrue();
        assertThat(type.group()).contains("`HEAP`").contains("`NON_HEAP`");
        assertThat(columns).contains("**-1 in `max_bytes`.**")
                           .contains("**null in `used_bytes`, `committed_bytes` and `max_bytes`.**");
    }

    @Test
    public void testPageSaysWhatANodeWithoutTheViewAnswersAndNamesTheStep() throws IOException
    {
        assertThat(section("## Nodes without the table")).contains("`table jvm_memory_pools does not exist`");
        assertThat(section("## Moving back")).contains("**The step.**");
    }

    @Test
    public void testPageSaysOneStatementCanTakeMoreThanOneRead() throws IOException
    {
        String reads = section("## One statement and its reads");
        assertThat(reads).contains("more than one read")
                         .contains("**Pages a client fetches.**")
                         .contains("**Pages the node fetches for an aggregate.**")
                         .contains("**Several names.**")
                         .contains("exactly one read: `SELECT * FROM system_views.jvm_memory_pools`")
                         .contains("**Different moments.**")
                         .contains("**A pool can be missing.**");
    }

    @Test
    public void testPageSaysHowToRemoveTheGrantsAndWhatOneLeftBehindDoes() throws IOException
    {
        String back = section("## Moving back");
        assertThat(back).contains("LIST ALL PERMISSIONS ON system_views.jvm_memory_pools NORECURSIVE;")
                        .contains("REVOKE ALL PERMISSIONS ON system_views.jvm_memory_pools FROM <role>;")
                        .contains("as a superuser")
                        .contains("**A grant left behind.**")
                        .contains("`DROP ROLE`")
                        .contains("for no other code");
        assertNamesThreeCommits(back.substring(back.indexOf("**A grant left behind.**")));
    }

    @Test
    public void testPageSaysAFailureForOnePoolFailsEveryRead() throws IOException
    {
        assertThat(section("## When a read fails")).containsPattern("for one memory pool[^.]*fails every read");
    }

    @Test
    public void testPageSaysWhatTheNodeAnswersAndLogsForAFailedRead() throws IOException
    {
        String fails = section("## When a read fails");
        assertThat(fails).contains("| Failure | What the client gets | What the node logs |")
                         .contains("`java.lang.IllegalStateException: the JVM lists more than one memory pool named <name>`")
                         .contains("catches nothing")
                         .contains("server error")
                         .contains("at ERROR")
                         .contains("`client_error_reporting_exclusions`")
                         .contains("for no other code")
                         .contains(OUT_OF_MEMORY);
        assertNamesThreeCommits(fails);

        // Of an out of memory error the page says only where it goes.
        for (String line : page().split("\n"))
        {
            String rest = line.replace("no out of memory error", "")
                              .replace("no cause of what was thrown is an out of memory error", "");
            if (rest.contains("out of memory error"))
                assertThat(line).as("a line on an out of memory error").contains(OUT_OF_MEMORY);
        }
    }

    /**
     * The part of the page under a heading, up to the next heading of the same level.
     */
    private static String section(String heading) throws IOException
    {
        int start = page().indexOf("\n" + heading + "\n");
        assertThat(start).as("the heading %s", heading).isNotNegative();
        int end = page().indexOf("\n## ", start + heading.length() + 2);
        return end < 0 ? page().substring(start) : page().substring(start, end);
    }

    private static void assertNamesThreeCommits(String text)
    {
        Set<String> commits = new HashSet<>();
        Matcher commit = COMMIT.matcher(text);
        while (commit.find())
            commits.add(commit.group(2));
        assertThat(commits).as("the commits the text names").hasSize(3);
    }
}
