# Copyright (c) 2021, netmanthan Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt


import netmanthan


def execute():
	netmanthan.reload_doc("website", "doctype", "web_form_list_column")
	netmanthan.reload_doctype("Web Form")

	for web_form in netmanthan.get_all("Web Form", fields=["*"]):
		if web_form.allow_multiple and not web_form.show_list:
			netmanthan.db.set_value("Web Form", web_form.name, "show_list", True)
