import os

import netmanthan


def setup_database(force, source_sql=None, verbose=False):
	root_conn = get_root_connection(netmanthan.flags.root_login, netmanthan.flags.root_password)
	root_conn.commit()
	root_conn.sql("end")
	root_conn.sql(f"DROP DATABASE IF EXISTS `{netmanthan.conf.db_name}`")
	root_conn.sql(f"DROP USER IF EXISTS {netmanthan.conf.db_name}")
	root_conn.sql(f"CREATE DATABASE `{netmanthan.conf.db_name}`")
	root_conn.sql(f"CREATE user {netmanthan.conf.db_name} password '{netmanthan.conf.db_password}'")
	root_conn.sql("GRANT ALL PRIVILEGES ON DATABASE `{0}` TO {0}".format(netmanthan.conf.db_name))
	root_conn.close()

	bootstrap_database(netmanthan.conf.db_name, verbose, source_sql=source_sql)
	netmanthan.connect()


def bootstrap_database(db_name, verbose, source_sql=None):
	netmanthan.connect(db_name=db_name)
	import_db_from_sql(source_sql, verbose)
	netmanthan.connect(db_name=db_name)

	if "tabDefaultValue" not in netmanthan.db.get_tables():
		import sys

		from click import secho

		secho(
			"Table 'tabDefaultValue' missing in the restored site. "
			"This may be due to incorrect permissions or the result of a restore from a bad backup file. "
			"Database not installed correctly.",
			fg="red",
		)
		sys.exit(1)


def import_db_from_sql(source_sql=None, verbose=False):
	from shutil import which
	from subprocess import PIPE, run

	# we can't pass psql password in arguments in postgresql as mysql. So
	# set password connection parameter in environment variable
	subprocess_env = os.environ.copy()
	subprocess_env["PGPASSWORD"] = str(netmanthan.conf.db_password)

	# bootstrap db
	if not source_sql:
		source_sql = os.path.join(os.path.dirname(__file__), "framework_postgres.sql")

	pv = which("pv")

	_command = (
		f"psql {netmanthan.conf.db_name} "
		f"-h {netmanthan.conf.db_host or 'localhost'} -p {str(netmanthan.conf.db_port or '5432')} "
		f"-U {netmanthan.conf.db_name}"
	)

	if pv:
		command = f"{pv} {source_sql} | " + _command
	else:
		command = _command + f" -f {source_sql}"

	print("Restoring Database file...")
	if verbose:
		print(command)

	restore_proc = run(command, env=subprocess_env, shell=True, stdout=PIPE)

	if verbose:
		print(
			f"\nSTDOUT by psql:\n{restore_proc.stdout.decode()}\nImported from Database File: {source_sql}"
		)


def setup_help_database(help_db_name):
	root_conn = get_root_connection(netmanthan.flags.root_login, netmanthan.flags.root_password)
	root_conn.sql(f"DROP DATABASE IF EXISTS `{help_db_name}`")
	root_conn.sql(f"DROP USER IF EXISTS {help_db_name}")
	root_conn.sql(f"CREATE DATABASE `{help_db_name}`")
	root_conn.sql(f"CREATE user {help_db_name} password '{help_db_name}'")
	root_conn.sql("GRANT ALL PRIVILEGES ON DATABASE `{0}` TO {0}".format(help_db_name))


def get_root_connection(root_login=None, root_password=None):
	if not netmanthan.local.flags.root_connection:
		if not root_login:
			root_login = netmanthan.conf.get("root_login") or None

		if not root_login:
			root_login = input("Enter postgres super user: ")

		if not root_password:
			root_password = netmanthan.conf.get("root_password") or None

		if not root_password:
			from getpass import getpass

			root_password = getpass("Postgres super user password: ")

		netmanthan.local.flags.root_connection = netmanthan.database.get_db(
			user=root_login, password=root_password
		)

	return netmanthan.local.flags.root_connection


def drop_user_and_database(db_name, root_login, root_password):
	root_conn = get_root_connection(
        netmanthan.flags.root_login or root_login, netmanthan.flags.root_password or root_password
	)
	root_conn.commit()
	root_conn.sql(
		"SELECT pg_terminate_backend (pg_stat_activity.pid) FROM pg_stat_activity WHERE pg_stat_activity.datname = %s",
		(db_name,),
	)
	root_conn.sql("end")
	root_conn.sql(f"DROP DATABASE IF EXISTS {db_name}")
	root_conn.sql(f"DROP USER IF EXISTS {db_name}")
