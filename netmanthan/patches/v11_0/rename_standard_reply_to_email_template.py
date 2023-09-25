import netmanthan
from netmanthan.model.rename_doc import rename_doc


def execute():
	if netmanthan.db.table_exists("Standard Reply") and not netmanthan.db.table_exists("Email Template"):
		rename_doc("DocType", "Standard Reply", "Email Template")
		netmanthan.reload_doc("email", "doctype", "email_template")
