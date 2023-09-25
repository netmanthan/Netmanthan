import netmanthan
from netmanthan.website.utils import build_response


class RedirectPage:
	def __init__(self, path, http_status_code=301):
		self.path = path
		self.http_status_code = http_status_code

	def can_render(self):
		return True

	def render(self):
		return build_response(
			self.path,
			"",
			301,
			{
				"Location": netmanthan.flags.redirect_location or (netmanthan.local.response or {}).get("location"),
				"Cache-Control": "no-store, no-cache, must-revalidate",
			},
		)
