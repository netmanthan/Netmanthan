// Copyright (c) 2015, netmanthan Technologies Pvt. Ltd. and Contributors
// MIT License. See license.txt

// provide a namespace
if (!window.netmanthan) window.netmanthan = {};

netmanthan.provide = function (namespace) {
	// docs: create a namespace //
	var nsl = namespace.split(".");
	var parent = window;
	for (var i = 0; i < nsl.length; i++) {
		var n = nsl[i];
		if (!parent[n]) {
			parent[n] = {};
		}
		parent = parent[n];
	}
	return parent;
};

netmanthan.provide("locals");
netmanthan.provide("netmanthan.flags");
netmanthan.provide("netmanthan.settings");
netmanthan.provide("netmanthan.utils");
netmanthan.provide("netmanthan.ui.form");
netmanthan.provide("netmanthan.modules");
netmanthan.provide("netmanthan.templates");
netmanthan.provide("netmanthan.test_data");
netmanthan.provide("netmanthan.utils");
netmanthan.provide("netmanthan.model");
netmanthan.provide("netmanthan.user");
netmanthan.provide("netmanthan.session");
netmanthan.provide("netmanthan._messages");
netmanthan.provide("locals.DocType");

// for listviews
netmanthan.provide("netmanthan.listview_settings");
netmanthan.provide("netmanthan.tour");
netmanthan.provide("netmanthan.listview_parent_route");

// constants
window.NEWLINE = "\n";
window.TAB = 9;
window.UP_ARROW = 38;
window.DOWN_ARROW = 40;

// proxy for user globals defined in desk.js

// API globals
window.cur_frm = null;
