# Copyright (c) 2020, netmanthan Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import netmanthan


def execute():
	netmanthan.delete_doc("DocType", "Package Publish Tool", ignore_missing=True)
	netmanthan.delete_doc("DocType", "Package Document Type", ignore_missing=True)
	netmanthan.delete_doc("DocType", "Package Publish Target", ignore_missing=True)
