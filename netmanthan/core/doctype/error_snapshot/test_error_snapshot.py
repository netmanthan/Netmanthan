# Copyright (c) 2015, netmanthan Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE
from netmanthan.tests.utils import netmanthanTestCase
from netmanthan.utils.logger import sanitized_dict

# test_records = netmanthan.get_test_records('Error Snapshot')


class TestErrorSnapshot(netmanthanTestCase):
	def test_form_dict_sanitization(self):
		self.assertNotEqual(sanitized_dict({"pwd": "SECRET", "usr": "WHAT"}).get("pwd"), "SECRET")
