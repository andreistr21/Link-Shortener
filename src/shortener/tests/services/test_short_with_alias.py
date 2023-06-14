from unittest import TestCase

from django.test import RequestFactory
from django.urls import reverse
from django.contrib.auth.models import AnonymousUser

from shortener.forms import ShortenForm
from shortener.models import Link
from shortener.services import short_with_alias


class ShortWithAliasTests(TestCase):
    def setUp(self):
        Link.objects.all().delete()
        self.request_factory = RequestFactory()
        self.request = self.request_factory.get(reverse("shortener:index"))
        self.request.user = AnonymousUser()

    def test_if_alias_taken(self):
        long_link = "youtube.com"
        alias = "test-value"
        Link.objects.create(long_link=long_link, alias=alias)
        shorten_form = ShortenForm(
            data={"long_link": long_link, "alias": alias}
        )
        shorten_form.is_valid()
        error_value = "This alias is unavailable"

        short_with_alias(self.request, alias, shorten_form)

        errors = shorten_form.errors.get("alias")
        self.assertTrue(error_value in errors)

    def test_if_alias_is_free(self):
        long_link = "youtube.com"
        alias = "test-value"
        shorten_form = ShortenForm(
            data={"long_link": long_link, "alias": alias}
        )
        shorten_form.is_valid()

        short_with_alias(self.request, alias, shorten_form)

        self.assertTrue(Link.objects.filter(alias=alias).exists())
