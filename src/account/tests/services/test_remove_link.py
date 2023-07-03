from django.test import TestCase

from account.services import remove_link
from shortener.models import Link


class RemoveLinkTests(TestCase):
    def test_link_deletion(self):
        link = Link.objects.create(
            long_link="https://www.youtube.com/", alias="youtube"
        )
        remove_link(link)

        self.assertFalse(Link.objects.all().exists())
