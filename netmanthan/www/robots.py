import netmanthan

base_template_path = "www/robots.txt"


def get_context(context):
	robots_txt = (
            netmanthan.db.get_single_value("Website Settings", "robots_txt")
            or (netmanthan.local.conf.robots_txt and netmanthan.read_file(netmanthan.local.conf.robots_txt))
            or ""
	)

	return {"robots_txt": robots_txt}
