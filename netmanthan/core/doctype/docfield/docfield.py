# Copyright (c) 2015, netmanthan Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import netmanthan
from netmanthan.model.document import Document


class DocField(Document):
	def get_link_doctype(self):
		"""Returns the Link doctype for the docfield (if applicable)
		if fieldtype is Link: Returns "options"
		if fieldtype is Table MultiSelect: Returns "options" of the Link field in the Child Table
		"""
		if self.fieldtype == "Link":
			return self.options

		if self.fieldtype == "Table MultiSelect":
			table_doctype = self.options

			link_doctype = netmanthan.db.get_value(
				"DocField",
				{"fieldtype": "Link", "parenttype": "DocType", "parent": table_doctype, "in_list_view": 1},
				"options",
			)

			return link_doctype

	def get_select_options(self):
		if self.fieldtype == "Select":
			options = self.options or ""
			return [d for d in options.split("\n") if d]
