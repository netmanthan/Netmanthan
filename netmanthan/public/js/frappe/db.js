// Copyright (c) 2015, netmanthan Technologies Pvt. Ltd. and Contributors
// MIT License. See license.txt

netmanthan.db = {
	get_list: function (doctype, args) {
		if (!args) {
			args = {};
		}
		args.doctype = doctype;
		if (!args.fields) {
			args.fields = ["name"];
		}
		if (!("limit" in args)) {
			args.limit = 20;
		}
		return new Promise((resolve) => {
			netmanthan.call({
				method: "netmanthan.desk.reportview.get_list",
				args: args,
				type: "GET",
				callback: function (r) {
					resolve(r.message);
				},
			});
		});
	},
	exists: function (doctype, name) {
		return new Promise((resolve) => {
			netmanthan.db.get_value(doctype, { name: name }, "name").then((r) => {
				r.message && r.message.name ? resolve(true) : resolve(false);
			});
		});
	},
	get_value: function (doctype, filters, fieldname, callback, parent_doc) {
		return netmanthan.call({
			method: "netmanthan.client.get_value",
			type: "GET",
			args: {
				doctype: doctype,
				fieldname: fieldname,
				filters: filters,
				parent: parent_doc,
			},
			callback: function (r) {
				callback && callback(r.message);
			},
		});
	},
	get_single_value: (doctype, field) => {
		return new Promise((resolve) => {
			netmanthan
				.call({
					method: "netmanthan.client.get_single_value",
					args: { doctype, field },
					type: "GET",
				})
				.then((r) => resolve(r ? r.message : null));
		});
	},
	set_value: function (doctype, docname, fieldname, value, callback) {
		return netmanthan.call({
			method: "netmanthan.client.set_value",
			args: {
				doctype: doctype,
				name: docname,
				fieldname: fieldname,
				value: value,
			},
			callback: function (r) {
				callback && callback(r.message);
			},
		});
	},
	get_doc: function (doctype, name, filters) {
		return new Promise((resolve, reject) => {
			netmanthan
				.call({
					method: "netmanthan.client.get",
					type: "GET",
					args: { doctype, name, filters },
					callback: (r) => {
						netmanthan.model.sync(r.message);
						resolve(r.message);
					},
				})
				.fail(reject);
		});
	},
	insert: function (doc) {
		return netmanthan.xcall("netmanthan.client.insert", { doc });
	},
	delete_doc: function (doctype, name) {
		return new Promise((resolve) => {
			netmanthan.call("netmanthan.client.delete", { doctype, name }, (r) => resolve(r.message));
		});
	},
	count: function (doctype, args = {}) {
		let filters = args.filters || {};

		// has a filter with childtable?
		const distinct =
			Array.isArray(filters) &&
			filters.some((filter) => {
				return filter[0] !== doctype;
			});

		const fields = [];

		return netmanthan.xcall("netmanthan.desk.reportview.get_count", {
			doctype,
			filters,
			fields,
			distinct,
		});
	},
	get_link_options(doctype, txt = "", filters = {}) {
		return new Promise((resolve) => {
			netmanthan.call({
				type: "GET",
				method: "netmanthan.desk.search.search_link",
				args: {
					doctype,
					txt,
					filters,
				},
				callback(r) {
					resolve(r.results);
				},
			});
		});
	},
};
