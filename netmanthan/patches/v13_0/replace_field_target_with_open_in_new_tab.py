import netmanthan


def execute():
	doctype = "Top Bar Item"
	if not netmanthan.db.table_exists(doctype) or not netmanthan.db.has_column(doctype, "target"):
		return

	netmanthan.reload_doc("website", "doctype", "top_bar_item")
	netmanthan.db.set_value(doctype, {"target": 'target = "_blank"'}, "open_in_new_tab", 1)
