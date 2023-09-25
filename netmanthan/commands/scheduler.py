import sys

import click

import netmanthan
from netmanthan.commands import get_site, pass_context
from netmanthan.exceptions import SiteNotSpecifiedError


@click.command("trigger-scheduler-event", help="Trigger a scheduler event")
@click.argument("event")
@pass_context
def trigger_scheduler_event(context, event):
	import netmanthan.utils.scheduler

	exit_code = 0

	for site in context.sites:
		try:
			netmanthan.init(site=site)
			netmanthan.connect()
			try:
				netmanthan.get_doc("Scheduled Job Type", {"method": event}).execute()
			except netmanthan.DoesNotExistError:
				click.secho(f"Event {event} does not exist!", fg="red")
				exit_code = 1
		finally:
			netmanthan.destroy()

	if not context.sites:
		raise SiteNotSpecifiedError

	sys.exit(exit_code)


@click.command("enable-scheduler")
@pass_context
def enable_scheduler(context):
	"Enable scheduler"
	import netmanthan.utils.scheduler

	for site in context.sites:
		try:
			netmanthan.init(site=site)
			netmanthan.connect()
			netmanthan.utils.scheduler.enable_scheduler()
			netmanthan.db.commit()
			print("Enabled for", site)
		finally:
			netmanthan.destroy()
	if not context.sites:
		raise SiteNotSpecifiedError


@click.command("disable-scheduler")
@pass_context
def disable_scheduler(context):
	"Disable scheduler"
	import netmanthan.utils.scheduler

	for site in context.sites:
		try:
			netmanthan.init(site=site)
			netmanthan.connect()
			netmanthan.utils.scheduler.disable_scheduler()
			netmanthan.db.commit()
			print("Disabled for", site)
		finally:
			netmanthan.destroy()
	if not context.sites:
		raise SiteNotSpecifiedError


@click.command("scheduler")
@click.option("--site", help="site name")
@click.argument("state", type=click.Choice(["pause", "resume", "disable", "enable", "status"]))
@click.option(
	"--format", "-f", default="text", type=click.Choice(["json", "text"]), help="Output format"
)
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
@pass_context
def scheduler(context, state: str, format: str, verbose: bool = False, site: str | None = None):
	"""Control scheduler state."""
	import netmanthan
	import netmanthan.utils.scheduler
	from netmanthan.utils.scheduler import is_scheduler_inactive, toggle_scheduler

	site = site or get_site(context)

	output = {
		"text": "Scheduler is {status} for site {site}",
		"json": '{{"status": "{status}", "site": "{site}"}}',
	}

	with netmanthan.init_site(site=site):
		match state:
			case "status":
				netmanthan.connect()
				status = "disabled" if is_scheduler_inactive(verbose=verbose) else "enabled"
				return print(output[format].format(status=status, site=site))
			case "pause" | "resume":
				from netmanthan.installer import update_site_config

				update_site_config("pause_scheduler", state == "pause")
			case "enable" | "disable":
				netmanthan.connect()
				toggle_scheduler(state == "enable")
				netmanthan.db.commit()

		print(output[format].format(status=f"{state}d", site=site))


@click.command("set-maintenance-mode")
@click.option("--site", help="site name")
@click.argument("state", type=click.Choice(["on", "off"]))
@pass_context
def set_maintenance_mode(context, state, site=None):
	from netmanthan.installer import update_site_config

	if not site:
		site = get_site(context)

	try:
		netmanthan.init(site=site)
		update_site_config("maintenance_mode", 1 if (state == "on") else 0)

	finally:
		netmanthan.destroy()


@click.command(
	"doctor"
)  # Passing context always gets a site and if there is no use site it breaks
@click.option("--site", help="site name")
@pass_context
def doctor(context, site=None):
	"Get diagnostic info about background workers"
	from netmanthan.utils.doctor import doctor as _doctor

	if not site:
		site = get_site(context, raise_err=False)
	return _doctor(site=site)


@click.command("show-pending-jobs")
@click.option("--site", help="site name")
@pass_context
def show_pending_jobs(context, site=None):
	"Get diagnostic info about background jobs"
	from netmanthan.utils.doctor import pending_jobs as _pending_jobs

	if not site:
		site = get_site(context)

	with netmanthan.init_site(site):
		pending_jobs = _pending_jobs(site=site)

	return pending_jobs


@click.command("purge-jobs")
@click.option("--site", help="site name")
@click.option("--queue", default=None, help='one of "low", "default", "high')
@click.option(
	"--event",
	default=None,
	help='one of "all", "weekly", "monthly", "hourly", "daily", "weekly_long", "daily_long"',
)
def purge_jobs(site=None, queue=None, event=None):
	"Purge any pending periodic tasks, if event option is not given, it will purge everything for the site"
	from netmanthan.utils.doctor import purge_pending_jobs

	netmanthan.init(site or "")
	count = purge_pending_jobs(event=event, site=site, queue=queue)
	print(f"Purged {count} jobs")


@click.command("schedule")
def start_scheduler():
	from netmanthan.utils.scheduler import start_scheduler

	start_scheduler()


@click.command("worker")
@click.option(
	"--queue",
	type=str,
	help="Queue to consume from. Multiple queues can be specified using comma-separated string. If not specified all queues are consumed.",
)
@click.option("--quiet", is_flag=True, default=False, help="Hide Log Outputs")
@click.option("-u", "--rq-username", default=None, help="Redis ACL user")
@click.option("-p", "--rq-password", default=None, help="Redis ACL user password")
@click.option("--burst", is_flag=True, default=False, help="Run Worker in Burst mode.")
@click.option(
	"--strategy",
	required=False,
	type=click.Choice(["round_robin", "random"]),
	help="Dequeuing strategy to use",
)
def start_worker(
	queue, quiet=False, rq_username=None, rq_password=None, burst=False, strategy=None
):
	from netmanthan.utils.background_jobs import start_worker

	start_worker(
		queue,
		quiet=quiet,
		rq_username=rq_username,
		rq_password=rq_password,
		burst=burst,
		strategy=strategy,
	)


@click.command("ready-for-migration")
@click.option("--site", help="site name")
@pass_context
def ready_for_migration(context, site=None):
	from netmanthan.utils.doctor import get_pending_jobs

	if not site:
		site = get_site(context)

	try:
		netmanthan.init(site=site)
		pending_jobs = get_pending_jobs(site=site)

		if pending_jobs:
			print(f"NOT READY for migration: site {site} has pending background jobs")
			sys.exit(1)

		else:
			print(f"READY for migration: site {site} does not have any background jobs")
			return 0

	finally:
		netmanthan.destroy()


commands = [
	disable_scheduler,
	doctor,
	enable_scheduler,
	purge_jobs,
	ready_for_migration,
	scheduler,
	set_maintenance_mode,
	show_pending_jobs,
	start_scheduler,
	start_worker,
	trigger_scheduler_event,
]
