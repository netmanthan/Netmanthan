# Copyright (c) 2021, netmanthan Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE
"""
Boot session from cache or build

Session bootstraps info needed by common client side activities including
permission, homepage, default variables, system defaults etc
"""
import json
from urllib.parse import unquote

import redis

import netmanthan
import netmanthan.defaults
import netmanthan.model.meta
import netmanthan.translate
import netmanthan.utils
from netmanthan import _
from netmanthan.cache_manager import clear_user_cache
from netmanthan.query_builder import Order
from netmanthan.utils import cint, cstr, get_assets_json
from netmanthan.utils.data import add_to_date


@netmanthan.whitelist()
def clear():
	netmanthan.local.session_obj.update(force=True)
	netmanthan.local.db.commit()
	clear_user_cache(netmanthan.session.user)
	netmanthan.response["message"] = _("Cache Cleared")


def clear_sessions(user=None, keep_current=False, device=None, force=False):
	"""Clear other sessions of the current user. Called at login / logout

	:param user: user name (default: current user)
	:param keep_current: keep current session (default: false)
	:param device: delete sessions of this device (default: desktop, mobile)
	:param force: triggered by the user (default false)
	"""

	reason = "Logged In From Another Session"
	if force:
		reason = "Force Logged out by the user"

	for sid in get_sessions_to_clear(user, keep_current, device):
		delete_session(sid, reason=reason)


def get_sessions_to_clear(user=None, keep_current=False, device=None):
	"""Returns sessions of the current user. Called at login / logout

	:param user: user name (default: current user)
	:param keep_current: keep current session (default: false)
	:param device: delete sessions of this device (default: desktop, mobile)
	"""
	if not user:
		user = netmanthan.session.user

	if not device:
		device = ("desktop", "mobile")

	if not isinstance(device, (tuple, list)):
		device = (device,)

	offset = 0
	if user == netmanthan.session.user:
		simultaneous_sessions = netmanthan.db.get_value("User", user, "simultaneous_sessions") or 1
		offset = simultaneous_sessions - 1

	session = netmanthan.qb.DocType("Sessions")
	session_id = netmanthan.qb.from_(session).where(
		(session.user == user) & (session.device.isin(device))
	)
	if keep_current:
		session_id = session_id.where(session.sid != netmanthan.session.sid)

	query = (
		session_id.select(session.sid)
		.offset(offset)
		.limit(100)
		.orderby(session.lastupdate, order=Order.desc)
	)

	return query.run(pluck=True)


def delete_session(sid=None, user=None, reason="Session Expired"):
	from netmanthan.core.doctype.activity_log.feed import logout_feed

	if netmanthan.flags.read_only:
		# This isn't manually initated logout, most likely user's cookies were expired in such case
		# we should just ignore it till database is back up again.
		return

	netmanthan.cache().hdel("session", sid)
	netmanthan.cache().hdel("last_db_session_update", sid)
	if sid and not user:
		table = netmanthan.qb.DocType("Sessions")
		user_details = (
			netmanthan.qb.from_(table).where(table.sid == sid).select(table.user).run(as_dict=True)
		)
		if user_details:
			user = user_details[0].get("user")

	logout_feed(user, reason)
	netmanthan.db.delete("Sessions", {"sid": sid})
	netmanthan.db.commit()


def clear_all_sessions(reason=None):
	"""This effectively logs out all users"""
	netmanthan.only_for("Administrator")
	if not reason:
		reason = "Deleted All Active Session"
	for sid in netmanthan.qb.from_("Sessions").select("sid").run(pluck=True):
		delete_session(sid, reason=reason)


def get_expired_sessions():
	"""Returns list of expired sessions"""
	sessions = netmanthan.qb.DocType("Sessions")
	expired = []
	for device in ("desktop", "mobile"):
		expired.extend(
			(
				netmanthan.qb.from_(sessions)
				.select(sessions.sid)
				.where((sessions.lastupdate < get_expired_threshold(device)) & (sessions.device == device))
			).run(pluck=True)
		)

	return expired


def clear_expired_sessions():
	"""This function is meant to be called from scheduler"""
	for sid in get_expired_sessions():
		delete_session(sid, reason="Session Expired")


