from django.test import TestCase
from django.urls import reverse


class ConfirmEmailTests(TestCase):
    def _test_view(self, resp, expected_status_code, expected_template):
        self.assertEqual(resp.status_code, expected_status_code)
        self.assertTemplateUsed(resp, expected_template)

    def test_request_get(self):
        resp = self.client.get(reverse("account:confirm_email"))

        self._test_view(resp, 200, "account/confirm_email.html")
