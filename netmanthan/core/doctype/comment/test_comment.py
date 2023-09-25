# Copyright (c) 2019, netmanthan Technologies and Contributors
# License: MIT. See LICENSE
import json

import netmanthan
from netmanthan.templates.includes.comments.comments import add_comment
from netmanthan.tests.test_model_utils import set_user
from netmanthan.tests.utils import netmanthanTestCase, change_settings
from netmanthan.website.doctype.blog_post.test_blog_post import make_test_blog


class TestComment(netmanthanTestCase):
	def tearDown(self):
		netmanthan.form_dict.comment = None
		netmanthan.form_dict.comment_email = None
		netmanthan.form_dict.comment_by = None
		netmanthan.form_dict.reference_doctype = None
		netmanthan.form_dict.reference_name = None
		netmanthan.form_dict.route = None
		netmanthan.local.request_ip = None

	def test_comment_creation(self):
		test_doc = netmanthan.get_doc(dict(doctype="ToDo", description="test"))
		test_doc.insert()
		comment = test_doc.add_comment("Comment", "test comment")

		test_doc.reload()

		# check if updated in _comments cache
		comments = json.loads(test_doc.get("_comments"))
		self.assertEqual(comments[0].get("name"), comment.name)
		self.assertEqual(comments[0].get("comment"), comment.content)

		# check document creation
		comment_1 = netmanthan.get_all(
			"Comment",
			fields=["*"],
			filters=dict(reference_doctype=test_doc.doctype, reference_name=test_doc.name),
		)[0]

		self.assertEqual(comment_1.content, "test comment")

	# test via blog
	def test_public_comment(self):
		test_blog = make_test_blog()

		netmanthan.db.delete("Comment", {"reference_doctype": "Blog Post"})

		netmanthan.form_dict.comment = "Good comment with 10 chars"
		netmanthan.form_dict.comment_email = "test@test.com"
		netmanthan.form_dict.comment_by = "Good Tester"
		netmanthan.form_dict.reference_doctype = "Blog Post"
		netmanthan.form_dict.reference_name = test_blog.name
		netmanthan.form_dict.route = test_blog.route
		netmanthan.local.request_ip = "127.0.0.1"

		add_comment()

		self.assertEqual(
			netmanthan.get_all(
				"Comment",
				fields=["*"],
				filters=dict(reference_doctype=test_blog.doctype, reference_name=test_blog.name),
			)[0].published,
			1,
		)

		netmanthan.db.delete("Comment", {"reference_doctype": "Blog Post"})

		netmanthan.form_dict.comment = "pleez vizits my site http://mysite.com"
		netmanthan.form_dict.comment_by = "bad commentor"

		add_comment()

		self.assertEqual(
			len(
				netmanthan.get_all(
					"Comment",
					fields=["*"],
					filters=dict(reference_doctype=test_blog.doctype, reference_name=test_blog.name),
				)
			),
			0,
		)

		# test for filtering html and css injection elements
		netmanthan.db.delete("Comment", {"reference_doctype": "Blog Post"})

		netmanthan.form_dict.comment = "<script>alert(1)</script>Comment"
		netmanthan.form_dict.comment_by = "hacker"

		add_comment()

		self.assertEqual(
			netmanthan.get_all(
				"Comment",
				fields=["content"],
				filters=dict(reference_doctype=test_blog.doctype, reference_name=test_blog.name),
			)[0]["content"],
			"Comment",
		)

		test_blog.delete()

	@change_settings("Blog Settings", {"allow_guest_to_comment": 0})
	def test_guest_cannot_comment(self):
		test_blog = make_test_blog()
		with set_user("Guest"):
			netmanthan.form_dict.comment = "Good comment with 10 chars"
			netmanthan.form_dict.comment_email = "mail@example.org"
			netmanthan.form_dict.comment_by = "Good Tester"
			netmanthan.form_dict.reference_doctype = "Blog Post"
			netmanthan.form_dict.reference_name = test_blog.name
			netmanthan.form_dict.route = test_blog.route
			netmanthan.local.request_ip = "127.0.0.1"

			self.assertEqual(add_comment(), None)

	def test_user_not_logged_in(self):
		some_system_user = netmanthan.db.get_value("User", {})

		test_blog = make_test_blog()
		with set_user("Guest"):
			netmanthan.form_dict.comment = "Good comment with 10 chars"
			netmanthan.form_dict.comment_email = some_system_user
			netmanthan.form_dict.comment_by = "Good Tester"
			netmanthan.form_dict.reference_doctype = "Blog Post"
			netmanthan.form_dict.reference_name = test_blog.name
			netmanthan.form_dict.route = test_blog.route
			netmanthan.local.request_ip = "127.0.0.1"

			self.assertRaises(netmanthan.ValidationError, add_comment)
