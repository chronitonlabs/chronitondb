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

import java.lang.management.GarbageCollectorMXBean;
import java.lang.management.ManagementFactory;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;

import com.google.common.collect.ImmutableList;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.ImmutableSet;
import org.junit.BeforeClass;
import org.junit.Test;

import com.datastax.driver.core.ResultSet;
import com.datastax.driver.core.Row;
import com.datastax.driver.core.SimpleStatement;
import org.apache.cassandra.cql3.CQLTester;
import org.apache.cassandra.service.CassandraDaemon;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

/**
 * The garbage collectors view on a test node started with the default configuration: its definition,
 * its rows against the collectors of the same JVM, and the list of the tables of system_views.
 * The table is named here by its text and not by the constant of the view class.
 */
public class JvmGarbageCollectorsTableTest extends CQLTester
{
    private static final String TABLE = "jvm_garbage_collectors";
    private static final String VIEW = "system_views." + TABLE;

    /**
     * Every table of system_views on a node of the line at the commit before the view was added,
     * Apache Cassandra's tables and the memory pools view. Written here and never read from the running node,
     * so a table the hook drops fails the test.
     */
    private static final List<String> TABLES_BEFORE_THE_VIEW = ImmutableList.of(
        "batch_metrics", "caches", "cidr_filtering_metrics_counts", "cidr_filtering_metrics_latencies",
        "clients", "coordinator_read_latency", "coordinator_scan_latency", "coordinator_write_latency",
        "cql_metrics", "credentials_cache_keys", "disk_usage", "gossip_info", "internode_inbound",
        "internode_outbound", "jmx_permissions_cache_keys", "jvm_memory_pools", "local_read_latency",
        "local_scan_latency", "local_write_latency", "max_partition_size", "max_sstable_duration",
        "max_sstable_size", "network_permissions_cache_keys", "pending_hints", "permissions_cache_keys",
        "queries", "repair_jobs", "repair_participates", "repair_sessions", "repair_validations", "repairs",
        "rows_per_read", "sai_column_indexes", "sai_sstable_index_segments", "sai_sstable_indexes",
        "settings", "snapshots", "sstable_tasks", "streaming", "system_logs", "system_properties",
        "thread_pools", "tombstones_per_read", "roles_cache_keys");

    /**
     * The two tables of system_views that a test node with no CIDR authorizer cannot read, on Apache Cassandra as here.
     */
    private static final Set<String> NEEDS_CIDR_AUTHORIZER = ImmutableSet.of("cidr_filtering_metrics_counts",
                                                                             "cidr_filtering_metrics_latencies");

    @BeforeClass
    public static void setUpClass()
    {
        CQLTester.setUpClass();
        requireNetwork();
        CassandraDaemon.getInstanceForTesting().setupVirtualKeyspaces();
    }

    @Test
    public void testNodeHoldsTheViewAndAnswersARead()
    {
        ResultSet columns = executeNet("SELECT column_name, kind, type FROM system_virtual_schema.columns " +
                                       "WHERE keyspace_name = 'system_views' AND table_name = ?", TABLE);
        Map<String, String> kinds = new HashMap<>();
        Map<String, String> types = new HashMap<>();
        for (Row row : columns)
        {
            kinds.put(row.getString("column_name"), row.getString("kind"));
            types.put(row.getString("column_name"), row.getString("type"));
        }
        assertThat(kinds).isEqualTo(ImmutableMap.of("name", "partition_key",
                                                     "collection_count", "regular",
                                                     "collection_time_millis", "regular"));
        assertThat(types).isEqualTo(ImmutableMap.of("name", "text",
                                                    "collection_count", "bigint",
                                                    "collection_time_millis", "bigint"));

        assertThat(executeNet("SELECT * FROM " + VIEW).all()).isNotEmpty();
    }

