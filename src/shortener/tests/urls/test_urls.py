from django.contrib.auth.models import AnonymousUser
from django.test import Client, TestCase
from django.urls import resolve, reverse

from account.models import Profile
from shortener import views


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
            
    def test_index_url_anonymous_user(self):
        response = self.client.get(reverse("shortener:index"))
        
        self._test_view_render(response, views.index)

    def test_index_url_auth_user(self):
        self._login()
        response = self.client.get(reverse("shortener:index"))
        
        self._test_view_render(response, views.index)