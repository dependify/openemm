/*

    Copyright (C) 2019 AGNITAS AG (https://www.agnitas.org)

    This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
    This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.
    You should have received a copy of the GNU Affero General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

*/

DROP PROCEDURE IF EXISTS TEMP_PROCEDURE;

DELIMITER ;;
CREATE PROCEDURE TEMP_PROCEDURE()
BEGIN
	DECLARE isMariaDB INTEGER;
	DECLARE CONTINUE HANDLER FOR SQLEXCEPTION BEGIN END;
	
	SELECT LOWER(VERSION()) LIKE '%maria%' INTO @isMariaDB FROM DUAL;

	IF isMariaDB > 0 THEN
		-- Use sql in string to hide it from MySQL
		SET @ddl1 = CONCAT('ALTER TABLE admin_group_permission_tbl DROP CONSTRAINT IF EXISTS admgrp$perm$fk');
		PREPARE stmt1 FROM @ddl1;
		EXECUTE stmt1;
		DEALLOCATE PREPARE stmt1;
	ELSE
		ALTER TABLE admin_group_permission_tbl DROP FOREIGN KEY admgrp$perm$fk;
		ALTER TABLE admin_group_permission_tbl DROP KEY admgrp$perm$fk;
	END IF;
END;;
DELIMITER ;

CALL TEMP_PROCEDURE;
DROP PROCEDURE TEMP_PROCEDURE;

INSERT INTO agn_dbversioninfo_tbl (version_number, updating_user, update_timestamp)
	VALUES ('21.01.410', CURRENT_USER, CURRENT_TIMESTAMP);
