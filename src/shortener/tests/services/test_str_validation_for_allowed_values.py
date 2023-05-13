from django.conf import settings
from django.test import TestCase

from shortener.services import validate_str_for_allowed_values


class StrValidationForAllowedValuesTests(TestCase):
    def test_validation_with_restricted_values(self):
        strs_to_validate = [
            "alias*",
            "library^",
            "lap%top",
            "some_str",
            "str#2",
            "(value)",
            "v[alidati]on",
            "do.t",
            ",comma",
            "questionmark?",
            "!mark",
            "equal=",
        ]
        allowed_values = settings.ALLOWED_CHARACTERS

        for str in strs_to_validate:
            self.assertFalse(validate_str_for_allowed_values(str, allowed_values))

    def test_validation_with_allowed_values(self):
        allowed_values = settings.ALLOWED_CHARACTERS

        strs_to_validate = [
            "properAlias",
            "alias",
            "test-alias",
            "New-aliAs",
            "some-text",
            "t3st",
            "text5",
        ]
        
        for str in strs_to_validate:
            self.assertTrue(validate_str_for_allowed_values(str, allowed_values))
