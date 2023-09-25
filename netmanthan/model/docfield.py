# Copyright (c) 2015, netmanthan Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

"""docfield utililtes"""

import netmanthan


def rename(doctype, fieldname, newname):
	"""rename docfield"""
	df = netmanthan.db.sql(
		"""select * from tabDocField where parent=%s and fieldname=%s""", (doctype, fieldname), as_dict=1
	)
	if not df:
		return

	df = df[0]

	if netmanthan.db.get_value("DocType", doctype, "issingle"):
		update_single(df, newname)
	else:
		update_table(df, newname)
		update_parent_field(df, newname)


def update_single(f, new):
	"""update in tabSingles"""
	netmanthan.db.begin()
	netmanthan.db.sql(
		"""update tabSingles set field=%s where doctype=%s and field=%s""",
		(new, f["parent"], f["fieldname"]),
	)
	netmanthan.db.commit()


def update_table(f, new):
	"""update table"""
	query = get_change_column_query(f, new)
	if query:
		netmanthan.db.sql(query)


def update_parent_field(f, new):
	"""update 'parentfield' in tables"""
	if f["fieldtype"] in netmanthan.model.table_fields:
		netmanthan.db.begin()
		netmanthan.db.sql(
			"""update `tab{}` set parentfield={} where parentfield={}""".format(f["options"], "%s", "%s"),
			(new, f["fieldname"]),
		)
		netmanthan.db.commit()


def get_change_column_query(f, new):
	"""generate change fieldname query"""
	desc = netmanthan.db.sql("desc `tab%s`" % f["parent"])
	for d in desc:
		if d[0] == f["fieldname"]:
			return "alter table `tab{}` change `{}` `{}` {}".format(f["parent"], f["fieldname"], new, d[1])


def supports_translation(fieldtype):
	return fieldtype in ["Data", "Select", "Text", "Small Text", "Text Editor"]
