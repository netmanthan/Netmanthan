from . import __version__ as app_version

app_name = "netmanthan"
app_title = "netmanthan Framework"
app_publisher = "netmanthan Technologies"
app_description = "Full stack web framework with Python, Javascript, MariaDB, Redis, Node"
source_link = "https://github.com/netmanthan/netmanthan"
app_license = "MIT"
app_logo_url = "/assets/netmanthan/images/netmanthan-framework-logo.svg"

develop_version = "14.x.x-develop"

app_email = "developers@netmanthan.io"

docs_app = "netmanthan_docs"

translator_url = "https://translate.erpnext.com"

before_install = "netmanthan.utils.install.before_install"
after_install = "netmanthan.utils.install.after_install"

page_js = {"setup-wizard": "public/js/netmanthan/setup_wizard.js"}

# website
app_include_js = [
	"libs.bundle.js",
	"desk.bundle.js",
	"list.bundle.js",
	"form.bundle.js",
	"controls.bundle.js",
	"report.bundle.js",
	"telemetry.bundle.js",
]
app_include_css = [
	"desk.bundle.css",
	"report.bundle.css",
]

doctype_js = {
	"Web Page": "public/js/netmanthan/utils/web_template.js",
	"Website Settings": "public/js/netmanthan/utils/web_template.js",
}

web_include_js = ["website_script.js"]

web_include_css = []

email_css = ["email.bundle.css"]

website_route_rules = [
	{"from_route": "/blog/<category>", "to_route": "Blog Post"},
	{"from_route": "/kb/<category>", "to_route": "Help Article"},
	{"from_route": "/newsletters", "to_route": "Newsletter"},
	{"from_route": "/profile", "to_route": "me"},
	{"from_route": "/app/<path:app_path>", "to_route": "app"},
]

website_redirects = [
	{"source": r"/desk(.*)", "target": r"/app\1"},
]

base_template = "templates/base.html"

write_file_keys = ["file_url", "file_name"]

notification_config = "netmanthan.core.notifications.get_notification_config"

before_tests = "netmanthan.utils.install.before_tests"

email_append_to = ["Event", "ToDo", "Communication"]

calendars = ["Event"]

leaderboards = "netmanthan.desk.leaderboard.get_leaderboards"

# login

on_session_creation = [
	"netmanthan.core.doctype.activity_log.feed.login_feed",
	"netmanthan.core.doctype.user.user.notify_admin_access_to_system_manager",
]

on_logout = (
	"netmanthan.core.doctype.session_default_settings.session_default_settings.clear_session_defaults"
)

# permissions

permission_query_conditions = {
	"Event": "netmanthan.desk.doctype.event.event.get_permission_query_conditions",
	"ToDo": "netmanthan.desk.doctype.todo.todo.get_permission_query_conditions",
	"User": "netmanthan.core.doctype.user.user.get_permission_query_conditions",
	"Dashboard Settings": "netmanthan.desk.doctype.dashboard_settings.dashboard_settings.get_permission_query_conditions",
	"Notification Log": "netmanthan.desk.doctype.notification_log.notification_log.get_permission_query_conditions",
	"Dashboard": "netmanthan.desk.doctype.dashboard.dashboard.get_permission_query_conditions",
	"Dashboard Chart": "netmanthan.desk.doctype.dashboard_chart.dashboard_chart.get_permission_query_conditions",
	"Number Card": "netmanthan.desk.doctype.number_card.number_card.get_permission_query_conditions",
	"Notification Settings": "netmanthan.desk.doctype.notification_settings.notification_settings.get_permission_query_conditions",
	"Note": "netmanthan.desk.doctype.note.note.get_permission_query_conditions",
	"Kanban Board": "netmanthan.desk.doctype.kanban_board.kanban_board.get_permission_query_conditions",
	"Contact": "netmanthan.contacts.address_and_contact.get_permission_query_conditions_for_contact",
	"Address": "netmanthan.contacts.address_and_contact.get_permission_query_conditions_for_address",
	"Communication": "netmanthan.core.doctype.communication.communication.get_permission_query_conditions_for_communication",
	"Workflow Action": "netmanthan.workflow.doctype.workflow_action.workflow_action.get_permission_query_conditions",
	"Prepared Report": "netmanthan.core.doctype.prepared_report.prepared_report.get_permission_query_condition",
	"File": "netmanthan.core.doctype.file.file.get_permission_query_conditions",
}

