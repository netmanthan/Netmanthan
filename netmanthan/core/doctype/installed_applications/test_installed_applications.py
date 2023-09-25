# Copyright (c) 2020, netmanthan Technologies and Contributors
# License: MIT. See LICENSE

import netmanthan
from netmanthan.core.doctype.installed_applications.installed_applications import (
	InvalidAppOrder,
	update_installed_apps_order,
)
from netmanthan.tests.utils import netmanthanTestCase


class TestInstalledApplications(netmanthanTestCase):
	def test_order_change(self):
		update_installed_apps_order(["netmanthan"])
		self.assertRaises(InvalidAppOrder, update_installed_apps_order, [])
		self.assertRaises(InvalidAppOrder, update_installed_apps_order, ["netmanthan", "deepmind"])
