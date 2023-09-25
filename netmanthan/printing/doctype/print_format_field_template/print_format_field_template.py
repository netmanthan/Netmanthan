# Copyright (c) 2021, netmanthan Technologies and contributors
# For license information, please see license.txt

import netmanthan
from netmanthan import _
from netmanthan.model.document import Document


class PrintFormatFieldTemplate(Document):
	def validate(self):
		if self.standard and not (netmanthan.conf.developer_mode or netmanthan.flags.in_patch):
			netmanthan.throw(_("Enable developer mode to create a standard Print Template"))

	def before_insert(self):
		self.validate_duplicate()

	def on_update(self):
		self.validate_duplicate()
		self.export_doc()

	def validate_duplicate(self):
		if not self.standard:
			return
		if not self.field:
			return

		filters = {"document_type": self.document_type, "field": self.field}
		if not self.is_new():
			filters.update({"name": ("!=", self.name)})
		result = netmanthan.get_all("Print Format Field Template", filters=filters, limit=1)
		if result:
			netmanthan.throw(
				_("A template already exists for field {0} of {1}").format(
					netmanthan.bold(self.field), netmanthan.bold(self.document_type)
				),
				netmanthan.DuplicateEntryError,
				title=_("Duplicate Entry"),
			)

	def export_doc(self):
		from netmanthan.modules.utils import export_module_json

		export_module_json(self, self.standard, self.module)
