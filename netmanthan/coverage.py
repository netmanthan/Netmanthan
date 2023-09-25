# Copyright (c) 2021, netmanthan Technologies Pvt. Ltd. and Contributors
# MIT License. See LICENSE
"""
	netmanthan.coverage
	~~~~~~~~~~~~~~~~

	Coverage settings for netmanthan
"""

STANDARD_INCLUSIONS = ["*.py"]

STANDARD_EXCLUSIONS = [
	"*.js",
	"*.xml",
	"*.pyc",
	"*.css",
	"*.less",
	"*.scss",
	"*.vue",
	"*.html",
	"*/test_*",
	"*/node_modules/*",
	"*/doctype/*/*_dashboard.py",
	"*/patches/*",
]

netmanthan_EXCLUSIONS = [
	"*/tests/*",
	"*/commands/*",
	"*/netmanthan/change_log/*",
	"*/netmanthan/exceptions*",
	"*/netmanthan/coverage.py",
	"*netmanthan/setup.py",
	"*/doctype/*/*_dashboard.py",
	"*/patches/*",
]


class CodeCoverage:
	def __init__(self, with_coverage, app):
		self.with_coverage = with_coverage
		self.app = app or "netmanthan"

	def __enter__(self):
		if self.with_coverage:
			import os

			from coverage import Coverage

			from netmanthan.utils import get_bench_path

			# Generate coverage report only for app that is being tested
			source_path = os.path.join(get_bench_path(), "apps", self.app)
			omit = STANDARD_EXCLUSIONS[:]

			if self.app == "netmanthan":
				omit.extend(netmanthan_EXCLUSIONS)

			self.coverage = Coverage(source=[source_path], omit=omit, include=STANDARD_INCLUSIONS)
			self.coverage.start()

	def __exit__(self, exc_type, exc_value, traceback):
		if self.with_coverage:
			self.coverage.stop()
			self.coverage.save()
			self.coverage.xml_report()
