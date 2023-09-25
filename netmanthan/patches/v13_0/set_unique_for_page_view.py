import netmanthan


def execute():
	netmanthan.reload_doc("website", "doctype", "web_page_view", force=True)
	site_url = netmanthan.utils.get_site_url(netmanthan.local.site)
	netmanthan.db.sql(f"""UPDATE `tabWeb Page View` set is_unique=1 where referrer LIKE '%{site_url}%'""")
