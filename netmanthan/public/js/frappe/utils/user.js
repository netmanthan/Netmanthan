netmanthan.user_info = function (uid) {
	if (!uid) uid = netmanthan.session.user;

	if (!(netmanthan.boot.user_info && netmanthan.boot.user_info[uid])) {
		var user_info = { fullname: uid || "Unknown" };
	} else {
		var user_info = netmanthan.boot.user_info[uid];
	}

	user_info.abbr = netmanthan.get_abbr(user_info.fullname);
	user_info.color = netmanthan.get_palette(user_info.fullname);

	return user_info;
};

netmanthan.update_user_info = function (user_info) {
	for (let user in user_info) {
		if (netmanthan.boot.user_info[user]) {
			Object.assign(netmanthan.boot.user_info[user], user_info[user]);
		} else {
			netmanthan.boot.user_info[user] = user_info[user];
		}
	}
};

netmanthan.provide("netmanthan.user");

$.extend(netmanthan.user, {
	name: "Guest",
	full_name: function (uid) {
		return uid === netmanthan.session.user
			? __(
					"You",
					null,
					"Name of the current user. For example: You edited this 5 hours ago."
			  )
			: netmanthan.user_info(uid).fullname;
	},
	image: function (uid) {
		return netmanthan.user_info(uid).image;
	},
	abbr: function (uid) {
		return netmanthan.user_info(uid).abbr;
	},
	has_role: function (rl) {
		if (typeof rl == "string") rl = [rl];
		for (var i in rl) {
			if ((netmanthan.boot ? netmanthan.boot.user.roles : ["Guest"]).indexOf(rl[i]) != -1)
				return true;
		}
	},
	get_desktop_items: function () {
		// hide based on permission
		var modules_list = $.map(netmanthan.boot.allowed_modules, function (icon) {
			var m = icon.module_name;
			var type = netmanthan.modules[m] && netmanthan.modules[m].type;

			if (netmanthan.boot.user.allow_modules.indexOf(m) === -1) return null;

			var ret = null;
			if (type === "module") {
				if (netmanthan.boot.user.allow_modules.indexOf(m) != -1 || netmanthan.modules[m].is_help)
					ret = m;
			} else if (type === "page") {
				if (netmanthan.boot.allowed_pages.indexOf(netmanthan.modules[m].link) != -1) ret = m;
			} else if (type === "list") {
				if (netmanthan.model.can_read(netmanthan.modules[m]._doctype)) ret = m;
			} else if (type === "view") {
				ret = m;
			} else if (type === "setup") {
				if (
					netmanthan.user.has_role("System Manager") ||
					netmanthan.user.has_role("Administrator")
				)
					ret = m;
			} else {
				ret = m;
			}

			return ret;
		});

		return modules_list;
	},

	is_report_manager: function () {
		return netmanthan.user.has_role(["Administrator", "System Manager", "Report Manager"]);
	},

	get_formatted_email: function (email) {
		var fullname = netmanthan.user.full_name(email);

		if (!fullname) {
			return email;
		} else {
			// to quote or to not
			var quote = "";

			// only if these special characters are found
			// why? To make the output same as that in python!
			if (fullname.search(/[\[\]\\()<>@,:;".]/) !== -1) {
				quote = '"';
			}

			return repl("%(quote)s%(fullname)s%(quote)s <%(email)s>", {
				fullname: fullname,
				email: email,
				quote: quote,
			});
		}
	},

	get_emails: () => {
		return Object.keys(netmanthan.boot.user_info).map((key) => netmanthan.boot.user_info[key].email);
	},

	/* Normally netmanthan.user is an object
	 * having properties and methods.
	 * But in the following case
	 *
	 * if (netmanthan.user === 'Administrator')
	 *
	 * netmanthan.user will cast to a string
	 * returning netmanthan.user.name
	 */
	toString: function () {
		return this.name;
	},
});

netmanthan.session_alive = true;
$(document).bind("mousemove", function () {
	if (netmanthan.session_alive === false) {
		$(document).trigger("session_alive");
	}
	netmanthan.session_alive = true;
	if (netmanthan.session_alive_timeout) clearTimeout(netmanthan.session_alive_timeout);
	netmanthan.session_alive_timeout = setTimeout("netmanthan.session_alive=false;", 30000);
});
