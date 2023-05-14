from unittest import TestCase

from shortener.forms import ShortenForm
from shortener.services import alias_validation

from .common_data import *


class AliasValidationTests(TestCase):
    def test_alias_validation_with_restricted_characters(self):
        strs_to_validate = strs_to_validate_restricted_characters

        for str in strs_to_validate:
            self.assertFalse(alias_validation(str))

    def test_alias_validation_with_allowed_characters(self):
        strs_to_validate = strs_to_validate_allowed_characters

        for str in strs_to_validate:
            self.assertTrue(alias_validation(str))

    def test_alias_validation_with_restricted_phrases(self):
        strs_to_validate = strs_to_validate_restricted_phrases

        for str in strs_to_validate:
            self.assertFalse(alias_validation(str))

    def test_alias_validation_with_allowed_phrases(self):
        strs_to_validate = strs_to_validate_allowed_phrases

        for str in strs_to_validate:
            self.assertTrue(alias_validation(str))

    def test_if_will_an_error_be_added_to_the_form_with_restricted_characters(self):
        self._test_restrictions(
            "Only alphabetic characters, numerals and hyphen are available for the alias",
            strs_to_validate_restricted_characters,
        )

    def test_if_will_an_error_be_added_to_the_form_with_restricted_phrases(self):
        self._test_restrictions("This alias is not allowed", strs_to_validate_restricted_phrases)

    def _test_restrictions(self, error_value, strs_to_validate):
        for str in strs_to_validate:
            shorten_form = ShortenForm(data={"long_link": "youtube.com"})
            if shorten_form.is_valid():
                alias_validation(str, shorten_form)
                errors = shorten_form.errors.get("alias")
                self.assertTrue(error_value in errors)
