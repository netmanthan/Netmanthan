// Copyright (c) 2022, netmanthan Technologies and contributors
// For license information, please see license.txt

netmanthan.ui.form.on("Document Naming Settings", {
	refresh: function (frm) {
		frm.trigger("setup_transaction_autocomplete");
		frm.disable_save();
	},

	setup_transaction_autocomplete: function (frm) {
		netmanthan.call({
			method: "get_transactions_and_prefixes",
			doc: frm.doc,
			callback: function (r) {
				frm.fields_dict.transaction_type.set_data(r.message.transactions);
				frm.fields_dict.prefix.set_data(r.message.prefixes);
			},
		});
	},

	transaction_type: function (frm) {
		frm.set_value("user_must_always_select", 0);
		netmanthan.call({
			method: "get_options",
			doc: frm.doc,
			callback: function (r) {
				frm.set_value("naming_series_options", r.message);
				if (r.message && r.message.split("\n")[0] == "")
					frm.set_value("user_must_always_select", 1);
			},
		});
	},

	prefix: function (frm) {
		netmanthan.call({
			method: "get_current",
			doc: frm.doc,
			callback: function (r) {
				frm.refresh_field("current_value");
			},
		});
	},

	update: function (frm) {
		netmanthan.call({
			method: "update_series",
			doc: frm.doc,
			freeze: true,
			freeze_msg: __("Updating naming series options"),
			callback: function (r) {
				frm.trigger("setup_transaction_autocomplete");
				frm.trigger("transaction_type");
			},
		});
	},

	try_naming_series(frm) {
		netmanthan.call({
			method: "preview_series",
			doc: frm.doc,
			callback: function (r) {
				if (!r.exc) {
					frm.set_value("series_preview", r.message);
				} else {
					frm.set_value("series_preview", __("Failed to generate preview of series"));
				}
			},
		});
	},
});
