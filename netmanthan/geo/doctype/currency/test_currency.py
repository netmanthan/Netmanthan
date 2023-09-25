# Copyright (c) 2015, netmanthan Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

# pre loaded

import netmanthan
from netmanthan.tests.utils import netmanthanTestCase


class TestUser(netmanthanTestCase):
	def test_default_currency_on_setup(self):
		usd = netmanthan.get_doc("Currency", "USD")
		self.assertDocumentEqual({"enabled": 1, "fraction": "Cent"}, usd)
