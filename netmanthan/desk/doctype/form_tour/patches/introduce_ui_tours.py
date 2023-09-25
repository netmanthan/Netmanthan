import json

import netmanthan


def execute():
	"""Handle introduction of UI tours"""
	completed = {}
	for tour in netmanthan.get_all("Form Tour", {"ui_tour": 1}, pluck="name"):
		completed[tour] = {"is_complete": True}

	User = netmanthan.qb.DocType("User")
	netmanthan.qb.update(User).set("onboarding_status", json.dumps(completed)).run()
