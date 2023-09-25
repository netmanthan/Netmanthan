netmanthan.listview_settings["Notification Log"] = {
	onload: function (listview) {
		netmanthan.require("logtypes.bundle.js", () => {
			netmanthan.utils.logtypes.show_log_retention_message(cur_list.doctype);
		});
	},
};
