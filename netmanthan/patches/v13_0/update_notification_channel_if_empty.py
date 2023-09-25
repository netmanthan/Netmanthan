# Copyright (c) 2020, netmanthan Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import netmanthan


def execute():

	netmanthan.reload_doc("Email", "doctype", "Notification")

	notifications = netmanthan.get_all("Notification", {"is_standard": 1}, {"name", "channel"})
	for notification in notifications:
		if not notification.channel:
			netmanthan.db.set_value(
				"Notification", notification.name, "channel", "Email", update_modified=False
			)
			netmanthan.db.commit()
