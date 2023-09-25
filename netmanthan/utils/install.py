# Copyright (c) 2015, netmanthan Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE
import getpass

import netmanthan
from netmanthan.utils.password import update_password


def before_install():
	netmanthan.reload_doc("core", "doctype", "doctype_state")
	netmanthan.reload_doc("core", "doctype", "docfield")
	netmanthan.reload_doc("core", "doctype", "docperm")
	netmanthan.reload_doc("core", "doctype", "doctype_action")
	netmanthan.reload_doc("core", "doctype", "doctype_link")
	netmanthan.reload_doc("desk", "doctype", "form_tour_step")
	netmanthan.reload_doc("desk", "doctype", "form_tour")
	netmanthan.reload_doc("core", "doctype", "doctype")


def after_install():
	create_user_type()
	install_basic_docs()

	from netmanthan.core.doctype.file.utils import make_home_folder

	make_home_folder()

	import_country_and_currency()

	from netmanthan.core.doctype.language.language import sync_languages

	sync_languages()

	# save default print setting
	print_settings = netmanthan.get_doc("Print Settings")
	print_settings.save()

	# all roles to admin
	netmanthan.get_doc("User", "Administrator").add_roles(*netmanthan.get_all("Role", pluck="name"))

	# update admin password
	update_password("Administrator", get_admin_password())

	if not netmanthan.conf.skip_setup_wizard:
		# only set home_page if the value doesn't exist in the db
		if not netmanthan.db.get_default("desktop:home_page"):
			netmanthan.db.set_default("desktop:home_page", "setup-wizard")
			netmanthan.db.set_single_value("System Settings", "setup_complete", 0)

	# clear test log
	with open(netmanthan.get_site_path(".test_log"), "w") as f:
		f.write("")

	add_standard_navbar_items()

	netmanthan.db.commit()


def create_user_type():
	for user_type in ["System User", "Website User"]:
		if not netmanthan.db.exists("User Type", user_type):
			netmanthan.get_doc({"doctype": "User Type", "name": user_type, "is_standard": 1}).insert(
				ignore_permissions=True
			)


def install_basic_docs():
	# core users / roles
	install_docs = [
		{
			"doctype": "User",
			"name": "Administrator",
			"first_name": "Administrator",
			"email": "admin@example.com",
			"enabled": 1,
			"is_admin": 1,
			"roles": [{"role": "Administrator"}],
			"thread_notify": 0,
			"send_me_a_copy": 0,
		},
		{
			"doctype": "User",
			"name": "Guest",
			"first_name": "Guest",
			"email": "guest@example.com",
			"enabled": 1,
			"is_guest": 1,
			"roles": [{"role": "Guest"}],
			"thread_notify": 0,
			"send_me_a_copy": 0,
		},
		{"doctype": "Role", "role_name": "Report Manager"},
		{"doctype": "Role", "role_name": "Translator"},
		{
			"doctype": "Workflow State",
			"workflow_state_name": "Pending",
			"icon": "question-sign",
			"style": "",
		},
		{
			"doctype": "Workflow State",
			"workflow_state_name": "Approved",
			"icon": "ok-sign",
			"style": "Success",
		},
		{
			"doctype": "Workflow State",
			"workflow_state_name": "Rejected",
			"icon": "remove",
			"style": "Danger",
		},
		{"doctype": "Workflow Action Master", "workflow_action_name": "Approve"},
		{"doctype": "Workflow Action Master", "workflow_action_name": "Reject"},
		{"doctype": "Workflow Action Master", "workflow_action_name": "Review"},
		{
			"doctype": "Email Domain",
			"domain_name": "example.com",
			"email_id": "account@example.com",
			"password": "pass",
			"email_server": "imap.example.com",
			"use_imap": 1,
			"smtp_server": "smtp.example.com",
		},
		{
			"doctype": "Email Account",
			"domain": "example.com",
			"email_id": "notifications@example.com",
			"default_outgoing": 1,
		},
		{
			"doctype": "Email Account",
			"domain": "example.com",
			"email_id": "replies@example.com",
			"default_incoming": 1,
		},
	]

	for d in install_docs:
		try:
			netmanthan.get_doc(d).insert(ignore_if_duplicate=True)
		except netmanthan.NameError:
			pass


def get_admin_password():
	def ask_admin_password():
		admin_password = getpass.getpass("Set Administrator password: ")
		admin_password2 = getpass.getpass("Re-enter Administrator password: ")
		if not admin_password == admin_password2:
			print("\nPasswords do not match")
			return ask_admin_password()
		return admin_password

	admin_password = netmanthan.conf.get("admin_password")
	if not admin_password:
		return ask_admin_password()
	return admin_password


