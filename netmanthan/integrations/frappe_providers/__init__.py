# imports - standard imports
import sys

# imports - module imports
from netmanthan.integrations.netmanthan_providers.netmanthancloud import netmanthancloud_migrator


def migrate_to(local_site, netmanthan_provider):
	if netmanthan_provider in ("netmanthan.cloud", "netmanthancloud.com"):
		return netmanthancloud_migrator(local_site)
	else:
		print(f"{netmanthan_provider} is not supported yet")
		sys.exit(1)
