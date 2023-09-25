// Copyright (c) 2015, netmanthan Technologies Pvt. Ltd. and Contributors
// MIT License. See license.txt

netmanthan.provide("netmanthan.help");

netmanthan.help.youtube_id = {};

netmanthan.help.has_help = function (doctype) {
	return netmanthan.help.youtube_id[doctype];
};

netmanthan.help.show = function (doctype) {
	if (netmanthan.help.youtube_id[doctype]) {
		netmanthan.help.show_video(netmanthan.help.youtube_id[doctype]);
	}
};

netmanthan.help.show_video = function (youtube_id, title) {
	if (netmanthan.utils.is_url(youtube_id)) {
		const expression =
			'(?:youtube.com/(?:[^/]+/.+/|(?:v|e(?:mbed)?)/|.*[?&]v=)|youtu.be/)([^"&?\\s]{11})';
		youtube_id = youtube_id.match(expression)[1];
	}

	// (netmanthan.help_feedback_link || "")
	let dialog = new netmanthan.ui.Dialog({
		title: title || __("Help"),
		size: "large",
	});

	let video = $(
		`<div class="video-player" data-plyr-provider="youtube" data-plyr-embed-id="${youtube_id}"></div>`
	);
	video.appendTo(dialog.body);

	dialog.show();
	dialog.$wrapper.addClass("video-modal");

	let plyr;
	netmanthan.utils.load_video_player().then(() => {
		plyr = new netmanthan.Plyr(video[0], {
			hideControls: true,
			resetOnEnd: true,
		});
	});

	dialog.onhide = () => {
		plyr?.destroy();
	};
};

$("body").on("click", "a.help-link", function () {
	var doctype = $(this).attr("data-doctype");
	doctype && netmanthan.help.show(doctype);
});
