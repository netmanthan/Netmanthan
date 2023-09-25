# Copyright (c) 2018, netmanthan Technologies and Contributors
# License: MIT. See LICENSE

from contextlib import contextmanager

import netmanthan
import netmanthan.utils
import netmanthan.utils.scheduler
from netmanthan.desk.form import assign_to
from netmanthan.tests.utils import netmanthanTestCase

test_dependencies = ["User", "Notification"]


@contextmanager
def get_test_notification(config):
	try:
		notification = netmanthan.get_doc(doctype="Notification", **config).insert()
		yield notification
	finally:
		notification.delete()


class TestNotification(netmanthanTestCase):
	def setUp(self):
		netmanthan.db.delete("Email Queue")
		netmanthan.set_user("test@example.com")

		if not netmanthan.db.exists("Notification", {"name": "ToDo Status Update"}, "name"):
			notification = netmanthan.new_doc("Notification")
			notification.name = "ToDo Status Update"
			notification.subject = "ToDo Status Update"
			notification.document_type = "ToDo"
			notification.event = "Value Change"
			notification.value_changed = "status"
			notification.send_to_all_assignees = 1
			notification.set_property_after_alert = "description"
			notification.property_value = "Changed by Notification"
			notification.save()

		if not netmanthan.db.exists("Notification", {"name": "Contact Status Update"}, "name"):
			notification = netmanthan.new_doc("Notification")
			notification.name = "Contact Status Update"
			notification.subject = "Contact Status Update"
			notification.document_type = "Contact"
			notification.event = "Value Change"
			notification.value_changed = "status"
			notification.message = "Test Contact Update"
			notification.append("recipients", {"receiver_by_document_field": "email_id,email_ids"})
			notification.save()

	def tearDown(self):
		netmanthan.set_user("Administrator")

	def test_new_and_save(self):
		"""Check creating a new communication triggers a notification."""
		communication = netmanthan.new_doc("Communication")
		communication.communication_type = "Comment"
		communication.subject = "test"
		communication.content = "test"
		communication.insert(ignore_permissions=True)

		self.assertTrue(
			netmanthan.db.get_value(
				"Email Queue",
				{
					"reference_doctype": "Communication",
					"reference_name": communication.name,
					"status": "Not Sent",
				},
			)
		)
		netmanthan.db.delete("Email Queue")

		communication.reload()
		communication.content = "test 2"
		communication.save()

		self.assertTrue(
			netmanthan.db.get_value(
				"Email Queue",
				{
					"reference_doctype": "Communication",
					"reference_name": communication.name,
					"status": "Not Sent",
				},
			)
		)

		self.assertEqual(
			netmanthan.db.get_value("Communication", communication.name, "subject"), "__testing__"
		)

	def test_condition(self):
		"""Check notification is triggered based on a condition."""
		event = netmanthan.new_doc("Event")
		event.subject = "test"
		event.event_type = "Private"
		event.starts_on = "2014-06-06 12:00:00"
		event.insert()

		self.assertFalse(
			netmanthan.db.get_value(
				"Email Queue",
				{"reference_doctype": "Event", "reference_name": event.name, "status": "Not Sent"},
			)
		)

		event.event_type = "Public"
		event.save()

		self.assertTrue(
			netmanthan.db.get_value(
				"Email Queue",
				{"reference_doctype": "Event", "reference_name": event.name, "status": "Not Sent"},
			)
		)

		# Make sure that we track the triggered notifications in communication doctype.
		self.assertTrue(
			netmanthan.db.get_value(
				"Communication",
				{
					"reference_doctype": "Event",
					"reference_name": event.name,
					"communication_type": "Automated Message",
				},
			)
		)

	def test_invalid_condition(self):
		netmanthan.set_user("Administrator")
		notification = netmanthan.new_doc("Notification")
		notification.subject = "test"
		notification.document_type = "ToDo"
		notification.send_alert_on = "New"
		notification.message = "test"

		recipent = netmanthan.new_doc("Notification Recipient")
		recipent.receiver_by_document_field = "owner"

		notification.recipents = recipent
		notification.condition = "test"

		self.assertRaises(netmanthan.ValidationError, notification.save)
		notification.delete()

	def test_value_changed(self):
		event = netmanthan.new_doc("Event")
		event.subject = "test"
		event.event_type = "Private"
		event.starts_on = "2014-06-06 12:00:00"
		event.insert()

		self.assertFalse(
			netmanthan.db.get_value(
				"Email Queue",
				{"reference_doctype": "Event", "reference_name": event.name, "status": "Not Sent"},
			)
		)

		event.subject = "test 1"
		event.save()

		self.assertFalse(
			netmanthan.db.get_value(
				"Email Queue",
				{"reference_doctype": "Event", "reference_name": event.name, "status": "Not Sent"},
			)
		)

		event.description = "test"
		event.save()

		self.assertTrue(
			netmanthan.db.get_value(
				"Email Queue",
				{"reference_doctype": "Event", "reference_name": event.name, "status": "Not Sent"},
			)
		)

	def test_alert_disabled_on_wrong_field(self):
		netmanthan.set_user("Administrator")
		notification = netmanthan.get_doc(
			{
				"doctype": "Notification",
				"subject": "_Test Notification for wrong field",
				"document_type": "Event",
				"event": "Value Change",
				"attach_print": 0,
				"value_changed": "description1",
				"message": "Description changed",
				"recipients": [{"receiver_by_document_field": "owner"}],
			}
		).insert()
		netmanthan.db.commit()

		event = netmanthan.new_doc("Event")
		event.subject = "test-2"
		event.event_type = "Private"
		event.starts_on = "2014-06-06 12:00:00"
		event.insert()
		event.subject = "test 1"
		event.save()

		# verify that notification is disabled
		notification.reload()
		self.assertEqual(notification.enabled, 0)
		notification.delete()
		event.delete()

	def test_date_changed(self):
		event = netmanthan.new_doc("Event")
		event.subject = "test"
		event.event_type = "Private"
		event.starts_on = "2014-01-01 12:00:00"
		event.insert()

		self.assertFalse(
			netmanthan.db.get_value(
				"Email Queue",
				{"reference_doctype": "Event", "reference_name": event.name, "status": "Not Sent"},
			)
		)

		netmanthan.set_user("Administrator")
		netmanthan.get_doc(
			"Scheduled Job Type",
			dict(method="netmanthan.email.doctype.notification.notification.trigger_daily_alerts"),
		).execute()

		# not today, so no alert
		self.assertFalse(
			netmanthan.db.get_value(
				"Email Queue",
				{"reference_doctype": "Event", "reference_name": event.name, "status": "Not Sent"},
			)
		)

		event.starts_on = netmanthan.utils.add_days(netmanthan.utils.nowdate(), 2) + " 12:00:00"
		event.save()

		# Value Change notification alert will be trigger as description is not changed
		# mail will not be sent
		self.assertFalse(
			netmanthan.db.get_value(
				"Email Queue",
				{"reference_doctype": "Event", "reference_name": event.name, "status": "Not Sent"},
			)
		)

		netmanthan.get_doc(
			"Scheduled Job Type",
			dict(method="netmanthan.email.doctype.notification.notification.trigger_daily_alerts"),
		).execute()

		# today so show alert
		self.assertTrue(
			netmanthan.db.get_value(
				"Email Queue",
				{"reference_doctype": "Event", "reference_name": event.name, "status": "Not Sent"},
			)
		)

	def test_cc_jinja(self):

		netmanthan.db.delete("User", {"email": "test_jinja@example.com"})
		netmanthan.db.delete("Email Queue")
		netmanthan.db.delete("Email Queue Recipient")

		test_user = netmanthan.new_doc("User")
		test_user.name = "test_jinja"
		test_user.first_name = "test_jinja"
		test_user.email = "test_jinja@example.com"

		test_user.insert(ignore_permissions=True)

		self.assertTrue(
			netmanthan.db.get_value(
				"Email Queue",
				{"reference_doctype": "User", "reference_name": test_user.name, "status": "Not Sent"},
			)
		)

		self.assertTrue(
			netmanthan.db.get_value("Email Queue Recipient", {"recipient": "test_jinja@example.com"})
		)

		netmanthan.db.delete("User", {"email": "test_jinja@example.com"})
		netmanthan.db.delete("Email Queue")
		netmanthan.db.delete("Email Queue Recipient")

	def test_notification_to_assignee(self):
		todo = netmanthan.new_doc("ToDo")
		todo.description = "Test Notification"
		todo.save()

		assign_to.add(
			{
				"assign_to": ["test2@example.com"],
				"doctype": todo.doctype,
				"name": todo.name,
				"description": "Close this Todo",
			}
		)

		assign_to.add(
			{
				"assign_to": ["test1@example.com"],
				"doctype": todo.doctype,
				"name": todo.name,
				"description": "Close this Todo",
			}
		)

		# change status of todo
		todo.status = "Closed"
		todo.save()

		email_queue = netmanthan.get_doc(
			"Email Queue", {"reference_doctype": "ToDo", "reference_name": todo.name}
		)

		self.assertTrue(email_queue)

		# check if description is changed after alert since set_property_after_alert is set
		self.assertEqual(todo.description, "Changed by Notification")

		recipients = [d.recipient for d in email_queue.recipients]
		self.assertTrue("test2@example.com" in recipients)
		self.assertTrue("test1@example.com" in recipients)

	def test_notification_by_child_table_field(self):
		contact = netmanthan.new_doc("Contact")
		contact.first_name = "John Doe"
		contact.status = "Open"
		contact.append("email_ids", {"email_id": "test2@example.com", "is_primary": 1})

		contact.append("email_ids", {"email_id": "test1@example.com"})

		contact.save()

		# change status of contact
		contact.status = "Replied"
		contact.save()

		email_queue = netmanthan.get_doc(
			"Email Queue", {"reference_doctype": "Contact", "reference_name": contact.name}
		)

		self.assertTrue(email_queue)

		recipients = [d.recipient for d in email_queue.recipients]
		self.assertTrue("test2@example.com" in recipients)
		self.assertTrue("test1@example.com" in recipients)

	def test_notification_value_change_casted_types(self):
		"""Make sure value change event dont fire because of incorrect type comparisons."""
		netmanthan.set_user("Administrator")

		notification = {
			"document_type": "User",
			"subject": "User changed birthdate",
			"event": "Value Change",
			"channel": "System Notification",
			"value_changed": "birth_date",
			"recipients": [{"receiver_by_document_field": "email"}],
		}

		with get_test_notification(notification) as n:
			netmanthan.db.delete("Notification Log", {"subject": n.subject})

			user = netmanthan.get_doc("User", "test@example.com")
			user.birth_date = netmanthan.utils.add_days(user.birth_date, 1)
			user.save()

			user.reload()
			user.birth_date = netmanthan.utils.getdate(user.birth_date)
			user.save()
			self.assertEqual(1, netmanthan.db.count("Notification Log", {"subject": n.subject}))

	@classmethod
	def tearDownClass(cls):
		netmanthan.delete_doc_if_exists("Notification", "ToDo Status Update")
		netmanthan.delete_doc_if_exists("Notification", "Contact Status Update")
