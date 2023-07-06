from unittest import mock
from django.test import TestCase

from account.services import remove_link
from shortener.models import Link


class RemoveLinkTests(TestCase):
    @mock.patch("account.services.remove_link_statistics")
    def test_link_deletion(self, remove_link_statistics_mock):
        link = Link.objects.create(
            long_link="https://www.youtube.com/", alias="youtube"
        )
        remove_link(link)

        self.assertFalse(Link.objects.all().exists())
        remove_link_statistics_mock.assert_called_once_with(link.alias)
