# Copyright (c) 2015, netmanthan Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

# Database Module
# --------------------

from netmanthan.database.database import savepoint


def setup_database(force, source_sql=None, verbose=None, no_mariadb_socket=False):
	import netmanthan

	if netmanthan.conf.db_type == "postgres":
		import netmanthan.database.postgres.setup_db

		return netmanthan.database.postgres.setup_db.setup_database(force, source_sql, verbose)
	else:
		import netmanthan.database.mariadb.setup_db

		return netmanthan.database.mariadb.setup_db.setup_database(
			force, source_sql, verbose, no_mariadb_socket=no_mariadb_socket
		)


def drop_user_and_database(db_name, root_login=None, root_password=None):
	import netmanthan

	if netmanthan.conf.db_type == "postgres":
		import netmanthan.database.postgres.setup_db

		return netmanthan.database.postgres.setup_db.drop_user_and_database(
			db_name, root_login, root_password
		)
	else:
		import netmanthan.database.mariadb.setup_db

		return netmanthan.database.mariadb.setup_db.drop_user_and_database(
			db_name, root_login, root_password
		)


def get_db(host=None, user=None, password=None, port=None):
	import netmanthan

	if netmanthan.conf.db_type == "postgres":
		import netmanthan.database.postgres.database

		return netmanthan.database.postgres.database.PostgresDatabase(host, user, password, port=port)
	else:
		import netmanthan.database.mariadb.database

		return netmanthan.database.mariadb.database.MariaDBDatabase(host, user, password, port=port)


def setup_help_database(help_db_name):
	import netmanthan

	if netmanthan.conf.db_type == "postgres":
		import netmanthan.database.postgres.setup_db

		return netmanthan.database.postgres.setup_db.setup_help_database(help_db_name)
	else:
		import netmanthan.database.mariadb.setup_db

		return netmanthan.database.mariadb.setup_db.setup_help_database(help_db_name)
