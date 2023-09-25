# Copyright (c) 2015, netmanthan Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

from netmanthan.website.utils import clear_cache
from netmanthan.website.website_generator import WebsiteGenerator


class BlogCategory(WebsiteGenerator):
	def autoname(self):
		# to override autoname of WebsiteGenerator
		self.name = self.scrub(self.title)

	def on_update(self):
		clear_cache()

	def set_route(self):
		# Override blog route since it has to been templated
		self.route = "blog/" + self.name
