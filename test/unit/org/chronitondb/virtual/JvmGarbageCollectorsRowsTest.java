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
import java.lang.management.GarbageCollectorMXBean;
import java.lang.management.ManagementFactory;
import java.lang.reflect.Field;
import java.lang.reflect.InvocationHandler;
import java.lang.reflect.Modifier;
import java.lang.reflect.Proxy;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.atomic.AtomicLong;
import java.util.concurrent.atomic.AtomicReference;
import java.util.function.LongSupplier;
import java.util.function.Supplier;

import com.google.common.collect.ImmutableList;
import org.junit.BeforeClass;
import org.junit.Test;

import com.datastax.driver.core.Row;
import org.apache.cassandra.concurrent.ExecutorFactory;
import org.apache.cassandra.cql3.CQLTester;
import org.apache.cassandra.cql3.QueryProcessor;
import org.apache.cassandra.db.DecoratedKey;
import org.apache.cassandra.db.marshal.UTF8Type;
import org.apache.cassandra.db.virtual.VirtualKeyspace;
import org.apache.cassandra.db.virtual.VirtualKeyspaceRegistry;
import org.apache.cassandra.service.CassandraDaemon;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.catchThrowable;
import static org.chronitondb.virtual.JvmGarbageCollectorsRowsTest.TestCollectors.collector;

/**
 * The rows of the garbage collectors view for collectors of the test's own, what a call to the JVM throws,
 * and the work the view does while nobody reads it.
 */
public class JvmGarbageCollectorsRowsTest extends CQLTester
{
    private static final String VIEW = "system_views." + JvmGarbageCollectorsTable.TABLE_NAME;
    private static final String TEST_KEYSPACE = "chronitondb_test_views";
    private static final String TEST_VIEW = TEST_KEYSPACE + '.' + JvmGarbageCollectorsTable.TABLE_NAME;

    @BeforeClass
    public static void setUpClass()
    {
        CQLTester.setUpClass();
        requireNetwork();
        CassandraDaemon.getInstanceForTesting().setupVirtualKeyspaces();
    }

    // The rows of the view for collectors of the test's own.

    @Test
    public void testRowHoldsTheCountAndTheTimeOfTheCollector()
    {
        useTestCollectors(collector("Young", 412, 3180),
                          collector("Old", 0, 0),
                          collector("Long Running", Long.MAX_VALUE, Long.MAX_VALUE));

        Map<String, Row> rows = rowsByName(executeNet("SELECT * FROM " + TEST_VIEW).all());
        assertThat(rows.keySet()).containsExactlyInAnyOrder("Young", "Old", "Long Running");
        assertRow(rows.get("Young"), 412L, 3180L);
        assertRow(rows.get("Old"), 0L, 0L);
        assertRow(rows.get("Long Running"), Long.MAX_VALUE, Long.MAX_VALUE);
    }

    @Test
    public void testUndefinedValueShowsMinusOne()
    {
        useTestCollectors(collector("No Count", -1, 25),
                          collector("No Time", 7, -1),
                          collector("Neither", -1, -1));

        Map<String, Row> rows = rowsByName(executeNet("SELECT * FROM " + TEST_VIEW).all());
        assertThat(rows.keySet()).containsExactlyInAnyOrder("No Count", "No Time", "Neither");
        assertRow(rows.get("No Count"), -1L, 25L);
        assertRow(rows.get("No Time"), 7L, -1L);
        assertRow(rows.get("Neither"), -1L, -1L);
    }

    @Test
    public void testSecondReadTakesTheValuesOfTheSecondRead()
    {
        AtomicLong count = new AtomicLong(3);
        useTestCollectors(collector("Growing", count::get, () -> count.get() * 10));

        assertRow(executeNet("SELECT * FROM " + TEST_VIEW).one(), 3L, 30L);
        count.set(9);
        assertRow(executeNet("SELECT * FROM " + TEST_VIEW).one(), 9L, 90L);
    }

    @Test
    public void testNoCollectorGivesNoRow()
    {
        useTestCollectors();
        assertThat(executeNet("SELECT * FROM " + TEST_VIEW).all()).isEmpty();
        assertThat(executeNet("SELECT * FROM " + TEST_VIEW + " WHERE name = 'Absent'").all()).isEmpty();

        useTestCollectors(collector("Present", 1, 2));
        assertThat(executeNet("SELECT * FROM " + TEST_VIEW + " WHERE name = 'Absent'").all()).isEmpty();
        assertThat(executeNet("SELECT * FROM " + TEST_VIEW + " WHERE name IN ('Absent', 'Present')").all())
            .extracting(row -> row.getString("name"))
            .containsExactly("Present");
    }

