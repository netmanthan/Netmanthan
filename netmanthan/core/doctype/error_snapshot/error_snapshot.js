netmanthan.ui.form.on("Error Snapshot", "load", function (frm) {
	frm.set_read_only(true);
});

netmanthan.ui.form.on("Error Snapshot", "refresh", function (frm) {
	frm.set_df_property(
		"view",
		"options",
		netmanthan.render_template("error_snapshot", { doc: frm.doc })
	);

	if (frm.doc.relapses) {
		frm.add_custom_button(__("Show Relapses"), function () {
			netmanthan.route_options = {
				parent_error_snapshot: frm.doc.name,
			};
			netmanthan.set_route("List", "Error Snapshot");
		});
	}
});
