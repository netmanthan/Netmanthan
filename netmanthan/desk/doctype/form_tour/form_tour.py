# Copyright (c) 2021, netmanthan Technologies and contributors
# License: MIT. See LICENSE

import json

import netmanthan
from netmanthan.model.document import Document
from netmanthan.modules.export_file import export_to_files


class FormTour(Document):
	def before_save(self):
		if self.is_standard and not self.module:
			if self.workspace_name:
				self.module = netmanthan.db.get_value("Workspace", self.workspace_name, "module")
			elif self.dashboard_name:
				dashboard_doctype = netmanthan.db.get_value("Dashboard", self.dashboard_name, "module")
				self.module = netmanthan.db.get_value("DocType", dashboard_doctype, "module")
			else:
				self.module = "Desk"
		if not self.ui_tour:
			meta = netmanthan.get_meta(self.reference_doctype)
			for step in self.steps:
				if step.is_table_field and step.parent_fieldname:
					parent_field_df = meta.get_field(step.parent_fieldname)
					step.child_doctype = parent_field_df.options
					field_df = netmanthan.get_meta(step.child_doctype).get_field(step.fieldname)
					step.label = field_df.label
					step.fieldtype = field_df.fieldtype
				else:
					field_df = meta.get_field(step.fieldname)
					step.label = field_df.label
					step.fieldtype = field_df.fieldtype

	def on_update(self):
		netmanthan.cache().delete_key("bootinfo")

		if netmanthan.conf.developer_mode and self.is_standard:
			export_to_files([["Form Tour", self.name]], self.module)

	def on_trash(self):
		netmanthan.cache().delete_key("bootinfo")


@netmanthan.whitelist()
def reset_tour(tour_name):
	for user in netmanthan.get_all("User"):
		user_doc = netmanthan.get_doc("User", user.name)
		onboarding_status = netmanthan.parse_json(user_doc.onboarding_status)
		onboarding_status.pop(tour_name, None)
		user_doc.onboarding_status = netmanthan.as_json(onboarding_status)
		user_doc.save()


@netmanthan.whitelist()
def update_user_status(value, step):
	from netmanthan.utils.telemetry import capture

	step = netmanthan.parse_json(step)
	tour = netmanthan.parse_json(value)

	capture(
		netmanthan.scrub(f"{step.parent}_{step.title}"),
		app="netmanthan_ui_tours",
		properties={"is_completed": tour.is_completed},
	)
	netmanthan.db.set_value(
		"User", netmanthan.session.user, "onboarding_status", value, update_modified=False
	)

	netmanthan.cache().hdel("bootinfo", netmanthan.session.user)


def get_onboarding_ui_tours():
	if not netmanthan.get_system_settings("enable_onboarding"):
		return []

	ui_tours = netmanthan.get_all("Form Tour", filters={"ui_tour": 1}, fields=["page_route", "name"])

	return [[tour.name, json.loads(tour.page_route)] for tour in ui_tours]
