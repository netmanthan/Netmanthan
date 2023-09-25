# Copyright (c) 2015, netmanthan Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

# License: MIT. See LICENSE

import netmanthan
from netmanthan.model.document import Document


class WebsiteScript(Document):
	def on_update(self):
		"""clear cache"""
		netmanthan.clear_cache(user="Guest")

		from netmanthan.website.utils import clear_cache

		clear_cache()
