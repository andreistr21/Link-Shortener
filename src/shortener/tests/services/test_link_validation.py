from unittest import TestCase

from shortener.forms import ShortenForm
from shortener.services import link_validation


class LinkValidationTests(TestCase):
    def test_if_link_valid(self):
        valid_links = [
            "https://www.youtube.com/",
            "https://youtube.com/",
        ]

        for link in valid_links:
            shorten_form = ShortenForm(data={"long_link": link})
            shorten_form.is_valid()

            self.assertTrue(link_validation(shorten_form))

    def test_if_link_invalid(self):
        valid_links = [
            "www.youtube.com/",
            "youtube",
            "youtube.com",
        ]

        for link in valid_links:
            shorten_form = ShortenForm(data={"long_link": link})
            shorten_form.is_valid()

            self.assertFalse(link_validation(shorten_form))

    def test_if_link_invalid_expect_form_error(self):
        error_value = "Enter a valid link"
        shorten_form = ShortenForm(data={"long_link": "youtube"})
        shorten_form.is_valid()

        link_validation(shorten_form)
        errors = shorten_form.errors.get("long_link")
        self.assertTrue(error_value in errors)

    def test_with_restricted_domain(self):
        restricted_links = [
            "http://127.0.0.1:8000",
            "https://127.0.0.1:8000/account",
        ]

        for link in restricted_links:
            shorten_form = ShortenForm(data={"long_link": link})
            shorten_form.is_valid()

            self.assertFalse(link_validation(shorten_form))

    def test_with_restricted_domain_expect_form_error(self):
        restricted_links = [
            "http://127.0.0.1:8000",
            "https://127.0.0.1:8000/account",
        ]
        error_value = "This domain is banned or invalid"

        for link in restricted_links:
            shorten_form = ShortenForm(data={"long_link": link})
            shorten_form.is_valid()
            link_validation(shorten_form)

            errors = shorten_form.errors.get("long_link")
            self.assertTrue(error_value in errors)