def get():
	"""get session boot info"""
	from netmanthan.boot import get_bootinfo, get_unseen_notes
	from netmanthan.utils.change_log import get_change_log

	bootinfo = None
	if not getattr(netmanthan.conf, "disable_session_cache", None):
		# check if cache exists
		bootinfo = netmanthan.cache().hget("bootinfo", netmanthan.session.user)
		if bootinfo:
			bootinfo["from_cache"] = 1
			bootinfo["user"]["recent"] = json.dumps(netmanthan.cache().hget("user_recent", netmanthan.session.user))

	if not bootinfo:
		# if not create it
		bootinfo = get_bootinfo()
		netmanthan.cache().hset("bootinfo", netmanthan.session.user, bootinfo)
		try:
			netmanthan.cache().ping()
		except redis.exceptions.ConnectionError:
			message = _("Redis cache server not running. Please contact Administrator / Tech support")
			if "messages" in bootinfo:
				bootinfo["messages"].append(message)
			else:
				bootinfo["messages"] = [message]

		# check only when clear cache is done, and don't cache this
		if netmanthan.local.request:
			bootinfo["change_log"] = get_change_log()

	bootinfo["metadata_version"] = netmanthan.cache().get_value("metadata_version")
	if not bootinfo["metadata_version"]:
		bootinfo["metadata_version"] = netmanthan.reset_metadata_version()

	bootinfo.notes = get_unseen_notes()
	bootinfo.assets_json = get_assets_json()
	bootinfo.read_only = bool(netmanthan.flags.read_only)

	for hook in netmanthan.get_hooks("extend_bootinfo"):
		netmanthan.get_attr(hook)(bootinfo=bootinfo)

	bootinfo["lang"] = netmanthan.translate.get_user_lang()
	bootinfo["disable_async"] = netmanthan.conf.disable_async

	bootinfo["setup_complete"] = cint(netmanthan.get_system_settings("setup_complete"))

	bootinfo["desk_theme"] = netmanthan.db.get_value("User", netmanthan.session.user, "desk_theme") or "Light"

	return bootinfo


@netmanthan.whitelist()
def get_boot_assets_json():
	return get_assets_json()


def get_csrf_token():
	if not netmanthan.local.session.data.csrf_token:
		generate_csrf_token()

	return netmanthan.local.session.data.csrf_token


def generate_csrf_token():
	netmanthan.local.session.data.csrf_token = netmanthan.generate_hash()
	if not netmanthan.flags.in_test:
		netmanthan.local.session_obj.update(force=True)


