# Copyright (c) 2020, netmanthan Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import netmanthan
from netmanthan.model.utils.rename_field import rename_field


def execute():
	"""
	Change notification recipient fields from email to receiver fields
	"""
	netmanthan.reload_doc("Email", "doctype", "Notification Recipient")
	netmanthan.reload_doc("Email", "doctype", "Notification")

	rename_field("Notification Recipient", "email_by_document_field", "receiver_by_document_field")
	rename_field("Notification Recipient", "email_by_role", "receiver_by_role")
