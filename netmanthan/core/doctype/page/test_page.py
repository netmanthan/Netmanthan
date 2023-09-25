# Copyright (c) 2015, netmanthan Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE
import netmanthan
from netmanthan.tests.utils import netmanthanTestCase

test_records = netmanthan.get_test_records("Page")


class TestPage(netmanthanTestCase):
	def test_naming(self):
		self.assertRaises(
			netmanthan.NameError,
			netmanthan.get_doc(dict(doctype="Page", page_name="DocType", module="Core")).insert,
		)
		self.assertRaises(
			netmanthan.NameError,
			netmanthan.get_doc(dict(doctype="Page", page_name="Settings", module="Core")).insert,
		)
