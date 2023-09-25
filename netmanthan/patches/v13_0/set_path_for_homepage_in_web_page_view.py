import netmanthan


def execute():
	netmanthan.reload_doc("website", "doctype", "web_page_view", force=True)
	netmanthan.db.sql("""UPDATE `tabWeb Page View` set path='/' where path=''""")
