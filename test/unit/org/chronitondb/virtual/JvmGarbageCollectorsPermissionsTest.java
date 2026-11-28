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

import java.util.ArrayList;
import java.util.List;

import org.junit.After;
import org.junit.BeforeClass;
import org.junit.Test;

import com.datastax.driver.core.Row;
import com.datastax.driver.core.exceptions.UnauthorizedException;
import org.apache.cassandra.ServerTestUtils;
import org.apache.cassandra.config.DatabaseDescriptor;
import org.apache.cassandra.cql3.CQLTester;
import org.apache.cassandra.service.CassandraDaemon;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

/**
 * Who may read the garbage collectors view, and grants on the view by name.
 */
public class JvmGarbageCollectorsPermissionsTest extends CQLTester
{
    private static final String VIEW = "system_views." + JvmGarbageCollectorsTable.TABLE_NAME;
    private static final String VIEW_RESOURCE = "<table " + VIEW + '>';
    private static final String PASSWORD = "secret";
    private static final String[] ROLES = { "on_view", "on_keyspace", "on_all_keyspaces", "on_other_view", "no_grant", "granted" };

    @BeforeClass
    public static void setUpClass()
    {
        ServerTestUtils.daemonInitialization();
        DatabaseDescriptor.setPermissionsValidity(0);
        DatabaseDescriptor.setRolesValidity(0);
        CQLTester.setUpClass();
        requireAuthentication();
        requireNetwork();
        CassandraDaemon.getInstanceForTesting().setupVirtualKeyspaces();
    }

    @After
    public void dropRoles()
    {
        useSuperUser();
        for (String role : ROLES)
            executeNet("DROP ROLE IF EXISTS " + role);
    }

    @Test
    public void testReadNeedsTheGrantsOfATableOfSystemViews()
    {
        useSuperUser();
        assertThat(executeNet("SELECT * FROM " + VIEW).all()).isNotEmpty();

        createRole("on_view");
        executeNet("GRANT SELECT ON " + VIEW + " TO on_view");
        createRole("on_keyspace");
        executeNet("GRANT SELECT ON KEYSPACE system_views TO on_keyspace");
        createRole("on_all_keyspaces");
        executeNet("GRANT SELECT ON ALL KEYSPACES TO on_all_keyspaces");
        createRole("on_other_view");
        executeNet("GRANT SELECT ON system_views." + JvmMemoryPoolsTable.TABLE_NAME + " TO on_other_view");
        createRole("no_grant");

        useUser("on_view", PASSWORD);
        assertThat(executeNet("SELECT * FROM " + VIEW).all()).isNotEmpty();
        useUser("on_keyspace", PASSWORD);
        assertThat(executeNet("SELECT * FROM " + VIEW).all()).isNotEmpty();
        for (String role : new String[]{ "on_all_keyspaces", "on_other_view", "no_grant" })
        {
            useUser(role, PASSWORD);
            assertThatThrownBy(() -> executeNet("SELECT * FROM " + VIEW))
                .isInstanceOf(UnauthorizedException.class)
                .hasMessageContaining("User " + role + " has no SELECT permission on " + VIEW_RESOURCE);
        }
    }

    @Test
    public void testGrantAndRevokeOnTheViewByName()
    {
        useSuperUser();
        createRole("granted");
        executeNet("GRANT SELECT ON " + VIEW + " TO granted");
        executeNet("GRANT AUTHORIZE ON " + VIEW + " TO granted");

        assertThat(permissionsOf("granted", "LIST ALL PERMISSIONS ON " + VIEW + " NORECURSIVE"))
            .containsExactlyInAnyOrder(VIEW_RESOURCE + " SELECT", VIEW_RESOURCE + " AUTHORIZE");

        executeNet("REVOKE ALL PERMISSIONS ON " + VIEW + " FROM granted");

        assertThat(permissionsOf("granted", "LIST ALL PERMISSIONS ON " + VIEW + " NORECURSIVE")).isEmpty();
    }

    private void createRole(String role)
    {
        executeNet("CREATE ROLE " + role + " WITH LOGIN = true AND PASSWORD = '" + PASSWORD + '\'');
    }

    private List<String> permissionsOf(String role, String listing)
    {
        List<String> permissions = new ArrayList<>();
        for (Row row : executeNet(listing))
        {
            if (role.equals(row.getString("role")))
                permissions.add(row.getString("resource") + ' ' + row.getString("permission"));
        }
        return permissions;
    }
}
