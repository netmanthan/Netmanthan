# Copyright (c) 2019, netmanthan Technologies and Contributors
# License: MIT. See LICENSE
import netmanthan
import netmanthan.cache_manager
from netmanthan.tests.utils import netmanthanTestCase


class TestMilestoneTracker(netmanthanTestCase):
	def test_milestone(self):
		netmanthan.db.delete("Milestone Tracker")

		netmanthan.cache().delete_key("milestone_tracker_map")

		milestone_tracker = netmanthan.get_doc(
			dict(doctype="Milestone Tracker", document_type="ToDo", track_field="status")
		).insert()

		todo = netmanthan.get_doc(dict(doctype="ToDo", description="test milestone", status="Open")).insert()

		milestones = netmanthan.get_all(
			"Milestone",
			fields=["track_field", "value", "milestone_tracker"],
			filters=dict(reference_type=todo.doctype, reference_name=todo.name),
		)

		self.assertEqual(len(milestones), 1)
		self.assertEqual(milestones[0].track_field, "status")
		self.assertEqual(milestones[0].value, "Open")

		todo.status = "Closed"
		todo.save()

		milestones = netmanthan.get_all(
			"Milestone",
			fields=["track_field", "value", "milestone_tracker"],
			filters=dict(reference_type=todo.doctype, reference_name=todo.name),
			order_by="modified desc",
		)

		self.assertEqual(len(milestones), 2)
		self.assertEqual(milestones[0].track_field, "status")
		self.assertEqual(milestones[0].value, "Closed")

		# cleanup
		netmanthan.db.delete("Milestone")
		milestone_tracker.delete()
