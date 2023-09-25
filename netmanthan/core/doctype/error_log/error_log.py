# Copyright (c) 2015, netmanthan Technologies and contributors
# License: MIT. See LICENSE

import netmanthan
from netmanthan.model.document import Document
from netmanthan.query_builder import Interval
from netmanthan.query_builder.functions import Now


class ErrorLog(Document):
	def onload(self):
		if not self.seen and not netmanthan.flags.read_only:
			self.db_set("seen", 1, update_modified=0)
			netmanthan.db.commit()

	@staticmethod
	def clear_old_logs(days=30):
		table = netmanthan.qb.DocType("Error Log")
		netmanthan.db.delete(table, filters=(table.modified < (Now() - Interval(days=days))))


@netmanthan.whitelist()
def clear_error_logs():
	"""Flush all Error Logs"""
	netmanthan.only_for("System Manager")
	netmanthan.db.truncate("Error Log")
