# Copyright (c) 2015, netmanthan Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import netmanthan
from netmanthan import _
from netmanthan.model import no_value_fields
from netmanthan.model.document import Document
from netmanthan.utils import cint, today


class SystemSettings(Document):
	def validate(self):
		from netmanthan.twofactor import toggle_two_factor_auth

		enable_password_policy = cint(self.enable_password_policy) and True or False
		minimum_password_score = cint(getattr(self, "minimum_password_score", 0)) or 0
		if enable_password_policy and minimum_password_score <= 0:
			netmanthan.throw(_("Please select Minimum Password Score"))
		elif not enable_password_policy:
			self.minimum_password_score = ""

		for key in ("session_expiry", "session_expiry_mobile"):
			if self.get(key):
				parts = self.get(key).split(":")
				if len(parts) != 2 or not (cint(parts[0]) or cint(parts[1])):
					netmanthan.throw(_("Session Expiry must be in format {0}").format("hh:mm"))

		if self.enable_two_factor_auth:
			if self.two_factor_method == "SMS":
				if not netmanthan.db.get_single_value("SMS Settings", "sms_gateway_url"):
					netmanthan.throw(
						_("Please setup SMS before setting it as an authentication method, via SMS Settings")
					)
			toggle_two_factor_auth(True, roles=["All"])
		else:
			self.bypass_2fa_for_retricted_ip_users = 0
			self.bypass_restrict_ip_check_if_2fa_enabled = 0

		netmanthan.flags.update_last_reset_password_date = False
		if self.force_user_to_reset_password and not cint(
			netmanthan.db.get_single_value("System Settings", "force_user_to_reset_password")
		):
			netmanthan.flags.update_last_reset_password_date = True

		self.validate_user_pass_login()
		self.validate_backup_limit()

	def validate_user_pass_login(self):
		if not self.disable_user_pass_login:
			return

		social_login_enabled = netmanthan.db.exists("Social Login Key", {"enable_social_login": 1})
		ldap_enabled = netmanthan.db.get_single_value("LDAP Settings", "enabled")

		if not (social_login_enabled or ldap_enabled):
			netmanthan.throw(
				_(
					"Please enable atleast one Social Login Key or LDAP before disabling username/password based login."
				)
			)

	def validate_backup_limit(self):
		if not self.backup_limit or self.backup_limit < 1:
			netmanthan.msgprint(_("Number of backups must be greater than zero."), alert=True)
			self.backup_limit = 1

	def on_update(self):
		self.set_defaults()

		netmanthan.cache().delete_value("system_settings")
		netmanthan.cache().delete_value("time_zone")

		if netmanthan.flags.update_last_reset_password_date:
			update_last_reset_password_date()

	def set_defaults(self):
		from netmanthan.translate import set_default_language

		for df in self.meta.get("fields"):
			if df.fieldtype not in no_value_fields and self.has_value_changed(df.fieldname):
				netmanthan.db.set_default(df.fieldname, self.get(df.fieldname))

		if self.language:
			set_default_language(self.language)


def update_last_reset_password_date():
	netmanthan.db.sql(
		""" UPDATE `tabUser`
		SET
			last_password_reset_date = %s
		WHERE
			last_password_reset_date is null""",
		today(),
	)


@netmanthan.whitelist()
def load():
	from netmanthan.utils.momentjs import get_all_timezones

	if not "System Manager" in netmanthan.get_roles():
		netmanthan.throw(_("Not permitted"), netmanthan.PermissionError)

	all_defaults = netmanthan.db.get_defaults()
	defaults = {}

	for df in netmanthan.get_meta("System Settings").get("fields"):
		if df.fieldtype in ("Select", "Data"):
			defaults[df.fieldname] = all_defaults.get(df.fieldname)

	return {"timezones": get_all_timezones(), "defaults": defaults}
