# Copyright (c) 2015, netmanthan Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

from contextlib import suppress

import netmanthan
from netmanthan import _
from netmanthan.rate_limiter import rate_limit
from netmanthan.utils import validate_email_address

sitemap = 1


def get_context(context):
	doc = netmanthan.get_doc("Contact Us Settings", "Contact Us Settings")

	if doc.query_options:
		query_options = [opt.strip() for opt in doc.query_options.replace(",", "\n").split("\n") if opt]
	else:
		query_options = ["Sales", "Support", "General"]

	out = {"query_options": query_options, "parents": [{"name": _("Home"), "route": "/"}]}
	out.update(doc.as_dict())

	return out


@netmanthan.whitelist(allow_guest=True)
@rate_limit(limit=1000, seconds=60 * 60)
def send_message(sender, message, subject="Website Query"):
	sender = validate_email_address(sender, throw=True)

	with suppress(netmanthan.OutgoingEmailError):
		if forward_to_email := netmanthan.db.get_single_value("Contact Us Settings", "forward_to_email"):
			netmanthan.sendmail(recipients=forward_to_email, reply_to=sender, content=message, subject=subject)

		netmanthan.sendmail(
			recipients=sender,
			content=f"<div style='white-space: pre-wrap'>Thank you for reaching out to us. We will get back to you at the earliest.\n\n\nYour query:\n\n{message}</div>",
			subject="We've received your query!",
		)

	# for clearing outgoing email error message
	netmanthan.clear_last_message()

	# add to to-do ?
	netmanthan.get_doc(
		dict(
			doctype="Communication",
			sender=sender,
			subject=_("New Message from Website Contact Page"),
			sent_or_received="Received",
			content=message,
			status="Open",
		)
	).insert(ignore_permissions=True)
