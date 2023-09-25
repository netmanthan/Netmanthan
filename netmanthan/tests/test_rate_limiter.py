# Copyright (c) 2020, netmanthan Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import time

from werkzeug.wrappers import Response

import netmanthan
import netmanthan.rate_limiter
from netmanthan.rate_limiter import RateLimiter
from netmanthan.tests.utils import netmanthanTestCase
from netmanthan.utils import cint


class TestRateLimiter(netmanthanTestCase):
	def test_apply_with_limit(self):
		netmanthan.conf.rate_limit = {"window": 86400, "limit": 1}
		netmanthan.rate_limiter.apply()

		self.assertTrue(hasattr(netmanthan.local, "rate_limiter"))
		self.assertIsInstance(netmanthan.local.rate_limiter, RateLimiter)

		netmanthan.cache().delete(netmanthan.local.rate_limiter.key)
		delattr(netmanthan.local, "rate_limiter")

	def test_apply_without_limit(self):
		netmanthan.conf.rate_limit = None
		netmanthan.rate_limiter.apply()

		self.assertFalse(hasattr(netmanthan.local, "rate_limiter"))

	def test_respond_over_limit(self):
		limiter = RateLimiter(0.01, 86400)
		time.sleep(0.01)
		limiter.update()

		netmanthan.conf.rate_limit = {"window": 86400, "limit": 0.01}
		self.assertRaises(netmanthan.TooManyRequestsError, netmanthan.rate_limiter.apply)
		netmanthan.rate_limiter.update()

		response = netmanthan.rate_limiter.respond()

		self.assertIsInstance(response, Response)
		self.assertEqual(response.status_code, 429)

		headers = netmanthan.local.rate_limiter.headers()
		self.assertIn("Retry-After", headers)
		self.assertNotIn("X-RateLimit-Used", headers)
		self.assertIn("X-RateLimit-Reset", headers)
		self.assertIn("X-RateLimit-Limit", headers)
		self.assertIn("X-RateLimit-Remaining", headers)
		self.assertTrue(int(headers["X-RateLimit-Reset"]) <= 86400)
		self.assertEqual(int(headers["X-RateLimit-Limit"]), 10000)
		self.assertEqual(int(headers["X-RateLimit-Remaining"]), 0)

		netmanthan.cache().delete(limiter.key)
		netmanthan.cache().delete(netmanthan.local.rate_limiter.key)
		delattr(netmanthan.local, "rate_limiter")

	def test_respond_under_limit(self):
		netmanthan.conf.rate_limit = {"window": 86400, "limit": 0.01}
		netmanthan.rate_limiter.apply()
		netmanthan.rate_limiter.update()
		response = netmanthan.rate_limiter.respond()
		self.assertEqual(response, None)

		netmanthan.cache().delete(netmanthan.local.rate_limiter.key)
		delattr(netmanthan.local, "rate_limiter")

	def test_headers_under_limit(self):
		netmanthan.conf.rate_limit = {"window": 86400, "limit": 0.01}
		netmanthan.rate_limiter.apply()
		netmanthan.rate_limiter.update()
		headers = netmanthan.local.rate_limiter.headers()
		self.assertNotIn("Retry-After", headers)
		self.assertIn("X-RateLimit-Reset", headers)
		self.assertTrue(int(headers["X-RateLimit-Reset"] < 86400))
		self.assertEqual(int(headers["X-RateLimit-Used"]), netmanthan.local.rate_limiter.duration)
		self.assertEqual(int(headers["X-RateLimit-Limit"]), 10000)
		self.assertEqual(int(headers["X-RateLimit-Remaining"]), 10000)

		netmanthan.cache().delete(netmanthan.local.rate_limiter.key)
		delattr(netmanthan.local, "rate_limiter")

	def test_reject_over_limit(self):
		limiter = RateLimiter(0.01, 86400)
		time.sleep(0.01)
		limiter.update()

		limiter = RateLimiter(0.01, 86400)
		self.assertRaises(netmanthan.TooManyRequestsError, limiter.apply)

		netmanthan.cache().delete(limiter.key)

	def test_do_not_reject_under_limit(self):
		limiter = RateLimiter(0.01, 86400)
		time.sleep(0.01)
		limiter.update()

		limiter = RateLimiter(0.02, 86400)
		self.assertEqual(limiter.apply(), None)

		netmanthan.cache().delete(limiter.key)

	def test_update_method(self):
		limiter = RateLimiter(0.01, 86400)
		time.sleep(0.01)
		limiter.update()

		self.assertEqual(limiter.duration, cint(netmanthan.cache().get(limiter.key)))

		netmanthan.cache().delete(limiter.key)
