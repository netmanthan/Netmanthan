// Copyright (c) 2015, netmanthan Technologies Pvt. Ltd. and Contributors
// MIT License. See license.txt

// library to mange assets (js, css, models, html) etc in the app.
// will try and get from localStorage if latest are available
// depends on netmanthan.versions to manage versioning

netmanthan.require = function (items, callback) {
	if (typeof items === "string") {
		items = [items];
	}
	items = items.map((item) => netmanthan.assets.bundled_asset(item));

	return new Promise((resolve) => {
		netmanthan.assets.execute(items, () => {
			resolve();
			callback && callback();
		});
	});
};

netmanthan.assets = {
	check: function () {
		// if version is different then clear localstorage
		if (window._version_number != localStorage.getItem("_version_number")) {
			netmanthan.assets.clear_local_storage();
			console.log("Cleared App Cache.");
		}

		if (localStorage._last_load) {
			let not_updated_since = new Date() - new Date(localStorage._last_load);
			// Evict cache every 2 days
			// Evict cache if page is reloaded within 10 seconds. Which could be user trying to
			// refresh if things feel broken.
			if ((not_updated_since < 5000 && is_reload()) || not_updated_since > 2 * 86400000) {
				netmanthan.assets.clear_local_storage();
			}
		} else {
			netmanthan.assets.clear_local_storage();
		}

		netmanthan.assets.init_local_storage();
	},

	init_local_storage: function () {
		localStorage._last_load = new Date();
		localStorage._version_number = window._version_number;
		if (netmanthan.boot) localStorage.metadata_version = netmanthan.boot.metadata_version;
	},

	clear_local_storage: function () {
		$.each(
			["_last_load", "_version_number", "metadata_version", "page_info", "last_visited"],
			function (i, key) {
				localStorage.removeItem(key);
			}
		);

		// clear assets
		for (var key in localStorage) {
			if (
				key.indexOf("desk_assets:") === 0 ||
				key.indexOf("_page:") === 0 ||
				key.indexOf("_doctype:") === 0 ||
				key.indexOf("preferred_breadcrumbs:") === 0
			) {
				localStorage.removeItem(key);
			}
		}
		console.log("localStorage cleared");
	},

	// keep track of executed assets
	executed_: [],

	// pass on to the handler to set
	execute: function (items, callback) {
		var to_fetch = [];
		for (var i = 0, l = items.length; i < l; i++) {
			if (!netmanthan.assets.exists(items[i])) {
				to_fetch.push(items[i]);
			}
		}
		if (to_fetch.length) {
			netmanthan.assets.fetch(to_fetch, function () {
				netmanthan.assets.eval_assets(items, callback);
			});
		} else {
			netmanthan.assets.eval_assets(items, callback);
		}
	},

	eval_assets: function (items, callback) {
		for (var i = 0, l = items.length; i < l; i++) {
			// execute js/css if not already.
			var path = items[i];
			if (netmanthan.assets.executed_.indexOf(path) === -1) {
				// execute
				netmanthan.assets.handler[netmanthan.assets.extn(path)](netmanthan.assets.get(path), path);
				netmanthan.assets.executed_.push(path);
			}
		}
		callback && callback();
	},

	// check if the asset exists in
	// localstorage
	exists: function (src) {
		if (netmanthan.assets.executed_.indexOf(src) !== -1) {
			return true;
		}
		if (netmanthan.boot.developer_mode) {
			return false;
		}
		if (netmanthan.assets.get(src)) {
			return true;
		} else {
			return false;
		}
	},

	// load an asset via
	fetch: function (items, callback) {
		// this is virtual page load, only get the the source
		// *without* the template

		netmanthan.call({
			type: "GET",
			method: "netmanthan.client.get_js",
			args: {
				items: items,
			},
			callback: function (r) {
				$.each(items, function (i, src) {
					netmanthan.assets.add(src, r.message[i]);
				});
				callback();
			},
			freeze: true,
		});
	},

	add: function (src, txt) {
		if ("localStorage" in window) {
			try {
				netmanthan.assets.set(src, txt);
			} catch (e) {
				// if quota is exceeded, clear local storage and set item
				netmanthan.assets.clear_local_storage();
				netmanthan.assets.set(src, txt);
			}
		}
	},

	get: function (src) {
		return localStorage.getItem("desk_assets:" + src);
	},

	set: function (src, txt) {
		localStorage.setItem("desk_assets:" + src, txt);
	},

	extn: function (src) {
		if (src.indexOf("?") != -1) {
			src = src.split("?").slice(-1)[0];
		}
		return src.split(".").slice(-1)[0];
	},

	handler: {
		js: function (txt, src) {
			netmanthan.dom.eval(txt);
		},
		css: function (txt, src) {
			netmanthan.dom.set_style(txt);
		},
	},

	bundled_asset(path, is_rtl = null) {
		if (!path.startsWith("/assets") && path.includes(".bundle.")) {
			if (path.endsWith(".css") && is_rtl) {
				path = `rtl_${path}`;
			}
			path = netmanthan.boot.assets_json[path] || path;
			return path;
		}
		return path;
	},
};

function is_reload() {
	try {
		return window.performance
			?.getEntriesByType("navigation")
			.map((nav) => nav.type)
			.includes("reload");
	} catch (e) {
		// Safari probably
		return true;
	}
}
