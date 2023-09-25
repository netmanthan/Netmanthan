# Copyright (c) 2020, netmanthan Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import netmanthan


def execute():
	netmanthan.reload_doc("core", "doctype", "DocField")

	if netmanthan.db.has_column("DocField", "show_days"):
		netmanthan.db.sql(
			"""
			UPDATE
				tabDocField
			SET
				hide_days = 1 WHERE show_days = 0
		"""
		)
		netmanthan.db.sql_ddl("alter table tabDocField drop column show_days")

	if netmanthan.db.has_column("DocField", "show_seconds"):
		netmanthan.db.sql(
			"""
			UPDATE
				tabDocField
			SET
				hide_seconds = 1 WHERE show_seconds = 0
		"""
		)
		netmanthan.db.sql_ddl("alter table tabDocField drop column show_seconds")

	netmanthan.clear_cache(doctype="DocField")
