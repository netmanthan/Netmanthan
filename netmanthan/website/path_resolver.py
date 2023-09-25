import re

import click
from werkzeug.routing import Rule

import netmanthan
from netmanthan.website.page_renderers.document_page import DocumentPage
from netmanthan.website.page_renderers.list_page import ListPage
from netmanthan.website.page_renderers.not_found_page import NotFoundPage
from netmanthan.website.page_renderers.print_page import PrintPage
from netmanthan.website.page_renderers.redirect_page import RedirectPage
from netmanthan.website.page_renderers.static_page import StaticPage
from netmanthan.website.page_renderers.template_page import TemplatePage
from netmanthan.website.page_renderers.web_form import WebFormPage
from netmanthan.website.router import evaluate_dynamic_routes
from netmanthan.website.utils import can_cache, get_home_page


class PathResolver:
	__slots__ = ("path",)

	def __init__(self, path):
		self.path = path.strip("/ ")

	def resolve(self):
		"""Returns endpoint and a renderer instance that can render the endpoint"""
		request = netmanthan._dict()
		if hasattr(netmanthan.local, "request"):
			request = netmanthan.local.request or request

		# check if the request url is in 404 list
		if request.url and can_cache() and netmanthan.cache().hget("website_404", request.url):
			return self.path, NotFoundPage(self.path)

		try:
			resolve_redirect(self.path, request.query_string)
		except netmanthan.Redirect:
			return netmanthan.flags.redirect_location, RedirectPage(self.path)

		endpoint = resolve_path(self.path)

		# WARN: Hardcoded for better performance
		if endpoint == "app":
			return endpoint, TemplatePage(endpoint, 200)

		custom_renderers = self.get_custom_page_renderers()
		renderers = custom_renderers + [
			StaticPage,
			WebFormPage,
			DocumentPage,
			TemplatePage,
			ListPage,
			PrintPage,
			NotFoundPage,
		]

		for renderer in renderers:
			renderer_instance = renderer(endpoint, 200)
			if renderer_instance.can_render():
				return endpoint, renderer_instance

		return endpoint, NotFoundPage(endpoint)

	def is_valid_path(self):
		_endpoint, renderer_instance = self.resolve()
		return not isinstance(renderer_instance, NotFoundPage)

	@staticmethod
	def get_custom_page_renderers():
		custom_renderers = []
		for renderer_path in netmanthan.get_hooks("page_renderer") or []:
			try:
				renderer = netmanthan.get_attr(renderer_path)
				if not hasattr(renderer, "can_render"):
					click.echo(f"{renderer.__name__} does not have can_render method")
					continue
				if not hasattr(renderer, "render"):
					click.echo(f"{renderer.__name__} does not have render method")
					continue

				custom_renderers.append(renderer)

			except Exception:
				click.echo(f"Failed to load page renderer. Import path: {renderer_path}")

		return custom_renderers


def resolve_redirect(path, query_string=None):
	"""
	Resolve redirects from hooks

	Example:

	        website_redirect = [
	                # absolute location
	                {"source": "/from", "target": "https://mysite/from"},

	                # relative location
	                {"source": "/from", "target": "/main"},

	                # use regex
	                {"source": r"/from/(.*)", "target": r"/main/\1"}
	                # use r as a string prefix if you use regex groups or want to escape any string literal
	        ]
	"""
	redirects = netmanthan.get_hooks("website_redirects")
	redirects += netmanthan.get_all("Website Route Redirect", ["source", "target"], order_by=None)

	if not redirects:
		return

	redirect_to = netmanthan.cache().hget("website_redirects", path)

	if redirect_to:
		netmanthan.flags.redirect_location = redirect_to
		raise netmanthan.Redirect

	for rule in redirects:
		pattern = rule["source"].strip("/ ") + "$"
		path_to_match = path
		if rule.get("match_with_query_string"):
			path_to_match = path + "?" + netmanthan.safe_decode(query_string)

		if re.match(pattern, path_to_match):
			redirect_to = re.sub(pattern, rule["target"], path_to_match)
			netmanthan.flags.redirect_location = redirect_to
			netmanthan.cache().hset("website_redirects", path_to_match, redirect_to)
			raise netmanthan.Redirect


def resolve_path(path):
	if not path:
		path = "index"

	if path.endswith(".html"):
		path = path[:-5]

	if path == "index":
		path = get_home_page()

	netmanthan.local.path = path

	if path != "index":
		path = resolve_from_map(path)

	return path


def resolve_from_map(path):
	"""transform dynamic route to a static one from hooks and route defined in doctype"""
	rules = [
		Rule(r["from_route"], endpoint=r["to_route"], defaults=r.get("defaults"))
		for r in get_website_rules()
	]

	return evaluate_dynamic_routes(rules, path) or path


def get_website_rules():
	"""Get website route rules from hooks and DocType route"""

	def _get():
		rules = netmanthan.get_hooks("website_route_rules")
		for d in netmanthan.get_all("DocType", "name, route", dict(has_web_view=1)):
			if d.route:
				rules.append(dict(from_route="/" + d.route.strip("/"), to_route=d.name))

		return rules

	if netmanthan.local.dev_server:
		# dont cache in development
		return _get()

	return netmanthan.cache().get_value("website_route_rules", _get)
