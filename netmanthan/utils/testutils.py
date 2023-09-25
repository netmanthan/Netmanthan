# Copyright (c) 2015, netmanthan Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE
import netmanthan


def add_custom_field(doctype, fieldname, fieldtype="Data", options=None):
	netmanthan.get_doc(
		{
			"doctype": "Custom Field",
			"dt": doctype,
			"fieldname": fieldname,
			"fieldtype": fieldtype,
			"options": options,
		}
	).insert()


def clear_custom_fields(doctype):
	netmanthan.db.delete("Custom Field", {"dt": doctype})
	netmanthan.clear_cache(doctype=doctype)
