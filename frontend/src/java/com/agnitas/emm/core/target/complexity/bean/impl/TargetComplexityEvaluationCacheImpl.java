/*

    Copyright (C) 2022 AGNITAS AG (https://www.agnitas.org)

    This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
    This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.
    You should have received a copy of the GNU Affero General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

*/

package com.agnitas.emm.core.target.complexity.bean.impl;

import java.util.HashMap;
import java.util.Map;
import java.util.Objects;

import com.agnitas.emm.core.target.complexity.bean.CustomerTableColumnMetadata;
import com.agnitas.emm.core.target.complexity.bean.TargetComplexityEvaluationCache;

public class TargetComplexityEvaluationCacheImpl implements TargetComplexityEvaluationCache {
    private Map<String, CustomerTableColumnMetadata> customerTableColumnMetadataMap = new HashMap<>();
    private Map<String, Boolean> referenceTableKeyColumnIsIndexedMap = new HashMap<>();

    @Override
    public CustomerTableColumnMetadata getCustomerTableColumnMetadata(String column) {
        return customerTableColumnMetadataMap.get(Objects.requireNonNull(column).toLowerCase());
    }

    @Override
    public void putCustomerTableColumnMetadata(String column, CustomerTableColumnMetadata metadata) {
        customerTableColumnMetadataMap.put(Objects.requireNonNull(column).toLowerCase(), Objects.requireNonNull(metadata));
    }

    @Override
    public Boolean isReferenceTableKeyColumnIndexed(String table) {
        return referenceTableKeyColumnIsIndexedMap.get(Objects.requireNonNull(table));
    }

    @Override
    public void setReferenceTableKeyColumnIndexed(String table, Boolean isIndexed) {
        referenceTableKeyColumnIsIndexedMap.put(Objects.requireNonNull(table), Objects.requireNonNull(isIndexed));
    }
}
