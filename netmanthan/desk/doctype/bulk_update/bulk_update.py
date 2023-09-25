# Copyright (c) 2015, netmanthan Technologies and contributors
# License: MIT. See LICENSE

import netmanthan
from netmanthan import _
from netmanthan.model.document import Document
from netmanthan.utils import cint


class BulkUpdate(Document):
	@netmanthan.whitelist()
	def bulk_update(self):
		self.check_permission("write")
		limit = self.limit if self.limit and cint(self.limit) < 500 else 500

		condition = ""
		if self.condition:
			if ";" in self.condition:
				netmanthan.throw(_("; not allowed in condition"))

			condition = f" where {self.condition}"

		docnames = netmanthan.db.sql_list(
			f"""select name from `tab{self.document_type}`{condition} limit {limit} offset 0"""
		)
		return submit_cancel_or_update_docs(
			self.document_type, docnames, "update", {self.field: self.update_value}
		)


@netmanthan.whitelist()
def submit_cancel_or_update_docs(doctype, docnames, action="submit", data=None):
	docnames = netmanthan.parse_json(docnames)

	if data:
		data = netmanthan.parse_json(data)

	failed = []

	for i, d in enumerate(docnames, 1):
		doc = netmanthan.get_doc(doctype, d)
		try:
			message = ""
			if action == "submit" and doc.docstatus.is_draft():
				doc.submit()
				message = _("Submitting {0}").format(doctype)
			elif action == "cancel" and doc.docstatus.is_submitted():
				doc.cancel()
				message = _("Cancelling {0}").format(doctype)
			elif action == "update" and not doc.docstatus.is_cancelled():
				doc.update(data)
				doc.save()
				message = _("Updating {0}").format(doctype)
			else:
				failed.append(d)
			netmanthan.db.commit()
			show_progress(docnames, message, i, d)

		except Exception:
			failed.append(d)
			netmanthan.db.rollback()

	return failed


def show_progress(docnames, message, i, description):
	n = len(docnames)
	if n >= 10:
		netmanthan.publish_progress(float(i) * 100 / n, title=message, description=description)
