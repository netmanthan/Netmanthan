// Copyright (c) 2015, netmanthan Technologies Pvt. Ltd. and Contributors
// MIT License. See license.txt

netmanthan.provide("netmanthan.messages");

import "./dialog";

netmanthan.messages.waiting = function (parent, msg) {
	return $(netmanthan.messages.get_waiting_message(msg)).appendTo(parent);
};

netmanthan.messages.get_waiting_message = function (msg) {
	return repl(
		'<div class="msg-box" style="width: 63%; margin: 30px auto;">\
		<p class="text-center">%(msg)s</p></div>',
		{ msg: msg }
	);
};

netmanthan.throw = function (msg) {
	if (typeof msg === "string") {
		msg = { message: msg, title: __("Error") };
	}
	if (!msg.indicator) msg.indicator = "red";
	netmanthan.msgprint(msg);
	throw new Error(msg.message);
};

netmanthan.confirm = function (message, confirm_action, reject_action) {
	var d = new netmanthan.ui.Dialog({
		title: __("Confirm", null, "Title of confirmation dialog"),
		primary_action_label: __("Yes", null, "Approve confirmation dialog"),
		primary_action: () => {
			confirm_action && confirm_action();
			d.hide();
		},
		secondary_action_label: __("No", null, "Dismiss confirmation dialog"),
		secondary_action: () => d.hide(),
	});

	d.$body.append(`<p class="netmanthan-confirm-message">${message}</p>`);
	d.show();

	// flag, used to bind "okay" on enter
	d.confirm_dialog = true;

	// no if closed without primary action
	if (reject_action) {
		d.onhide = () => {
			if (!d.primary_action_fulfilled) {
				reject_action();
			}
		};
	}

	return d;
};

netmanthan.warn = function (title, message_html, proceed_action, primary_label, is_minimizable) {
	const d = new netmanthan.ui.Dialog({
		title: title,
		indicator: "red",
		primary_action_label: primary_label,
		primary_action: () => {
			if (proceed_action) proceed_action();
			d.hide();
		},
		secondary_action_label: __("Cancel", null, "Secondary button in warning dialog"),
		secondary_action: () => d.hide(),
		minimizable: is_minimizable,
	});

	d.$body.append(`<div class="netmanthan-confirm-message">${message_html}</div>`);
	d.standard_actions.find(".btn-primary").removeClass("btn-primary").addClass("btn-danger");

	d.show();
	return d;
};

netmanthan.prompt = function (fields, callback, title, primary_label) {
	if (typeof fields === "string") {
		fields = [
			{
				label: fields,
				fieldname: "value",
				fieldtype: "Data",
				reqd: 1,
			},
		];
	}
	if (!$.isArray(fields)) fields = [fields];
	var d = new netmanthan.ui.Dialog({
		fields: fields,
		title: title || __("Enter Value", null, "Title of prompt dialog"),
	});
	d.set_primary_action(
		primary_label || __("Submit", null, "Primary action of prompt dialog"),
		function () {
			var values = d.get_values();
			if (!values) {
				return;
			}
			d.hide();
			callback(values);
		}
	);
	d.show();
	return d;
};

