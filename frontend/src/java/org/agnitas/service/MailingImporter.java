/*

    Copyright (C) 2019 AGNITAS AG (https://www.agnitas.org)

    This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
    This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.
    You should have received a copy of the GNU Affero General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

*/

package org.agnitas.service;

import java.io.InputStream;

import com.agnitas.util.TimingLogger;

public interface MailingImporter {
	
	ImportResult importMailingFromJson(int companyID, InputStream input, boolean importAsTemplate, boolean overwriteTemplate, boolean isGrid) throws Exception;

	ImportResult importMailingFromJson(int companyID, InputStream input, boolean importAsTemplate, String shortName, String description, boolean overwriteTemplate, boolean isGrid) throws Exception;
	
	ImportResult importMailingFromJson(int companyID, InputStream input, boolean importAsTemplate, String shortName, String description, boolean overwriteTemplate, boolean checkIsTemplate, boolean isGrid) throws Exception;

	@Deprecated // Not for common use. Used by EMM-8126 only to measure timing.
	ImportResult importMailingFromJson(final TimingLogger timingLogger, int companyID, InputStream input, boolean importAsTemplate, boolean overwriteTemplate, boolean isGrid) throws Exception;
	@Deprecated // Not for common use. Used by EMM-8126 only to measure timing.
	ImportResult importMailingFromJson(final TimingLogger timingLogger, int companyID, InputStream input, boolean importAsTemplate, String shortName, String description, boolean overwriteTemplate, boolean isGrid) throws Exception;
	@Deprecated // Not for common use. Used by EMM-8126 only to measure timing.
	ImportResult importMailingFromJson(final TimingLogger timingLogger, int companyID, InputStream input, boolean importAsTemplate, String shortName, String description, boolean overwriteTemplate, boolean checkIsTemplate, boolean isGrid) throws Exception;
}