has_permission = {
	"Event": "netmanthan.desk.doctype.event.event.has_permission",
	"ToDo": "netmanthan.desk.doctype.todo.todo.has_permission",
	"User": "netmanthan.core.doctype.user.user.has_permission",
	"Note": "netmanthan.desk.doctype.note.note.has_permission",
	"Dashboard Chart": "netmanthan.desk.doctype.dashboard_chart.dashboard_chart.has_permission",
	"Number Card": "netmanthan.desk.doctype.number_card.number_card.has_permission",
	"Kanban Board": "netmanthan.desk.doctype.kanban_board.kanban_board.has_permission",
	"Contact": "netmanthan.contacts.address_and_contact.has_permission",
	"Address": "netmanthan.contacts.address_and_contact.has_permission",
	"Communication": "netmanthan.core.doctype.communication.communication.has_permission",
	"Workflow Action": "netmanthan.workflow.doctype.workflow_action.workflow_action.has_permission",
	"File": "netmanthan.core.doctype.file.file.has_permission",
	"Prepared Report": "netmanthan.core.doctype.prepared_report.prepared_report.has_permission",
}

has_website_permission = {
	"Address": "netmanthan.contacts.doctype.address.address.has_website_permission"
}

jinja = {
	"methods": "netmanthan.utils.jinja_globals",
	"filters": [
		"netmanthan.utils.data.global_date_format",
		"netmanthan.utils.markdown",
		"netmanthan.website.utils.get_shade",
		"netmanthan.website.utils.abs_url",
	],
}

standard_queries = {"User": "netmanthan.core.doctype.user.user.user_query"}

doc_events = {
	"*": {
		"after_insert": [
			"netmanthan.event_streaming.doctype.event_update_log.event_update_log.notify_consumers"
		],
		"on_update": [
			"netmanthan.desk.notifications.clear_doctype_notifications",
			"netmanthan.core.doctype.activity_log.feed.update_feed",
			"netmanthan.workflow.doctype.workflow_action.workflow_action.process_workflow_actions",
			"netmanthan.core.doctype.file.utils.attach_files_to_document",
			"netmanthan.event_streaming.doctype.event_update_log.event_update_log.notify_consumers",
			"netmanthan.automation.doctype.assignment_rule.assignment_rule.apply",
			"netmanthan.automation.doctype.assignment_rule.assignment_rule.update_due_date",
			"netmanthan.core.doctype.user_type.user_type.apply_permissions_for_non_standard_user_type",
		],
		"after_rename": "netmanthan.desk.notifications.clear_doctype_notifications",
		"on_cancel": [
			"netmanthan.desk.notifications.clear_doctype_notifications",
			"netmanthan.workflow.doctype.workflow_action.workflow_action.process_workflow_actions",
			"netmanthan.event_streaming.doctype.event_update_log.event_update_log.notify_consumers",
			"netmanthan.automation.doctype.assignment_rule.assignment_rule.apply",
		],
		"on_trash": [
			"netmanthan.desk.notifications.clear_doctype_notifications",
			"netmanthan.workflow.doctype.workflow_action.workflow_action.process_workflow_actions",
			"netmanthan.event_streaming.doctype.event_update_log.event_update_log.notify_consumers",
		],
		"on_update_after_submit": [
			"netmanthan.workflow.doctype.workflow_action.workflow_action.process_workflow_actions",
			"netmanthan.automation.doctype.assignment_rule.assignment_rule.apply",
			"netmanthan.automation.doctype.assignment_rule.assignment_rule.update_due_date",
		],
		"on_change": [
			"netmanthan.social.doctype.energy_point_rule.energy_point_rule.process_energy_points",
			"netmanthan.automation.doctype.milestone_tracker.milestone_tracker.evaluate_milestone",
		],
	},
	"Event": {
		"after_insert": "netmanthan.integrations.doctype.google_calendar.google_calendar.insert_event_in_google_calendar",
		"on_update": "netmanthan.integrations.doctype.google_calendar.google_calendar.update_event_in_google_calendar",
		"on_trash": "netmanthan.integrations.doctype.google_calendar.google_calendar.delete_event_from_google_calendar",
	},
	"Contact": {
		"after_insert": "netmanthan.integrations.doctype.google_contacts.google_contacts.insert_contacts_to_google_contacts",
		"on_update": "netmanthan.integrations.doctype.google_contacts.google_contacts.update_contacts_to_google_contacts",
	},
	"DocType": {
		"on_update": "netmanthan.cache_manager.build_domain_restriced_doctype_cache",
	},
	"Page": {
		"on_update": "netmanthan.cache_manager.build_domain_restriced_page_cache",
	},
}

