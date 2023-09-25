# Copyright (c) 2015, netmanthan Technologies and contributors
# License: MIT. See LICENSE

import json
import re

import netmanthan
from netmanthan import _
from netmanthan.model.document import Document


class Language(Document):
	def validate(self):
		validate_with_regex(self.language_code, "Language Code")

	def before_rename(self, old, new, merge=False):
		validate_with_regex(new, "Name")

	def on_update(self):
		netmanthan.cache().delete_value("languages_with_name")
		netmanthan.cache().delete_value("languages")


def validate_with_regex(name, label):
	pattern = re.compile("^[a-zA-Z]+[-_]*[a-zA-Z]+$")
	if not pattern.match(name):
		netmanthan.throw(
			_(
				"""{0} must begin and end with a letter and can only contain letters,
				hyphen or underscore."""
			).format(label)
		)


def export_languages_json():
	"""Export list of all languages"""
	languages = netmanthan.get_all("Language", fields=["name", "language_name"])
	languages = [{"name": d.language_name, "code": d.name} for d in languages]

	languages.sort(key=lambda a: a["code"])

	with open(netmanthan.get_app_path("netmanthan", "geo", "languages.json"), "w") as f:
		f.write(netmanthan.as_json(languages))


def sync_languages():
	"""Sync netmanthan/geo/languages.json with Language"""
	with open(netmanthan.get_app_path("netmanthan", "geo", "languages.json")) as f:
		data = json.loads(f.read())

	for l in data:
		if not netmanthan.db.exists("Language", l["code"]):
			netmanthan.get_doc(
				{
					"doctype": "Language",
					"language_code": l["code"],
					"language_name": l["name"],
					"enabled": 1,
				}
			).insert()


def update_language_names():
	"""Update netmanthan/geo/languages.json names (for use via patch)"""
	with open(netmanthan.get_app_path("netmanthan", "geo", "languages.json")) as f:
		data = json.loads(f.read())

	for l in data:
		netmanthan.db.set_value("Language", l["code"], "language_name", l["name"])
