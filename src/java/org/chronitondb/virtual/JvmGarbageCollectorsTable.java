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
 * The garbage collectors of the JVM of this node, one row for each collector, read from the JVM at each read.
 * The view keeps nothing between reads and catches nothing that a call to the JVM throws.
 */
public final class JvmGarbageCollectorsTable extends AbstractVirtualTable
{
    public static final String TABLE_NAME = "jvm_garbage_collectors";

    private static final String NAME = "name";
    private static final String COLLECTION_COUNT = "collection_count";
    private static final String COLLECTION_TIME_MILLIS = "collection_time_millis";

    private final Supplier<? extends List<? extends GarbageCollectorMXBean>> collectors;

    public JvmGarbageCollectorsTable(String keyspace)
    {
        this(keyspace, ManagementFactory::getGarbageCollectorMXBeans);
    }

    /**
     * Builds the view on collectors that a test supplies. Only test code calls this.
     */
    @VisibleForTesting
    public JvmGarbageCollectorsTable(String keyspace, Supplier<? extends List<? extends GarbageCollectorMXBean>> collectors)
    {
        super(TableMetadata.builder(keyspace, TABLE_NAME)
                           .kind(TableMetadata.Kind.VIRTUAL)
                           .partitioner(new LocalPartitioner(UTF8Type.instance))
                           .addPartitionKeyColumn(NAME, UTF8Type.instance)
                           .addRegularColumn(COLLECTION_COUNT, LongType.instance)
                           .addRegularColumn(COLLECTION_TIME_MILLIS, LongType.instance)
                           .build());
        this.collectors = collectors;
    }

    /**
     * Builds the row of every collector the JVM lists now. A read of one collector by its name builds them all too,
     * so a failure for any collector fails every read.
     */
    @Override
    public DataSet data()
    {
        SimpleDataSet result = new SimpleDataSet(metadata());
        Set<String> names = new HashSet<>();
        for (GarbageCollectorMXBean collector : collectors.get())
        {
            String name = collector.getName();
            if (!names.add(name))
                throw new IllegalStateException("the JVM lists more than one garbage collector named " + name);
            // Each value as the bean returns it, so -1 shows a value the JVM leaves undefined for the collector.
            result.row(name)
                  .column(COLLECTION_COUNT, collector.getCollectionCount())
                  .column(COLLECTION_TIME_MILLIS, collector.getCollectionTime());
        }
        return result;
    }
}
