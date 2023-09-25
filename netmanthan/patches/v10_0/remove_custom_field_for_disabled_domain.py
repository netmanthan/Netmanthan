import netmanthan


def execute():
	netmanthan.reload_doc("core", "doctype", "domain")
	netmanthan.reload_doc("core", "doctype", "has_domain")
	active_domains = netmanthan.get_active_domains()
	all_domains = netmanthan.get_all("Domain")

	for d in all_domains:
		if d.name not in active_domains:
			inactive_domain = netmanthan.get_doc("Domain", d.name)
			inactive_domain.setup_data()
			inactive_domain.remove_custom_field()
