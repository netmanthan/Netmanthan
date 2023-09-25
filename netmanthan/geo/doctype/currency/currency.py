# Copyright (c) 2015, netmanthan Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import netmanthan
from netmanthan.model.document import Document


class Currency(Document):
	def validate(self):
		if not netmanthan.flags.in_install_app:
			netmanthan.clear_cache()
