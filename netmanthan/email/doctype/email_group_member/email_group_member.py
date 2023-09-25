# Copyright (c) 2015, netmanthan Technologies and contributors
# License: MIT. See LICENSE

import netmanthan
from netmanthan.model.document import Document


class EmailGroupMember(Document):
	def after_delete(self):
		email_group = netmanthan.get_doc("Email Group", self.email_group)
		email_group.update_total_subscribers()

	def after_insert(self):
		email_group = netmanthan.get_doc("Email Group", self.email_group)
		email_group.update_total_subscribers()


def after_doctype_insert():
	netmanthan.db.add_unique("Email Group Member", ("email_group", "email"))
