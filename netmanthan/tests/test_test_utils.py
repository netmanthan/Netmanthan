import netmanthan
from netmanthan.tests.utils import netmanthanTestCase, change_settings


class TestTestUtils(netmanthanTestCase):
	SHOW_TRANSACTION_COMMIT_WARNINGS = True

	def test_document_assertions(self):

		currency = netmanthan.new_doc("Currency")
		currency.currency_name = "STONKS"
		currency.smallest_currency_fraction_value = 0.420_001
		currency.save()

		self.assertDocumentEqual(currency.as_dict(), currency)

	def test_thread_locals(self):
		netmanthan.flags.temp_flag_to_be_discarded = True

	def test_temp_setting_changes(self):
		current_setting = netmanthan.get_system_settings("logout_on_password_reset")

		with change_settings("System Settings", {"logout_on_password_reset": int(not current_setting)}):
			updated_settings = netmanthan.get_system_settings("logout_on_password_reset")
			self.assertNotEqual(current_setting, updated_settings)

		restored_settings = netmanthan.get_system_settings("logout_on_password_reset")
		self.assertEqual(current_setting, restored_settings)


def tearDownModule():
	"""assertions for ensuring tests didn't leave state behind"""
	assert "temp_flag_to_be_discarded" not in netmanthan.flags
	assert not netmanthan.db.exists("Currency", "STONKS")
