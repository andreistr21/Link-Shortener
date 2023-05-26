from datetime import datetime

import six
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.test import TestCase

from account.models import Profile
from account.tokens import EmailActivationTokenGenerator, email_activation_token


class TokenGeneratorTestCase(TestCase):
    def setUp(self):
        self.generator = EmailActivationTokenGenerator()
        self.user = Profile.objects.create_user(email="test@gmail.com", password="test_password")
        self.timestamp = datetime.now()

    def test_make_hash_value(self):
        expected_hash_value = (
            six.text_type(self.user.pk)
            + six.text_type(self.timestamp)
            + six.text_type(self.user.is_email_confirmed)
        )
        hash_value = self.generator._make_hash_value(self.user, self.timestamp)

        self.assertEqual(hash_value, expected_hash_value)

    def test_email_activation_token_instance(self):
        self.assertIsInstance(email_activation_token, PasswordResetTokenGenerator)
