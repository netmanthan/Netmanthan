import netmanthan
from netmanthan.desk.doctype.notification_settings.notification_settings import (
	create_notification_settings,
)


def execute():
	netmanthan.reload_doc("desk", "doctype", "notification_settings")
	netmanthan.reload_doc("desk", "doctype", "notification_subscribed_document")

	users = netmanthan.get_all("User", fields=["name"])
	for user in users:
		create_notification_settings(user.name)
