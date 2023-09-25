# Copyright (c) 2022, netmanthan Technologies and contributors
# License: MIT. See LICENSE

import json

import netmanthan
from netmanthan import _
from netmanthan.config import get_modules_from_all_apps_for_user
from netmanthan.model.document import Document
from netmanthan.modules.export_file import export_to_files
from netmanthan.query_builder import DocType


class Dashboard(Document):
	def on_update(self):
		if self.is_default:
			# make all other dashboards non-default
			DashBoard = DocType("Dashboard")

			netmanthan.qb.update(DashBoard).set(DashBoard.is_default, 0).where(
				DashBoard.name != self.name
			).run()

		if netmanthan.conf.developer_mode and self.is_standard:
			export_to_files(
				record_list=[["Dashboard", self.name, f"{self.module} Dashboard"]], record_module=self.module
			)

	def validate(self):
		if not netmanthan.conf.developer_mode and self.is_standard:
			netmanthan.throw(_("Cannot edit Standard Dashboards"))

		if self.is_standard:
			non_standard_docs_map = {
				"Dashboard Chart": get_non_standard_charts_in_dashboard(self),
				"Number Card": get_non_standard_cards_in_dashboard(self),
			}

			if non_standard_docs_map["Dashboard Chart"] or non_standard_docs_map["Number Card"]:
				message = get_non_standard_warning_message(non_standard_docs_map)
				netmanthan.throw(message, title=_("Standard Not Set"), is_minimizable=True)

		self.validate_custom_options()

	def validate_custom_options(self):
		if self.chart_options:
			try:
				json.loads(self.chart_options)
			except ValueError as error:
				netmanthan.throw(_("Invalid json added in the custom options: {0}").format(error))


def get_permission_query_conditions(user):
	if not user:
		user = netmanthan.session.user

	if user == "Administrator":
		return

	roles = netmanthan.get_roles(user)
	if "System Manager" in roles:
		return None

	allowed_modules = [
		netmanthan.db.escape(module.get("module_name")) for module in get_modules_from_all_apps_for_user()
	]
	module_condition = (
		"`tabDashboard`.`module` in ({allowed_modules}) or `tabDashboard`.`module` is NULL".format(
			allowed_modules=",".join(allowed_modules)
		)
	)

	return module_condition


@netmanthan.whitelist()
def get_permitted_charts(dashboard_name):
	permitted_charts = []
	dashboard = netmanthan.get_doc("Dashboard", dashboard_name)
	for chart in dashboard.charts:
		if netmanthan.has_permission("Dashboard Chart", doc=chart.chart):
			chart_dict = netmanthan._dict()
			chart_dict.update(chart.as_dict())

			if dashboard.get("chart_options"):
				chart_dict.custom_options = dashboard.get("chart_options")
			permitted_charts.append(chart_dict)

	return permitted_charts


@netmanthan.whitelist()
def get_permitted_cards(dashboard_name):
	permitted_cards = []
	dashboard = netmanthan.get_doc("Dashboard", dashboard_name)
	for card in dashboard.cards:
		if netmanthan.has_permission("Number Card", doc=card.card):
			permitted_cards.append(card)
	return permitted_cards


def get_non_standard_charts_in_dashboard(dashboard):
	non_standard_charts = [doc.name for doc in netmanthan.get_list("Dashboard Chart", {"is_standard": 0})]
	return [
		chart_link.chart for chart_link in dashboard.charts if chart_link.chart in non_standard_charts
	]


def get_non_standard_cards_in_dashboard(dashboard):
	non_standard_cards = [doc.name for doc in netmanthan.get_list("Number Card", {"is_standard": 0})]
	return [card_link.card for card_link in dashboard.cards if card_link.card in non_standard_cards]


def get_non_standard_warning_message(non_standard_docs_map):
	message = _("""Please set the following documents in this Dashboard as standard first.""")

	def get_html(docs, doctype):
		html = f"<p>{netmanthan.bold(doctype)}</p>"
		for doc in docs:
			html += '<div><a href="/app/Form/{doctype}/{doc}">{doc}</a></div>'.format(
				doctype=doctype, doc=doc
			)
		html += "<br>"
		return html

	html = message + "<br>"

	for doctype in non_standard_docs_map:
		if non_standard_docs_map[doctype]:
			html += get_html(non_standard_docs_map[doctype], doctype)

	return html
