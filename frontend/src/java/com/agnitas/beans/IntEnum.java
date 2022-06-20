/*

    Copyright (C) 2022 AGNITAS AG (https://www.agnitas.org)

    This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
    This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.
    You should have received a copy of the GNU Affero General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

*/

package com.agnitas.beans;

public interface IntEnum {
    static <T extends Enum<T> & IntEnum> T fromId(Class<T> clz, int id) {
        return fromId(clz, id, true);
    }

    static <T extends Enum<T> & IntEnum> T fromId(Class<T> clz, int id, boolean safe) {
        for (T value : clz.getEnumConstants()) {
            if (id == value.getId()) {
                return value;
            }
        }

        if (safe) {
            return null;
        }

        throw new IllegalArgumentException(clz.getSimpleName() + ".class: unknown id: " + id);
    }

    int getId();
}
