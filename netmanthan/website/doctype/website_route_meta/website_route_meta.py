# Copyright (c) 2019, netmanthan Technologies and contributors
# License: MIT. See LICENSE

from netmanthan.model.document import Document


class WebsiteRouteMeta(Document):
	def autoname(self):
		if self.name and self.name.startswith("/"):
			self.name = self.name[1:]
