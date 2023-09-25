# Copyright (c) 2015, netmanthan Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

# License: MIT. See LICENSE

import netmanthan
from netmanthan.model.document import Document


class AboutUsSettings(Document):
	def on_update(self):
		from netmanthan.website.utils import clear_cache

		clear_cache("about")


def get_args():
	obj = netmanthan.get_doc("About Us Settings")
	return {"obj": obj}
