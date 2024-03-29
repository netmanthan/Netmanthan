import time
from contextlib import contextmanager
from unittest.mock import patch

from rq import Queue

import netmanthan
from netmanthan.core.page.background_jobs.background_jobs import remove_failed_jobs
from netmanthan.tests.utils import netmanthanTestCase
from netmanthan.utils.background_jobs import (
	RQ_JOB_FAILURE_TTL,
	RQ_RESULTS_TTL,
	execute_job,
	generate_qname,
	get_redis_conn,
)


class TestBackgroundJobs(netmanthanTestCase):
	def test_remove_failed_jobs(self):
		netmanthan.enqueue(method="netmanthan.tests.test_background_jobs.fail_function", queue="short")
		# wait for enqueued job to execute
		time.sleep(2)
		conn = get_redis_conn()
		queues = Queue.all(conn)

		for queue in queues:
			if queue.name == generate_qname("short"):
				fail_registry = queue.failed_job_registry
				self.assertGreater(fail_registry.count, 0)

		remove_failed_jobs()

		for queue in queues:
			if queue.name == generate_qname("short"):
				fail_registry = queue.failed_job_registry
				self.assertEqual(fail_registry.count, 0)

	def test_enqueue_at_front(self):
		kwargs = {
			"method": "netmanthan.handler.ping",
			"queue": "short",
		}

		# give worker something to work on first so that get_position doesn't return None
		netmanthan.enqueue(**kwargs)

		# test enqueue with at_front=True
		low_priority_job = netmanthan.enqueue(**kwargs)
		high_priority_job = netmanthan.enqueue(**kwargs, at_front=True)

		# lesser is earlier
		self.assertTrue(high_priority_job.get_position() < low_priority_job.get_position())

	def test_job_hooks(self):
		self.addCleanup(lambda: _test_JOB_HOOK.clear())
		with freeze_local() as locals, netmanthan.init_site(locals.site), patch(
			"netmanthan.get_hooks", patch_job_hooks
		):
			netmanthan.connect()
			self.assertIsNone(_test_JOB_HOOK.get("before_job"))
			r = execute_job(
				site=netmanthan.local.site,
				user="Administrator",
				method="netmanthan.handler.ping",
				event=None,
				job_name="netmanthan.handler.ping",
				is_async=True,
				kwargs={},
			)
			self.assertEqual(r, "pong")
			self.assertLess(_test_JOB_HOOK.get("before_job"), _test_JOB_HOOK.get("after_job"))


def fail_function():
	return 1 / 0


_test_JOB_HOOK = {}


def before_job(*args, **kwargs):
	_test_JOB_HOOK["before_job"] = time.time()


def after_job(*args, **kwargs):
	_test_JOB_HOOK["after_job"] = time.time()


@contextmanager
def freeze_local():
	locals = netmanthan.local
	netmanthan.local = netmanthan.Local()
	yield locals
	netmanthan.local = locals


def patch_job_hooks(event: str):
	return {
		"before_job": ["netmanthan.tests.test_background_jobs.before_job"],
		"after_job": ["netmanthan.tests.test_background_jobs.after_job"],
	}[event]
