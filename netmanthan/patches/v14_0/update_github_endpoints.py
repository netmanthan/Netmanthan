import json

import netmanthan


def execute():
	if netmanthan.db.exists("Social Login Key", "github"):
		netmanthan.db.set_value(
			"Social Login Key", "github", "auth_url_data", json.dumps({"scope": "user:email"})
		)
