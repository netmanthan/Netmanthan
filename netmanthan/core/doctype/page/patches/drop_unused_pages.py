import netmanthan


def execute():
	for name in ("desktop", "space"):
		netmanthan.delete_doc("Page", name)
