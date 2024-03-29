# Copyright (c) 2015, netmanthan Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import os

import netmanthan
from netmanthan.core.doctype.data_import.data_import import export_json, import_doc
from netmanthan.utils.deprecations import deprecation_warning


def sync_fixtures(app=None):
	"""Import, overwrite fixtures from `[app]/fixtures`"""
	if app:
		apps = [app]
	else:
		apps = netmanthan.get_installed_apps()

	netmanthan.flags.in_fixtures = True

	for app in apps:
		import_fixtures(app)
		import_custom_scripts(app)

	netmanthan.flags.in_fixtures = False


def import_fixtures(app):
	fixtures_path = netmanthan.get_app_path(app, "fixtures")
	if not os.path.exists(fixtures_path):
		return

	fixture_files = os.listdir(fixtures_path)

	for fname in fixture_files:
		if not fname.endswith(".json"):
			continue

		file_path = netmanthan.get_app_path(app, "fixtures", fname)
		try:
			import_doc(file_path)
		except (ImportError, netmanthan.DoesNotExistError) as e:
			# fixture syncing for missing doctypes
			print(f"Skipping fixture syncing from the file {fname}. Reason: {e}")


def import_custom_scripts(app):
	"""Import custom scripts from `[app]/fixtures/custom_scripts`"""
	scripts_folder = netmanthan.get_app_path(app, "fixtures", "custom_scripts")
	if not os.path.exists(scripts_folder):
		return

	for fname in os.listdir(scripts_folder):
		if not fname.endswith(".js"):
			continue

		doctype = fname.rsplit(".", 1)[0]
		if not netmanthan.db.exists("DocType", doctype):
			print(
				f"Skipping custom script fixture syncing for the missing doctype {doctype} from the file {fname}"
			)
			continue

		# not using get_app_path here as it scrubs the fname (will not work for dt name with > 1 word)
		file_path = scripts_folder + os.path.sep + fname
		deprecation_warning(
			f"Importing client script {fname} from {scripts_folder} is deprecated and will be removed in version-15. Use client scripts as fixtures directly."
		)

		with open(file_path) as f:
			script = f.read()
			if netmanthan.db.exists("Client Script", {"dt": doctype}):
				client_script = netmanthan.get_doc("Client Script", {"dt": doctype})
				client_script.script = script
				client_script.save()
			else:
				client_script = netmanthan.new_doc("Client Script")
				client_script.update({"__newname": doctype, "dt": doctype, "script": script})
				client_script.insert()


def export_fixtures(app=None):
	"""Export fixtures as JSON to `[app]/fixtures`"""
	if app:
		apps = [app]
	else:
		apps = netmanthan.get_installed_apps()
	for app in apps:
		for fixture in netmanthan.get_hooks("fixtures", app_name=app):
			filters = None
			or_filters = None
			if isinstance(fixture, dict):
				filters = fixture.get("filters")
				or_filters = fixture.get("or_filters")
				fixture = fixture.get("doctype") or fixture.get("dt")
			print(f"Exporting {fixture} app {app} filters {(filters if filters else or_filters)}")
			if not os.path.exists(netmanthan.get_app_path(app, "fixtures")):
				os.mkdir(netmanthan.get_app_path(app, "fixtures"))

			export_json(
				fixture,
				netmanthan.get_app_path(app, "fixtures", netmanthan.scrub(fixture) + ".json"),
				filters=filters,
				or_filters=or_filters,
				order_by="idx asc, creation asc",
			)
