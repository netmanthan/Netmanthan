# Copyright (c) 2015, netmanthan Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import netmanthan
from netmanthan.desk.form.linked_with import get_linked_docs, get_linked_doctypes
from netmanthan.tests.utils import netmanthanTestCase


class TestForm(netmanthanTestCase):
	def test_linked_with(self):
		results = get_linked_docs("Role", "System Manager", linkinfo=get_linked_doctypes("Role"))
		self.assertTrue("User" in results)
		self.assertTrue("DocType" in results)


if __name__ == "__main__":
	import unittest

	netmanthan.connect()
	unittest.main()
