# Copyright (c) 2022, netmanthan Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

import netmanthan


def execute():
	doctypes = netmanthan.get_all("DocType", {"module": "Data Migration", "custom": 0}, pluck="name")
	for doctype in doctypes:
		netmanthan.delete_doc("DocType", doctype, ignore_missing=True)

	netmanthan.delete_doc("Module Def", "Data Migration", ignore_missing=True, force=True)
