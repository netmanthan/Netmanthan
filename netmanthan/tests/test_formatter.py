import netmanthan
from netmanthan import format
from netmanthan.tests.utils import netmanthanTestCase


class TestFormatter(netmanthanTestCase):
	def test_currency_formatting(self):
		df = netmanthan._dict({"fieldname": "amount", "fieldtype": "Currency", "options": "currency"})

		doc = netmanthan._dict({"amount": 5})
		netmanthan.db.set_default("currency", "INR")

		# if currency field is not passed then default currency should be used.
		self.assertEqual(format(100000, df, doc, format="#,###.##"), "₹ 100,000.00")

		doc.currency = "USD"
		self.assertEqual(format(100000, df, doc, format="#,###.##"), "$ 100,000.00")

		netmanthan.db.set_default("currency", None)
