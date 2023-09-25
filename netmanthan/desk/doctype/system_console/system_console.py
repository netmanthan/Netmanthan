# Copyright (c) 2020, netmanthan Technologies and contributors
# License: MIT. See LICENSE

import json

import netmanthan
from netmanthan.model.document import Document
from netmanthan.utils.safe_exec import read_sql, safe_exec


class SystemConsole(Document):
	def run(self):
		netmanthan.only_for("System Manager")
		try:
			netmanthan.local.debug_log = []
			if self.type == "Python":
				safe_exec(self.console)
				self.output = "\n".join(netmanthan.debug_log)
			elif self.type == "SQL":
				self.output = netmanthan.as_json(read_sql(self.console, as_dict=1))
		except Exception:
			self.commit = False
			self.output = netmanthan.get_traceback()

		if self.commit:
			netmanthan.db.commit()
		else:
			netmanthan.db.rollback()

		netmanthan.get_doc(dict(doctype="Console Log", script=self.console)).insert()
		netmanthan.db.commit()


@netmanthan.whitelist()
def execute_code(doc):
	console = netmanthan.get_doc(json.loads(doc))
	console.run()
	return console.as_dict()


@netmanthan.whitelist()
def show_processlist():
	netmanthan.only_for("System Manager")

	return netmanthan.db.multisql(
		{
			"postgres": """
			SELECT pid AS "Id",
				query_start AS "Time",
				state AS "State",
				query AS "Info",
				wait_event AS "Progress"
			FROM pg_stat_activity""",
			"mariadb": "show full processlist",
		},
		as_dict=True,
	)
