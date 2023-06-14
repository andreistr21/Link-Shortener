from unittest import mock

from django.test import TestCase
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from account.models import Profile
from account.selectors import get_profile
from account.services import update_email_confirmation_status


class UpdateEmailConfirmationStatusTests(TestCase):
    def setUp(self):
        Profile.objects.all().delete()
        self.user = Profile.objects.create_user(
            "test@gmail.com", "test_password"
        )

    @mock.patch(
        "django.contrib.auth.tokens.PasswordResetTokenGenerator.check_token"
    )
    def test_status_change(self, check_token_mock: mock.Mock):
        check_token_mock.return_value = True

        self.assertFalse(self.user.is_email_confirmed)

        update_email_confirmation_status(
            urlsafe_base64_encode(force_bytes(self.user.pk)), "test_token"
        )

        self.assertTrue(get_profile(self.user.pk).is_email_confirmed)
