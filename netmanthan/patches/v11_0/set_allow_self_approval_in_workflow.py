import netmanthan


def execute():
	netmanthan.reload_doc("workflow", "doctype", "workflow_transition")
	netmanthan.db.sql("update `tabWorkflow Transition` set allow_self_approval=1")
