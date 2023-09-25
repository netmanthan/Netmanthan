# Copyright (c) 2018, netmanthan Technologies and contributors
# License: MIT. See LICENSE

import netmanthan
from netmanthan import _
from netmanthan.model.document import Document
from netmanthan.utils import cint


class PrintSettings(Document):
	def validate(self):
		if self.pdf_page_size == "Custom" and not (self.pdf_page_height and self.pdf_page_width):
			netmanthan.throw(_("Page height and width cannot be zero"))

	def on_update(self):
		netmanthan.clear_cache()


@netmanthan.whitelist()
def is_print_server_enabled():
	if not hasattr(netmanthan.local, "enable_print_server"):
		netmanthan.local.enable_print_server = cint(
			netmanthan.db.get_single_value("Print Settings", "enable_print_server")
		)

	return netmanthan.local.enable_print_server
