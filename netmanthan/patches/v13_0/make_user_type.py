import netmanthan
from netmanthan.utils.install import create_user_type


def execute():
	netmanthan.reload_doc("core", "doctype", "role")
	netmanthan.reload_doc("core", "doctype", "user_document_type")
	netmanthan.reload_doc("core", "doctype", "user_type_module")
	netmanthan.reload_doc("core", "doctype", "user_select_document_type")
	netmanthan.reload_doc("core", "doctype", "user_type")

	create_user_type()
