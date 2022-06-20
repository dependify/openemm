/*

    Copyright (C) 2022 AGNITAS AG (https://www.agnitas.org)

    This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
    This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.
    You should have received a copy of the GNU Affero General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

*/

package org.agnitas.util.importvalues;

import org.agnitas.util.DateUtilities;

/**
 * Values for dateFormat property of import profile
 */
public enum DateFormat {
	ddMMyyyy("dd.MM.yyyy", 1),
	ddMMyy("dd.MM.yy", 6),
	ddMMyyyyHHmm("dd.MM.yyyy HH:mm", 0),
	ddMMyyyyHHmmss("dd.MM.yyyy HH:mm:ss", 5),
	
	MMddyyyy("MM/dd/yyyy", 11),
	MMddyy("MM/dd/yy", 12),
	MMddyyyyhhmm("MM/dd/yyyy HH:mm", 10),
	MMddyyyyhhmmss("MM/dd/yyyy HH:mm:ss", 7),
	
	yyyyMMdd("yyyyMMdd", 2),
	yyyy_MM_dd("yyyy-MM-dd", 8),
	yyyyMMddHHmm("yyyyMMdd HH:mm", 3),
	yyyyMMddHHmmss("yyyy-MM-dd HH:mm:ss", 4),
	
	ISO8601(DateUtilities.ISO_8601_DATETIME_FORMAT, 9);

	/**
	 * The value that will be used during csv-file parsing
	 */
	private String value;

	/**
	 * Id value used for storage in db
	 */
	private int id;

	public String getValue() {
		return value;
	}

	public String getPublicValue() {
		return value;
	}

	public int getIntValue() {
		return id;
	}

	DateFormat(String value, int id) {
		this.value = value;
		this.id = id;
	}

	public static DateFormat getDateFormatById(int id) throws Exception {
		for (DateFormat item : DateFormat.values()) {
			if (item.getIntValue() == id) {
				return item;
			}
		}
		throw new Exception("Invalid DateFormat id: " + id);
	}

	public static DateFormat getDateFormatByValue(String value) throws Exception {
		for (DateFormat item : DateFormat.values()) {
			if (item.value.equals(value)) {
				return item;
			}
		}
		throw new Exception("Invalid DateFormat value: " + value);
	}
}
