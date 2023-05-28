from unittest import mock

from celery import current_app
from django.contrib.sites.shortcuts import get_current_site
from django.test import RequestFactory, TestCase
from django.urls import reverse

from account.forms import SignUpForm
from account.models import Profile
from account.services import _send_activation_email


class SendActivationEmailTests(TestCase):
    def setUp(self):
        current_app.conf.task_always_eager = True
        self.factory = RequestFactory()

    @mock.patch("account.forms.SignUpForm.clean")
    @mock.patch("account.tasks.send_activation_email.delay")
    @mock.patch("django.http.request.HttpRequest.is_secure")
    def test_task_called(
        self,
        is_secure_mock: mock.Mock,
        send_activation_email_mock: mock.Mock,
        sign_up_form_clean: mock.Mock,
    ):
        protocol = "https"
        to_email = "to@gmail.com"
        is_secure_mock.return_value = protocol
        sign_up_form_clean.return_value = {"email": to_email}

        user = Profile.objects.create_user(to_email, "test-password")
        request = self.factory.get(reverse("account:sign_up"))
        form = SignUpForm(data={"email": to_email})
        form.is_valid()
        _send_activation_email(request, user, form)

        send_activation_email_mock.assert_called_once_with(
            domain="testserver:80",
            protocol=protocol,
            user_id=user.pk,
            to_email=to_email,
        )
