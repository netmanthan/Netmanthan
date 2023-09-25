import json
import os
import subprocess
import sys
from shutil import which

import click

import netmanthan
from netmanthan.commands import get_site, pass_context
from netmanthan.coverage import CodeCoverage
from netmanthan.exceptions import SiteNotSpecifiedError
from netmanthan.utils import cint, update_progress_bar

DATA_IMPORT_DEPRECATION = (
	"[DEPRECATED] The `import-csv` command used 'Data Import Legacy' which has been deprecated.\n"
	"Use `data-import` command instead to import data via 'Data Import'."
)


@click.command("build")
@click.option("--app", help="Build assets for app")
@click.option("--apps", help="Build assets for specific apps")
@click.option(
	"--hard-link",
	is_flag=True,
	default=False,
	help="Copy the files instead of symlinking",
	envvar="netmanthan_HARD_LINK_ASSETS",
)
@click.option(
	"--make-copy",
	is_flag=True,
	default=False,
	help="[DEPRECATED] Copy the files instead of symlinking",
)
@click.option(
	"--restore",
	is_flag=True,
	default=False,
	help="[DEPRECATED] Copy the files instead of symlinking with force",
)
@click.option("--production", is_flag=True, default=False, help="Build assets in production mode")
@click.option("--verbose", is_flag=True, default=False, help="Verbose")
@click.option(
	"--force", is_flag=True, default=False, help="Force build assets instead of downloading available"
)
def build(
	app=None,
	apps=None,
	hard_link=False,
	make_copy=False,
	restore=False,
	production=False,
	verbose=False,
	force=False,
):
	"Compile JS and CSS source files"
	from netmanthan.build import bundle, download_netmanthan_assets

	netmanthan.init("")

	if not apps and app:
		apps = app

	# dont try downloading assets if force used, app specified or running via CI
	if not (force or apps or os.environ.get("CI")):
		# skip building netmanthan if assets exist remotely
		skip_netmanthan = download_netmanthan_assets(verbose=verbose)
	else:
		skip_netmanthan = False

	# don't minify in developer_mode for faster builds
	development = netmanthan.local.conf.developer_mode or netmanthan.local.dev_server
	mode = "development" if development else "production"
	if production:
		mode = "production"

	if make_copy or restore:
		hard_link = make_copy or restore
		click.secho(
			"bench build: --make-copy and --restore options are deprecated in favour of --hard-link",
			fg="yellow",
		)

	bundle(mode, apps=apps, hard_link=hard_link, verbose=verbose, skip_netmanthan=skip_netmanthan)


@click.command("watch")
@click.option("--apps", help="Watch assets for specific apps")
def watch(apps=None):
	"Watch and compile JS and CSS files as and when they change"
	from netmanthan.build import watch

	netmanthan.init("")
	watch(apps)


@click.command("clear-cache")
@pass_context
def clear_cache(context):
	"Clear cache, doctype cache and defaults"
	import netmanthan.sessions
	from netmanthan.desk.notifications import clear_notifications
	from netmanthan.website.utils import clear_website_cache

	for site in context.sites:
		try:
			netmanthan.connect(site)
			netmanthan.clear_cache()
			clear_notifications()
			clear_website_cache()
		finally:
			netmanthan.destroy()
	if not context.sites:
		raise SiteNotSpecifiedError


@click.command("clear-website-cache")
@pass_context
def clear_website_cache(context):
	"Clear website cache"
	from netmanthan.website.utils import clear_website_cache

	for site in context.sites:
		try:
			netmanthan.init(site=site)
			netmanthan.connect()
			clear_website_cache()
		finally:
			netmanthan.destroy()
	if not context.sites:
		raise SiteNotSpecifiedError


@click.command("destroy-all-sessions")
@click.option("--reason")
@pass_context
def destroy_all_sessions(context, reason=None):
	"Clear sessions of all users (logs them out)"
	import netmanthan.sessions

	for site in context.sites:
		try:
			netmanthan.init(site=site)
			netmanthan.connect()
			netmanthan.sessions.clear_all_sessions(reason)
			netmanthan.db.commit()
		finally:
			netmanthan.destroy()
	if not context.sites:
		raise SiteNotSpecifiedError


