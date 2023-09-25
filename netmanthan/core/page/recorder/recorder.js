netmanthan.pages["recorder"].on_page_load = function (wrapper) {
	netmanthan.ui.make_app_page({
		parent: wrapper,
		title: __("Recorder"),
		single_column: true,
		card_layout: true,
	});

	netmanthan.recorder = new Recorder(wrapper);
	$(wrapper).bind("show", function () {
		netmanthan.recorder.show();
	});

	netmanthan.require("recorder.bundle.js");
};

class Recorder {
	constructor(wrapper) {
		this.wrapper = $(wrapper);
		this.container = this.wrapper.find(".layout-main-section");
		this.container.append($('<div class="recorder-container"></div>'));
	}

	show() {
		if (!this.view || this.view.$route.name == "recorder-detail") return;
		this.view.$router.replace({ name: "recorder-detail" });
	}
}
