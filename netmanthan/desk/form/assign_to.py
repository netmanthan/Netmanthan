# Copyright (c) 2015, netmanthan Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

"""assign/unassign to ToDo"""

import json

import netmanthan
import netmanthan.share
import netmanthan.utils
from netmanthan import _
from netmanthan.desk.doctype.notification_log.notification_log import (
	enqueue_create_notification,
	get_title,
	get_title_html,
)
from netmanthan.desk.form.document_follow import follow_document


class DuplicateToDoError(netmanthan.ValidationError):
	pass


def get(args=None):
	"""get assigned to"""
	if not args:
		args = netmanthan.local.form_dict

	return netmanthan.get_all(
		"ToDo",
		fields=["allocated_to as owner", "name"],
		filters={
			"reference_type": args.get("doctype"),
			"reference_name": args.get("name"),
			"status": ("not in", ("Cancelled", "Closed")),
		},
		limit=5,
	)


@netmanthan.whitelist()
def add(args=None):
	"""add in someone's to do list
	args = {
	        "assign_to": [],
	        "doctype": ,
	        "name": ,
	        "description": ,
	        "assignment_rule":
	}

	"""
	if not args:
		args = netmanthan.local.form_dict

	users_with_duplicate_todo = []
	shared_with_users = []

	for assign_to in netmanthan.parse_json(args.get("assign_to")):
		filters = {
			"reference_type": args["doctype"],
			"reference_name": args["name"],
			"status": "Open",
			"allocated_to": assign_to,
		}

		if netmanthan.get_all("ToDo", filters=filters):
			users_with_duplicate_todo.append(assign_to)
		else:
			from netmanthan.utils import nowdate

			if not args.get("description"):
				args["description"] = _("Assignment for {0} {1}").format(args["doctype"], args["name"])

			d = netmanthan.get_doc(
				{
					"doctype": "ToDo",
					"allocated_to": assign_to,
					"reference_type": args["doctype"],
					"reference_name": args["name"],
					"description": args.get("description"),
					"priority": args.get("priority", "Medium"),
					"status": "Open",
					"date": args.get("date", nowdate()),
					"assigned_by": args.get("assigned_by", netmanthan.session.user),
					"assignment_rule": args.get("assignment_rule"),
				}
			).insert(ignore_permissions=True)

			# set assigned_to if field exists
			if netmanthan.get_meta(args["doctype"]).get_field("assigned_to"):
				netmanthan.db.set_value(args["doctype"], args["name"], "assigned_to", assign_to)

			doc = netmanthan.get_doc(args["doctype"], args["name"])

			# if assignee does not have permissions, share or inform
			if not netmanthan.has_permission(doc=doc, user=assign_to):
				if netmanthan.get_system_settings("disable_document_sharing"):
					msg = _("User {0} is not permitted to access this document.").format(netmanthan.bold(assign_to))
					msg += "<br>" + _(
						"As document sharing is disabled, please give them the required permissions before assigning."
					)
					netmanthan.throw(msg, title=_("Missing Permission"))
				else:
					netmanthan.share.add(doc.doctype, doc.name, assign_to)
					shared_with_users.append(assign_to)

			# make this document followed by assigned user
			if netmanthan.get_cached_value("User", assign_to, "follow_assigned_documents"):
				follow_document(args["doctype"], args["name"], assign_to)

			# notify
			notify_assignment(
				d.assigned_by,
				d.allocated_to,
				d.reference_type,
				d.reference_name,
				action="ASSIGN",
				description=args.get("description"),
			)

	if shared_with_users:
		user_list = format_message_for_assign_to(shared_with_users)
		netmanthan.msgprint(
			_("Shared with the following Users with Read access:{0}").format(user_list, alert=True)
		)

	if users_with_duplicate_todo:
		user_list = format_message_for_assign_to(users_with_duplicate_todo)
		netmanthan.msgprint(_("Already in the following Users ToDo list:{0}").format(user_list, alert=True))

	return get(args)


