# Copyright (c) 2019, netmanthan Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE
import json

import netmanthan
from netmanthan.desk.listview import get_group_by_count, get_list_settings, set_list_settings
from netmanthan.tests.utils import netmanthanTestCase


class TestListView(netmanthanTestCase):
	def setUp(self):
		if netmanthan.db.exists("List View Settings", "DocType"):
			netmanthan.delete_doc("List View Settings", "DocType")

	def test_get_list_settings_without_settings(self):
		self.assertIsNone(get_list_settings("DocType"), None)

	def test_get_list_settings_with_default_settings(self):
		netmanthan.get_doc({"doctype": "List View Settings", "name": "DocType"}).insert()
		settings = get_list_settings("DocType")
		self.assertIsNotNone(settings)

		self.assertEqual(settings.disable_auto_refresh, 0)
		self.assertEqual(settings.disable_count, 0)
		self.assertEqual(settings.disable_sidebar_stats, 0)

	def test_get_list_settings_with_non_default_settings(self):
		netmanthan.get_doc({"doctype": "List View Settings", "name": "DocType", "disable_count": 1}).insert()
		settings = get_list_settings("DocType")
		self.assertIsNotNone(settings)

		self.assertEqual(settings.disable_auto_refresh, 0)
		self.assertEqual(settings.disable_count, 1)
		self.assertEqual(settings.disable_sidebar_stats, 0)

	def test_set_list_settings_without_settings(self):
		set_list_settings("DocType", json.dumps({}))
		settings = netmanthan.get_doc("List View Settings", "DocType")

		self.assertEqual(settings.disable_auto_refresh, 0)
		self.assertEqual(settings.disable_count, 0)
		self.assertEqual(settings.disable_sidebar_stats, 0)

	def test_set_list_settings_with_existing_settings(self):
		netmanthan.get_doc({"doctype": "List View Settings", "name": "DocType", "disable_count": 1}).insert()
		set_list_settings("DocType", json.dumps({"disable_count": 0, "disable_auto_refresh": 1}))
		settings = netmanthan.get_doc("List View Settings", "DocType")

		self.assertEqual(settings.disable_auto_refresh, 1)
		self.assertEqual(settings.disable_count, 0)
		self.assertEqual(settings.disable_sidebar_stats, 0)

	def test_list_view_child_table_filter_with_created_by_filter(self):
		if netmanthan.db.exists("Note", "Test created by filter with child table filter"):
			netmanthan.delete_doc("Note", "Test created by filter with child table filter")

		doc = netmanthan.get_doc(
			{"doctype": "Note", "title": "Test created by filter with child table filter", "public": 1}
		)
		doc.append("seen_by", {"user": "Administrator"})
		doc.insert()

		data = {
			d.name: d.count
			for d in get_group_by_count("Note", '[["Note Seen By","user","=","Administrator"]]', "owner")
		}
		self.assertEqual(data["Administrator"], 1)

	def test_get_group_by_invalid_field(self):
		self.assertRaises(
			ValueError,
			get_group_by_count,
			"Note",
			'[["Note Seen By","user","=","Administrator"]]',
			"invalid_field",
		)
