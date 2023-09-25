import netmanthan
from netmanthan.tests.utils import netmanthanTestCase
from netmanthan.utils import get_html_for_route


class TestSitemap(netmanthanTestCase):
	def test_sitemap(self):
		from netmanthan.test_runner import make_test_records

		make_test_records("Blog Post")
		blogs = netmanthan.get_all("Blog Post", {"published": 1}, ["route"], limit=1)
		xml = get_html_for_route("sitemap.xml")
		self.assertTrue("/about</loc>" in xml)
		self.assertTrue("/contact</loc>" in xml)
		self.assertTrue(blogs[0].route in xml)
