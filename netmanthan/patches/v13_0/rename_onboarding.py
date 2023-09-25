# Copyright (c) 2020, netmanthan Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import netmanthan


def execute():
	if netmanthan.db.exists("DocType", "Onboarding"):
		netmanthan.rename_doc("DocType", "Onboarding", "Module Onboarding", ignore_if_exists=True)
