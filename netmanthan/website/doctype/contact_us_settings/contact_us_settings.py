# Copyright (c) 2015, netmanthan Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

# License: MIT. See LICENSE

import netmanthan
from netmanthan.model.document import Document


class ContactUsSettings(Document):
	def on_update(self):
		from netmanthan.website.utils import clear_cache

		clear_cache("contact")
