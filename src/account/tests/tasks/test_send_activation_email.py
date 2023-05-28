from unittest import mock

from django.test import TestCase

from account.models import Profile
from account.tasks import send_activation_email_task


class SendActivationEmailTests(TestCase):
    def setUp(self):
        Profile.objects.all().delete()
        self.domain = "example.com"
        self.protocol = True  # Assuming the protocol is HTTPS
        self.to_email = "test@example.com"
        self.user = Profile.objects.create_user(
            email="test@gmail.com",
            password="test_password",
        )

    @mock.patch("django.core.mail.message.EmailMessage.send")
    def test_email_sent(self, send_mock):
        send_activation_email_task.apply(
            args=(
                self.domain,
                self.protocol,
                self.user.pk,
                self.to_email,
            ),
            throw=True,
        )

        send_mock.assert_called_once()
