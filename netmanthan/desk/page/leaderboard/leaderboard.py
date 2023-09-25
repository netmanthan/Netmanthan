# Copyright (c) 2017, netmanthan Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE
import netmanthan


@netmanthan.whitelist()
def get_leaderboard_config():
	leaderboard_config = netmanthan._dict()
	leaderboard_hooks = netmanthan.get_hooks("leaderboards")
	for hook in leaderboard_hooks:
		leaderboard_config.update(netmanthan.get_attr(hook)())

	return leaderboard_config
