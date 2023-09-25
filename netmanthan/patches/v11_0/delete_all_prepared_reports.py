import netmanthan


def execute():
	if netmanthan.db.table_exists("Prepared Report"):
		netmanthan.reload_doc("core", "doctype", "prepared_report")
		prepared_reports = netmanthan.get_all("Prepared Report")
		for report in prepared_reports:
			netmanthan.delete_doc("Prepared Report", report.name)
