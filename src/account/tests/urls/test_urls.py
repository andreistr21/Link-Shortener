from unittest import mock
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.views import (
    LogoutView,
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
)
from django.test import Client, TestCase
from django.urls import resolve, reverse
from django.views.generic import TemplateView

from account import views
from account.models import Profile


class AccountUrlTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_email = "test@gmail.com"
        cls.user_password = "test_password"
        cls.user = Profile.objects.create_user(
            cls.user_email, cls.user_password
        )
        cls.anonymous_require_redirect_name = "account:overview"
        cls.login_required_redirect_name = "account:sign_in"

    def setUp(self):
        self.client = Client()
        self.client.user = AnonymousUser()

    def _test_template_used(self, response, template_name):
        self.assertTemplateUsed(response, template_name)

    def _test_url_status(self, response, status_code=200):
        self.assertEqual(response.status_code, status_code)

    def _test_redirect(self, response, redirect_url):
        self.assertRedirects(response, redirect_url)

    def _test_view_used(self, response, expected_view):
        view_name = resolve(response.request["PATH_INFO"]).func.__name__
        if view_name == "view":
            view_name = expected_view.__name__
        expected_view_name = expected_view.__name__

        self.assertEqual(view_name, expected_view_name)

    def _login(self):
        self.client.force_login(self.user)

    def _test_view_render(self, response, view, template_name=None):
        self._test_url_status(response)
        self._test_view_used(response, view)
        if template_name:
            self._test_template_used(response, template_name)

    def _test_view_redirect(
        self, response, view, redirect_name=None, next=None
    ):
        if not redirect_name:
            redirect_name = self.anonymous_require_redirect_name

        if next:
            expected_url = f"{reverse(redirect_name)}{next}"
            self._test_redirect(response, expected_url)
        else:
            self._test_redirect(response, reverse(redirect_name))

        self._test_view_used(response, view)

    def test_sign_up_url_anonymous_user(self):
        response = self.client.get(reverse("account:sign_up"))

        self._test_view_render(response, views.sign_up)

    def test_sign_up_url_auth_user(self):
        self._login()
        response = self.client.get(reverse("account:sign_up"))

        self._test_view_redirect(response, views.sign_up)

    def test_sign_in_url_anonymous_user(self):
        response = self.client.get(reverse("account:sign_in"))

        self._test_view_render(response, views.sign_in)

    def test_sign_in_url_auth_user(self):
        self._login()
        response = self.client.get(reverse("account:sign_in"))

        self._test_view_redirect(response, views.sign_in)

    def test_logout_url_anonymous_user(self):
        response = self.client.get(reverse("account:logout"))

        self._test_view_redirect(
            response,
            LogoutView,
            self.login_required_redirect_name,
            "?next=/account/logout/",
        )

    def test_logout_url_auth_user(self):
        self._login()
        response = self.client.get(reverse("account:logout"))

        self._test_view_render(
            response,
            LogoutView,
            "account/logged_out.html",
        )

    def test_confirm_email_url_anonymous_user(self):
        response = self.client.get(reverse("account:confirm_email"))

        self._test_view_render(response, views.confirm_email)

    def test_confirm_email_url_auth_user(self):
        self._login()
        response = self.client.get(reverse("account:confirm_email"))

        self._test_view_render(response, views.confirm_email)

    def test_new_confirmation_link_url_anonymous_user(self):
        response = self.client.get(reverse("account:new_confirmation_link"))

        self._test_view_render(response, views.new_confirmation_link)

    def test_new_confirmation_link_url_auth_user(self):
        self._login()
        response = self.client.get(reverse("account:new_confirmation_link"))

        self._test_view_redirect(response, views.new_confirmation_link)

    @mock.patch(
        "account.views.update_email_confirmation_status",
        return_value=None,
    )
    def test_activate_email_url_anonymous_user(self, _):
        response = self.client.get(
            reverse("account:activate_email", args=("pk", "token"))
        )

        self._test_view_redirect(
            response, views.activate_email, "account:sign_in"
        )

    def test_activate_email_url_auth_user(self):
        self._login()
        response = self.client.get(
            reverse("account:activate_email", args=("pk", "token"))
        )

        self._test_view_redirect(response, views.activate_email)

    def test_overview_url_anonymous_user(self):
        response = self.client.get(reverse("account:overview"))

        self._test_view_redirect(
            response,
            views.overview,
            self.login_required_redirect_name,
            "?next=/account/overview",
        )

    def test_overview_url_auth_user(self):
        self._login()
        response = self.client.get(reverse("account:overview"))

        self._test_view_render(response, views.overview)

    def test_password_reset_url_anonymous_user(self):
        response = self.client.get(reverse("account:password_reset"))

        self._test_view_render(
            response, PasswordResetView, "account/password_reset.html"
        )

    def test_password_reset_url_auth_user(self):
        self._login()
        response = self.client.get(reverse("account:password_reset"))

        self._test_view_redirect(response, PasswordResetView)

    def test_password_reset_done_url_anonymous_user(self):
        response = self.client.get(reverse("account:password_reset_done"))

        self._test_view_render(
            response, PasswordResetDoneView, "account/password_reset_done.html"
        )

    def test_password_reset_done_url_auth_user(self):
        self._login()
        response = self.client.get(reverse("account:password_reset_done"))

        self._test_view_render(
            response, PasswordResetDoneView, "account/password_reset_done.html"
        )

    def test_password_reset_confirm_url_anonymous_user(self):
        response = self.client.get(
            reverse("account:password_reset_confirm", args=["uidb64", "token"])
        )

        self._test_view_render(
            response,
            PasswordResetConfirmView,
            "account/password_reset_confirm.html",
        )

    def test_password_reset_confirm_url_auth_user(self):
        self._login()
        response = self.client.get(
            reverse("account:password_reset_confirm", args=("uidb64", "token"))
        )

        self._test_view_redirect(response, PasswordResetConfirmView)

    def test_password_reset_complete_url_anonymous_user(self):
        response = self.client.get(reverse("account:password_reset_complete"))

        self._test_view_render(
            response,
            PasswordResetCompleteView,
            "account/password_reset_complete.html",
        )

    def test_password_reset_complete_url_auth_user(self):
        self._login()
        response = self.client.get(reverse("account:password_reset_complete"))

        self._test_view_render(
            response,
            PasswordResetCompleteView,
            "account/password_reset_complete.html",
        )

    def test_privacy_policy_url_anonymous_user(self):
        response = self.client.get(reverse("account:privacy_policy"))

        self._test_view_render(
            response, TemplateView, "account/privacy_policy.html"
        )

    def test_privacy_policy_url_auth_user(self):
        self._login()
        response = self.client.get(reverse("account:privacy_policy"))

        self._test_view_render(
            response, TemplateView, "account/privacy_policy.html"
        )

    def test_terms_of_use_url_anonymous_user(self):
        response = self.client.get(reverse("account:terms_of_use"))

        self._test_view_render(
            response, TemplateView, "account/terms_of_use.html"
        )

    def test_terms_of_use_url_auth_user(self):
        self._login()
        response = self.client.get(reverse("account:terms_of_use"))

        self._test_view_render(
            response, TemplateView, "account/terms_of_use.html"
        )