scheduler_events = {
	"cron": {
		"0/15 * * * *": [
			"netmanthan.oauth.delete_oauth2_data",
			"netmanthan.website.doctype.web_page.web_page.check_publish_status",
			"netmanthan.twofactor.delete_all_barcodes_for_users",
		],
		"0/10 * * * *": [
			"netmanthan.email.doctype.email_account.email_account.pull",
		],
		# Hourly but offset by 30 minutes
		# "30 * * * *": [
		#
		# ],
		# Daily but offset by 45 minutes
		"45 0 * * *": [
			"netmanthan.core.doctype.log_settings.log_settings.run_log_clean_up",
		],
	},
	"all": [
		"netmanthan.email.queue.flush",
		"netmanthan.email.doctype.email_account.email_account.notify_unreplied",
		"netmanthan.utils.global_search.sync_global_search",
		"netmanthan.monitor.flush",
	],
	"hourly": [
		"netmanthan.model.utils.link_count.update_link_count",
		"netmanthan.model.utils.user_settings.sync_user_settings",
		"netmanthan.utils.error.collect_error_snapshots",
		"netmanthan.desk.page.backups.backups.delete_downloadable_backups",
		"netmanthan.deferred_insert.save_to_db",
		"netmanthan.desk.form.document_follow.send_hourly_updates",
		"netmanthan.integrations.doctype.google_calendar.google_calendar.sync",
		"netmanthan.email.doctype.newsletter.newsletter.send_scheduled_email",
		"netmanthan.website.doctype.personal_data_deletion_request.personal_data_deletion_request.process_data_deletion_request",
	],
	"daily": [
		"netmanthan.email.queue.set_expiry_for_email_queue",
		"netmanthan.desk.notifications.clear_notifications",
		"netmanthan.desk.doctype.event.event.send_event_digest",
		"netmanthan.sessions.clear_expired_sessions",
		"netmanthan.email.doctype.notification.notification.trigger_daily_alerts",
		"netmanthan.website.doctype.personal_data_deletion_request.personal_data_deletion_request.remove_unverified_record",
		"netmanthan.desk.form.document_follow.send_daily_updates",
		"netmanthan.social.doctype.energy_point_settings.energy_point_settings.allocate_review_points",
		"netmanthan.integrations.doctype.google_contacts.google_contacts.sync",
		"netmanthan.automation.doctype.auto_repeat.auto_repeat.make_auto_repeat_entry",
		"netmanthan.automation.doctype.auto_repeat.auto_repeat.set_auto_repeat_as_completed",
		"netmanthan.email.doctype.unhandled_email.unhandled_email.remove_old_unhandled_emails",
	],
	"daily_long": [
		"netmanthan.integrations.doctype.dropbox_settings.dropbox_settings.take_backups_daily",
		"netmanthan.utils.change_log.check_for_update",
		"netmanthan.integrations.doctype.s3_backup_settings.s3_backup_settings.take_backups_daily",
		"netmanthan.email.doctype.auto_email_report.auto_email_report.send_daily",
		"netmanthan.integrations.doctype.google_drive.google_drive.daily_backup",
	],
	"weekly_long": [
		"netmanthan.integrations.doctype.dropbox_settings.dropbox_settings.take_backups_weekly",
		"netmanthan.integrations.doctype.s3_backup_settings.s3_backup_settings.take_backups_weekly",
		"netmanthan.desk.form.document_follow.send_weekly_updates",
		"netmanthan.social.doctype.energy_point_log.energy_point_log.send_weekly_summary",
		"netmanthan.integrations.doctype.google_drive.google_drive.weekly_backup",
	],
	"monthly": [
		"netmanthan.email.doctype.auto_email_report.auto_email_report.send_monthly",
		"netmanthan.social.doctype.energy_point_log.energy_point_log.send_monthly_summary",
	],
	"monthly_long": [
		"netmanthan.integrations.doctype.s3_backup_settings.s3_backup_settings.take_backups_monthly"
	],
}

