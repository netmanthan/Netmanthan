import netmanthan
from netmanthan.model.rename_doc import rename_doc


def execute():
	if netmanthan.db.exists("DocType", "Client Script"):
		return

	netmanthan.flags.ignore_route_conflict_validation = True
	rename_doc("DocType", "Custom Script", "Client Script")
	netmanthan.flags.ignore_route_conflict_validation = False

	netmanthan.reload_doctype("Client Script", force=True)
