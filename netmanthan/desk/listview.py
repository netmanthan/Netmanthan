# Copyright (c) 2022, netmanthan Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import netmanthan
from netmanthan.model import is_default_field
from netmanthan.query_builder import Order
from netmanthan.query_builder.functions import Count
from netmanthan.query_builder.terms import SubQuery
from netmanthan.query_builder.utils import DocType


@netmanthan.whitelist()
def get_list_settings(doctype):
	try:
		return netmanthan.get_cached_doc("List View Settings", doctype)
	except netmanthan.DoesNotExistError:
		netmanthan.clear_messages()


@netmanthan.whitelist()
def set_list_settings(doctype, values):
	try:
		doc = netmanthan.get_doc("List View Settings", doctype)
	except netmanthan.DoesNotExistError:
		doc = netmanthan.new_doc("List View Settings")
		doc.name = doctype
		netmanthan.clear_messages()
	doc.update(netmanthan.parse_json(values))
	doc.save()


@netmanthan.whitelist()
def get_group_by_count(doctype: str, current_filters: str, field: str) -> list[dict]:
	current_filters = netmanthan.parse_json(current_filters)

	if field == "assigned_to":
		ToDo = DocType("ToDo")
		User = DocType("User")
		count = Count("*").as_("count")
		filtered_records = netmanthan.qb.get_query(
			doctype,
			filters=current_filters,
			fields=["name"],
			validate_filters=True,
		)

		return (
			netmanthan.qb.from_(ToDo)
			.from_(User)
			.select(ToDo.allocated_to.as_("name"), count)
			.where(
				(ToDo.status != "Cancelled")
				& (ToDo.allocated_to == User.name)
				& (User.user_type == "System User")
				& (ToDo.reference_name.isin(SubQuery(filtered_records)))
			)
			.groupby(ToDo.allocated_to)
			.orderby(count, order=Order.desc)
			.limit(50)
			.run(as_dict=True)
		)

	if not netmanthan.get_meta(doctype).has_field(field) and not is_default_field(field):
		raise ValueError("Field does not belong to doctype")

	return netmanthan.get_list(
		doctype,
		filters=current_filters,
		group_by=f"`tab{doctype}`.{field}",
		fields=["count(*) as count", f"`{field}` as name"],
		order_by="count desc",
		limit=50,
	)
