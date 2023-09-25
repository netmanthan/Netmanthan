# Copyright (c) 2022, netmanthan Technologies and contributors
# For license information, please see license.txt


from netmanthan.core.report.database_storage_usage_by_tables.database_storage_usage_by_tables import (
	execute,
)
from netmanthan.tests.utils import netmanthanTestCase


class TestDBUsageReport(netmanthanTestCase):
	def test_basic_query(self):
		_, data = execute()
		tables = [d.table for d in data]
		self.assertFalse({"tabUser", "tabDocField"}.difference(tables))
