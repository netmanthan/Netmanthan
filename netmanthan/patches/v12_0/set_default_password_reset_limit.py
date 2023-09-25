# Copyright (c) 2015, netmanthan Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import netmanthan


def execute():
	netmanthan.reload_doc("core", "doctype", "system_settings", force=1)
	netmanthan.db.set_single_value("System Settings", "password_reset_limit", 3)
