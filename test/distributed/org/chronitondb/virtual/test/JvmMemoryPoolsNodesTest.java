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

package org.chronitondb.virtual.test;

import java.io.IOException;
import java.lang.management.MemoryPoolMXBean;
import java.lang.management.MemoryType;
import java.lang.management.MemoryUsage;
import java.lang.reflect.InvocationHandler;
import java.lang.reflect.Proxy;
import java.util.ArrayList;
import java.util.List;
import java.util.function.Supplier;

import com.google.common.collect.ImmutableList;
import org.junit.AfterClass;
import org.junit.BeforeClass;
import org.junit.Test;

import org.apache.cassandra.db.virtual.SystemViewsKeyspace;
import org.apache.cassandra.db.virtual.VirtualKeyspace;
import org.apache.cassandra.db.virtual.VirtualKeyspaceRegistry;
import org.apache.cassandra.db.virtual.VirtualTable;
import org.apache.cassandra.distributed.Cluster;
import org.apache.cassandra.distributed.api.ConsistencyLevel;
import org.apache.cassandra.distributed.test.TestBaseImpl;
import org.chronitondb.virtual.JvmMemoryPoolsTable;

import static org.assertj.core.api.Assertions.assertThat;

/**
 * Each node of a cluster answers a read of the view from its own pools.
 */
public class JvmMemoryPoolsNodesTest extends TestBaseImpl
{
    private static final String POOL = "Only On Node One";
    private static Cluster cluster;

    @BeforeClass
    public static void startCluster() throws IOException
    {
        cluster = Cluster.build(2).start();
    }

    @AfterClass
    public static void closeCluster()
    {
        if (cluster != null)
            cluster.close();
    }

    @Test
    public void testPoolGivenToOneNodeShowsOnThatNodeOnly()
    {
        cluster.get(1).runOnInstance(() -> {
            List<VirtualTable> tables = new ArrayList<>();
            for (VirtualTable table : SystemViewsKeyspace.instance.tables())
            {
                if (!table.metadata().name.equals(JvmMemoryPoolsTable.TABLE_NAME))
                    tables.add(table);
            }
            tables.add(new JvmMemoryPoolsTable(SystemViewsKeyspace.instance.name(),
                                               () -> ImmutableList.of(pool(POOL, MemoryType.HEAP, new MemoryUsage(0, 1, 2, 3)))));
            VirtualKeyspaceRegistry.instance.register(new VirtualKeyspace(SystemViewsKeyspace.instance.name(), tables));
        });

        Object[][] first = cluster.coordinator(1).execute("SELECT name, used_bytes FROM system_views.jvm_memory_pools", ConsistencyLevel.ONE);
        assertThat(first).hasDimensions(1, 2);
        assertThat(first[0]).containsExactly(POOL, 1L);

        List<Object> second = new ArrayList<>();
        for (Object[] row : cluster.coordinator(2).execute("SELECT name FROM system_views.jvm_memory_pools", ConsistencyLevel.ONE))
            second.add(row[0]);
        assertThat(second).isNotEmpty().doesNotContain(POOL);
    }

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
}
