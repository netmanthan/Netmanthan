# Copyright (c) 2015, netmanthan Technologies and Contributors
# License: MIT. See LICENSE
import time

import netmanthan
from netmanthan.auth import CookieManager, LoginManager
from netmanthan.tests.utils import netmanthanTestCase


class TestActivityLog(netmanthanTestCase):
	def test_activity_log(self):

		# test user login log
		netmanthan.local.form_dict = netmanthan._dict(
			{
				"cmd": "login",
				"sid": "Guest",
				"pwd": netmanthan.conf.admin_password or "admin",
				"usr": "Administrator",
			}
		)

		netmanthan.local.cookie_manager = CookieManager()
		netmanthan.local.login_manager = LoginManager()

		auth_log = self.get_auth_log()
		self.assertFalse(netmanthan.form_dict.pwd)
		self.assertEqual(auth_log.status, "Success")

		# test user logout log
		netmanthan.local.login_manager.logout()
		auth_log = self.get_auth_log(operation="Logout")
		self.assertEqual(auth_log.status, "Success")

		# test invalid login
		netmanthan.form_dict.update({"pwd": "password"})
		self.assertRaises(netmanthan.AuthenticationError, LoginManager)
		auth_log = self.get_auth_log()
		self.assertEqual(auth_log.status, "Failed")

		netmanthan.local.form_dict = netmanthan._dict()

	def get_auth_log(self, operation="Login"):
		names = netmanthan.get_all(
			"Activity Log",
			filters={
				"user": "Administrator",
				"operation": operation,
			},
			order_by="`creation` DESC",
		)

		name = names[0]
		auth_log = netmanthan.get_doc("Activity Log", name)
		return auth_log

	def test_brute_security(self):
		update_system_settings({"allow_consecutive_login_attempts": 3, "allow_login_after_fail": 5})

		netmanthan.local.form_dict = netmanthan._dict(
			{"cmd": "login", "sid": "Guest", "pwd": "admin", "usr": "Administrator"}
		)

		netmanthan.local.cookie_manager = CookieManager()
		netmanthan.local.login_manager = LoginManager()

		auth_log = self.get_auth_log()
		self.assertEqual(auth_log.status, "Success")

		# test user logout log
		netmanthan.local.login_manager.logout()
		auth_log = self.get_auth_log(operation="Logout")
		self.assertEqual(auth_log.status, "Success")

		# test invalid login
		netmanthan.form_dict.update({"pwd": "password"})
		self.assertRaises(netmanthan.AuthenticationError, LoginManager)
		self.assertRaises(netmanthan.AuthenticationError, LoginManager)
		self.assertRaises(netmanthan.AuthenticationError, LoginManager)

		# REMOVE ME: current logic allows allow_consecutive_login_attempts+1 attempts
		# before raising security exception, remove below line when that is fixed.
		self.assertRaises(netmanthan.AuthenticationError, LoginManager)
		self.assertRaises(netmanthan.SecurityException, LoginManager)
		time.sleep(5)
		self.assertRaises(netmanthan.AuthenticationError, LoginManager)

		netmanthan.local.form_dict = netmanthan._dict()


def update_system_settings(args):
	doc = netmanthan.get_doc("System Settings")
	doc.update(args)
	doc.flags.ignore_mandatory = 1
	doc.save()
