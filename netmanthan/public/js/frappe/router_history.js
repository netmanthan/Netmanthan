netmanthan.route_history_queue = [];
const routes_to_skip = ["Form", "social", "setup-wizard", "recorder"];

const save_routes = netmanthan.utils.debounce(() => {
	if (netmanthan.session.user === "Guest") return;
	const routes = netmanthan.route_history_queue;
	if (!routes.length) return;

	netmanthan.route_history_queue = [];

	netmanthan
		.xcall("netmanthan.desk.doctype.route_history.route_history.deferred_insert", {
			routes: routes,
		})
		.catch(() => {
			netmanthan.route_history_queue.concat(routes);
		});
}, 10000);

netmanthan.router.on("change", () => {
	const route = netmanthan.get_route();
	if (is_route_useful(route)) {
		netmanthan.route_history_queue.push({
			creation: netmanthan.datetime.now_datetime(),
			route: netmanthan.get_route_str(),
		});

		save_routes();
	}
});

function is_route_useful(route) {
	if (!route[1]) {
		return false;
	} else if ((route[0] === "List" && !route[2]) || routes_to_skip.includes(route[0])) {
		return false;
	} else {
		return true;
	}
}
