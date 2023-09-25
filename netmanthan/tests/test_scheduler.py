import os
import time
from unittest import TestCase
from unittest.mock import patch

import netmanthan
from netmanthan.core.doctype.scheduled_job_type.scheduled_job_type import ScheduledJobType, sync_jobs
from netmanthan.utils import add_days, get_datetime
from netmanthan.utils.doctor import purge_pending_jobs
from netmanthan.utils.scheduler import (
	_get_last_modified_timestamp,
	enqueue_events,
	is_dormant,
	schedule_jobs_based_on_activity,
)


def test_timeout_10():
	time.sleep(10)


def test_method():
	pass


class TestScheduler(TestCase):
	def setUp(self):
		netmanthan.db.rollback()

		if not os.environ.get("CI"):
			return

		purge_pending_jobs()
		if not netmanthan.get_all("Scheduled Job Type", limit=1):
			sync_jobs()

	def test_enqueue_jobs(self):
		netmanthan.db.sql("update `tabScheduled Job Type` set last_execution = '2010-01-01 00:00:00'")

		netmanthan.flags.execute_job = True
		enqueue_events(site=netmanthan.local.site)
		netmanthan.flags.execute_job = False

		self.assertTrue("netmanthan.email.queue.set_expiry_for_email_queue", netmanthan.flags.enqueued_jobs)
		self.assertTrue("netmanthan.utils.change_log.check_for_update", netmanthan.flags.enqueued_jobs)
		self.assertTrue(
			"netmanthan.email.doctype.auto_email_report.auto_email_report.send_monthly",
			netmanthan.flags.enqueued_jobs,
		)

	def test_queue_peeking(self):
		job = get_test_job()

		with patch.object(job, "is_job_in_queue", return_value=True):
			# 1st job is in the queue (or running), don't enqueue it again
			self.assertFalse(job.enqueue())

	def test_is_dormant(self):
		self.assertTrue(is_dormant(check_time=get_datetime("2100-01-01 00:00:00")))
		self.assertTrue(is_dormant(check_time=add_days(netmanthan.db.get_last_created("Activity Log"), 5)))
		self.assertFalse(is_dormant(check_time=netmanthan.db.get_last_created("Activity Log")))

	def test_once_a_day_for_dormant(self):
		netmanthan.db.truncate("Scheduled Job Log")
		self.assertTrue(schedule_jobs_based_on_activity(check_time=get_datetime("2100-01-01 00:00:00")))
		self.assertTrue(
			schedule_jobs_based_on_activity(
				check_time=add_days(netmanthan.db.get_last_created("Activity Log"), 5)
			)
		)

		# create a fake job executed 5 days from now
		job = get_test_job(method="netmanthan.tests.test_scheduler.test_method", frequency="Daily")
		job.execute()
		job_log = netmanthan.get_doc("Scheduled Job Log", dict(scheduled_job_type=job.name))
		job_log.db_set(
			"modified", add_days(_get_last_modified_timestamp("Activity Log"), 5), update_modified=False
		)

		# inactive site with recent job, don't run
		self.assertFalse(
			schedule_jobs_based_on_activity(
				check_time=add_days(_get_last_modified_timestamp("Activity Log"), 5)
			)
		)

		# one more day has passed
		self.assertTrue(
			schedule_jobs_based_on_activity(
				check_time=add_days(_get_last_modified_timestamp("Activity Log"), 6)
			)
		)


def get_test_job(
	method="netmanthan.tests.test_scheduler.test_timeout_10", frequency="All"
) -> ScheduledJobType:
	if not netmanthan.db.exists("Scheduled Job Type", dict(method=method)):
		job = netmanthan.get_doc(
			dict(
				doctype="Scheduled Job Type",
				method=method,
				last_execution="2010-01-01 00:00:00",
				frequency=frequency,
			)
		).insert()
	else:
		job = netmanthan.get_doc("Scheduled Job Type", dict(method=method))
		job.db_set("last_execution", "2010-01-01 00:00:00")
		job.db_set("frequency", frequency)
	netmanthan.db.commit()

	return job
