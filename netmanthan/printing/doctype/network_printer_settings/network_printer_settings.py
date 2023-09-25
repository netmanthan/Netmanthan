# Copyright (c) 2021, netmanthan Technologies and contributors
# For license information, please see license.txt

import netmanthan
from netmanthan import _
from netmanthan.model.document import Document


class NetworkPrinterSettings(Document):
	@netmanthan.whitelist()
	def get_printers_list(self, ip="127.0.0.1", port=631):
		printer_list = []
		try:
			import cups
		except ImportError:
			netmanthan.throw(
				_(
					"""This feature can not be used as dependencies are missing.
				Please contact your system manager to enable this by installing pycups!"""
				)
			)
			return
		try:
			cups.setServer(self.server_ip)
			cups.setPort(self.port)
			conn = cups.Connection()
			printers = conn.getPrinters()
			for printer_id, printer in printers.items():
				printer_list.append({"value": printer_id, "label": printer["printer-make-and-model"]})

		except RuntimeError:
			netmanthan.throw(_("Failed to connect to server"))
		except netmanthan.ValidationError:
			netmanthan.throw(_("Failed to connect to server"))
		return printer_list


@netmanthan.whitelist()
def get_network_printer_settings():
	return netmanthan.db.get_list("Network Printer Settings", pluck="name")
