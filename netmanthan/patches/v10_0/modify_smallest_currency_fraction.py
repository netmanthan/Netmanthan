# Copyright (c) 2018, netmanthan Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import netmanthan


def execute():
	netmanthan.db.set_value("Currency", "USD", "smallest_currency_fraction_value", "0.01")
