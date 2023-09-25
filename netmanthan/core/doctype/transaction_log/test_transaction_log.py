# Copyright (c) 2018, netmanthan Technologies and Contributors
# License: MIT. See LICENSE
import hashlib

import netmanthan
from netmanthan.tests.utils import netmanthanTestCase

test_records = []


class TestTransactionLog(netmanthanTestCase):
	def test_validate_chaining(self):
		netmanthan.get_doc(
			{
				"doctype": "Transaction Log",
				"reference_doctype": "Test Doctype",
				"document_name": "Test Document 1",
				"data": "first_data",
			}
		).insert(ignore_permissions=True)

		second_log = netmanthan.get_doc(
			{
				"doctype": "Transaction Log",
				"reference_doctype": "Test Doctype",
				"document_name": "Test Document 2",
				"data": "second_data",
			}
		).insert(ignore_permissions=True)

		third_log = netmanthan.get_doc(
			{
				"doctype": "Transaction Log",
				"reference_doctype": "Test Doctype",
				"document_name": "Test Document 3",
				"data": "third_data",
			}
		).insert(ignore_permissions=True)

		sha = hashlib.sha256()
		sha.update(
            netmanthan.safe_encode(str(third_log.transaction_hash))
            + netmanthan.safe_encode(str(second_log.chaining_hash))
		)

		self.assertEqual(sha.hexdigest(), third_log.chaining_hash)
