# Copyright (c) 2017, netmanthan Technologies and contributors
# License: MIT. See LICENSE

import netmanthan
from netmanthan.model.document import Document


class PrintStyle(Document):
	def validate(self):
		if (
			self.standard == 1
			and not netmanthan.local.conf.get("developer_mode")
			and not (netmanthan.flags.in_import or netmanthan.flags.in_test)
		):

			netmanthan.throw(netmanthan._("Standard Print Style cannot be changed. Please duplicate to edit."))

	def on_update(self):
		self.export_doc()

	def export_doc(self):
		# export
		from netmanthan.modules.utils import export_module_json

		export_module_json(self, self.standard == 1, "Printing")
