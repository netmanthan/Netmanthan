# Copyright (c) 2020, netmanthan Technologies and contributors
# License: MIT. See LICENSE

import netmanthan
from netmanthan.model.document import Document


class ListViewSettings(Document):
	def on_update(self):
		netmanthan.clear_document_cache(self.doctype, self.name)


@netmanthan.whitelist()
def save_listview_settings(doctype, listview_settings, removed_listview_fields):

	listview_settings = netmanthan.parse_json(listview_settings)
	removed_listview_fields = netmanthan.parse_json(removed_listview_fields)

	if netmanthan.get_all("List View Settings", filters={"name": doctype}):
		doc = netmanthan.get_doc("List View Settings", doctype)
		doc.update(listview_settings)
		doc.save()
	else:
		doc = netmanthan.new_doc("List View Settings")
		doc.name = doctype
		doc.update(listview_settings)
		doc.insert()

	set_listview_fields(doctype, listview_settings.get("fields"), removed_listview_fields)

	return {"meta": netmanthan.get_meta(doctype, False), "listview_settings": doc}


def set_listview_fields(doctype, listview_fields, removed_listview_fields):
	meta = netmanthan.get_meta(doctype)

	listview_fields = [
		f.get("fieldname") for f in netmanthan.parse_json(listview_fields) if f.get("fieldname")
	]

	for field in removed_listview_fields:
		set_in_list_view_property(doctype, meta.get_field(field), "0")

	for field in listview_fields:
		set_in_list_view_property(doctype, meta.get_field(field), "1")


def set_in_list_view_property(doctype, field, value):
	if not field or field.fieldname == "status_field":
		return

	property_setter = netmanthan.db.get_value(
		"Property Setter",
		{"doc_type": doctype, "field_name": field.fieldname, "property": "in_list_view"},
	)
	if property_setter:
		doc = netmanthan.get_doc("Property Setter", property_setter)
		doc.value = value
		doc.save()
	else:
		netmanthan.make_property_setter(
			{
				"doctype": doctype,
				"doctype_or_field": "DocField",
				"fieldname": field.fieldname,
				"property": "in_list_view",
				"value": value,
				"property_type": "Check",
			},
			ignore_validate=True,
		)


@netmanthan.whitelist()
def get_default_listview_fields(doctype):
	meta = netmanthan.get_meta(doctype)
	path = netmanthan.get_module_path(
		netmanthan.scrub(meta.module), "doctype", netmanthan.scrub(meta.name), netmanthan.scrub(meta.name) + ".json"
	)
	doctype_json = netmanthan.get_file_json(path)

	fields = [f.get("fieldname") for f in doctype_json.get("fields") if f.get("in_list_view")]

	if meta.title_field:
		if not meta.title_field.strip() in fields:
			fields.append(meta.title_field.strip())

	return fields
