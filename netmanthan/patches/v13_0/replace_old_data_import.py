# Copyright (c) 2020, netmanthan Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import netmanthan


def execute():
	if not netmanthan.db.table_exists("Data Import"):
		return

	meta = netmanthan.get_meta("Data Import")
	# if Data Import is the new one, return early
	if meta.fields[1].fieldname == "import_type":
		return

	netmanthan.db.sql("DROP TABLE IF EXISTS `tabData Import Legacy`")
	netmanthan.rename_doc("DocType", "Data Import", "Data Import Legacy")
	netmanthan.db.commit()
	netmanthan.db.sql("DROP TABLE IF EXISTS `tabData Import`")
	netmanthan.rename_doc("DocType", "Data Import Beta", "Data Import")
