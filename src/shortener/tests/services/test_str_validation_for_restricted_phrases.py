from unittest import TestCase

from django.conf import settings

from shortener.services import validate_str_for_restriction

from .common_data import strs_to_validate_allowed_phrases, strs_to_validate_restricted_phrases


class StrValidationForRestrictedPhrasesTests(TestCase):
    def test_validation_for_restricted_phrases_with_restricted_phrases(self):
        restricted_phrases = settings.RESTRICTED_PHRASES
        strs_to_validate = strs_to_validate_restricted_phrases

        for str in strs_to_validate:
            self.assertFalse(validate_str_for_restriction(str, restricted_phrases))

    def test_validation_for_restricted_phrases_with_allowed_phrases(self):
        restricted_phrases = settings.RESTRICTED_PHRASES
        strs_to_validate = strs_to_validate_allowed_phrases

        for str in strs_to_validate:
            self.assertTrue(validate_str_for_restriction(str, restricted_phrases))
