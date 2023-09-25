# Copyright (c) 2015, netmanthan Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import json

import netmanthan
from netmanthan import _


@netmanthan.whitelist()
def update_event(args, field_map):
	"""Updates Event (called via calendar) based on passed `field_map`"""
	args = netmanthan._dict(json.loads(args))
	field_map = netmanthan._dict(json.loads(field_map))
	w = netmanthan.get_doc(args.doctype, args.name)
	w.set(field_map.start, args[field_map.start])
	w.set(field_map.end, args.get(field_map.end))
	w.save()


def get_event_conditions(doctype, filters=None):
	"""Returns SQL conditions with user permissions and filters for event queries"""
	from netmanthan.desk.reportview import get_filters_cond

	if not netmanthan.has_permission(doctype):
		netmanthan.throw(_("Not Permitted"), netmanthan.PermissionError)

	return get_filters_cond(doctype, filters, [], with_match_conditions=True)


@netmanthan.whitelist()
def get_events(doctype, start, end, field_map, filters=None, fields=None):
	field_map = netmanthan._dict(json.loads(field_map))
	fields = netmanthan.parse_json(fields)

	doc_meta = netmanthan.get_meta(doctype)
	for d in doc_meta.fields:
		if d.fieldtype == "Color":
			field_map.update({"color": d.fieldname})

	filters = json.loads(filters) if filters else []

	if not fields:
		fields = [field_map.start, field_map.end, field_map.title, "name"]

	if field_map.color:
		fields.append(field_map.color)

	start_date = "ifnull(%s, '0001-01-01 00:00:00')" % field_map.start
	end_date = "ifnull(%s, '2199-12-31 00:00:00')" % field_map.end

	filters += [
		[doctype, start_date, "<=", end],
		[doctype, end_date, ">=", start],
	]
	fields = list({field for field in fields if field})
	return netmanthan.get_list(doctype, fields=fields, filters=filters)
