# Copyright (c) 2017, netmanthan Technologies and Contributors
# License: MIT. See LICENSE
import netmanthan
from netmanthan.tests.utils import netmanthanTestCase


class TestLetterHead(netmanthanTestCase):
	def test_auto_image(self):
		letter_head = netmanthan.get_doc(
			dict(doctype="Letter Head", letter_head_name="Test", source="Image", image="/public/test.png")
		).insert()

		# test if image is automatically set
		self.assertTrue(letter_head.image in letter_head.content)
