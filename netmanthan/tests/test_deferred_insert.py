import netmanthan
from netmanthan.deferred_insert import deferred_insert, save_to_db
from netmanthan.tests.utils import netmanthanTestCase


class TestDeferredInsert(netmanthanTestCase):
	def test_deferred_insert(self):
		route_history = {"route": netmanthan.generate_hash(), "user": "Administrator"}
		deferred_insert("Route History", [route_history])

		save_to_db()
		self.assertTrue(netmanthan.db.exists("Route History", route_history))