get_translated_dict = {
	("doctype", "System Settings"): "netmanthan.geo.country_info.get_translated_dict",
	("page", "setup-wizard"): "netmanthan.geo.country_info.get_translated_dict",
}

sounds = [
	{"name": "email", "src": "/assets/netmanthan/sounds/email.mp3", "volume": 0.1},
	{"name": "submit", "src": "/assets/netmanthan/sounds/submit.mp3", "volume": 0.1},
	{"name": "cancel", "src": "/assets/netmanthan/sounds/cancel.mp3", "volume": 0.1},
	{"name": "delete", "src": "/assets/netmanthan/sounds/delete.mp3", "volume": 0.05},
	{"name": "click", "src": "/assets/netmanthan/sounds/click.mp3", "volume": 0.05},
	{"name": "error", "src": "/assets/netmanthan/sounds/error.mp3", "volume": 0.1},
	{"name": "alert", "src": "/assets/netmanthan/sounds/alert.mp3", "volume": 0.2},
	# {"name": "chime", "src": "/assets/netmanthan/sounds/chime.mp3"},
]

setup_wizard_exception = [
	"netmanthan.desk.page.setup_wizard.setup_wizard.email_setup_wizard_exception",
	"netmanthan.desk.page.setup_wizard.setup_wizard.log_setup_wizard_exception",
]

before_migrate = []
after_migrate = ["netmanthan.website.doctype.website_theme.website_theme.after_migrate"]

otp_methods = ["OTP App", "Email", "SMS"]

user_data_fields = [
	{"doctype": "Access Log", "strict": True},
	{"doctype": "Activity Log", "strict": True},
	{"doctype": "Comment", "strict": True},
	{
		"doctype": "Contact",
		"filter_by": "email_id",
		"redact_fields": ["first_name", "last_name", "phone", "mobile_no"],
		"rename": True,
	},
	{"doctype": "Contact Email", "filter_by": "email_id"},
	{
		"doctype": "Address",
		"filter_by": "email_id",
		"redact_fields": [
			"address_title",
			"address_line1",
			"address_line2",
			"city",
			"county",
			"state",
			"pincode",
			"phone",
			"fax",
		],
	},
	{
		"doctype": "Communication",
		"filter_by": "sender",
		"redact_fields": ["sender_full_name", "phone_no", "content"],
	},
	{"doctype": "Communication", "filter_by": "recipients"},
	{"doctype": "Email Group Member", "filter_by": "email"},
	{"doctype": "Email Unsubscribe", "filter_by": "email", "partial": True},
	{"doctype": "Email Queue", "filter_by": "sender"},
	{"doctype": "Email Queue Recipient", "filter_by": "recipient"},
	{
		"doctype": "File",
		"filter_by": "attached_to_name",
		"redact_fields": ["file_name", "file_url"],
	},
	{
		"doctype": "User",
		"filter_by": "name",
		"redact_fields": [
			"email",
			"username",
			"first_name",
			"middle_name",
			"last_name",
			"full_name",
			"birth_date",
			"user_image",
			"phone",
			"mobile_no",
			"location",
			"banner_image",
			"interest",
			"bio",
			"email_signature",
		],
	},
	{"doctype": "Version", "strict": True},
]