    @Test
    public void testRepeatedCollectorNameFailsTheRead()
    {
        useTestCollectors(collector("Copy", 1, 2),
                          collector("Copy", 3, 4),
                          collector("Other", 5, 6));

        String message = "the JVM lists more than one garbage collector named Copy";
        for (String read : new String[]{ "SELECT * FROM " + TEST_VIEW, "SELECT * FROM " + TEST_VIEW + " WHERE name = 'Other'" })
        {
            Throwable failure = catchThrowable(() -> QueryProcessor.executeInternal(read));
            assertThat(failure).as("the failure of %s", read).isInstanceOf(IllegalStateException.class).hasMessage(message);
        }
    }

    // What a call to the JVM throws reaches the read as it was thrown.

    @Test
    public void testFailureForOneCollectorFailsAReadOfAnotherCollector()
    {
        for (Throwable thrown : exceptionAndError("count of one collector"))
        {
            useTestCollectors(collector("Broken", () -> { throw sneaky(thrown); }, () -> 1), collector("Fine", 1, 2));
            assertFailsWith(thrown, "SELECT * FROM " + TEST_VIEW + " WHERE name = 'Fine'");
        }
        for (Throwable thrown : exceptionAndError("time of one collector"))
        {
            useTestCollectors(collector("Broken", () -> 1, () -> { throw sneaky(thrown); }), collector("Fine", 1, 2));
            assertFailsWith(thrown, "SELECT * FROM " + TEST_VIEW + " WHERE name = 'Fine'");
        }
    }

    @Test
    public void testFailureFromTheListOfCollectorsFailsAReadOfOneCollector()
    {
        for (Throwable thrown : exceptionAndError("list of collectors"))
        {
            useTestCollectors(throwingList(thrown));
            assertFailsWith(thrown, "SELECT * FROM " + TEST_VIEW + " WHERE name = 'Fine'");
        }
    }

    @Test
    public void testDirectReadPassesOnTheObjectThatWasThrown()
    {
        for (Throwable t : exceptionAndError("thrown"))
        {
            JvmGarbageCollectorsTable fromCollector = new JvmGarbageCollectorsTable(TEST_KEYSPACE, () -> ImmutableList.of(collector("Broken", () -> { throw sneaky(t); }, () -> 1)));
            assertThat(catchThrowable(fromCollector::data)).isSameAs(t);
            assertThat(catchThrowable(() -> fromCollector.data(key(fromCollector, "Other")))).isSameAs(t);

            JvmGarbageCollectorsTable fromList = new JvmGarbageCollectorsTable(TEST_KEYSPACE, throwingList(t));
            assertThat(catchThrowable(fromList::data)).isSameAs(t);
            assertThat(catchThrowable(() -> fromList.data(key(fromList, "Other")))).isSameAs(t);
        }
    }

    @Test
    public void testBuildingTheViewMakesNoCallForTheCollectors()
    {
        JvmGarbageCollectorsTable table = new JvmGarbageCollectorsTable(TEST_KEYSPACE, throwingList(new AssertionError("a call for the collectors")));
        assertThat(table.metadata().name).isEqualTo(JvmGarbageCollectorsTable.TABLE_NAME);
    }

    // The view does no work while nobody reads it.

    @Test
    public void testNoThreadNoTaskAndNoKeptValue() throws Exception
    {
        assertNoThreadOfTheView();
        assertViewNamesNoThreadOrTask();

        JvmGarbageCollectorsTable table = new JvmGarbageCollectorsTable(TEST_KEYSPACE, ManagementFactory::getGarbageCollectorMXBeans);
        Map<Field, Object> before = instanceFields(table);
        assertNoStaticFieldButConstants();

        register(table);
        assertThat(executeNet("SELECT * FROM " + TEST_VIEW).all()).isNotEmpty();
        assertThat(executeNet("SELECT * FROM " + VIEW).all()).isNotEmpty();
        assertReadsLeaveNoThread(table);

        Map<Field, Object> after = instanceFields(table);
        assertThat(after.keySet()).isEqualTo(before.keySet());
        for (Field field : before.keySet())
            assertThat(after.get(field)).as("field %s after a read", field.getName()).isSameAs(before.get(field));
        assertNoThreadOfTheView();
    }

    /**
     * No thread but the test's own runs code of the view.
     */
    private static void assertNoThreadOfTheView()
    {
        Thread current = Thread.currentThread();
        for (Map.Entry<Thread, StackTraceElement[]> thread : Thread.getAllStackTraces().entrySet())
        {
            if (thread.getKey() == current)
                continue;
            for (StackTraceElement frame : thread.getValue())
                assertThat(frame.getClassName()).as("a frame of thread %s", thread.getKey().getName())
                                                .isNotEqualTo(JvmGarbageCollectorsTable.class.getName());
        }
    }

