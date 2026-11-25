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
import java.util.Map;
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
    private static final String[] COMMITS = { "ChronitonDB `chronitondb-sandbox` at `ffa1bc742d`",
                                              "Apache Cassandra `cassandra-5.0` at `76550e9314`",
                                              "Apache Cassandra `cassandra-5.0` at `47227d98bf`" };
    private static final String OUT_OF_MEMORY = "An out of memory error during a read of the table goes to the node's own handling " +
                                                "of an out of memory error, as on any request.";

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
        assertThat(page()).contains("`HEAP` for a pool of heap memory, `NON_HEAP` for any other pool. These are the two values of the column")
                          .contains("**-1 in `max_bytes`.** The JVM reports a usage for the pool and defines no maximum for it.")
                          .contains("**null in `used_bytes`, `committed_bytes` and `max_bytes`.** The JVM lists the pool and reports no usage for it");
    }

    @Test
    public void testPageSaysWhatANodeWithoutTheViewAnswersAndNamesTheStep() throws IOException
    {
        assertThat(page()).contains("## Nodes without the table")
                          .contains("refuses a read of it with `table jvm_memory_pools does not exist`")
                          .contains("## Moving back")
                          .contains("**The step.** Before the last node that has the table moves back");
    }

    @Test
    public void testPageSaysOneStatementCanTakeMoreThanOneRead() throws IOException
    {
        assertThat(page()).contains("One statement can be answered from more than one read. These are the cases that were read in the code. They are not the whole list:")
                          .contains("1. **Pages a client fetches.**")
                          .contains("2. **Pages the node fetches for an aggregate.**")
                          .contains("3. **Several names.**")
                          .contains("One statement was read in the code as exactly one read: `SELECT * FROM system_views.jvm_memory_pools`, " +
                                    "sent with no page size or with a page size above the number of pools.")
                          .contains("1. **Different moments.**")
                          .contains("2. **A pool can be missing.**");
    }

    @Test
    public void testPageSaysHowToRemoveTheGrantsAndWhatOneLeftBehindDoes() throws IOException
    {
        assertThat(page()).contains("LIST ALL PERMISSIONS ON system_views.jvm_memory_pools NORECURSIVE;")
                          .contains("revokes every permission of each")
                          .contains("REVOKE ALL PERMISSIONS ON system_views.jvm_memory_pools FROM <role>;")
                          .contains("The operator MUST send both statements as a superuser, to a node that has the table")
                          .contains("**A grant left behind.**")
                          .contains("1. It gives its role nothing.")
                          .contains("It is removed by `DROP ROLE` of its role")
                          .contains("This page says what a row left behind does for the code of those three commits, and for no other code.");
        assertNamesTheThreeCommitsAfter("**A grant left behind.**");
    }

    @Test
    public void testPageSaysAFailureForOnePoolFailsEveryRead() throws IOException
    {
        assertThat(page()).contains("An exception, or an error of the JVM that is no out of memory error, that the JVM raises for one memory pool " +
                                    "fails every read of the table while it lasts, a read of another pool by its name included.");
    }

    @Test
    public void testPageSaysWhatTheNodeAnswersAndLogsForAFailedRead() throws IOException
    {
        assertThat(page()).contains("The table catches nothing that a call to the JVM throws while a read builds its rows.")
                          .contains("1. **Answered.** An exception is answered with a server error")
                          .contains("2. **Logged.** The node logs an exception at ERROR")
                          .contains("This page says what the node answers and logs for the code of those three commits, and for no other code.")
                          .contains(OUT_OF_MEMORY);
        assertNamesTheThreeCommitsAfter("## When a read fails");

        for (String sentence : page().replace('\n', ' ').split("(?<=\\.) "))
        {
            if (!sentence.contains("out of memory error")
                || sentence.contains("no out of memory error")
                || sentence.contains("where no cause of what was thrown is an out of memory error"))
                continue;
            assertThat(sentence.trim()).as("a sentence on an out of memory error").isEqualTo(OUT_OF_MEMORY);
        }
    }

    private static void assertNamesTheThreeCommitsAfter(String heading) throws IOException
    {
        String section = page().substring(page().indexOf(heading));
        for (String commit : COMMITS)
            assertThat(section).contains(commit);
    }
}
