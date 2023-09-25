# Copyright (c) 2015, netmanthan Technologies and Contributors
# License: MIT. See LICENSE

import netmanthan
from netmanthan.tests.utils import netmanthanTestCase


class TestEmailQueue(netmanthanTestCase):
	def test_email_queue_deletion_based_on_modified_date(self):
		from netmanthan.email.doctype.email_queue.email_queue import EmailQueue

		old_record = netmanthan.get_doc(
			{
				"doctype": "Email Queue",
				"sender": "Test <test@example.com>",
				"show_as_cc": "",
				"message": "Test message",
				"status": "Sent",
				"priority": 1,
				"recipients": [
					{
						"recipient": "test_auth@test.com",
					}
				],
			}
		).insert()

		old_record.modified = "2010-01-01 00:00:01"
		old_record.recipients[0].modified = old_record.modified
		old_record.db_update_all()

		new_record = netmanthan.copy_doc(old_record)
		new_record.insert()

		EmailQueue.clear_old_logs()

		self.assertFalse(netmanthan.db.exists("Email Queue", old_record.name))
		self.assertFalse(netmanthan.db.exists("Email Queue Recipient", {"parent": old_record.name}))

		self.assertTrue(netmanthan.db.exists("Email Queue", new_record.name))
		self.assertTrue(netmanthan.db.exists("Email Queue Recipient", {"parent": new_record.name}))
