# Copyright (c) 2015, netmanthan Technologies and contributors
# License: MIT. See LICENSE

import netmanthan
from netmanthan.model.document import Document


class EmailQueueRecipient(Document):
	DOCTYPE = "Email Queue Recipient"

	def is_mail_to_be_sent(self):
		return self.status == "Not Sent"

	def is_mail_sent(self):
		return self.status == "Sent"

	def update_db(self, commit=False, **kwargs):
		netmanthan.db.set_value(self.DOCTYPE, self.name, kwargs)
		if commit:
			netmanthan.db.commit()
