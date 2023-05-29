from unittest import mock

from django.test import TestCase
from django.urls import reverse

from account.services import update_email_confirmation_status


class ActivateEmailTests(TestCase):
    @mock.patch(
        "account.views.update_email_confirmation_status", return_value=None
    )
    def test_request_get(self, _):
        resp = self.client.get(
            reverse("account:activate_email", args=(1, "test_token"))
        )

        self.assertRedirects(resp, reverse("account:sign_in"))
