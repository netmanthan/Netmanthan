# Copyright (c) 2021, netmanthan Technologies Pvt. Ltd. and Contributors
# MIT License. See LICENSE

from netmanthan.exceptions import ValidationError


class NewsletterAlreadySentError(ValidationError):
	pass


class NoRecipientFoundError(ValidationError):
	pass


class NewsletterNotSavedError(ValidationError):
	pass
