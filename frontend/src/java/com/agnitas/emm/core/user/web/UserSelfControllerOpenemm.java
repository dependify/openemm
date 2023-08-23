package com.agnitas.emm.core.user.web;

import com.agnitas.dao.AdminGroupDao;
import com.agnitas.dao.AdminPreferencesDao;
import com.agnitas.dao.ComCompanyDao;
import com.agnitas.dao.EmmLayoutBaseDao;
import com.agnitas.emm.core.admin.service.AdminService;
import com.agnitas.emm.core.logon.service.ComLogonService;
import com.agnitas.emm.core.user.service.UserSelfService;
import com.agnitas.web.perm.annotations.PermissionMapping;
import org.agnitas.emm.core.commons.password.PasswordCheck;
import org.agnitas.emm.core.commons.util.ConfigService;
import org.agnitas.service.UserActivityLogService;
import org.agnitas.service.WebStorage;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestMapping;

@Controller
@RequestMapping("/user/self")
@PermissionMapping("user.self")
public class UserSelfControllerOpenemm extends UserSelfController {

    public UserSelfControllerOpenemm(WebStorage webStorage, ComCompanyDao companyDao, AdminPreferencesDao adminPreferencesDao, AdminService adminService, AdminGroupDao adminGroupDao, ConfigService configService, UserActivityLogService userActivityLogService, PasswordCheck passwordCheck, EmmLayoutBaseDao layoutBaseDao, ComLogonService logonService, UserSelfService userSelfService) {
        super(webStorage, companyDao, adminPreferencesDao, adminService, adminGroupDao, configService, userActivityLogService, passwordCheck, layoutBaseDao, logonService, userSelfService);
    }
}