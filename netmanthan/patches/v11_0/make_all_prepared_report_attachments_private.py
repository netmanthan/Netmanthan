import netmanthan


def execute():
	if (
		netmanthan.db.count("File", filters={"attached_to_doctype": "Prepared Report", "is_private": 0})
		> 10000
	):
		netmanthan.db.auto_commit_on_many_writes = True

	files = netmanthan.get_all(
		"File",
		fields=["name", "attached_to_name"],
		filters={"attached_to_doctype": "Prepared Report", "is_private": 0},
	)
	for file_dict in files:
		# For some reason Prepared Report doc might not exist, check if it exists first
		if netmanthan.db.exists("Prepared Report", file_dict.attached_to_name):
			try:
				file_doc = netmanthan.get_doc("File", file_dict.name)
				file_doc.is_private = 1
				file_doc.save()
			except Exception:
				# File might not exist on the file system in that case delete both Prepared Report and File doc
				netmanthan.delete_doc("Prepared Report", file_dict.attached_to_name)
		else:
			# If Prepared Report doc doesn't exist then the file doc is useless. Delete it.
			netmanthan.delete_doc("File", file_dict.name)

	if netmanthan.db.auto_commit_on_many_writes:
		netmanthan.db.auto_commit_on_many_writes = False