netmanthan.msgprint = function (msg, title, is_minimizable) {
	if (!msg) return;

	if ($.isPlainObject(msg)) {
		var data = msg;
	} else {
		// passed as JSON
		if (typeof msg === "string" && msg.substr(0, 1) === "{") {
			var data = JSON.parse(msg);
		} else {
			var data = { message: msg, title: title };
		}
	}

	if (!data.indicator) {
		data.indicator = "blue";
	}

	if (data.as_list) {
		const list_rows = data.message.map((m) => `<li>${m}</li>`).join("");
		data.message = `<ul style="padding-left: 20px">${list_rows}</ul>`;
	}

	if (data.as_table) {
		const rows = data.message
			.map((row) => {
				const cols = row.map((col) => `<td>${col}</td>`).join("");
				return `<tr>${cols}</tr>`;
			})
			.join("");
		data.message = `<table class="table table-bordered" style="margin: 0;">${rows}</table>`;
	}

	if (data.message instanceof Array) {
		let messages = data.message;
		const exceptions = messages.map((m) => JSON.parse(m)).filter((m) => m.raise_exception);

		// only show exceptions if any exceptions exist
		if (exceptions.length) {
			messages = exceptions;
		}

		messages.forEach(function (m) {
			netmanthan.msgprint(m);
		});
		return;
	}

	if (data.alert || data.toast) {
		netmanthan.show_alert(data);
		return;
	}

	if (!netmanthan.msg_dialog) {
		netmanthan.msg_dialog = new netmanthan.ui.Dialog({
			title: __("Message"),
			onhide: function () {
				if (netmanthan.msg_dialog.custom_onhide) {
					netmanthan.msg_dialog.custom_onhide();
				}
				netmanthan.msg_dialog.msg_area.empty();
			},
			minimizable: data.is_minimizable || is_minimizable,
		});

		// class "msgprint" is used in tests
		netmanthan.msg_dialog.msg_area = $('<div class="msgprint">').appendTo(netmanthan.msg_dialog.body);

		netmanthan.msg_dialog.clear = function () {
			netmanthan.msg_dialog.msg_area.empty();
		};

		netmanthan.msg_dialog.indicator = netmanthan.msg_dialog.header.find(".indicator");
	}

	// setup and bind an action to the primary button
	if (data.primary_action) {
		if (
			data.primary_action.server_action &&
			typeof data.primary_action.server_action === "string"
		) {
			data.primary_action.action = () => {
				netmanthan.call({
					method: data.primary_action.server_action,
					args: {
						args: data.primary_action.args,
					},
					callback() {
						if (data.primary_action.hide_on_success) {
							netmanthan.hide_msgprint();
						}
					},
				});
			};
		}

		if (
			data.primary_action.client_action &&
			typeof data.primary_action.client_action === "string"
		) {
			let parts = data.primary_action.client_action.split(".");
			let obj = window;
			for (let part of parts) {
				obj = obj[part];
			}
			data.primary_action.action = () => {
				if (typeof obj === "function") {
					obj(data.primary_action.args);
				}
			};
		}

		netmanthan.msg_dialog.set_primary_action(
			__(data.primary_action.label || data.primary_action_label || "Done"),
			data.primary_action.action
		);
	} else {
		if (netmanthan.msg_dialog.has_primary_action) {
			netmanthan.msg_dialog.get_primary_btn().addClass("hide");
			netmanthan.msg_dialog.has_primary_action = false;
		}
	}

	if (data.secondary_action) {
		netmanthan.msg_dialog.set_secondary_action(data.secondary_action.action);
		netmanthan.msg_dialog.set_secondary_action_label(__(data.secondary_action.label || "Close"));
	}

	if (data.message == null) {
		data.message = "";
	}

	if (data.message.search(/<br>|<p>|<li>/) == -1) {
		msg = netmanthan.utils.replace_newlines(data.message);
	}

	var msg_exists = false;
	if (data.clear) {
		netmanthan.msg_dialog.msg_area.empty();
	} else {
		msg_exists = netmanthan.msg_dialog.msg_area.html();
	}

	if (data.title || !msg_exists) {
		// set title only if it is explicitly given
		// and no existing title exists
		netmanthan.msg_dialog.set_title(
			data.title || __("Message", null, "Default title of the message dialog")
		);
	}

	// show / hide indicator
	if (data.indicator) {
		netmanthan.msg_dialog.indicator.removeClass().addClass("indicator " + data.indicator);
	} else {
		netmanthan.msg_dialog.indicator.removeClass().addClass("hidden");
	}

	// width
	if (data.wide) {
		// msgprint should be narrower than the usual dialog
		if (netmanthan.msg_dialog.wrapper.classList.contains("msgprint-dialog")) {
			netmanthan.msg_dialog.wrapper.classList.remove("msgprint-dialog");
		}
	} else {
		// msgprint should be narrower than the usual dialog
		netmanthan.msg_dialog.wrapper.classList.add("msgprint-dialog");
	}

	if (msg_exists) {
		netmanthan.msg_dialog.msg_area.append("<hr>");
		// append a <hr> if another msg already exists
	}

	netmanthan.msg_dialog.msg_area.append(data.message);

	// make msgprint always appear on top
	netmanthan.msg_dialog.$wrapper.css("z-index", 2000);
	netmanthan.msg_dialog.show();

	return netmanthan.msg_dialog;
};

window.msgprint = netmanthan.msgprint;

netmanthan.hide_msgprint = function (instant) {
	// clear msgprint
	if (netmanthan.msg_dialog && netmanthan.msg_dialog.msg_area) {
		netmanthan.msg_dialog.msg_area.empty();
	}
	if (netmanthan.msg_dialog && netmanthan.msg_dialog.$wrapper.is(":visible")) {
		if (instant) {
			netmanthan.msg_dialog.$wrapper.removeClass("fade");
		}
		netmanthan.msg_dialog.hide();
		if (instant) {
			netmanthan.msg_dialog.$wrapper.addClass("fade");
		}
	}
};

