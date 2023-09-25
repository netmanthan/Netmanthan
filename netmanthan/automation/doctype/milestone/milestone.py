# Copyright (c) 2019, netmanthan Technologies and contributors
# License: MIT. See LICENSE

import netmanthan
from netmanthan.model.document import Document


class Milestone(Document):
	pass


def on_doctype_update():
	netmanthan.db.add_index("Milestone", ["reference_type", "reference_name"])
