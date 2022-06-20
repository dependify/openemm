/*

    Copyright (C) 2022 AGNITAS AG (https://www.agnitas.org)

    This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
    This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.
    You should have received a copy of the GNU Affero General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

*/

package com.agnitas.emm.landingpage.dao;

import java.sql.ResultSet;
import java.sql.SQLException;

import org.springframework.jdbc.core.RowMapper;

import com.agnitas.emm.landingpage.beans.RedirectSettings;

final class RedirectSettingsRowMapper implements RowMapper<RedirectSettings> {

	@Override
	public final RedirectSettings mapRow(final ResultSet resultSet, final int row) throws SQLException {
		final String url = resultSet.getString("landingpage");
		final int httpCode = resultSet.getInt("http_code");
		
		return new RedirectSettings(url, httpCode);
	}

}
