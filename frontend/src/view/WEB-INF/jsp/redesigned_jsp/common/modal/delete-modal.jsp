<%@ page language="java" contentType="text/html; charset=utf-8" errorPage="/errorRedesigned.action" %>
<%@ taglib prefix="mvc" uri="https://emm.agnitas.de/jsp/jsp/spring" %>
<%@ taglib prefix="emm" uri="https://emm.agnitas.de/jsp/jsp/common" %>
<%@ taglib prefix="c"   uri="http://java.sun.com/jsp/jstl/core" %>
<%@ taglib prefix="fn"  uri="http://java.sun.com/jsp/jstl/functions" %>

<%--@elvariable id="title" type="java.lang.String"--%>
<%--@elvariable id="question" type="java.lang.String"--%>
<%--@elvariable id="items" type="java.lang.Object"--%>

<c:set var="isBulkDeletion" value="${items.getClass().getName() ne 'java.lang.String'}"/>

<div class="modal" tabindex="-1">
    <div class="modal-dialog modal-fullscreen-lg-down modal-lg modal-dialog-centered">
        <mvc:form cssClass="modal-content" method="DELETE" modelAttribute="bulkActionForm">
            <div class="modal-header">
                <h1 class="modal-title"><mvc:message code="${title}"/></h1>
                <button type="button" class="btn-close shadow-none js-confirm-negative" data-bs-dismiss="modal">
                    <span class="sr-only"><mvc:message code="button.Cancel"/></span>
                </button>
            </div>
            <div class="modal-body">
                <mvc:message code="${question}" arguments="${items}"/>

                <c:if test="${isBulkDeletion}">
                    <%-- rows + header + table-controls--%>
                    <c:set var="tableHeight" value="${(items.size() + 2) * 40}"/>
                    <div class="js-data-table mt-3" data-table="delete-items" style="height: ${tableHeight}px; max-height: 500px">
                        <div class="js-data-table-body h-100"></div>

                        <script id="delete-items" type="application/json">
                            {
                                "columns": [
                                     {
                                        "field": "name",
                                        "headerName": "<mvc:message code='Name'/>",
                                        "filter": false,
                                        "suppressMovable": true,
                                        "sortable": true,
                                        "sort": "asc",
                                        "resizable": false
                                    }
                                ],
                                "options": {
                                    "pagination": false,
                                    "singleNameTable": true,
                                    "showRecordsCount": "simple"
                                },
                                "data": ${emm:toJson(items)}
                            }
                        </script>
                    </div>
                </c:if>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-danger js-confirm-positive flex-grow-1">
                    <i class="icon icon-trash-alt"></i>
                    <b><mvc:message code="button.Delete"/></b>
                </button>
            </div>
        </mvc:form>
    </div>
</div>
