from unittest import mock
from django.test import TestCase
from django.urls import reverse

from account.forms import SignInForm
from account.models import Profile


class SignInTests(TestCase):
    def _test_view(self, resp, expected_status_code, expected_template):
        self.assertEqual(resp.status_code, expected_status_code)
        self.assertTemplateUsed(resp, expected_template)

    def test_request_get(self):
        resp = self.client.get(reverse("account:sign_in"))
        sign_in_form = SignInForm()

        self._test_view(resp, 200, "account/sign_in.html")
        self.assertEqual(str(resp.context["sign_in_form"]), str(sign_in_form))
        self.assertFalse(resp.context["new_activation_link"])

    def test_if_email_is_not_confirmed(self):
        form_data = {"email": "test@gmail.com", "password": "test_pass"}
        Profile.objects.create_user(**form_data)
        resp = self.client.post(reverse("account:sign_in"), form_data)

        self._test_view(resp, 200, "account/sign_in.html")
        self.assertTrue(resp.context["sign_in_form"].errors)
        self.assertTrue(resp.context["new_activation_link"])
        
        
    def test_if_form_is_valid(self):
        form_data = {"email": "test@gmail.com", "password": "test_pass"}
        Profile.objects.create_user(is_email_confirmed=True, **form_data)
        resp = self.client.post(reverse("account:sign_in"), form_data)

        self.assertRedirects(resp, reverse("account:overview"))