@click.command("show-config")
@click.option("--format", "-f", type=click.Choice(["text", "json"]), default="text")
@pass_context
def show_config(context, format):
	"Print configuration file to STDOUT in speified format"

	if not context.sites:
		raise SiteNotSpecifiedError

	sites_config = {}
	sites_path = os.getcwd()

	from netmanthan.utils.commands import render_table

	def transform_config(config, prefix=None):
		prefix = f"{prefix}." if prefix else ""
		site_config = []

		for conf, value in config.items():
			if isinstance(value, dict):
				site_config += transform_config(value, prefix=f"{prefix}{conf}")
			else:
				log_value = json.dumps(value) if isinstance(value, list) else value
				site_config += [[f"{prefix}{conf}", log_value]]

		return site_config

	for site in context.sites:
		netmanthan.init(site)

		if len(context.sites) != 1 and format == "text":
			if context.sites.index(site) != 0:
				click.echo()
			click.secho(f"Site {site}", fg="yellow")

		configuration = netmanthan.get_site_config(sites_path=sites_path, site_path=site)

		if format == "text":
			data = transform_config(configuration)
			data.insert(0, ["Config", "Value"])
			render_table(data)

		if format == "json":
			sites_config[site] = configuration

		netmanthan.destroy()

	if format == "json":
		click.echo(netmanthan.as_json(sites_config))


@click.command("reset-perms")
@pass_context
def reset_perms(context):
	"Reset permissions for all doctypes"
	from netmanthan.permissions import reset_perms

	for site in context.sites:
		try:
			netmanthan.init(site=site)
			netmanthan.connect()
			for d in netmanthan.db.sql_list(
				"""select name from `tabDocType`
				where istable=0 and custom=0"""
			):
				netmanthan.clear_cache(doctype=d)
				reset_perms(d)
		finally:
			netmanthan.destroy()
	if not context.sites:
		raise SiteNotSpecifiedError


@click.command("execute")
@click.argument("method")
@click.option("--args")
@click.option("--kwargs")
@click.option("--profile", is_flag=True, default=False)
@pass_context
def execute(context, method, args=None, kwargs=None, profile=False):
	"Execute a function"
	for site in context.sites:
		ret = ""
		try:
			netmanthan.init(site=site)
			netmanthan.connect()

			if args:
				try:
					args = eval(args)
				except NameError:
					args = [args]
			else:
				args = ()

			if kwargs:
				kwargs = eval(kwargs)
			else:
				kwargs = {}

			if profile:
				import cProfile

				pr = cProfile.Profile()
				pr.enable()

			try:
				ret = netmanthan.get_attr(method)(*args, **kwargs)
			except Exception:
				# eval is safe here because input is from console
				ret = eval(method + "(*args, **kwargs)", globals(), locals())  # nosemgrep

			if profile:
				import pstats
				from io import StringIO

				pr.disable()
				s = StringIO()
				pstats.Stats(pr, stream=s).sort_stats("cumulative").print_stats(0.5)
				print(s.getvalue())

			if netmanthan.db:
				netmanthan.db.commit()
		finally:
			netmanthan.destroy()
		if ret:
			from netmanthan.utils.response import json_handler

			print(json.dumps(ret, default=json_handler))

	if not context.sites:
		raise SiteNotSpecifiedError


@click.command("add-to-email-queue")
@click.argument("email-path")
@pass_context
def add_to_email_queue(context, email_path):
	"Add an email to the Email Queue"
	site = get_site(context)

	if os.path.isdir(email_path):
		with netmanthan.init_site(site):
			netmanthan.connect()
			for email in os.listdir(email_path):
				with open(os.path.join(email_path, email)) as email_data:
					kwargs = json.load(email_data)
					kwargs["delayed"] = True
					netmanthan.sendmail(**kwargs)
					netmanthan.db.commit()


@click.command("export-doc")
@click.argument("doctype")
@click.argument("docname")
@pass_context
def export_doc(context, doctype, docname):
	"Export a single document to csv"
	import netmanthan.modules

	for site in context.sites:
		try:
			netmanthan.init(site=site)
			netmanthan.connect()
			netmanthan.modules.export_doc(doctype, docname)
		finally:
			netmanthan.destroy()
	if not context.sites:
		raise SiteNotSpecifiedError


