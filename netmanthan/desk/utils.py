# Copyright (c) 2020, netmanthan Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import netmanthan


def validate_route_conflict(doctype, name):
	"""
	Raises exception if name clashes with routes from other documents for /app routing
	"""

	if netmanthan.flags.in_migrate:
		return

	all_names = []
	for _doctype in ["Page", "Workspace", "DocType"]:
		all_names.extend(
			[slug(d) for d in netmanthan.get_all(_doctype, pluck="name") if (doctype != _doctype and d != name)]
		)

	if slug(name) in all_names:
		netmanthan.msgprint(netmanthan._("Name already taken, please set a new name"))
		raise netmanthan.NameError


def slug(name):
	return name.lower().replace(" ", "-")
