import netmanthan


def execute():
	netmanthan.delete_doc_if_exists("DocType", "Post")
	netmanthan.delete_doc_if_exists("DocType", "Post Comment")
