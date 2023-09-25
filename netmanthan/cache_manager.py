# Copyright (c) 2018, netmanthan Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import netmanthan

common_default_keys = ["__default", "__global"]

doctypes_for_mapping = {
	"Energy Point Rule",
	"Assignment Rule",
	"Milestone Tracker",
	"Document Naming Rule",
}


def get_doctype_map_key(doctype):
	return netmanthan.scrub(doctype) + "_map"


doctype_map_keys = tuple(map(get_doctype_map_key, doctypes_for_mapping))

bench_cache_keys = ("assets_json",)

global_cache_keys = (
	"app_hooks",
	"installed_apps",
	"all_apps",
	"app_modules",
	"module_app",
	"system_settings",
	"scheduler_events",
	"time_zone",
	"webhooks",
	"active_domains",
	"active_modules",
	"assignment_rule",
	"server_script_map",
	"wkhtmltopdf_version",
	"domain_restricted_doctypes",
	"domain_restricted_pages",
	"information_schema:counts",
	"sitemap_routes",
	"db_tables",
	"server_script_autocompletion_items",
) + doctype_map_keys

user_cache_keys = (
	"bootinfo",
	"user_recent",
	"roles",
	"user_doc",
	"lang",
	"defaults",
	"user_permissions",
	"home_page",
	"linked_with",
	"desktop_icons",
	"portal_menu_items",
	"user_perm_can_read",
	"has_role:Page",
	"has_role:Report",
	"desk_sidebar_items",
	"contacts",
)

doctype_cache_keys = (
	"doctype_meta",
	"doctype_form_meta",
	"table_columns",
	"last_modified",
	"linked_doctypes",
	"notifications",
	"workflow",
	"data_import_column_header_map",
)


def clear_user_cache(user=None):
	from netmanthan.desk.notifications import clear_notifications

	cache = netmanthan.cache()

	# this will automatically reload the global cache
	# so it is important to clear this first
	clear_notifications(user)

	if user:
		for name in user_cache_keys:
			cache.hdel(name, user)
		cache.delete_keys("user:" + user)
		clear_defaults_cache(user)
	else:
		for name in user_cache_keys:
			cache.delete_key(name)
		clear_defaults_cache()
		clear_global_cache()


def clear_domain_cache(user=None):
	cache = netmanthan.cache()
	domain_cache_keys = ("domain_restricted_doctypes", "domain_restricted_pages")
	cache.delete_value(domain_cache_keys)


def clear_global_cache():
	from netmanthan.website.utils import clear_website_cache

	clear_doctype_cache()
	clear_website_cache()
	netmanthan.cache().delete_value(global_cache_keys)
	netmanthan.cache().delete_value(bench_cache_keys)
	netmanthan.setup_module_map()


def clear_defaults_cache(user=None):
	if user:
		for p in [user] + common_default_keys:
			netmanthan.cache().hdel("defaults", p)
	elif netmanthan.flags.in_install != "netmanthan":
		netmanthan.cache().delete_key("defaults")


def clear_doctype_cache(doctype=None):
	from netmanthan.desk.notifications import delete_notification_count_for

	clear_controller_cache(doctype)

	cache = netmanthan.cache()

	for key in ("is_table", "doctype_modules", "document_cache"):
		cache.delete_value(key)

	netmanthan.local.document_cache = {}

	def clear_single(dt):
		for name in doctype_cache_keys:
			cache.hdel(name, dt)

	if doctype:
		clear_single(doctype)

		# clear all parent doctypes
		for dt in netmanthan.get_all(
			"DocField", "parent", dict(fieldtype=["in", netmanthan.model.table_fields], options=doctype)
		):
			clear_single(dt.parent)

		# clear all parent doctypes
		if not netmanthan.flags.in_install:
			for dt in netmanthan.get_all(
				"Custom Field", "dt", dict(fieldtype=["in", netmanthan.model.table_fields], options=doctype)
			):
				clear_single(dt.dt)

		# clear all notifications
		delete_notification_count_for(doctype)

	else:
		# clear all
		for name in doctype_cache_keys:
			cache.delete_value(name)


def clear_controller_cache(doctype=None):
	if not doctype:
		netmanthan.controllers.pop(netmanthan.local.site, None)
		return

	if site_controllers := netmanthan.controllers.get(netmanthan.local.site):
		site_controllers.pop(doctype, None)


def get_doctype_map(doctype, name, filters=None, order_by=None):
	return netmanthan.cache().hget(
		get_doctype_map_key(doctype),
		name,
		lambda: netmanthan.get_all(doctype, filters=filters, order_by=order_by, ignore_ddl=True),
	)


def clear_doctype_map(doctype, name):
	netmanthan.cache().hdel(netmanthan.scrub(doctype) + "_map", name)


def build_table_count_cache():
	if (
		netmanthan.flags.in_patch
		or netmanthan.flags.in_install
		or netmanthan.flags.in_migrate
		or netmanthan.flags.in_import
		or netmanthan.flags.in_setup_wizard
	):
		return

	_cache = netmanthan.cache()
	table_name = netmanthan.qb.Field("table_name").as_("name")
	table_rows = netmanthan.qb.Field("table_rows").as_("count")
	information_schema = netmanthan.qb.Schema("information_schema")

	data = (netmanthan.qb.from_(information_schema.tables).select(table_name, table_rows)).run(
		as_dict=True
	)
	counts = {d.get("name").replace("tab", "", 1): d.get("count", None) for d in data}
	_cache.set_value("information_schema:counts", counts)

	return counts


def build_domain_restriced_doctype_cache(*args, **kwargs):
	if (
		netmanthan.flags.in_patch
		or netmanthan.flags.in_install
		or netmanthan.flags.in_migrate
		or netmanthan.flags.in_import
		or netmanthan.flags.in_setup_wizard
	):
		return
	_cache = netmanthan.cache()
	active_domains = netmanthan.get_active_domains()
	doctypes = netmanthan.get_all("DocType", filters={"restrict_to_domain": ("IN", active_domains)})
	doctypes = [doc.name for doc in doctypes]
	_cache.set_value("domain_restricted_doctypes", doctypes)

	return doctypes


def build_domain_restriced_page_cache(*args, **kwargs):
	if (
		netmanthan.flags.in_patch
		or netmanthan.flags.in_install
		or netmanthan.flags.in_migrate
		or netmanthan.flags.in_import
		or netmanthan.flags.in_setup_wizard
	):
		return
	_cache = netmanthan.cache()
	active_domains = netmanthan.get_active_domains()
	pages = netmanthan.get_all("Page", filters={"restrict_to_domain": ("IN", active_domains)})
	pages = [page.name for page in pages]
	_cache.set_value("domain_restricted_pages", pages)

	return pages
