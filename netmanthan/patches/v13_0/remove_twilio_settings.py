# Copyright (c) 2015, netmanthan Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import netmanthan


def execute():
	"""Add missing Twilio patch.

	While making Twilio as a standaone app, we missed to delete Twilio records from DB through migration. Adding the missing patch.
	"""
	netmanthan.delete_doc_if_exists("DocType", "Twilio Number Group")
	if twilio_settings_doctype_in_integrations():
		netmanthan.delete_doc_if_exists("DocType", "Twilio Settings")
		netmanthan.db.delete("Singles", {"doctype": "Twilio Settings"})


def twilio_settings_doctype_in_integrations() -> bool:
	"""Check Twilio Settings doctype exists in integrations module or not."""
	return netmanthan.db.exists("DocType", {"name": "Twilio Settings", "module": "Integrations"})
