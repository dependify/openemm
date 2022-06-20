/*

    Copyright (C) 2022 AGNITAS AG (https://www.agnitas.org)

    This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
    This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.
    You should have received a copy of the GNU Affero General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

*/

package com.agnitas.beans.impl;

import org.agnitas.beans.DynamicTagContent;
import org.agnitas.beans.impl.DynamicTagContentImpl;

import com.agnitas.beans.ComUndoDynContent;

public class ComUndoDynContentImpl extends DynamicTagContentImpl implements ComUndoDynContent {

	private int undoId;
	
	@Override
	public int getUndoId() {
		return this.undoId;
	}

	@Override
	public void setUndoId(int undoId) {
		this.undoId = undoId;
	}

	@Override
	public DynamicTagContent clone() {
		ComUndoDynContentImpl comUndoDynContent = new ComUndoDynContentImpl();
		comUndoDynContent.setUndoId(undoId);
		return comUndoDynContent;
	}
}
