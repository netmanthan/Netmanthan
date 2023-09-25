import click

import netmanthan


def execute():
	netmanthan.delete_doc_if_exists("DocType", "Chat Message")
	netmanthan.delete_doc_if_exists("DocType", "Chat Message Attachment")
	netmanthan.delete_doc_if_exists("DocType", "Chat Profile")
	netmanthan.delete_doc_if_exists("DocType", "Chat Token")
	netmanthan.delete_doc_if_exists("DocType", "Chat Room User")
	netmanthan.delete_doc_if_exists("DocType", "Chat Room")
	netmanthan.delete_doc_if_exists("Module Def", "Chat")

	click.secho(
		"Chat Module is moved to a separate app and is removed from netmanthan in version-13.\n"
		"Please install the app to continue using the chat feature: https://github.com/netmanthan/chat",
		fg="yellow",
	)
