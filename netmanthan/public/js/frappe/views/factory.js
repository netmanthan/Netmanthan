// Copyright (c) 2015, netmanthan Technologies Pvt. Ltd. and Contributors
// MIT License. See license.txt

netmanthan.provide("netmanthan.pages");
netmanthan.provide("netmanthan.views");

netmanthan.views.Factory = class Factory {
	constructor(opts) {
		$.extend(this, opts);
	}

	show() {
		this.route = netmanthan.get_route();
		this.page_name = netmanthan.get_route_str();

		if (this.before_show && this.before_show() === false) return;

		if (netmanthan.pages[this.page_name]) {
			netmanthan.container.change_to(this.page_name);
			if (this.on_show) {
				this.on_show();
			}
		} else {
			if (this.route[1]) {
				this.make(this.route);
			} else {
				netmanthan.show_not_found(this.route);
			}
		}
	}

	make_page(double_column, page_name) {
		return netmanthan.make_page(double_column, page_name);
	}
};

netmanthan.make_page = function (double_column, page_name) {
	if (!page_name) {
		page_name = netmanthan.get_route_str();
	}

	const page = netmanthan.container.add_page(page_name);

	netmanthan.ui.make_app_page({
		parent: page,
		single_column: !double_column,
	});

	netmanthan.container.change_to(page_name);
	return page;
};
