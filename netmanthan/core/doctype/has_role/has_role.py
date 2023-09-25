# Copyright (c) 2015, netmanthan Technologies and contributors
# License: MIT. See LICENSE

import netmanthan
from netmanthan.model.document import Document


class HasRole(Document):
	def before_insert(self):
		if netmanthan.db.exists("Has Role", {"parent": self.parent, "role": self.role}):
			netmanthan.throw(netmanthan._("User '{0}' already has the role '{1}'").format(self.parent, self.role))
