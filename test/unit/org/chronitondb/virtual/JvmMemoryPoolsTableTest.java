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
import java.io.InputStream;
import java.lang.management.ManagementFactory;
import java.lang.management.MemoryPoolMXBean;
import java.lang.management.MemoryType;
import java.lang.management.MemoryUsage;
import java.lang.reflect.Field;
import java.lang.reflect.InvocationHandler;
import java.lang.reflect.Modifier;
import java.lang.reflect.Proxy;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.atomic.AtomicLong;
import java.util.function.Supplier;

import com.google.common.collect.ImmutableList;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.ImmutableSet;
import org.junit.BeforeClass;
import org.junit.Test;

import com.datastax.driver.core.ResultSet;
import com.datastax.driver.core.Row;
import com.datastax.driver.core.SimpleStatement;
import org.apache.cassandra.cql3.CQLTester;
import org.apache.cassandra.cql3.QueryProcessor;
import org.apache.cassandra.db.marshal.UTF8Type;
import org.apache.cassandra.db.virtual.VirtualKeyspace;
import org.apache.cassandra.db.virtual.VirtualKeyspaceRegistry;
import org.apache.cassandra.service.CassandraDaemon;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.assertj.core.api.Assertions.catchThrowable;

/**
 * The view on a test node: its definition, its rows against the pools of the same JVM,
 * and its rows for pools of the test's own.
 */
public class JvmMemoryPoolsTableTest extends CQLTester
{
    private static final String VIEW = "system_views." + JvmMemoryPoolsTable.TABLE_NAME;
    private static final String TEST_KEYSPACE = "chronitondb_test_views";
    private static final String TEST_VIEW = TEST_KEYSPACE + '.' + JvmMemoryPoolsTable.TABLE_NAME;

