netmanthan.ui.form.FormViewers = class FormViewers {
	constructor({ frm, parent }) {
		this.frm = frm;
		this.parent = parent;
		this.parent.tooltip({ title: __("Currently Viewing") });
	}

	refresh() {
		let users = this.frm.get_docinfo()["viewers"];
		if (!users || !users.current || !users.current.length) {
			this.parent.empty();
			return;
		}

		let currently_viewing = users.current.filter((user) => user != netmanthan.session.user);
		let avatar_group = netmanthan.avatar_group(currently_viewing, 5, {
			align: "left",
			overlap: true,
		});
		this.parent.empty().append(avatar_group);
	}
};

netmanthan.ui.form.FormViewers.set_users = function (data, type) {
	const doctype = data.doctype;
	const docname = data.docname;
	const docinfo = netmanthan.model.get_docinfo(doctype, docname);

	const past_users = ((docinfo && docinfo[type]) || {}).past || [];
	const users = data.users || [];
	const new_users = users.filter((user) => !past_users.includes(user));

	if (new_users.length === 0) return;

	const set_and_refresh = () => {
		const info = {
			past: past_users.concat(new_users),
			new: new_users,
			current: users,
		};

		netmanthan.model.set_docinfo(doctype, docname, type, info);

		if (
			cur_frm &&
			cur_frm.doc &&
			cur_frm.doc.doctype === doctype &&
			cur_frm.doc.name == docname &&
			cur_frm.viewers
		) {
			cur_frm.viewers.refresh(true, type);
		}
	};

	let unknown_users = [];
	for (let user of users) {
		if (!netmanthan.boot.user_info[user]) unknown_users.push(user);
	}

	if (unknown_users.length === 0) {
		set_and_refresh();
	} else {
		// load additional user info
		netmanthan
			.xcall("netmanthan.desk.form.load.get_user_info_for_viewers", { users: unknown_users })
			.then((data) => {
				Object.assign(netmanthan.boot.user_info, data);
				set_and_refresh();
			});
	}
};
