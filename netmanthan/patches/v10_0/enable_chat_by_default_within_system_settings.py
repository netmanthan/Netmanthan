import netmanthan


def execute():
	netmanthan.reload_doctype("System Settings")
	doc = netmanthan.get_single("System Settings")
	doc.enable_chat = 1

	# Changes prescribed by Nabin Hait (nabin@netmanthan.io)
	doc.flags.ignore_mandatory = True
	doc.flags.ignore_permissions = True

	doc.save()
