import netmanthan


def execute():
	netmanthan.reload_doc("website", "doctype", "website_theme_ignore_app")
	netmanthan.reload_doc("website", "doctype", "color")
	netmanthan.reload_doc("website", "doctype", "website_theme")
	netmanthan.reload_doc("website", "doctype", "website_settings")

	for theme in netmanthan.get_all("Website Theme"):
		doc = netmanthan.get_doc("Website Theme", theme.name)
		if not doc.get("custom_scss") and doc.theme_scss:
			# move old theme to new theme
			doc.custom_scss = doc.theme_scss

			if doc.background_color:
				setup_color_record(doc.background_color)

			doc.save()


def setup_color_record(color):
	netmanthan.get_doc(
		{
			"doctype": "Color",
			"__newname": color,
			"color": color,
		}
	).save()
