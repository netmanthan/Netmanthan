netmanthan.listview_settings["Integration Request"] = {
	onload: function (list_view) {
		netmanthan.require("logtypes.bundle.js", () => {
			netmanthan.utils.logtypes.show_log_retention_message(list_view.doctype);
		});
	},
};
