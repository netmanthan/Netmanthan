# Copyright (c) 2019, netmanthan Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import sqlparse

import netmanthan
import netmanthan.recorder
from netmanthan.recorder import normalize_query
from netmanthan.tests.utils import netmanthanTestCase
from netmanthan.utils import set_request
from netmanthan.website.serve import get_response_content


class TestRecorder(netmanthanTestCase):
	def setUp(self):
		netmanthan.recorder.stop()
		netmanthan.recorder.delete()
		set_request()
		netmanthan.recorder.start()
		netmanthan.recorder.record()

	def test_start(self):
		netmanthan.recorder.dump()
		requests = netmanthan.recorder.get()
		self.assertEqual(len(requests), 1)

	def test_do_not_record(self):
		netmanthan.recorder.do_not_record(netmanthan.get_all)("DocType")
		netmanthan.recorder.dump()
		requests = netmanthan.recorder.get()
		self.assertEqual(len(requests), 0)

	def test_get(self):
		netmanthan.recorder.dump()

		requests = netmanthan.recorder.get()
		self.assertEqual(len(requests), 1)

		request = netmanthan.recorder.get(requests[0]["uuid"])
		self.assertTrue(request)

	def test_delete(self):
		netmanthan.recorder.dump()

		requests = netmanthan.recorder.get()
		self.assertEqual(len(requests), 1)

		netmanthan.recorder.delete()

		requests = netmanthan.recorder.get()
		self.assertEqual(len(requests), 0)

	def test_record_without_sql_queries(self):
		netmanthan.recorder.dump()

		requests = netmanthan.recorder.get()
		request = netmanthan.recorder.get(requests[0]["uuid"])

		self.assertEqual(len(request["calls"]), 0)

	def test_record_with_sql_queries(self):
		netmanthan.get_all("DocType")
		netmanthan.recorder.dump()

		requests = netmanthan.recorder.get()
		request = netmanthan.recorder.get(requests[0]["uuid"])

		self.assertNotEqual(len(request["calls"]), 0)

	def test_explain(self):
		netmanthan.db.sql("SELECT * FROM tabDocType")
		netmanthan.db.sql("COMMIT")
		netmanthan.recorder.dump()
		netmanthan.recorder.post_process()

		requests = netmanthan.recorder.get()
		request = netmanthan.recorder.get(requests[0]["uuid"])

		self.assertEqual(len(request["calls"][0]["explain_result"]), 1)
		self.assertEqual(len(request["calls"][1]["explain_result"]), 0)

	def test_multiple_queries(self):
		queries = [
			{"mariadb": "SELECT * FROM tabDocType", "postgres": 'SELECT * FROM "tabDocType"'},
			{"mariadb": "SELECT COUNT(*) FROM tabDocType", "postgres": 'SELECT COUNT(*) FROM "tabDocType"'},
			{"mariadb": "COMMIT", "postgres": "COMMIT"},
		]

		sql_dialect = netmanthan.db.db_type or "mariadb"
		for query in queries:
			netmanthan.db.sql(query[sql_dialect])

		netmanthan.recorder.dump()
		netmanthan.recorder.post_process()

		requests = netmanthan.recorder.get()
		request = netmanthan.recorder.get(requests[0]["uuid"])

		self.assertEqual(len(request["calls"]), len(queries))

		for query, call in zip(queries, request["calls"]):
			self.assertEqual(
				call["query"], sqlparse.format(query[sql_dialect].strip(), keyword_case="upper", reindent=True)
			)

	def test_duplicate_queries(self):
		queries = [
			("SELECT * FROM tabDocType", 2),
			("SELECT COUNT(*) FROM tabDocType", 1),
			("select * from tabDocType", 2),
			("COMMIT", 3),
			("COMMIT", 3),
			("COMMIT", 3),
		]
		for query in queries:
			netmanthan.db.sql(query[0])

		netmanthan.recorder.dump()
		netmanthan.recorder.post_process()

		requests = netmanthan.recorder.get()
		request = netmanthan.recorder.get(requests[0]["uuid"])

		for query, call in zip(queries, request["calls"]):
			self.assertEqual(call["exact_copies"], query[1])

	def test_error_page_rendering(self):
		content = get_response_content("error")
		self.assertIn("Error", content)


class TestRecorderDeco(netmanthanTestCase):
	def test_recorder_flag(self):
		netmanthan.recorder.delete()

		@netmanthan.recorder.record_queries
		def test():
			netmanthan.get_all("User")

		test()
		self.assertTrue(netmanthan.recorder.get())


class TestQueryNormalization(netmanthanTestCase):
	def test_query_normalization(self):
		test_cases = {
			"select * from user where name = 'x'": "select * from user where name = ?",
			"select * from user where a > 5": "select * from user where a > ?",
			"select * from `user` where a > 5": "select * from `user` where a > ?",
			"select `name` from `user`": "select `name` from `user`",
			"select `name` from `user` limit 10": "select `name` from `user` limit ?",
		}

		for query, normalized in test_cases.items():
			self.assertEqual(normalize_query(query), normalized)