global_search_doctypes = {
	"Default": [
		{"doctype": "Contact"},
		{"doctype": "Address"},
		{"doctype": "ToDo"},
		{"doctype": "Note"},
		{"doctype": "Event"},
		{"doctype": "Blog Post"},
		{"doctype": "Dashboard"},
		{"doctype": "Country"},
		{"doctype": "Currency"},
		{"doctype": "Newsletter"},
		{"doctype": "Letter Head"},
		{"doctype": "Workflow"},
		{"doctype": "Web Page"},
		{"doctype": "Web Form"},
	]
}

override_whitelisted_methods = {
	# Legacy File APIs
	"netmanthan.core.doctype.file.file.download_file": "download_file",
	"netmanthan.core.doctype.file.file.unzip_file": "netmanthan.core.api.file.unzip_file",
	"netmanthan.core.doctype.file.file.get_attached_images": "netmanthan.core.api.file.get_attached_images",
	"netmanthan.core.doctype.file.file.get_files_in_folder": "netmanthan.core.api.file.get_files_in_folder",
	"netmanthan.core.doctype.file.file.get_files_by_search_text": "netmanthan.core.api.file.get_files_by_search_text",
	"netmanthan.core.doctype.file.file.get_max_file_size": "netmanthan.core.api.file.get_max_file_size",
	"netmanthan.core.doctype.file.file.create_new_folder": "netmanthan.core.api.file.create_new_folder",
	"netmanthan.core.doctype.file.file.move_file": "netmanthan.core.api.file.move_file",
	"netmanthan.core.doctype.file.file.zip_files": "netmanthan.core.api.file.zip_files",
	# Legacy (& Consistency) OAuth2 APIs
	"netmanthan.www.login.login_via_google": "netmanthan.integrations.oauth2_logins.login_via_google",
	"netmanthan.www.login.login_via_github": "netmanthan.integrations.oauth2_logins.login_via_github",
	"netmanthan.www.login.login_via_facebook": "netmanthan.integrations.oauth2_logins.login_via_facebook",
	"netmanthan.www.login.login_via_netmanthan": "netmanthan.integrations.oauth2_logins.login_via_netmanthan",
	"netmanthan.www.login.login_via_office365": "netmanthan.integrations.oauth2_logins.login_via_office365",
	"netmanthan.www.login.login_via_salesforce": "netmanthan.integrations.oauth2_logins.login_via_salesforce",
	"netmanthan.www.login.login_via_fairlogin": "netmanthan.integrations.oauth2_logins.login_via_fairlogin",
}

ignore_links_on_delete = [
	"Communication",
	"ToDo",
	"DocShare",
	"Email Unsubscribe",
	"Activity Log",
	"File",
	"Version",
	"Document Follow",
	"Comment",
	"View Log",
	"Tag Link",
	"Notification Log",
	"Email Queue",
	"Document Share Key",
	"Integration Request",
	"Unhandled Email",
	"Webhook Request Log",
]

# Request Hooks
before_request = [
	"netmanthan.recorder.record",
	"netmanthan.monitor.start",
	"netmanthan.rate_limiter.apply",
]
after_request = ["netmanthan.rate_limiter.update", "netmanthan.monitor.stop", "netmanthan.recorder.dump"]

# Background Job Hooks
before_job = [
	"netmanthan.monitor.start",
]
after_job = [
	"netmanthan.monitor.stop",
	"netmanthan.utils.file_lock.release_document_locks",
]

extend_bootinfo = [
	"netmanthan.utils.telemetry.add_bootinfo",
	"netmanthan.core.doctype.user_permission.user_permission.send_user_permissions",
]
