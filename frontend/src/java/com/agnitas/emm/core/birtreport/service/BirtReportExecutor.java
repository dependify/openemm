/*

    Copyright (C) 2022 AGNITAS AG (https://www.agnitas.org)

    This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
    This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.
    You should have received a copy of the GNU Affero General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

*/

package com.agnitas.emm.core.birtreport.service;

import java.io.File;
import java.net.MalformedURLException;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.Map;

import org.agnitas.emm.core.commons.util.ConfigValue;
import org.agnitas.util.AgnUtils;
import org.agnitas.util.DateUtilities;
import org.agnitas.util.FileDownload;
import org.agnitas.util.HttpUtils;
import org.agnitas.web.ExportException;
import org.apache.commons.httpclient.HttpClient;
import org.apache.commons.io.FileUtils;
import org.apache.commons.lang3.StringUtils;
import org.apache.http.impl.client.CloseableHttpClient;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import com.agnitas.emm.core.JavaMailAttachment;
import com.agnitas.emm.core.birtreport.bean.ComBirtReport;
import com.agnitas.messages.I18nString;
import com.agnitas.service.impl.ServiceLookupFactory;

public class BirtReportExecutor implements Runnable {
	private static final transient Logger logger = LogManager.getLogger(BirtReportExecutor.class);

	private ServiceLookupFactory serviceLookupFactory;
	
	private ComBirtReport birtReport;
	
	private Map<String, String> urlsMap;
	
	public BirtReportExecutor(ServiceLookupFactory serviceLookupFactory, ComBirtReport birtReport, Map<String, String> urlsMap) {
		this.serviceLookupFactory = serviceLookupFactory;
		this.birtReport = birtReport;
		this.urlsMap = urlsMap;
	}

	@Override
	public void run() {
		executeBirtReport();
	}
	
	public void executeBirtReport() {
		if(useNewHttpClient()) {
			executeBirtReport_Client4();
		} else {
			executeBirtReport_Client3();
		}
	}
	
	private final boolean useNewHttpClient() {
		return this.serviceLookupFactory.getBeanConfigService().getBooleanValue(ConfigValue.Development.BirtReportUseNewHttpClient);
	}
	
	private final void executeBirtReport_Client4() {
		updateNextStart();
		
		if(!serviceLookupFactory.getBeanBirtReportService().announceStart(this.birtReport)) {
			logger.info(String.format(
					"Cannot start BIRT report job '%s' (id %d) on host '%s'. Maybe the report is running on some other host at the moment.", 
					birtReport.getShortname(),
					birtReport.getId(),
					AgnUtils.getHostName()));
			return;
		}

		final String birtUrl = determineBirtUrl(this.birtReport.getCompanyID());
		
		try(final CloseableHttpClient httpClient = FileDownload.createHttpClientForDownload(birtUrl)) {
			final List<JavaMailAttachment> attachments = downloadReportFiles(httpClient);
			
			sendReportMail(attachments);
			
			birtReport.setLastresult("OK");
			serviceLookupFactory.getBeanBirtReportService().announceEnd(birtReport);
		} catch (Throwable t) {
			reportError(t);
			throw new ExportException(false, null, t.getMessage());
		}
	}

	private final void updateNextStart() {
		if (StringUtils.isBlank(birtReport.getIntervalpattern())) {
			birtReport.setNextStart(null);
		} else {
			birtReport.setNextStart(DateUtilities.calculateNextJobStart(birtReport.getIntervalpattern()));
		}
	}
	
	private final String determineBirtUrl(final int companyID) {
		String birtUrl = serviceLookupFactory.getBeanConfigService().getValue(ConfigValue.BirtUrlIntern, companyID);
		
		if (StringUtils.isBlank(birtUrl)) {
			birtUrl = serviceLookupFactory.getBeanConfigService().getValue(ConfigValue.BirtUrl, companyID);
		}
		
		return birtUrl;
	}
	
	private final List<JavaMailAttachment> downloadReportFiles(final CloseableHttpClient httpClient) {
		final List<JavaMailAttachment> attachments = new ArrayList<>();
		
        for (final Map.Entry<String, String> entry : urlsMap.entrySet()) {
        	try {
        		logger.info(String.format("BIRT report %d: Downloading report frm '%s'", birtReport.getId(), entry.getValue()));
        		
				final File temporaryFile = serviceLookupFactory.getBeanBirtStatisticsService().getBirtReportTmpFile(birtReport.getId(), entry.getValue(), httpClient, logger);
				
				attachments.add(new JavaMailAttachment(entry.getKey(), FileUtils.readFileToByteArray(temporaryFile), String.format("application/%s", birtReport.getFormatName())));
        	} catch( Exception e) {
        		logger.error( "Error retrieving report data for BIRT report " + birtReport.getId() + "\nURL:" + entry.getValue(), e);
        	}
        }
        
        return attachments;
	}
	
