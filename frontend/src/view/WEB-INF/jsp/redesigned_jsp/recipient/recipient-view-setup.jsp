<%@ page language="java" contentType="text/html; charset=utf-8" errorPage="/errorRedesigned.action" %>
<%@ page import="org.agnitas.web.forms.FormSearchParams" %>

<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>
<%@ taglib prefix="mvc" uri="https://emm.agnitas.de/jsp/jsp/spring" %>
<%@ taglib prefix="emm" uri="https://emm.agnitas.de/jsp/jsp/common" %>

<c:set var="RESTORE_SEARCH_PARAM_NAME" value="<%= FormSearchParams.RESTORE_PARAM_NAME%>"/>

<%--@elvariable id="form" type="com.agnitas.emm.core.recipient.forms.RecipientForm"--%>
<%--@elvariable id="isSaveButtonDisabled" type="java.lang.Boolean"--%>

<c:url var="recipientsOverviewLink" value="/recipient/list.action">
    <c:param name="${RESTORE_SEARCH_PARAM_NAME}" value="true"/>
</c:url>

<c:url var="saveAndBackToListLink" value="/recipient/saveAndBackToList.action"/>

<c:set var="recipientExists" value="${form.id gt 0}"/>
<mvc:message var="reportTooltipMessage" code="recipient.report.rightOfAccess.mouseover"/>

<c:set var="agnTitleKey" 			value="Recipient" 									scope="request" />
<c:set var="agnSubtitleKey" 		value="Recipients" 									scope="request" />
<c:set var="sidemenu_active" 		value="Recipients" 									scope="request" />
<c:set var="sidemenu_sub_active" 	value="default.search" 								scope="request" />
<c:set var="isBreadcrumbsShown" 	value="true" 										scope="request" />
<c:set var="agnBreadcrumbsRootKey"	value="Recipients" 									scope="request" />
<c:url var="agnBreadcrumbsRootUrl"	value="/recipient/list.action" 						scope="request" />
<c:set var="agnEditViewKey" 	    value="recipient-view"                              scope="request" />

<emm:sideMenuAdditionalParam name="${RESTORE_SEARCH_PARAM_NAME}" value="true" forSubmenuOnly="false"/>

<emm:instantiate var="agnNavHrefParams" type="java.util.LinkedHashMap" scope="request">
    <c:set target="${agnNavHrefParams}" property="recipientID" value="${form.id}"/>
</emm:instantiate>

<c:choose>
    <c:when test="${recipientExists}">
        <c:set var="agnHighlightKey" 	value="recipient.RecipientEdit" scope="request" />
		<c:set var="agnHelpKey" 		value="recipientView" 			scope="request" />
		<c:choose>
		    <c:when test="${isMailTrackingEnabled}">
				<c:set var="agnNavigationKey" value="subscriber_editor_mailtracking" scope="request" />
		    </c:when>
		    <c:otherwise>
				<c:set var="agnNavigationKey" value="subscriber_editor_no_mailtracking" scope="request" />
		    </c:otherwise>
		</c:choose>
        
        <c:choose>
            <c:when test="${not empty form.firstname and not empty form.lastname}">
                <c:set var="recipientMention" value="${form.firstname} ${form.lastname}"/>
            </c:when>
            <c:when test="${not empty form.firstname}">
                <c:set var="recipientMention" value="${form.firstname}"/>
            </c:when>
            <c:when test="${not empty form.lastname}">
                <c:set var="recipientMention" value="${form.lastname}"/>
            </c:when>
            <c:otherwise>
                <c:set var="recipientMention" value="${form.email}"/>
            </c:otherwise>
        </c:choose>

        <emm:instantiate var="agnBreadcrumbs" type="java.util.LinkedHashMap" scope="request">
            <emm:instantiate var="agnBreadcrumb" type="java.util.LinkedHashMap">
                <c:set target="${agnBreadcrumbs}" property="1" value="${agnBreadcrumb}"/>
                <c:set target="${agnBreadcrumb}" property="text" value="${recipientMention}"/>
            </emm:instantiate>
        </emm:instantiate>
    </c:when>
    <c:otherwise>
        <c:set var="agnNavigationKey" 	value="none" 					scope="request" />
        <c:set var="agnHighlightKey" 	value="recipient.NewRecipient" 	scope="request" />
        <c:set var="agnHelpKey" 		value="newRecipient" 			scope="request" />

        <emm:instantiate var="agnBreadcrumbs" type="java.util.LinkedHashMap" scope="request">
            <emm:instantiate var="agnBreadcrumb" type="java.util.LinkedHashMap">
                <c:set target="${agnBreadcrumbs}" property="0" value="${agnBreadcrumb}"/>
                <c:set target="${agnBreadcrumb}" property="textKey" value="recipient.NewRecipient"/>
            </emm:instantiate>
        </emm:instantiate>
    </c:otherwise>
