# Copyright (c) 2020, netmanthan Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import netmanthan


def execute():
	"""Enable all the existing Client script"""

	netmanthan.db.sql(
		"""
		UPDATE `tabClient Script` SET enabled=1
	"""
	)
