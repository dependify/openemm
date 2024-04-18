package com.agnitas.emm.core.components.web;

import com.agnitas.emm.core.components.form.MailingImagesFormSearchParams;
import com.agnitas.emm.core.components.service.ComMailingComponentsService;
import com.agnitas.emm.core.maildrop.service.MaildropService;
import com.agnitas.emm.core.mailing.service.ComMailingBaseService;
import com.agnitas.emm.core.mailinglist.service.MailinglistApprovalService;
import com.agnitas.util.preview.PreviewImageService;
import com.agnitas.web.perm.annotations.PermissionMapping;
import org.agnitas.emm.core.commons.util.ConfigService;
import org.agnitas.service.UserActivityLogService;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.SessionAttributes;

@Controller
@RequestMapping("/mailing/{mailingId:\\d+}/images")
@PermissionMapping("mailing.images")
@SessionAttributes(types = MailingImagesFormSearchParams.class)
public class MailingImagesControllerOpenemm extends MailingImagesController {

    public MailingImagesControllerOpenemm(ComMailingBaseService mailingBaseService, PreviewImageService previewImageService,
                                          MaildropService maildropService, UserActivityLogService userActivityLogService,
                                          ComMailingComponentsService mailingComponentsService,
                                          MailinglistApprovalService mailinglistApprovalService, ConfigService configService) {
        super(mailingBaseService, previewImageService, maildropService, userActivityLogService,
                mailingComponentsService, configService, mailinglistApprovalService);
    }
}
