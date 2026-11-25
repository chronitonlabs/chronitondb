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

import java.lang.management.ManagementFactory;
import java.lang.management.MemoryPoolMXBean;
import java.lang.management.MemoryType;
import java.lang.management.MemoryUsage;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.function.Supplier;

import com.google.common.annotations.VisibleForTesting;

import org.apache.cassandra.db.marshal.LongType;
import org.apache.cassandra.db.marshal.UTF8Type;
import org.apache.cassandra.db.virtual.AbstractVirtualTable;
import org.apache.cassandra.db.virtual.SimpleDataSet;
import org.apache.cassandra.dht.LocalPartitioner;
import org.apache.cassandra.schema.TableMetadata;

/**
 * The memory pools of the JVM of this node, one row for each pool, read from the JVM at each read.
 * The view keeps nothing between reads and catches nothing that a call to the JVM throws.
 */
public final class JvmMemoryPoolsTable extends AbstractVirtualTable
{
    public static final String TABLE_NAME = "jvm_memory_pools";

    private static final String NAME = "name";
    private static final String TYPE = "type";
    private static final String USED_BYTES = "used_bytes";
    private static final String COMMITTED_BYTES = "committed_bytes";
    private static final String MAX_BYTES = "max_bytes";

    private final Supplier<? extends List<? extends MemoryPoolMXBean>> pools;

    public JvmMemoryPoolsTable(String keyspace)
    {
        this(keyspace, ManagementFactory::getMemoryPoolMXBeans);
    }

    /**
     * Builds the view on pools that a test supplies. Only test code calls this.
     */
    @VisibleForTesting
    public JvmMemoryPoolsTable(String keyspace, Supplier<? extends List<? extends MemoryPoolMXBean>> pools)
    {
        super(TableMetadata.builder(keyspace, TABLE_NAME)
                           .kind(TableMetadata.Kind.VIRTUAL)
                           .partitioner(new LocalPartitioner(UTF8Type.instance))
                           .addPartitionKeyColumn(NAME, UTF8Type.instance)
                           .addRegularColumn(TYPE, UTF8Type.instance)
                           .addRegularColumn(USED_BYTES, LongType.instance)
                           .addRegularColumn(COMMITTED_BYTES, LongType.instance)
                           .addRegularColumn(MAX_BYTES, LongType.instance)
                           .build());
        this.pools = pools;
    }

    /**
     * Builds the row of every pool the JVM lists now. A read of one pool by its name builds them all too,
     * so a failure for any pool fails every read.
     */
    @Override
    public DataSet data()
    {
        SimpleDataSet result = new SimpleDataSet(metadata());
        Set<String> names = new HashSet<>();
        for (MemoryPoolMXBean pool : pools.get())
        {
            String name = pool.getName();
            if (!names.add(name))
                throw new IllegalStateException("the JVM lists more than one memory pool named " + name);
            addRow(result, name, pool);
        }
        return result;
    }

    private static void addRow(SimpleDataSet result, String name, MemoryPoolMXBean pool)
    {
        // Any type that is not HEAP shows as NON_HEAP, so the column keeps its two values
        // even if a later JDK adds a value to MemoryType. getType().name() would show that new value.
        String type = pool.getType() == MemoryType.HEAP ? MemoryType.HEAP.name() : MemoryType.NON_HEAP.name();
        // One call for the three sizes, so they belong to one moment. A pool the JVM reports no usage for keeps null sizes.
        MemoryUsage usage = pool.getUsage();
        result.row(name).column(TYPE, type);
        if (usage != null)
        {
            result.column(USED_BYTES, usage.getUsed())
                  .column(COMMITTED_BYTES, usage.getCommitted())
                  .column(MAX_BYTES, usage.getMax());
        }
    }
}
