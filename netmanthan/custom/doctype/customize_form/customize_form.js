// Copyright (c) 2015, netmanthan Technologies Pvt. Ltd. and Contributors
// MIT License. See license.txt

netmanthan.provide("netmanthan.customize_form");

netmanthan.ui.form.on("Customize Form", {
	setup: function (frm) {
		// save the last setting if refreshing
		window.addEventListener("beforeunload", () => {
			if (frm.doc.doc_type && frm.doc.doc_type != "undefined") {
				localStorage["customize_doctype"] = frm.doc.doc_type;
			}
		});
	},

	onload: function (frm) {
		frm.set_query("doc_type", function () {
			return {
				filters: [
					["DocType", "issingle", "=", 0],
					["DocType", "custom", "=", 0],
					["DocType", "name", "not in", netmanthan.model.core_doctypes_list],
					["DocType", "restrict_to_domain", "in", netmanthan.boot.active_domains],
				],
			};
		});

		frm.set_query("default_print_format", function () {
			return {
				filters: {
					print_format_type: ["!=", "JS"],
					doc_type: ["=", frm.doc.doc_type],
				},
			};
		});

		$(frm.wrapper).on("grid-row-render", function (e, grid_row) {
			if (grid_row.doc && grid_row.doc.fieldtype == "Section Break") {
				$(grid_row.row).css({ "font-weight": "bold" });
			}

			grid_row.row.removeClass("highlight");

			if (
				grid_row.doc.is_custom_field &&
				!grid_row.row.hasClass("highlight") &&
				!grid_row.doc.is_system_generated
			) {
				grid_row.row.addClass("highlight");
			}
		});
	},

	doc_type: function (frm) {
		if (frm.doc.doc_type) {
			return frm.call({
				method: "fetch_to_customize",
				doc: frm.doc,
				freeze: true,
				callback: function (r) {
					if (r) {
						if (r._server_messages && r._server_messages.length) {
							frm.set_value("doc_type", "");
						} else {
							frm.refresh();
							frm.trigger("add_customize_child_table_button");
							frm.trigger("setup_default_views");
						}
					}
					localStorage["customize_doctype"] = frm.doc.doc_type;
				},
			});
		} else {
			frm.refresh();
		}
	},

	is_calendar_and_gantt: function (frm) {
		frm.trigger("setup_default_views");
	},

	add_customize_child_table_button: function (frm) {
		frm.doc.fields.forEach(function (f) {
			if (!in_list(["Table", "Table MultiSelect"], f.fieldtype)) return;

			frm.add_custom_button(
				f.options,
				() => frm.set_value("doc_type", f.options),
				__("Customize Child Table")
			);
		});
	},

	refresh: function (frm) {
		frm.disable_save(true);
		frm.page.clear_icons();

		if (frm.doc.doc_type) {
			frm.page.set_title(__("Customize Form - {0}", [frm.doc.doc_type]));
			netmanthan.customize_form.set_primary_action(frm);

			frm.add_custom_button(
				__("Go to {0} List", [__(frm.doc.doc_type)]),
				function () {
					netmanthan.set_route("List", frm.doc.doc_type);
				},
				__("Actions")
			);

			frm.add_custom_button(
				__("Reload"),
				function () {
					frm.script_manager.trigger("doc_type");
				},
				__("Actions")
			);

			frm.add_custom_button(
				__("Reset to defaults"),
				function () {
					netmanthan.customize_form.confirm(__("Remove all customizations?"), frm);
				},
				__("Actions")
			);

			frm.add_custom_button(
				__("Set Permissions"),
				function () {
					netmanthan.set_route("permission-manager", frm.doc.doc_type);
				},
				__("Actions")
			);

			const is_autoname_autoincrement = frm.doc.autoname === "autoincrement";
			frm.set_df_property("naming_rule", "hidden", is_autoname_autoincrement);
			frm.set_df_property("autoname", "read_only", is_autoname_autoincrement);
		}

		frm.events.setup_export(frm);
		frm.events.setup_sort_order(frm);
		frm.events.set_default_doc_type(frm);
	},

	set_default_doc_type(frm) {
		let doc_type;
		if (netmanthan.route_options && netmanthan.route_options.doc_type) {
			doc_type = netmanthan.route_options.doc_type;
			netmanthan.route_options = null;
			localStorage.removeItem("customize_doctype");
		}
		if (!doc_type) {
			doc_type = localStorage.getItem("customize_doctype");
		}
		if (doc_type) {
			setTimeout(() => frm.set_value("doc_type", doc_type, false, true), 1000);
		}
	},

	setup_export(frm) {
		if (netmanthan.boot.developer_mode) {
			frm.add_custom_button(
				__("Export Customizations"),
				function () {
					netmanthan.prompt(
						[
							{
								fieldtype: "Link",
								fieldname: "module",
								options: "Module Def",
								label: __("Module to Export"),
								reqd: 1,
							},
							{
								fieldtype: "Check",
								fieldname: "sync_on_migrate",
								label: __("Sync on Migrate"),
								default: 1,
							},
							{
								fieldtype: "Check",
								fieldname: "with_permissions",
								label: __("Export Custom Permissions"),
								default: 1,
							},
						],
						function (data) {
							netmanthan.call({
								method: "netmanthan.modules.utils.export_customizations",
								args: {
									doctype: frm.doc.doc_type,
									module: data.module,
									sync_on_migrate: data.sync_on_migrate,
									with_permissions: data.with_permissions,
								},
							});
						},
						__("Select Module")
					);
				},
				__("Actions")
			);
		}
	},

	setup_sort_order(frm) {
		// sort order select
		if (frm.doc.doc_type) {
			var fields = $.map(frm.doc.fields, function (df) {
				return netmanthan.model.is_value_type(df.fieldtype) ? df.fieldname : null;
			});
			fields = ["", "name", "modified"].concat(fields);
			frm.set_df_property("sort_field", "options", fields);
		}
	},

	setup_default_views(frm) {
		netmanthan.model.set_default_views_for_doctype(frm.doc.doc_type, frm);
	},
});

