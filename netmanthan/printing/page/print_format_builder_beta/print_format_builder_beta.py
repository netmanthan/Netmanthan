# Copyright (c) 2021, netmanthan Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt


import functools

import netmanthan


@netmanthan.whitelist()
def get_google_fonts():
	return _get_google_fonts()


@functools.lru_cache
def _get_google_fonts():
	file_path = netmanthan.get_app_path("netmanthan", "data", "google_fonts.json")
	return netmanthan.parse_json(netmanthan.read_file(file_path))
