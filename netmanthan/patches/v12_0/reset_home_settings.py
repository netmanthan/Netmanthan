import netmanthan


def execute():
	netmanthan.reload_doc("core", "doctype", "user")
	netmanthan.db.sql(
		"""
		UPDATE `tabUser`
		SET `home_settings` = ''
		WHERE `user_type` = 'System User'
	"""
	)
