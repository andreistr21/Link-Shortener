from django.conf import settings
from django.test import TestCase

from shortener.services import validate_str_for_restriction


class StrValidationForRestrictedPhrasesTests(TestCase):
    def test_validation_for_restricted_phrases_with_restricted_phrases(self):
        restricted_phrases = settings.RESTRICTED_PHRASES + ["test-1", "more-restrictions2"]
        strs_to_validate = [
            "admin",
            "test-1",
            "more-restrictions2",
        ]

        for str in strs_to_validate:
            self.assertFalse(validate_str_for_restriction(str, restricted_phrases))

    def test_validation_for_restricted_phrases_with_allowed_phrases(self):
        restricted_phrases = settings.RESTRICTED_PHRASES
        strs_to_validate = [
            "admin-1",
            "admins",
            "someText",
            "more-text",
            "numbers124",
            "one1",
            "two-2",
            "more-2-numbers-571f",
        ]

        for str in strs_to_validate:
            self.assertTrue(validate_str_for_restriction(str, restricted_phrases))
