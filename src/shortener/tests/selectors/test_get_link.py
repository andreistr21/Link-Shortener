from django.http import Http404
from django.test import TestCase


from shortener.selectors import get_link
from shortener.models import Link


class GetLinkTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.link = Link.objects.create(
            long_link="https://google.com", alias="test-alias"
        )

    def test_link_exists(self):
        link = get_link("test-alias")

        self.assertEqual(link, self.link)

    def test_link_does_not_exists(self):
        self.assertRaises(Http404, get_link, "does-not-exists")
