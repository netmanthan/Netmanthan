# Copyright (c) 2020, netmanthan Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import netmanthan


def execute():
	if netmanthan.db.exists("DocType", "Event Producer"):
		netmanthan.db.sql("""UPDATE `tabEvent Producer` SET api_key='', api_secret=''""")
	if netmanthan.db.exists("DocType", "Event Consumer"):
		netmanthan.db.sql("""UPDATE `tabEvent Consumer` SET api_key='', api_secret=''""")
