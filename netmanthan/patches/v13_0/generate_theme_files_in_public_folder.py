# Copyright (c) 2020, netmanthan Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import netmanthan


def execute():
	netmanthan.reload_doc("website", "doctype", "website_theme_ignore_app")
	themes = netmanthan.get_all(
		"Website Theme", filters={"theme_url": ("not like", "/files/website_theme/%")}
	)
	for theme in themes:
		doc = netmanthan.get_doc("Website Theme", theme.name)
		try:
			doc.generate_bootstrap_theme()
			doc.save()
		except Exception:
			print("Ignoring....")
			print(netmanthan.get_traceback())
