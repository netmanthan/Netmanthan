import re

import netmanthan
from netmanthan.core.doctype.user.user import create_contact


def execute():
	"""Create Contact for each User if not present"""
	netmanthan.reload_doc("integrations", "doctype", "google_contacts")
	netmanthan.reload_doc("contacts", "doctype", "contact")
	netmanthan.reload_doc("core", "doctype", "dynamic_link")

	contact_meta = netmanthan.get_meta("Contact")
	if contact_meta.has_field("phone_nos") and contact_meta.has_field("email_ids"):
		netmanthan.reload_doc("contacts", "doctype", "contact_phone")
		netmanthan.reload_doc("contacts", "doctype", "contact_email")

	users = netmanthan.get_all("User", filters={"name": ("not in", "Administrator, Guest")}, fields=["*"])
	for user in users:
		if netmanthan.db.exists("Contact", {"email_id": user.email}) or netmanthan.db.exists(
			"Contact Email", {"email_id": user.email}
		):
			continue
		if user.first_name:
			user.first_name = re.sub("[<>]+", "", netmanthan.safe_decode(user.first_name))
		if user.last_name:
			user.last_name = re.sub("[<>]+", "", netmanthan.safe_decode(user.last_name))
		create_contact(user, ignore_links=True, ignore_mandatory=True)
