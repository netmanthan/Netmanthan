# Copyright (c) 2015, netmanthan Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import netmanthan
from netmanthan import _
from netmanthan.model.document import Document
from netmanthan.utils import flt, is_image


class LetterHead(Document):
	def before_insert(self):
		# for better UX, let user set from attachment
		self.source = "Image"

	def validate(self):
		self.set_image()
		self.validate_disabled_and_default()

	def validate_disabled_and_default(self):
		if self.disabled and self.is_default:
			netmanthan.throw(_("Letter Head cannot be both disabled and default"))

		if not self.is_default and not self.disabled:
			if not netmanthan.db.exists("Letter Head", dict(is_default=1)):
				self.is_default = 1

	def set_image(self):
		if self.source == "Image":
			self.set_image_as_html(
				field="image",
				width="image_width",
				height="image_height",
				align="align",
				html_field="content",
				dimension_prefix="image_",
				success_msg=_("Header HTML set from attachment {0}").format(self.image),
				failure_msg=_("Please attach an image file to set HTML for Letter Head."),
			)

		if self.footer_source == "Image":
			self.set_image_as_html(
				field="footer_image",
				width="footer_image_width",
				height="footer_image_height",
				align="footer_align",
				html_field="footer",
				dimension_prefix="footer_image_",
				success_msg=_("Footer HTML set from attachment {0}").format(self.footer_image),
				failure_msg=_("Please attach an image file to set HTML for Footer."),
			)

	def set_image_as_html(
		self, field, width, height, dimension_prefix, align, html_field, success_msg, failure_msg
	):
		if not self.get(field) or not is_image(self.get(field)):
			netmanthan.msgprint(failure_msg, alert=True, indicator="orange")
			return

		self.set(width, flt(self.get(width)))
		self.set(height, flt(self.get(height)))

		# To preserve the aspect ratio of the image, apply constraints only on
		# the greater dimension and allow the other to scale accordingly
		dimension = "width" if self.get(width) > self.get(height) else "height"
		dimension_value = self.get(f"{dimension_prefix}{dimension}")

		if not dimension_value:
			dimension_value = ""

		self.set(
			html_field,
			f"""<div style="text-align: {self.get(align, "").lower()};">
<img src="{self.get(field)}" alt="{self.get("name")}"
{dimension}="{dimension_value}" style="{dimension}: {dimension_value}px;">
</div>""",
		)

		netmanthan.msgprint(success_msg, alert=True)

	def on_update(self):
		self.set_as_default()

		# clear the cache so that the new letter head is uploaded
		netmanthan.clear_cache()

	def set_as_default(self):
		from netmanthan.utils import set_default

		if self.is_default:
			netmanthan.db.sql("update `tabLetter Head` set is_default=0 where name != %s", self.name)

			set_default("letter_head", self.name)

			# update control panel - so it loads new letter directly
			netmanthan.db.set_default("default_letter_head_content", self.content)
		else:
			netmanthan.defaults.clear_default("letter_head", self.name)
			netmanthan.defaults.clear_default("default_letter_head_content", self.content)
