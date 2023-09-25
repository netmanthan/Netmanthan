// Copyright (c) 2017, netmanthan Technologies and contributors
// For license information, please see license.txt

netmanthan.ui.form.on("Role Profile", {
	refresh: function (frm) {
		if (has_common(netmanthan.user_roles, ["Administrator", "System Manager"])) {
			if (!frm.roles_editor) {
				const role_area = $(frm.fields_dict.roles_html.wrapper);
				frm.roles_editor = new netmanthan.RoleEditor(role_area, frm);
			}
			frm.roles_editor.show();
		}
	},

	validate: function (frm) {
		if (frm.roles_editor) {
			frm.roles_editor.set_roles_in_table();
		}
	},
});
