# Copyright (c) 2015, netmanthan Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import netmanthan
import netmanthan.utils.user
from netmanthan.model import data_fieldtypes
from netmanthan.permissions import rights


def execute(filters=None):
	netmanthan.only_for("System Manager")

	user, doctype, show_permissions = (
		filters.get("user"),
		filters.get("doctype"),
		filters.get("show_permissions"),
	)

	columns, fields = get_columns_and_fields(doctype)
	data = netmanthan.get_list(doctype, fields=fields, as_list=True, user=user)

	if show_permissions:
		columns = columns + [netmanthan.unscrub(right) + ":Check:80" for right in rights]
		data = list(data)
		for i, doc in enumerate(data):
			permission = netmanthan.permissions.get_doc_permissions(netmanthan.get_doc(doctype, doc[0]), user)
			data[i] = doc + tuple(permission.get(right) for right in rights)

	return columns, data


def get_columns_and_fields(doctype):
	columns = [f"Name:Link/{doctype}:200"]
	fields = ["`name`"]
	for df in netmanthan.get_meta(doctype).fields:
		if df.in_list_view and df.fieldtype in data_fieldtypes:
			fields.append(f"`{df.fieldname}`")
			fieldtype = f"Link/{df.options}" if df.fieldtype == "Link" else df.fieldtype
			columns.append(
				"{label}:{fieldtype}:{width}".format(
					label=df.label, fieldtype=fieldtype, width=df.width or 100
				)
			)

	return columns, fields


@netmanthan.whitelist()
@netmanthan.validate_and_sanitize_search_inputs
def query_doctypes(doctype, txt, searchfield, start, page_len, filters):
	user = filters.get("user")
	user_perms = netmanthan.utils.user.UserPermissions(user)
	user_perms.build_permissions()
	can_read = user_perms.can_read  # Does not include child tables
	include_single_doctypes = filters.get("include_single_doctypes")

	single_doctypes = [d[0] for d in netmanthan.db.get_values("DocType", {"issingle": 1})]

	out = []
	for dt in can_read:
		if txt.lower().replace("%", "") in dt.lower() and (
			include_single_doctypes or dt not in single_doctypes
		):
			out.append([dt])

	return out
