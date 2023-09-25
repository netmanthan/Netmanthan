# Copyright (c) 2015, netmanthan Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import json

import netmanthan


@netmanthan.whitelist()
def update_task(args, field_map):
	"""Updates Doc (called via gantt) based on passed `field_map`"""
	args = netmanthan._dict(json.loads(args))
	field_map = netmanthan._dict(json.loads(field_map))
	d = netmanthan.get_doc(args.doctype, args.name)
	d.set(field_map.start, args.start)
	d.set(field_map.end, args.end)
	d.save()
