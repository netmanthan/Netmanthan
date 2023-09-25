import netmanthan
from netmanthan.boot import get_unseen_notes, get_user_pages_or_reports
from netmanthan.desk.doctype.note.note import mark_as_seen
from netmanthan.tests.utils import netmanthanTestCase


class TestBootData(netmanthanTestCase):
	def test_get_unseen_notes(self):
		netmanthan.db.delete("Note")
		netmanthan.db.delete("Note Seen By")
		note = netmanthan.get_doc(
			{
				"doctype": "Note",
				"title": "Test Note",
				"notify_on_login": 1,
				"content": "Test Note 1",
				"public": 1,
			}
		)
		note.insert()

		netmanthan.set_user("test@example.com")
		unseen_notes = [d.title for d in get_unseen_notes()]
		self.assertListEqual(unseen_notes, ["Test Note"])

		mark_as_seen(note.name)
		unseen_notes = [d.title for d in get_unseen_notes()]
		self.assertListEqual(unseen_notes, [])

	def test_get_user_pages_or_reports_with_permission_query(self):
		# Create a ToDo custom report with admin user
		netmanthan.set_user("Administrator")
		netmanthan.get_doc(
			{
				"doctype": "Report",
				"ref_doctype": "ToDo",
				"report_name": "Test Admin Report",
				"report_type": "Report Builder",
				"is_standard": "No",
			}
		).insert()

		# Add permission query such that each user can only see their own custom reports
		netmanthan.get_doc(
			dict(
				doctype="Server Script",
				name="test_report_permission_query",
				script_type="Permission Query",
				reference_doctype="Report",
				script="""conditions = f"(`tabReport`.is_standard = 'Yes' or `tabReport`.owner = '{netmanthan.session.user}')"
				""",
			)
		).insert()

		# Create a ToDo custom report with test user
		netmanthan.set_user("test@example.com")
		netmanthan.get_doc(
			{
				"doctype": "Report",
				"ref_doctype": "ToDo",
				"report_name": "Test User Report",
				"report_type": "Report Builder",
				"is_standard": "No",
			}
		).insert(ignore_permissions=True)

		get_user_pages_or_reports("Report")
		allowed_reports = netmanthan.cache().get_value("has_role:Report", user=netmanthan.session.user)

		# Test user must not see admin user's report
		self.assertNotIn("Test Admin Report", allowed_reports)
		self.assertIn("Test User Report", allowed_reports)
