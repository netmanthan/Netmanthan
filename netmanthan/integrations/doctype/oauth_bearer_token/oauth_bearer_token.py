# Copyright (c) 2015, netmanthan Technologies and contributors
# License: MIT. See LICENSE

import netmanthan
from netmanthan.model.document import Document


class OAuthBearerToken(Document):
	def validate(self):
		if not self.expiration_time:
			self.expiration_time = netmanthan.utils.datetime.datetime.strptime(
				self.creation, "%Y-%m-%d %H:%M:%S.%f"
			) + netmanthan.utils.datetime.timedelta(seconds=self.expires_in)
