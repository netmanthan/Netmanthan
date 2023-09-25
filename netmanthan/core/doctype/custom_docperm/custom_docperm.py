# Copyright (c) 2015, netmanthan Technologies and contributors
# License: MIT. See LICENSE

import netmanthan
from netmanthan.model.document import Document


class CustomDocPerm(Document):
	def on_update(self):
		netmanthan.clear_cache(doctype=self.parent)
