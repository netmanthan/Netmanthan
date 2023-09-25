# Copyright (c) 2018, netmanthan Technologies and Contributors
# License: MIT. See LICENSE
import netmanthan
from netmanthan.tests.utils import netmanthanTestCase


class TestViewLog(netmanthanTestCase):
	def tearDown(self):
		netmanthan.set_user("Administrator")

	def test_if_user_is_added(self):
		ev = netmanthan.get_doc(
			{
				"doctype": "Event",
				"subject": "test event for view logs",
				"starts_on": "2018-06-04 14:11:00",
				"event_type": "Public",
			}
		).insert()

		netmanthan.set_user("test@example.com")

		from netmanthan.desk.form.load import getdoc

		# load the form
		getdoc("Event", ev.name)
		a = netmanthan.get_value(
			doctype="View Log",
			filters={"reference_doctype": "Event", "reference_name": ev.name},
			fieldname=["viewed_by"],
		)

		self.assertEqual("test@example.com", a)
		self.assertNotEqual("test1@example.com", a)
