# Copyright (c) 2022, netmanthan Technologies and contributors
# For license information, please see license.txt


from netmanthan.custom.report.audit_system_hooks.audit_system_hooks import execute
from netmanthan.tests.utils import netmanthanTestCase


class TestAuditSystemHooksReport(netmanthanTestCase):
	def test_basic_query(self):
		_, data = execute()
		for row in data:
			if row.get("hook_name") == "app_name":
				self.assertEqual(row.get("hook_values"), "netmanthan")
				break
		else:
			self.fail("Failed to generate hooks report")
