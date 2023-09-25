# Copyright (c) 2015, netmanthan Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import netmanthan

ignore_doctypes = ("DocType", "Print Format", "Role", "Module Def", "Communication", "ToDo")


def notify_link_count(doctype, name):
	"""updates link count for given document"""
	if hasattr(netmanthan.local, "link_count"):
		if (doctype, name) in netmanthan.local.link_count:
			netmanthan.local.link_count[(doctype, name)] += 1
		else:
			netmanthan.local.link_count[(doctype, name)] = 1


def flush_local_link_count():
	"""flush from local before ending request"""
	if not getattr(netmanthan.local, "link_count", None):
		return

	link_count = netmanthan.cache().get_value("_link_count")
	if not link_count:
		link_count = {}

		for key, value in netmanthan.local.link_count.items():
			if key in link_count:
				link_count[key] += netmanthan.local.link_count[key]
			else:
				link_count[key] = netmanthan.local.link_count[key]

	netmanthan.cache().set_value("_link_count", link_count)


def update_link_count():
	"""increment link count in the `idx` column for the given document"""
	link_count = netmanthan.cache().get_value("_link_count")

	if link_count:
		for key, count in link_count.items():
			if key[0] not in ignore_doctypes:
				try:
					netmanthan.db.sql(
						f"update `tab{key[0]}` set idx = idx + {count} where name=%s",
						key[1],
						auto_commit=1,
					)
				except Exception as e:
					if not netmanthan.db.is_table_missing(e):  # table not found, single
						raise e
	# reset the count
	netmanthan.cache().delete_value("_link_count")
