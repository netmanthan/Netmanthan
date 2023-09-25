import netmanthan
from netmanthan.model.rename_doc import rename_doc


def execute():
	if netmanthan.db.exists("DocType", "Google Maps") and not netmanthan.db.exists(
		"DocType", "Google Maps Settings"
	):
		rename_doc("DocType", "Google Maps", "Google Maps Settings")
