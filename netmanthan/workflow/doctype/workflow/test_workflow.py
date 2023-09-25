# Copyright (c) 2015, netmanthan Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE
import netmanthan
from netmanthan.model.workflow import (
	WorkflowTransitionError,
	apply_workflow,
	get_common_transition_actions,
)
from netmanthan.query_builder import DocType
from netmanthan.test_runner import make_test_records
from netmanthan.tests.utils import netmanthanTestCase
from netmanthan.utils import random_string


class TestWorkflow(netmanthanTestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		make_test_records("User")

	def setUp(self):
		self.workflow = create_todo_workflow()
		netmanthan.set_user("Administrator")
		if self._testMethodName == "test_if_workflow_actions_were_processed_using_user":
			if not netmanthan.db.has_column("Workflow Action", "user"):
				# mariadb would raise this statement would create an implicit commit
				# if we do not commit before alter statement
				# nosemgrep
				netmanthan.db.commit()
				netmanthan.db.multisql(
					{
						"mariadb": "ALTER TABLE `tabWorkflow Action` ADD COLUMN user varchar(140)",
						"postgres": 'ALTER TABLE "tabWorkflow Action" ADD COLUMN "user" varchar(140)',
					}
				)
				netmanthan.cache().delete_value("table_columns")

	def tearDown(self):
		netmanthan.delete_doc("Workflow", "Test ToDo")
		if self._testMethodName == "test_if_workflow_actions_were_processed_using_user":
			if netmanthan.db.has_column("Workflow Action", "user"):
				# mariadb would raise this statement would create an implicit commit
				# if we do not commit before alter statement
				# nosemgrep
				netmanthan.db.commit()
				netmanthan.db.multisql(
					{
						"mariadb": "ALTER TABLE `tabWorkflow Action` DROP COLUMN user",
						"postgres": 'ALTER TABLE "tabWorkflow Action" DROP COLUMN "user"',
					}
				)
				netmanthan.cache().delete_value("table_columns")

	def test_default_condition(self):
		"""test default condition is set"""
		todo = create_new_todo()

		# default condition is set
		self.assertEqual(todo.workflow_state, "Pending")

		return todo

	def test_approve(self, doc=None):
		"""test simple workflow"""
		todo = doc or self.test_default_condition()

		apply_workflow(todo, "Approve")
		# default condition is set
		self.assertEqual(todo.workflow_state, "Approved")
		self.assertEqual(todo.status, "Closed")

		return todo

	def test_wrong_action(self):
		"""Check illegal action (approve after reject)"""
		todo = self.test_approve()

		self.assertRaises(WorkflowTransitionError, apply_workflow, todo, "Reject")

	def test_workflow_condition(self):
		"""Test condition in transition"""
		self.workflow.transitions[0].condition = 'doc.status == "Closed"'
		self.workflow.save()

		# only approve if status is closed
		self.assertRaises(WorkflowTransitionError, self.test_approve)

		self.workflow.transitions[0].condition = ""
		self.workflow.save()

	def test_get_common_transition_actions(self):
		todo1 = create_new_todo()
		todo2 = create_new_todo()
		todo3 = create_new_todo()
		todo4 = create_new_todo()

		actions = get_common_transition_actions([todo1, todo2, todo3, todo4], "ToDo")
		self.assertSetEqual(set(actions), {"Approve", "Reject"})

		apply_workflow(todo1, "Reject")
		apply_workflow(todo2, "Reject")
		apply_workflow(todo3, "Approve")

		actions = get_common_transition_actions([todo1, todo2, todo3], "ToDo")
		self.assertListEqual(actions, [])

		actions = get_common_transition_actions([todo1, todo2], "ToDo")
		self.assertListEqual(actions, ["Review"])

	def test_if_workflow_actions_were_processed_using_role(self):
		netmanthan.db.delete("Workflow Action")
		user = netmanthan.get_doc("User", "test2@example.com")
		user.add_roles("Test Approver", "System Manager")
		netmanthan.set_user("test2@example.com")

		doc = self.test_default_condition()
		workflow_actions = netmanthan.get_all("Workflow Action", fields=["*"])
		self.assertEqual(len(workflow_actions), 1)

		# test if status of workflow actions are updated on approval
		self.test_approve(doc)
		user.remove_roles("Test Approver", "System Manager")
		workflow_actions = netmanthan.get_all("Workflow Action", fields=["status"])
		self.assertEqual(len(workflow_actions), 1)
		self.assertEqual(workflow_actions[0].status, "Completed")
		netmanthan.set_user("Administrator")

	def test_if_workflow_actions_were_processed_using_user(self):
		netmanthan.db.delete("Workflow Action")

		user = netmanthan.get_doc("User", "test2@example.com")
		user.add_roles("Test Approver", "System Manager")
		netmanthan.set_user("test2@example.com")

		doc = self.test_default_condition()
		workflow_actions = netmanthan.get_all("Workflow Action", fields=["*"])
		self.assertEqual(len(workflow_actions), 1)

		# test if status of workflow actions are updated on approval
		WorkflowAction = DocType("Workflow Action")
		WorkflowActionPermittedRole = DocType("Workflow Action Permitted Role")
		netmanthan.qb.update(WorkflowAction).set(WorkflowAction.user, "test2@example.com").run()
		netmanthan.qb.update(WorkflowActionPermittedRole).set(WorkflowActionPermittedRole.role, "").run()

		self.test_approve(doc)

		user.remove_roles("Test Approver", "System Manager")
		workflow_actions = netmanthan.get_all("Workflow Action", fields=["status"])
		self.assertEqual(len(workflow_actions), 1)
		self.assertEqual(workflow_actions[0].status, "Completed")
		netmanthan.set_user("Administrator")

	def test_update_docstatus(self):
		todo = create_new_todo()
		apply_workflow(todo, "Approve")

		self.workflow.states[1].doc_status = 0
		self.workflow.save()
		todo.reload()
		self.assertEqual(todo.docstatus, 0)
		self.workflow.states[1].doc_status = 1
		self.workflow.save()
		todo.reload()
		self.assertEqual(todo.docstatus, 1)

		self.workflow.states[1].doc_status = 0
		self.workflow.save()

	def test_if_workflow_set_on_action(self):
		self.workflow.states[1].doc_status = 1
		self.workflow.save()
		todo = create_new_todo()
		self.assertEqual(todo.docstatus, 0)
		todo.submit()
		self.assertEqual(todo.docstatus, 1)
		self.assertEqual(todo.workflow_state, "Approved")

		self.workflow.states[1].doc_status = 0
		self.workflow.save()

	def test_syntax_error_in_transition_rule(self):
		self.workflow.transitions[0].condition = 'doc.status =! "Closed"'

		with self.assertRaises(netmanthan.ValidationError) as se:
			self.workflow.save()

		self.assertTrue(
			"invalid python code" in str(se.exception).lower(), msg="Python code validation not working"
		)


def create_todo_workflow():
	from netmanthan.tests.ui_test_helpers import UI_TEST_USER

	if netmanthan.db.exists("Workflow", "Test ToDo"):
		netmanthan.delete_doc("Workflow", "Test ToDo")

	TEST_ROLE = "Test Approver"

	if not netmanthan.db.exists("Role", TEST_ROLE):
		netmanthan.get_doc(dict(doctype="Role", role_name=TEST_ROLE)).insert(ignore_if_duplicate=True)
		if netmanthan.db.exists("User", UI_TEST_USER):
			netmanthan.get_doc("User", UI_TEST_USER).add_roles(TEST_ROLE)

	workflow = netmanthan.new_doc("Workflow")
	workflow.workflow_name = "Test ToDo"
	workflow.document_type = "ToDo"
	workflow.workflow_state_field = "workflow_state"
	workflow.is_active = 1
	workflow.send_email_alert = 0
	workflow.append("states", dict(state="Pending", allow_edit="All"))
	workflow.append(
		"states",
		dict(state="Approved", allow_edit=TEST_ROLE, update_field="status", update_value="Closed"),
	)
	workflow.append("states", dict(state="Rejected", allow_edit=TEST_ROLE))
	workflow.append(
		"transitions",
		dict(
			state="Pending",
			action="Approve",
			next_state="Approved",
			allowed=TEST_ROLE,
			allow_self_approval=1,
		),
	)
	workflow.append(
		"transitions",
		dict(
			state="Pending",
			action="Reject",
			next_state="Rejected",
			allowed=TEST_ROLE,
			allow_self_approval=1,
		),
	)
	workflow.append(
		"transitions",
		dict(
			state="Rejected", action="Review", next_state="Pending", allowed="All", allow_self_approval=1
		),
	)
	workflow.insert(ignore_permissions=True)

	return workflow


def create_new_todo():
	return netmanthan.get_doc(dict(doctype="ToDo", description="workflow " + random_string(10))).insert()
