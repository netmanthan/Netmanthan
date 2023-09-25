# Copyright (c) 2015, netmanthan Technologies Pvt. Ltd. and Contributors

from unittest.mock import patch

import netmanthan
from netmanthan.tests.utils import netmanthanTestCase


class TestClient(netmanthanTestCase):
	def test_set_value(self):
		todo = netmanthan.get_doc(dict(doctype="ToDo", description="test")).insert()
		netmanthan.set_value("ToDo", todo.name, "description", "test 1")
		self.assertEqual(netmanthan.get_value("ToDo", todo.name, "description"), "test 1")

		netmanthan.set_value("ToDo", todo.name, {"description": "test 2"})
		self.assertEqual(netmanthan.get_value("ToDo", todo.name, "description"), "test 2")

	def test_delete(self):
		from netmanthan.client import delete
		from netmanthan.desk.doctype.note.note import Note

		note = netmanthan.get_doc(
			doctype="Note",
			title=netmanthan.generate_hash(length=8),
			content="test",
			seen_by=[{"user": "Administrator"}],
		).insert()

		child_row_name = note.seen_by[0].name

		with patch.object(Note, "save") as save:
			delete("Note Seen By", child_row_name)
			save.assert_called()

		delete("Note", note.name)

		self.assertFalse(netmanthan.db.exists("Note", note.name))
		self.assertRaises(netmanthan.DoesNotExistError, delete, "Note", note.name)
		self.assertRaises(netmanthan.DoesNotExistError, delete, "Note Seen By", child_row_name)

	def test_http_valid_method_access(self):
		from netmanthan.client import delete
		from netmanthan.handler import execute_cmd

		netmanthan.set_user("Administrator")

		netmanthan.local.request = netmanthan._dict()
		netmanthan.local.request.method = "POST"

		netmanthan.local.form_dict = netmanthan._dict(
			{"doc": dict(doctype="ToDo", description="Valid http method"), "cmd": "netmanthan.client.save"}
		)
		todo = execute_cmd("netmanthan.client.save")

		self.assertEqual(todo.get("description"), "Valid http method")

		delete("ToDo", todo.name)

	def test_http_invalid_method_access(self):
		from netmanthan.handler import execute_cmd

		netmanthan.set_user("Administrator")

		netmanthan.local.request = netmanthan._dict()
		netmanthan.local.request.method = "GET"

		netmanthan.local.form_dict = netmanthan._dict(
			{"doc": dict(doctype="ToDo", description="Invalid http method"), "cmd": "netmanthan.client.save"}
		)

		self.assertRaises(netmanthan.PermissionError, execute_cmd, "netmanthan.client.save")

	def test_run_doc_method(self):
		from netmanthan.handler import execute_cmd

		if not netmanthan.db.exists("Report", "Test Run Doc Method"):
			report = netmanthan.get_doc(
				{
					"doctype": "Report",
					"ref_doctype": "User",
					"report_name": "Test Run Doc Method",
					"report_type": "Query Report",
					"is_standard": "No",
					"roles": [{"role": "System Manager"}],
				}
			).insert()
		else:
			report = netmanthan.get_doc("Report", "Test Run Doc Method")

		netmanthan.local.request = netmanthan._dict()
		netmanthan.local.request.method = "GET"

		# Whitelisted, works as expected
		netmanthan.local.form_dict = netmanthan._dict(
			{
				"dt": report.doctype,
				"dn": report.name,
				"method": "toggle_disable",
				"cmd": "run_doc_method",
				"args": 0,
			}
		)

		execute_cmd(netmanthan.local.form_dict.cmd)

		# Not whitelisted, throws permission error
		netmanthan.local.form_dict = netmanthan._dict(
			{
				"dt": report.doctype,
				"dn": report.name,
				"method": "create_report_py",
				"cmd": "run_doc_method",
				"args": 0,
			}
		)

		self.assertRaises(netmanthan.PermissionError, execute_cmd, netmanthan.local.form_dict.cmd)

	def test_array_values_in_request_args(self):
		import requests

		from netmanthan.auth import CookieManager, LoginManager

		netmanthan.utils.set_request(path="/")
		netmanthan.local.cookie_manager = CookieManager()
		netmanthan.local.login_manager = LoginManager()
		netmanthan.local.login_manager.login_as("Administrator")
		params = {
			"doctype": "DocType",
			"fields": ["name", "modified"],
			"sid": netmanthan.session.sid,
		}
		headers = {
			"accept": "application/json",
			"content-type": "application/json",
		}
		url = (
			f"http://{netmanthan.local.site}:{netmanthan.conf.webserver_port}/api/method/netmanthan.client.get_list"
		)
		res = requests.post(url, json=params, headers=headers)
		self.assertEqual(res.status_code, 200)
		data = res.json()
		first_item = data["message"][0]
		self.assertTrue("name" in first_item)
		self.assertTrue("modified" in first_item)
		netmanthan.local.login_manager.logout()

	def test_client_get(self):
		from netmanthan.client import get

		todo = netmanthan.get_doc(doctype="ToDo", description="test").insert()
		filters = {"name": todo.name}
		filters_json = netmanthan.as_json(filters)

		self.assertEqual(get("ToDo", filters=filters).description, "test")
		self.assertEqual(get("ToDo", filters=filters_json).description, "test")
		self.assertEqual(get("System Settings", "", "").doctype, "System Settings")
		self.assertEqual(get("ToDo", filters={}), get("ToDo", filters="{}"))
		todo.delete()

	def test_client_insert(self):
		from netmanthan.client import insert

		def get_random_title():
			return f"test-{netmanthan.generate_hash()}"

		# test insert dict
		doc = {"doctype": "Note", "title": get_random_title(), "content": "test"}
		note1 = insert(doc)
		self.assertTrue(note1)

		# test insert json
		doc["title"] = get_random_title()
		json_doc = netmanthan.as_json(doc)
		note2 = insert(json_doc)
		self.assertTrue(note2)

		# test insert child doc without parent fields
		child_doc = {"doctype": "Note Seen By", "user": "Administrator"}
		with self.assertRaises(netmanthan.ValidationError):
			insert(child_doc)

		# test insert child doc with parent fields
		child_doc = {
			"doctype": "Note Seen By",
			"user": "Administrator",
			"parenttype": "Note",
			"parent": note1.name,
			"parentfield": "seen_by",
		}
		note3 = insert(child_doc)
		self.assertTrue(note3)

		# cleanup
		netmanthan.delete_doc("Note", note1.name)
		netmanthan.delete_doc("Note", note2.name)

	def test_client_insert_many(self):
		from netmanthan.client import insert, insert_many

		def get_random_title():
			return f"test-{netmanthan.generate_hash(length=5)}"

		# insert a (parent) doc
		note1 = {"doctype": "Note", "title": get_random_title(), "content": "test"}
		note1 = insert(note1)

		doc_list = [
			{
				"doctype": "Note Seen By",
				"user": "Administrator",
				"parenttype": "Note",
				"parent": note1.name,
				"parentfield": "seen_by",
			},
			{
				"doctype": "Note Seen By",
				"user": "Administrator",
				"parenttype": "Note",
				"parent": note1.name,
				"parentfield": "seen_by",
			},
			{
				"doctype": "Note Seen By",
				"user": "Administrator",
				"parenttype": "Note",
				"parent": note1.name,
				"parentfield": "seen_by",
			},
			{"doctype": "Note", "title": "not-a-random-title", "content": "test"},
			{"doctype": "Note", "title": get_random_title(), "content": "test"},
			{"doctype": "Note", "title": get_random_title(), "content": "test"},
			{"doctype": "Note", "title": "another-note-title", "content": "test"},
		]

		# insert all docs
		docs = insert_many(doc_list)

		self.assertEqual(len(docs), 7)
		self.assertEqual(docs[3], "not-a-random-title")
		self.assertEqual(docs[6], "another-note-title")
		self.assertIn(note1.name, docs)

		# cleanup
		for doc in docs:
			netmanthan.delete_doc("Note", doc)
