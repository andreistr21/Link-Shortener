from os import error
from django.test import RequestFactory, TestCase
from django.urls import reverse

from account.forms import SignInForm
from account.models import Profile


class SignInTests(TestCase):
    def setUp(self):
        Profile.objects.all().delete()
        self.factory = RequestFactory()
        self.profile = Profile.objects.create_user("test@gmail.com", "test_password")

    def test_email_field_html(self):
        self.assertInHTML(
            (
                '<input type="email" name="email" autofocus="" max_length="150" placeholder="Your'
                ' email" required="" id="id_email">'
            ),
            str(SignInForm()),
        )

    def test_password_field_html(self):
        self.assertInHTML(
            (
                '<input type="password" name="password" placeholder="Password" required=""'
                ' id="id_password">'
            ),
            str(SignInForm()),
        )

    def test_initial_vars(self):
        request = self.factory.get(reverse("account:sign_in"))
        form = SignInForm(request)

        self.assertEqual(form.user_cache, None)
        self.assertEqual(form.request, request)

    def test_if_no_email(self):
        self._test_for_field_error("password", "test_password", "email")

    def test_if_no_password(self):
        self._test_for_field_error("email", "test@gmail.com", "password")

    def _test_for_field_error(self, attr_key, attr_val, error_field):
        request = self.factory.get(reverse("account:sign_in"))
        form = SignInForm(request, data={attr_key: attr_val})
        form.is_valid()
        errors = form.errors.get(error_field)
        error_val = "This field is required."

        self.assertTrue(error_val in errors)

    def test_if_email_is_wrong(self):
        self._test_for_non_field_error(
            "testw@gmail.com",
            "test_password",
            (
                "Please enter a correct email and password. Note that both fields may be"
                " case-sensitive."
            ),
        )

    def test_if_password_is_wrong(self):
        self._test_for_non_field_error(
            "test@gmail.com",
            "test_password_w",
            (
                "Please enter a correct email and password. Note that both fields may be"
                " case-sensitive."
            ),
        )

    def test_if_email_is_not_confirmed(self):
        self._test_for_non_field_error(
            "test@gmail.com",
            "test_password",
            (
                "Email for this account not confirmed. Confirmation link was sent to your email"
                " during registration."
            ),
        )

    def test_if_user_is_inactive(self):
        self.profile.is_email_confirmed = True
        self.profile.is_active = False
        self.profile.save()

        self._test_for_non_field_error(
            "test@gmail.com",
            "test_password",
            (
                "Please enter a correct email and password. Note that both fields may be"
                " case-sensitive."
            ),
        )

    def _test_for_non_field_error(self, email, password, error_val):
        request = self.factory.get(reverse("account:sign_in"))
        form = SignInForm(request, data={"email": email, "password": password})
        form.is_valid()
        errors = form.non_field_errors()
        self.assertTrue(error_val in errors)

    def test_if_user_login_allow(self):  # sourcery skip: class-extract-method
        self.profile.is_email_confirmed = True
        self.profile.save()
        request = self.factory.get(reverse("account:sign_in"))
        form = SignInForm(request, data={"email": "test@gmail.com", "password": "test_password"})
        form.is_valid()

        self.assertFalse(form.errors)