@click.command("export-json")
@click.argument("doctype")
@click.argument("path")
@click.option("--name", help="Export only one document")
@pass_context
def export_json(context, doctype, path, name=None):
	"Export doclist as json to the given path, use '-' as name for Singles."
	from netmanthan.core.doctype.data_import.data_import import export_json

	for site in context.sites:
		try:
			netmanthan.init(site=site)
			netmanthan.connect()
			export_json(doctype, path, name=name)
		finally:
			netmanthan.destroy()
	if not context.sites:
		raise SiteNotSpecifiedError


@click.command("export-csv")
@click.argument("doctype")
@click.argument("path")
@pass_context
def export_csv(context, doctype, path):
	"Export data import template with data for DocType"
	from netmanthan.core.doctype.data_import.data_import import export_csv

	for site in context.sites:
		try:
			netmanthan.init(site=site)
			netmanthan.connect()
			export_csv(doctype, path)
		finally:
			netmanthan.destroy()
	if not context.sites:
		raise SiteNotSpecifiedError


@click.command("export-fixtures")
@click.option("--app", default=None, help="Export fixtures of a specific app")
@pass_context
def export_fixtures(context, app=None):
	"Export fixtures"
	from netmanthan.utils.fixtures import export_fixtures

	for site in context.sites:
		try:
			netmanthan.init(site=site)
			netmanthan.connect()
			export_fixtures(app=app)
		finally:
			netmanthan.destroy()
	if not context.sites:
		raise SiteNotSpecifiedError


@click.command("import-doc")
@click.argument("path")
@pass_context
def import_doc(context, path, force=False):
	"Import (insert/update) doclist. If the argument is a directory, all files ending with .json are imported"
	from netmanthan.core.doctype.data_import.data_import import import_doc

	if not os.path.exists(path):
		path = os.path.join("..", path)
	if not os.path.exists(path):
		print(f"Invalid path {path}")
		sys.exit(1)

	for site in context.sites:
		try:
			netmanthan.init(site=site)
			netmanthan.connect()
			import_doc(path)
		finally:
			netmanthan.destroy()
	if not context.sites:
		raise SiteNotSpecifiedError


@click.command("import-csv", help=DATA_IMPORT_DEPRECATION)
@click.argument("path")
@click.option(
	"--only-insert", default=False, is_flag=True, help="Do not overwrite existing records"
)
@click.option(
	"--submit-after-import", default=False, is_flag=True, help="Submit document after importing it"
)
@click.option(
	"--ignore-encoding-errors",
	default=False,
	is_flag=True,
	help="Ignore encoding errors while coverting to unicode",
)
@click.option("--no-email", default=True, is_flag=True, help="Send email if applicable")
@pass_context
def import_csv(
	context,
	path,
	only_insert=False,
	submit_after_import=False,
	ignore_encoding_errors=False,
	no_email=True,
):
	click.secho(DATA_IMPORT_DEPRECATION, fg="yellow")
	sys.exit(1)


@click.command("data-import")
@click.option(
	"--file", "file_path", type=click.Path(), required=True, help="Path to import file (.csv, .xlsx)"
)
@click.option("--doctype", type=str, required=True)
@click.option(
	"--type",
	"import_type",
	type=click.Choice(["Insert", "Update"], case_sensitive=False),
	default="Insert",
	help="Insert New Records or Update Existing Records",
)
@click.option(
	"--submit-after-import", default=False, is_flag=True, help="Submit document after importing it"
)
@click.option("--mute-emails", default=True, is_flag=True, help="Mute emails during import")
@pass_context
def data_import(
	context, file_path, doctype, import_type=None, submit_after_import=False, mute_emails=True
):
	"Import documents in bulk from CSV or XLSX using data import"
	from netmanthan.core.doctype.data_import.data_import import import_file

	site = get_site(context)

	netmanthan.init(site=site)
	netmanthan.connect()
	import_file(doctype, file_path, import_type, submit_after_import, console=True)
	netmanthan.destroy()


