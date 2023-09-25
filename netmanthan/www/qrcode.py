# Copyright (c) 2015, netmanthan Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

from urllib.parse import parse_qsl

import netmanthan
from netmanthan import _
from netmanthan.twofactor import get_qr_svg_code


def get_context(context):
	context.no_cache = 1
	context.qr_code_user, context.qrcode_svg = get_user_svg_from_cache()


def get_query_key():
	"""Return query string arg."""
	query_string = netmanthan.local.request.query_string
	query = dict(parse_qsl(query_string))
	query = {key.decode(): val.decode() for key, val in query.items()}
	if not "k" in list(query):
		netmanthan.throw(_("Not Permitted"), netmanthan.PermissionError)
	query = (query["k"]).strip()
	if False in [i.isalpha() or i.isdigit() for i in query]:
		netmanthan.throw(_("Not Permitted"), netmanthan.PermissionError)
	return query


def get_user_svg_from_cache():
	"""Get User and SVG code from cache."""
	key = get_query_key()
	totp_uri = netmanthan.cache().get_value(f"{key}_uri")
	user = netmanthan.cache().get_value(f"{key}_user")
	if not totp_uri or not user:
		netmanthan.throw(_("Page has expired!"), netmanthan.PermissionError)
	if not netmanthan.db.exists("User", user):
		netmanthan.throw(_("Not Permitted"), netmanthan.PermissionError)
	user = netmanthan.get_doc("User", user)
	svg = get_qr_svg_code(totp_uri)
	return (user, svg.decode())
