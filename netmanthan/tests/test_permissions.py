# Copyright (c) 2015, netmanthan Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE
"""Use blog post test to test user permissions logic"""

import netmanthan
import netmanthan.defaults
import netmanthan.model.meta
from netmanthan.core.doctype.user_permission.user_permission import clear_user_permissions
from netmanthan.core.page.permission_manager.permission_manager import reset, update
from netmanthan.desk.form.load import getdoc
from netmanthan.permissions import (
	add_permission,
	add_user_permission,
	clear_user_permissions_for_doctype,
	get_doc_permissions,
	remove_user_permission,
	update_permission_property,
)
from netmanthan.test_runner import make_test_records_for_doctype
from netmanthan.tests.test_db_query import enable_permlevel_restrictions
from netmanthan.tests.utils import netmanthanTestCase
from netmanthan.utils.data import now_datetime

test_dependencies = ["Blogger", "Blog Post", "User", "Contact", "Salutation"]


class TestPermissions(netmanthanTestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		netmanthan.clear_cache(doctype="Blog Post")
		user = netmanthan.get_doc("User", "test1@example.com")
		user.add_roles("Website Manager")
		user.add_roles("System Manager")

		user = netmanthan.get_doc("User", "test2@example.com")
		user.add_roles("Blogger")

		user = netmanthan.get_doc("User", "test3@example.com")
		user.add_roles("Sales User")

		user = netmanthan.get_doc("User", "testperm@example.com")
		user.add_roles("Website Manager")

	def setUp(self):
		netmanthan.clear_cache(doctype="Blog Post")

		reset("Blogger")
		reset("Blog Post")

		netmanthan.db.delete("User Permission")

		netmanthan.set_user("test1@example.com")

	def tearDown(self):
		netmanthan.set_user("Administrator")
		netmanthan.db.set_value("Blogger", "_Test Blogger 1", "user", None)

		clear_user_permissions_for_doctype("Blog Category")
		clear_user_permissions_for_doctype("Blog Post")
		clear_user_permissions_for_doctype("Blogger")

	@staticmethod
	def set_strict_user_permissions(ignore):
		ss = netmanthan.get_doc("System Settings")
		ss.apply_strict_user_permissions = ignore
		ss.flags.ignore_mandatory = 1
		ss.save()

	def test_basic_permission(self):
		post = netmanthan.get_doc("Blog Post", "-test-blog-post")
		self.assertTrue(post.has_permission("read"))

	def test_select_permission(self):
		# grant only select perm to blog post
		add_permission("Blog Post", "Sales User", 0)
		update_permission_property("Blog Post", "Sales User", 0, "select", 1)
		update_permission_property("Blog Post", "Sales User", 0, "read", 0)
		update_permission_property("Blog Post", "Sales User", 0, "write", 0)

		netmanthan.clear_cache(doctype="Blog Post")
		netmanthan.set_user("test3@example.com")

		# validate select perm
		post = netmanthan.get_doc("Blog Post", "-test-blog-post")
		self.assertTrue(post.has_permission("select"))

		# validate does not have read and write perm
		self.assertFalse(post.has_permission("read"))
		self.assertRaises(netmanthan.PermissionError, post.save)

		with enable_permlevel_restrictions():
			permitted_record = netmanthan.get_list("Blog Post", fields="*", limit=1)[0]
			full_record = netmanthan.get_all("Blog Post", fields="*", limit=1)[0]
			self.assertNotEqual(permitted_record, full_record)
			self.assertSequenceSubset(post.meta.get_search_fields(), permitted_record)

	def test_user_permissions_in_doc(self):
		add_user_permission("Blog Category", "-test-blog-category-1", "test2@example.com")

		netmanthan.set_user("test2@example.com")

		post = netmanthan.get_doc("Blog Post", "-test-blog-post")
		self.assertFalse(post.has_permission("read"))
		self.assertFalse(get_doc_permissions(post).get("read"))

		post1 = netmanthan.get_doc("Blog Post", "-test-blog-post-1")
		self.assertTrue(post1.has_permission("read"))
		self.assertTrue(get_doc_permissions(post1).get("read"))

	def test_user_permissions_in_report(self):
		add_user_permission("Blog Category", "-test-blog-category-1", "test2@example.com")

		netmanthan.set_user("test2@example.com")
		names = [d.name for d in netmanthan.get_list("Blog Post", fields=["name", "blog_category"])]

		self.assertTrue("-test-blog-post-1" in names)
		self.assertFalse("-test-blog-post" in names)

	def test_default_values(self):
		doc = netmanthan.new_doc("Blog Post")
		self.assertFalse(doc.get("blog_category"))

		# Fetch default based on single user permission
		add_user_permission("Blog Category", "-test-blog-category-1", "test2@example.com")

		netmanthan.set_user("test2@example.com")
		doc = netmanthan.new_doc("Blog Post")
		self.assertEqual(doc.get("blog_category"), "-test-blog-category-1")

		# Don't fetch default if user permissions is more than 1
		add_user_permission(
			"Blog Category", "-test-blog-category", "test2@example.com", ignore_permissions=True
		)
		netmanthan.clear_cache()
		doc = netmanthan.new_doc("Blog Post")
		self.assertFalse(doc.get("blog_category"))

		# Fetch user permission set as default from multiple user permission
		add_user_permission(
			"Blog Category",
			"-test-blog-category-2",
			"test2@example.com",
			ignore_permissions=True,
			is_default=1,
		)
		netmanthan.clear_cache()
		doc = netmanthan.new_doc("Blog Post")
		self.assertEqual(doc.get("blog_category"), "-test-blog-category-2")

	def test_user_link_match_doc(self):
		blogger = netmanthan.get_doc("Blogger", "_Test Blogger 1")
		blogger.user = "test2@example.com"
		blogger.save()

		netmanthan.set_user("test2@example.com")

		post = netmanthan.get_doc("Blog Post", "-test-blog-post-2")
		self.assertTrue(post.has_permission("read"))

		post1 = netmanthan.get_doc("Blog Post", "-test-blog-post-1")
		self.assertFalse(post1.has_permission("read"))

	def test_user_link_match_report(self):
		blogger = netmanthan.get_doc("Blogger", "_Test Blogger 1")
		blogger.user = "test2@example.com"
		blogger.save()

		netmanthan.set_user("test2@example.com")

		names = [d.name for d in netmanthan.get_list("Blog Post", fields=["name", "owner"])]
		self.assertTrue("-test-blog-post-2" in names)
		self.assertFalse("-test-blog-post-1" in names)

	def test_set_user_permissions(self):
		netmanthan.set_user("test1@example.com")
		add_user_permission("Blog Post", "-test-blog-post", "test2@example.com")

	def test_not_allowed_to_set_user_permissions(self):
		netmanthan.set_user("test2@example.com")

		# this user can't add user permissions
		self.assertRaises(
			netmanthan.PermissionError, add_user_permission, "Blog Post", "-test-blog-post", "test2@example.com"
		)

	def test_read_if_explicit_user_permissions_are_set(self):
		self.test_set_user_permissions()

		netmanthan.set_user("test2@example.com")

		# user can only access permitted blog post
		doc = netmanthan.get_doc("Blog Post", "-test-blog-post")
		self.assertTrue(doc.has_permission("read"))

		# and not this one
		doc = netmanthan.get_doc("Blog Post", "-test-blog-post-1")
		self.assertFalse(doc.has_permission("read"))

	def test_not_allowed_to_remove_user_permissions(self):
		self.test_set_user_permissions()

		netmanthan.set_user("test2@example.com")

		# user cannot remove their own user permissions
		self.assertRaises(
			netmanthan.PermissionError,
			remove_user_permission,
			"Blog Post",
			"-test-blog-post",
			"test2@example.com",
		)

	def test_user_permissions_if_applied_on_doc_being_evaluated(self):
		netmanthan.set_user("test2@example.com")
		doc = netmanthan.get_doc("Blog Post", "-test-blog-post-1")
		self.assertTrue(doc.has_permission("read"))

		netmanthan.set_user("test1@example.com")
		add_user_permission("Blog Post", "-test-blog-post", "test2@example.com")

		netmanthan.set_user("test2@example.com")
		doc = netmanthan.get_doc("Blog Post", "-test-blog-post-1")
		self.assertFalse(doc.has_permission("read"))

		doc = netmanthan.get_doc("Blog Post", "-test-blog-post")
		self.assertTrue(doc.has_permission("read"))

	def test_set_standard_fields_manually(self):
		# check that creation and owner cannot be set manually
		from datetime import timedelta

		fake_creation = now_datetime() + timedelta(days=-7)
		fake_owner = netmanthan.db.get_value("User", {"name": ("!=", netmanthan.session.user)})

		d = netmanthan.new_doc("ToDo")
		d.description = "ToDo created via test_set_standard_fields_manually"
		d.creation = fake_creation
		d.owner = fake_owner
		d.save()
		self.assertNotEqual(d.creation, fake_creation)
		self.assertNotEqual(d.owner, fake_owner)

	def test_dont_change_standard_constants(self):
		# check that Document.creation cannot be changed
		user = netmanthan.get_doc("User", netmanthan.session.user)
		user.creation = now_datetime()
		self.assertRaises(netmanthan.CannotChangeConstantError, user.save)

		# check that Document.owner cannot be changed
		user.reload()
		user.owner = "Guest"
		self.assertRaises(netmanthan.CannotChangeConstantError, user.save)

	def test_set_only_once(self):
		blog_post = netmanthan.get_meta("Blog Post")
		doc = netmanthan.get_doc("Blog Post", "-test-blog-post-1")
		doc.db_set("title", "Old")
		blog_post.get_field("title").set_only_once = 1
		doc.title = "New"
		self.assertRaises(netmanthan.CannotChangeConstantError, doc.save)
		blog_post.get_field("title").set_only_once = 0

	def test_set_only_once_child_table_rows(self):
		doctype_meta = netmanthan.get_meta("DocType")
		doctype_meta.get_field("fields").set_only_once = 1
		doc = netmanthan.get_doc("DocType", "Blog Post")

		# remove last one
		doc.fields = doc.fields[:-1]
		self.assertRaises(netmanthan.CannotChangeConstantError, doc.save)
		netmanthan.clear_cache(doctype="DocType")

	def test_set_only_once_child_table_row_value(self):
		doctype_meta = netmanthan.get_meta("DocType")
		doctype_meta.get_field("fields").set_only_once = 1
		doc = netmanthan.get_doc("DocType", "Blog Post")

		# change one property from the child table
		doc.fields[-1].fieldtype = "Check"
		self.assertRaises(netmanthan.CannotChangeConstantError, doc.save)
		netmanthan.clear_cache(doctype="DocType")

	def test_set_only_once_child_table_okay(self):
		doctype_meta = netmanthan.get_meta("DocType")
		doctype_meta.get_field("fields").set_only_once = 1
		doc = netmanthan.get_doc("DocType", "Blog Post")

		doc.load_doc_before_save()
		self.assertFalse(doc.validate_set_only_once())
		netmanthan.clear_cache(doctype="DocType")

	def test_user_permission_doctypes(self):
		add_user_permission("Blog Category", "-test-blog-category-1", "test2@example.com")
		add_user_permission("Blogger", "_Test Blogger 1", "test2@example.com")

		netmanthan.set_user("test2@example.com")

		netmanthan.clear_cache(doctype="Blog Post")

		doc = netmanthan.get_doc("Blog Post", "-test-blog-post")
		self.assertFalse(doc.has_permission("read"))

		doc = netmanthan.get_doc("Blog Post", "-test-blog-post-2")
		self.assertTrue(doc.has_permission("read"))

		netmanthan.clear_cache(doctype="Blog Post")

	def if_owner_setup(self):
		update("Blog Post", "Blogger", 0, "if_owner", 1)

		add_user_permission("Blog Category", "-test-blog-category-1", "test2@example.com")
		add_user_permission("Blogger", "_Test Blogger 1", "test2@example.com")

		netmanthan.clear_cache(doctype="Blog Post")

	def test_insert_if_owner_with_user_permissions(self):
		"""If `If Owner` is checked for a Role, check if that document
		is allowed to be read, updated, submitted, etc. except be created,
		even if the document is restricted based on User Permissions."""
		netmanthan.delete_doc("Blog Post", "-test-blog-post-title")

		self.if_owner_setup()

		netmanthan.set_user("test2@example.com")

		doc = netmanthan.get_doc(
			{
				"doctype": "Blog Post",
				"blog_category": "-test-blog-category",
				"blogger": "_Test Blogger 1",
				"title": "_Test Blog Post Title",
				"content": "_Test Blog Post Content",
			}
		)

		self.assertRaises(netmanthan.PermissionError, doc.insert)

		netmanthan.set_user("test1@example.com")
		add_user_permission("Blog Category", "-test-blog-category", "test2@example.com")

		netmanthan.set_user("test2@example.com")
		doc.insert()

		netmanthan.set_user("Administrator")
		remove_user_permission("Blog Category", "-test-blog-category", "test2@example.com")

		netmanthan.set_user("test2@example.com")
		doc = netmanthan.get_doc(doc.doctype, doc.name)
		self.assertTrue(doc.has_permission("read"))
		self.assertTrue(doc.has_permission("write"))
		self.assertFalse(doc.has_permission("create"))

		# delete created record
		netmanthan.set_user("Administrator")
		netmanthan.delete_doc("Blog Post", "-test-blog-post-title")

	def test_ignore_user_permissions_if_missing(self):
		"""If there are no user permissions, then allow as per role"""

		add_user_permission("Blog Category", "-test-blog-category", "test2@example.com")
		netmanthan.set_user("test2@example.com")

		doc = netmanthan.get_doc(
			{
				"doctype": "Blog Post",
				"blog_category": "-test-blog-category-2",
				"blogger": "_Test Blogger 1",
				"title": "_Test Blog Post Title",
				"content": "_Test Blog Post Content",
			}
		)

		self.assertFalse(doc.has_permission("write"))

		netmanthan.set_user("Administrator")
		remove_user_permission("Blog Category", "-test-blog-category", "test2@example.com")

		netmanthan.set_user("test2@example.com")
		self.assertTrue(doc.has_permission("write"))

	def test_strict_user_permissions(self):
		"""If `Strict User Permissions` is checked in System Settings,
		show records even if User Permissions are missing for a linked
		doctype"""

		netmanthan.set_user("Administrator")
		netmanthan.db.delete("Contact")
		netmanthan.db.delete("Contact Email")
		netmanthan.db.delete("Contact Phone")

		reset("Salutation")
		reset("Contact")

		make_test_records_for_doctype("Contact", force=True)

		add_user_permission("Salutation", "Mr", "test3@example.com")
		self.set_strict_user_permissions(0)

		allowed_contact = netmanthan.get_doc("Contact", "_Test Contact For _Test Customer")
		other_contact = netmanthan.get_doc("Contact", "_Test Contact For _Test Supplier")

		netmanthan.set_user("test3@example.com")
		self.assertTrue(allowed_contact.has_permission("read"))
		self.assertTrue(other_contact.has_permission("read"))
		self.assertEqual(len(netmanthan.get_list("Contact")), 2)

		netmanthan.set_user("Administrator")
		self.set_strict_user_permissions(1)

		netmanthan.set_user("test3@example.com")
		self.assertTrue(allowed_contact.has_permission("read"))
		self.assertFalse(other_contact.has_permission("read"))
		self.assertTrue(len(netmanthan.get_list("Contact")), 1)

		netmanthan.set_user("Administrator")
		self.set_strict_user_permissions(0)

		clear_user_permissions_for_doctype("Salutation")
		clear_user_permissions_for_doctype("Contact")

	def test_user_permissions_not_applied_if_user_can_edit_user_permissions(self):
		add_user_permission("Blogger", "_Test Blogger 1", "test1@example.com")

		# test1@example.com has rights to create user permissions
		# so it should not matter if explicit user permissions are not set
		self.assertTrue(netmanthan.get_doc("Blogger", "_Test Blogger").has_permission("read"))

	def test_user_permission_is_not_applied_if_user_roles_does_not_have_permission(self):
		add_user_permission("Blog Post", "-test-blog-post-1", "test3@example.com")
		netmanthan.set_user("test3@example.com")
		doc = netmanthan.get_doc("Blog Post", "-test-blog-post-1")
		self.assertFalse(doc.has_permission("read"))

		netmanthan.set_user("Administrator")
		user = netmanthan.get_doc("User", "test3@example.com")
		user.add_roles("Blogger")
		netmanthan.set_user("test3@example.com")
		self.assertTrue(doc.has_permission("read"))

		netmanthan.set_user("Administrator")
		user.remove_roles("Blogger")

	def test_contextual_user_permission(self):
		# should be applicable for across all doctypes
		add_user_permission("Blogger", "_Test Blogger", "test2@example.com")
		# should be applicable only while accessing Blog Post
		add_user_permission(
			"Blogger", "_Test Blogger 1", "test2@example.com", applicable_for="Blog Post"
		)
		# should be applicable only while accessing User
		add_user_permission("Blogger", "_Test Blogger 2", "test2@example.com", applicable_for="User")

		posts = netmanthan.get_all("Blog Post", fields=["name", "blogger"])

		# Get all posts for admin
		self.assertEqual(len(posts), 4)

		netmanthan.set_user("test2@example.com")

		posts = netmanthan.get_list("Blog Post", fields=["name", "blogger"])

		# Should get only posts with allowed blogger via user permission
		# only '_Test Blogger', '_Test Blogger 1' are allowed in Blog Post
		self.assertEqual(len(posts), 3)

		for post in posts:
			self.assertIn(
				post.blogger,
				["_Test Blogger", "_Test Blogger 1"],
				f"A post from {post.blogger} is not expected.",
			)

	def test_if_owner_permission_overrides_properly(self):
		# check if user is not granted access if the user is not the owner of the doc
		# Blogger has only read access on the blog post unless he is the owner of the blog
		update("Blog Post", "Blogger", 0, "if_owner", 1)
		update("Blog Post", "Blogger", 0, "read", 1, 1)
		update("Blog Post", "Blogger", 0, "write", 1, 1)
		update("Blog Post", "Blogger", 0, "delete", 1, 1)

		# currently test2 user has not created any document
		# still he should be able to do get_list query which should
		# not raise permission error but simply return empty list
		netmanthan.set_user("test2@example.com")
		self.assertEqual(netmanthan.get_list("Blog Post"), [])

		netmanthan.set_user("Administrator")

		# creates a custom docperm with just read access
		# now any user can read any blog post (but other rights are limited to the blog post owner)
		add_permission("Blog Post", "Blogger")
		netmanthan.clear_cache(doctype="Blog Post")

		netmanthan.delete_doc("Blog Post", "-test-blog-post-title")

		netmanthan.set_user("test1@example.com")

		doc = netmanthan.get_doc(
			{
				"doctype": "Blog Post",
				"blog_category": "-test-blog-category",
				"blogger": "_Test Blogger 1",
				"title": "_Test Blog Post Title",
				"content": "_Test Blog Post Content",
			}
		)

		doc.insert()

		netmanthan.set_user("test2@example.com")
		doc = netmanthan.get_doc(doc.doctype, doc.name)

		self.assertTrue(doc.has_permission("read"))
		self.assertFalse(doc.has_permission("write"))
		self.assertFalse(doc.has_permission("delete"))

		# check if owner of the doc has the access that is available only for the owner of the doc
		netmanthan.set_user("test1@example.com")
		doc = netmanthan.get_doc(doc.doctype, doc.name)

		self.assertTrue(doc.has_permission("read"))
		self.assertTrue(doc.has_permission("write"))
		self.assertTrue(doc.has_permission("delete"))

		# delete the created doc
		netmanthan.delete_doc("Blog Post", "-test-blog-post-title")

	def test_if_owner_permission_on_getdoc(self):
		update("Blog Post", "Blogger", 0, "if_owner", 1)
		update("Blog Post", "Blogger", 0, "read", 1)
		update("Blog Post", "Blogger", 0, "write", 1)
		update("Blog Post", "Blogger", 0, "delete", 1)
		netmanthan.clear_cache(doctype="Blog Post")

		netmanthan.set_user("test1@example.com")

		doc = netmanthan.get_doc(
			{
				"doctype": "Blog Post",
				"blog_category": "-test-blog-category",
				"blogger": "_Test Blogger 1",
				"title": "_Test Blog Post Title New",
				"content": "_Test Blog Post Content",
			}
		)

		doc.insert()

		getdoc("Blog Post", doc.name)
		doclist = [d.name for d in netmanthan.response.docs]
		self.assertTrue(doc.name in doclist)

		netmanthan.set_user("test2@example.com")
		self.assertRaises(netmanthan.PermissionError, getdoc, "Blog Post", doc.name)

	def test_if_owner_permission_on_get_list(self):
		doc = netmanthan.get_doc(
			{
				"doctype": "Blog Post",
				"blog_category": "-test-blog-category",
				"blogger": "_Test Blogger 1",
				"title": "_Test If Owner Permissions on Get List",
				"content": "_Test Blog Post Content",
			}
		)

		doc.insert(ignore_if_duplicate=True)

		update("Blog Post", "Blogger", 0, "if_owner", 1)
		update("Blog Post", "Blogger", 0, "read", 1)
		user = netmanthan.get_doc("User", "test2@example.com")
		user.add_roles("Website Manager")
		netmanthan.clear_cache(doctype="Blog Post")

		netmanthan.set_user("test2@example.com")
		self.assertIn(doc.name, netmanthan.get_list("Blog Post", pluck="name"))

		# Become system manager to remove role
		netmanthan.set_user("test1@example.com")
		user.remove_roles("Website Manager")
		netmanthan.clear_cache(doctype="Blog Post")

		netmanthan.set_user("test2@example.com")
		self.assertNotIn(doc.name, netmanthan.get_list("Blog Post", pluck="name"))

	def test_if_owner_permission_on_delete(self):
		update("Blog Post", "Blogger", 0, "if_owner", 1)
		update("Blog Post", "Blogger", 0, "read", 1, 1)
		update("Blog Post", "Blogger", 0, "write", 1, 1)
		update("Blog Post", "Blogger", 0, "delete", 1, 1)

		# Remove delete perm
		update("Blog Post", "Website Manager", 0, "delete", 0)

		netmanthan.clear_cache(doctype="Blog Post")

		netmanthan.set_user("test2@example.com")

		doc = netmanthan.get_doc(
			{
				"doctype": "Blog Post",
				"blog_category": "-test-blog-category",
				"blogger": "_Test Blogger 1",
				"title": "_Test Blog Post Title New 1",
				"content": "_Test Blog Post Content",
			}
		)

		doc.insert()

		getdoc("Blog Post", doc.name)
		doclist = [d.name for d in netmanthan.response.docs]
		self.assertTrue(doc.name in doclist)

		netmanthan.set_user("testperm@example.com")

		# Website Manager able to read
		getdoc("Blog Post", doc.name)
		doclist = [d.name for d in netmanthan.response.docs]
		self.assertTrue(doc.name in doclist)

		# Website Manager should not be able to delete
		self.assertRaises(netmanthan.PermissionError, netmanthan.delete_doc, "Blog Post", doc.name)

		netmanthan.set_user("test2@example.com")
		netmanthan.delete_doc("Blog Post", "-test-blog-post-title-new-1")
		update("Blog Post", "Website Manager", 0, "delete", 1, 1)

	def test_clear_user_permissions(self):
		current_user = netmanthan.session.user
		netmanthan.set_user("Administrator")
		clear_user_permissions_for_doctype("Blog Category", "test2@example.com")
		clear_user_permissions_for_doctype("Blog Post", "test2@example.com")

		add_user_permission("Blog Post", "-test-blog-post-1", "test2@example.com")
		add_user_permission("Blog Post", "-test-blog-post-2", "test2@example.com")
		add_user_permission("Blog Category", "-test-blog-category-1", "test2@example.com")

		deleted_user_permission_count = clear_user_permissions("test2@example.com", "Blog Post")

		self.assertEqual(deleted_user_permission_count, 2)

		blog_post_user_permission_count = netmanthan.db.count(
			"User Permission", filters={"user": "test2@example.com", "allow": "Blog Post"}
		)

		self.assertEqual(blog_post_user_permission_count, 0)

		blog_category_user_permission_count = netmanthan.db.count(
			"User Permission", filters={"user": "test2@example.com", "allow": "Blog Category"}
		)

		self.assertEqual(blog_category_user_permission_count, 1)

		# reset the user
		netmanthan.set_user(current_user)

	def test_child_permissions(self):
		netmanthan.set_user("test3@example.com")
		self.assertIsInstance(netmanthan.get_list("DefaultValue", parent_doctype="User", limit=1), list)

		# netmanthan.get_list
		self.assertRaises(netmanthan.PermissionError, netmanthan.get_list, "DefaultValue")
		self.assertRaises(netmanthan.PermissionError, netmanthan.get_list, "DefaultValue", parent_doctype="ToDo")
		self.assertRaises(
			netmanthan.PermissionError, netmanthan.get_list, "DefaultValue", parent_doctype="DefaultValue"
		)

		# netmanthan.get_doc
		user = netmanthan.get_doc("User", netmanthan.session.user)
		doc = user.append("defaults")
		doc.check_permission()

		# false due to missing parentfield
		doc = user.append("roles")
		doc.parentfield = None
		self.assertRaises(netmanthan.PermissionError, doc.check_permission)

		# false due to invalid parentfield
		doc = user.append("roles")
		doc.parentfield = "first_name"
		self.assertRaises(netmanthan.PermissionError, doc.check_permission)

		# false by permlevel
		doc = user.append("roles")
		self.assertRaises(netmanthan.PermissionError, doc.check_permission)

		# false by user permission
		user = netmanthan.get_doc("User", "Administrator")
		doc = user.append("defaults")
		self.assertRaises(netmanthan.PermissionError, doc.check_permission)

	def test_select_user(self):
		"""If test3@example.com is restricted by a User Permission to see only
		users linked to a certain doctype (in this case: Gender "Female"), he
		should not be able to query other users (Gender "Male").
		"""
		# ensure required genders exist
		for gender in ("Male", "Female"):
			if netmanthan.db.exists("Gender", gender):
				continue

			netmanthan.get_doc({"doctype": "Gender", "gender": gender}).insert()

		# asssign gender to test users
		netmanthan.db.set_value("User", "test1@example.com", "gender", "Male")
		netmanthan.db.set_value("User", "test2@example.com", "gender", "Female")
		netmanthan.db.set_value("User", "test3@example.com", "gender", "Female")

		# restrict test3@example.com to see only female users
		add_user_permission("Gender", "Female", "test3@example.com")

		# become user test3@example.com and see what users he can query
		netmanthan.set_user("test3@example.com")
		users = netmanthan.get_list("User", pluck="name")

		self.assertNotIn("test1@example.com", users)
		self.assertIn("test2@example.com", users)
		self.assertIn("test3@example.com", users)
