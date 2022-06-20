/*

    Copyright (C) 2022 AGNITAS AG (https://www.agnitas.org)

    This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
    This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.
    You should have received a copy of the GNU Affero General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

*/

package com.agnitas.emm.springws.exception;

/**
 * Exception indicating that the webservice user is not
 * allowed to invoke a webservice method.
 */
public class WebserviceNotAllowedException extends Exception {

	/** Serial version UID. */
	private static final long serialVersionUID = 3077729810579852385L;
	
	/** Name of webservice. */
	private final String name;
	
	/**
	 * Creates a new exception.
	 * 
	 * @param name webservice name
	 */
	public WebserviceNotAllowedException(String name) {
		super("Webservice not allowed: " + name);
		
		this.name = name;
	}
	
	/**
	 * Returns the webservice name.
	 * 
	 * @return webservice name
	 */
	public String getName() {
		return this.name;
	}
}
