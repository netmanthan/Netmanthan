netmanthan.pages["backups"].on_page_load = function (wrapper) {
	var page = netmanthan.ui.make_app_page({
		parent: wrapper,
		title: __("Download Backups"),
		single_column: true,
	});

	page.add_inner_button(__("Set Number of Backups"), function () {
		netmanthan.set_route("Form", "System Settings");
	});

	page.add_inner_button(__("Download Files Backup"), function () {
		netmanthan.call({
			method: "netmanthan.desk.page.backups.backups.schedule_files_backup",
			args: { user_email: netmanthan.session.user_email },
		});
	});

	page.add_inner_button(__("Get Backup Encryption Key"), function () {
		if (netmanthan.user.has_role("System Manager")) {
			netmanthan.verify_password(function () {
				netmanthan.call({
					method: "netmanthan.utils.backups.get_backup_encryption_key",
					callback: function (r) {
						netmanthan.msgprint({
							title: __("Backup Encryption Key"),
							message: __(r.message),
							indicator: "blue",
						});
					},
				});
			});
		} else {
			netmanthan.msgprint({
				title: __("Error"),
				message: __("System Manager privileges required."),
				indicator: "red",
			});
		}
	});

	netmanthan.breadcrumbs.add("Setup");

	$(netmanthan.render_template("backups")).appendTo(page.body.addClass("no-border"));
};
