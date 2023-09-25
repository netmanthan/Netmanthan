netmanthan.provide("netmanthan.model");
netmanthan.provide("netmanthan.utils");

/**
 * Opens the Website Meta Tag form if it exists for {route}
 * or creates a new doc and opens the form
 */
netmanthan.utils.set_meta_tag = function (route) {
	netmanthan.db.exists("Website Route Meta", route).then((exists) => {
		if (exists) {
			netmanthan.set_route("Form", "Website Route Meta", route);
		} else {
			// new doc
			const doc = netmanthan.model.get_new_doc("Website Route Meta");
			doc.__newname = route;
			netmanthan.set_route("Form", doc.doctype, doc.name);
		}
	});
};
