# Copyright (c) 2015, netmanthan Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import netmanthan


@netmanthan.whitelist()
def get(name):
	"""
	Return the :term:`doclist` of the `Page` specified by `name`
	"""
	page = netmanthan.get_doc("Page", name)
	if page.is_permitted():
		page.load_assets()
		docs = netmanthan._dict(page.as_dict())
		if getattr(page, "_dynamic_page", None):
			docs["_dynamic_page"] = 1

		return docs
	else:
		netmanthan.response["403"] = 1
		raise netmanthan.PermissionError("No read permission for Page %s" % (page.title or name))


@netmanthan.whitelist(allow_guest=True)
def getpage():
	"""
	Load the page from `netmanthan.form` and send it via `netmanthan.response`
	"""
	page = netmanthan.form_dict.get("name")
	doc = get(page)

	netmanthan.response.docs.append(doc)


def has_permission(page):
	if netmanthan.session.user == "Administrator" or "System Manager" in netmanthan.get_roles():
		return True

	page_roles = [d.role for d in page.get("roles")]
	if page_roles:
		if netmanthan.session.user == "Guest" and "Guest" not in page_roles:
			return False
		elif not set(page_roles).intersection(set(netmanthan.get_roles())):
			# check if roles match
			return False

	if not netmanthan.has_permission("Page", ptype="read", doc=page):
		# check if there are any user_permissions
		return False
	else:
		# hack for home pages! if no Has Roles, allow everyone to see!
		return True
