from unittest import mock
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse
from account.forms import SignInForm

from account.models import Profile
from account.services import send_new_activation_link


class SendNewActivationLinkTests(TestCase):
    def setUp(self):
        self.user = Profile.objects.create_user(
            "test@gmail.com", "test_password"
        )
        self.request_factory = RequestFactory()
        self.request = self.request_factory.get(reverse("account:sign_in"))
        self.form = SignInForm(
            data={"email": self.user.email, "password": "test_password"}
        )

    def test_if_email_confirmed(self):
        self.user.is_email_confirmed = True
        self.user.save()

        resp = send_new_activation_link(self.user, self.form)

        self.assertIsNone(resp)

    @mock.patch("account.services._send_activation_email")
    def test_if_email_not_confirmed(self, send_activation_email_mock):
        send_activation_email_mock.return_value = None

        resp = send_new_activation_link(self.user, self.form)
        resp.client = Client()

        self.assertRedirects(resp, reverse("account:confirm_email"))
