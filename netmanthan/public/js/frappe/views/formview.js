// Copyright (c) 2015, netmanthan Technologies Pvt. Ltd. and Contributors
// MIT License. See license.txt

netmanthan.provide("netmanthan.views.formview");

netmanthan.views.FormFactory = class FormFactory extends netmanthan.views.Factory {
	make(route) {
		var doctype = route[1],
			doctype_layout = netmanthan.router.doctype_layout || doctype;

		if (!netmanthan.views.formview[doctype_layout]) {
			netmanthan.model.with_doctype(doctype, () => {
				this.page = netmanthan.container.add_page(doctype_layout);
				netmanthan.views.formview[doctype_layout] = this.page;
				this.make_and_show(doctype, route);
			});
		} else {
			this.show_doc(route);
		}

		this.setup_events();
	}

	make_and_show(doctype, route) {
		if (netmanthan.router.doctype_layout) {
			netmanthan.model.with_doc("DocType Layout", netmanthan.router.doctype_layout, () => {
				this.make_form(doctype);
				this.show_doc(route);
			});
		} else {
			this.make_form(doctype);
			this.show_doc(route);
		}
	}

	make_form(doctype) {
		this.page.frm = new netmanthan.ui.form.Form(
			doctype,
			this.page,
			true,
			netmanthan.router.doctype_layout
		);
	}

	setup_events() {
		if (!this.initialized) {
			$(document).on("page-change", function () {
				netmanthan.ui.form.close_grid_form();
			});

			netmanthan.realtime.on("doc_viewers", function (data) {
				// set users that currently viewing the form
				netmanthan.ui.form.FormViewers.set_users(data, "viewers");
			});

			netmanthan.realtime.on("doc_typers", function (data) {
				// set users that currently typing on the form
				netmanthan.ui.form.FormViewers.set_users(data, "typers");
			});
		}
		this.initialized = true;
	}

	show_doc(route) {
		var doctype = route[1],
			doctype_layout = netmanthan.router.doctype_layout || doctype,
			name = route.slice(2).join("/");

		if (netmanthan.model.new_names[name]) {
			// document has been renamed, reroute
			name = netmanthan.model.new_names[name];
			netmanthan.set_route("Form", doctype_layout, name);
			return;
		}

		const doc = netmanthan.get_doc(doctype, name);
		if (
			doc &&
			netmanthan.model.get_docinfo(doctype, name) &&
			(doc.__islocal || netmanthan.model.is_fresh(doc))
		) {
			// is document available and recent?
			this.render(doctype_layout, name);
		} else {
			this.fetch_and_render(doctype, name, doctype_layout);
		}
	}

	fetch_and_render(doctype, name, doctype_layout) {
		netmanthan.model.with_doc(doctype, name, (name, r) => {
			if (r && r["403"]) return; // not permitted

			if (!(locals[doctype] && locals[doctype][name])) {
				if (name && name.substr(0, 3) === "new") {
					this.render_new_doc(doctype, name, doctype_layout);
				} else {
					netmanthan.show_not_found();
				}
				return;
			}
			this.render(doctype_layout, name);
		});
	}

	render_new_doc(doctype, name, doctype_layout) {
		const new_name = netmanthan.model.make_new_doc_and_get_name(doctype, true);
		if (new_name === name) {
			this.render(doctype_layout, name);
		} else {
			netmanthan.route_flags.replace_route = true;
			netmanthan.set_route("Form", doctype_layout, new_name);
		}
	}

	render(doctype_layout, name) {
		netmanthan.container.change_to(doctype_layout);
		netmanthan.views.formview[doctype_layout].frm.refresh(name);
	}
};