    @Test
    public void testViewShowsTheCollectorsOfTheSameJvm()
    {
        // The count and the time of a collector only grow, so a row read between two readings
        // of the bean lies between them. A bean that leaves a value undefined gives -1 at both readings.
        Map<String, long[]> before = readBeans();
        List<Row> rows = executeNet("SELECT * FROM " + VIEW).all();
        Map<String, long[]> after = readBeans();

        List<String> names = new ArrayList<>();
        for (Row row : rows)
        {
            String name = row.getString("name");
            names.add(name);
            assertThat(before).as("the collectors of the JVM").containsKey(name);
            assertBetween(name + " collection_count", row.getLong("collection_count"), before.get(name)[0], after.get(name)[0]);
            assertBetween(name + " collection_time_millis", row.getLong("collection_time_millis"), before.get(name)[1], after.get(name)[1]);
        }
        assertThat(names).containsExactlyInAnyOrderElementsOf(before.keySet());

        for (String name : before.keySet())
            assertThat(executeNet("SELECT name FROM " + VIEW + " WHERE name = ?", name).all())
                .extracting(row -> row.getString("name"))
                .containsExactly(name);

        assertThat(executeNet("SELECT name FROM " + VIEW + " WHERE name IN ?", new ArrayList<>(before.keySet())).all())
            .extracting(row -> row.getString("name"))
            .containsExactlyInAnyOrderElementsOf(before.keySet());
        assertThat(executeNet("SELECT name FROM " + VIEW + " WHERE name = 'No Such Collector'").all()).isEmpty();
    }

    @Test
    public void testPagedReadGivesEveryCollectorOnce()
    {
        Set<String> expected = readBeans().keySet();
        assertThat(expected.size()).isGreaterThan(1);

        SimpleStatement statement = new SimpleStatement("SELECT name FROM " + VIEW);
        statement.setFetchSize(1);
        List<String> names = new ArrayList<>();
        for (Row row : sessionNet().execute(statement))
            names.add(row.getString("name"));

        assertThat(names).containsExactlyInAnyOrderElementsOf(expected);
    }

    @Test
    public void testWritesAndTruncationAreRefused()
    {
        assertThatThrownBy(() -> executeNet("INSERT INTO " + VIEW + " (name, collection_count) VALUES ('x', 1)"))
            .hasMessageContaining("Modification is not supported by table " + VIEW);
        assertThatThrownBy(() -> executeNet("UPDATE " + VIEW + " SET collection_count = 1 WHERE name = 'x'"))
            .hasMessageContaining("Modification is not supported by table " + VIEW);
        assertThatThrownBy(() -> executeNet("DELETE FROM " + VIEW + " WHERE name = 'x'"))
            .hasMessageContaining("Modification is not supported by table " + VIEW);
        assertThatThrownBy(() -> executeNet("TRUNCATE " + VIEW))
            .hasMessageContaining("Truncation is not supported by table " + VIEW);
    }

    @Test
    public void testSystemViewsListsEveryEarlierTableAndTheView()
    {
        List<String> names = new ArrayList<>();
        for (Row row : executeNet("SELECT table_name FROM system_virtual_schema.tables WHERE keyspace_name = 'system_views'"))
            names.add(row.getString("table_name"));

        List<String> expected = new ArrayList<>(TABLES_BEFORE_THE_VIEW);
        expected.add(TABLE);
        assertThat(names).containsExactlyInAnyOrderElementsOf(expected);

        for (String table : TABLES_BEFORE_THE_VIEW)
        {
            if (!NEEDS_CIDR_AUTHORIZER.contains(table))
                executeNet("SELECT * FROM system_views." + table + " LIMIT 1");
        }
    }

    /**
     * The count and the time of each collector of the JVM, by its name.
     */
    private static Map<String, long[]> readBeans()
    {
        Map<String, long[]> values = new HashMap<>();
        for (GarbageCollectorMXBean bean : ManagementFactory.getGarbageCollectorMXBeans())
            values.put(bean.getName(), new long[]{ bean.getCollectionCount(), bean.getCollectionTime() });
        return values;
    }

    private static void assertBetween(String what, long value, long before, long after)
    {
        if (before == -1 && after == -1)
            assertThat(value).as(what).isEqualTo(-1L);
        else
            assertThat(value).as(what).isBetween(before, after);
    }
}
