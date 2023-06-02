from django.contrib.sessions.middleware import SessionMiddleware
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse

from account.forms import SignInForm
from account.models import Profile
from account.services import sign_in_user


class SignInUserTests(TestCase):
    def setUp(self):
        self.request_factory = RequestFactory()
        # login method need session middleware
        self.middleware = SessionMiddleware(self.request_factory)
        self.request = self.request_factory.get(reverse("account:sign_in"))

    def test_if_form_is_invalid(self):
        email = "test@gmail.com"
        Profile.objects.create_user(email=email, password="test_password")
        form_data = {"email": email, "password": "wrong_password"}
        sign_in_form = SignInForm(data=form_data)
        resp = sign_in_user(self.request, sign_in_form)

        self.assertIsNone(resp)

    def test_if_email_is_not_confirmed(self):
        email = "test@gmail.com"
        password = "test_password"
        Profile.objects.create_user(email=email, password=password)
        form_data = {"email": email, "password": password}
        sign_in_form = SignInForm(data=form_data)
        resp = sign_in_user(self.request, sign_in_form)

        self.assertEqual(resp, "Error")

    def test_if_form_is_valid(self):
        email = "test@gmail.com"
        password = "test_password"
        self.middleware.process_request(self.request)

        profile = Profile.objects.create_user(email=email, password=password)
        profile.is_email_confirmed = True
        profile.save()
        self.request.user = profile

        form_data = {"email": email, "password": password}
        sign_in_form = SignInForm(self.request, data=form_data)
        resp = sign_in_user(self.request, sign_in_form)
        resp.client = Client()
        resp.client.login(email=email, password=password)

        self.assertRedirects(resp, reverse("account:overview"))
