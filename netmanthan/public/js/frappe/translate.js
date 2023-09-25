// Copyright (c) 2015, netmanthan Technologies Pvt. Ltd. and Contributors
// MIT License. See license.txt

// for translation
netmanthan._ = function (txt, replace, context = null) {
	if (!txt) return txt;
	if (typeof txt != "string") return txt;

	let translated_text = "";

	let key = txt; // txt.replace(/\n/g, "");
	if (context) {
		translated_text = netmanthan._messages[`${key}:${context}`];
	}

	if (!translated_text) {
		translated_text = netmanthan._messages[key] || txt;
	}

	if (replace && typeof replace === "object") {
		translated_text = $.format(translated_text, replace);
	}
	return translated_text;
};

window.__ = netmanthan._;

netmanthan.get_languages = function () {
	if (!netmanthan.languages) {
		netmanthan.languages = [];
		$.each(netmanthan.boot.lang_dict, function (lang, value) {
			netmanthan.languages.push({ label: lang, value: value });
		});
		netmanthan.languages = netmanthan.languages.sort(function (a, b) {
			return a.value < b.value ? -1 : 1;
		});
	}
	return netmanthan.languages;
};
