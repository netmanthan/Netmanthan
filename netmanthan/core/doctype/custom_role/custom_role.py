# Copyright (c) 2015, netmanthan Technologies and contributors
# License: MIT. See LICENSE

import netmanthan
from netmanthan.model.document import Document


class CustomRole(Document):
	def validate(self):
		if self.report and not self.ref_doctype:
			self.ref_doctype = netmanthan.db.get_value("Report", self.report, "ref_doctype")


def get_custom_allowed_roles(field, name):
	allowed_roles = []
	custom_role = netmanthan.db.get_value("Custom Role", {field: name}, "name")
	if custom_role:
		custom_role_doc = netmanthan.get_doc("Custom Role", custom_role)
		allowed_roles = [d.role for d in custom_role_doc.roles]

	return allowed_roles
