from unittest import mock

from celery import current_app
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse

from account.forms import SignUpForm
from account.models import Profile
from account.services import sign_up_user


class SignUpUserTests(TestCase):
    def setUp(self):
        current_app.conf.task_always_eager = True
        self.factory = RequestFactory()
        self.request = self.factory.get(reverse("account:sign_up"))

    @mock.patch("account.services._send_activation_email")
    def test_if_form_is_invalid(self, send_activation_email_mock: mock.Mock):
        form_data = {
            "email": "test@gmail.com",
            "password1": "pass",
            "password2": "pass2",
        }
        sign_up_form = SignUpForm(data=form_data)
        resp = sign_up_user(self.request, sign_up_form)

        self.assertEqual(resp, None)
        send_activation_email_mock.assert_not_called()

    @mock.patch("account.services._send_activation_email")
    def test_if_form_is_valid(self, send_activation_email_mock: mock.Mock):
        form_data = {
            "email": "test@gmail.com",
            "password1": "test_password",
            "password2": "test_password",
        }
        sign_up_form = SignUpForm(data=form_data)
        resp = sign_up_user(self.request, sign_up_form)
        resp.client = Client()

        self.assertTrue(Profile.objects.get(email="test@gmail.com"))
        send_activation_email_mock.assert_called_once()
        self.assertRedirects(resp, reverse("account:confirm_email"))
