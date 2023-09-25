import netmanthan


def execute():
	if netmanthan.db.db_type == "mariadb":
		netmanthan.db.sql_ddl("alter table `tabSingles` modify column `value` longtext")
