import netmanthan
from netmanthan.utils import cint


def execute():
	netmanthan.reload_doctype("Dropbox Settings")
	check_dropbox_enabled = cint(netmanthan.db.get_single_value("Dropbox Settings", "enabled"))
	if check_dropbox_enabled == 1:
		netmanthan.db.set_single_value("Dropbox Settings", "file_backup", 1)
