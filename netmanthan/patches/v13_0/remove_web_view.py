import netmanthan


def execute():
	netmanthan.delete_doc_if_exists("DocType", "Web View")
	netmanthan.delete_doc_if_exists("DocType", "Web View Component")
	netmanthan.delete_doc_if_exists("DocType", "CSS Class")
