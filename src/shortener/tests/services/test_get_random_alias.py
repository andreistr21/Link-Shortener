from django.test import TestCase
from unittest import mock

from shortener.forms import ShortenForm
from shortener.models import Link
from shortener.services import get_random_alias, save_link
from shortener.selectors import is_alias_free


class GetRandomAliasTests(TestCase):
    def _is_alias_free(self, alias):
        return not Link.objects.filter(alias=alias).exists()

    def test_if_given_alias_free(self):
        for _ in range(100):
            alias = get_random_alias()
            self.assertTrue(self._is_alias_free(alias))

    @mock.patch("shortener.services.gen_random_str")
    def test_if_alias_taken(self, gen_random_str_mock):
        long_link = "youtube.com"
        alias_1 = "testval1"
        alias_2 = "testval2"
        shorten_form = ShortenForm(data={"long_link": long_link, "alias": alias_1})
        save_link(shorten_form)

        gen_random_str_mock.side_effect = [alias_1, alias_2]
        returned_alias = get_random_alias()

        self.assertEqual(returned_alias, alias_2)
        self.assertEqual(gen_random_str_mock.call_count, 2)
