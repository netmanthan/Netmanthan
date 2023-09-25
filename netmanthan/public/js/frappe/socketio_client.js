import { io } from "socket.io-client";
netmanthan.socketio = {
	open_tasks: {},
	open_docs: [],
	emit_queue: [],

	init: function (port = 3000) {
		if (netmanthan.boot.disable_async) {
			return;
		}

		if (netmanthan.socketio.socket) {
			return;
		}

		// Enable secure option when using HTTPS
		if (window.location.protocol == "https:") {
			netmanthan.socketio.socket = io.connect(netmanthan.socketio.get_host(port), {
				secure: true,
				withCredentials: true,
				reconnectionAttempts: 3,
			});
		} else if (window.location.protocol == "http:") {
			netmanthan.socketio.socket = io.connect(netmanthan.socketio.get_host(port), {
				withCredentials: true,
				reconnectionAttempts: 3,
			});
		}

		if (!netmanthan.socketio.socket) {
			console.log("Unable to connect to " + netmanthan.socketio.get_host(port));
			return;
		}

		netmanthan.socketio.socket.on("msgprint", function (message) {
			netmanthan.msgprint(message);
		});

		netmanthan.socketio.socket.on("progress", function (data) {
			if (data.progress) {
				data.percent = (flt(data.progress[0]) / data.progress[1]) * 100;
			}
			if (data.percent) {
				netmanthan.show_progress(
					data.title || __("Progress"),
					data.percent,
					100,
					data.description,
					true
				);
			}
		});

		netmanthan.socketio.setup_listeners();
		netmanthan.socketio.setup_reconnect();

		$(document).on("form-load form-rename", function (e, frm) {
			if (!frm.doc || frm.is_new()) {
				return;
			}

			for (var i = 0, l = netmanthan.socketio.open_docs.length; i < l; i++) {
				var d = netmanthan.socketio.open_docs[i];
				if (frm.doctype == d.doctype && frm.docname == d.name) {
					// already subscribed
					return false;
				}
			}

			netmanthan.socketio.doc_subscribe(frm.doctype, frm.docname);
		});

		$(document).on("form-refresh", function (e, frm) {
			if (!frm.doc || frm.is_new()) {
				return;
			}

			netmanthan.socketio.doc_open(frm.doctype, frm.docname);
		});

		$(document).on("form-unload", function (e, frm) {
			if (!frm.doc || frm.is_new()) {
				return;
			}

			// netmanthan.socketio.doc_unsubscribe(frm.doctype, frm.docname);
			netmanthan.socketio.doc_close(frm.doctype, frm.docname);
		});

		$(document).on("form-typing", function (e, frm) {
			netmanthan.socketio.form_typing(frm.doctype, frm.docname);
		});

		$(document).on("form-stopped-typing", function (e, frm) {
			netmanthan.socketio.form_stopped_typing(frm.doctype, frm.docname);
		});

		window.addEventListener("beforeunload", () => {
			if (!cur_frm || !cur_frm.doc || cur_frm.is_new()) {
				return;
			}

			netmanthan.socketio.doc_close(cur_frm.doctype, cur_frm.docname);
		});
	},
	get_host: function (port = 3000) {
		var host = window.location.origin;
		if (window.dev_server) {
			var parts = host.split(":");
			port = netmanthan.boot.socketio_port || port.toString() || "3000";
			if (parts.length > 2) {
				host = parts[0] + ":" + parts[1];
			}
			host = host + ":" + port;
		}
		return host;
	},
	subscribe: function (task_id, opts) {
		// TODO DEPRECATE

		netmanthan.socketio.socket.emit("task_subscribe", task_id);
		netmanthan.socketio.socket.emit("progress_subscribe", task_id);

		netmanthan.socketio.open_tasks[task_id] = opts;
	},
	task_subscribe: function (task_id) {
		netmanthan.socketio.socket.emit("task_subscribe", task_id);
	},
	task_unsubscribe: function (task_id) {
		netmanthan.socketio.socket.emit("task_unsubscribe", task_id);
	},
	doctype_subscribe: function (doctype) {
		netmanthan.socketio.socket.emit("doctype_subscribe", doctype);
	},
	doctype_unsubscribe: function (doctype) {
		netmanthan.socketio.socket.emit("doctype_unsubscribe", doctype);
	},
	doc_subscribe: function (doctype, docname) {
		if (netmanthan.flags.doc_subscribe) {
			console.log("throttled");
			return;
		}

		netmanthan.flags.doc_subscribe = true;

		// throttle to 1 per sec
		setTimeout(function () {
			netmanthan.flags.doc_subscribe = false;
		}, 1000);

		netmanthan.socketio.socket.emit("doc_subscribe", doctype, docname);
		netmanthan.socketio.open_docs.push({ doctype: doctype, docname: docname });
	},
	doc_unsubscribe: function (doctype, docname) {
		netmanthan.socketio.socket.emit("doc_unsubscribe", doctype, docname);
		netmanthan.socketio.open_docs = $.filter(netmanthan.socketio.open_docs, function (d) {
			if (d.doctype === doctype && d.name === docname) {
				return null;
			} else {
				return d;
			}
		});
	},
	doc_open: function (doctype, docname) {
		// notify that the user has opened this doc, if not already notified
		if (
			!netmanthan.socketio.last_doc ||
			netmanthan.socketio.last_doc[0] != doctype ||
			netmanthan.socketio.last_doc[1] != docname
		) {
			netmanthan.socketio.socket.emit("doc_open", doctype, docname);

			netmanthan.socketio.last_doc &&
				netmanthan.socketio.doc_close(
					netmanthan.socketio.last_doc[0],
					netmanthan.socketio.last_doc[1]
				);
		}
		netmanthan.socketio.last_doc = [doctype, docname];
	},
	doc_close: function (doctype, docname) {
		// notify that the user has closed this doc
		netmanthan.socketio.socket.emit("doc_close", doctype, docname);

		// if the doc is closed the user has also stopped typing
		netmanthan.socketio.socket.emit("doc_typing_stopped", doctype, docname);
	},
	form_typing: function (doctype, docname) {
		// notifiy that the user is typing on the doc
		netmanthan.socketio.socket.emit("doc_typing", doctype, docname);
	},
	form_stopped_typing: function (doctype, docname) {
		// notifiy that the user has stopped typing
		netmanthan.socketio.socket.emit("doc_typing_stopped", doctype, docname);
	},
	setup_listeners: function () {
		netmanthan.socketio.socket.on("task_status_change", function (data) {
			netmanthan.socketio.process_response(data, data.status.toLowerCase());
		});
		netmanthan.socketio.socket.on("task_progress", function (data) {
			netmanthan.socketio.process_response(data, "progress");
		});
	},
	setup_reconnect: function () {
		// subscribe again to open_tasks
		netmanthan.socketio.socket.on("connect", function () {
			// wait for 5 seconds before subscribing again
			// because it takes more time to start python server than nodejs server
			// and we use validation requests to python server for subscribing
			setTimeout(function () {
				$.each(netmanthan.socketio.open_tasks, function (task_id, opts) {
					netmanthan.socketio.subscribe(task_id, opts);
				});

				// re-connect open docs
				$.each(netmanthan.socketio.open_docs, function (d) {
					if (locals[d.doctype] && locals[d.doctype][d.name]) {
						netmanthan.socketio.doc_subscribe(d.doctype, d.name);
					}
				});

				if (cur_frm && cur_frm.doc && !cur_frm.is_new()) {
					netmanthan.socketio.doc_open(cur_frm.doc.doctype, cur_frm.doc.name);
				}
			}, 5000);
		});
	},
	process_response: function (data, method) {
		if (!data) {
			return;
		}

		// success
		var opts = netmanthan.socketio.open_tasks[data.task_id];
		if (opts[method]) {
			opts[method](data);
		}

		// "callback" is std netmanthan term
		if (method === "success") {
			if (opts.callback) opts.callback(data);
		}

		// always
		netmanthan.request.cleanup(opts, data);
		if (opts.always) {
			opts.always(data);
		}

		// error
		if (data.status_code && data.status_code > 400 && opts.error) {
			opts.error(data);
		}
	},
};

netmanthan.provide("netmanthan.realtime");
netmanthan.realtime.on = function (event, callback) {
	netmanthan.socketio.socket && netmanthan.socketio.socket.on(event, callback);
};

netmanthan.realtime.off = function (event, callback) {
	netmanthan.socketio.socket && netmanthan.socketio.socket.off(event, callback);
};

netmanthan.realtime.publish = function (event, message) {
	if (netmanthan.socketio.socket) {
		netmanthan.socketio.socket.emit(event, message);
	}
};
