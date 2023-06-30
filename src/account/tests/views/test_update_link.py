from unittest import mock

from django.contrib.auth.models import AnonymousUser
from django.http import Http404, HttpResponse
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse

from account.models import Profile
from account.views import update_link
from shortener.forms import ShortenForm
from shortener.models import Link


class UpdateLinkTests(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.request_factory = RequestFactory()
        cls.user = Profile.objects.create_user(
            "test@gmail.com", "test_password"
        )
        cls.link = Link.objects.create(
            long_link="https://www.youtube.com/", alias="youtube1"
        )
        cls.clicks_chart_data = {"30.06": 3, "29.06": 2}
        cls.expected_countries_chart_data = {
            "PL": 2,
            "DE": 1,
            "ES": 2,
            "Unknown": 1,
        }
        cls.form_data = {
            "long_link": "https://www.youtube.com/",
            "alias": "youtube1",
        }

    def setUp(self) -> None:
        # get_link mock
        self.get_link_patch = mock.patch("account.views.get_link")
        self.get_link_mock = self.get_link_patch.start()
        self.addCleanup(self.get_link_patch.stop)
        self.get_link_mock.return_value = self.link

        # check_user_access mock
        self.check_user_access_patch = mock.patch(
            "account.views.check_user_access"
        )
        self.check_user_access_mock = self.check_user_access_patch.start()
        self.addCleanup(self.check_user_access_patch.stop)
        self.check_user_access_mock.return_value = None

        # ShortenForm.is_valid mock
        self.is_valid_patch = mock.patch.object(ShortenForm, "is_valid")
        self.is_valid_mock = self.is_valid_patch.start()
        self.addCleanup(self.is_valid_patch.stop)
        self.is_valid_mock.return_value = True

        # short_link mock
        self.short_link_patch = mock.patch("account.views.short_link")
        self.short_link_mock = self.short_link_patch.start()
        self.addCleanup(self.short_link_patch.stop)
        self.short_link_mock.return_value = None

        # rename_redis_list mock
        self.rename_redis_list_patch = mock.patch(
            "account.views.rename_redis_list"
        )
        self.rename_redis_list_mock = self.rename_redis_list_patch.start()
        self.addCleanup(self.rename_redis_list_patch.stop)
        self.rename_redis_list_mock.return_value = None

    def test_login_required_redirect(self):
        request = self.request_factory.get(
            reverse("account:update_link", args=(self.link.alias,))
        )
        request.user = AnonymousUser()

        response = update_link(request, self.link.alias)
        response.client = Client()

        self.assertRedirects(
            response,
            reverse("account:sign_in")
            + "?next="
            + reverse("account:update_link", args=(self.link.alias,)),
        )

    def test_auth_user_get(self):  # sourcery skip: class-extract-method
        request = self.request_factory.get(
            reverse("account:update_link", args=(self.link.alias,))
        )
        request.user = self.user

        response = update_link(request, self.link.alias)
        response.client = Client()

        self.assertIsInstance(response, HttpResponse)
        self.assertEqual(response.status_code, 200)
        self.get_link_mock.assert_called_once_with(self.link.alias)
        self.check_user_access_mock.assert_called_once_with(
            request.user, self.link
        )
        self.short_link_mock.assert_not_called()
        self.rename_redis_list_mock.assert_not_called()

    def test_auth_user_get_no_link_found(
        self,
    ):  # sourcery skip: class-extract-method
        self.get_link_mock.side_effect = Http404
        request = self.request_factory.get(
            reverse("account:update_link", args=(self.link.alias,))
        )
        request.user = self.user

        self.assertRaises(Http404, update_link, request, self.link.alias)

    def test_auth_user_get_link_do_not_belongs_to_current_user(
        self,
    ):  # sourcery skip: class-extract-method
        self.check_user_access_mock.side_effect = Http404
        request = self.request_factory.get(
            reverse("account:update_link", args=(self.link.alias,))
        )
        request.user = self.user

        self.assertRaises(Http404, update_link, request, self.link.alias)

    def test_auth_user_post_invalid_form(self):
        self.is_valid_mock.return_value = False

        request = self.request_factory.post(
            reverse("account:update_link", args=(self.link.alias,)),
            data=self.form_data,
        )
        request.user = self.user

        response = update_link(request, self.link.alias)
        response.client = Client()

        self.assertIsInstance(response, HttpResponse)
        self.assertEqual(response.status_code, 200)
        self.get_link_mock.assert_called_once_with(self.link.alias)
        self.check_user_access_mock.assert_called_once_with(
            request.user, self.link
        )
        self.short_link_mock.assert_not_called()
        self.rename_redis_list_mock.assert_not_called()

    def test_auth_user_post_valid_form_without_errors_during_shortening_same_aliases(
        self,
    ):
        self.short_link_mock.return_value = self.link.alias
        request = self.request_factory.post(
            reverse("account:update_link", args=(self.link.alias,)),
            data=self.form_data,
        )
        request.user = self.user

        response = update_link(request, self.link.alias)
        response.client = Client()

        self.assertEqual(response.status_code, 302)
        self.get_link_mock.assert_called_once_with(self.link.alias)
        self.check_user_access_mock.assert_called_once_with(
            request.user, self.link
        )
        self.short_link_mock.assert_called_once()
        self.rename_redis_list_mock.assert_not_called()

    def test_auth_user_post_valid_form_without_errors_during_shortening_same_different_aliases(
        self,
    ):  # sourcery skip: use-fstring-for-concatenation
        self.short_link_mock.return_value = self.link.alias + "2"
        request = self.request_factory.post(
            reverse("account:update_link", args=(self.link.alias,)),
            data=self.form_data,
        )
        request.user = self.user

        response = update_link(request, self.link.alias)
        response.client = Client()

        self.assertEqual(response.status_code, 302)
        self.get_link_mock.assert_called_once_with(self.link.alias)
        self.check_user_access_mock.assert_called_once_with(
            request.user, self.link
        )
        self.short_link_mock.assert_called_once()
        self.rename_redis_list_mock.assert_called_once_with(
            self.link.alias, self.link.alias + "2"
        )
