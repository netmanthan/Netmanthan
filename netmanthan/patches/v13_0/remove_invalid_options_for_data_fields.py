# Copyright (c) 2022, netmanthan and Contributors
# License: MIT. See LICENSE


import netmanthan
from netmanthan.model import data_field_options


def execute():
	custom_field = netmanthan.qb.DocType("Custom Field")
	(
		netmanthan.qb.update(custom_field)
		.set(custom_field.options, None)
		.where((custom_field.fieldtype == "Data") & (custom_field.options.notin(data_field_options)))
	).run()
