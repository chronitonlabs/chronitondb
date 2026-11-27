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
import java.util.ArrayList;
import java.util.List;

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
import org.chronitondb.virtual.JvmGarbageCollectorsTable;

import static org.assertj.core.api.Assertions.assertThat;
import static org.chronitondb.virtual.JvmGarbageCollectorsRowsTest.TestCollectors.collector;

/**
 * Each node of a cluster answers a read of the garbage collectors view from its own collectors.
 */
public class JvmGarbageCollectorsNodesTest extends TestBaseImpl
{
    private static final String COLLECTOR = "Only On Node One";
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
    public void testCollectorGivenToOneNodeShowsOnThatNodeOnly()
    {
        cluster.get(1).runOnInstance(() -> {
            List<VirtualTable> tables = new ArrayList<>();
            for (VirtualTable table : SystemViewsKeyspace.instance.tables())
            {
                if (!table.metadata().name.equals(JvmGarbageCollectorsTable.TABLE_NAME))
                    tables.add(table);
            }
            tables.add(new JvmGarbageCollectorsTable(SystemViewsKeyspace.instance.name(),
                                                     () -> ImmutableList.of(collector(COLLECTOR, 5, 70))));
            VirtualKeyspaceRegistry.instance.register(new VirtualKeyspace(SystemViewsKeyspace.instance.name(), tables));
        });

        Object[][] first = cluster.coordinator(1).execute("SELECT name, collection_count, collection_time_millis " +
                                                          "FROM system_views.jvm_garbage_collectors", ConsistencyLevel.ONE);
        assertThat(first).hasDimensions(1, 3);
        assertThat(first[0]).containsExactly(COLLECTOR, 5L, 70L);

        List<Object> second = new ArrayList<>();
        for (Object[] row : cluster.coordinator(2).execute("SELECT name FROM system_views.jvm_garbage_collectors", ConsistencyLevel.ONE))
            second.add(row[0]);
        assertThat(second).isNotEmpty().doesNotContain(COLLECTOR);
    }
}
