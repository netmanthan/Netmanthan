# Copyright (c) 2015, netmanthan Technologies Pvt. Ltd. and contributors
# License: MIT. See LICENSE

import os
from contextlib import suppress

import redis

import netmanthan
from netmanthan.utils.data import cstr

redis_server = None


def publish_progress(percent, title=None, doctype=None, docname=None, description=None):
	publish_realtime(
		"progress",
		{"percent": percent, "title": title, "description": description},
		user=None if doctype and docname else netmanthan.session.user,
		doctype=doctype,
		docname=docname,
	)


def publish_realtime(
	event: str = None,
	message: dict = None,
	room: str = None,
	user: str = None,
	doctype: str = None,
	docname: str = None,
	task_id: str = None,
	after_commit: bool = False,
):
	"""Publish real-time updates

	:param event: Event name, like `task_progress` etc. that will be handled by the client (default is `task_progress` if within task or `global`)
	:param message: JSON message object. For async must contain `task_id`
	:param room: Room in which to publish update (default entire site)
	:param user: Transmit to user
	:param doctype: Transmit to doctype, docname
	:param docname: Transmit to doctype, docname
	:param after_commit: (default False) will emit after current transaction is committed"""
	if message is None:
		message = {}

	if event is None:
		event = "task_progress" if netmanthan.local.task_id else "global"
	elif event == "msgprint" and not user:
		user = netmanthan.session.user
	elif event == "list_update":
		doctype = doctype or message.get("doctype")
		room = get_doctype_room(doctype)
	elif event == "docinfo_update":
		room = get_doc_room(doctype, docname)

	if not task_id and hasattr(netmanthan.local, "task_id"):
		task_id = netmanthan.local.task_id

	if not room:
		if task_id:
			after_commit = False
			if "task_id" not in message:
				message["task_id"] = task_id
			room = get_task_progress_room(task_id)
		elif user:
			# transmit to specific user: System, Website or Guest
			room = get_user_room(user)
		elif doctype and docname:
			room = get_doc_room(doctype, docname)
		else:
			# This will be broadcasted to all Desk users
			room = get_site_room()

	if after_commit:
		params = [event, message, room]
		if params not in netmanthan.local.realtime_log:
			netmanthan.local.realtime_log.append(params)
	else:
		emit_via_redis(event, message, room)


def emit_via_redis(event, message, room):
	"""Publish real-time updates via redis

	:param event: Event name, like `task_progress` etc.
	:param message: JSON message object. For async must contain `task_id`
	:param room: name of the room"""

	with suppress(redis.exceptions.ConnectionError):
		r = get_redis_server()
		r.publish("events", netmanthan.as_json({"event": event, "message": message, "room": room}))


def get_redis_server():
	"""returns redis_socketio connection."""
	global redis_server
	if not redis_server:
		from redis import Redis

		redis_server = Redis.from_url(netmanthan.conf.redis_socketio or "redis://localhost:12311")
	return redis_server


@netmanthan.whitelist(allow_guest=True)
def can_subscribe_doc(doctype, docname):
	if os.environ.get("CI"):
		return True

	from netmanthan.exceptions import PermissionError

	if not netmanthan.has_permission(doctype=doctype, doc=docname, ptype="read"):
		raise PermissionError()

	return True


@netmanthan.whitelist(allow_guest=True)
def can_subscribe_doctype(doctype: str) -> bool:
	from netmanthan.exceptions import PermissionError

	if not netmanthan.has_permission(doctype=doctype, ptype="read"):
		raise PermissionError()

	return True


@netmanthan.whitelist(allow_guest=True)
def get_user_info():
	return {
		"user": netmanthan.session.user,
		"user_type": netmanthan.session.data.user_type,
	}


def get_doctype_room(doctype):
	return f"{netmanthan.local.site}:doctype:{doctype}"


def get_doc_room(doctype, docname):
	return f"{netmanthan.local.site}:doc:{doctype}/{cstr(docname)}"


def get_user_room(user):
	return f"{netmanthan.local.site}:user:{user}"


def get_site_room():
	return f"{netmanthan.local.site}:all"


def get_task_progress_room(task_id):
	return f"{netmanthan.local.site}:task_progress:{task_id}"


def get_website_room():
	return f"{netmanthan.local.site}:website"
