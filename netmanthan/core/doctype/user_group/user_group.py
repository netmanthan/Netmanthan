# Copyright (c) 2021, netmanthan Technologies and contributors
# License: MIT. See LICENSE

import netmanthan

# import netmanthan
from netmanthan.model.document import Document


class UserGroup(Document):
	def after_insert(self):
		netmanthan.cache().delete_key("user_groups")

	def on_trash(self):
		netmanthan.cache().delete_key("user_groups")
