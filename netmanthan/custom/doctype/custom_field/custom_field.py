# Copyright (c) 2015, netmanthan Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import json

import netmanthan
from netmanthan import _
from netmanthan.model import core_doctypes_list
from netmanthan.model.docfield import supports_translation
from netmanthan.model.document import Document
from netmanthan.query_builder.functions import IfNull
from netmanthan.utils import cstr, random_string


class CustomField(Document):
	def autoname(self):
		self.set_fieldname()
		self.name = self.dt + "-" + self.fieldname

	def set_fieldname(self):
		restricted = (
			"name",
			"parent",
			"creation",
			"modified",
			"modified_by",
			"parentfield",
			"parenttype",
			"file_list",
			"flags",
			"docstatus",
		)
		if not self.fieldname:
			label = self.label
			if not label:
				if self.fieldtype in ["Section Break", "Column Break", "Tab Break"]:
					label = self.fieldtype + "_" + str(random_string(5))
				else:
					netmanthan.throw(_("Label is mandatory"))

			# remove special characters from fieldname
			self.fieldname = "".join(
				[c for c in cstr(label).replace(" ", "_") if c.isdigit() or c.isalpha() or c == "_"]
			)
			self.fieldname = f"custom_{self.fieldname}"

		# fieldnames should be lowercase
		self.fieldname = self.fieldname.lower()

		if self.fieldname in restricted:
			self.fieldname = self.fieldname + "1"

	def before_insert(self):
		self.set_fieldname()

	def validate(self):
		# these imports have been added to avoid cyclical import, should fix in future
		from netmanthan.core.doctype.doctype.doctype import check_fieldname_conflicts
		from netmanthan.custom.doctype.customize_form.customize_form import CustomizeForm

		# don't always get meta to improve performance
		# setting idx is just an improvement, not a requirement
		if self.is_new() or self.insert_after == "append":
			meta = netmanthan.get_meta(self.dt, cached=False)
			fieldnames = [df.fieldname for df in meta.get("fields")]

			if self.is_new() and self.fieldname in fieldnames:
				netmanthan.throw(
					_("A field with the name {0} already exists in {1}").format(
						netmanthan.bold(self.fieldname), self.dt
					)
				)

			if self.insert_after == "append":
				self.insert_after = fieldnames[-1]

			if self.insert_after and self.insert_after in fieldnames:
				self.idx = fieldnames.index(self.insert_after) + 1

		if (
			not self.is_virtual
			and (doc_before_save := self.get_doc_before_save())
			and (old_fieldtype := doc_before_save.fieldtype) != self.fieldtype
			and not CustomizeForm.allow_fieldtype_change(old_fieldtype, self.fieldtype)
		):
			netmanthan.throw(
				_("Fieldtype cannot be changed from {0} to {1}").format(old_fieldtype, self.fieldtype)
			)

		if not self.fieldname:
			netmanthan.throw(_("Fieldname not set for Custom Field"))

		if self.get("translatable", 0) and not supports_translation(self.fieldtype):
			self.translatable = 0

		check_fieldname_conflicts(self)

	def on_update(self):
		# validate field
		if not self.flags.ignore_validate:
			from netmanthan.core.doctype.doctype.doctype import validate_fields_for_doctype

			validate_fields_for_doctype(self.dt)

		# clear cache and update the schema
		if not netmanthan.flags.in_create_custom_fields:
			netmanthan.clear_cache(doctype=self.dt)
			netmanthan.db.updatedb(self.dt)

	def on_trash(self):
		# check if Admin owned field
		if self.owner == "Administrator" and netmanthan.session.user != "Administrator":
			netmanthan.throw(
				_(
					"Custom Field {0} is created by the Administrator and can only be deleted through the Administrator account."
				).format(netmanthan.bold(self.label))
			)

		# delete property setter entries
		netmanthan.db.delete("Property Setter", {"doc_type": self.dt, "field_name": self.fieldname})

		# update doctype layouts
		doctype_layouts = netmanthan.get_all(
			"DocType Layout", filters={"document_type": self.dt}, pluck="name"
		)

		for layout in doctype_layouts:
			layout_doc = netmanthan.get_doc("DocType Layout", layout)
			for field in layout_doc.fields:
				if field.fieldname == self.fieldname:
					layout_doc.remove(field)
					layout_doc.save()
					break

		netmanthan.clear_cache(doctype=self.dt)

	def validate_insert_after(self, meta):
		if not meta.get_field(self.insert_after):
			netmanthan.throw(
				_(
					"Insert After field '{0}' mentioned in Custom Field '{1}', with label '{2}', does not exist"
				).format(self.insert_after, self.name, self.label),
				netmanthan.DoesNotExistError,
			)

		if self.fieldname == self.insert_after:
			netmanthan.throw(_("Insert After cannot be set as {0}").format(meta.get_label(self.insert_after)))