// update html in existing msgprint
netmanthan.update_msgprint = function (html) {
	if (!netmanthan.msg_dialog || (netmanthan.msg_dialog && !netmanthan.msg_dialog.$wrapper.is(":visible"))) {
		netmanthan.msgprint(html);
	} else {
		netmanthan.msg_dialog.msg_area.html(html);
	}
};

netmanthan.verify_password = function (callback) {
	netmanthan.prompt(
		{
			fieldname: "password",
			label: __("Enter your password"),
			fieldtype: "Password",
			reqd: 1,
		},
		function (data) {
			netmanthan.call({
				method: "netmanthan.core.doctype.user.user.verify_password",
				args: {
					password: data.password,
				},
				callback: function (r) {
					if (!r.exc) {
						callback();
					}
				},
			});
		},
		__("Verify Password"),
		__("Verify")
	);
};

netmanthan.show_progress = (title, count, total = 100, description, hide_on_completion = false) => {
	let dialog;
	if (
		netmanthan.cur_progress &&
		netmanthan.cur_progress.title === title &&
		netmanthan.cur_progress.is_visible
	) {
		dialog = netmanthan.cur_progress;
	} else {
		dialog = new netmanthan.ui.Dialog({
			title: title,
		});
		dialog.progress = $(`<div>
			<div class="progress">
				<div class="progress-bar"></div>
			</div>
			<p class="description text-muted small"></p>
		</div`).appendTo(dialog.body);
		dialog.progress_bar = dialog.progress.css({ "margin-top": "10px" }).find(".progress-bar");
		dialog.$wrapper.removeClass("fade");
		dialog.show();
		netmanthan.cur_progress = dialog;
	}
	if (description) {
		dialog.progress.find(".description").text(description);
	}
	dialog.percent = cint((flt(count) * 100) / total);
	dialog.progress_bar.css({ width: dialog.percent + "%" });
	if (hide_on_completion && dialog.percent === 100) {
		// timeout to avoid abrupt hide
		setTimeout(netmanthan.hide_progress, 500);
	}
	return dialog;
};

netmanthan.hide_progress = function () {
	if (netmanthan.cur_progress) {
		netmanthan.cur_progress.hide();
		netmanthan.cur_progress = null;
	}
};

// Floating Message
netmanthan.show_alert = netmanthan.toast = function (message, seconds = 7, actions = {}) {
	let indicator_icon_map = {
		orange: "solid-warning",
		yellow: "solid-warning",
		blue: "solid-info",
		green: "solid-success",
		red: "solid-error",
	};

	if (typeof message === "string") {
		message = {
			message: message,
		};
	}

	if (!$("#dialog-container").length) {
		$('<div id="dialog-container"><div id="alert-container"></div></div>').appendTo("body");
	}

	let icon;
	if (message.indicator) {
		icon = indicator_icon_map[message.indicator.toLowerCase()] || "solid-" + message.indicator;
	} else {
		icon = "solid-info";
	}

	const indicator = message.indicator || "blue";

	const div = $(`
		<div class="alert desk-alert ${indicator}" role="alert">
			<div class="alert-message-container">
				<div class="alert-title-container">
					<div>${netmanthan.utils.icon(icon, "lg")}</div>
					<div class="alert-message">${message.message}</div>
				</div>
				<div class="alert-subtitle">${message.subtitle || ""}</div>
			</div>
			<div class="alert-body" style="display: none"></div>
			<a class="close">${netmanthan.utils.icon("close-alt")}</a>
		</div>
	`);

	div.hide().appendTo("#alert-container").show();

	if (message.body) {
		div.find(".alert-body").show().html(message.body);
	}

	div.find(".close, button").click(function () {
		div.addClass("out");
		setTimeout(() => div.remove(), 800);
		return false;
	});

	Object.keys(actions).map((key) => {
		div.find(`[data-action=${key}]`).on("click", actions[key]);
	});

	if (seconds > 2) {
		// Delay for animation
		seconds = seconds - 0.8;
	}

	setTimeout(() => {
		div.addClass("out");
		setTimeout(() => div.remove(), 800);
		return false;
	}, seconds * 1000);

	return div;
};

// Proxy for netmanthan.show_alert
Object.defineProperty(window, "show_alert", {
	get: function () {
		console.warn(
			"Please use `netmanthan.show_alert` instead of `show_alert`. It will be deprecated soon."
		);
		return netmanthan.show_alert;
	},
});
