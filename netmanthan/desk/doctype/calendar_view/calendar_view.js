// Copyright (c) 2017, netmanthan Technologies and contributors
// For license information, please see license.txt

netmanthan.ui.form.on("Calendar View", {
	onload: function (frm) {
		frm.trigger("reference_doctype");
	},
	refresh: function (frm) {
		if (!frm.is_new()) {
			frm.add_custom_button(__("Show Calendar"), () =>
				netmanthan.set_route("List", frm.doc.reference_doctype, "Calendar", frm.doc.name)
			);
		}
	},
	reference_doctype: function (frm) {
		const { reference_doctype } = frm.doc;
		if (!reference_doctype) return;

		netmanthan.model.with_doctype(reference_doctype, () => {
			const meta = netmanthan.get_meta(reference_doctype);

			const subject_options = meta.fields
				.filter((df) => !netmanthan.model.no_value_type.includes(df.fieldtype))
				.map((df) => df.fieldname);

			const date_options = meta.fields
				.filter((df) => ["Date", "Datetime"].includes(df.fieldtype))
				.map((df) => df.fieldname);

			frm.set_df_property("subject_field", "options", subject_options);
			frm.set_df_property("start_date_field", "options", date_options);
			frm.set_df_property("end_date_field", "options", date_options);
			frm.refresh();
		});
	},
});