// can't delete standard fields
netmanthan.ui.form.on("Customize Form Field", {
	before_fields_remove: function (frm, doctype, name) {
		const row = netmanthan.get_doc(doctype, name);

		if (row.is_system_generated) {
			netmanthan.throw(
				__(
					"Cannot delete system generated field <strong>{0}</strong>. You can hide it instead.",
					[__(row.label) || row.fieldname]
				)
			);
		}

		if (!(row.is_custom_field || row.__islocal)) {
			netmanthan.throw(
				__("Cannot delete standard field <strong>{0}</strong>. You can hide it instead.", [
					__(row.label) || row.fieldname,
				])
			);
		}
	},
	fields_add: function (frm, cdt, cdn) {
		var f = netmanthan.model.get_doc(cdt, cdn);
		f.is_system_generated = false;
		f.is_custom_field = true;
		frm.trigger("setup_default_views");
	},
});

// can't delete standard links
netmanthan.ui.form.on("DocType Link", {
	before_links_remove: function (frm, doctype, name) {
		let row = netmanthan.get_doc(doctype, name);
		if (!(row.custom || row.__islocal)) {
			netmanthan.msgprint(__("Cannot delete standard link. You can hide it if you want"));
			throw "cannot delete standard link";
		}
	},
	links_add: function (frm, cdt, cdn) {
		let f = netmanthan.model.get_doc(cdt, cdn);
		f.custom = 1;
	},
});

// can't delete standard actions
netmanthan.ui.form.on("DocType Action", {
	before_actions_remove: function (frm, doctype, name) {
		let row = netmanthan.get_doc(doctype, name);
		if (!(row.custom || row.__islocal)) {
			netmanthan.msgprint(__("Cannot delete standard action. You can hide it if you want"));
			throw "cannot delete standard action";
		}
	},
	actions_add: function (frm, cdt, cdn) {
		let f = netmanthan.model.get_doc(cdt, cdn);
		f.custom = 1;
	},
});

// can't delete standard states
netmanthan.ui.form.on("DocType State", {
	before_states_remove: function (frm, doctype, name) {
		let row = netmanthan.get_doc(doctype, name);
		if (!(row.custom || row.__islocal)) {
			netmanthan.msgprint(__("Cannot delete standard document state."));
			throw "cannot delete standard document state";
		}
	},
	states_add: function (frm, cdt, cdn) {
		let f = netmanthan.model.get_doc(cdt, cdn);
		f.custom = 1;
	},
});

netmanthan.customize_form.validate_fieldnames = async function (frm) {
	for (let i = 0; i < frm.doc.fields.length; i++) {
		let field = frm.doc.fields[i];

		let fieldname = field.label && netmanthan.model.scrub(field.label).toLowerCase();
		if (
			field.label &&
			!field.fieldname &&
			in_list(netmanthan.model.restricted_fields, fieldname)
		) {
			let message = __(
				"For field <b>{0}</b> in row <b>{1}</b>, fieldname <b>{2}</b> is restricted it will be renamed as <b>{2}1</b>. Do you want to continue?",
				[field.label, field.idx, fieldname]
			);
			await pause_to_confirm(message);
		}
	}

	function pause_to_confirm(message) {
		return new Promise((resolve) => {
			netmanthan.confirm(
				message,
				() => resolve(),
				() => {
					frm.page.btn_primary.prop("disabled", false);
				}
			);
		});
	}
};

netmanthan.customize_form.save_customization = function (frm) {
	if (frm.doc.doc_type) {
		return frm.call({
			doc: frm.doc,
			freeze: true,
			freeze_message: __("Saving Customization..."),
			btn: frm.page.btn_primary,
			method: "save_customization",
			callback: function (r) {
				if (!r.exc) {
					netmanthan.customize_form.clear_locals_and_refresh(frm);
					frm.script_manager.trigger("doc_type");
				}
			},
		});
	}
};

netmanthan.customize_form.set_primary_action = function (frm) {
	frm.page.set_primary_action(__("Update"), async () => {
		await this.validate_fieldnames(frm);
		this.save_customization(frm);
	});
};

netmanthan.customize_form.confirm = function (msg, frm) {
	if (!frm.doc.doc_type) return;

	var d = new netmanthan.ui.Dialog({
		title: "Reset To Defaults",
		fields: [
			{
				fieldtype: "HTML",
				options: __("All customizations will be removed. Please confirm."),
			},
		],
		primary_action: function () {
			return frm.call({
				doc: frm.doc,
				method: "reset_to_defaults",
				callback: function (r) {
					if (r.exc) {
						netmanthan.msgprint(r.exc);
					} else {
						d.hide();
						netmanthan.show_alert({
							message: __("Customizations Reset"),
							indicator: "green",
						});
						netmanthan.customize_form.clear_locals_and_refresh(frm);
					}
				},
			});
		},
	});

	netmanthan.customize_form.confirm.dialog = d;
	d.show();
};

netmanthan.customize_form.clear_locals_and_refresh = function (frm) {
	delete frm.doc.__unsaved;
	// clear doctype from locals
	netmanthan.model.clear_doc("DocType", frm.doc.doc_type);
	delete netmanthan.meta.docfield_copy[frm.doc.doc_type];
	frm.refresh();
};

extend_cscript(cur_frm.cscript, new netmanthan.model.DocTypeController({ frm: cur_frm }));
