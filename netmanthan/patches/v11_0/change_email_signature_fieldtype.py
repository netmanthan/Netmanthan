# Copyright (c) 2018, netmanthan Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import netmanthan


def execute():
	signatures = netmanthan.db.get_list(
		"User", {"email_signature": ["!=", ""]}, ["name", "email_signature"]
	)
	netmanthan.reload_doc("core", "doctype", "user")
	for d in signatures:
		signature = d.get("email_signature")
		signature = signature.replace("\n", "<br>")
		signature = "<div>" + signature + "</div>"
		netmanthan.db.set_value("User", d.get("name"), "email_signature", signature)
