import netmanthan


def execute():
	item = netmanthan.db.exists("Navbar Item", {"item_label": "Background Jobs"})
	if not item:
		return

	netmanthan.delete_doc("Navbar Item", item)
