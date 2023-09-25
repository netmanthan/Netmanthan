import netmanthan
from netmanthan.model.utils.rename_field import rename_field


def execute():
	if not netmanthan.db.table_exists("Dashboard Chart"):
		return

	netmanthan.reload_doc("desk", "doctype", "dashboard_chart")

	if netmanthan.db.has_column("Dashboard Chart", "is_custom"):
		rename_field("Dashboard Chart", "is_custom", "use_report_chart")
