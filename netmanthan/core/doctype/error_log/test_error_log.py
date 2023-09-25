# Copyright (c) 2015, netmanthan Technologies and Contributors
# License: MIT. See LICENSE
from ldap3.core.exceptions import LDAPException, LDAPInappropriateAuthenticationResult

import netmanthan
from netmanthan.tests.utils import netmanthanTestCase
from netmanthan.utils.error import _is_ldap_exception

# test_records = netmanthan.get_test_records('Error Log')


class TestErrorLog(netmanthanTestCase):
	def test_error_log(self):
		"""let's do an error log on error log?"""
		doc = netmanthan.new_doc("Error Log")
		error = doc.log_error("This is an error")
		self.assertEqual(error.doctype, "Error Log")

	def test_ldap_exceptions(self):
		exc = [LDAPException, LDAPInappropriateAuthenticationResult]

		for e in exc:
			self.assertTrue(_is_ldap_exception(e()))
