# Copyright (c) 2015, netmanthan Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE
import netmanthan
from netmanthan.model.document import Document


class ClientScript(Document):
	def on_update(self):
		netmanthan.clear_cache(doctype=self.dt)

	def on_trash(self):
		netmanthan.clear_cache(doctype=self.dt)
