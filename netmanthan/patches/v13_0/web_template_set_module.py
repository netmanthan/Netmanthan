# Copyright (c) 2020, netmanthan Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import netmanthan


def execute():
	"""Set default module for standard Web Template, if none."""
	netmanthan.reload_doc("website", "doctype", "Web Template Field")
	netmanthan.reload_doc("website", "doctype", "web_template")

	standard_templates = netmanthan.get_list("Web Template", {"standard": 1})
	for template in standard_templates:
		doc = netmanthan.get_doc("Web Template", template.name)
		if not doc.module:
			doc.module = "Website"
			doc.save()
