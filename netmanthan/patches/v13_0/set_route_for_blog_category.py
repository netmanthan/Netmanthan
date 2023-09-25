import netmanthan


def execute():
	categories = netmanthan.get_list("Blog Category")
	for category in categories:
		doc = netmanthan.get_doc("Blog Category", category["name"])
		doc.set_route()
		doc.save()
