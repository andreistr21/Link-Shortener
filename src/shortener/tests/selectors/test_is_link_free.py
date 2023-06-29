from django.test import TestCase


from shortener.selectors import is_alias_free
from shortener.models import Link


class IsLinkFreeTests(TestCase):
    def tearDown(self) -> None:
        Link.objects.all().delete()

    def test_if_alias_dont_exists(self):
        alias = "test-value"
        self.assertTrue(is_alias_free(alias))

    def test_if_alias_exists(self):
        alias = "test-value"
        long_link = "youtube.com"
        Link.objects.create(long_link=long_link, alias=alias)

        self.assertFalse(is_alias_free(alias))

    def test_if_alias_exists_with_excluding_current_link(self):
        links = Link.objects.bulk_create(
            [
                Link(alias="test-value", long_link="youtube.com"),
                Link(alias="test-value2", long_link="youtube.com"),
                Link(alias="test-value3", long_link="youtube.com"),
            ]
        )

        resp = is_alias_free(links[0].alias, links[0])

        self.assertTrue(resp)

    def test_if_alias_exists_with_excluding_not_current_link(self):
        links = Link.objects.bulk_create(
            [
                Link(alias="test-value", long_link="youtube.com"),
                Link(alias="test-value2", long_link="youtube.com"),
                Link(alias="test-value3", long_link="youtube.com"),
            ]
        )

        resp = is_alias_free(links[0].alias, links[1])

        self.assertFalse(resp)
