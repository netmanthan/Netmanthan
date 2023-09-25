import netmanthan
from netmanthan.model.rename_doc import rename_doc


def execute():
	if netmanthan.db.table_exists("Workflow Action") and not netmanthan.db.table_exists(
		"Workflow Action Master"
	):
		rename_doc("DocType", "Workflow Action", "Workflow Action Master")
		netmanthan.reload_doc("workflow", "doctype", "workflow_action_master")
