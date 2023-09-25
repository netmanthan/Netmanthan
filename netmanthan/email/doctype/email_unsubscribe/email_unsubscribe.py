# Copyright (c) 2015, netmanthan Technologies Pvt. Ltd. and contributors
# License: MIT. See LICENSE

import netmanthan
from netmanthan import _
from netmanthan.model.document import Document


class EmailUnsubscribe(Document):
	def validate(self):
		if not self.global_unsubscribe and not (self.reference_doctype and self.reference_name):
			netmanthan.throw(_("Reference DocType and Reference Name are required"), netmanthan.MandatoryError)

		if not self.global_unsubscribe and netmanthan.db.get_value(
			self.doctype, self.name, "global_unsubscribe"
		):
			netmanthan.throw(_("Delete this record to allow sending to this email address"))

		if self.global_unsubscribe:
			if netmanthan.get_all(
				"Email Unsubscribe",
				filters={"email": self.email, "global_unsubscribe": 1, "name": ["!=", self.name]},
			):
				netmanthan.throw(_("{0} already unsubscribed").format(self.email), netmanthan.DuplicateEntryError)

		else:
			if netmanthan.get_all(
				"Email Unsubscribe",
				filters={
					"email": self.email,
					"reference_doctype": self.reference_doctype,
					"reference_name": self.reference_name,
					"name": ["!=", self.name],
				},
			):
				netmanthan.throw(
					_("{0} already unsubscribed for {1} {2}").format(
						self.email, self.reference_doctype, self.reference_name
					),
					netmanthan.DuplicateEntryError,
				)

	def on_update(self):
		if self.reference_doctype and self.reference_name:
			doc = netmanthan.get_doc(self.reference_doctype, self.reference_name)
			doc.add_comment("Label", _("Left this conversation"), comment_email=self.email)
