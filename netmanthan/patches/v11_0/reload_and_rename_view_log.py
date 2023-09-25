import netmanthan


def execute():
	if netmanthan.db.table_exists("View log"):
		# for mac users direct renaming would not work since mysql for mac saves table name in lower case
		# so while renaming `tabView log` to `tabView Log` we get "Table 'tabView Log' already exists" error
		# more info https://stackoverflow.com/a/44753093/5955589 ,
		# https://dev.mysql.com/doc/refman/8.0/en/server-system-variables.html#sysvar_lower_case_table_names

		# here we are creating a temp table to store view log data
		netmanthan.db.sql("CREATE TABLE `ViewLogTemp` AS SELECT * FROM `tabView log`")

		# deleting old View log table
		netmanthan.db.sql("DROP table `tabView log`")
		netmanthan.delete_doc("DocType", "View log")

		# reloading view log doctype to create `tabView Log` table
		netmanthan.reload_doc("core", "doctype", "view_log")

		# Move the data to newly created `tabView Log` table
		netmanthan.db.sql("INSERT INTO `tabView Log` SELECT * FROM `ViewLogTemp`")
		netmanthan.db.commit()

		# Delete temporary table
		netmanthan.db.sql("DROP table `ViewLogTemp`")
	else:
		netmanthan.reload_doc("core", "doctype", "view_log")