@click.command("bulk-rename")
@click.argument("doctype")
@click.argument("path")
@pass_context
def bulk_rename(context, doctype, path):
	"Rename multiple records via CSV file"
	from netmanthan.model.rename_doc import bulk_rename
	from netmanthan.utils.csvutils import read_csv_content

	site = get_site(context)

	with open(path) as csvfile:
		rows = read_csv_content(csvfile.read())

	netmanthan.init(site=site)
	netmanthan.connect()

	bulk_rename(doctype, rows, via_console=True)

	netmanthan.destroy()


@click.command("db-console")
@pass_context
def database(context):
	"""
	Enter into the Database console for given site.
	"""
	site = get_site(context)
	if not site:
		raise SiteNotSpecifiedError
	netmanthan.init(site=site)
	if not netmanthan.conf.db_type or netmanthan.conf.db_type == "mariadb":
		_mariadb()
	elif netmanthan.conf.db_type == "postgres":
		_psql()


@click.command("mariadb")
@pass_context
def mariadb(context):
	"""
	Enter into mariadb console for a given site.
	"""
	site = get_site(context)
	if not site:
		raise SiteNotSpecifiedError
	netmanthan.init(site=site)
	_mariadb()


@click.command("postgres")
@pass_context
def postgres(context):
	"""
	Enter into postgres console for a given site.
	"""
	site = get_site(context)
	netmanthan.init(site=site)
	_psql()


def _mariadb():
	from netmanthan.database.mariadb.database import MariaDBDatabase

	mysql = which("mysql")
	command = [
		mysql,
		"--port",
		str(netmanthan.conf.db_port or MariaDBDatabase.default_port),
		"-u",
		netmanthan.conf.db_name,
		f"-p{netmanthan.conf.db_password}",
		netmanthan.conf.db_name,
		"-h",
        netmanthan.conf.db_host or "localhost",
		"--pager=less -SFX",
		"--safe-updates",
		"-A",
	]
	os.execv(mysql, command)


def _psql():
	psql = which("psql")

	host = netmanthan.conf.db_host or "127.0.0.1"
	port = netmanthan.conf.db_port or "5432"
	env = os.environ.copy()
	env["PGPASSWORD"] = netmanthan.conf.db_password
	conn_string = f"postgresql://{netmanthan.conf.db_name}@{host}:{port}/{netmanthan.conf.db_name}"
	subprocess.run([psql, conn_string], check=True, env=env)


@click.command("jupyter")
@pass_context
def jupyter(context):
	installed_packages = (
		r.split("==", 1)[0]
		for r in subprocess.check_output([sys.executable, "-m", "pip", "freeze"], encoding="utf8")
	)

	if "jupyter" not in installed_packages:
		subprocess.check_output([sys.executable, "-m", "pip", "install", "jupyter"])

	site = get_site(context)
	netmanthan.init(site=site)

	jupyter_notebooks_path = os.path.abspath(netmanthan.get_site_path("jupyter_notebooks"))
	sites_path = os.path.abspath(netmanthan.get_site_path(".."))

	try:
		os.stat(jupyter_notebooks_path)
	except OSError:
		print(f"Creating folder to keep jupyter notebooks at {jupyter_notebooks_path}")
		os.mkdir(jupyter_notebooks_path)
	bin_path = os.path.abspath("../env/bin")
	print(
		"""
Starting Jupyter notebook
Run the following in your first cell to connect notebook to netmanthan
```
import netmanthan
netmanthan.init(site='{site}', sites_path='{sites_path}')
netmanthan.connect()
netmanthan.local.lang = netmanthan.db.get_default('lang')
netmanthan.db.connect()
```
	""".format(
			site=site, sites_path=sites_path
		)
	)
	os.execv(
		f"{bin_path}/jupyter",
		[
			f"{bin_path}/jupyter",
			"notebook",
			jupyter_notebooks_path,
		],
	)


def _console_cleanup():
	# Execute rollback_observers on console close
	netmanthan.db.rollback()
	netmanthan.destroy()


