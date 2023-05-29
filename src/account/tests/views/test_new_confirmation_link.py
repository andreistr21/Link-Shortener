from unittest import mock

from django.shortcuts import redirect
from django.test import TestCase
from django.urls import reverse

from account.forms import SignInForm


class NewConfirmationLinkTests(TestCase):
    def _test_view(self, resp, expected_status_code, expected_template):
        self.assertEqual(resp.status_code, expected_status_code)
        self.assertTemplateUsed(resp, expected_template)

    def test_request_get(self):
        resp = self.client.get(reverse("account:new_confirmation_link"))
        new_confirmation_link_form = SignInForm()

        self._test_view(resp, 200, "account/new_confirmation_link.html")
        self.assertEqual(
            str(resp.context["new_confirmation_link_form"]),
            str(new_confirmation_link_form),
        )

    @mock.patch("account.views.send_new_activation_link", return_value=None)
    def test_if_form_is_valid(self, _):
        form_data = {"email": "test@gmail.com", "password": "test_password"}
        resp = self.client.post(
            reverse("account:new_confirmation_link"), form_data
        )

        self._test_view(resp, 200, "account/new_confirmation_link.html")

    @mock.patch(
        "account.views.send_new_activation_link",
        return_value=redirect(reverse("account:confirm_email")),
    )
    def test_if_form_is_invalid(self, _):
        form_data = {"email": "test@gmail.com", "password": "test_password"}
        resp = self.client.post(
            reverse("account:new_confirmation_link"), form_data
        )

        self.assertRedirects(resp, reverse("account:confirm_email"))
