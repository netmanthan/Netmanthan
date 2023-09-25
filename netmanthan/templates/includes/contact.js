// Copyright (c) 2015, netmanthan Technologies Pvt. Ltd. and Contributors
// MIT License. See license.txt

netmanthan.ready(function() {

	if(netmanthan.utils.get_url_arg('subject')) {
	  $('[name="subject"]').val(netmanthan.utils.get_url_arg('subject'));
	}

	$('.btn-send').off("click").on("click", function() {
		var email = $('[name="email"]').val();
		var message = $('[name="message"]').val();

		if(!(email && message)) {
			netmanthan.msgprint('{{ _("Please enter both your email and message so that we can get back to you. Thanks!") }}');
			return false;
		}

		if(!validate_email(email)) {
			netmanthan.msgprint('{{ _("You seem to have written your name instead of your email. Please enter a valid email address so that we can get back.") }}');
			$('[name="email"]').focus();
			return false;
		}

		$("#contact-alert").toggle(false);
		netmanthan.send_message({
			subject: $('[name="subject"]').val(),
			sender: email,
			message: message,
			callback: function(r) {
				if (!r.exc) {
					netmanthan.msgprint('{{ _("Thank you for your message") }}');
				}
				$(':input').val('');
			}
		}, this);
		return false;
	});

});

var msgprint = function(txt) {
	if(txt) $("#contact-alert").html(txt).toggle(true);
}
