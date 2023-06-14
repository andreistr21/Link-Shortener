from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.test import TestCase
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from account.models import Profile
from account.tasks import construct_email
from account.tokens import email_activation_token


class ConstructEmailTests(TestCase):
    def setUp(self):
        Profile.objects.all().delete()
        self.domain = "example.com"
        self.protocol = True  # Assuming the protocol is HTTPS
        self.to_email = "test@example.com"
        self.user = Profile.objects.create_user(
            email="test@gmail.com",
            password="test_password",
        )

    def test_construct_email(self):
        expected_subject = "Activate your user account."
        expected_message = render_to_string(
            "account/email_activation.html",
            {
                "user": self.user.email,
                "domain": self.domain,
                "uid": urlsafe_base64_encode(force_bytes(self.user.pk)),
                "token": email_activation_token.make_token(self.user),
                "protocol": "https" if self.protocol else "http",
            },
        )
        expected_email = EmailMessage(
            expected_subject, expected_message, to=[self.to_email]
        )

        constructed_email = construct_email(
            self.domain, self.protocol, self.user.pk, self.to_email
        )

        self.assertEqual(constructed_email.subject, expected_email.subject)
        self.assertEqual(constructed_email.body, expected_email.body)
        self.assertEqual(constructed_email.to, expected_email.to)
