netmanthan.listview_settings["RQ Job"] = {
	hide_name_column: true,

	onload(listview) {
		if (!has_common(netmanthan.user_roles, ["Administrator", "System Manager"])) return;

		listview.page.add_inner_button(
			__("Remove Failed Jobs"),
			() => {
				netmanthan.confirm(__("Are you sure you want to remove all failed jobs?"), () => {
					netmanthan.xcall("netmanthan.core.doctype.rq_job.rq_job.remove_failed_jobs");
				});
			},
			__("Actions")
		);

		if (listview.list_view_settings) {
			listview.list_view_settings.disable_count = 1;
			listview.list_view_settings.disable_sidebar_stats = 1;
		}

		netmanthan.xcall("netmanthan.utils.scheduler.get_scheduler_status").then(({ status }) => {
			if (status === "active") {
				listview.page.set_indicator(__("Scheduler: Active"), "green");
			} else {
				listview.page.set_indicator(__("Scheduler: Inactive"), "red");
				listview.page.add_inner_button(
					__("Enable Scheduler"),
					() => {
						netmanthan.confirm(__("Are you sure you want to re-enable scheduler?"), () => {
							netmanthan
								.xcall("netmanthan.utils.scheduler.activate_scheduler")
								.then(() => {
									netmanthan.show_alert(__("Enabled Scheduler"));
								})
								.catch((e) => {
									netmanthan.show_alert({
										message: __("Failed to enable scheduler: {0}", e),
										indicator: "error",
									});
								});
						});
					},
					__("Actions")
				);
			}
		});

		setInterval(() => {
			if (listview.list_view_settings.disable_auto_refresh) {
				return;
			}

			const route = netmanthan.get_route() || [];
			if (route[0] != "List" || "RQ Job" != route[1]) {
				return;
			}

			listview.refresh();
		}, 5000);
	},
};
