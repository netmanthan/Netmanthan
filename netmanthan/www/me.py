# Copyright (c) 2015, netmanthan Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import netmanthan
import netmanthan.www.list
from netmanthan import _

no_cache = 1


def get_context(context):
	if netmanthan.session.user == "Guest":
		netmanthan.throw(_("You need to be logged in to access this page"), netmanthan.PermissionError)

	context.current_user = netmanthan.get_doc("User", netmanthan.session.user)
	context.show_sidebar = True
