# Copyright (c) 2015, netmanthan Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import netmanthan
import netmanthan.share
from netmanthan.automation.doctype.auto_repeat.test_auto_repeat import create_submittable_doctype
from netmanthan.tests.utils import netmanthanTestCase, change_settings

test_dependencies = ["User"]


class TestDocShare(netmanthanTestCase):
	def setUp(self):
		self.user = "test@example.com"
		self.event = netmanthan.get_doc(
			{
				"doctype": "Event",
				"subject": "test share event",
				"starts_on": "2015-01-01 10:00:00",
				"event_type": "Private",
			}
		).insert()

	def tearDown(self):
		netmanthan.set_user("Administrator")
		self.event.delete()

	def test_add(self):
		# user not shared
		self.assertTrue(self.event.name not in netmanthan.share.get_shared("Event", self.user))
		netmanthan.share.add("Event", self.event.name, self.user)
		self.assertTrue(self.event.name in netmanthan.share.get_shared("Event", self.user))

	def test_doc_permission(self):
		netmanthan.set_user(self.user)

		self.assertFalse(self.event.has_permission())

		netmanthan.set_user("Administrator")
		netmanthan.share.add("Event", self.event.name, self.user)

		netmanthan.set_user(self.user)
		# PERF: All share permission check should happen with maximum 1 query.
		with self.assertRowsRead(1):
			self.assertTrue(self.event.has_permission())

		second_event = netmanthan.get_doc(
			{
				"doctype": "Event",
				"subject": "test share event 2",
				"starts_on": "2015-01-01 10:00:00",
				"event_type": "Private",
			}
		).insert()
		netmanthan.share.add("Event", second_event.name, self.user)
		with self.assertRowsRead(1):
			self.assertTrue(self.event.has_permission())

	def test_share_permission(self):
		netmanthan.share.add("Event", self.event.name, self.user, write=1, share=1)

		netmanthan.set_user(self.user)
		self.assertTrue(self.event.has_permission("share"))

		# test cascade
		self.assertTrue(self.event.has_permission("read"))
		self.assertTrue(self.event.has_permission("write"))

	def test_set_permission(self):
		netmanthan.share.add("Event", self.event.name, self.user)

		netmanthan.set_user(self.user)
		self.assertFalse(self.event.has_permission("share"))

		netmanthan.set_user("Administrator")
		netmanthan.share.set_permission("Event", self.event.name, self.user, "share")

		netmanthan.set_user(self.user)
		self.assertTrue(self.event.has_permission("share"))

	def test_permission_to_share(self):
		netmanthan.set_user(self.user)
		self.assertRaises(netmanthan.PermissionError, netmanthan.share.add, "Event", self.event.name, self.user)

		netmanthan.set_user("Administrator")
		netmanthan.share.add("Event", self.event.name, self.user, write=1, share=1)

		# test not raises
		netmanthan.set_user(self.user)
		netmanthan.share.add("Event", self.event.name, "test1@example.com", write=1, share=1)

	def test_remove_share(self):
		netmanthan.share.add("Event", self.event.name, self.user, write=1, share=1)

		netmanthan.set_user(self.user)
		self.assertTrue(self.event.has_permission("share"))

		netmanthan.set_user("Administrator")
		netmanthan.share.remove("Event", self.event.name, self.user)

		netmanthan.set_user(self.user)
		self.assertFalse(self.event.has_permission("share"))

	def test_share_with_everyone(self):
		self.assertTrue(self.event.name not in netmanthan.share.get_shared("Event", self.user))

		netmanthan.share.set_permission("Event", self.event.name, None, "read", everyone=1)
		self.assertTrue(self.event.name in netmanthan.share.get_shared("Event", self.user))
		self.assertTrue(self.event.name in netmanthan.share.get_shared("Event", "test1@example.com"))
		self.assertTrue(self.event.name not in netmanthan.share.get_shared("Event", "Guest"))

		netmanthan.share.set_permission("Event", self.event.name, None, "read", value=0, everyone=1)
		self.assertTrue(self.event.name not in netmanthan.share.get_shared("Event", self.user))
		self.assertTrue(self.event.name not in netmanthan.share.get_shared("Event", "test1@example.com"))
		self.assertTrue(self.event.name not in netmanthan.share.get_shared("Event", "Guest"))

	def test_share_with_submit_perm(self):
		doctype = "Test DocShare with Submit"
		create_submittable_doctype(doctype, submit_perms=0)

		submittable_doc = netmanthan.get_doc(
			dict(doctype=doctype, test="test docshare with submit")
		).insert()

		netmanthan.set_user(self.user)
		self.assertFalse(netmanthan.has_permission(doctype, "submit", user=self.user))

		netmanthan.set_user("Administrator")
		netmanthan.share.add(doctype, submittable_doc.name, self.user, submit=1)

		netmanthan.set_user(self.user)
		self.assertTrue(
			netmanthan.has_permission(doctype, "submit", doc=submittable_doc.name, user=self.user)
		)

		# test cascade
		self.assertTrue(netmanthan.has_permission(doctype, "read", doc=submittable_doc.name, user=self.user))
		self.assertTrue(
			netmanthan.has_permission(doctype, "write", doc=submittable_doc.name, user=self.user)
		)

		netmanthan.share.remove(doctype, submittable_doc.name, self.user)

	def test_share_int_pk(self):
		test_doc = netmanthan.new_doc("Console Log")

		test_doc.insert()
		netmanthan.share.add("Console Log", test_doc.name, self.user)

		netmanthan.set_user(self.user)
		self.assertIn(
			str(test_doc.name), [str(name) for name in netmanthan.get_list("Console Log", pluck="name")]
		)

		test_doc.reload()
		self.assertTrue(test_doc.has_permission("read"))

	@change_settings("System Settings", {"disable_document_sharing": 1})
	def test_share_disabled_add(self):
		"Test if user loses share access on disabling share globally."
		netmanthan.share.add("Event", self.event.name, self.user, share=1)  # Share as admin
		netmanthan.set_user(self.user)

		# User does not have share access although given to them
		self.assertFalse(self.event.has_permission("share"))
		self.assertRaises(
			netmanthan.PermissionError, netmanthan.share.add, "Event", self.event.name, "test1@example.com"
		)

	@change_settings("System Settings", {"disable_document_sharing": 1})
	def test_share_disabled_add_with_ignore_permissions(self):
		netmanthan.share.add("Event", self.event.name, self.user, share=1)
		netmanthan.set_user(self.user)

		# User does not have share access although given to them
		self.assertFalse(self.event.has_permission("share"))

		# Test if behaviour is consistent for developer overrides
		netmanthan.share.add_docshare(
			"Event", self.event.name, "test1@example.com", flags={"ignore_share_permission": True}
		)

	@change_settings("System Settings", {"disable_document_sharing": 1})
	def test_share_disabled_set_permission(self):
		netmanthan.share.add("Event", self.event.name, self.user, share=1)
		netmanthan.set_user(self.user)

		# User does not have share access although given to them
		self.assertFalse(self.event.has_permission("share"))
		self.assertRaises(
			netmanthan.PermissionError,
			netmanthan.share.set_permission,
			"Event",
			self.event.name,
			"test1@example.com",
			"read",
		)

	@change_settings("System Settings", {"disable_document_sharing": 1})
	def test_share_disabled_assign_to(self):
		"""
		Assigning a document to a user without access must not share the document,
		if sharing disabled.
		"""
		from netmanthan.desk.form.assign_to import add

		netmanthan.share.add("Event", self.event.name, self.user, share=1)
		netmanthan.set_user(self.user)

		self.assertRaises(
			netmanthan.ValidationError,
			add,
			{"doctype": "Event", "name": self.event.name, "assign_to": ["test1@example.com"]},
		)
