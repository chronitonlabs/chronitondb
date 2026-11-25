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
import java.util.Set;

import org.junit.After;
import org.junit.BeforeClass;
import org.junit.Test;

import com.datastax.driver.core.Row;
import com.datastax.driver.core.exceptions.UnauthorizedException;
import org.apache.cassandra.ServerTestUtils;
import org.apache.cassandra.auth.AuthCacheService;
import org.apache.cassandra.auth.AuthenticatedUser;
import org.apache.cassandra.auth.DataResource;
import org.apache.cassandra.auth.IResource;
import org.apache.cassandra.auth.Permission;
import org.apache.cassandra.config.DatabaseDescriptor;
import org.apache.cassandra.cql3.CQLTester;
import org.apache.cassandra.cql3.QueryProcessor;
import org.apache.cassandra.service.CassandraDaemon;
import org.apache.cassandra.utils.Pair;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

/**
 * Who may read the view, grants on the view by name, and what a grant row left behind
 * for a table of system_views that the node does not have does.
 */
public class JvmMemoryPoolsPermissionsTest extends CQLTester
{
    private static final String VIEW = "system_views." + JvmMemoryPoolsTable.TABLE_NAME;
    private static final String VIEW_RESOURCE = "<table " + VIEW + '>';
    private static final String PASSWORD = "secret";
    private static final String[] ROLES = { "on_view", "on_keyspace", "no_grant", "granted", "leftover" };

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
        createRole("no_grant");

        useUser("on_view", PASSWORD);
        assertThat(executeNet("SELECT * FROM " + VIEW).all()).isNotEmpty();
        useUser("on_keyspace", PASSWORD);
        assertThat(executeNet("SELECT * FROM " + VIEW).all()).isNotEmpty();
        useUser("no_grant", PASSWORD);
        assertThatThrownBy(() -> executeNet("SELECT * FROM " + VIEW))
            .isInstanceOf(UnauthorizedException.class)
            .hasMessageContaining("User no_grant has no SELECT permission on " + VIEW_RESOURCE);
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

    @Test
    public void testGrantRowForATableTheNodeDoesNotHave()
    {
        String table = "no_such_view";
        String resource = "<table system_views." + table + '>';

        useSuperUser();
        createRole("leftover");
        createTable("CREATE TABLE %s (k int PRIMARY KEY, v int)");
        executeNet("GRANT SELECT ON " + KEYSPACE + '.' + currentTable() + " TO leftover");
        QueryProcessor.executeInternal("INSERT INTO system_auth.role_permissions (role, resource, permissions) " +
                                       "VALUES ('leftover', 'data/system_views/" + table + "', {'SELECT', 'AUTHORIZE'})");

        // A permission check reads only the row of the resource the statement names.
        useUser("leftover", PASSWORD);
        executeNet("SELECT * FROM " + KEYSPACE + '.' + currentTable());

        // Both listings show the row.
        useSuperUser();
        assertThat(permissionsOf("leftover", "LIST ALL PERMISSIONS"))
            .contains(resource + " SELECT", resource + " AUTHORIZE");
        assertThat(permissionsOf("leftover", "LIST ALL PERMISSIONS OF leftover"))
            .contains(resource + " SELECT", resource + " AUTHORIZE");

        // The warm-up of the permissions cache parses the row and goes on.
        assertWarmUpLoads("leftover", DataResource.table("system_views", table));

        // DROP ROLE removes the row.
        executeNet("DROP ROLE leftover");
        assertThat(QueryProcessor.executeInternal("SELECT * FROM system_auth.role_permissions WHERE role = 'leftover'").isEmpty())
            .isTrue();
    }

    private static void assertWarmUpLoads(String role, IResource resource)
    {
        boolean warming = DatabaseDescriptor.getRawConfig().auth_cache_warming_enabled;
        DatabaseDescriptor.getRawConfig().auth_cache_warming_enabled = true;
        AuthenticatedUser.permissionsCache.setValidity(60_000);
        try
        {
            AuthCacheService.instance.warmCaches();
            Set<Permission> loaded = null;
            for (java.util.Map.Entry<Pair<AuthenticatedUser, IResource>, Set<Permission>> entry : AuthenticatedUser.permissionsCache.getAll().entrySet())
            {
                if (entry.getKey().left.getName().equals(role) && entry.getKey().right.equals(resource))
                    loaded = entry.getValue();
            }
            assertThat(loaded).as("permissions the warm-up loaded for %s", resource)
                              .containsExactlyInAnyOrder(Permission.SELECT, Permission.AUTHORIZE);
        }
        finally
        {
            AuthenticatedUser.permissionsCache.setValidity(0);
            DatabaseDescriptor.getRawConfig().auth_cache_warming_enabled = warming;
        }
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