@netmanthan.whitelist()
def get_fields_label(doctype=None):
	meta = netmanthan.get_meta(doctype)

	if doctype in core_doctypes_list:
		return netmanthan.msgprint(_("Custom Fields cannot be added to core DocTypes."))

	if meta.custom:
		return netmanthan.msgprint(_("Custom Fields can only be added to a standard DocType."))

	return [
		{"value": df.fieldname or "", "label": _(df.label or "")}
		for df in netmanthan.get_meta(doctype).get("fields")
	]


def create_custom_field_if_values_exist(doctype, df):
	df = netmanthan._dict(df)
	if df.fieldname in netmanthan.db.get_table_columns(doctype) and netmanthan.db.count(
		dt=doctype, filters=IfNull(df.fieldname, "") != ""
	):
		create_custom_field(doctype, df)


def create_custom_field(doctype, df, ignore_validate=False, is_system_generated=True):
	df = netmanthan._dict(df)
	if not df.fieldname and df.label:
		df.fieldname = netmanthan.scrub(df.label)
	if not netmanthan.db.get_value("Custom Field", {"dt": doctype, "fieldname": df.fieldname}):
		custom_field = netmanthan.get_doc(
			{
				"doctype": "Custom Field",
				"dt": doctype,
				"permlevel": 0,
				"fieldtype": "Data",
				"hidden": 0,
				"is_system_generated": is_system_generated,
			}
		)
		custom_field.update(df)
		custom_field.flags.ignore_validate = ignore_validate
		custom_field.insert()
		return custom_field


def create_custom_fields(custom_fields, ignore_validate=False, update=True):
	"""Add / update multiple custom fields

	:param custom_fields: example `{'Sales Invoice': [dict(fieldname='test')]}`"""

	try:
		netmanthan.flags.in_create_custom_fields = True
		doctypes_to_update = set()

		if netmanthan.flags.in_setup_wizard:
			ignore_validate = True

		for doctypes, fields in custom_fields.items():
			if isinstance(fields, dict):
				# only one field
				fields = [fields]

			if isinstance(doctypes, str):
				# only one doctype
				doctypes = (doctypes,)

			for doctype in doctypes:
				doctypes_to_update.add(doctype)

				for df in fields:
					field = netmanthan.db.get_value("Custom Field", {"dt": doctype, "fieldname": df["fieldname"]})
					if not field:
						try:
							df = df.copy()
							df["owner"] = "Administrator"
							create_custom_field(doctype, df, ignore_validate=ignore_validate)

						except netmanthan.exceptions.DuplicateEntryError:
							pass

					elif update:
						custom_field = netmanthan.get_doc("Custom Field", field)
						custom_field.flags.ignore_validate = ignore_validate
						custom_field.update(df)
						custom_field.save()

		for doctype in doctypes_to_update:
			netmanthan.clear_cache(doctype=doctype)
			netmanthan.db.updatedb(doctype)

	finally:
		netmanthan.flags.in_create_custom_fields = False


@netmanthan.whitelist()
def add_custom_field(doctype, df):
	df = json.loads(df)
	return create_custom_field(doctype, df)
