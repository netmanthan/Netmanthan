import netmanthan


def execute():
	netmanthan.reload_doctype("Letter Head")

	# source of all existing letter heads must be HTML
	netmanthan.db.sql("update `tabLetter Head` set source = 'HTML'")
