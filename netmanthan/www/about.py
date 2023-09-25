# Copyright (c) 2015, netmanthan Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import netmanthan

sitemap = 1


def get_context(context):
	context.doc = netmanthan.get_cached_doc("About Us Settings")

	return context
