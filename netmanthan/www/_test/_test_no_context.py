import netmanthan


# no context object is accepted
def get_context():
	context = netmanthan._dict()
	context.body = "Custom Content"
	return context
