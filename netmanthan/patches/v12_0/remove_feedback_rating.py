import netmanthan


def execute():
	"""
	Deprecate Feedback Trigger and Rating. This feature was not customizable.
	Now can be achieved via custom Web Forms
	"""
	netmanthan.delete_doc("DocType", "Feedback Trigger")
	netmanthan.delete_doc("DocType", "Feedback Rating")
