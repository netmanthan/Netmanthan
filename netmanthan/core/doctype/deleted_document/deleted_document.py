# Copyright (c) 2015, netmanthan Technologies and contributors
# License: MIT. See LICENSE

import json

import netmanthan
from netmanthan import _
from netmanthan.desk.doctype.bulk_update.bulk_update import show_progress
from netmanthan.model.document import Document
from netmanthan.model.workflow import get_workflow_name


class DeletedDocument(Document):
	pass


@netmanthan.whitelist()
def restore(name, alert=True):
	deleted = netmanthan.get_doc("Deleted Document", name)

	if deleted.restored:
		netmanthan.throw(_("Document {0} Already Restored").format(name), exc=netmanthan.DocumentAlreadyRestored)

	doc = netmanthan.get_doc(json.loads(deleted.data))

	try:
		doc.insert()
	except netmanthan.DocstatusTransitionError:
		netmanthan.msgprint(_("Cancelled Document restored as Draft"))
		doc.docstatus = 0
		active_workflow = get_workflow_name(doc.doctype)
		if active_workflow:
			workflow_state_fieldname = netmanthan.get_value("Workflow", active_workflow, "workflow_state_field")
			if doc.get(workflow_state_fieldname):
				doc.set(workflow_state_fieldname, None)
		doc.insert()

	doc.add_comment("Edit", _("restored {0} as {1}").format(deleted.deleted_name, doc.name))

	deleted.new_name = doc.name
	deleted.restored = 1
	deleted.db_update()

	if alert:
		netmanthan.msgprint(_("Document Restored"))


@netmanthan.whitelist()
def bulk_restore(docnames):
	docnames = netmanthan.parse_json(docnames)
	message = _("Restoring Deleted Document")
	restored, invalid, failed = [], [], []

	for i, d in enumerate(docnames):
		try:
			show_progress(docnames, message, i + 1, d)
			restore(d, alert=False)
			netmanthan.db.commit()
			restored.append(d)

		except netmanthan.DocumentAlreadyRestored:
			netmanthan.message_log.pop()
			invalid.append(d)

		except Exception:
			netmanthan.message_log.pop()
			failed.append(d)
			netmanthan.db.rollback()

	return {"restored": restored, "invalid": invalid, "failed": failed}
