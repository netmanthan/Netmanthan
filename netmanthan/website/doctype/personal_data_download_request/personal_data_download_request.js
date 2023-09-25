// Copyright (c) 2019, netmanthan Technologies and contributors
// For license information, please see license.txt

netmanthan.ui.form.on("Personal Data Download Request", {
	onload: function (frm) {
		if (frm.is_new()) {
			frm.doc.user = netmanthan.session.user;
		}
	},
});