def before_tests():
	if len(netmanthan.get_installed_apps()) > 1:
		# don't run before tests if any other app is installed
		return

	netmanthan.db.truncate("Custom Field")
	netmanthan.db.truncate("Event")

	netmanthan.clear_cache()

	# complete setup if missing
	if not int(netmanthan.db.get_single_value("System Settings", "setup_complete") or 0):
		complete_setup_wizard()

	netmanthan.db.set_single_value("Website Settings", "disable_signup", 0)
	netmanthan.db.commit()
	netmanthan.clear_cache()


def complete_setup_wizard():
	from netmanthan.desk.page.setup_wizard.setup_wizard import setup_complete

	setup_complete(
		{
			"language": "English",
			"email": "test@erpnext.com",
			"full_name": "Test User",
			"password": "test",
			"country": "United States",
			"timezone": "America/New_York",
			"currency": "USD",
		}
	)


def import_country_and_currency():
	from netmanthan.geo.country_info import get_all
	from netmanthan.utils import update_progress_bar

	data = get_all()

	for i, name in enumerate(data):
		update_progress_bar("Updating country info", i, len(data))
		country = netmanthan._dict(data[name])
		add_country_and_currency(name, country)

	print("")

	# enable frequently used currencies
	for currency in ("INR", "USD", "GBP", "EUR", "AED", "AUD", "JPY", "CNY", "CHF"):
		netmanthan.db.set_value("Currency", currency, "enabled", 1)


def add_country_and_currency(name, country):
	if not netmanthan.db.exists("Country", name):
		netmanthan.get_doc(
			{
				"doctype": "Country",
				"country_name": name,
				"code": country.code,
				"date_format": country.date_format or "dd-mm-yyyy",
				"time_format": country.time_format or "HH:mm:ss",
				"time_zones": "\n".join(country.timezones or []),
				"docstatus": 0,
			}
		).db_insert()

	if country.currency and not netmanthan.db.exists("Currency", country.currency):
		netmanthan.get_doc(
			{
				"doctype": "Currency",
				"currency_name": country.currency,
				"fraction": country.currency_fraction,
				"symbol": country.currency_symbol,
				"fraction_units": country.currency_fraction_units,
				"smallest_currency_fraction_value": country.smallest_currency_fraction_value,
				"number_format": country.number_format,
				"docstatus": 0,
			}
		).db_insert()


def add_standard_navbar_items():
	navbar_settings = netmanthan.get_single("Navbar Settings")

	# don't add settings/help options if they're already present
	if navbar_settings.settings_dropdown and navbar_settings.help_dropdown:
		return

	standard_navbar_items = [
		{
			"item_label": "My Profile",
			"item_type": "Route",
			"route": "/app/user-profile",
			"is_standard": 1,
		},
		{
			"item_label": "My Settings",
			"item_type": "Action",
			"action": "netmanthan.ui.toolbar.route_to_user()",
			"is_standard": 1,
		},
		{
			"item_label": "Session Defaults",
			"item_type": "Action",
			"action": "netmanthan.ui.toolbar.setup_session_defaults()",
			"is_standard": 1,
		},
		{
			"item_label": "Reload",
			"item_type": "Action",
			"action": "netmanthan.ui.toolbar.clear_cache()",
			"is_standard": 1,
		},
		{
			"item_label": "View Website",
			"item_type": "Action",
			"action": "netmanthan.ui.toolbar.view_website()",
			"is_standard": 1,
		},
		{
			"item_label": "Toggle Full Width",
			"item_type": "Action",
			"action": "netmanthan.ui.toolbar.toggle_full_width()",
			"is_standard": 1,
		},
		{
			"item_label": "Toggle Theme",
			"item_type": "Action",
			"action": "new netmanthan.ui.ThemeSwitcher().show()",
			"is_standard": 1,
		},
		{
			"item_type": "Separator",
			"is_standard": 1,
			"item_label": "",
		},
		{
			"item_label": "Log out",
			"item_type": "Action",
			"action": "netmanthan.app.logout()",
			"is_standard": 1,
		},
	]

	standard_help_items = [
		{
			"item_label": "About",
			"item_type": "Action",
			"action": "netmanthan.ui.toolbar.show_about()",
			"is_standard": 1,
		},
		{
			"item_label": "Keyboard Shortcuts",
			"item_type": "Action",
			"action": "netmanthan.ui.toolbar.show_shortcuts(event)",
			"is_standard": 1,
		},
		{
			"item_label": "netmanthan Support",
			"item_type": "Route",
			"route": "https://netmanthan.io/support",
			"is_standard": 1,
		},
	]

	navbar_settings.settings_dropdown = []
	navbar_settings.help_dropdown = []

	for item in standard_navbar_items:
		navbar_settings.append("settings_dropdown", item)

	for item in standard_help_items:
		navbar_settings.append("help_dropdown", item)

	navbar_settings.save()
