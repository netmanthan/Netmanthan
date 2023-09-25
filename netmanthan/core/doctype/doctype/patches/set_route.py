import netmanthan
from netmanthan.desk.utils import slug


def execute():
	for doctype in netmanthan.get_all("DocType", ["name", "route"], dict(istable=0)):
		if not doctype.route:
			netmanthan.db.set_value("DocType", doctype.name, "route", slug(doctype.name), update_modified=False)
