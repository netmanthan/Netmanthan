# Copyright (c) 2022, netmanthan Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE
import netmanthan
from netmanthan.config import get_modules_from_all_apps_for_user
from netmanthan.tests.utils import netmanthanTestCase


class TestConfig(netmanthanTestCase):
	def test_get_modules(self):
		netmanthan_modules = netmanthan.get_all("Module Def", filters={"app_name": "netmanthan"}, pluck="name")
		all_modules_data = get_modules_from_all_apps_for_user()
		first_module_entry = all_modules_data[0]
		all_modules = [x["module_name"] for x in all_modules_data]
		self.assertIn("links", first_module_entry)
		self.assertIsInstance(all_modules_data, list)
		self.assertFalse([x for x in netmanthan_modules if x not in all_modules])
