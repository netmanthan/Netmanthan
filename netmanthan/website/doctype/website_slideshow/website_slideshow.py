# Copyright (c) 2015, netmanthan Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

# License: MIT. See LICENSE

import netmanthan
from netmanthan import _
from netmanthan.model.document import Document


class WebsiteSlideshow(Document):
	def validate(self):
		self.validate_images()

	def on_update(self):
		# a slide show can be in use and any change in it should get reflected
		from netmanthan.website.utils import clear_cache

		clear_cache()

	def validate_images(self):
		"""atleast one image file should be public for slideshow"""
		files = map(lambda row: row.image, self.slideshow_items)
		if files:
			result = netmanthan.get_all("File", filters={"file_url": ("in", list(files))}, fields="is_private")
			if any(file.is_private for file in result):
				netmanthan.throw(_("All Images attached to Website Slideshow should be public"))


def get_slideshow(doc):
	if not doc.slideshow:
		return {}

	slideshow = netmanthan.get_doc("Website Slideshow", doc.slideshow)

	return {
		"slides": slideshow.get({"doctype": "Website Slideshow Item"}),
		"slideshow_header": slideshow.header or "",
	}
