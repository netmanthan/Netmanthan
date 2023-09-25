// Copyright (c) 2015, netmanthan Technologies Pvt. Ltd. and Contributors
// MIT License. See license.txt
/* eslint-disable no-console */

// __('Modules') __('Domains') __('Places') __('Administration') # for translation, don't remove

netmanthan.start_app = function () {
	if (!netmanthan.Application) return;
	netmanthan.assets.check();
	netmanthan.provide("netmanthan.app");
	netmanthan.provide("netmanthan.desk");
	netmanthan.app = new netmanthan.Application();
};

$(document).ready(function () {
	if (!netmanthan.utils.supportsES6) {
		netmanthan.msgprint({
			indicator: "red",
			title: __("Browser not supported"),
			message: __(
				"Some of the features might not work in your browser. Please update your browser to the latest version."
			),
		});
	}
	netmanthan.start_app();
});

netmanthan.Application = class Application {
	constructor() {
		this.startup();
	}

	startup() {
		netmanthan.socketio.init();
		netmanthan.model.init();

		this.setup_netmanthan_vue();
		this.load_bootinfo();
		this.load_user_permissions();
		this.make_nav_bar();
		this.set_favicon();
		this.setup_analytics();
		this.set_fullwidth_if_enabled();
		this.add_browser_class();
		this.setup_energy_point_listeners();
		this.setup_copy_doc_listener();

		netmanthan.ui.keys.setup();

		netmanthan.ui.keys.add_shortcut({
			shortcut: "shift+ctrl+g",
			description: __("Switch Theme"),
			action: () => {
				if (netmanthan.theme_switcher && netmanthan.theme_switcher.dialog.is_visible) {
					netmanthan.theme_switcher.hide();
				} else {
					netmanthan.theme_switcher = new netmanthan.ui.ThemeSwitcher();
					netmanthan.theme_switcher.show();
				}
			},
		});

		netmanthan.ui.add_system_theme_switch_listener();
		const root = document.documentElement;

		const observer = new MutationObserver(() => {
			netmanthan.ui.set_theme();
		});
		observer.observe(root, {
			attributes: true,
			attributeFilter: ["data-theme-mode"],
		});

		netmanthan.ui.set_theme();

		// page container
		this.make_page_container();
		if (
			!window.Cypress &&
			netmanthan.boot.onboarding_tours &&
			netmanthan.boot.user.onboarding_status != null
		) {
			let pending_tours =
				netmanthan.boot.onboarding_tours.findIndex((tour) => {
					netmanthan.boot.user.onboarding_status[tour[0]]?.is_complete == true;
				}) == -1;
			if (pending_tours && netmanthan.boot.onboarding_tours.length > 0) {
				netmanthan.require("onboarding_tours.bundle.js", () => {
					netmanthan.utils.sleep(1000).then(() => {
						netmanthan.ui.init_onboarding_tour();
					});
				});
			}
		}
		this.set_route();

		// trigger app startup
		$(document).trigger("startup");

		$(document).trigger("app_ready");

		if (netmanthan.boot.messages) {
			netmanthan.msgprint(netmanthan.boot.messages);
		}

		if (netmanthan.user_roles.includes("System Manager")) {
			// delayed following requests to make boot faster
			setTimeout(() => {
				this.show_change_log();
				this.show_update_available();
			}, 1000);
		}

		if (!netmanthan.boot.developer_mode) {
			let console_security_message = __(
				"Using this console may allow attackers to impersonate you and steal your information. Do not enter or paste code that you do not understand."
			);
			console.log(`%c${console_security_message}`, "font-size: large");
		}

		this.show_notes();

		if (netmanthan.ui.startup_setup_dialog && !netmanthan.boot.setup_complete) {
			netmanthan.ui.startup_setup_dialog.pre_show();
			netmanthan.ui.startup_setup_dialog.show();
		}

		netmanthan.realtime.on("version-update", function () {
			var dialog = netmanthan.msgprint({
				message: __(
					"The application has been updated to a new version, please refresh this page"
				),
				indicator: "green",
				title: __("Version Updated"),
			});
			dialog.set_primary_action(__("Refresh"), function () {
				location.reload(true);
			});
			dialog.get_close_btn().toggle(false);
		});

		// listen to build errors
		this.setup_build_events();

		if (netmanthan.sys_defaults.email_user_password) {
			var email_list = netmanthan.sys_defaults.email_user_password.split(",");
			for (var u in email_list) {
				if (email_list[u] === netmanthan.user.name) {
					this.set_password(email_list[u]);
				}
			}
		}

		// REDESIGN-TODO: Fix preview popovers
		this.link_preview = new netmanthan.ui.LinkPreview();
	}

	set_route() {
		if (netmanthan.boot && localStorage.getItem("session_last_route")) {
			netmanthan.set_route(localStorage.getItem("session_last_route"));
			localStorage.removeItem("session_last_route");
		} else {
			// route to home page
			netmanthan.router.route();
		}
		netmanthan.router.on("change", () => {
			$(".tooltip").hide();
		});
	}

	setup_netmanthan_vue() {
		Vue.prototype.__ = window.__;
		Vue.prototype.netmanthan = window.netmanthan;
	}

	set_password(user) {
		var me = this;
		netmanthan.call({
			method: "netmanthan.core.doctype.user.user.get_email_awaiting",
			args: {
				user: user,
			},
			callback: function (email_account) {
				email_account = email_account["message"];
				if (email_account) {
					var i = 0;
					if (i < email_account.length) {
						me.email_password_prompt(email_account, user, i);
					}
				}
			},
		});
	}

	email_password_prompt(email_account, user, i) {
		var me = this;
		const email_id = email_account[i]["email_id"];
		let d = new netmanthan.ui.Dialog({
			title: __("Password missing in Email Account"),
			fields: [
				{
					fieldname: "password",
					fieldtype: "Password",
					label: __(
						"Please enter the password for: <b>{0}</b>",
						[email_id],
						"Email Account"
					),
					reqd: 1,
				},
				{
					fieldname: "submit",
					fieldtype: "Button",
					label: __("Submit", null, "Submit password for Email Account"),
				},
			],
		});
		d.get_input("submit").on("click", function () {
			//setup spinner
			d.hide();
			var s = new netmanthan.ui.Dialog({
				title: __("Checking one moment"),
				fields: [
					{
						fieldtype: "HTML",
						fieldname: "checking",
					},
				],
			});
			s.fields_dict.checking.$wrapper.html('<i class="fa fa-spinner fa-spin fa-4x"></i>');
			s.show();
			netmanthan.call({
				method: "netmanthan.email.doctype.email_account.email_account.set_email_password",
				args: {
					email_account: email_account[i]["email_account"],
					password: d.get_value("password"),
				},
				callback: function (passed) {
					s.hide();
					d.hide(); //hide waiting indication
					if (!passed["message"]) {
						netmanthan.show_alert(
							{ message: __("Login Failed please try again"), indicator: "error" },
							5
						);
						me.email_password_prompt(email_account, user, i);
					} else {
						if (i + 1 < email_account.length) {
							i = i + 1;
							me.email_password_prompt(email_account, user, i);
						}
					}
				},
			});
		});
		d.show();
	}
	load_bootinfo() {
		if (netmanthan.boot) {
			this.setup_workspaces();
			netmanthan.model.sync(netmanthan.boot.docs);
			this.check_metadata_cache_status();
			this.set_globals();
			this.sync_pages();
			netmanthan.router.setup();
			this.setup_moment();
			if (netmanthan.boot.print_css) {
				netmanthan.dom.set_style(netmanthan.boot.print_css, "print-style");
			}
			netmanthan.user.name = netmanthan.boot.user.name;
			netmanthan.router.setup();
		} else {
			this.set_as_guest();
		}
	}

	setup_workspaces() {
		netmanthan.modules = {};
		netmanthan.workspaces = {};
		for (let page of netmanthan.boot.allowed_workspaces || []) {
			netmanthan.modules[page.module] = page;
			netmanthan.workspaces[netmanthan.router.slug(page.name)] = page;
		}
	}

	load_user_permissions() {
		netmanthan.defaults.load_user_permission_from_boot();

		netmanthan.realtime.on(
			"update_user_permissions",
			netmanthan.utils.debounce(() => {
				netmanthan.defaults.update_user_permissions();
			}, 500)
		);
	}

	check_metadata_cache_status() {
		if (netmanthan.boot.metadata_version != localStorage.metadata_version) {
			netmanthan.assets.clear_local_storage();
			netmanthan.assets.init_local_storage();
		}
	}

	set_globals() {
		netmanthan.session.user = netmanthan.boot.user.name;
		netmanthan.session.logged_in_user = netmanthan.boot.user.name;
		netmanthan.session.user_email = netmanthan.boot.user.email;
		netmanthan.session.user_fullname = netmanthan.user_info().fullname;

		netmanthan.user_defaults = netmanthan.boot.user.defaults;
		netmanthan.user_roles = netmanthan.boot.user.roles;
		netmanthan.sys_defaults = netmanthan.boot.sysdefaults;

		netmanthan.ui.py_date_format = netmanthan.boot.sysdefaults.date_format
			.replace("dd", "%d")
			.replace("mm", "%m")
			.replace("yyyy", "%Y");
		netmanthan.boot.user.last_selected_values = {};

		// Proxy for user globals
		Object.defineProperties(window, {
			user: {
				get: function () {
					console.warn(
						"Please use `netmanthan.session.user` instead of `user`. It will be deprecated soon."
					);
					return netmanthan.session.user;
				},
			},
			user_fullname: {
				get: function () {
					console.warn(
						"Please use `netmanthan.session.user_fullname` instead of `user_fullname`. It will be deprecated soon."
					);
					return netmanthan.session.user;
				},
			},
			user_email: {
				get: function () {
					console.warn(
						"Please use `netmanthan.session.user_email` instead of `user_email`. It will be deprecated soon."
					);
					return netmanthan.session.user_email;
				},
			},
			user_defaults: {
				get: function () {
					console.warn(
						"Please use `netmanthan.user_defaults` instead of `user_defaults`. It will be deprecated soon."
					);
					return netmanthan.user_defaults;
				},
			},
			roles: {
				get: function () {
					console.warn(
						"Please use `netmanthan.user_roles` instead of `roles`. It will be deprecated soon."
					);
					return netmanthan.user_roles;
				},
			},
			sys_defaults: {
				get: function () {
					console.warn(
						"Please use `netmanthan.sys_defaults` instead of `sys_defaults`. It will be deprecated soon."
					);
					return netmanthan.user_roles;
				},
			},
		});
	}
	sync_pages() {
		// clear cached pages if timestamp is not found
		if (localStorage["page_info"]) {
			netmanthan.boot.allowed_pages = [];
			var page_info = JSON.parse(localStorage["page_info"]);
			$.each(netmanthan.boot.page_info, function (name, p) {
				if (!page_info[name] || page_info[name].modified != p.modified) {
					delete localStorage["_page:" + name];
				}
				netmanthan.boot.allowed_pages.push(name);
			});
		} else {
			netmanthan.boot.allowed_pages = Object.keys(netmanthan.boot.page_info);
		}
		localStorage["page_info"] = JSON.stringify(netmanthan.boot.page_info);
	}
	set_as_guest() {
		netmanthan.session.user = "Guest";
		netmanthan.session.user_email = "";
		netmanthan.session.user_fullname = "Guest";

		netmanthan.user_defaults = {};
		netmanthan.user_roles = ["Guest"];
		netmanthan.sys_defaults = {};
	}
	make_page_container() {
		if ($("#body").length) {
			$(".splash").remove();
			netmanthan.temp_container = $("<div id='temp-container' style='display: none;'>").appendTo(
				"body"
			);
			netmanthan.container = new netmanthan.views.Container();
		}
	}
	make_nav_bar() {
		// toolbar
		if (netmanthan.boot && netmanthan.boot.home_page !== "setup-wizard") {
			netmanthan.netmanthan_toolbar = new netmanthan.ui.toolbar.Toolbar();
		}
	}
	logout() {
		var me = this;
		me.logged_out = true;
		return netmanthan.call({
			method: "logout",
			callback: function (r) {
				if (r.exc) {
					return;
				}
				me.redirect_to_login();
			},
		});
	}
	handle_session_expired() {
		if (!netmanthan.app.session_expired_dialog) {
			var dialog = new netmanthan.ui.Dialog({
				title: __("Session Expired"),
				keep_open: true,
				fields: [
					{
						fieldtype: "Password",
						fieldname: "password",
						label: __("Please Enter Your Password to Continue"),
					},
				],
				onhide: () => {
					if (!dialog.logged_in) {
						netmanthan.app.redirect_to_login();
					}
				},
			});
			dialog.get_field("password").disable_password_checks();
			dialog.set_primary_action(__("Login"), () => {
				dialog.set_message(__("Authenticating..."));
				netmanthan.call({
					method: "login",
					args: {
						usr: netmanthan.session.user,
						pwd: dialog.get_values().password,
					},
					callback: (r) => {
						if (r.message === "Logged In") {
							dialog.logged_in = true;

							// revert backdrop
							$(".modal-backdrop").css({
								opacity: "",
								"background-color": "#334143",
							});
						}
						dialog.hide();
					},
					statusCode: () => {
						dialog.hide();
					},
				});
			});
			netmanthan.app.session_expired_dialog = dialog;
		}
		if (!netmanthan.app.session_expired_dialog.display) {
			netmanthan.app.session_expired_dialog.show();
			// add backdrop
			$(".modal-backdrop").css({
				opacity: 1,
				"background-color": "#4B4C9D",
			});
		}
	}
	redirect_to_login() {
		window.location.href = "/";
	}
	set_favicon() {
		var link = $('link[type="image/x-icon"]').remove().attr("href");
		$('<link rel="shortcut icon" href="' + link + '" type="image/x-icon">').appendTo("head");
		$('<link rel="icon" href="' + link + '" type="image/x-icon">').appendTo("head");
	}
	trigger_primary_action() {
		// to trigger change event on active input before triggering primary action
		$(document.activeElement).blur();
		// wait for possible JS validations triggered after blur (it might change primary button)
		setTimeout(() => {
			if (window.cur_dialog && cur_dialog.display) {
				// trigger primary
				cur_dialog.get_primary_btn().trigger("click");
			} else if (cur_frm && cur_frm.page.btn_primary.is(":visible")) {
				cur_frm.page.btn_primary.trigger("click");
			} else if (netmanthan.container.page.save_action) {
				netmanthan.container.page.save_action();
			}
		}, 100);
	}

	show_change_log() {
		var me = this;
		let change_log = netmanthan.boot.change_log;

		// netmanthan.boot.change_log = [{
		// 	"change_log": [
		// 		[<version>, <change_log in markdown>],
		// 		[<version>, <change_log in markdown>],
		// 	],
		// 	"description": "ERP made simple",
		// 	"title": "ERPNext",
		// 	"version": "12.2.0"
		// }];

		if (
			!Array.isArray(change_log) ||
			!change_log.length ||
			window.Cypress ||
			cint(netmanthan.boot.sysdefaults.disable_change_log_notification)
		) {
			return;
		}

		// Iterate over changelog
		var change_log_dialog = netmanthan.msgprint({
			message: netmanthan.render_template("change_log", { change_log: change_log }),
			title: __("Updated To A New Version 🎉"),
			wide: true,
		});
		change_log_dialog.keep_open = true;
		change_log_dialog.custom_onhide = function () {
			netmanthan.call({
				method: "netmanthan.utils.change_log.update_last_known_versions",
			});
			me.show_notes();
		};
	}

	show_update_available() {
		if (netmanthan.boot.sysdefaults.disable_system_update_notification) return;

		netmanthan.call({
			method: "netmanthan.utils.change_log.show_update_popup",
		});
	}

	setup_analytics() {
		if (window.mixpanel) {
			window.mixpanel.identify(netmanthan.session.user);
			window.mixpanel.people.set({
				$first_name: netmanthan.boot.user.first_name,
				$last_name: netmanthan.boot.user.last_name,
				$created: netmanthan.boot.user.creation,
				$email: netmanthan.session.user,
			});
		}
	}

	add_browser_class() {
		$("html").addClass(netmanthan.utils.get_browser().name.toLowerCase());
	}

	set_fullwidth_if_enabled() {
		netmanthan.ui.toolbar.set_fullwidth_if_enabled();
	}

	show_notes() {
		var me = this;
		if (netmanthan.boot.notes.length) {
			netmanthan.boot.notes.forEach(function (note) {
				if (!note.seen || note.notify_on_every_login) {
					var d = netmanthan.msgprint({ message: note.content, title: note.title });
					d.keep_open = true;
					d.custom_onhide = function () {
						note.seen = true;

						// Mark note as read if the Notify On Every Login flag is not set
						if (!note.notify_on_every_login) {
							netmanthan.call({
								method: "netmanthan.desk.doctype.note.note.mark_as_seen",
								args: {
									note: note.name,
								},
							});
						}

						// next note
						me.show_notes();
					};
				}
			});
		}
	}

	setup_build_events() {
		if (netmanthan.boot.developer_mode) {
			netmanthan.require("build_events.bundle.js");
		}
	}

	setup_energy_point_listeners() {
		netmanthan.realtime.on("energy_point_alert", (message) => {
			netmanthan.show_alert(message);
		});
	}

	setup_copy_doc_listener() {
		$("body").on("paste", (e) => {
			try {
				let pasted_data = netmanthan.utils.get_clipboard_data(e);
				let doc = JSON.parse(pasted_data);
				if (doc.doctype) {
					e.preventDefault();
					const sleep = netmanthan.utils.sleep;

					netmanthan.dom.freeze(__("Creating {0}", [doc.doctype]) + "...");
					// to avoid abrupt UX
					// wait for activity feedback
					sleep(500).then(() => {
						let res = netmanthan.model.with_doctype(doc.doctype, () => {
							let newdoc = netmanthan.model.copy_doc(doc);
							newdoc.__newname = doc.name;
							delete doc.name;
							newdoc.idx = null;
							newdoc.__run_link_triggers = false;
							netmanthan.set_route("Form", newdoc.doctype, newdoc.name);
							netmanthan.dom.unfreeze();
						});
						res && res.fail(netmanthan.dom.unfreeze);
					});
				}
			} catch (e) {
				//
			}
		});
	}

	setup_moment() {
		moment.updateLocale("en", {
			week: {
				dow: netmanthan.datetime.get_first_day_of_the_week_index(),
			},
		});
		moment.locale("en");
		moment.user_utc_offset = moment().utcOffset();
		if (netmanthan.boot.timezone_info) {
			moment.tz.add(netmanthan.boot.timezone_info);
		}
	}
};

netmanthan.get_module = function (m, default_module) {
	var module = netmanthan.modules[m] || default_module;
	if (!module) {
		return;
	}

	if (module._setup) {
		return module;
	}

	if (!module.label) {
		module.label = m;
	}

	if (!module._label) {
		module._label = __(module.label);
	}

	module._setup = true;

	return module;
};
