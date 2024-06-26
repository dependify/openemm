/*

    Copyright (C) 2022 AGNITAS AG (https://www.agnitas.org)

    This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
    This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.
    You should have received a copy of the GNU Affero General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

*/

package org.agnitas.emm.core.binding.service;

import java.util.List;

import org.agnitas.beans.BindingEntry;
import org.agnitas.dao.UserStatus;
import org.agnitas.emm.core.mailinglist.service.impl.MailinglistException;


public interface BindingService {

	BindingEntry getBinding(BindingModel model);

	void setBinding(BindingModel model) throws MailinglistException;
	
	void deleteBinding(BindingModel model);
	
	List<BindingEntry> getBindings(BindingModel model);
	
	void updateBindingStatusByEmailPattern( int companyId, String emailPattern, UserStatus userStatus, String remark) throws BindingServiceException;
}