class Session:
	__slots__ = ("user", "device", "user_type", "full_name", "data", "time_diff", "sid")

	def __init__(self, user, resume=False, full_name=None, user_type=None):
		self.sid = cstr(
            netmanthan.form_dict.get("sid") or unquote(netmanthan.request.cookies.get("sid", "Guest"))
		)
		self.user = user
		self.device = netmanthan.form_dict.get("device") or "desktop"
		self.user_type = user_type
		self.full_name = full_name
		self.data = netmanthan._dict({"data": netmanthan._dict({})})
		self.time_diff = None

		# set local session
		netmanthan.local.session = self.data

		if resume:
			self.resume()

		else:
			if self.user:
				self.start()

	def start(self):
		"""start a new session"""
		# generate sid
		if self.user == "Guest":
			sid = "Guest"
		else:
			sid = netmanthan.generate_hash()

		self.data.user = self.user
		self.sid = self.data.sid = sid
		self.data.data.user = self.user
		self.data.data.session_ip = netmanthan.local.request_ip
		if self.user != "Guest":
			self.data.data.update(
				{
					"last_updated": netmanthan.utils.now(),
					"session_expiry": get_expiry_period(self.device),
					"full_name": self.full_name,
					"user_type": self.user_type,
					"device": self.device,
				}
			)

		# insert session
		if self.user != "Guest":
			self.insert_session_record()

			# update user
			user = netmanthan.get_doc("User", self.data["user"])
			user_doctype = netmanthan.qb.DocType("User")
			(
				netmanthan.qb.update(user_doctype)
				.set(user_doctype.last_login, netmanthan.utils.now())
				.set(user_doctype.last_ip, netmanthan.local.request_ip)
				.set(user_doctype.last_active, netmanthan.utils.now())
				.where(user_doctype.name == self.data["user"])
			).run()

			user.run_notifications("before_change")
			user.run_notifications("on_update")
			netmanthan.db.commit()

	def insert_session_record(self):
		Sessions = netmanthan.qb.DocType("Sessions")
		now = netmanthan.utils.now()

		(
			netmanthan.qb.into(Sessions)
			.columns(
				Sessions.sessiondata,
				Sessions.user,
				Sessions.lastupdate,
				Sessions.sid,
				Sessions.status,
				Sessions.device,
			)
			.insert(
				(str(self.data["data"]), self.data["user"], now, self.data["sid"], "Active", self.device)
			)
		).run()
		netmanthan.cache().hset("session", self.data.sid, self.data)

	def resume(self):
		"""non-login request: load a session"""
		import netmanthan
		from netmanthan.auth import validate_ip_address

		data = self.get_session_record()

		if data:
			self.data.update({"data": data, "user": data.user, "sid": self.sid})
			self.user = data.user
			validate_ip_address(self.user)
			self.device = data.device
		else:
			self.start_as_guest()

		if self.sid != "Guest":
			netmanthan.local.user_lang = netmanthan.translate.get_user_lang(self.data.user)
			netmanthan.local.lang = netmanthan.local.user_lang

	def get_session_record(self):
		"""get session record, or return the standard Guest Record"""
		from netmanthan.auth import clear_cookies

		r = self.get_session_data()

		if not r:
			netmanthan.response["session_expired"] = 1
			clear_cookies()
			self.sid = "Guest"
			r = self.get_session_data()

		return r

	def get_session_data(self):
		if self.sid == "Guest":
			return netmanthan._dict({"user": "Guest"})

		data = self.get_session_data_from_cache()
		if not data:
			data = self.get_session_data_from_db()
		return data

	def get_session_data_from_cache(self):
		data = netmanthan.cache().hget("session", self.sid)
		if data:
			data = netmanthan._dict(data)
			session_data = data.get("data", {})

			# set user for correct timezone
			self.time_diff = netmanthan.utils.time_diff_in_seconds(
				netmanthan.utils.now(), session_data.get("last_updated")
			)
			expiry = get_expiry_in_seconds(session_data.get("session_expiry"))

			if self.time_diff > expiry:
				self._delete_session()
				data = None

		return data and data.data

	def get_session_data_from_db(self):
		sessions = netmanthan.qb.DocType("Sessions")

		self.device = (
                netmanthan.db.get_value(
				sessions,
				filters=sessions.sid == self.sid,
				fieldname="device",
				order_by=None,
			)
                or "desktop"
		)

		record = (
			netmanthan.qb.from_(sessions)
			.select(sessions.user, sessions.sessiondata)
			.where(sessions.sid == self.sid)
			.where(sessions.lastupdate > get_expired_threshold(self.device))
		).run()

		if record:
			data = netmanthan._dict(netmanthan.safe_eval(record and record[0][1] or "{}"))
			data.user = record[0][0]
		else:
			self._delete_session()
			data = None

		return data

	def _delete_session(self):
		delete_session(self.sid, reason="Session Expired")

	def start_as_guest(self):
		"""all guests share the same 'Guest' session"""
		self.user = "Guest"
		self.start()

	def update(self, force=False):
		"""extend session expiry"""
		if netmanthan.session["user"] == "Guest" or netmanthan.form_dict.cmd == "logout":
			return

		now = netmanthan.utils.now()

		Sessions = netmanthan.qb.DocType("Sessions")

		self.data["data"]["last_updated"] = now
		self.data["data"]["lang"] = str(netmanthan.lang)

		# update session in db
		last_updated = netmanthan.cache().hget("last_db_session_update", self.sid)
		time_diff = netmanthan.utils.time_diff_in_seconds(now, last_updated) if last_updated else None

		# database persistence is secondary, don't update it too often
		updated_in_db = False
		if (force or (time_diff is None) or (time_diff > 600)) and not netmanthan.flags.read_only:
			# update sessions table
			(
				netmanthan.qb.update(Sessions)
				.where(Sessions.sid == self.data["sid"])
				.set(Sessions.sessiondata, str(self.data["data"]))
				.set(Sessions.lastupdate, now)
			).run()

			netmanthan.db.set_value("User", netmanthan.session.user, "last_active", now, update_modified=False)

			netmanthan.db.commit()
			netmanthan.cache().hset("last_db_session_update", self.sid, now)

			updated_in_db = True

		netmanthan.cache().hset("session", self.sid, self.data)

		return updated_in_db


def get_expiry_period_for_query(device=None):
	if netmanthan.db.db_type == "postgres":
		return get_expiry_period(device)
	else:
		return get_expiry_in_seconds(device=device)


def get_expiry_in_seconds(expiry=None, device=None):
	if not expiry:
		expiry = get_expiry_period(device)
	parts = expiry.split(":")
	return (cint(parts[0]) * 3600) + (cint(parts[1]) * 60) + cint(parts[2])


def get_expired_threshold(device):
	"""Get cutoff time before which all sessions are considered expired."""

	now = netmanthan.utils.now()
	expiry_in_seconds = get_expiry_in_seconds(device=device)

	return add_to_date(now, seconds=-expiry_in_seconds, as_string=True)


def get_expiry_period(device="desktop"):
	if device == "mobile":
		key = "session_expiry_mobile"
		default = "720:00:00"
	else:
		key = "session_expiry"
		default = "06:00:00"

	exp_sec = netmanthan.defaults.get_global_default(key) or default

	# incase seconds is missing
	if len(exp_sec.split(":")) == 2:
		exp_sec = exp_sec + ":00"

	return exp_sec


def get_geo_from_ip(ip_addr):
	try:
		from geolite2 import geolite2

		with geolite2 as f:
			reader = f.reader()
			data = reader.get(ip_addr)

			return netmanthan._dict(data)
	except ImportError:
		return
	except ValueError:
		return
	except TypeError:
		return


def get_geo_ip_country(ip_addr):
	match = get_geo_from_ip(ip_addr)
	if match:
		return match.country
