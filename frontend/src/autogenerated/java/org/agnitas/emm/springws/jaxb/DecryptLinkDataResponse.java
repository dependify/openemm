/*

    Copyright (C) 2022 AGNITAS AG (https://www.agnitas.org)

    This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
    This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.
    You should have received a copy of the GNU Affero General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

*/


package org.agnitas.emm.springws.jaxb;

import jakarta.xml.bind.annotation.XmlAccessType;
import jakarta.xml.bind.annotation.XmlAccessorType;
import jakarta.xml.bind.annotation.XmlRootElement;
import jakarta.xml.bind.annotation.XmlType;


/**
 * <p>Java class for anonymous complex type.
 * 
 * <p>The following schema fragment specifies the expected content contained within this class.
 * 
 * <pre>
 * &lt;complexType&gt;
 *   &lt;complexContent&gt;
 *     &lt;restriction base="{http://www.w3.org/2001/XMLSchema}anyType"&gt;
 *       &lt;all&gt;
 *         &lt;element name="companyID" type="{http://www.w3.org/2001/XMLSchema}int"/&gt;
 *         &lt;element name="mailingID" type="{http://www.w3.org/2001/XMLSchema}int"/&gt;
 *         &lt;element name="urlID" type="{http://www.w3.org/2001/XMLSchema}int"/&gt;
 *         &lt;element name="customerID" type="{http://www.w3.org/2001/XMLSchema}int"/&gt;
 *       &lt;/all&gt;
 *     &lt;/restriction&gt;
 *   &lt;/complexContent&gt;
 * &lt;/complexType&gt;
 * </pre>
 * 
 * 
 */
@XmlAccessorType(XmlAccessType.FIELD)
@XmlType(name = "", propOrder = {

})
@XmlRootElement(name = "DecryptLinkDataResponse")
@SuppressWarnings("all")
public class DecryptLinkDataResponse {

    protected int companyID;
    protected int mailingID;
    protected int urlID;
    protected int customerID;

    /**
     * Gets the value of the companyID property.
     * 
     */
    public int getCompanyID() {
        return companyID;
    }

    /**
     * Sets the value of the companyID property.
     * 
     */
    public void setCompanyID(int value) {
        this.companyID = value;
    }

    /**
     * Gets the value of the mailingID property.
     * 
     */
    public int getMailingID() {
        return mailingID;
    }

    /**
     * Sets the value of the mailingID property.
     * 
     */
    public void setMailingID(int value) {
        this.mailingID = value;
    }

    /**
     * Gets the value of the urlID property.
     * 
     */
    public int getUrlID() {
        return urlID;
    }

    /**
     * Sets the value of the urlID property.
     * 
     */
    public void setUrlID(int value) {
        this.urlID = value;
    }

    /**
     * Gets the value of the customerID property.
     * 
     */
    public int getCustomerID() {
        return customerID;
    }

    /**
     * Sets the value of the customerID property.
     * 
     */
    public void setCustomerID(int value) {
        this.customerID = value;
    }

}
