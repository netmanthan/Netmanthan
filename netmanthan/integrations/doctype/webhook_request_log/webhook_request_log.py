# Copyright (c) 2021, netmanthan Technologies and contributors
# License: MIT. See LICENSE

import netmanthan
from netmanthan.model.document import Document


class WebhookRequestLog(Document):
	@staticmethod
	def clear_old_logs(days=30):
		from netmanthan.query_builder import Interval
		from netmanthan.query_builder.functions import Now

		table = netmanthan.qb.DocType("Webhook Request Log")
		netmanthan.db.delete(table, filters=(table.modified < (Now() - Interval(days=days))))
