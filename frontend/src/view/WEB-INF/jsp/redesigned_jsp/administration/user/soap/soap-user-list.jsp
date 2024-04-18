<%@ page language="java" contentType="text/html; charset=utf-8" buffer="32kb"  errorPage="/errorRedesigned.action" %>
<%@ taglib prefix="emm"     uri="https://emm.agnitas.de/jsp/jsp/common" %>
<%@ taglib prefix="mvc"     uri="https://emm.agnitas.de/jsp/jsp/spring" %>
<%@ taglib prefix="display" uri="http://displaytag.sf.net" %>
<%@ taglib prefix="c"       uri="http://java.sun.com/jsp/jstl/core" %>

<%--@elvariable id="filter" type="com.agnitas.emm.core.wsmanager.form.WebserviceUserOverviewFilter"--%>
<c:set var="allowedCreation" value="false"/>
<emm:ShowByPermission token="webservice.user.create">
    <c:set var="allowedCreation" value="true"/>
</emm:ShowByPermission>

<c:set var="allowedChange" value="false"/>
<emm:ShowByPermission token="webservice.user.change">
    <c:set var="allowedChange" value="true"/>
</emm:ShowByPermission>

<div id="soap-users-overview" class="tiles-container hidden" data-editable-view="${agnEditViewKey}">
    <c:if test="${allowedCreation}">
        <div id="new-user-tile" class="tile" data-editable-tile>
            <div class="tile-header">
                <h1 class="tile-title"><mvc:message code="settings.webservice.user.new" /></h1>
            </div>
            <mvc:form servletRelativeAction="/administration/wsmanager/user/new.action" id="wsuser-creation-form"
                      data-resource-selector="#wsuser-creation-form, #table-tile" modelAttribute="webserviceUserForm"
                      data-form-focus="userName" data-form="resource" cssClass="tile-body">
                <div class="row">
                    <div class="col">
                        <label for="newUsername" class="form-label">
                            <mvc:message var="usernameMsg" code="logon.username" />
                            ${usernameMsg}&nbsp;*
                        </label>
                        <mvc:text path="userName" id="newUsername" cssClass="form-control" placeholder="${usernameMsg}" data-field="required"/>
                    </div>

                    <div class="col">
                        <label for="newEmail" class="form-label">
                            <mvc:message code="mailing.MediaType.email" />&nbsp;*
                        </label>
                        <mvc:text path="email" id="newEmail" cssClass="form-control" placeholder="${emailPlaceholder}" data-field="required"/>
                    </div>

                    <emm:ShowByPermission token="master.companies.show">
                        <div class="col">
                            <label for="newClient" class="form-label">
                                <mvc:message code="webserviceuser.company" />
                            </label>
                            <mvc:select path="companyId" cssClass="form-control" id="newClient">
                                <mvc:option value="-1"><mvc:message code="select.company"/></mvc:option>
                                <mvc:options items="${companyList}" itemValue="companyId" itemLabel="shortname"/>
                            </mvc:select>
                        </div>
                    </emm:ShowByPermission>

                    <div class="col" data-field="password">
                        <label for="newPassword" class="form-label">
                            <mvc:message code="password"/>&nbsp;*
                            <a href="#" class="icon icon-question-circle" data-help="help_${helplanguage}/webserviceuser/AdminPasswordRules.xml" tabindex="-1" type="button"></a>
                        </label>
                        <mvc:password path="password" id="newPassword" cssClass="form-control js-password-strength" size="52" maxlength="99" data-field="required" data-rule="${PASSWORD_POLICY}"/>
                    </div>

                    <div class="col">
                        <label for="newPasswordRepeat" class="form-label text-nowrap">
                            <mvc:message code="settings.admin.Confirm"/>&nbsp;*
                        </label>
                        <input type="password" id="newPasswordRepeat" class="form-control js-password-match" size="52" maxlength="99" readonly />
                    </div>

                    <%-- In case if inputs have feedback message button should still be aligned to the bottom of other inputs !!! --%>
                    <div class="col-auto" style="padding-top: 23px">
                        <button class="btn btn-primary" type="button" data-form-submit>
                            <i class="icon icon-plus"></i>
                            <mvc:message code="settings.webservice.user.create" />
                        </button>
                    </div>
                </div>
            </mvc:form>
        </div>
    </c:if>

    <div class="tiles-block" style="flex: 1">
        <mvc:form servletRelativeAction="/administration/wsmanager/usersRedesigned.action" id="table-tile" modelAttribute="filter" cssClass="tile" data-editable-tile="main">
            <script type="application/json" data-initializer="web-storage-persist">
                {
                    "ws-manager-overview": {
                        "rows-count": ${filter.numberOfRows}
                    }
                }
            </script>

            <div class="tile-header">
                <h1 class="tile-title"><mvc:message code="default.Overview" /></h1>
            </div>
            <div class="tile-body">
                <div class="table-box">
                    <div class="table-scrollable">
                        <display:table class="table table-rounded js-table table-hover" id="wsUser"
                                       name="webserviceUserList" requestURI="/administration/wsmanager/usersRedesigned.action"
                                       pagesize="${filter.numberOfRows}" excludedParams="*">

                            <%@ include file="../../../displaytag/displaytag-properties.jspf" %>

                            <display:column headerClass="js-table-sort" property="userName" titleKey="logon.username" sortable="true" sortProperty="username"/>

                            <display:column headerClass="js-table-sort" titleKey="Status" sortable="true" sortProperty="active">
                                <mvc:message code="${wsUser.active ? 'workflow.view.status.active' : 'webserviceuser.not_active'}"/>
                            </display:column>

                            <emm:ShowByPermission token="master.companies.show">
                                <display:column headerClass="js-table-sort" titleKey="webserviceuser.company" sortable="true" sortProperty="company_name" value="${wsUser.clientName} (${wsUser.companyId})"/>
                            </emm:ShowByPermission>

                            <display:column headerClass="js-table-sort" property="dataSourceId" titleKey="webserviceuser.default_datasource_id" sortable="true" sortProperty="default_data_source_id"/>

                            <display:column class="hidden" headerClass="hidden" sortable="false">
                                <c:url var="viewWsUserLink" value="/administration/wsmanager/user/${wsUser.userName}/view.action"/>
                                <a href="${viewWsUserLink}" class="hidden" data-view-row="page"></a>
                            </display:column>
                        </display:table>
                    </div>
                </div>
            </div>
        </mvc:form>

        <mvc:form id="filter-tile" cssClass="tile" method="GET" servletRelativeAction="/administration/wsmanager/search.action"
                  modelAttribute="filter" data-form="resource" data-resource-selector="#table-tile" data-toggle-tile="mobile" data-editable-tile="">

            <div class="tile-header">
                <h1 class="tile-title">
                    <i class="icon icon-caret-up desktop-hidden"></i><mvc:message code="report.mailing.filter"/>
                </h1>
                <div class="tile-controls">
                    <a class="btn btn-icon btn-icon-sm btn-inverse" data-form-clear data-form-submit data-tooltip="<mvc:message code="filter.reset"/>"><i class="icon icon-sync"></i></a>
                    <a class="btn btn-icon btn-icon-sm btn-primary" data-form-submit data-tooltip="<mvc:message code='button.filter.apply'/>"><i class="icon icon-search"></i></a>
                </div>
            </div>

            <div class="tile-body js-scrollable">
                <div class="row g-3">
                    <div class="col-12">
                        <mvc:message var="usernameMsg" code="logon.username"/>
                        <label class="form-label" for="filter-username">${usernameMsg}</label>
                        <mvc:text id="filter-username" path="username" cssClass="form-control" placeholder="${usernameMsg}"/>
                    </div>

                    <div class="col-12">
                        <label class="form-label" for="filter-status"><mvc:message code="Status"/></label>
                        <mvc:select id="filter-status" path="status" cssClass="form-control">
                            <mvc:option value=""><mvc:message code="default.All" /></mvc:option>
                            <mvc:option value="0"><mvc:message code="webserviceuser.not_active" /></mvc:option>
                            <mvc:option value="1"><mvc:message code="workflow.view.status.active" /></mvc:option>
                        </mvc:select>
                    </div>

                    <emm:ShowByPermission token="master.companies.show">
                        <div class="col-12">
                            <label class="form-label" for="filter-client"><mvc:message code="Company"/></label>
                            <mvc:select id="filter-client" path="companyId" cssClass="form-control" data-sort="alphabetic">
                                <mvc:option value="" data-no-sort=""><mvc:message code="default.All" /></mvc:option>
                                <c:forEach var="client" items="${companyList}">
                                    <mvc:option value="${client.companyId}">${client.shortname} (${client.companyId})</mvc:option>
                                </c:forEach>
                            </mvc:select>
                        </div>
                    </emm:ShowByPermission>

                    <div class="col-12">
                        <label class="form-label" for="filter-datasource"><mvc:message code="webserviceuser.default_datasource_id"/></label>
                        <mvc:number id="filter-datasource" path="defaultDataSourceId" cssClass="form-control" placeholder="0"/>
                    </div>
                </div>
            </div>
        </mvc:form>
    </div>
</div>
