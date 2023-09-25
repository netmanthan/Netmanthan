import netmanthan


def execute():
	providers = netmanthan.get_all("Social Login Key")

	for provider in providers:
		doc = netmanthan.get_doc("Social Login Key", provider)
		doc.set_icon()
		doc.save()