</c:choose>

<emm:instantiate var="itemActionsSettings" type="java.util.LinkedHashMap" scope="request">

    <%-- Actions dropdown --%>
    <emm:instantiate var="element" type="java.util.LinkedHashMap">

        <emm:instantiate var="element" type="java.util.LinkedHashMap">
            <c:set target="${itemActionsSettings}" property="0" value="${element}"/>

            <c:set target="${element}" property="btnCls" value="btn dropdown-toggle"/>
            <c:set target="${element}" property="cls" value="mobile-hidden"/>
            <c:set target="${element}" property="extraAttributes" value="data-bs-toggle='dropdown'"/>
            <c:set target="${element}" property="iconBefore" value="icon-wrench"/>
            <c:set target="${element}" property="name"><mvc:message code="action.Action"/></c:set>

            <emm:instantiate var="optionList" type="java.util.LinkedHashMap">
                <c:set target="${element}" property="dropDownItems" value="${optionList}"/>
            </emm:instantiate>

            <%-- Items for dropdown --%>
            <c:if test="${recipientExists}">
                <emm:instantiate var="option" type="java.util.LinkedHashMap">
                    <c:set target="${optionList}" property="0" value="${option}"/>

                    <c:set var="reportTooltipOptions" value='{"content":"${reportTooltipMessage}", "placement": "bottom-end" }'/>
                    <c:set target="${option}" property="extraAttributes" value="data-prevent-load='' data-tooltip-help='${reportTooltipOptions}'"/>
                    <c:set target="${option}" property="url">
                        <c:url value="/report/recipients.action">
                            <c:param name="id" value="${form.id}"/>
                        </c:url>
                    </c:set>
                    <c:set target="${option}" property="name">
                        <mvc:message code="recipient.report.rightOfAccess"/>
                    </c:set>
                </emm:instantiate>
                <emm:ShowByPermission token="recipient.delete">
                    <emm:instantiate var="option" type="java.util.LinkedHashMap">
                        <c:set target="${optionList}" property="2" value="${option}"/>

                        <c:set target="${option}" property="extraAttributes" value="data-confirm=''"/>
                        <c:set target="${option}" property="url">
                            <c:url value="/recipient/${form.id}/confirmDelete.action"/>
                        </c:set>
                        <c:set target="${option}" property="name">
                            <mvc:message code="button.Delete"/>
                        </c:set>
                    </emm:instantiate>
                </emm:ShowByPermission>
            </c:if>
        </emm:instantiate>
    </emm:instantiate>

    <emm:ShowByPermission token="recipient.change">
        <c:choose>
            <c:when test="${recipientExists}">
                <emm:instantiate var="element" type="java.util.LinkedHashMap">
                    <c:set target="${itemActionsSettings}" property="1" value="${element}"/>

                    <c:set target="${element}" property="btnCls" value="btn js-btn-dropdown ${isSaveButtonDisabled ? 'disabled' : ''}"/>
                    <c:set target="${element}" property="cls" value="mobile-hidden" />
                    <c:set target="${element}" property="type" value="button"/>
                    <c:set target="${element}" property="extraAttributes" value="data-form-target='#recipient-detail-view' data-form-submit-event"/>
                    <c:set target="${element}" property="iconBefore" value="icon-save"/>
                    <c:set target="${element}" property="name">
                        <mvc:message code="button.Save"/>
                    </c:set>

                    <emm:instantiate var="optionList" type="java.util.LinkedHashMap">
                        <c:set target="${element}" property="dropDownItems" value="${optionList}"/>
                    </emm:instantiate>

                    <emm:instantiate var="option" type="java.util.LinkedHashMap">
                        <c:set target="${optionList}" property="0" value="${option}"/>

                        <c:set target="${option}" property="extraAttributes" value="data-form-url='${saveAndBackToListLink}' data-form-target='#recipient-detail-view' data-form-submit-event"/>
                        <c:set target="${option}" property="url" value="#"/>
                        <c:set target="${option}" property="name">
                            <mvc:message code="button.SaveAndBack"/>
                        </c:set>
                    </emm:instantiate>
                </emm:instantiate>
            </c:when>
            <c:otherwise>
                <emm:instantiate var="element" type="java.util.LinkedHashMap">

                    <c:set target="${itemActionsSettings}" property="1" value="${element}"/>

                    <c:set target="${element}" property="btnCls" value="btn"/>
                    <c:set target="${element}" property="extraAttributes" value="data-form-target='#recipient-detail-view' data-form-submit-event"/>
                    <c:set target="${element}" property="iconBefore" value="icon-save"/>
                    <c:set target="${element}" property="name">
                        <mvc:message code="button.Save"/>
                    </c:set>
                </emm:instantiate>
            </c:otherwise>
        </c:choose>
    </emm:ShowByPermission>
</emm:instantiate>
