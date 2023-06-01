/*

    Copyright (C) 2022 AGNITAS AG (https://www.agnitas.org)

    This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
    This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.
    You should have received a copy of the GNU Affero General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

*/

package com.agnitas.service;

import java.util.List;
import java.util.Map;
import java.util.Set;

import org.agnitas.emm.core.velocity.VelocityCheck;
import org.apache.commons.collections4.map.CaseInsensitiveMap;

import com.agnitas.beans.ProfileField;
import com.agnitas.beans.ProfileFieldMode;

public interface ColumnInfoService {
	ProfileField getColumnInfo(@VelocityCheck int companyID, String column) throws Exception;
	
	List<ProfileField> getColumnInfos(@VelocityCheck int companyID) throws Exception;
	
	List<ProfileField> getColumnInfos(@VelocityCheck int companyID, int adminID) throws Exception;

	CaseInsensitiveMap<String, ProfileField> getColumnInfoMap(@VelocityCheck int companyID) throws Exception;
	
	CaseInsensitiveMap<String, ProfileField> getColumnInfoMap(@VelocityCheck int companyID, int adminID) throws Exception;
	
	ProfileField getColumnInfo(@VelocityCheck int companyID, String column, int adminID) throws Exception;
	
	List<ProfileField> getComColumnInfos(@VelocityCheck int companyID) throws Exception;

    List<ProfileField> getComColumnInfos(@VelocityCheck int companyID, int adminID) throws Exception;

    List<ProfileField> getComColumnInfos(@VelocityCheck int companyID, int adminID, boolean customSorting) throws Exception;

	List<ProfileField> getHistorizedComColumnInfos(@VelocityCheck int companyID) throws Exception;

    CaseInsensitiveMap<String, ProfileField> getComColumnInfoMap(@VelocityCheck int companyID) throws Exception;
    
	CaseInsensitiveMap<String, ProfileField> getComColumnInfoMap(@VelocityCheck int companyID, int adminId) throws Exception;

	Map<Integer, ProfileFieldMode> getProfileFieldAdminPermissions(int companyID, String columnName) throws Exception;

	void storeProfileFieldAdminPermissions(int companyID, String column, Set<Integer> readOnlyUsers, Set<Integer> notVisibleUsers);
}