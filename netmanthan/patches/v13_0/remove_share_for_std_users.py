import netmanthan
import netmanthan.share


def execute():
	for user in netmanthan.STANDARD_USERS:
		netmanthan.share.remove("User", user, user)