    /**
     * Every table of system_views on a node of the line at the commit before the view was added.
     * Written here and never read from the running node, so a table the hook drops fails the test.
     */
    private static final List<String> STOCK_SYSTEM_VIEWS = ImmutableList.of(
        "batch_metrics", "caches", "cidr_filtering_metrics_counts", "cidr_filtering_metrics_latencies",
        "clients", "coordinator_read_latency", "coordinator_scan_latency", "coordinator_write_latency",
        "cql_metrics", "credentials_cache_keys", "disk_usage", "gossip_info", "internode_inbound",
        "internode_outbound", "jmx_permissions_cache_keys", "local_read_latency", "local_scan_latency",
        "local_write_latency", "max_partition_size", "max_sstable_duration", "max_sstable_size",
        "network_permissions_cache_keys", "pending_hints", "permissions_cache_keys", "queries",
        "repair_jobs", "repair_participates", "repair_sessions", "repair_validations", "repairs",
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

    // The view on a node started with the default configuration.

    @Test
    public void testNodeHoldsTheViewAndAnswersARead()
    {
        ResultSet columns = executeNet("SELECT column_name, clustering_order, kind, position, type " +
                                       "FROM system_virtual_schema.columns " +
                                       "WHERE keyspace_name = 'system_views' AND table_name = ?",
                                       JvmMemoryPoolsTable.TABLE_NAME);
        Map<String, String> kinds = new HashMap<>();
        Map<String, String> types = new HashMap<>();
        for (Row row : columns)
        {
            kinds.put(row.getString("column_name"), row.getString("kind"));
            types.put(row.getString("column_name"), row.getString("type"));
        }
        assertThat(kinds).isEqualTo(ImmutableMap.of("name", "partition_key",
                                                     "type", "regular",
                                                     "used_bytes", "regular",
                                                     "committed_bytes", "regular",
                                                     "max_bytes", "regular"));
        assertThat(types).isEqualTo(ImmutableMap.of("name", "text",
                                                    "type", "text",
                                                    "used_bytes", "bigint",
                                                    "committed_bytes", "bigint",
                                                    "max_bytes", "bigint"));

        assertThat(executeNet("SELECT * FROM " + VIEW).all()).isNotEmpty();
    }

    @Test
    public void testViewShowsThePoolsOfTheSameJvm()
    {
        Map<String, MemoryPoolMXBean> pools = new HashMap<>();
        for (MemoryPoolMXBean pool : ManagementFactory.getMemoryPoolMXBeans())
            pools.put(pool.getName(), pool);

        List<Row> rows = executeNet("SELECT * FROM " + VIEW).all();
        List<String> names = new ArrayList<>();
        for (Row row : rows)
        {
            String name = row.getString("name");
            names.add(name);
            MemoryPoolMXBean pool = pools.get(name);
            assertThat(pool).as("a pool of the JVM named %s", name).isNotNull();
            assertThat(row.getString("type")).isEqualTo(pool.getType() == MemoryType.HEAP ? "HEAP" : "NON_HEAP");
            MemoryUsage usage = pool.getUsage();
            if (usage == null)
            {
                assertThat(row.isNull("used_bytes")).isTrue();
                assertThat(row.isNull("committed_bytes")).isTrue();
                assertThat(row.isNull("max_bytes")).isTrue();
            }
            else
            {
                assertThat(row.getLong("max_bytes")).isEqualTo(usage.getMax());
                assertThat(row.getLong("used_bytes")).isBetween(0L, row.getLong("committed_bytes"));
            }
        }
        assertThat(names).containsExactlyInAnyOrderElementsOf(pools.keySet());

        for (String name : pools.keySet())
            assertThat(executeNet("SELECT name FROM " + VIEW + " WHERE name = ?", name).all())
                .extracting(row -> row.getString("name"))
                .containsExactly(name);

        List<String> two = new ArrayList<>(pools.keySet()).subList(0, 2);
        assertThat(executeNet("SELECT name FROM " + VIEW + " WHERE name IN ?", two).all())
            .extracting(row -> row.getString("name"))
            .containsExactlyInAnyOrderElementsOf(two);
    }

    @Test
    public void testPagedReadGivesEveryPoolOnce()
    {
        Set<String> expected = new HashSet<>();
        for (MemoryPoolMXBean pool : ManagementFactory.getMemoryPoolMXBeans())
            expected.add(pool.getName());
        assertThat(expected.size()).isGreaterThan(2);

        SimpleStatement statement = new SimpleStatement("SELECT name FROM " + VIEW);
        statement.setFetchSize(2);
        List<String> names = new ArrayList<>();
        for (Row row : sessionNet().execute(statement))
            names.add(row.getString("name"));

        assertThat(names).containsExactlyInAnyOrderElementsOf(expected);
    }

    @Test
    public void testWritesAndTruncationAreRefused()
    {
        assertThatThrownBy(() -> executeNet("INSERT INTO " + VIEW + " (name, type) VALUES ('x', 'HEAP')"))
            .hasMessageContaining("Modification is not supported by table " + VIEW);
        assertThatThrownBy(() -> executeNet("UPDATE " + VIEW + " SET type = 'HEAP' WHERE name = 'x'"))
            .hasMessageContaining("Modification is not supported by table " + VIEW);
        assertThatThrownBy(() -> executeNet("DELETE FROM " + VIEW + " WHERE name = 'x'"))
            .hasMessageContaining("Modification is not supported by table " + VIEW);
        assertThatThrownBy(() -> executeNet("TRUNCATE " + VIEW))
            .hasMessageContaining("Truncation is not supported by table " + VIEW);
    }

    @Test
    public void testSystemViewsListsEveryStockTableAndTheView()
    {
        List<String> names = new ArrayList<>();
        for (Row row : executeNet("SELECT table_name FROM system_virtual_schema.tables WHERE keyspace_name = 'system_views'"))
            names.add(row.getString("table_name"));

        List<String> expected = new ArrayList<>(STOCK_SYSTEM_VIEWS);
        expected.add(JvmMemoryPoolsTable.TABLE_NAME);
        assertThat(names).containsExactlyInAnyOrderElementsOf(expected);

        for (String table : STOCK_SYSTEM_VIEWS)
        {
            if (!NEEDS_CIDR_AUTHORIZER.contains(table))
                executeNet("SELECT * FROM system_views." + table + " LIMIT 1");
        }
    }

    // The rows of the view for pools of the test's own.

    @Test
    public void testRowHoldsTheSizesOfTheUsage()
    {
        useTestPools(pool("Heap Pool", MemoryType.HEAP, new MemoryUsage(1, 10, 20, 30)),
                     pool("No Maximum", MemoryType.NON_HEAP, new MemoryUsage(-1, 40, 50, -1)));

        Map<String, Row> rows = rowsByName(executeNet("SELECT * FROM " + TEST_VIEW).all());
        assertThat(rows.keySet()).containsExactlyInAnyOrder("Heap Pool", "No Maximum");

        Row heap = rows.get("Heap Pool");
        assertThat(heap.getString("type")).isEqualTo("HEAP");
        assertThat(heap.getLong("used_bytes")).isEqualTo(10L);
        assertThat(heap.getLong("committed_bytes")).isEqualTo(20L);
        assertThat(heap.getLong("max_bytes")).isEqualTo(30L);

        Row noMax = rows.get("No Maximum");
        assertThat(noMax.getString("type")).isEqualTo("NON_HEAP");
        assertThat(noMax.getLong("used_bytes")).isEqualTo(40L);
        assertThat(noMax.getLong("committed_bytes")).isEqualTo(50L);
        assertThat(noMax.getLong("max_bytes")).isEqualTo(-1L);
    }

    @Test
    public void testPoolWithNoUsageShowsNullSizes()
    {
        useTestPools(pool("Not Valid", MemoryType.NON_HEAP, () -> null),
                     pool("Valid", MemoryType.HEAP, new MemoryUsage(0, 1, 2, 3)));

        Row row = executeNet("SELECT * FROM " + TEST_VIEW + " WHERE name = 'Not Valid'").one();
        assertThat(row.getString("name")).isEqualTo("Not Valid");
        assertThat(row.getString("type")).isEqualTo("NON_HEAP");
        assertThat(row.isNull("used_bytes")).isTrue();
        assertThat(row.isNull("committed_bytes")).isTrue();
        assertThat(row.isNull("max_bytes")).isTrue();
        assertThat(executeNet("SELECT * FROM " + TEST_VIEW).all()).hasSize(2);
    }

    @Test
    public void testThreeSizesOfARowComeFromOneCall()
    {
        AtomicLong calls = new AtomicLong();
        useTestPools(pool("Moving", MemoryType.HEAP, () -> {
            long n = calls.incrementAndGet() * 1000;
            return new MemoryUsage(0, n + 1, n + 2, n + 3);
        }));

        for (int i = 0; i < 3; i++)
        {
            Row row = executeNet("SELECT * FROM " + TEST_VIEW).one();
            long used = row.getLong("used_bytes");
            assertThat(row.getLong("committed_bytes")).isEqualTo(used + 1);
            assertThat(row.getLong("max_bytes")).isEqualTo(used + 2);
        }
    }

    @Test
    public void testSecondReadTakesTheValuesOfTheSecondRead()
    {
        AtomicLong used = new AtomicLong(100);
        useTestPools(pool("Growing", MemoryType.HEAP, () -> new MemoryUsage(0, used.get(), 1000, 2000)));

        assertThat(executeNet("SELECT used_bytes FROM " + TEST_VIEW).one().getLong("used_bytes")).isEqualTo(100L);
        used.set(700);
        assertThat(executeNet("SELECT used_bytes FROM " + TEST_VIEW).one().getLong("used_bytes")).isEqualTo(700L);
    }

    @Test
    public void testRepeatedPoolNameFailsTheRead()
    {
        useTestPools(pool("Metaspace", MemoryType.NON_HEAP, new MemoryUsage(0, 1, 2, 3)),
                     pool("Metaspace", MemoryType.NON_HEAP, new MemoryUsage(0, 4, 5, 6)),
                     pool("Other", MemoryType.HEAP, new MemoryUsage(0, 7, 8, 9)));

        String message = "the JVM lists more than one memory pool named Metaspace";
        for (String read : new String[]{ "SELECT * FROM " + TEST_VIEW, "SELECT * FROM " + TEST_VIEW + " WHERE name = 'Other'" })
        {
            Throwable failure = catchThrowable(() -> QueryProcessor.executeInternal(read));
            assertThat(failure).isInstanceOf(IllegalStateException.class).hasMessage(message);
        }
    }

    // What a call to the JVM throws reaches the read as it was thrown.

    @Test
    public void testExceptionForOnePoolFailsAReadOfAnotherPool()
    {
        RuntimeException thrown = new IllegalStateException("usage of one pool");
        useTestPools(throwingPool("Broken", thrown), pool("Fine", MemoryType.HEAP, new MemoryUsage(0, 1, 2, 3)));

        assertFailsWith(thrown, "SELECT * FROM " + TEST_VIEW + " WHERE name = 'Fine'");
    }

    @Test
    public void testErrorForOnePoolFailsAReadOfAnotherPool()
    {
        Error thrown = new StackOverflowError("usage of one pool");
        useTestPools(throwingPool("Broken", thrown), pool("Fine", MemoryType.HEAP, new MemoryUsage(0, 1, 2, 3)));

        assertFailsWith(thrown, "SELECT * FROM " + TEST_VIEW + " WHERE name = 'Fine'");
    }

    @Test
    public void testExceptionFromTheListOfPoolsFailsAReadOfOnePool()
    {
        RuntimeException thrown = new IllegalStateException("list of pools");
        useTestPools(throwingList(thrown));

        assertFailsWith(thrown, "SELECT * FROM " + TEST_VIEW + " WHERE name = 'Fine'");
    }

    @Test
    public void testErrorFromTheListOfPoolsFailsAReadOfOnePool()
    {
        Error thrown = new StackOverflowError("list of pools");
        useTestPools(throwingList(thrown));

        assertFailsWith(thrown, "SELECT * FROM " + TEST_VIEW + " WHERE name = 'Fine'");
    }

    @Test
    public void testDirectReadPassesOnTheObjectThatWasThrown()
    {
        Throwable[] thrown = { new IllegalStateException("thrown"), new StackOverflowError("thrown") };
        for (Throwable t : thrown)
        {
            JvmMemoryPoolsTable fromPool = new JvmMemoryPoolsTable(TEST_KEYSPACE, () -> ImmutableList.of(throwingPool("Broken", t)));
            assertThat(catchThrowable(fromPool::data)).isSameAs(t);
            assertThat(catchThrowable(() -> fromPool.data(key(fromPool, "Other")))).isSameAs(t);

            JvmMemoryPoolsTable fromList = new JvmMemoryPoolsTable(TEST_KEYSPACE, throwingList(t));
            assertThat(catchThrowable(fromList::data)).isSameAs(t);
            assertThat(catchThrowable(() -> fromList.data(key(fromList, "Other")))).isSameAs(t);
        }
    }

    @Test
    public void testBuildingTheViewMakesNoCallForThePools()
    {
        JvmMemoryPoolsTable table = new JvmMemoryPoolsTable(TEST_KEYSPACE, throwingList(new AssertionError("a call for the pools")));
        assertThat(table.metadata().name).isEqualTo(JvmMemoryPoolsTable.TABLE_NAME);
    }

    // The feature does no work while nobody reads the view.

    @Test
    public void testNoThreadNoTaskAndNoKeptValue() throws Exception
    {
        assertNoThreadAndNoTaskOfTheFeature();
        assertViewNamesNoThreadOrTask();

        JvmMemoryPoolsTable table = new JvmMemoryPoolsTable(TEST_KEYSPACE, ManagementFactory::getMemoryPoolMXBeans);
        Map<Field, Object> before = instanceFields(table);
        assertNoStaticFieldButConstants();

        register(table);
        assertThat(executeNet("SELECT * FROM " + TEST_VIEW).all()).isNotEmpty();
        assertThat(executeNet("SELECT * FROM " + VIEW).all()).isNotEmpty();

        Map<Field, Object> after = instanceFields(table);
        assertThat(after.keySet()).isEqualTo(before.keySet());
        for (Field field : before.keySet())
            assertThat(after.get(field)).as("field %s after a read", field.getName()).isSameAs(before.get(field));
        assertNoThreadAndNoTaskOfTheFeature();
    }

    private static void assertNoThreadAndNoTaskOfTheFeature()
    {
        Thread current = Thread.currentThread();
        for (Map.Entry<Thread, StackTraceElement[]> thread : Thread.getAllStackTraces().entrySet())
        {
            if (thread.getKey() == current)
                continue;
            for (StackTraceElement frame : thread.getValue())
                assertThat(frame.getClassName()).as("a frame of thread %s", thread.getKey().getName())
                                                .doesNotStartWith("org.chronitondb.");
        }
    }

    /**
     * The view class names no class that starts a thread or schedules a task, so no read leaves one behind.
     */
    private static void assertViewNamesNoThreadOrTask() throws IOException
    {
        String resource = JvmMemoryPoolsTable.class.getName().replace('.', '/') + ".class";
        String classFile;
        try (InputStream in = JvmMemoryPoolsTable.class.getClassLoader().getResourceAsStream(resource))
        {
            assertThat(in).as("the class file of the view").isNotNull();
            classFile = new String(in.readAllBytes(), StandardCharsets.ISO_8859_1);
        }
        for (String name : new String[]{ "java/lang/Thread", "java/util/Timer", "java/util/concurrent/", "org/apache/cassandra/concurrent/" })
            assertThat(classFile).as("the view class names %s", name).doesNotContain(name);
    }

    private static Map<Field, Object> instanceFields(JvmMemoryPoolsTable table) throws IllegalAccessException
    {
        Map<Field, Object> values = new HashMap<>();
        for (Class<?> type = table.getClass(); type != Object.class; type = type.getSuperclass())
        {
            for (Field field : type.getDeclaredFields())
            {
                if (Modifier.isStatic(field.getModifiers()))
                    continue;
                field.setAccessible(true);
                values.put(field, field.get(table));
            }
        }
        return values;
    }

    private static void assertNoStaticFieldButConstants()
    {
        for (Field field : JvmMemoryPoolsTable.class.getDeclaredFields())
        {
            if (!Modifier.isStatic(field.getModifiers()))
                continue;
            assertThat(Modifier.isFinal(field.getModifiers())).as("static field %s is final", field.getName()).isTrue();
            assertThat(field.getType()).as("static field %s", field.getName()).isEqualTo(String.class);
        }
    }

    // Helpers.

    /**
     * A memory pool of the test's own. The view needs only its name, its type and its usage,
     * and every other call fails the test.
     */
    static MemoryPoolMXBean pool(String name, MemoryType type, Supplier<MemoryUsage> usage)
    {
        InvocationHandler handler = (proxy, method, args) -> {
            switch (method.getName())
            {
                case "getName":
                case "toString":
                    return name;
                case "getType":
                    return type;
                case "getUsage":
                    return usage.get();
                default:
                    throw new AssertionError("The view called " + method.getName() + ", which it does not need");
            }
        };
        return (MemoryPoolMXBean) Proxy.newProxyInstance(MemoryPoolMXBean.class.getClassLoader(),
                                                         new Class<?>[]{ MemoryPoolMXBean.class },
                                                         handler);
    }

    static MemoryPoolMXBean pool(String name, MemoryType type, MemoryUsage usage)
    {
        return pool(name, type, () -> usage);
    }

    /**
     * The read fails with the object that was thrown, in the throwable itself or among its causes.
     * A read through the node's internal path is used, since the driver drops its connection after a server error.
     */
    private static void assertFailsWith(Throwable thrown, String read)
    {
        Throwable failure = catchThrowable(() -> QueryProcessor.executeInternal(read));
        assertThat(failure).as("the failure of %s", read).isNotNull();
        boolean found = false;
        for (Throwable t = failure; t != null && !found; t = t.getCause())
            found = t == thrown;
        assertThat(found).as("%s holds the object that was thrown", failure).isTrue();
    }

    private static void useTestPools(MemoryPoolMXBean... pools)
    {
        List<MemoryPoolMXBean> list = ImmutableList.copyOf(pools);
        useTestPools(() -> list);
    }

    private static void useTestPools(Supplier<List<MemoryPoolMXBean>> pools)
    {
        register(new JvmMemoryPoolsTable(TEST_KEYSPACE, pools));
    }

    private static void register(JvmMemoryPoolsTable table)
    {
        VirtualKeyspaceRegistry.instance.register(new VirtualKeyspace(TEST_KEYSPACE, ImmutableList.of(table)));
    }

    private static MemoryPoolMXBean throwingPool(String name, Throwable thrown)
    {
        return pool(name, MemoryType.HEAP, () -> { throw sneaky(thrown); });
    }

    private static Supplier<List<MemoryPoolMXBean>> throwingList(Throwable thrown)
    {
        return () -> { throw sneaky(thrown); };
    }

    private static RuntimeException sneaky(Throwable thrown)
    {
        if (thrown instanceof RuntimeException)
            throw (RuntimeException) thrown;
        throw (Error) thrown;
    }

    private static org.apache.cassandra.db.DecoratedKey key(JvmMemoryPoolsTable table, String name)
    {
        return table.metadata().partitioner.decorateKey(UTF8Type.instance.decompose(name));
    }

    private static Map<String, Row> rowsByName(List<Row> rows)
    {
        Map<String, Row> byName = new HashMap<>();
        for (Row row : rows)
            byName.put(row.getString("name"), row);
        return byName;
    }
}
