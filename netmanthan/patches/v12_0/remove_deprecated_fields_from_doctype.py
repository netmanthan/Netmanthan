import netmanthan


def execute():
	netmanthan.reload_doc("core", "doctype", "doctype_link")
	netmanthan.reload_doc("core", "doctype", "doctype_action")
	netmanthan.reload_doc("core", "doctype", "doctype")
	netmanthan.model.delete_fields(
		{"DocType": ["hide_heading", "image_view", "read_only_onload"]}, delete=1
	)

	netmanthan.db.delete("Property Setter", {"property": "read_only_onload"})
