<%@ page contentType="text/html; charset=utf-8" errorPage="/errorRedesigned.action" %>
<%@ taglib prefix="mvc" uri="https://emm.agnitas.de/jsp/jsp/spring" %>
<%@ taglib prefix="fn" uri="http://java.sun.com/jsp/jstl/functions" %>

<%--@elvariable id="mailingShortname" type="java.lang.String"--%>
<%--@elvariable id="adminDateTimeFormat" type="java.lang.String"--%>
<%--@elvariable id="deliveryHistoryJson" type="net.sf.json.JSONArray"--%>

<div class="modal" tabindex="-1">
    <div class="modal-dialog modal-lg modal-dialog-centered">
        <div class="modal-content">

            <div class="modal-header">
                <h1 class="modal-title"><mvc:message code="recipient.history.mailing.delivery" arguments="${mailingShortname}"/></h1>
                <button type="button" class="btn-close shadow-none" data-bs-dismiss="modal">
                    <span class="sr-only"><mvc:message code="button.Cancel"/></span>
                </button>
            </div>

            <div class="modal-body">
                <div class="js-data-table" data-table="delivery-info">
                    <div class="js-data-table-body" style="height: 30vh"></div>
                    <script id="delivery-info" type="application/json">
                        {
                            "columns": [
                                {
                                    "headerName": "<mvc:message code='recipient.Timestamp'/>",
                                    "editable": false,
                                    "suppressMenu": true,
                                    "width": 60,
                                    "field": "timestamp",
                                    "type": "dateColumn"
                                },
                                {
                                    "headerName": "<mvc:message code='Mailing'/>",
                                    "editable": false,
                                    "suppressMenu": true,
                                    "width": 100,
                                    "field": "mailing",
                                    "textInPopoverIfTruncated": true
                                }
                            ],
                            "data": ${deliveryHistoryJson}
                        }
                    </script>
                </div>
            </div>
        </div>
    </div>
</div>
