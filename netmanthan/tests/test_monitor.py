# Copyright (c) 2020, netmanthan Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import netmanthan
import netmanthan.monitor
from netmanthan.monitor import MONITOR_REDIS_KEY
from netmanthan.tests.utils import netmanthanTestCase
from netmanthan.utils import set_request
from netmanthan.utils.response import build_response


class TestMonitor(netmanthanTestCase):
	def setUp(self):
		netmanthan.conf.monitor = 1
		netmanthan.cache().delete_value(MONITOR_REDIS_KEY)

	def test_enable_monitor(self):
		set_request(method="GET", path="/api/method/netmanthan.ping")
		response = build_response("json")

		netmanthan.monitor.start()
		netmanthan.monitor.stop(response)

		logs = netmanthan.cache().lrange(MONITOR_REDIS_KEY, 0, -1)
		self.assertEqual(len(logs), 1)

		log = netmanthan.parse_json(logs[0].decode())
		self.assertTrue(log.duration)
		self.assertTrue(log.site)
		self.assertTrue(log.timestamp)
		self.assertTrue(log.uuid)
		self.assertTrue(log.request)
		self.assertEqual(log.transaction_type, "request")
		self.assertEqual(log.request["method"], "GET")

	def test_no_response(self):
		set_request(method="GET", path="/api/method/netmanthan.ping")

		netmanthan.monitor.start()
		netmanthan.monitor.stop(response=None)

		logs = netmanthan.cache().lrange(MONITOR_REDIS_KEY, 0, -1)
		self.assertEqual(len(logs), 1)

		log = netmanthan.parse_json(logs[0].decode())
		self.assertEqual(log.request["status_code"], 500)
		self.assertEqual(log.transaction_type, "request")
		self.assertEqual(log.request["method"], "GET")

	def test_job(self):
		netmanthan.utils.background_jobs.execute_job(
			netmanthan.local.site, "netmanthan.ping", None, None, {}, is_async=False
		)

		logs = netmanthan.cache().lrange(MONITOR_REDIS_KEY, 0, -1)
		self.assertEqual(len(logs), 1)
		log = netmanthan.parse_json(logs[0].decode())
		self.assertEqual(log.transaction_type, "job")
		self.assertTrue(log.job)
		self.assertEqual(log.job["method"], "netmanthan.ping")
		self.assertEqual(log.job["scheduled"], False)
		self.assertEqual(log.job["wait"], 0)

	def test_flush(self):
		set_request(method="GET", path="/api/method/netmanthan.ping")
		response = build_response("json")
		netmanthan.monitor.start()
		netmanthan.monitor.stop(response)

		open(netmanthan.monitor.log_file(), "w").close()
		netmanthan.monitor.flush()

		with open(netmanthan.monitor.log_file()) as f:
			logs = f.readlines()

		self.assertEqual(len(logs), 1)
		log = netmanthan.parse_json(logs[0])
		self.assertEqual(log.transaction_type, "request")

	def tearDown(self):
		netmanthan.conf.monitor = 0
		netmanthan.cache().delete_value(MONITOR_REDIS_KEY)
