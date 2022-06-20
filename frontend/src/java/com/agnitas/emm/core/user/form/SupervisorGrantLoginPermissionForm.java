/*

    Copyright (C) 2022 AGNITAS AG (https://www.agnitas.org)

    This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
    This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.
    You should have received a copy of the GNU Affero General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

*/

package com.agnitas.emm.core.user.form;

public class SupervisorGrantLoginPermissionForm {

    private int departmentID;
    private String expireDateLocalized;
    private String limit;

    public int getDepartmentID() {
        return this.departmentID;
    }

    public void setDepartmentID(int id) {
        this.departmentID = id;
    }

    public String getExpireDateLocalized() {
        return this.expireDateLocalized;
    }

    public void setExpireDateLocalized(String date) {
        this.expireDateLocalized = date;
    }

    public void setLimit(String value) {
        this.limit = value;
    }

    public String getLimit() {
        return this.limit;
    }
}
