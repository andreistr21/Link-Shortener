from unittest import mock

from django.http import Http404, HttpResponseRedirect
from django.shortcuts import redirect
from django.test import RequestFactory, TestCase
from django.urls import reverse

from account.models import Profile
from shortener.models import Link
from shortener.views import shorten_redirect


class ShortenRedirectTests(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.patcher = mock.patch(
            "shortener.views.update_link_statistics", return_value=None
        )

        long_link = "https://www.youtube.com"
        cls.user = Profile.objects.create_user(
            "test@gmail.com", "test_password"
        )
        cls.link_no_profile = Link.objects.create(
            long_link=long_link,
            alias="youtube1",
        )
        cls.link_with_profile = Link.objects.create(
            long_link=long_link,
            alias="youtube2",
            user_profile=cls.user,
        )
        cls.redirect = redirect(long_link)
        cls.request_factory = RequestFactory()
        cls.request = cls.request_factory.get(
            reverse("shortener:shorten_redirect", args=("alias",))
        )

    def setUp(self) -> None:
        self.update_link_statistics_mock = self.patcher.start()
        self.addCleanup(self.patcher.stop)

    @mock.patch("shortener.views.get_link", side_effect=Http404)
    def test_if_no_link_exists(self, get_link_mock):
        self.assertRaises(Http404, shorten_redirect, self.request, "alias")
        get_link_mock.assert_called_once_with("alias")
        self.update_link_statistics_mock.assert_not_called()

    @mock.patch("shortener.views.get_link")
    def test_no_statistics_updated(self, get_link_mock):
        get_link_mock.return_value = self.link_no_profile
        resp = shorten_redirect(self.request, "alias")

        get_link_mock.assert_called_once_with("alias")
        self.update_link_statistics_mock.assert_not_called()
        self.assertIsInstance(resp, HttpResponseRedirect)

    @mock.patch("shortener.views.get_link")
    def test_statistics_updated(self, get_link_mock):
        get_link_mock.return_value = self.link_with_profile
        resp = shorten_redirect(self.request, "alias")

        get_link_mock.assert_called_once_with("alias")
        self.update_link_statistics_mock.assert_called_with(
            self.request, self.link_with_profile
        )
        self.assertIsInstance(resp, HttpResponseRedirect)
