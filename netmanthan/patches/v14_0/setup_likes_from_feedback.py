import netmanthan


def execute():
	netmanthan.reload_doctype("Comment")

	if not netmanthan.db.table_exists("Feedback"):
		return

	if netmanthan.db.count("Feedback") > 20000:
		netmanthan.db.auto_commit_on_many_writes = True

	for feedback in netmanthan.get_all("Feedback", fields=["*"]):
		if feedback.like:
			new_comment = netmanthan.new_doc("Comment")
			new_comment.comment_type = "Like"
			new_comment.comment_email = feedback.owner
			new_comment.content = "Liked by: " + feedback.owner
			new_comment.reference_doctype = feedback.reference_doctype
			new_comment.reference_name = feedback.reference_name
			new_comment.creation = feedback.creation
			new_comment.modified = feedback.modified
			new_comment.owner = feedback.owner
			new_comment.modified_by = feedback.modified_by
			new_comment.ip_address = feedback.ip_address
			new_comment.db_insert()

	if netmanthan.db.auto_commit_on_many_writes:
		netmanthan.db.auto_commit_on_many_writes = False

	# clean up
	netmanthan.db.delete("Feedback")
	netmanthan.db.commit()

	netmanthan.delete_doc("DocType", "Feedback")
