# Copyright (c) 2013, netmanthan and contributors
# License: MIT. See LICENSE

import netmanthan
from netmanthan import _
from netmanthan.utils import cint, is_markdown, markdown
from netmanthan.website.utils import get_comment_list
from netmanthan.website.website_generator import WebsiteGenerator


class HelpArticle(WebsiteGenerator):
	def validate(self):
		self.set_route()

	def set_route(self):
		"""Set route from category and title if missing"""
		if not self.route:
			self.route = "/".join(
				[netmanthan.get_value("Help Category", self.category, "route"), self.scrub(self.title)]
			)

	def on_update(self):
		self.update_category()
		clear_cache()

	def update_category(self):
		cnt = netmanthan.db.sql(
			"""select count(*) from `tabHelp Article`
			where category=%s and ifnull(published,0)=1""",
			self.category,
		)[0][0]
		cat = netmanthan.get_doc("Help Category", self.category)
		cat.help_articles = cnt
		cat.save()

	def get_context(self, context):
		if is_markdown(context.content):
			context.content = markdown(context.content)
		context.login_required = True
		context.category = netmanthan.get_doc("Help Category", self.category)
		context.level_class = get_level_class(self.level)
		context.comment_list = get_comment_list(self.doctype, self.name)
		context.show_sidebar = True
		context.sidebar_items = get_sidebar_items()
		context.parents = self.get_parents(context)

	def get_parents(self, context):
		return [{"title": context.category.category_name, "route": context.category.route}]


def get_list_context(context=None):
	filters = dict(published=1)

	category = netmanthan.db.get_value("Help Category", {"route": netmanthan.local.path})

	if category:
		filters["category"] = category

	list_context = netmanthan._dict(
		title=category or _("Knowledge Base"),
		get_level_class=get_level_class,
		show_sidebar=True,
		sidebar_items=get_sidebar_items(),
		hide_filters=True,
		filters=filters,
		category=netmanthan.local.form_dict.category,
		no_breadcrumbs=True,
	)

	if netmanthan.local.form_dict.txt:
		list_context.blog_subtitle = _('Filtered by "{0}"').format(netmanthan.local.form_dict.txt)
	#
	# list_context.update(netmanthan.get_doc("Blog Settings", "Blog Settings").as_dict())
	return list_context


def get_level_class(level):
	return {"Beginner": "green", "Intermediate": "orange", "Expert": "red"}[level]


def get_sidebar_items():
	def _get():
		return netmanthan.db.sql(
			"""select
				concat(category_name, " (", help_articles, ")") as title,
				concat('/', route) as route
			from
				`tabHelp Category`
			where
				ifnull(published,0)=1 and help_articles > 0
			order by
				help_articles desc""",
			as_dict=True,
		)

	return netmanthan.cache().get_value("knowledge_base:category_sidebar", _get)


def clear_cache():
	clear_website_cache()

	from netmanthan.website.utils import clear_cache

	clear_cache()


def clear_website_cache(path=None):
	netmanthan.cache().delete_value("knowledge_base:category_sidebar")
	netmanthan.cache().delete_value("knowledge_base:faq")


@netmanthan.whitelist(allow_guest=True)
def add_feedback(article, helpful):
	field = "helpful"
	if helpful == "No":
		field = "not_helpful"

	value = cint(netmanthan.db.get_value("Help Article", article, field))
	netmanthan.db.set_value("Help Article", article, field, value + 1, update_modified=False)
