# Copyright (c) 2015, netmanthan Technologies and contributors
# License: MIT. See LICENSE

import json

import netmanthan
from netmanthan.model.document import Document
from netmanthan.translate import MERGED_TRANSLATION_KEY, USER_TRANSLATION_KEY, get_translator_url
from netmanthan.utils import is_html, strip_html_tags


class Translation(Document):
	def validate(self):
		if is_html(self.source_text):
			self.remove_html_from_source()

	def remove_html_from_source(self):
		self.source_text = strip_html_tags(self.source_text).strip()

	def on_update(self):
		clear_user_translation_cache(self.language)

	def on_trash(self):
		clear_user_translation_cache(self.language)

	def contribute(self):
		pass

	def get_contribution_status(self):
		pass


@netmanthan.whitelist()
def create_translations(translation_map, language):
	translation_map = json.loads(translation_map)
	translation_map_to_send = netmanthan._dict({})
	# first create / update local user translations
	for source_id, translation_dict in translation_map.items():
		translation_dict = netmanthan._dict(translation_dict)
		existing_doc_name = netmanthan.get_all(
			"Translation",
			{
				"source_text": translation_dict.source_text,
				"context": translation_dict.context or "",
				"language": language,
			},
		)
		translation_map_to_send[source_id] = translation_dict
		if existing_doc_name:
			netmanthan.db.set_value(
				"Translation",
				existing_doc_name[0].name,
				{
					"translated_text": translation_dict.translated_text,
					"contributed": 1,
					"contribution_status": "Pending",
				},
			)
			translation_map_to_send[source_id].name = existing_doc_name[0].name
		else:
			doc = netmanthan.get_doc(
				{
					"doctype": "Translation",
					"source_text": translation_dict.source_text,
					"contributed": 1,
					"contribution_status": "Pending",
					"translated_text": translation_dict.translated_text,
					"context": translation_dict.context,
					"language": language,
				}
			)
			doc.insert()
			translation_map_to_send[source_id].name = doc.name


def clear_user_translation_cache(lang):
	netmanthan.cache().hdel(USER_TRANSLATION_KEY, lang)
	netmanthan.cache().hdel(MERGED_TRANSLATION_KEY, lang)
