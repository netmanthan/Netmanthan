# Copyright (c) 2015, netmanthan Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE
import netmanthan
from netmanthan.tests.utils import netmanthanTestCase


class TestDocumentLocks(netmanthanTestCase):
	def test_locking(self):
		todo = netmanthan.get_doc(dict(doctype="ToDo", description="test")).insert()
		todo_1 = netmanthan.get_doc("ToDo", todo.name)

		todo.lock()
		self.assertRaises(netmanthan.DocumentLockedError, todo_1.lock)
		todo.unlock()

		todo_1.lock()
		self.assertRaises(netmanthan.DocumentLockedError, todo.lock)
		todo_1.unlock()