@netmanthan.whitelist()
def add_multiple(args=None):
	if not args:
		args = netmanthan.local.form_dict

	docname_list = json.loads(args["name"])

	for docname in docname_list:
		args.update({"name": docname})
		add(args)


def close_all_assignments(doctype, name):
	assignments = netmanthan.get_all(
		"ToDo",
		fields=["allocated_to", "name"],
		filters=dict(reference_type=doctype, reference_name=name, status=("!=", "Cancelled")),
	)
	if not assignments:
		return False

	for assign_to in assignments:
		set_status(doctype, name, todo=assign_to.name, assign_to=assign_to.allocated_to, status="Closed")

	return True


@netmanthan.whitelist()
def remove(doctype, name, assign_to):
	return set_status(doctype, name, "", assign_to, status="Cancelled")


@netmanthan.whitelist()
def close(doctype: str, name: str, assign_to: str):
	if assign_to != netmanthan.session.user:
		netmanthan.throw(_("Only the assignee can complete this to-do."))

	return set_status(doctype, name, "", assign_to, status="Closed")


def set_status(doctype, name, todo=None, assign_to=None, status="Cancelled"):
	"""remove from todo"""
	try:
		if not todo:
			todo = netmanthan.db.get_value(
				"ToDo",
				{
					"reference_type": doctype,
					"reference_name": name,
					"allocated_to": assign_to,
					"status": ("!=", status),
				},
			)
		if todo:
			todo = netmanthan.get_doc("ToDo", todo)
			todo.status = status
			todo.save(ignore_permissions=True)

			notify_assignment(todo.assigned_by, todo.allocated_to, todo.reference_type, todo.reference_name)
	except netmanthan.DoesNotExistError:
		pass

	# clear assigned_to if field exists
	if netmanthan.get_meta(doctype).get_field("assigned_to") and status in ("Cancelled", "Closed"):
		netmanthan.db.set_value(doctype, name, "assigned_to", None)

	return get({"doctype": doctype, "name": name})


def clear(doctype, name):
	"""
	Clears assignments, return False if not assigned.
	"""
	assignments = netmanthan.get_all(
		"ToDo",
		fields=["allocated_to", "name"],
		filters=dict(reference_type=doctype, reference_name=name),
	)
	if not assignments:
		return False

	for assign_to in assignments:
		set_status(
			doctype, name, todo=assign_to.name, assign_to=assign_to.allocated_to, status="Cancelled"
		)

	return True


def notify_assignment(
	assigned_by, allocated_to, doc_type, doc_name, action="CLOSE", description=None
):
	"""
	Notify assignee that there is a change in assignment
	"""
	if not (assigned_by and allocated_to and doc_type and doc_name):
		return

	# return if self assigned or user disabled
	if assigned_by == allocated_to or not netmanthan.db.get_value("User", allocated_to, "enabled"):
		return

	# Search for email address in description -- i.e. assignee
	user_name = netmanthan.get_cached_value("User", netmanthan.session.user, "full_name")
	title = get_title(doc_type, doc_name)
	description_html = f"<div>{description}</div>" if description else None

	if action == "CLOSE":
		subject = _("Your assignment on {0} {1} has been removed by {2}").format(
			netmanthan.bold(_(doc_type)), get_title_html(title), netmanthan.bold(user_name)
		)
	else:
		user_name = netmanthan.bold(user_name)
		document_type = netmanthan.bold(_(doc_type))
		title = get_title_html(title)
		subject = _("{0} assigned a new task {1} {2} to you").format(user_name, document_type, title)

	notification_doc = {
		"type": "Assignment",
		"document_type": doc_type,
		"subject": subject,
		"document_name": doc_name,
		"from_user": netmanthan.session.user,
		"email_content": description_html,
	}

	enqueue_create_notification(allocated_to, notification_doc)


def format_message_for_assign_to(users):
	return "<br><br>" + "<br>".join(users)
