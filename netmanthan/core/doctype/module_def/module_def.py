# Copyright (c) 2015, netmanthan Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import json
import os

import netmanthan
from netmanthan.model.document import Document
from netmanthan.modules.export_file import delete_folder


class ModuleDef(Document):
	def on_update(self):
		"""If in `developer_mode`, create folder for module and
		add in `modules.txt` of app if missing."""
		netmanthan.clear_cache()
		if not self.custom and netmanthan.conf.get("developer_mode"):
			self.create_modules_folder()
			self.add_to_modules_txt()

	def create_modules_folder(self):
		"""Creates a folder `[app]/[module]` and adds `__init__.py`"""
		module_path = netmanthan.get_app_path(self.app_name, self.name)
		if not os.path.exists(module_path):
			os.mkdir(module_path)
			with open(os.path.join(module_path, "__init__.py"), "w") as f:
				f.write("")

	def add_to_modules_txt(self):
		"""Adds to `[app]/modules.txt`"""
		modules = None
		if not netmanthan.local.module_app.get(netmanthan.scrub(self.name)):
			with open(netmanthan.get_app_path(self.app_name, "modules.txt")) as f:
				content = f.read()
				if not self.name in content.splitlines():
					modules = list(filter(None, content.splitlines()))
					modules.append(self.name)

			if modules:
				with open(netmanthan.get_app_path(self.app_name, "modules.txt"), "w") as f:
					f.write("\n".join(modules))

				netmanthan.clear_cache()
				netmanthan.setup_module_map()

	def on_trash(self):
		"""Delete module name from modules.txt"""

		if not netmanthan.conf.get("developer_mode") or netmanthan.flags.in_uninstall or self.custom:
			return

		modules = None
		if netmanthan.local.module_app.get(netmanthan.scrub(self.name)):
			delete_folder(self.module_name, "Module Def", self.name)
			with open(netmanthan.get_app_path(self.app_name, "modules.txt")) as f:
				content = f.read()
				if self.name in content.splitlines():
					modules = list(filter(None, content.splitlines()))
					modules.remove(self.name)

			if modules:
				with open(netmanthan.get_app_path(self.app_name, "modules.txt"), "w") as f:
					f.write("\n".join(modules))

				netmanthan.clear_cache()
				netmanthan.setup_module_map()


@netmanthan.whitelist()
def get_installed_apps():
	return json.dumps(netmanthan.get_installed_apps())
