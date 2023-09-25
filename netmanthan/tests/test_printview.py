import netmanthan
from netmanthan.tests.utils import netmanthanTestCase
from netmanthan.www.printview import get_html_and_style


class PrintViewTest(netmanthanTestCase):
	def test_print_view_without_errors(self):

		user = netmanthan.get_last_doc("User")

		messages_before = netmanthan.get_message_log()
		ret = get_html_and_style(doc=user.as_json(), print_format="Standard", no_letterhead=1)
		messages_after = netmanthan.get_message_log()

		if len(messages_after) > len(messages_before):
			new_messages = messages_after[len(messages_before) :]
			self.fail("Print view showing error/warnings: \n" + "\n".join(str(msg) for msg in new_messages))

		# html should exist
		self.assertTrue(bool(ret["html"]))
