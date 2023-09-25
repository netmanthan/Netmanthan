netmanthan.listview_settings["Error Log"] = {
	add_fields: ["seen"],
	get_indicator: function (doc) {
		if (cint(doc.seen)) {
			return [__("Seen"), "green", "seen,=,1"];
		} else {
			return [__("Not Seen"), "red", "seen,=,0"];
		}
	},
	order_by: "seen asc, modified desc",
	onload: function (listview) {
		listview.page.add_menu_item(__("Clear Error Logs"), function () {
			netmanthan.call({
				method: "netmanthan.core.doctype.error_log.error_log.clear_error_logs",
				callback: function () {
					listview.refresh();
				},
			});
		});

		netmanthan.require("logtypes.bundle.js", () => {
			netmanthan.utils.logtypes.show_log_retention_message(cur_list.doctype);
		});
	},
};
