# Copyright (c) 2022, netmanthan Technologies and contributors
# License: MIT. See LICENSE

import netmanthan
from netmanthan.deferred_insert import deferred_insert as _deferred_insert
from netmanthan.model.document import Document


class RouteHistory(Document):
	@staticmethod
	def clear_old_logs(days=30):
		from netmanthan.query_builder import Interval
		from netmanthan.query_builder.functions import Now

		table = netmanthan.qb.DocType("Route History")
		netmanthan.db.delete(table, filters=(table.modified < (Now() - Interval(days=days))))


@netmanthan.whitelist()
def deferred_insert(routes):
	routes = [
		{
			"user": netmanthan.session.user,
			"route": route.get("route"),
			"creation": route.get("creation"),
		}
		for route in netmanthan.parse_json(routes)
	]

	_deferred_insert("Route History", routes)


@netmanthan.whitelist()
def frequently_visited_links():
	return netmanthan.get_all(
		"Route History",
		fields=["route", "count(name) as count"],
		filters={"user": netmanthan.session.user},
		group_by="route",
		order_by="count desc",
		limit=5,
	)
