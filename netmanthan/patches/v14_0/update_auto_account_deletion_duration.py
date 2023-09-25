import netmanthan


def execute():
	days = netmanthan.db.get_single_value("Website Settings", "auto_account_deletion")
	netmanthan.db.set_single_value("Website Settings", "auto_account_deletion", days * 24)