@click.command("console")
@click.option("--autoreload", is_flag=True, help="Reload changes to code automatically")
@pass_context
def console(context, autoreload=False):
	"Start ipython console for a site"
	site = get_site(context)
	netmanthan.init(site=site)
	netmanthan.connect()
	netmanthan.local.lang = netmanthan.db.get_default("lang")

	from atexit import register

	from IPython.terminal.embed import InteractiveShellEmbed

	register(_console_cleanup)

	terminal = InteractiveShellEmbed()
	if autoreload:
		terminal.extension_manager.load_extension("autoreload")
		terminal.run_line_magic("autoreload", "2")

	all_apps = netmanthan.get_installed_apps()
	failed_to_import = []

	for app in all_apps:
		try:
			locals()[app] = __import__(app)
		except ModuleNotFoundError:
			failed_to_import.append(app)
			all_apps.remove(app)

	print("Apps in this namespace:\n{}".format(", ".join(all_apps)))
	if failed_to_import:
		print("\nFailed to import:\n{}".format(", ".join(failed_to_import)))

	terminal.colors = "neutral"
	terminal.display_banner = False
	terminal()


@click.command(
	"transform-database", help="Change tables' internal settings changing engine and row formats"
)
@click.option(
	"--table",
	required=True,
	help="Comma separated name of tables to convert. To convert all tables, pass 'all'",
)
@click.option(
	"--engine",
	default=None,
	type=click.Choice(["InnoDB", "MyISAM"]),
	help="Choice of storage engine for said table(s)",
)
@click.option(
	"--row_format",
	default=None,
	type=click.Choice(["DYNAMIC", "COMPACT", "REDUNDANT", "COMPRESSED"]),
	help="Set ROW_FORMAT parameter for said table(s)",
)
@click.option("--failfast", is_flag=True, default=False, help="Exit on first failure occurred")
@pass_context
def transform_database(context, table, engine, row_format, failfast):
	"Transform site database through given parameters"
	site = get_site(context)
	check_table = []
	add_line = False
	skipped = 0
	netmanthan.init(site=site)

	if netmanthan.conf.db_type and netmanthan.conf.db_type != "mariadb":
		click.secho("This command only has support for MariaDB databases at this point", fg="yellow")
		sys.exit(1)

	if not (engine or row_format):
		click.secho("Values for `--engine` or `--row_format` must be set")
		sys.exit(1)

	netmanthan.connect()

	if table == "all":
		information_schema = netmanthan.qb.Schema("information_schema")
		queried_tables = (
			netmanthan.qb.from_(information_schema.tables)
			.select("table_name")
			.where(
				(information_schema.tables.row_format != row_format)
				& (information_schema.tables.table_schema == netmanthan.conf.db_name)
			)
			.run()
		)
		tables = [x[0] for x in queried_tables]
	else:
		tables = [x.strip() for x in table.split(",")]

	total = len(tables)

	for current, table in enumerate(tables):
		values_to_set = ""
		if engine:
			values_to_set += f" ENGINE={engine}"
		if row_format:
			values_to_set += f" ROW_FORMAT={row_format}"

		try:
			netmanthan.db.sql(f"ALTER TABLE `{table}`{values_to_set}")
			update_progress_bar("Updating table schema", current - skipped, total)
			add_line = True

		except Exception as e:
			check_table.append([table, e.args])
			skipped += 1

			if failfast:
				break

	if add_line:
		print()

	for errored_table in check_table:
		table, err = errored_table
		err_msg = f"{table}: ERROR {err[0]}: {err[1]}"
		click.secho(err_msg, fg="yellow")

	netmanthan.destroy()


