import netmanthan
from netmanthan import _
from netmanthan.utils import cstr
from netmanthan.website.page_renderers.template_page import TemplatePage


class NotPermittedPage(TemplatePage):
	def __init__(self, path=None, http_status_code=None, exception=""):
		netmanthan.local.message = cstr(exception)
		super().__init__(path=path, http_status_code=http_status_code)
		self.http_status_code = 403

	def can_render(self):
		return True

	def render(self):
		action = f"/login?redirect-to={netmanthan.request.path}"
		if netmanthan.request.path.startswith("/app"):
			action = "/login"
		netmanthan.local.message_title = _("Not Permitted")
		netmanthan.local.response["context"] = dict(
			indicator_color="red", primary_action=action, primary_label=_("Login"), fullpage=True
		)
		self.set_standard_path("message")
		return super().render()
