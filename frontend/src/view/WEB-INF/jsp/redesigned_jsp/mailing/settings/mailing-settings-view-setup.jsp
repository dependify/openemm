<%@ page language="java" contentType="text/html; charset=utf-8" buffer="64kb" errorPage="/errorRedesigned.action" %>
<%@ taglib prefix="c"   uri="http://java.sun.com/jsp/jstl/core" %>
<%@ taglib prefix="emm" uri="https://emm.agnitas.de/jsp/jsp/common" %>
<%@ taglib prefix="mvc" uri="https://emm.agnitas.de/jsp/jsp/spring" %>

<%--@elvariable id="mailingSettingsForm" type="com.agnitas.emm.core.mailing.forms.MailingSettingsForm"--%>
<%--@elvariable id="limitedRecipientOverview" type="java.lang.Boolean"--%>
<%--@elvariable id="gridTemplateId" type="java.lang.Integer"--%>
<%--@elvariable id="isPostMailing" type="java.lang.Boolean"--%>
<%--@elvariable id="undoAvailable" type="java.lang.Boolean"--%>
<%--@elvariable id="isTemplate" type="java.lang.Boolean"--%>
<%--@elvariable id="isSettingsReadonly" type="java.lang.Boolean"--%>
<%--@elvariable id="workflowId" type="java.lang.Integer"--%>
<%--@elvariable id="mailingId" type="java.lang.Integer"--%>

<c:set var="isMailingGrid" value="${gridTemplateId > 0}"/>

<c:url var="mailingsOverviewLink" value="/mailing/list.action?restoreSort=true"/>

<c:set var="mailingExists" value="${mailingId ne 0}"/>

<c:set var="workflowParams" value="${emm:getWorkflowParamsWithDefault(pageContext.request, workflowId)}" scope="request"/>
<c:set var="workflowDriven" value="${workflowParams.workflowId gt 0}" scope="request" />

<c:set var="sidemenu_active" 		value="Mailings" 				scope="request" />
<c:set var="isBreadcrumbsShown" 	value="true" 					scope="request" />
<c:set var="agnBreadcrumbsRootKey"	value="Mailings" 				scope="request" />
<c:set var="agnBreadcrumbsRootUrl" 	value="${mailingsOverviewLink}"	scope="request" />
<c:set var="agnEditViewKey"         value="mailing-settings"        scope="request"/>

<c:url var="templatesOverviewLink" value="/mailing/list.action">
    <c:param name="restoreSort" value="true"/>
    <c:param name="forTemplates" value="true"/>
</c:url>

