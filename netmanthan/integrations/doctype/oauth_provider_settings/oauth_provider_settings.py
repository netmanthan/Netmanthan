# Copyright (c) 2015, netmanthan Technologies and contributors
# License: MIT. See LICENSE

import netmanthan
from netmanthan import _
from netmanthan.model.document import Document


class OAuthProviderSettings(Document):
	pass


def get_oauth_settings():
	"""Returns oauth settings"""
	out = netmanthan._dict(
		{
			"skip_authorization": netmanthan.db.get_single_value(
				"OAuth Provider Settings", "skip_authorization"
			)
		}
	)

	return out
