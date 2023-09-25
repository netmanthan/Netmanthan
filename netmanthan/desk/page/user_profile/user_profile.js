netmanthan.pages["user-profile"].on_page_load = function (wrapper) {
	netmanthan.require("user_profile_controller.bundle.js", () => {
		let user_profile = new netmanthan.ui.UserProfile(wrapper);
		user_profile.show();
	});
};
