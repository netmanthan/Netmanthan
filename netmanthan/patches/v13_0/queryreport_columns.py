# Copyright (c) 2021, netmanthan Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import json

import netmanthan


def execute():
	"""Convert Query Report json to support other content"""
	records = netmanthan.get_all("Report", filters={"json": ["!=", ""]}, fields=["name", "json"])
	for record in records:
		jstr = record["json"]
		data = json.loads(jstr)
		if isinstance(data, list):
			# double escape braces
			jstr = f'{{"columns":{jstr}}}'
			netmanthan.db.update("Report", record["name"], "json", jstr)
