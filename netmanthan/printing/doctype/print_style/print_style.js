// Copyright (c) 2017, netmanthan Technologies and contributors
// For license information, please see license.txt

netmanthan.ui.form.on("Print Style", {
	refresh: function (frm) {
		frm.add_custom_button(__("Print Settings"), () => {
			netmanthan.set_route("Form", "Print Settings");
		});
	},
});
