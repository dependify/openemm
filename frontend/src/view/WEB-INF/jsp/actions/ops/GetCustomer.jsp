
<script id="module-GetCustomer" type="text/x-mustache-template">
    <div class="inline-tile-content" data-module-content="{{- index}}">
        <input type="hidden" name="modules[].type" id="module_{{- index}}.type" value="GetCustomer"/>
        <input type="hidden" name="modules[].id" id="module_{{- index}}.id" value="{{- id}}"/>
        <div class="form-group">
            <div class="col-sm-offset-4 col-sm-8">
                <div class="checkbox">
                    <label class="toggle">
                        {{ if (loadAlways) { }}
                            <input type="checkbox" name="modules[].loadAlways" id="module_{{- index}}.loadAlways" checked="ckecked"/>
                        {{ } else { }}
                            <input type="checkbox" name="modules[].loadAlways" id="module_{{- index}}.loadAlways" />
                        {{ } }}

						<div class="toggle-control"></div><%-- Use separate closing tag. Otherwise the layout will break. (Why? I don't know...) --%>

                        <mvc:message code="action.getcustomer.loadalways"/>
                    </label>
                </div>
            </div>
        </div>
    </div>
    <div class="inline-tile-footer">
        <emm:ShowByPermission token="actions.change">
            <a class="btn btn-regular" href="#" data-action="action-delete-module" data-property-id="{{- index}}">
                <i class="icon icon-trash-o"></i>
                <span class="text"><mvc:message code="button.Delete"/></span>
            </a>
        </emm:ShowByPermission>
    </div>
</script>
