# Copyright (c) 2020, netmanthan Technologies and contributors
# License: MIT. See LICENSE

import json

import netmanthan

# import netmanthan
from netmanthan.model.document import Document


class DashboardSettings(Document):
	pass


@netmanthan.whitelist()
def create_dashboard_settings(user):
	if not netmanthan.db.exists("Dashboard Settings", user):
		doc = netmanthan.new_doc("Dashboard Settings")
		doc.name = user
		doc.insert(ignore_permissions=True)
		netmanthan.db.commit()
		return doc


def get_permission_query_conditions(user):
	if not user:
		user = netmanthan.session.user

	return f"""(`tabDashboard Settings`.name = {netmanthan.db.escape(user)})"""


@netmanthan.whitelist()
def save_chart_config(reset, config, chart_name):
	reset = netmanthan.parse_json(reset)
	doc = netmanthan.get_doc("Dashboard Settings", netmanthan.session.user)
	chart_config = netmanthan.parse_json(doc.chart_config) or {}

	if reset:
		chart_config[chart_name] = {}
	else:
		config = netmanthan.parse_json(config)
		if not chart_name in chart_config:
			chart_config[chart_name] = {}
		chart_config[chart_name].update(config)

	netmanthan.db.set_value(
		"Dashboard Settings", netmanthan.session.user, "chart_config", json.dumps(chart_config)
	)
