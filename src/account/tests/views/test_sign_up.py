from unittest import mock
from django.test import TestCase
from django.urls import reverse

from account.forms import SignUpForm


class SignUpTests(TestCase):
    def _test_view(self, resp, expected_status_code, expected_template):
        self.assertEqual(resp.status_code, expected_status_code)
        self.assertTemplateUsed(resp, expected_template)

    def test_request_get(self):
        resp = self.client.get(reverse("account:sign_up"))
        sign_up_form = SignUpForm()

        self._test_view(resp, 200, "account/sign_up.html")
        self.assertEqual(str(resp.context["sign_up_form"]), str(sign_up_form))

    def test_if_form_is_invalid(self):
        resp = self.client.post(
            reverse("account:sign_up"),
            {
                "email": "test@gmail.com",
                "password1": "test_pass",
                "password2": "test_pass2",
            },
        )

        self._test_view(resp, 200, "account/sign_up.html")
        self.assertTrue(resp.context["sign_up_form"].errors)

    @mock.patch("account.services._send_activation_email")
    def test_if_form_is_valid(self, send_activation_email_mock):
        send_activation_email_mock.return_value = None
        resp = self.client.post(
            reverse("account:sign_up"),
            {
                "email": "test@gmail.com",
                "password1": "test_pass",
                "password2": "test_pass",
            },
        )

        self.assertRedirects(resp, reverse("account:confirm_email"))
