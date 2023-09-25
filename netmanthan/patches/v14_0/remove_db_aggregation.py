import re

import netmanthan
from netmanthan.query_builder import DocType


def execute():
	"""Replace temporarily available Database Aggregate APIs on netmanthan (develop)

	APIs changed:
	        * netmanthan.db.max => netmanthan.qb.max
	        * netmanthan.db.min => netmanthan.qb.min
	        * netmanthan.db.sum => netmanthan.qb.sum
	        * netmanthan.db.avg => netmanthan.qb.avg
	"""
	ServerScript = DocType("Server Script")
	server_scripts = (
		netmanthan.qb.from_(ServerScript)
		.where(
			ServerScript.script.like("%netmanthan.db.max(%")
			| ServerScript.script.like("%netmanthan.db.min(%")
			| ServerScript.script.like("%netmanthan.db.sum(%")
			| ServerScript.script.like("%netmanthan.db.avg(%")
		)
		.select("name", "script")
		.run(as_dict=True)
	)

	for server_script in server_scripts:
		name, script = server_script["name"], server_script["script"]

		for agg in ["avg", "max", "min", "sum"]:
			script = re.sub(f"netmanthan.db.{agg}\\(", f"netmanthan.qb.{agg}(", script)

		netmanthan.db.update("Server Script", name, "script", script)
