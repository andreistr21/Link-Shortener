from unittest.mock import patch

from django.test import TestCase

from shortener.forms import ShortenForm
from shortener.services import short_link


class ShortLinkTests(TestCase):
    @patch("shortener.services.link_validation")
    def test_if_link_validation_method_executed(self, link_validation_mock):
        long_link = "https://www.youtube.com/"
        shorten_form = ShortenForm(data={"long_link": long_link})
        shorten_form.is_valid()
        short_link(shorten_form)
        
        link_validation_mock.assert_called_once()
        
    @patch("shortener.services.short_with_alias")
    def test_if_short_with_alias_method_executed(self, short_with_alias_mock):
        long_link = "https://www.youtube.com/"
        alias = "test-case-alias"
        shorten_form = ShortenForm(data={"long_link": long_link, "alias": alias})
        shorten_form.is_valid()
        short_link(shorten_form)
        
        short_with_alias_mock.assert_called_once()

    @patch("shortener.services.short_with_random_value")
    def test_if_short_with_random_value_method_executed(self, short_with_random_value_mock):
        long_link = "https://www.youtube.com/"
        shorten_form = ShortenForm(data={"long_link": long_link})
        shorten_form.is_valid()
        short_link(shorten_form)
        
        short_with_random_value_mock.assert_called_once()
        
        
    def test_if_error_will_be_added_with_short_alias(self):
        long_link = "https://www.youtube.com/"
        alias = "shr"
        shorten_form = ShortenForm(data={"long_link": long_link, "alias": alias})
        shorten_form.is_valid()
        short_link(shorten_form)
        error_value = "The alias must be at least 4 characters"
        form_errors = shorten_form.errors.get("alias")
        
        self.assertTrue(error_value in form_errors)
        
        