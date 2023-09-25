import netmanthan


def execute():
	column = "apply_user_permissions"
	to_remove = ["DocPerm", "Custom DocPerm"]

	for doctype in to_remove:
		if netmanthan.db.table_exists(doctype):
			if column in netmanthan.db.get_table_columns(doctype):
				netmanthan.db.sql(f"alter table `tab{doctype}` drop column {column}")

	netmanthan.reload_doc("core", "doctype", "docperm", force=True)
	netmanthan.reload_doc("core", "doctype", "custom_docperm", force=True)
