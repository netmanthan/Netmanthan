# Copyright (c) 2015, netmanthan Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import netmanthan
from netmanthan.utils import strip_html_tags
from netmanthan.utils.html_utils import clean_html

no_cache = 1


def get_context(context):
	message_context = netmanthan._dict()
	if hasattr(netmanthan.local, "message"):
		message_context["header"] = netmanthan.local.message_title
		message_context["title"] = strip_html_tags(netmanthan.local.message_title)
		message_context["message"] = netmanthan.local.message
		if hasattr(netmanthan.local, "message_success"):
			message_context["success"] = netmanthan.local.message_success

	elif netmanthan.local.form_dict.id:
		message_id = netmanthan.local.form_dict.id
		key = f"message_id:{message_id}"
		message = netmanthan.cache().get_value(key, expires=True)
		if message:
			message_context.update(message.get("context", {}))
			if message.get("http_status_code"):
				netmanthan.local.response["http_status_code"] = message["http_status_code"]

	if not message_context.title:
		message_context.title = clean_html(netmanthan.form_dict.title)

	if not message_context.message:
		message_context.message = clean_html(netmanthan.form_dict.message)

	return message_context
