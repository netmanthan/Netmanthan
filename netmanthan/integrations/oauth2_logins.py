# Copyright (c) 2022, netmanthan Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import json

import netmanthan
import netmanthan.utils
from netmanthan.utils.oauth import login_via_oauth2, login_via_oauth2_id_token


@netmanthan.whitelist(allow_guest=True)
def login_via_google(code: str, state: str):
	login_via_oauth2("google", code, state, decoder=decoder_compat)


@netmanthan.whitelist(allow_guest=True)
def login_via_github(code: str, state: str):
	login_via_oauth2("github", code, state)


@netmanthan.whitelist(allow_guest=True)
def login_via_facebook(code: str, state: str):
	login_via_oauth2("facebook", code, state, decoder=decoder_compat)


@netmanthan.whitelist(allow_guest=True)
def login_via_netmanthan(code: str, state: str):
	login_via_oauth2("netmanthan", code, state, decoder=decoder_compat)


@netmanthan.whitelist(allow_guest=True)
def login_via_office365(code: str, state: str):
	login_via_oauth2_id_token("office_365", code, state, decoder=decoder_compat)


@netmanthan.whitelist(allow_guest=True)
def login_via_salesforce(code: str, state: str):
	login_via_oauth2("salesforce", code, state, decoder=decoder_compat)


@netmanthan.whitelist(allow_guest=True)
def login_via_fairlogin(code: str, state: str):
	login_via_oauth2("fairlogin", code, state, decoder=decoder_compat)


@netmanthan.whitelist(allow_guest=True)
def custom(code: str, state: str):
	"""
	Callback for processing code and state for user added providers

	process social login from /api/method/netmanthan.integrations.custom/<provider>
	"""
	path = netmanthan.request.path[1:].split("/")
	if len(path) == 4 and path[3]:
		provider = path[3]
		# Validates if provider doctype exists
		if netmanthan.db.exists("Social Login Key", provider):
			login_via_oauth2(provider, code, state, decoder=decoder_compat)


def decoder_compat(b):
	# https://github.com/litl/rauth/issues/145#issuecomment-31199471
	return json.loads(bytes(b).decode("utf-8"))
