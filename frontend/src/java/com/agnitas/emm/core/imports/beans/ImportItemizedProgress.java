/*

    Copyright (C) 2019 AGNITAS AG (https://www.agnitas.org)

    This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
    This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.
    You should have received a copy of the GNU Affero General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

*/

package com.agnitas.emm.core.imports.beans;

public enum ImportItemizedProgress {
    PREPARATIONS(ImportProgressSteps.PREPARATIONS),

    IMPORTING_DATA_TO_TMP_TABLE(ImportProgressSteps.IMPORTING_DATA_TO_TMP_TBL),

    HANDLING_BLACKLIST(ImportProgressSteps.IMPORTING),
    HANDLING_DUPLICATES(ImportProgressSteps.IMPORTING),
    EXECUTING_IMPORT_ACTION(ImportProgressSteps.IMPORTING),
    HANDLING_PREPROCESSING(ImportProgressSteps.IMPORTING),
    HANDLING_NEW_RECIPIENTS(ImportProgressSteps.IMPORTING),
    HANDLING_EXISTING_RECIPIENTS(ImportProgressSteps.IMPORTING),
    HANDLING_POSTPROCESSING(ImportProgressSteps.IMPORTING),

    REPORTING_TO_RESULT_FILE(ImportProgressSteps.PREPARING_REPORTS),
    REPORTING_SUCCESS_RECIPIENTS(ImportProgressSteps.PREPARING_REPORTS),
    REPORTING_INVALID_RECIPIENTS(ImportProgressSteps.PREPARING_REPORTS),
    REPORTING_FIXED_RECIPIENTS(ImportProgressSteps.PREPARING_REPORTS),
    REPORTING_DUPLICATED_RECIPIENTS(ImportProgressSteps.PREPARING_REPORTS),
    SENDING_REPORT_MAIL(ImportProgressSteps.PREPARING_REPORTS);

    final ImportProgressSteps prentStep;

    ImportItemizedProgress(ImportProgressSteps prentStep) {
        this.prentStep = prentStep;
    }

    public ImportProgressSteps getPrentStep() {
        return prentStep;
    }
}
