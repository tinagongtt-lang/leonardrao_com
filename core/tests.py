from django.test import TestCase
from django.urls import reverse

from .models import FriendlyLink


class CoreViewTests(TestCase):
    def test_homepage_200(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_robots_txt(self):
        response = self.client.get('/robots.txt')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sitemap: /sitemap.xml')

    def test_sitemap_xml(self):
        response = self.client.get('/sitemap.xml')
        self.assertEqual(response.status_code, 200)


class FriendlyLinkTests(TestCase):
    def test_create_link(self):
        link = FriendlyLink.objects.create(name='Example', url='https://example.com')
        self.assertEqual(str(link), 'Example')
