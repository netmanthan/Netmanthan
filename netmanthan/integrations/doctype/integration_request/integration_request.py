# Copyright (c) 2015, netmanthan Technologies and contributors
# License: MIT. See LICENSE

import json

import netmanthan
from netmanthan.integrations.utils import json_handler
from netmanthan.model.document import Document


class IntegrationRequest(Document):
	def autoname(self):
		if self.flags._name:
			self.name = self.flags._name

	def clear_old_logs(days=30):
		from netmanthan.query_builder import Interval
		from netmanthan.query_builder.functions import Now

		table = netmanthan.qb.DocType("Integration Request")
		netmanthan.db.delete(table, filters=(table.modified < (Now() - Interval(days=days))))

	def update_status(self, params, status):
		data = json.loads(self.data)
		data.update(params)

		self.data = json.dumps(data)
		self.status = status
		self.save(ignore_permissions=True)
		netmanthan.db.commit()

	def handle_success(self, response):
		"""update the output field with the response along with the relevant status"""
		if isinstance(response, str):
			response = json.loads(response)
		self.db_set("status", "Completed")
		self.db_set("output", json.dumps(response, default=json_handler))

	def handle_failure(self, response):
		"""update the error field with the response along with the relevant status"""
		if isinstance(response, str):
			response = json.loads(response)
		self.db_set("status", "Failed")
		self.db_set("error", json.dumps(response, default=json_handler))
