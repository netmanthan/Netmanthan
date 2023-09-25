netmanthan.listview_settings["Webhook Request Log"] = {
	onload: function (list_view) {
		netmanthan.require("logtypes.bundle.js", () => {
			netmanthan.utils.logtypes.show_log_retention_message(list_view.doctype);
		});
	},
};
