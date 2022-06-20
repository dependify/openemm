/*

    Copyright (C) 2022 AGNITAS AG (https://www.agnitas.org)

    This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
    This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.
    You should have received a copy of the GNU Affero General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

*/

package org.agnitas.emm.core.binding.service;

import org.agnitas.emm.core.velocity.VelocityCheck;


public class BindingModel {
	public interface SetGroup {
    	// do nothing
    }

	public interface GetGroup {
    	// do nothing
    }
	
	public interface ListGroup {
    	// do nothing
    }

	private int companyId;
	private int customerId;
	private int mailinglistId;
	private int mediatype;
	private int status;					// TODO Change status to type UserStatus
	private String userType;
	private String remark;
	private int exitMailingId;
	private int actionId;

	public int getCompanyId() {
		return companyId;
	}

	public void setCompanyId(@VelocityCheck int companyId) {
		this.companyId = companyId;
	}

	public int getCustomerId() {
		return customerId;
	}

	public void setCustomerId(int customerId) {
		this.customerId = customerId;
	}

	public int getMailinglistId() {
		return mailinglistId;
	}

	public void setMailinglistId(int mailinglistId) {
		this.mailinglistId = mailinglistId;
	}

	public int getMediatype() {
		return mediatype;
	}

	public void setMediatype(int mediatype) {
		this.mediatype = mediatype;
	}

	// TODO Change return type to org.agnitas.dao.UserStatus
	public int getStatus() {
		return status;
	}

	// TODO Change parameter to org.agnitas.dao.UserStatus
	public void setStatus(int status) {
		this.status = status;
	}

	public String getUserType() {
		return userType;
	}

	public void setUserType(String userType) {
		this.userType = userType;
	}

	public String getRemark() {
		return remark;
	}

	public void setRemark(String remark) {
		this.remark = remark;
	}

	public int getExitMailingId() {
		return exitMailingId;
	}

	public void setExitMailingId(int exitMailingId) {
		this.exitMailingId = exitMailingId;
	}

	public int getActionId() {
		return actionId;
	}

	public void setActionId(int actionId) {
		this.actionId = actionId;
	}

}
