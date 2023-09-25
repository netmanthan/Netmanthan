# Copyright (c) 2019, netmanthan Technologies and contributors
# License: MIT. See LICENSE

import netmanthan
from netmanthan.model.document import Document
from netmanthan.query_builder import Interval
from netmanthan.query_builder.functions import Now


class ScheduledJobLog(Document):
	@staticmethod
	def clear_old_logs(days=90):
		table = netmanthan.qb.DocType("Scheduled Job Log")
		netmanthan.db.delete(table, filters=(table.modified < (Now() - Interval(days=days))))
