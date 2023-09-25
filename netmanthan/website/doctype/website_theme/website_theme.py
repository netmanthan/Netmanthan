# Copyright (c) 2015, netmanthan Technologies Pvt. Ltd. and contributors
# License: MIT. See LICENSE

from os.path import abspath
from os.path import exists as path_exists
from os.path import join as join_path
from os.path import splitext
from typing import Optional

import netmanthan
from netmanthan import _
from netmanthan.model.document import Document
from netmanthan.utils import get_path


class WebsiteTheme(Document):
	def validate(self):
		self.validate_if_customizable()
		self.generate_bootstrap_theme()

	def on_update(self):
		if (
			not self.custom
			and netmanthan.local.conf.get("developer_mode")
			and not (netmanthan.flags.in_import or netmanthan.flags.in_test)
		):

			self.export_doc()

		self.clear_cache_if_current_theme()

	def is_standard_and_not_valid_user(self):
		return (
			not self.custom
			and not netmanthan.local.conf.get("developer_mode")
			and not (netmanthan.flags.in_import or netmanthan.flags.in_test or netmanthan.flags.in_migrate)
		)

	def on_trash(self):
		if self.is_standard_and_not_valid_user():
			netmanthan.throw(
				_("You are not allowed to delete a standard Website Theme"), netmanthan.PermissionError
			)

	def validate_if_customizable(self):
		if self.is_standard_and_not_valid_user():
			netmanthan.throw(_("Please Duplicate this Website Theme to customize."))

	def export_doc(self):
		"""Export to standard folder `[module]/website_theme/[name]/[name].json`."""
		from netmanthan.modules.export_file import export_to_files

		export_to_files(record_list=[["Website Theme", self.name]], create_init=True)

	def clear_cache_if_current_theme(self):
		if netmanthan.flags.in_install == "netmanthan":
			return
		website_settings = netmanthan.get_doc("Website Settings", "Website Settings")
		if getattr(website_settings, "website_theme", None) == self.name:
			website_settings.clear_cache()

	def generate_bootstrap_theme(self):
		from subprocess import PIPE, Popen

		self.theme_scss = netmanthan.render_template(
			"netmanthan/website/doctype/website_theme/website_theme_template.scss", self.as_dict()
		)

		# create theme file in site public files folder
		folder_path = abspath(netmanthan.utils.get_files_path("website_theme", is_private=False))
		# create folder if not exist
		netmanthan.create_folder(folder_path)

		if self.custom:
			self.delete_old_theme_files(folder_path)

		# add a random suffix
		suffix = netmanthan.generate_hash(length=8) if self.custom else "style"
		file_name = netmanthan.scrub(self.name) + "_" + suffix + ".css"
		output_path = join_path(folder_path, file_name)

		self.theme_scss = content = get_scss(self)
		content = content.replace("\n", "\\n")
		command = ["node", "generate_bootstrap_theme.js", output_path, content]

		process = Popen(command, cwd=netmanthan.get_app_path("netmanthan", ".."), stdout=PIPE, stderr=PIPE)

		stderr = process.communicate()[1]

		if stderr:
			stderr = netmanthan.safe_decode(stderr)
			stderr = stderr.replace("\n", "<br>")
			netmanthan.throw(f'<div style="font-family: monospace;">{stderr}</div>')
		else:
			self.theme_url = "/files/website_theme/" + file_name

		netmanthan.msgprint(_("Compiled Successfully"), alert=True)

	def delete_old_theme_files(self, folder_path):
		import os

		for fname in os.listdir(folder_path):
			if fname.startswith(netmanthan.scrub(self.name) + "_") and fname.endswith(".css"):
				os.remove(os.path.join(folder_path, fname))

	@netmanthan.whitelist()
	def set_as_default(self):
		self.save()
		website_settings = netmanthan.get_doc("Website Settings")
		website_settings.website_theme = self.name
		website_settings.ignore_validate = True
		website_settings.save()

	@netmanthan.whitelist()
	def get_apps(self):
		from netmanthan.utils.change_log import get_versions

		apps = get_versions()
		out = []
		for app, values in apps.items():
			out.append({"name": app, "title": values["title"]})
		return out


def get_active_theme() -> Optional["WebsiteTheme"]:
	if website_theme := netmanthan.get_website_settings("website_theme"):
		try:
			return netmanthan.get_cached_doc("Website Theme", website_theme)
		except netmanthan.DoesNotExistError:
			netmanthan.clear_last_message()
			pass


def get_scss(website_theme):
	"""
	Render `website_theme_template.scss` with the values defined in Website Theme.

	params:
	website_theme - instance of a Website Theme
	"""
	apps_to_ignore = tuple((d.app + "/") for d in website_theme.ignored_apps)
	available_imports = get_scss_paths()
	imports_to_include = [d for d in available_imports if not d.startswith(apps_to_ignore)]
	context = website_theme.as_dict()
	context["website_theme_scss"] = imports_to_include
	return netmanthan.render_template(
		"netmanthan/website/doctype/website_theme/website_theme_template.scss", context
	)


def get_scss_paths():
	"""
	Return a set of SCSS import paths from all apps that provide `website.scss`.

	If `$BENCH_PATH/apps/netmanthan/netmanthan/public/scss/website[.bundle].scss` exists, the
	returned set will contain 'netmanthan/public/scss/website[.bundle]'.
	"""
	import_path_list = []
	bench_path = netmanthan.utils.get_bench_path()

	scss_files = ["public/scss/website.scss", "public/scss/website.bundle.scss"]
	for app in netmanthan.get_installed_apps():
		for scss_file in scss_files:
			relative_path = join_path(app, scss_file)
			full_path = get_path("apps", app, relative_path, base=bench_path)
			if path_exists(full_path):
				import_path = splitext(relative_path)[0]
				import_path_list.append(import_path)

	return import_path_list


def after_migrate():
	"""
	Regenerate Active Theme CSS file after migration.

	Necessary to reflect possible changes in the imported SCSS files. Called at
	the end of every `bench migrate`.
	"""
	website_theme = netmanthan.db.get_single_value("Website Settings", "website_theme")
	if not website_theme or website_theme == "Standard":
		return

	doc = netmanthan.get_doc("Website Theme", website_theme)
	doc.save()  # Just re-saving re-generates the theme.
