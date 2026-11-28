# Copyright 2026 AxonOps Limited
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from dtest import Tester


class TestLineCluster(Tester):
    """A cluster of the line that ccm starts answers a write and a read."""

    def test_write_and_read(self):
        self.cluster.populate(2).start()
        session = self.patient_cql_connection(self.cluster.nodelist()[0])
        session.execute("CREATE KEYSPACE ks WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 2}")
        session.execute("CREATE TABLE ks.tbl (pk int PRIMARY KEY, v int)")
        session.execute("INSERT INTO ks.tbl (pk, v) VALUES (1, 1)")
        assert [row.v for row in session.execute("SELECT v FROM ks.tbl WHERE pk = 1")] == [1]
