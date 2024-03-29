# Copyright (c) 2015, netmanthan Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

# model __init__.py
import netmanthan

data_fieldtypes = (
	"Currency",
	"Int",
	"Long Int",
	"Float",
	"Percent",
	"Check",
	"Small Text",
	"Long Text",
	"Code",
	"Text Editor",
	"Markdown Editor",
	"HTML Editor",
	"Date",
	"Datetime",
	"Time",
	"Text",
	"Data",
	"Link",
	"Dynamic Link",
	"Password",
	"Select",
	"Rating",
	"Read Only",
	"Attach",
	"Attach Image",
	"Signature",
	"Color",
	"Barcode",
	"Geolocation",
	"Duration",
	"Icon",
	"Phone",
	"Autocomplete",
	"JSON",
)

float_like_fields = {"Float", "Currency", "Percent"}
datetime_fields = {"Datetime", "Date", "Time"}

attachment_fieldtypes = (
	"Attach",
	"Attach Image",
)

no_value_fields = (
	"Section Break",
	"Column Break",
	"Tab Break",
	"HTML",
	"Table",
	"Table MultiSelect",
	"Button",
	"Image",
	"Fold",
	"Heading",
)

display_fieldtypes = (
	"Section Break",
	"Column Break",
	"Tab Break",
	"HTML",
	"Button",
	"Image",
	"Fold",
	"Heading",
)

numeric_fieldtypes = ("Currency", "Int", "Long Int", "Float", "Percent", "Check")

data_field_options = ("Email", "Name", "Phone", "URL", "Barcode")

default_fields = (
	"doctype",
	"name",
	"owner",
	"creation",
	"modified",
	"modified_by",
	"docstatus",
	"idx",
)

child_table_fields = ("parent", "parentfield", "parenttype")

optional_fields = ("_user_tags", "_comments", "_assign", "_liked_by", "_seen")

table_fields = ("Table", "Table MultiSelect")

core_doctypes_list = (
	"DefaultValue",
	"DocType",
	"DocField",
	"DocPerm",
	"DocType Action",
	"DocType Link",
	"User",
	"Role",
	"Has Role",
	"Page",
	"Module Def",
	"Print Format",
	"Report",
	"Customize Form",
	"Customize Form Field",
	"Property Setter",
	"Custom Field",
	"Client Script",
)

log_types = (
	"Version",
	"Error Log",
	"Scheduled Job Log",
	"Event Sync Log",
	"Event Update Log",
	"Access Log",
	"View Log",
	"Activity Log",
	"Energy Point Log",
	"Notification Log",
	"Email Queue",
	"DocShare",
	"Document Follow",
	"Console Log",
)


def delete_fields(args_dict, delete=0):
	"""
	Delete a field.
	* Deletes record from `tabDocField`
	* If not single doctype: Drops column from table
	* If single, deletes record from `tabSingles`
	args_dict = { dt: [field names] }
	"""
	import netmanthan.utils

	for dt in args_dict:
		fields = args_dict[dt]
		if not fields:
			continue

		netmanthan.db.delete(
			"DocField",
			{
				"parent": dt,
				"fieldname": ("in", fields),
			},
		)

		# Delete the data/column only if delete is specified
		if not delete:
			continue

		if netmanthan.db.get_value("DocType", dt, "issingle"):
			netmanthan.db.delete(
				"Singles",
				{
					"doctype": dt,
					"field": ("in", fields),
				},
			)
		else:
			existing_fields = netmanthan.db.describe(dt)
			existing_fields = existing_fields and [e[0] for e in existing_fields] or []
			fields_need_to_delete = set(fields) & set(existing_fields)
			if not fields_need_to_delete:
				continue

			if netmanthan.db.db_type == "mariadb":
				# mariadb implicitly commits before DDL, make it explicit
				netmanthan.db.commit()

			query = "ALTER TABLE `tab%s` " % dt + ", ".join(
				"DROP COLUMN `%s`" % f for f in fields_need_to_delete
			)
			netmanthan.db.sql(query)

		if netmanthan.db.db_type == "postgres":
			# commit the results to db
			netmanthan.db.commit()


def get_permitted_fields(
	doctype: str,
	parenttype: str | None = None,
	user: str | None = None,
	permission_type: str | None = None,
) -> list[str]:
	meta = netmanthan.get_meta(doctype)
	valid_columns = meta.get_valid_columns()

	if doctype in core_doctypes_list:
		return valid_columns

	# DocType has only fields of type Table (Table, Table MultiSelect)
	if set(valid_columns).issubset(default_fields):
		return valid_columns

	if permission_type is None:
		permission_type = "select" if netmanthan.only_has_select_perm(doctype, user=user) else "read"

	if permitted_fields := meta.get_permitted_fieldnames(
		parenttype=parenttype, user=user, permission_type=permission_type
	):
		if permission_type == "select":
			return permitted_fields

		meta_fields = meta.default_fields.copy()
		optional_meta_fields = [x for x in optional_fields if x in valid_columns]

		if meta.istable:
			meta_fields.extend(child_table_fields)

		return meta_fields + permitted_fields + optional_meta_fields

	return []


def is_default_field(fieldname: str) -> bool:
	return fieldname in default_fields
