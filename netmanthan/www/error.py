# Copyright (c) 2015, netmanthan Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE
import netmanthan
from netmanthan import _

no_cache = 1


def get_context(context):
	if netmanthan.flags.in_migrate:
		return

	context.error_title = context.error_title or _("Uncaught Server Exception")
	context.error_message = context.error_message or _("There was an error building this page")

	return {"error": netmanthan.get_traceback().replace("<", "&lt;").replace(">", "&gt;")}
