# Copyright (c) 2020, netmanthan Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import netmanthan


def execute():
	netmanthan.reload_doc("website", "doctype", "web_page_block")
	# remove unused templates
	netmanthan.delete_doc("Web Template", "Navbar with Links on Right", force=1)
	netmanthan.delete_doc("Web Template", "Footer Horizontal", force=1)
