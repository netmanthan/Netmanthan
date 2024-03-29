import click

from netmanthan.commands import get_site, pass_context
from netmanthan.exceptions import SiteNotSpecifiedError


# translation
@click.command("build-message-files")
@pass_context
def build_message_files(context):
	"Build message files for translation"
	import netmanthan.translate

	for site in context.sites:
		try:
			netmanthan.init(site=site)
			netmanthan.connect()
			netmanthan.translate.rebuild_all_translation_files()
		finally:
			netmanthan.destroy()
	if not context.sites:
		raise SiteNotSpecifiedError


@click.command("new-language")  # , help="Create lang-code.csv for given app")
@pass_context
@click.argument("lang_code")  # , help="Language code eg. en")
@click.argument("app")  # , help="App name eg. netmanthan")
def new_language(context, lang_code, app):
	"""Create lang-code.csv for given app"""
	import netmanthan.translate

	if not context["sites"]:
		raise Exception("--site is required")

	# init site
	netmanthan.connect(site=context["sites"][0])
	netmanthan.translate.write_translations_file(app, lang_code)

	print(
		"File created at ./apps/{app}/{app}/translations/{lang_code}.csv".format(
			app=app, lang_code=lang_code
		)
	)
	print(
		"You will need to add the language in netmanthan/geo/languages.json, if you haven't done it already."
	)


@click.command("get-untranslated")
@click.option("--app", default="_ALL_APPS")
@click.argument("lang")
@click.argument("untranslated_file")
@click.option("--all", default=False, is_flag=True, help="Get all message strings")
@pass_context
def get_untranslated(context, lang, untranslated_file, app="_ALL_APPS", all=None):
	"Get untranslated strings for language"
	import netmanthan.translate

	site = get_site(context)
	try:
		netmanthan.init(site=site)
		netmanthan.connect()
		netmanthan.translate.get_untranslated(lang, untranslated_file, get_all=all, app=app)
	finally:
		netmanthan.destroy()


@click.command("update-translations")
@click.option("--app", default="_ALL_APPS")
@click.argument("lang")
@click.argument("untranslated_file")
@click.argument("translated-file")
@pass_context
def update_translations(context, lang, untranslated_file, translated_file, app="_ALL_APPS"):
	"Update translated strings"
	import netmanthan.translate

	site = get_site(context)
	try:
		netmanthan.init(site=site)
		netmanthan.connect()
		netmanthan.translate.update_translations(lang, untranslated_file, translated_file, app=app)
	finally:
		netmanthan.destroy()


@click.command("import-translations")
@click.argument("lang")
@click.argument("path")
@pass_context
def import_translations(context, lang, path):
	"Update translated strings"
	import netmanthan.translate

	site = get_site(context)
	try:
		netmanthan.init(site=site)
		netmanthan.connect()
		netmanthan.translate.import_translations(lang, path)
	finally:
		netmanthan.destroy()


commands = [
	build_message_files,
	get_untranslated,
	import_translations,
	new_language,
	update_translations,
]
