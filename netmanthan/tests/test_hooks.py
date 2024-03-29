# Copyright (c) 2015, netmanthan Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import netmanthan
from netmanthan.cache_manager import clear_controller_cache
from netmanthan.desk.doctype.todo.todo import ToDo
from netmanthan.tests.utils import netmanthanTestCase


class TestHooks(netmanthanTestCase):
	def test_hooks(self):
		hooks = netmanthan.get_hooks()
		self.assertTrue(isinstance(hooks.get("app_name"), list))
		self.assertTrue(isinstance(hooks.get("doc_events"), dict))
		self.assertTrue(isinstance(hooks.get("doc_events").get("*"), dict))
		self.assertTrue(isinstance(hooks.get("doc_events").get("*"), dict))
		self.assertTrue(
			"netmanthan.desk.notifications.clear_doctype_notifications"
			in hooks.get("doc_events").get("*").get("on_update")
		)

	def test_override_doctype_class(self):
		from netmanthan import hooks

		# Set hook
		hooks.override_doctype_class = {"ToDo": ["netmanthan.tests.test_hooks.CustomToDo"]}

		# Clear cache
		netmanthan.cache().delete_value("app_hooks")
		clear_controller_cache("ToDo")

		todo = netmanthan.get_doc(doctype="ToDo", description="asdf")
		self.assertTrue(isinstance(todo, CustomToDo))

	def test_has_permission(self):
		from netmanthan import hooks

		# Set hook
		address_has_permission_hook = hooks.has_permission.get("Address", [])
		if isinstance(address_has_permission_hook, str):
			address_has_permission_hook = [address_has_permission_hook]

		address_has_permission_hook.append("netmanthan.tests.test_hooks.custom_has_permission")

		hooks.has_permission["Address"] = address_has_permission_hook

		# Clear cache
		netmanthan.cache().delete_value("app_hooks")

		# Init User and Address
		username = "test@example.com"
		user = netmanthan.get_doc("User", username)
		user.add_roles("System Manager")
		address = netmanthan.new_doc("Address")

		# Test!
		self.assertTrue(netmanthan.has_permission("Address", doc=address, user=username))

		address.flags.dont_touch_me = True
		self.assertFalse(netmanthan.has_permission("Address", doc=address, user=username))

	def test_ignore_links_on_delete(self):
		email_unsubscribe = netmanthan.get_doc(
			{"doctype": "Email Unsubscribe", "email": "test@example.com", "global_unsubscribe": 1}
		).insert()

		event = netmanthan.get_doc(
			{
				"doctype": "Event",
				"subject": "Test Event",
				"starts_on": "2022-12-21",
				"event_type": "Public",
				"event_participants": [
					{
						"reference_doctype": "Email Unsubscribe",
						"reference_docname": email_unsubscribe.name,
					}
				],
			}
		).insert()
		self.assertRaises(netmanthan.LinkExistsError, email_unsubscribe.delete)

		event.event_participants = []
		event.save()

		todo = netmanthan.get_doc(
			{
				"doctype": "ToDo",
				"description": "Test ToDo",
				"reference_type": "Event",
				"reference_name": event.name,
			}
		)
		todo.insert()

		event.delete()


def custom_has_permission(doc, ptype, user):
	if doc.flags.dont_touch_me:
		return False


class CustomToDo(ToDo):
	pass
