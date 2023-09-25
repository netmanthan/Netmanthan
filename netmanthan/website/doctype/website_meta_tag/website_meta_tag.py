# Copyright (c) 2019, netmanthan Technologies and contributors
# License: MIT. See LICENSE

import netmanthan
from netmanthan.model.document import Document


class WebsiteMetaTag(Document):
	def get_content(self):
		# can't have new lines in meta content
		return (self.value or "").replace("\n", " ")

	def get_meta_dict(self):
		return {self.key: self.get_content()}

	def set_in_context(self, context):
		context.setdefault("metatags", netmanthan._dict({}))
		context.metatags[self.key] = self.get_content()
		return context
