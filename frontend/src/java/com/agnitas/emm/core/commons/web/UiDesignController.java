/*

    Copyright (C) 2022 AGNITAS AG (https://www.agnitas.org)

    This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
    This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.
    You should have received a copy of the GNU Affero General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

*/

package com.agnitas.emm.core.commons.web;

import com.agnitas.beans.Admin;
import com.agnitas.emm.core.Permission;
import com.agnitas.emm.core.admin.service.AdminService;
import com.agnitas.web.dto.BooleanResponseDto;
import com.agnitas.web.perm.annotations.PermissionMapping;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.ResponseBody;

@Controller
@RequestMapping("/ui-design")
@PermissionMapping("ui.design")
public class UiDesignController {

    private final AdminService adminService;

    public UiDesignController(AdminService adminService) {
        this.adminService = adminService;
    }

    @PostMapping("/switch.action")
    public @ResponseBody BooleanResponseDto switchDesign(Admin admin) {
        if (admin.isRedesignedUiUsed()) {
            adminService.revokePermission(admin, Permission.USE_REDESIGNED_UI);
        } else {
            adminService.grantPermission(admin, Permission.USE_REDESIGNED_UI);
        }

        return new BooleanResponseDto(true);
    }
}