@click.command("run-tests")
@click.option("--app", help="For App")
@click.option("--doctype", help="For DocType")
@click.option("--module-def", help="For all Doctypes in Module Def")
@click.option("--case", help="Select particular TestCase")
@click.option(
	"--doctype-list-path",
	help="Path to .txt file for list of doctypes. Example erpnext/tests/server/agriculture.txt",
)
@click.option("--test", multiple=True, help="Specific test")
@click.option("--ui-tests", is_flag=True, default=False, help="Run UI Tests")
@click.option("--module", help="Run tests in a module")
@click.option("--profile", is_flag=True, default=False)
@click.option("--coverage", is_flag=True, default=False)
@click.option("--skip-test-records", is_flag=True, default=False, help="Don't create test records")
@click.option(
	"--skip-before-tests", is_flag=True, default=False, help="Don't run before tests hook"
)
@click.option("--junit-xml-output", help="Destination file path for junit xml report")
@click.option(
	"--failfast", is_flag=True, default=False, help="Stop the test run on the first error or failure"
)
@pass_context
def run_tests(
	context,
	app=None,
	module=None,
	doctype=None,
	module_def=None,
	test=(),
	profile=False,
	coverage=False,
	junit_xml_output=False,
	ui_tests=False,
	doctype_list_path=None,
	skip_test_records=False,
	skip_before_tests=False,
	failfast=False,
	case=None,
):

	with CodeCoverage(coverage, app):
		import netmanthan
		import netmanthan.test_runner

		tests = test
		site = get_site(context)

		allow_tests = netmanthan.get_conf(site).allow_tests

		if not (allow_tests or os.environ.get("CI")):
			click.secho("Testing is disabled for the site!", bold=True)
			click.secho("You can enable tests by entering following command:")
			click.secho(f"bench --site {site} set-config allow_tests true", fg="green")
			return

		netmanthan.init(site=site)

		netmanthan.flags.skip_before_tests = skip_before_tests
		netmanthan.flags.skip_test_records = skip_test_records

		ret = netmanthan.test_runner.main(
			app,
			module,
			doctype,
			module_def,
			context.verbose,
			tests=tests,
			force=context.force,
			profile=profile,
			junit_xml_output=junit_xml_output,
			ui_tests=ui_tests,
			doctype_list_path=doctype_list_path,
			failfast=failfast,
			case=case,
		)

		if len(ret.failures) == 0 and len(ret.errors) == 0:
			ret = 0

		if os.environ.get("CI"):
			sys.exit(ret)


@click.command("run-parallel-tests")
@click.option("--app", help="For App", default="netmanthan")
@click.option("--build-number", help="Build number", default=1)
@click.option("--total-builds", help="Total number of builds", default=1)
@click.option("--with-coverage", is_flag=True, help="Build coverage file")
@click.option("--use-orchestrator", is_flag=True, help="Use orchestrator to run parallel tests")
@click.option("--dry-run", is_flag=True, default=False, help="Dont actually run tests")
@pass_context
def run_parallel_tests(
	context,
	app,
	build_number,
	total_builds,
	with_coverage=False,
	use_orchestrator=False,
	dry_run=False,
):
	with CodeCoverage(with_coverage, app):
		site = get_site(context)
		if use_orchestrator:
			from netmanthan.parallel_test_runner import ParallelTestWithOrchestrator

			ParallelTestWithOrchestrator(app, site=site)
		else:
			from netmanthan.parallel_test_runner import ParallelTestRunner

			ParallelTestRunner(
				app,
				site=site,
				build_number=build_number,
				total_builds=total_builds,
				dry_run=dry_run,
			)


@click.command(
	"run-ui-tests",
	context_settings=dict(
		ignore_unknown_options=True,
	),
)
@click.argument("app")
@click.argument("cypressargs", nargs=-1, type=click.UNPROCESSED)
@click.option("--headless", is_flag=True, help="Run UI Test in headless mode")
@click.option("--parallel", is_flag=True, help="Run UI Test in parallel mode")
@click.option("--with-coverage", is_flag=True, help="Generate coverage report")
@click.option("--ci-build-id")
@pass_context
def run_ui_tests(
	context,
	app,
	headless=False,
	parallel=True,
	with_coverage=False,
	ci_build_id=None,
	cypressargs=None,
):
	"Run UI tests"
	site = get_site(context)
	app_base_path = os.path.abspath(os.path.join(netmanthan.get_app_path(app), ".."))
	site_url = netmanthan.utils.get_site_url(site)
	admin_password = netmanthan.get_conf(site).admin_password

	# override baseUrl using env variable
	site_env = f"CYPRESS_baseUrl={site_url}"
	password_env = f"CYPRESS_adminPassword={admin_password}" if admin_password else ""
	coverage_env = f"CYPRESS_coverage={str(with_coverage).lower()}"

	os.chdir(app_base_path)

	node_bin = subprocess.getoutput("yarn bin")
	cypress_path = f"{node_bin}/cypress"
	drag_drop_plugin_path = f"{node_bin}/../@4tw/cypress-drag-drop"
	real_events_plugin_path = f"{node_bin}/../cypress-real-events"
	testing_library_path = f"{node_bin}/../@testing-library"
	coverage_plugin_path = f"{node_bin}/../@cypress/code-coverage"

	# check if cypress in path...if not, install it.
	if not (
		os.path.exists(cypress_path)
		and os.path.exists(drag_drop_plugin_path)
		and os.path.exists(real_events_plugin_path)
		and os.path.exists(testing_library_path)
		and os.path.exists(coverage_plugin_path)
	):
		# install cypress & dependent plugins
		click.secho("Installing Cypress...", fg="yellow")
		packages = " ".join(
			[
				"cypress@^10",
				"@4tw/cypress-drag-drop@^2",
				"cypress-real-events",
				"@testing-library/cypress@^8",
				"@testing-library/dom@8.17.1",
				"@cypress/code-coverage@^3",
			]
		)
		netmanthan.commands.popen(f"yarn add {packages} --no-lockfile")

	# run for headless mode
	run_or_open = "run --browser chrome" if headless else "open"
	formatted_command = f"{site_env} {password_env} {coverage_env} {cypress_path} {run_or_open}"

	if parallel:
		formatted_command += " --parallel"

	if ci_build_id:
		formatted_command += f" --ci-build-id {ci_build_id}"

	if cypressargs:
		formatted_command += " " + " ".join(cypressargs)

	click.secho("Running Cypress...", fg="yellow")
	netmanthan.commands.popen(formatted_command, cwd=app_base_path, raise_err=True)


