// Copyright (c) 2022, netmanthan Technologies Pvt. Ltd. and Contributors
// MIT License. See LICENSE

netmanthan.ui.form.on("Role", {
	refresh: function (frm) {
		if (frm.doc.name === "All") {
			frm.dashboard.add_comment(
				__("Role 'All' will be given to all System Users."),
				"yellow"
			);
		}

		frm.set_df_property("is_custom", "read_only", netmanthan.session.user !== "Administrator");

		frm.add_custom_button("Role Permissions Manager", function () {
			netmanthan.route_options = { role: frm.doc.name };
			netmanthan.set_route("permission-manager");
		});
		frm.add_custom_button("Show Users", function () {
			netmanthan.route_options = { role: frm.doc.name };
			netmanthan.set_route("List", "User", "Report");
		});
	},
});
