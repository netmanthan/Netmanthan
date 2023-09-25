# Copyright (c) 2021, netmanthan Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE
import time
from unittest.mock import patch

import requests

import netmanthan
from netmanthan.auth import LoginAttemptTracker
from netmanthan.netmanthanclient import AuthError, netmanthanClient
from netmanthan.sessions import Session, get_expired_sessions, get_expiry_in_seconds
from netmanthan.tests.test_api import netmanthanAPITestCase
from netmanthan.tests.utils import netmanthanTestCase
from netmanthan.utils import get_site_url, now
from netmanthan.utils.data import add_to_date
from netmanthan.www.login import _generate_temporary_login_link


def add_user(email, password, username=None, mobile_no=None):
	first_name = email.split("@", 1)[0]
	user = netmanthan.get_doc(
		dict(doctype="User", email=email, first_name=first_name, username=username, mobile_no=mobile_no)
	).insert()
	user.new_password = password
	user.add_roles("System Manager")
	netmanthan.db.commit()


class TestAuth(netmanthanTestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		cls.HOST_NAME = netmanthan.get_site_config().host_name or get_site_url(netmanthan.local.site)
		cls.test_user_email = "test_auth@test.com"
		cls.test_user_name = "test_auth_user"
		cls.test_user_mobile = "+911234567890"
		cls.test_user_password = "pwd_012"

		cls.tearDownClass()
		add_user(
			email=cls.test_user_email,
			password=cls.test_user_password,
			username=cls.test_user_name,
			mobile_no=cls.test_user_mobile,
		)

	@classmethod
	def tearDownClass(cls):
		netmanthan.delete_doc("User", cls.test_user_email, force=True)
		netmanthan.local.request_ip = None
		netmanthan.form_dict.email = None
		netmanthan.local.response["http_status_code"] = None

	def set_system_settings(self, k, v):
		netmanthan.db.set_value("System Settings", "System Settings", k, v)
		netmanthan.clear_cache()
		netmanthan.db.commit()

	def test_allow_login_using_mobile(self):
		self.set_system_settings("allow_login_using_mobile_number", 1)
		self.set_system_settings("allow_login_using_user_name", 0)

		# Login by both email and mobile should work
		netmanthanClient(self.HOST_NAME, self.test_user_mobile, self.test_user_password)
		netmanthanClient(self.HOST_NAME, self.test_user_email, self.test_user_password)

		# login by username should fail
		with self.assertRaises(AuthError):
			netmanthanClient(self.HOST_NAME, self.test_user_name, self.test_user_password)

	def test_allow_login_using_only_email(self):
		self.set_system_settings("allow_login_using_mobile_number", 0)
		self.set_system_settings("allow_login_using_user_name", 0)

		# Login by mobile number should fail
		with self.assertRaises(AuthError):
			netmanthanClient(self.HOST_NAME, self.test_user_mobile, self.test_user_password)

		# login by username should fail
		with self.assertRaises(AuthError):
			netmanthanClient(self.HOST_NAME, self.test_user_name, self.test_user_password)

		# Login by email should work
		netmanthanClient(self.HOST_NAME, self.test_user_email, self.test_user_password)

	def test_allow_login_using_username(self):
		self.set_system_settings("allow_login_using_mobile_number", 0)
		self.set_system_settings("allow_login_using_user_name", 1)

		# Mobile login should fail
		with self.assertRaises(AuthError):
			netmanthanClient(self.HOST_NAME, self.test_user_mobile, self.test_user_password)

		# Both email and username logins should work
		netmanthanClient(self.HOST_NAME, self.test_user_email, self.test_user_password)
		netmanthanClient(self.HOST_NAME, self.test_user_name, self.test_user_password)

	def test_allow_login_using_username_and_mobile(self):
		self.set_system_settings("allow_login_using_mobile_number", 1)
		self.set_system_settings("allow_login_using_user_name", 1)

		# Both email and username and mobile logins should work
		netmanthanClient(self.HOST_NAME, self.test_user_mobile, self.test_user_password)
		netmanthanClient(self.HOST_NAME, self.test_user_email, self.test_user_password)
		netmanthanClient(self.HOST_NAME, self.test_user_name, self.test_user_password)

	def test_deny_multiple_login(self):
		self.set_system_settings("deny_multiple_sessions", 1)
		self.addCleanup(self.set_system_settings, "deny_multiple_sessions", 0)

		first_login = netmanthanClient(self.HOST_NAME, self.test_user_email, self.test_user_password)
		first_login.get_list("ToDo")

		second_login = netmanthanClient(self.HOST_NAME, self.test_user_email, self.test_user_password)
		second_login.get_list("ToDo")
		with self.assertRaises(Exception):
			first_login.get_list("ToDo")

		third_login = netmanthanClient(self.HOST_NAME, self.test_user_email, self.test_user_password)
		with self.assertRaises(Exception):
			first_login.get_list("ToDo")
		with self.assertRaises(Exception):
			second_login.get_list("ToDo")
		third_login.get_list("ToDo")

	def test_disable_user_pass_login(self):
		netmanthanClient(self.HOST_NAME, self.test_user_email, self.test_user_password).get_list("ToDo")
		self.set_system_settings("disable_user_pass_login", 1)
		self.addCleanup(self.set_system_settings, "disable_user_pass_login", 0)

		with self.assertRaises(Exception):
			netmanthanClient(self.HOST_NAME, self.test_user_email, self.test_user_password).get_list("ToDo")

	def test_login_with_email_link(self):

		user = self.test_user_email

		# Logs in
		res = requests.get(_generate_temporary_login_link(user, 10))
		self.assertEqual(res.status_code, 200)
		self.assertTrue(res.cookies.get("sid"))
		self.assertNotEqual(res.cookies.get("sid"), "Guest")

		# Random incorrect URL
		res = requests.get(_generate_temporary_login_link(user, 10) + "aa")
		self.assertEqual(res.cookies.get("sid"), "Guest")

		# POST doesn't work
		res = requests.post(_generate_temporary_login_link(user, 10))
		self.assertEqual(res.status_code, 403)

		# Rate limiting
		for _ in range(6):
			res = requests.get(_generate_temporary_login_link(user, 10))
			if res.status_code == 417:
				break
		else:
			self.fail("Rate limting not working")


class TestLoginAttemptTracker(netmanthanTestCase):
	def test_account_lock(self):
		"""Make sure that account locks after `n consecutive failures"""
		tracker = LoginAttemptTracker(
			user_name="tester", max_consecutive_login_attempts=3, lock_interval=60
		)
		# Clear the cache by setting attempt as success
		tracker.add_success_attempt()

		tracker.add_failure_attempt()
		self.assertTrue(tracker.is_user_allowed())

		tracker.add_failure_attempt()
		self.assertTrue(tracker.is_user_allowed())

		tracker.add_failure_attempt()
		self.assertTrue(tracker.is_user_allowed())

		tracker.add_failure_attempt()
		self.assertFalse(tracker.is_user_allowed())

	def test_account_unlock(self):
		"""Make sure that locked account gets unlocked after lock_interval of time."""
		lock_interval = 2  # In sec
		tracker = LoginAttemptTracker(
			user_name="tester", max_consecutive_login_attempts=1, lock_interval=lock_interval
		)
		# Clear the cache by setting attempt as success
		tracker.add_success_attempt()

		tracker.add_failure_attempt()
		self.assertTrue(tracker.is_user_allowed())

		tracker.add_failure_attempt()
		self.assertFalse(tracker.is_user_allowed())

		# Sleep for lock_interval of time, so that next request con unlock the user access.
		time.sleep(lock_interval)

		tracker.add_failure_attempt()
		self.assertTrue(tracker.is_user_allowed())


class TestSessionExpirty(netmanthanAPITestCase):
	def test_session_expires(self):
		sid = self.sid  # triggers login for test case login
		s: Session = netmanthan.local.session_obj

		expiry_in = get_expiry_in_seconds()
		session_created = now()

		# Try with 1% increments of times, it should always work
		for step in range(0, 100, 1):
			seconds_elapsed = expiry_in * step / 100

			time_now = add_to_date(session_created, seconds=seconds_elapsed, as_string=True)
			with patch("netmanthan.utils.now", return_value=time_now):
				data = s.get_session_data_from_db()
				self.assertEqual(data.user, "Administrator")

		# 1% higher should immediately expire
		time_now = add_to_date(session_created, seconds=expiry_in * 1.01, as_string=True)
		with patch("netmanthan.utils.now", return_value=time_now):
			self.assertIn(sid, get_expired_sessions())
			self.assertFalse(s.get_session_data_from_db())
