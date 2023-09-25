import netmanthan


def execute():
	netmanthan.db.delete("DocType", {"name": "Feedback Request"})