<c:choose>
    <%-- Template navigation --%>
    <c:when test="${isTemplate}">
        <emm:Permission token="template.show"/>

		<c:set var="agnTitleKey" 			value="Template" 	scope="request" />
        <c:set var="agnSubtitleKey" 		value="Template" 	scope="request" />
        <c:set var="sidemenu_sub_active"	value="Templates" 	scope="request" />
        <c:set var="agnHelpKey" 			value="newTemplate"	scope="request" />

        <c:choose>
            <c:when test="${mailingExists}">
				<c:choose>
					<c:when test="${isPostMailing}">
						<c:set var="agnNavigationKey" value="templateView_post" scope="request" />
					</c:when>
					<c:otherwise>
						<c:set var="agnNavigationKey" value="templateView" scope="request" />
					</c:otherwise>
				</c:choose>
				<c:set var="agnHighlightKey" 	value="Template" scope="request" />

                <emm:instantiate var="agnNavHrefParams" type="java.util.LinkedHashMap" scope="request">
                    <c:set target="${agnNavHrefParams}" property="mailingID" value="${mailingId}"/>
                    <c:set target="${agnNavHrefParams}" property="init" value="true"/>
                </emm:instantiate>
                
                <emm:instantiate var="agnBreadcrumbs" type="java.util.LinkedHashMap" scope="request">
                    <emm:instantiate var="agnBreadcrumb" type="java.util.LinkedHashMap">
                        <c:set target="${agnBreadcrumbs}" property="0" value="${agnBreadcrumb}"/>
                        <c:set target="${agnBreadcrumb}" property="textKey" value="Templates"/>
                        <c:set target="${agnBreadcrumb}" property="url" value="${templatesOverviewLink}"/>
                    </emm:instantiate>

                    <emm:instantiate var="agnBreadcrumb" type="java.util.LinkedHashMap">
                        <c:set target="${agnBreadcrumbs}" property="1" value="${agnBreadcrumb}"/>
                        <c:set target="${agnBreadcrumb}" property="text" value="${mailingSettingsForm.shortname}"/>
                    </emm:instantiate>
                </emm:instantiate>
            </c:when>
            <c:otherwise>
                <c:set var="agnNavigationKey"	value="TemplateNew" 			scope="request" />
                <c:set var="agnHighlightKey" 	value="mailing.New_Template"	scope="request" />

                <emm:instantiate var="agnBreadcrumbs" type="java.util.LinkedHashMap" scope="request">
                    <emm:instantiate var="agnBreadcrumb" type="java.util.LinkedHashMap">
                        <c:set target="${agnBreadcrumbs}" property="0" value="${agnBreadcrumb}"/>
                        <c:set target="${agnBreadcrumb}" property="textKey" value="mailing.New_Template"/>
                    </emm:instantiate>
                </emm:instantiate>
            </c:otherwise>
        </c:choose>
    </c:when>

    <%-- Mailing navigation --%>
    <c:otherwise>
        <emm:Permission token="mailing.show"/>

		<c:set var="agnTitleKey" 	value="Mailing" 						scope="request" />
        <c:set var="agnSubtitleKey"	value="Mailing" 						scope="request" />
        <c:set var="agnHelpKey" 	value="mailingBase"	                    scope="request" />
		
        <c:choose>
            <c:when test="${mailingExists}">
                <c:choose>
		            <c:when test="${isPostMailing}">
		                <c:set var="agnNavigationKey" value="mailingView_post"                scope="request" />
		            </c:when>
                    <c:when test="${limitedRecipientOverview}">
                        <c:set var="agnNavigationKey" value="mailingView_DisabledMailinglist" scope="request" />
                    </c:when>
                    <c:otherwise>
                        <c:set var="agnNavigationKey" value="mailingView"                     scope="request" />
                    </c:otherwise>
                </c:choose>

                <emm:instantiate var="agnNavHrefParams" type="java.util.LinkedHashMap" scope="request">
                    <c:set target="${agnNavHrefParams}" property="mailingID" value="${mailingId}"/>
                    <c:set target="${agnNavHrefParams}" property="init" value="true"/>
                </emm:instantiate>
				<c:set var="sidemenu_sub_active"	value="none" 			 scope="request" />
                <c:set var="agnHighlightKey" 		value="default.settings" scope="request" />
                
                <emm:instantiate var="agnBreadcrumbs" type="java.util.LinkedHashMap" scope="request">
                    <emm:instantiate var="agnBreadcrumb" type="java.util.LinkedHashMap">
                        <c:set target="${agnBreadcrumbs}" property="0" value="${agnBreadcrumb}"/>
                        <c:set target="${agnBreadcrumb}" property="text" value="${mailingSettingsForm.shortname}"/>
                    </emm:instantiate>
                </emm:instantiate>
            </c:when>
            <c:otherwise>
                <c:set var="agnNavigationKey" 		value="MailingNew" 			scope="request" />
                <c:set var="sidemenu_sub_active"	value="mailing.New_Mailing" scope="request" />
                <c:set var="agnHighlightKey" 		value="mailing.New_Mailing"	scope="request" />

                <emm:instantiate var="agnBreadcrumbs" type="java.util.LinkedHashMap" scope="request">
                    <emm:instantiate var="agnBreadcrumb" type="java.util.LinkedHashMap">
                        <c:set target="${agnBreadcrumbs}" property="0" value="${agnBreadcrumb}"/>
                        <c:set target="${agnBreadcrumb}" property="textKey" value="mailing.New_Mailing"/>
                    </emm:instantiate>
                </emm:instantiate>
            </c:otherwise>
        </c:choose>
    </c:otherwise>
</c:choose>

<%-- Grid Mailing --%>
<c:if test="${isMailingGrid}">
    <c:set var="agnTitleKey" 		value="Mailing" 	scope="request" />
    <c:set var="agnSubtitleKey" 	value="Mailings"	scope="request" />
    <c:set var="agnHelpKey"         value="mailingBase" scope="request" />
    
    <c:if test="${mailingExists}">
        <%@ include file="../fragments/mailing-grid-navigation.jspf" %>

        <emm:instantiate var="agnNavHrefParams" type="java.util.LinkedHashMap" scope="request">
            <c:set target="${agnNavHrefParams}" property="templateID" value="${gridTemplateId}"/>
            <c:set target="${agnNavHrefParams}" property="mailingID" value="${mailingId}"/>
        </emm:instantiate>

        <c:set var="sidemenu_sub_active"	value="none" 		                scope="request" />
        <c:set var="agnHighlightKey" 		value="default.settings" 			scope="request" />
        <c:set var="agnHelpKey" 			value="mailingBase" 				scope="request" />

        <emm:instantiate var="agnBreadcrumbs" type="java.util.LinkedHashMap" scope="request">
            <emm:instantiate var="agnBreadcrumb" type="java.util.LinkedHashMap">
                <c:set target="${agnBreadcrumbs}" property="0" value="${agnBreadcrumb}"/>
                <c:set target="${agnBreadcrumb}" property="text" value="${mailingSettingsForm.shortname}"/>
            </emm:instantiate>
        </emm:instantiate>
    </c:if>
