# Copyright (c) 2020, netmanthan Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import netmanthan
from netmanthan.search.full_text_search import FullTextSearch
from netmanthan.search.website_search import WebsiteSearch
from netmanthan.utils import cint


@netmanthan.whitelist(allow_guest=True)
def web_search(query, scope=None, limit=20):
	limit = cint(limit)
	ws = WebsiteSearch(index_name="web_routes")
	return ws.search(query, scope, limit)
