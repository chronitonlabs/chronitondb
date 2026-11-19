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

package org.chronitondb.shape;

import java.util.ArrayList;
import java.util.List;

/**
 * Fixture for shape-check.sh --self-test: the duplicated block of the Duplicate fixtures, hidden from CPD by comments. The marker is the finding.
 */
public class SuppressedDuplicate
{
    // CPD-OFF
    private final List<Integer> values = new ArrayList<>();

    public void fill()
    {
        values.add(1);
        values.add(2);
        values.add(3);
        values.add(4);
        values.add(5);
        values.add(6);
        values.add(7);
        values.add(8);
        values.add(9);
        values.add(10);
        values.add(11);
        values.add(12);
        values.add(13);
        values.add(14);
    }
}
