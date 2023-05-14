from django.db import IntegrityError
from django.test import TestCase

from shortener.models import Link


class SaveLinkTests(TestCase):
    def save_link_test_method(self, long_link, short_link):
        short_link = short_link

        link_1 = Link(long_link=long_link, short_link=short_link)
        link_1.save()

    def test_save_with_long_and_short_links(self):
        long_link = "youtube.com"
        short_link = "test-short-link"

        link = Link(long_link=long_link, short_link=short_link)
        link.save()

        self.assertTrue(Link.objects.filter(long_link=long_link).exists())

    def test_save_with_long_link_only(self):
        long_link = "youtube.com"

        link = Link(long_link=long_link)
        link.save()

        self.assertTrue(Link.objects.filter(long_link=long_link).exists())

    def test_save_with_existing_long_link(self):
        long_link = "youtube.com"
        self.save_link_test_method(long_link, "test-short-link")
        self.save_link_test_method(long_link, "test-short-link-2")

        self.assertTrue(Link.objects.filter(long_link=long_link).count() == 2)

    def test_save_with_existing_short_link(self):
        long_link = "youtube.com"
        short_link = "test-short-link"
        self.save_link_test_method(long_link, short_link)
        
        self.assertRaises(IntegrityError, self.save_link_test_method, long_link=long_link, short_link=short_link)
