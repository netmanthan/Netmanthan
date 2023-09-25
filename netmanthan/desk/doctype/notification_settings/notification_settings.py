# Copyright (c) 2019, netmanthan Technologies and contributors
# License: MIT. See LICENSE

import netmanthan
from netmanthan.model.document import Document


class NotificationSettings(Document):
	def on_update(self):
		from netmanthan.desk.notifications import clear_notification_config

		clear_notification_config(netmanthan.session.user)


def is_notifications_enabled(user):
	enabled = netmanthan.db.get_value("Notification Settings", user, "enabled")
	if enabled is None:
		return True
	return enabled


def is_email_notifications_enabled(user):
	enabled = netmanthan.db.get_value("Notification Settings", user, "enable_email_notifications")
	if enabled is None:
		return True
	return enabled


def is_email_notifications_enabled_for_type(user, notification_type):
	if not is_email_notifications_enabled(user):
		return False

	if notification_type == "Alert":
		return False

	fieldname = "enable_email_" + netmanthan.scrub(notification_type)
	enabled = netmanthan.db.get_value("Notification Settings", user, fieldname)
	if enabled is None:
		return True
	return enabled


def create_notification_settings(user):
	if not netmanthan.db.exists("Notification Settings", user):
		_doc = netmanthan.new_doc("Notification Settings")
		_doc.name = user
		_doc.insert(ignore_permissions=True)


def toggle_notifications(user: str, enable: bool = False):
	try:
		settings = netmanthan.get_doc("Notification Settings", user)
	except netmanthan.DoesNotExistError:
		netmanthan.clear_last_message()
		return

	if settings.enabled != enable:
		settings.enabled = enable
		settings.save()


@netmanthan.whitelist()
def get_subscribed_documents():
	if not netmanthan.session.user:
		return []

	try:
		if netmanthan.db.exists("Notification Settings", netmanthan.session.user):
			doc = netmanthan.get_doc("Notification Settings", netmanthan.session.user)
			return [item.document for item in doc.subscribed_documents]
	# Notification Settings is fetched even before sync doctype is called
	# but it will throw an ImportError, we can ignore it in migrate
	except ImportError:
		pass

	return []


def get_permission_query_conditions(user):
	if not user:
		user = netmanthan.session.user

	if user == "Administrator":
		return

	roles = netmanthan.get_roles(user)
	if "System Manager" in roles:
		return """(`tabNotification Settings`.name != 'Administrator')"""

	return f"""(`tabNotification Settings`.name = {netmanthan.db.escape(user)})"""


@netmanthan.whitelist()
def set_seen_value(value, user):
	netmanthan.db.set_value("Notification Settings", user, "seen", value, update_modified=False)
