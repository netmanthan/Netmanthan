// Copyright (c) 2019, netmanthan Technologies and contributors
// For license information, please see license.txt

netmanthan.ui.form.on("Notification Settings", {
	onload: (frm) => {
		netmanthan.breadcrumbs.add({
			label: __("Settings"),
			route: "#modules/Settings",
			type: "Custom",
		});
		frm.set_query("subscribed_documents", () => {
			return {
				filters: {
					istable: 0,
				},
			};
		});
	},

	refresh: (frm) => {
		if (netmanthan.user.has_role("System Manager")) {
			frm.add_custom_button(__("Go to Notification Settings List"), () => {
				netmanthan.set_route("List", "Notification Settings");
			});
		}
	},
});
