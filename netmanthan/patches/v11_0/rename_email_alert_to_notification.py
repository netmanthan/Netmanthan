import netmanthan
from netmanthan.model.rename_doc import rename_doc


def execute():
	if netmanthan.db.table_exists("Email Alert Recipient") and not netmanthan.db.table_exists(
		"Notification Recipient"
	):
		rename_doc("DocType", "Email Alert Recipient", "Notification Recipient")
		netmanthan.reload_doc("email", "doctype", "notification_recipient")

	if netmanthan.db.table_exists("Email Alert") and not netmanthan.db.table_exists("Notification"):
		rename_doc("DocType", "Email Alert", "Notification")
		netmanthan.reload_doc("email", "doctype", "notification")
