import netmanthan


def execute():
	netmanthan.db.sql(
		"""UPDATE `tabUser Permission`
		SET `modified`=NOW(), `creation`=NOW()
		WHERE `creation` IS NULL"""
	)
