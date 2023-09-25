# Copyright (c) 2021, netmanthan Technologies and contributors
# For license information, please see license.txt

import os

import netmanthan
from netmanthan.model.document import Document

LICENSES = (
	"GNU Affero General Public License",
	"GNU General Public License",
	"MIT License",
)


class Package(Document):
	def validate(self):
		if not self.package_name:
			self.package_name = self.name.lower().replace(" ", "-")


@netmanthan.whitelist()
def get_license_text(license_type: str) -> str | None:
	if license_type in LICENSES:
		with open(os.path.join(os.path.dirname(__file__), "licenses", license_type + ".md")) as textfile:
			return textfile.read()
