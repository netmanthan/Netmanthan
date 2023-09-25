# Copyright (c) 2019, netmanthan Technologies and contributors
# License: MIT. See LICENSE

import json

import netmanthan
from netmanthan import _
from netmanthan.model.document import Document


class SessionDefaultSettings(Document):
	pass


@netmanthan.whitelist()
def get_session_default_values():
	settings = netmanthan.get_single("Session Default Settings")
	fields = []
	for default_values in settings.session_defaults:
		reference_doctype = netmanthan.scrub(default_values.ref_doctype)
		fields.append(
			{
				"fieldname": reference_doctype,
				"fieldtype": "Link",
				"options": default_values.ref_doctype,
				"label": _("Default {0}").format(_(default_values.ref_doctype)),
				"default": netmanthan.defaults.get_user_default(reference_doctype),
			}
		)
	return json.dumps(fields)


@netmanthan.whitelist()
def set_session_default_values(default_values):
	default_values = netmanthan.parse_json(default_values)
	for entry in default_values:
		try:
			netmanthan.defaults.set_user_default(entry, default_values.get(entry))
		except Exception:
			return
	return "success"


# called on hook 'on_logout' to clear defaults for the session
def clear_session_defaults():
	settings = netmanthan.get_single("Session Default Settings").session_defaults
	for entry in settings:
		netmanthan.defaults.clear_user_default(netmanthan.scrub(entry.ref_doctype))
