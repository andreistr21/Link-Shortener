from django.test import TestCase

from shortener.forms import ShortenForm
from shortener.models import Link
from shortener.services import save_link


class SaveLinkTests(TestCase):
    def setUp(self) -> None:
        Link.objects.all().delete()

    def test_save_with_form_and_alias(self):
        long_link = "youtube.com"
        alias = "test-short-link"
        shorten_form = ShortenForm(data={"long_link": long_link})
        save_link(shorten_form, alias)

        self.assertTrue(Link.objects.filter(long_link=long_link).exists())

    def test_save_with_form_only(self):
        long_link = "youtube.com"
        shorten_form = ShortenForm(data={"long_link": long_link})
        save_link(shorten_form)

        self.assertTrue(Link.objects.filter(long_link=long_link).exists())

    def test_save_with_existing_long_link(self):
        long_link = "youtube.com"
        shorten_form_1 = ShortenForm(data={"long_link": long_link})
        shorten_form_2 = ShortenForm(data={"long_link": long_link})
        save_link(shorten_form_1)
        save_link(shorten_form_2)

        self.assertTrue(Link.objects.filter(long_link=long_link).count() == 2)
