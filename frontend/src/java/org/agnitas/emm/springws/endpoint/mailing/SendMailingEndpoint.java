/*

    Copyright (C) 2022 AGNITAS AG (https://www.agnitas.org)

    This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
    This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.
    You should have received a copy of the GNU Affero General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

*/

package org.agnitas.emm.springws.endpoint.mailing;

import java.util.ArrayList;
import java.util.List;

import org.agnitas.emm.core.commons.util.ConfigService;
import org.agnitas.emm.core.commons.util.ConfigValue;
import org.agnitas.emm.core.mailing.service.MailingModel;
import org.agnitas.emm.core.useractivitylog.UserAction;
import org.agnitas.emm.springws.endpoint.BaseEndpoint;
import org.agnitas.emm.springws.endpoint.Namespaces;
import org.agnitas.emm.springws.jaxb.SendMailingRequest;
import org.agnitas.emm.springws.jaxb.SendMailingResponse;
import org.agnitas.emm.springws.util.SecurityContextAccess;
import org.agnitas.emm.springws.util.UserActivityLogAccess;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.ws.server.endpoint.annotation.Endpoint;
import org.springframework.ws.server.endpoint.annotation.PayloadRoot;
import org.springframework.ws.server.endpoint.annotation.RequestPayload;
import org.springframework.ws.server.endpoint.annotation.ResponsePayload;

import com.agnitas.emm.core.mailing.service.MailingService;

@Endpoint
public class SendMailingEndpoint extends BaseEndpoint {

	private MailingService mailingService;
	private ConfigService configService;
	private SecurityContextAccess securityContextAccess;
	private UserActivityLogAccess userActivityLogAccess;

	public SendMailingEndpoint(@Qualifier("MailingService") MailingService mailingService, ConfigService configService, final SecurityContextAccess securityContextAccess, final UserActivityLogAccess userActivityLogAccess) {
		this.mailingService = mailingService;
		this.configService = configService;
		this.securityContextAccess = securityContextAccess;
		this.userActivityLogAccess = userActivityLogAccess;
	}

	@PayloadRoot(namespace = Namespaces.AGNITAS_ORG, localPart = "SendMailingRequest")
	public @ResponsePayload SendMailingResponse sendMailing(@RequestPayload SendMailingRequest request) throws Exception {
		if (this.securityContextAccess.getWebserviceUserCompanyId() == 1 && !configService.getBooleanValue(ConfigValue.System_License_AllowMailingSendForMasterCompany)) {
    		throw new Exception("error.company.mailings.sent.forbidden");
    	} else {
			MailingModel model = new MailingModel();
			model.setCompanyId(this.securityContextAccess.getWebserviceUserCompanyId());
			model.setMailingId(request.getMailingID());
			model.setMaildropStatus(request.getRecipientsType());
			model.setSendDate(request.getSendDate());
			model.setBlocksize(null != request.getBlocksize() ? request.getBlocksize() : 0);
			model.setStepping(null != request.getStepping() ? request.getStepping() : 0);
	
			List<UserAction> userActions = new ArrayList<>();
			mailingService.sendMailing(model, userActions);
			this.userActivityLogAccess.writeLog(userActions);
	
			return new SendMailingResponse();
    	}
	}
}