	private final void sendReportMail(final List<JavaMailAttachment> attachments) {
        final String emailRecipientStringList = StringUtils.join(birtReport.getEmailRecipientList(), ",");
        final String emailSubject = birtReport.getEmailSubject();
        
        String content = "";
        if (StringUtils.isBlank(birtReport.getEmailDescription())) {
        	content = I18nString.getLocaleString("report.body.text", new Locale(birtReport.getLanguage()));
        } else {
        	content = birtReport.getEmailDescription();
        }
        
        final String emailDescription = content;
        serviceLookupFactory.getBeanJavaMailService().sendEmail(birtReport.getCompanyID(), emailRecipientStringList, emailSubject, emailDescription, emailDescription, attachments.toArray(new JavaMailAttachment[0]));
		serviceLookupFactory.getBeanBirtReportService().logSentReport(birtReport);
	}
	
	private final void executeBirtReport_Client3() {
    	try {
    		updateNextStart();
			
			if (serviceLookupFactory.getBeanBirtReportService().announceStart(birtReport)) {
				final String birtUrl = determineBirtUrl(birtReport.getCompanyID());
		
				HttpClient httpClient;
				try {
					httpClient = HttpUtils.initializeHttpClient(birtUrl + "/run");
				} catch (MalformedURLException e) {
					logger.fatal("Malformed report URL reported in report ID: " + birtReport.getId() + ": " + e.getMessage(), e);
					for (Map.Entry<String, String> entry : urlsMap.entrySet()) {
						logger.fatal(String.format("  + Report '%s' : %s", entry.getKey(), entry.getValue()));
					}
					return;
				}
		
				final List<JavaMailAttachment> attachments = new ArrayList<>();
		        for (final Map.Entry<String, String> entry : urlsMap.entrySet()) {
		        	try {
		                logger.info("BIRT report for sending\nreport id: " + birtReport.getId() + "\nURL:" + entry.getValue());
						File temporaryFile = serviceLookupFactory.getBeanBirtStatisticsService().getBirtReportTmpFile(birtReport.getId(), entry.getValue(), httpClient, logger);
		        		attachments.add(new JavaMailAttachment(entry.getKey(), FileUtils.readFileToByteArray(temporaryFile), String.format("application/%s", birtReport.getFormatName())));
		        	} catch( Exception e) {
		        		logger.error( "Error retrieving report data for BIRT report " + birtReport.getId() + "\nURL:" + entry.getValue(), e);
		        	}
		        }
		
		        final String emailRecipientStringList = StringUtils.join(birtReport.getEmailRecipientList(), ",");
		        final String emailSubject = birtReport.getEmailSubject();
		        String content = "";
		        if (StringUtils.isBlank(birtReport.getEmailDescription())) {
		        	content = I18nString.getLocaleString("report.body.text", new Locale(birtReport.getLanguage()));
		        } else {
		        	content = birtReport.getEmailDescription();
		        }
		        final String emailDescription = content;
		        serviceLookupFactory.getBeanJavaMailService().sendEmail(birtReport.getCompanyID(), emailRecipientStringList, emailSubject, emailDescription, emailDescription, attachments.toArray(new JavaMailAttachment[0]));
				serviceLookupFactory.getBeanBirtReportService().logSentReport(birtReport);
				
				birtReport.setLastresult("OK");
				serviceLookupFactory.getBeanBirtReportService().announceEnd(birtReport);
			} else {
				logger.info("Cannot start BirtReportJob " + birtReport.getShortname() + "(" + birtReport.getId() + ") on host '" + AgnUtils.getHostName() + "'. Maybe some other host executes it already");
			}
		} catch (Throwable t) {
			reportError(t);
			throw new ExportException(false, null, t.getMessage());
		}
	}
	
	private final void reportError(final Throwable t) {
		logger.error("Error in " + this.getClass().getName() + ": " + t.getMessage(), t);
		// Watchout: NullpointerExceptions have Message "null", which would result in another jobrun, so enter some additional text (classname)
		birtReport.setLastresult(t.getClass().getSimpleName() + ": " + t.getMessage() + "\n" + AgnUtils.getStackTraceString(t));
		serviceLookupFactory.getBeanJavaMailService().sendExceptionMail(birtReport.getCompanyID(), "BirtReport error", t);
		try {
			serviceLookupFactory.getBeanBirtReportService().announceEnd(birtReport);
		} catch (Exception e1) {
			logger.error("Cannot announce BirtReport end: " + e1.getMessage(), e1);
		}
	}
}
