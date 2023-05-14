from django.test import TestCase


from shortener.selectors import is_alias_free
from shortener.models import Link


class IsLinkFreeTests(TestCase):
    def test_if_alias_dont_exists(self):
        alias = "test-value"
        self.assertTrue(is_alias_free(alias))

    def test_if_alias_exists(self):
        alias = "test-value"
        long_link = "youtube.com"
        Link.objects.create(long_link=long_link, alias=alias)
        
        self.assertFalse(is_alias_free(alias))
        