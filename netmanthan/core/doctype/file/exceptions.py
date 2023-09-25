import netmanthan


class MaxFileSizeReachedError(netmanthan.ValidationError):
	pass


class FolderNotEmpty(netmanthan.ValidationError):
	pass


from netmanthan.exceptions import *
