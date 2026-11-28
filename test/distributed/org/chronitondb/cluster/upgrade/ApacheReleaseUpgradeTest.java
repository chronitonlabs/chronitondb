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


package org.chronitondb.cluster.upgrade;

import com.vdurmont.semver4j.Semver;
import com.vdurmont.semver4j.Semver.SemverType;
import org.junit.Test;

import org.apache.cassandra.distributed.UpgradeableCluster;
import org.apache.cassandra.distributed.api.ConsistencyLevel;
import org.apache.cassandra.distributed.api.Feature;
import org.apache.cassandra.distributed.api.IUpgradeableInstance;
import org.apache.cassandra.distributed.impl.AbstractCluster;
import org.apache.cassandra.distributed.shared.Versions;
import org.apache.cassandra.distributed.upgrade.UpgradeTestBase;

import static org.apache.cassandra.distributed.shared.AssertUtils.assertRows;
import static org.apache.cassandra.distributed.shared.AssertUtils.row;

/**
 * The line's upgrade path. A cluster of the latest Apache Cassandra 5.0 release takes one node of the line, serves
 * writes and reads through a node of each version, and reads every row back after that node returns to the release.
 * The release is read from {@code build/dtest-5.0.9.jar}, which CI places there from the jar it builds as
 * {@code dtest-apache-5.0.9.jar}.
 */
public class ApacheReleaseUpgradeTest extends UpgradeTestBase
{
    /** The latest Apache Cassandra 5.0 release, where the line's upgrade path starts. */
    private static final Semver APACHE_RELEASE = new Semver("5.0.9", SemverType.STRICT);

    @Test
    public void testMixedClusterServesBothVersionsAndRollbackReadsEveryRow() throws Throwable
    {
        Versions.Version release = Versions.find().get(APACHE_RELEASE);
        Versions.Version line = AbstractCluster.CURRENT_VERSION;

        try (UpgradeableCluster cluster = init(UpgradeableCluster.create(2, release, config -> config.with(Feature.GOSSIP, Feature.NETWORK))))
        {
            cluster.schemaChange(withKeyspace("CREATE TABLE %s.tbl (pk int PRIMARY KEY, v int)"));
            write(cluster, 1, 1);

            restartOn(cluster.get(1), line);
            write(cluster, 1, 2);
            write(cluster, 2, 3);
            readEveryRow(cluster, 3);
            cluster.get(1).flush(KEYSPACE);

            restartOn(cluster.get(1), release);
            readEveryRow(cluster, 3);
        }
    }

    private static void restartOn(IUpgradeableInstance instance, Versions.Version version) throws Exception
    {
        instance.shutdown().get();
        instance.setVersion(version);
        instance.startup();
    }

    /** Writes the row pk = value through the node {@code coordinator}, on both replicas. */
    private static void write(UpgradeableCluster cluster, int coordinator, int value)
    {
        cluster.coordinator(coordinator).execute(withKeyspace("INSERT INTO %s.tbl (pk, v) VALUES (?, ?)"), ConsistencyLevel.ALL, value, value);
    }

    /** Reads the rows 1 to {@code rows} through each node, from both replicas. */
    private static void readEveryRow(UpgradeableCluster cluster, int rows)
    {
        for (int coordinator = 1; coordinator <= cluster.size(); coordinator++)
        {
            for (int pk = 1; pk <= rows; pk++)
            {
                assertRows(cluster.coordinator(coordinator).execute(withKeyspace("SELECT pk, v FROM %s.tbl WHERE pk = ?"), ConsistencyLevel.ALL, pk),
                           row(pk, pk));
            }
        }
    }
}
