# Copyright (c) 2015, netmanthan Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

# License: MIT. See LICENSE

import netmanthan
from netmanthan import _
from netmanthan.model.document import Document


class Blogger(Document):
	def validate(self):
		if self.user and not netmanthan.db.exists("User", self.user):
			# for data import
			netmanthan.get_doc(
				{"doctype": "User", "email": self.user, "first_name": self.user.split("@", 1)[0]}
			).insert()

	def on_update(self):
		"if user is set, then update all older blogs"

		from netmanthan.website.doctype.blog_post.blog_post import clear_blog_cache

		clear_blog_cache()

		if self.user:
			for blog in netmanthan.db.sql_list(
				"""select name from `tabBlog Post` where owner=%s
				and ifnull(blogger,'')=''""",
				self.user,
			):
				b = netmanthan.get_doc("Blog Post", blog)
				b.blogger = self.name
				b.save()

			netmanthan.permissions.add_user_permission("Blogger", self.name, self.user)
