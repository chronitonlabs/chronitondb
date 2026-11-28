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
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import org.junit.BeforeClass;
import org.junit.Test;

import com.datastax.driver.core.ColumnDefinitions;
import com.datastax.driver.core.Row;
import org.apache.cassandra.cql3.CQLTester;
import org.apache.cassandra.service.CassandraDaemon;

import static org.assertj.core.api.Assertions.assertThat;

/**
 * The reference page of the garbage collectors view against a test node, and the statements the page must make.
 */
public class JvmGarbageCollectorsPageTest extends CQLTester
{
    private static final Path PAGE = Paths.get("docs", "reference", "virtual-tables", "jvm-garbage-collectors.md");
    private static final Pattern COLUMN_ROW = Pattern.compile("^\\| `([a-z_]+)` \\| `([a-z]+)` \\| ([a-z ]+) \\| (.*) \\|$", Pattern.MULTILINE);

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
        assertThat(page()).startsWith("---\ntitle: ").contains("\ndescription: ").contains("\n---\n<!--").contains("# system_views.jvm_garbage_collectors\n");

        Map<String, String> onPage = new HashMap<>();
        Matcher row = COLUMN_ROW.matcher(page());
        while (row.find())
        {
            assertThat(row.group(4).trim()).as("the meaning of column %s", row.group(1)).hasSizeGreaterThan(20);
            onPage.put(row.group(1), row.group(2) + ' ' + row.group(3).replace(' ', '_'));
        }

        Map<String, String> onNode = new HashMap<>();
        for (Row column : executeNet("SELECT column_name, type, kind FROM system_virtual_schema.columns " +
                                     "WHERE keyspace_name = 'system_views' AND table_name = ?", JvmGarbageCollectorsTable.TABLE_NAME))
            onNode.put(column.getString("column_name"), column.getString("type") + ' ' + column.getString("kind"));

        assertThat(onNode).hasSize(3);
        assertThat(onPage).isEqualTo(onNode);
    }

    @Test
    public void testExampleStatementsRunAndTheSampleShowsTheColumnsInTheirOrder() throws IOException
    {
        String example = section("## Example");
        assertThat(example).contains("A sample of a read");

        List<String> statements = new ArrayList<>();
        for (String line : example.split("\n"))
        {
            String statement = line.startsWith("cqlsh> ") ? line.substring("cqlsh> ".length()) : line;
            if (statement.startsWith("SELECT "))
                statements.add(statement);
        }
        assertThat(statements).hasSize(2);
        for (String statement : statements)
            executeNet(statement);

        List<String> columns = new ArrayList<>();
        for (ColumnDefinitions.Definition column : executeNet("SELECT * FROM system_views.jvm_garbage_collectors").getColumnDefinitions())
            columns.add(column.getName());
        Matcher header = Pattern.compile("^ name +\\|.*$", Pattern.MULTILINE).matcher(example);
        assertThat(header.find()).as("the header of the sample").isTrue();
        List<String> shown = new ArrayList<>();
        for (String name : header.group().split("\\|"))
            shown.add(name.trim());
        assertThat(shown).isEqualTo(columns);
    }

    @Test
    public void testPageGivesTheMeaningOfMinusOne() throws IOException
    {
        assertThat(section("## Columns")).contains("**-1 in `collection_count` or `collection_time_millis`.**")
                                         .contains("undefined");
    }

    @Test
    public void testPageSaysWhatANodeWithoutTheViewAnswersAndNamesTheStep() throws IOException
    {
        assertThat(section("## Nodes without the table")).contains("`table jvm_garbage_collectors does not exist`");
        String back = section("## Moving back");
        assertThat(back).contains("**The step.**")
                        .contains("LIST ALL PERMISSIONS ON system_views.jvm_garbage_collectors NORECURSIVE;")
                        .contains("REVOKE ALL PERMISSIONS ON system_views.jvm_garbage_collectors FROM <role>;")
                        .contains("as a superuser")
                        .contains("**A grant left behind.**")
                        .contains("(jvm-memory-pools.md#moving-back)");
    }

    @Test
    public void testPageSaysOneStatementCanTakeMoreThanOneRead() throws IOException
    {
        assertThat(section("## One statement and its reads")).contains("more than one read")
                                                             .contains("different moments")
                                                             .contains("(jvm-memory-pools.md#one-statement-and-its-reads)")
                                                             .contains("`SELECT * FROM system_views.jvm_garbage_collectors` with no page size");
    }

    @Test
    public void testPageSaysAFailureForOneCollectorFailsEveryReadAndNamesTheError() throws IOException
    {
        String fails = section("## When a read fails");
        assertThat(fails).containsPattern("for one garbage collector[^.]*fails every read")
                         .contains("catches nothing")
                         .contains("`java.lang.IllegalStateException: the JVM lists more than one garbage collector named <name>`")
                         .contains("(jvm-memory-pools.md#when-a-read-fails)");
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
}
