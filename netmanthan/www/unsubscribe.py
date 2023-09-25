import netmanthan
from netmanthan.email.doctype.newsletter.newsletter import confirmed_unsubscribe
from netmanthan.utils.verified_command import verify_request

no_cache = True


def get_context(context):
	netmanthan.flags.ignore_permissions = True
	# Called for confirmation.
	if "email" in netmanthan.form_dict and netmanthan.request.method == "GET":
		if verify_request():
			user_email = netmanthan.form_dict["email"]
			context.email = user_email
			title = netmanthan.form_dict["name"]
			context.email_groups = get_email_groups(user_email)
			context.current_group = get_current_groups(title)
			context.status = "waiting_for_confirmation"

	# Called when form is submitted.
	elif "user_email" in netmanthan.form_dict and netmanthan.request.method == "POST":
		context.status = "unsubscribed"
		email = netmanthan.form_dict["user_email"]
		email_group = get_email_groups(email)
		for group in email_group:
			if group.email_group in netmanthan.form_dict:
				confirmed_unsubscribe(email, group.email_group)

	# Called on Invalid or unsigned request.
	else:
		context.status = "invalid"


def get_email_groups(user_email):
	# Return the all email_groups in which the email has been registered.
	return netmanthan.get_all(
		"Email Group Member", fields=["email_group"], filters={"email": user_email, "unsubscribed": 0}
	)


def get_current_groups(name):
	# Return current group by which the mail has been sent.
	return netmanthan.get_all(
		"Newsletter Email Group",
		fields=["email_group"],
		filters={"parent": name, "parenttype": "Newsletter"},
	)
