import netmanthan
from netmanthan.utils.install import add_standard_navbar_items


def execute():
	# Add standard navbar items for ERPNext in Navbar Settings
	netmanthan.reload_doc("core", "doctype", "navbar_settings")
	netmanthan.reload_doc("core", "doctype", "navbar_item")
	add_standard_navbar_items()
