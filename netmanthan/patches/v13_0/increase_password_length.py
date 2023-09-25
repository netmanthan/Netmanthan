import netmanthan


def execute():
	netmanthan.db.change_column_type("__Auth", column="password", type="TEXT")
