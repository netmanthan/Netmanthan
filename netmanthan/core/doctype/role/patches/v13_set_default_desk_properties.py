import netmanthan

from ..role import desk_properties


def execute():
	for role in netmanthan.get_all("Role", ["name", "desk_access"]):
		role_doc = netmanthan.get_doc("Role", role.name)
		for key in desk_properties:
			role_doc.set(key, role_doc.desk_access)
		role_doc.save()
