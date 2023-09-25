# Copyright (c) 2015, netmanthan Technologies Pvt. Ltd. and contributors
# License: MIT. See LICENSE

import netmanthan
from netmanthan.model.document import Document


class UnhandledEmail(Document):
	pass


def remove_old_unhandled_emails():
	netmanthan.db.delete(
		"Unhandled Email", {"creation": ("<", netmanthan.utils.add_days(netmanthan.utils.nowdate(), -30))}
	)
