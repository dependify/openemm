/*

    Copyright (C) 2019 AGNITAS AG (https://www.agnitas.org)

    This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
    This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.
    You should have received a copy of the GNU Affero General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

*/

package com.agnitas.dao;

import java.util.AbstractMap.SimpleEntry;
import java.util.List;
import java.util.Set;

import org.agnitas.beans.BindingEntry;
import org.agnitas.emm.core.velocity.VelocityCheck;

import com.agnitas.beans.ComTarget;
import com.agnitas.emm.core.mediatypes.common.MediaTypes;
import com.agnitas.emm.core.report.bean.CompositeBindingEntry;
import com.agnitas.emm.core.report.bean.PlainBindingEntry;

public interface ComBindingEntryDao {

	boolean getExistingRecipientIDByMailinglistID(Set<Integer> mailinglistIds, @VelocityCheck int companyId);

    void deleteRecipientBindingsByMailinglistID(Set<Integer> mailinglistIds, @VelocityCheck int companyId);

    /**
	 * Loads a binding from database. Uses recipientID, mailinglistID and
	 * mediaType of the given binding.
	 *
	 * @param recipientID The id of the recipient for the binding.
	 * @param companyID The id of the company for the binding.
     * @param mailinglistID The id of the mailinglist for the binding.
     * @param mediaType The value of mediatype for the binding.
	 * @return The BindingEntry or null on failure.
	 */
	BindingEntry get(int recipientID, @VelocityCheck int companyID, int mailinglistID, int mediaType);

	/**
	 * Loads bindings from database by recipient id and mailing id.
	 *
	 * @param recipientId The id of the recipient for the binding.
	 * @param companyId The id of the company for the binding.
	 * @param mailingId The id of the mailing for the mailing list.
	 * @return The BindingEntry or null on failure.
	 */
	List<PlainBindingEntry> get(@VelocityCheck int companyId, int recipientId, int mailingId);

    /**
     * Updates existing Binding in Database or create new Binding.
     *
     * @param companyID The id of the company for the binding
     * @param entry The Binding to update or create
     */
	void save(@VelocityCheck int companyID, BindingEntry entry);

	/**
	 * Updates the Binding in the Database
	 *
     * @param entry Binding to update
	 * @param companyID The company ID of the Binding
	 * @return true if success and false if failure
	 */
	boolean updateBinding(BindingEntry entry, @VelocityCheck int companyID);

	void updateBindings(@VelocityCheck int companyId, List<BindingEntry> bindings) throws Exception;

	void insertBindings(@VelocityCheck int companyId, List<BindingEntry> bindings) throws Exception;

	/**
	 * Inserts a new binding into the database.
	 *
	 * @param entry The entry to create.
	 * @param companyID The company we are working on.
	 * @return true on success.
	 */
	boolean insertNewBinding(BindingEntry entry, @VelocityCheck int companyID);

    /**
     * Update the status for the binding. Also updates exit_mailing_id and
     * user_remark to reflect the status change.
     *
     * @param entry The entry on which the status has changed.
     * @param companyID The company we are working on.
     * @return true on success.
     */
	boolean updateStatus(BindingEntry entry, @VelocityCheck int companyID);

    /**
     * Set given email to status optout. The given email can be an sql
     * like pattern.
     *
     * @param email The sql like pattern of the email-address.
     * @param CompanyID Only update addresses for this company.
     */
	boolean optOutEmailAdr(String email, @VelocityCheck int CompanyID);

    /**
     * Subscribes all customers in the given target group to the given mailinglist.
     *
     * @param companyID The company to work in.
     * @param mailinglistID The id of the mailinglist to which the targets should be subscribed.
     * @param target The target describing the recipients that shall be added.
     * @return true on success.
     */
    boolean addTargetsToMailinglist(@VelocityCheck int companyID, int mailinglistID, ComTarget target, Set<MediaTypes> mediaTypes);

    /* moved form BindingEntry */
	/**
	 * Load a binding from database. Uses recipientID, mailinglistID and
	 * mediaType of the given binding.
	 *
	 * @param entry Binding that holds parameters for loading.
	 * @param companyID The id of the company for the binding.
	 * @return true if success and false if failure
	 */
    boolean getUserBindingFromDB(BindingEntry entry, @VelocityCheck int companyID);

    /**
     * Check if Binding entry exists.
     *
     * @param customerId The id of the customer for the binding
     * @param companyId The id of the company for the binding.
     * @param mailinglistId The id of the mailinglist for the binding.
     * @param mediatype The value of mediatype for the binding.
     * @return true if the Binding exists and false otherwise
     */
    boolean exist(int customerId, @VelocityCheck int companyId, int mailinglistId, int mediatype);

    boolean exist(@VelocityCheck int companyId, int mailinglistId);

    /**
     * Delete Binding. Uses customerId, companyId, mailinglistId and
	 * mediatype of the given binding.
     *
     * @param customerId The id of the customer for the binding.
     * @param companyId The id of the company for the binding.
     * @param mailinglistId The id of the mailinglist for the binding.
     * @param mediatype The value of mediatype for the binding.
     */
    void delete(int customerId, @VelocityCheck int companyId, int mailinglistId, int mediatype);

    /**
     * Load list of Bindings by companyId and recipientID.
     *
     * @param companyId The id of the company for the bindings.
     * @param recipientID The id of the recipient for the binding.
     * @return Binding entity
     */
	List<BindingEntry> getBindings(@VelocityCheck int companyId, int recipientID);

	List<CompositeBindingEntry> getCompositeBindings(@VelocityCheck int companyID, int recipientID);

	void updateBindingStatusByEmailPattern(@VelocityCheck int companyId, String emailPattern, int userStatus, String remark) throws Exception;

	void lockBindings(int companyId, List<SimpleEntry<Integer, Integer>> cmPairs);
}
