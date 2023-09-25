# Copyright (c) 2020, netmanthan Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import netmanthan


def execute():
	netmanthan.reload_doc("email", "doctype", "Newsletter")
	netmanthan.db.sql(
		"""
		UPDATE tabNewsletter
		SET content_type = 'Rich Text'
	"""
	)
