# Copyright (c) 2020, netmanthan Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE
from werkzeug.wrappers import Response

import netmanthan
from netmanthan.app import process_response
from netmanthan.tests.utils import netmanthanTestCase

HEADERS = (
	"Access-Control-Allow-Origin",
	"Access-Control-Allow-Credentials",
	"Access-Control-Allow-Methods",
	"Access-Control-Allow-Headers",
	"Vary",
)


class TestCORS(netmanthanTestCase):
	def make_request_and_test(self, origin="http://example.com", absent=False):
		self.origin = origin

		headers = {}
		if origin:
			headers = {
				"Origin": origin,
				"Access-Control-Request-Method": "POST",
				"Access-Control-Request-Headers": "X-Test-Header",
			}

		netmanthan.utils.set_request(method="OPTIONS", headers=headers)

		self.response = Response()
		process_response(self.response)

		for header in HEADERS:
			if absent:
				self.assertNotIn(header, self.response.headers)
			else:
				if header == "Access-Control-Allow-Origin":
					self.assertEqual(self.response.headers.get(header), self.origin)
				else:
					self.assertIn(header, self.response.headers)

	def test_cors_disabled(self):
		netmanthan.conf.allow_cors = None
		self.make_request_and_test("http://example.com", True)

	def test_request_without_origin(self):
		netmanthan.conf.allow_cors = "http://example.com"
		self.make_request_and_test(None, True)

	def test_valid_origin(self):
		netmanthan.conf.allow_cors = "http://example.com"
		self.make_request_and_test()

		netmanthan.conf.allow_cors = "*"
		self.make_request_and_test()

		netmanthan.conf.allow_cors = ["http://example.com", "https://example.com"]
		self.make_request_and_test()

	def test_invalid_origin(self):
		netmanthan.conf.allow_cors = "http://example1.com"
		self.make_request_and_test(absent=True)

		netmanthan.conf.allow_cors = ["http://example1.com", "https://example.com"]
		self.make_request_and_test(absent=True)
