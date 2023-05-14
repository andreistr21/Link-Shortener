from unittest import TestCase

from django.conf import settings

from shortener.services import validate_str_for_allowed_values

from .common_data import strs_to_validate_allowed_characters, strs_to_validate_restricted_characters


class StrValidationForAllowedValuesTests(TestCase):
    def test_validation_with_restricted_values(self):
        strs_to_validate = strs_to_validate_restricted_characters

        for str in strs_to_validate:
            self.assertFalse(validate_str_for_allowed_values(str))

    def test_validation_with_allowed_values(self):
        strs_to_validate = strs_to_validate_allowed_characters

        for str in strs_to_validate:
            self.assertTrue(validate_str_for_allowed_values(str))
