import netmanthan
from netmanthan.desk.page.setup_wizard.install_fixtures import update_global_search_doctypes


def execute():
	netmanthan.reload_doc("desk", "doctype", "global_search_doctype")
	netmanthan.reload_doc("desk", "doctype", "global_search_settings")
	update_global_search_doctypes()