</c:if>

<emm:instantiate var="itemActionsSettings" type="java.util.LinkedHashMap" scope="request">
    <%-- Actions dropdown --%>

    <jsp:include page="../mailing-actions-dropdown.jsp">
        <jsp:param name="elementIndex" value="0"/>
        <jsp:param name="mailingId" value="${mailingId}"/>
        <jsp:param name="isTemplate" value="${isTemplate}"/>
        <jsp:param name="workflowId" value="${workflowId}"/>
        <jsp:param name="isMailingUndoAvailable" value="${undoAvailable}"/>
    </jsp:include>

    <c:if test="${not isMailingGrid}">
        <c:set var="agnHelpKey"         value="mailingGeneralOptions" scope="request" />
        <c:choose>
            <c:when test="${mailingExists}">
                <c:set var="agnHelpKey"         value="mailingGeneralOptions" scope="request" />
                <%-- Save button --%>
                <c:if test="${not isSettingsReadonly}">
                    <c:set var="saveBtnExtraAttrs" value="disabled"/>
                    <emm:ShowByPermission token="${isTemplate ? 'template.change' : 'mailing.change'}">
                        <c:set var="saveBtnExtraAttrs" value="data-form-target='#mailingSettingsForm' data-controls-group='save' data-form-submit-event"/>
                    </emm:ShowByPermission>
                    <emm:instantiate var="element" type="java.util.LinkedHashMap">
                        <c:set target="${itemActionsSettings}" property="2" value="${element}"/>

                        <c:set target="${element}" property="btnCls" value="btn"/>
                        <c:set target="${element}" property="extraAttributes" value="${saveBtnExtraAttrs}"/>
                        <c:set target="${element}" property="iconBefore" value="icon-save"/>
                        <c:set target="${element}" property="name">
                            <mvc:message code="button.Save"/>
                        </c:set>
                    </emm:instantiate>
                </c:if>
            </c:when>
            <c:otherwise>
                <c:set var="agnHelpKey" value="mailingGeneralOptions" scope="request" />
                <%-- Generate (save new) button --%>

                <emm:instantiate var="element" type="java.util.LinkedHashMap">
                    <c:set target="${itemActionsSettings}" property="1" value="${element}"/>

                    <c:set target="${element}" property="btnCls" value="btn"/>
                    <c:set target="${element}" property="extraAttributes" value="data-form-target='#mailingSettingsForm' data-controls-group='save' data-form-submit-event"/>
                    <c:set target="${element}" property="iconBefore" value="icon-save"/>
                    <c:set target="${element}" property="name">
                        <c:if test="${isTemplate}">
                            <mvc:message code="button.save.template.create"/>
                        </c:if>
                        <c:if test="${not isTemplate}">
                            <mvc:message code="button.save.mailing.create"/>
                        </c:if>
                    </c:set>
                </emm:instantiate>
            </c:otherwise>
        </c:choose>
    </c:if>

    <%-- Grid Mailing save button --%>
    <c:if test="${isMailingGrid}">
        <c:choose>
            <c:when test="${mailingExists}">
                <%-- Save button --%>
                <c:if test="${not isSettingsReadonly}">
                    <c:set var="saveBtnExtraAttrs" value="disabled"/>
                    <emm:ShowByPermission token="mailing.change">
                        <c:set var="saveBtnExtraAttrs" value="data-form-target='#mailingSettingsForm' data-form-submit-event data-controls-group='save'"/>
                    </emm:ShowByPermission>
                    <emm:instantiate var="element" type="java.util.LinkedHashMap">
                        <c:set target="${itemActionsSettings}" property="2" value="${element}"/>
                        <c:set target="${element}" property="btnCls" value="btn"/>
                        <c:set target="${element}" property="extraAttributes" value="${saveBtnExtraAttrs}"/>
                        <c:set target="${element}" property="iconBefore" value="icon-save"/>
                        <c:set target="${element}" property="name"><mvc:message code="button.Save"/></c:set>
                    </emm:instantiate>
                </c:if>
            </c:when>
            <c:otherwise>
                <%-- Generate (save new) button --%>
                <emm:instantiate var="element" type="java.util.LinkedHashMap">
                    <c:set target="${itemActionsSettings}" property="1" value="${element}"/>
                    <c:set target="${element}" property="btnCls" value="btn"/>
                    <c:set target="${element}" property="extraAttributes" value="data-form-target='#mailingSettingsForm' data-form-submit-event data-controls-group='save'"/>
                    <c:set target="${element}" property="iconBefore" value="icon-save"/>
                    <c:set target="${element}" property="name"><mvc:message code="button.save.mailing.create"/></c:set>
                </emm:instantiate>
            </c:otherwise>
        </c:choose>
    </c:if>
</emm:instantiate>