    /**
     * Reads the view from a thread of a new thread group, then checks that the group holds no thread.
     * A thread that a read starts joins the group of the thread that starts it, unless the code names another group,
     * so a thread that a read leaves behind stays in the group, idle or not.
     */
    private static void assertReadsLeaveNoThread(JvmGarbageCollectorsTable table) throws InterruptedException
    {
        ThreadGroup group = new ThreadGroup("garbage collectors view reads");
        AtomicReference<Throwable> failure = new AtomicReference<>();
        Thread reader = new ExecutorFactory.Default(null, group, null).startThread("garbage collectors view reader", () -> {
            try
            {
                for (int i = 0; i < 3; i++)
                {
                    table.data();
                    QueryProcessor.executeInternal("SELECT * FROM " + TEST_VIEW);
                }
            }
            catch (Throwable t)
            {
                failure.set(t);
            }
        });
        reader.join();
        assertThat(failure.get()).as("a failure of the reads").isNull();
        Thread[] left = new Thread[8];
        int count = group.enumerate(left, true);
        assertThat(count).as("threads left in the group of the reads").isZero();
    }

    /**
     * The view class names no class that starts a thread or schedules a task, so no read leaves one behind.
     */
    private static void assertViewNamesNoThreadOrTask() throws IOException
    {
        String resource = JvmGarbageCollectorsTable.class.getName().replace('.', '/') + ".class";
        String classFile;
        try (InputStream in = JvmGarbageCollectorsTable.class.getClassLoader().getResourceAsStream(resource))
        {
            assertThat(in).as("the class file of the view").isNotNull();
            classFile = new String(in.readAllBytes(), StandardCharsets.ISO_8859_1);
        }
        for (String name : new String[]{ "java/lang/Thread", "java/util/Timer", "java/util/concurrent/", "org/apache/cassandra/concurrent/" })
            assertThat(classFile).as("the view class names %s", name).doesNotContain(name);
    }

    private static Map<Field, Object> instanceFields(JvmGarbageCollectorsTable table) throws IllegalAccessException
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
        for (Field field : JvmGarbageCollectorsTable.class.getDeclaredFields())
        {
            if (!Modifier.isStatic(field.getModifiers()))
                continue;
            assertThat(Modifier.isFinal(field.getModifiers())).as("static field %s is final", field.getName()).isTrue();
            assertThat(field.getType()).as("static field %s", field.getName()).isEqualTo(String.class);
        }
    }

    // Helpers.

    /**
     * Garbage collectors of a test's own, for this class and for the test of the view on a cluster.
     * The collectors are built in a class of their own, so a node of a cluster can build them
     * without loading this test class.
     */
    public static final class TestCollectors
    {
        private TestCollectors()
        {
        }

        /**
         * A garbage collector of the test's own. The view needs only its name, its count and its time,
         * and every other call fails the test.
         */
        public static GarbageCollectorMXBean collector(String name, LongSupplier count, LongSupplier time)
        {
            InvocationHandler handler = (proxy, method, args) -> {
                switch (method.getName())
                {
                    case "getName":
                    case "toString":
                        return name;
                    case "getCollectionCount":
                        return count.getAsLong();
                    case "getCollectionTime":
                        return time.getAsLong();
                    default:
                        throw new AssertionError("The view called " + method.getName() + ", which it does not need");
                }
            };
            return (GarbageCollectorMXBean) Proxy.newProxyInstance(GarbageCollectorMXBean.class.getClassLoader(),
                                                                   new Class<?>[]{ GarbageCollectorMXBean.class },
                                                                   handler);
        }

        public static GarbageCollectorMXBean collector(String name, long count, long time)
        {
            return collector(name, () -> count, () -> time);
        }
    }

    private static void assertRow(Row row, long count, long time)
    {
        assertThat(row.getLong("collection_count")).as("collection_count of %s", row.getString("name")).isEqualTo(count);
        assertThat(row.getLong("collection_time_millis")).as("collection_time_millis of %s", row.getString("name")).isEqualTo(time);
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

    private static void useTestCollectors(GarbageCollectorMXBean... collectors)
    {
        List<GarbageCollectorMXBean> list = ImmutableList.copyOf(collectors);
        useTestCollectors(() -> list);
    }

    private static void useTestCollectors(Supplier<List<GarbageCollectorMXBean>> collectors)
    {
        register(new JvmGarbageCollectorsTable(TEST_KEYSPACE, collectors));
    }

    private static void register(JvmGarbageCollectorsTable table)
    {
        VirtualKeyspaceRegistry.instance.register(new VirtualKeyspace(TEST_KEYSPACE, ImmutableList.of(table)));
    }

    private static Supplier<List<GarbageCollectorMXBean>> throwingList(Throwable thrown)
    {
        return () -> { throw sneaky(thrown); };
    }

    /**
     * An exception and an error of the JVM that is no out of memory error, both with the given message.
     */
    private static Throwable[] exceptionAndError(String message)
    {
        return new Throwable[]{ new IllegalStateException(message), new StackOverflowError(message) };
    }

    private static RuntimeException sneaky(Throwable thrown)
    {
        if (thrown instanceof RuntimeException)
            throw (RuntimeException) thrown;
        throw (Error) thrown;
    }

    private static DecoratedKey key(JvmGarbageCollectorsTable table, String name)
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
