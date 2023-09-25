# Copyright (c) 2021, netmanthan Technologies and contributors
# For license information, please see license.txt

import json
import os
import subprocess

import netmanthan
from netmanthan.desk.form.load import get_attachments
from netmanthan.model.document import Document
from netmanthan.model.sync import get_doc_files
from netmanthan.modules.import_file import import_doc, import_file_by_path
from netmanthan.utils import get_files_path


class PackageImport(Document):
	def validate(self):
		if self.activate:
			self.import_package()

	def import_package(self):
		attachment = get_attachments(self.doctype, self.name)

		if not attachment:
			netmanthan.throw(netmanthan._("Please attach the package"))

		attachment = attachment[0]

		# get package_name from file (package_name-0.0.0.tar.gz)
		package_name = attachment.file_name.split(".", 1)[0].rsplit("-", 1)[0]
		if not os.path.exists(netmanthan.get_site_path("packages")):
			os.makedirs(netmanthan.get_site_path("packages"))

		# extract
		subprocess.check_output(
			[
				"tar",
				"xzf",
				get_files_path(attachment.file_name, is_private=attachment.is_private),
				"-C",
				netmanthan.get_site_path("packages"),
			]
		)

		package_path = netmanthan.get_site_path("packages", package_name)

		# import Package
		with open(os.path.join(package_path, package_name + ".json")) as packagefile:
			doc_dict = json.loads(packagefile.read())

		netmanthan.flags.package = import_doc(doc_dict)

		# collect modules
		files = []
		log = []
		for module in os.listdir(package_path):
			module_path = os.path.join(package_path, module)
			if os.path.isdir(module_path):
				files = get_doc_files(files, module_path)

		# import files
		for file in files:
			import_file_by_path(file, force=self.force, ignore_version=True)
			log.append(f"Imported {file}")

		self.log = "\n".join(log)
