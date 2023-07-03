from unittest import mock

from django.contrib.auth.models import AnonymousUser
from django.http import Http404
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse

from account.models import Profile
from account.views import delete_link
from shortener.models import Link


class DeleteLinkTests(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.request_factory = RequestFactory()
        cls.request = cls.request_factory.get(
            reverse("account:delete_link", args=("test-alias",))
        )
        cls.user = Profile.objects.create_user(
            "test@gmail.com", "test_password"
        )
        cls.request.user = cls.user
        cls.link = Link.objects.create(
            long_link="https://www.youtube.com/",
            alias="youtube",
            user_profile=cls.user,
        )

    def test_anonymous_user(self):
        self.request.user = AnonymousUser()
        resp = delete_link(self.request, "wrong-test-alias")
        resp.client = Client()

        self.assertRedirects(
            resp,
            reverse("account:sign_in")
            + "?next="
            + reverse("account:delete_link", args=("test-alias",)),
        )

    @mock.patch(
        "account.views.get_link", return_value=None, side_effect=Http404
    )
    def test_if_link_do_not_exists(self, _):
        self.assertRaises(
            Http404, delete_link, self.request, "wrong-test-alias"
        )

    @mock.patch("account.views.check_user_access", side_effect=Http404)
    @mock.patch("account.views.get_link")
    def test_if_link_do_not_belongs_to_user(self, get_link_mock, _):
        get_link_mock.return_value = self.link
        self.assertRaises(
            Http404, delete_link, self.request, "wrong-test-alias"
        )

    @mock.patch("account.views.remove_link")
    @mock.patch("account.views.check_user_access")
    @mock.patch("account.views.get_link")
    def test_if_link_exists(self, get_link_mock, *args):
        get_link_mock.return_value = self.link

        resp = delete_link(self.request, "youtube")
        resp.client = Client()

        self.assertRedirects(
            resp, reverse("account:links_list"), target_status_code=302
        )