@click.command("serve")
@click.option("--port", default=8000)
@click.option("--profile", is_flag=True, default=False)
@click.option("--noreload", "no_reload", is_flag=True, default=False)
@click.option("--nothreading", "no_threading", is_flag=True, default=False)
@click.option("--with-coverage", is_flag=True, default=False)
@pass_context
def serve(
	context,
	port=None,
	profile=False,
	no_reload=False,
	no_threading=False,
	sites_path=".",
	site=None,
	with_coverage=False,
):
	"Start development web server"
	import netmanthan.app

	if not context.sites:
		site = None
	else:
		site = context.sites[0]
	with CodeCoverage(with_coverage, "netmanthan"):
		if with_coverage:
			# unable to track coverage with threading enabled
			no_threading = True
			no_reload = True
		netmanthan.app.serve(
			port=port,
			profile=profile,
			no_reload=no_reload,
			no_threading=no_threading,
			site=site,
			sites_path=".",
		)


@click.command("request")
@click.option("--args", help="arguments like `?cmd=test&key=value` or `/api/request/method?..`")
@click.option("--path", help="path to request JSON")
@pass_context
def request(context, args=None, path=None):
	"Run a request as an admin"
	import netmanthan.api
	import netmanthan.handler

	for site in context.sites:
		try:
			netmanthan.init(site=site)
			netmanthan.connect()
			if args:
				if "?" in args:
					netmanthan.local.form_dict = netmanthan._dict([a.split("=") for a in args.split("?")[-1].split("&")])
				else:
					netmanthan.local.form_dict = netmanthan._dict()

				if args.startswith("/api/method"):
					netmanthan.local.form_dict.cmd = args.split("?", 1)[0].split("/")[-1]
			elif path:
				with open(os.path.join("..", path)) as f:
					args = json.loads(f.read())

				netmanthan.local.form_dict = netmanthan._dict(args)

			netmanthan.handler.execute_cmd(netmanthan.form_dict.cmd)

			print(netmanthan.response)
		finally:
			netmanthan.destroy()
	if not context.sites:
		raise SiteNotSpecifiedError


@click.command("make-app")
@click.argument("destination")
@click.argument("app_name")
@click.option(
	"--no-git", is_flag=True, default=False, help="Do not initialize git repository for the app"
)
def make_app(destination, app_name, no_git=False):
	"Creates a boilerplate app"
	from netmanthan.utils.boilerplate import make_boilerplate

	make_boilerplate(destination, app_name, no_git=no_git)


@click.command("create-patch")
def create_patch():
	"Creates a new patch interactively"
	from netmanthan.utils.boilerplate import PatchCreator

	pc = PatchCreator()
	pc.fetch_user_inputs()
	pc.create_patch_file()


@click.command("set-config")
@click.argument("key")
@click.argument("value")
@click.option(
	"-g", "--global", "global_", is_flag=True, default=False, help="Set value in bench config"
)
@click.option("-p", "--parse", is_flag=True, default=False, help="Evaluate as Python Object")
@click.option("--as-dict", is_flag=True, default=False, help="Legacy: Evaluate as Python Object")
@pass_context
def set_config(context, key, value, global_=False, parse=False, as_dict=False):
	"Insert/Update a value in site_config.json"
	from netmanthan.installer import update_site_config

	if as_dict:
		from netmanthan.utils.commands import warn

		warn(
			"--as-dict will be deprecated in v14. Use --parse instead", category=PendingDeprecationWarning
		)
		parse = as_dict

	if parse:
		import ast

		value = ast.literal_eval(value)

	if global_:
		sites_path = os.getcwd()
		common_site_config_path = os.path.join(sites_path, "common_site_config.json")
		update_site_config(key, value, validate=False, site_config_path=common_site_config_path)
	else:
		for site in context.sites:
			netmanthan.init(site=site)
			update_site_config(key, value, validate=False)
			netmanthan.destroy()


@click.command("version")
@click.option(
	"-f",
	"--format",
	"output",
	type=click.Choice(["plain", "table", "json", "legacy"]),
	help="Output format",
	default="legacy",
)
def get_version(output):
	"""Show the versions of all the installed apps."""
	from git import Repo
	from git.exc import InvalidGitRepositoryError

	from netmanthan.utils.change_log import get_app_branch
	from netmanthan.utils.commands import render_table

	netmanthan.init("")
	data = []

	for app in sorted(netmanthan.get_all_apps()):
		module = netmanthan.get_module(app)
		app_hooks = netmanthan.get_module(app + ".hooks")

		app_info = netmanthan._dict()

		try:
			app_info.commit = Repo(netmanthan.get_app_path(app, "..")).head.object.hexsha[:7]
		except InvalidGitRepositoryError:
			app_info.commit = ""

		app_info.app = app
		app_info.branch = get_app_branch(app)
		app_info.version = getattr(app_hooks, f"{app_info.branch}_version", None) or module.__version__

		data.append(app_info)

	{
		"legacy": lambda: [click.echo(f"{app_info.app} {app_info.version}") for app_info in data],
		"plain": lambda: [
			click.echo(f"{app_info.app} {app_info.version} {app_info.branch} ({app_info.commit})")
			for app_info in data
		],
		"table": lambda: render_table(
			[["App", "Version", "Branch", "Commit"]]
			+ [[app_info.app, app_info.version, app_info.branch, app_info.commit] for app_info in data]
		),
		"json": lambda: click.echo(json.dumps(data, indent=4)),
	}[output]()


@click.command("rebuild-global-search")
@click.option(
	"--static-pages", is_flag=True, default=False, help="Rebuild global search for static pages"
)
@pass_context
def rebuild_global_search(context, static_pages=False):
	"""Setup help table in the current site (called after migrate)"""
	from netmanthan.utils.global_search import (
		add_route_to_global_search,
		get_doctypes_with_global_search,
		get_routes_to_index,
		rebuild_for_doctype,
		sync_global_search,
	)

	for site in context.sites:
		try:
			netmanthan.init(site)
			netmanthan.connect()

			if static_pages:
				routes = get_routes_to_index()
				for i, route in enumerate(routes):
					add_route_to_global_search(route)
					netmanthan.local.request = None
					update_progress_bar("Rebuilding Global Search", i, len(routes))
				sync_global_search()
			else:
				doctypes = get_doctypes_with_global_search()
				for i, doctype in enumerate(doctypes):
					rebuild_for_doctype(doctype)
					update_progress_bar("Rebuilding Global Search", i, len(doctypes))

		finally:
			netmanthan.destroy()
	if not context.sites:
		raise SiteNotSpecifiedError


commands = [
	build,
	clear_cache,
	clear_website_cache,
	database,
	transform_database,
	jupyter,
	console,
	destroy_all_sessions,
	execute,
	export_csv,
	export_doc,
	export_fixtures,
	export_json,
	get_version,
	import_csv,
	data_import,
	import_doc,
	make_app,
	create_patch,
	mariadb,
	postgres,
	request,
	reset_perms,
	run_tests,
	run_ui_tests,
	serve,
	set_config,
	show_config,
	watch,
	bulk_rename,
	add_to_email_queue,
	rebuild_global_search,
	run_parallel_tests,
]
